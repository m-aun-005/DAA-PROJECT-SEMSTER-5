"""src/gui/screens/racing_screen.py — Screen 3: Live 2D Top-Down Racing (Section 2.1).
Simulates real-time 4-car competition with human controls, deterministic AI opponents,
vehicle physics, fuel consumption, nitro bursts, and min-heap dynamic events.
"""

from typing import Callable, Dict, List, Optional, Tuple
import math
import pygame
from src.core.graph import Graph
from src.models.circuit import Circuit
from src.models.vehicle import Vehicle, VehicleState
from src.data.circuits import ALL_CIRCUITS
from src.engine.race_engine import RaceEngine
from src.gui.components.button import Button
from src.gui.components.graph_renderer import GraphRenderer
from src.gui.components.hud import HUD
from src.gui.assets.colors import BG_DARK, PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_ACCENT
from src.gui.assets.fonts import get_font


class RacingScreen:
    """Screen 3: Live 2D racing simulation with active car animations and HUD."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.circuit_idx: int = 0
        self.circuit: Circuit = ALL_CIRCUITS[0]()
        self.engine: RaceEngine = RaceEngine(self.circuit, total_laps=2)
        self.renderer = GraphRenderer(pygame.display.get_surface(), self.circuit.graph)
        self.hud = HUD(pygame.display.get_surface())

        self.is_paused: bool = False
        self.buttons: List[Button] = [
            Button((20, 20, 110, 32), "← MENU", lambda: self.switch_screen("main_menu", {})),
            Button((140, 20, 110, 32), "PAUSE", lambda: self._toggle_pause()),
            Button((260, 20, 110, 32), "RESTART", lambda: self._restart_race()),
        ]

    def set_context(self, context: Dict) -> None:
        self.circuit_idx = context.get("circuit_idx", 0)
        laps = context.get("laps", 2)
        self.circuit = ALL_CIRCUITS[self.circuit_idx]()
        self.engine = RaceEngine(self.circuit, total_laps=laps)
        self.renderer = GraphRenderer(pygame.display.get_surface(), self.circuit.graph)
        self.hud = HUD(pygame.display.get_surface())
        self.engine.start_race()
        self.is_paused = False

    def _toggle_pause(self) -> None:
        self.is_paused = not self.is_paused
        self.buttons[1].text = "RESUME" if self.is_paused else "PAUSE"

    def _restart_race(self) -> None:
        self.engine.start_race()
        self.is_paused = False
        self.buttons[1].text = "PAUSE"

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

        if event.type == pygame.KEYDOWN:
            # Human Controls: Space for Nitro
            if event.key == pygame.K_SPACE:
                player = self.engine.vehicles[0]
                player.activate_nitro()
            elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                self._toggle_pause()

            # Human steering: Arrow keys or WASD to pick next outgoing edge
            player = self.engine.vehicles[0]
            if player.isHuman and player.state == VehicleState.RACING:
                out_edges = self.circuit.graph.get_outgoing_edges(player.currentVertex, traversable_only=True)
                if len(out_edges) > 1:
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        player.targetVertex = out_edges[-1].to_vertex
                        player.current_edge_id = out_edges[-1].id
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        player.targetVertex = out_edges[0].to_vertex
                        player.current_edge_id = out_edges[0].id

    def update(self, dt: float) -> None:
        if self.is_paused:
            return

        self.engine.tick(dt)

        # Transition to dashboard when race finishes
        if self.engine.is_finished:
            self.switch_screen("dashboard", {
                "results": self.engine.results,
                "circuit_name": self.circuit.name
            })

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self.renderer.surface = surface
        self.hud.surface = surface

        # 1. Draw Circuit Roads and Checkpoints
        self.renderer.draw()

        # 2. Draw 4 Competitor Cars
        self._draw_cars(surface)

        # 3. Draw In-Game HUD
        player = self.engine.vehicles[0]
        self.hud.draw(
            player_veh=player,
            vehicles=self.engine.vehicles,
            circuit=self.circuit,
            current_time=self.engine.current_time,
            active_alerts=self.engine.event_engine.event_log
        )

        # 4. Draw Header Buttons
        for btn in self.buttons:
            btn.draw(surface)

    def _draw_cars(self, surface: pygame.Surface) -> None:
        """Draws animated car sprites interpolated along their current active edge."""
        for veh in self.engine.vehicles:
            pos = self._get_vehicle_screen_pos(veh)
            if pos is None:
                continue

            px, py = int(pos[0]), int(pos[1])

            # Draw Nitro exhaust flame
            if veh.nitroTimer > 0:
                pygame.draw.circle(surface, (0, 200, 255), (px, py), 15, 2)
                pygame.draw.circle(surface, (255, 255, 255), (px, py), 8)

            # Draw Car Body
            radius = 10 if veh.isHuman else 8
            pygame.draw.circle(surface, (10, 12, 18), (px, py), radius + 2)
            pygame.draw.circle(surface, veh.color, (px, py), radius)

            # Label above car
            lbl_font = get_font(size=10, bold=True)
            txt = lbl_font.render(veh.name[:6], True, TEXT_WHITE)
            surface.blit(txt, (px - 14, py - 20))

    def _get_vehicle_screen_pos(self, veh: Vehicle) -> Optional[Tuple[float, float]]:
        u = self.circuit.graph.get_vertex(veh.currentVertex)
        if u is None:
            return None

        if veh.targetVertex is None or veh.state in (VehicleState.FINISHED, VehicleState.DNF, VehicleState.IDLE):
            return (u.x, u.y)

        v = self.circuit.graph.get_vertex(veh.targetVertex)
        if v is None:
            return (u.x, u.y)

        # Linear interpolation between u and v
        prog = max(0.0, min(1.0, veh.progress))
        cur_x = u.x + (v.x - u.x) * prog
        cur_y = u.y + (v.y - u.y) * prog
        return (cur_x, cur_y)
