"""src/gui/screens/racing_screen.py — Asphalt 8-style Live Racing Screen.
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
from src.gui.components.car_renderer import draw_car_at
from src.gui.assets.colors import BG_DARK, ROAD_GRASS, PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_ACCENT, TEXT_GOLD
from src.gui.assets.fonts import get_font, get_ui_font


class RacingScreen:
    """Screen 3: Asphalt 8-style live 2D racing simulation."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.circuit_idx: int = 0
        self.car_idx:     int = 0
        self.circuit: Circuit    = ALL_CIRCUITS[0]()
        self.engine:  RaceEngine = RaceEngine(self.circuit, total_laps=2)
        self.renderer = GraphRenderer(pygame.display.get_surface(), self.circuit.graph)
        self.hud      = HUD(pygame.display.get_surface())

        self.is_paused  = False
        self._countdown = 3.0   # 3-2-1-GO countdown
        self._race_started = False

        self.buttons: List[Button] = [
            Button((20, 672, 110, 36), "← MENU",   lambda: self.switch_screen("main_menu", {}), font_size=13),
            Button((140, 672, 110, 36), "PAUSE",    lambda: self._toggle_pause(), font_size=13),
            Button((260, 672, 110, 36), "RESTART",  lambda: self._restart_race(), font_size=13),
        ]

    def set_context(self, context: Dict) -> None:
        self.circuit_idx = context.get("circuit_idx", 0)
        self.car_idx     = context.get("car_idx", 0)
        laps             = context.get("laps", 2)
        self.circuit     = ALL_CIRCUITS[self.circuit_idx]()
        self.engine      = RaceEngine(self.circuit, total_laps=laps)
        self.renderer    = GraphRenderer(pygame.display.get_surface(), self.circuit.graph)
        self.hud         = HUD(pygame.display.get_surface())

        # Apply selected car to player vehicle and opponents
        from src.gui.components.car_renderer import CAR_DESIGNS
        if self.engine.vehicles:
            # Human player
            p_des = CAR_DESIGNS[self.car_idx % len(CAR_DESIGNS)]
            self.engine.vehicles[0].color = p_des["body"]
            self.engine.vehicles[0].name = p_des["name"]
            # AI opponents pick distinct classic cars
            for i, veh in enumerate(self.engine.vehicles[1:], 1):
                opp_ci = (self.car_idx + i * 2) % len(CAR_DESIGNS)
                veh.color = CAR_DESIGNS[opp_ci]["body"]
                veh.name = CAR_DESIGNS[opp_ci]["name"]

        self.engine.start_race()
        self.is_paused    = False
        self._countdown   = 3.0
        self._race_started = False
        self.buttons[1].text = "PAUSE"

    def _toggle_pause(self) -> None:
        self.is_paused = not self.is_paused
        self.buttons[1].text = "RESUME" if self.is_paused else "PAUSE"

    def _restart_race(self) -> None:
        self.engine.start_race()
        self.is_paused    = False
        self._countdown   = 3.0
        self._race_started = False
        self.buttons[1].text = "PAUSE"

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player = self.engine.vehicles[0]
                player.activate_nitro()
            elif event.key in (pygame.K_p, pygame.K_ESCAPE):
                self._toggle_pause()

            player = self.engine.vehicles[0]
            if player.isHuman and player.state == VehicleState.RACING:
                out_edges = self.circuit.graph.get_outgoing_edges(player.currentVertex, traversable_only=True)
                if len(out_edges) > 1:
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        player.targetVertex   = out_edges[-1].to_vertex
                        player.current_edge_id = out_edges[-1].id
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        player.targetVertex   = out_edges[0].to_vertex
                        player.current_edge_id = out_edges[0].id

    def update(self, dt: float) -> None:
        for btn in self.buttons:
            btn.update(dt)

        # Countdown phase
        if not self._race_started:
            self._countdown -= dt
            if self._countdown <= 0:
                self._race_started = True
            return

        if self.is_paused:
            return

        self.engine.tick(dt)
        self.hud.update(dt)

        if self.engine.is_finished:
            from src.gui.components.car_renderer import CAR_DESIGNS
            _car_name = CAR_DESIGNS[self.car_idx % len(CAR_DESIGNS)]["name"]
            self.switch_screen("dashboard", {
                "results":      self.engine.results,
                "circuit_name": self.circuit.name,
                "car_name":     _car_name,
            })

    def draw(self, surface: pygame.Surface) -> None:
        W, H = surface.get_size()

        # ── Background: dark grass/terrain ───────────────────────────────────
        surface.fill(ROAD_GRASS)

        # Subtle diagonal lines on grass
        for gx in range(-H, W+H, 40):
            pygame.draw.line(surface, (20, 46, 24), (gx, 0), (gx+H, H), 1)

        self.renderer.surface = surface

        # ── Draw circuit ──────────────────────────────────────────────────────
        self.renderer.draw()

        # ── Draw cars ─────────────────────────────────────────────────────────
        self._draw_cars(surface)

        # ── HUD ───────────────────────────────────────────────────────────────
        player = self.engine.vehicles[0]
        self.hud.surface = surface
        self.hud.draw(
            player_veh=player,
            vehicles=self.engine.vehicles,
            circuit=self.circuit,
            current_time=self.engine.current_time,
            active_alerts=self.engine.event_engine.event_log,
        )

        # ── Countdown overlay ─────────────────────────────────────────────────
        if not self._race_started:
            self._draw_countdown(surface, W, H)

        # ── Pause overlay ─────────────────────────────────────────────────────
        if self.is_paused:
            self._draw_pause_overlay(surface, W, H)

        # ── Bottom control bar ────────────────────────────────────────────────
        ctrl_bar = pygame.Surface((W, 44), pygame.SRCALPHA)
        pygame.draw.rect(ctrl_bar, (6, 8, 16, 220), ctrl_bar.get_rect())
        surface.blit(ctrl_bar, (0, H - 44))
        for btn in self.buttons:
            btn.draw(surface)

        # Circuit name watermark
        wm = get_ui_font(size=12).render(self.circuit.name, True, (60, 70, 90))
        surface.blit(wm, (W - wm.get_width() - 14, H - 36))

    def _draw_cars(self, surface: pygame.Surface) -> None:
        for veh in self.engine.vehicles:
            pos = self._get_vehicle_screen_pos(veh)
            if pos is None:
                continue
            px, py = int(pos[0]), int(pos[1])
            angle  = self._get_vehicle_angle(veh)

            # Determine car_index from car list or index
            from src.gui.components.car_renderer import CAR_DESIGNS
            ci = 0
            for k, des in enumerate(CAR_DESIGNS):
                if des["name"] == veh.name or des["body"] == veh.color:
                    ci = k
                    break
            else:
                ci = (self.car_idx + veh.id) % len(CAR_DESIGNS)

            nitro_on = hasattr(veh, "nitroTimer") and veh.nitroTimer > 0
            draw_car_at(surface, px, py, ci, angle=angle, scale=1.0,
                        nitro_active=nitro_on, is_human=veh.isHuman, show_shadow=True)

            # Name tag
            lbl_font = get_ui_font(size=10, bold=True)
            lbl_txt  = lbl_font.render(veh.name[:8], True, (230,230,230))
            surface.blit(lbl_txt, (px - lbl_txt.get_width()//2, py - 28))

    def _get_vehicle_screen_pos(self, veh: Vehicle) -> Optional[Tuple[float, float]]:
        u = self.circuit.graph.get_vertex(veh.currentVertex)
        if u is None:
            return None
        if veh.targetVertex is None or veh.state in (VehicleState.FINISHED, VehicleState.DNF, VehicleState.IDLE):
            return (u.x, u.y)
        v = self.circuit.graph.get_vertex(veh.targetVertex)
        if v is None:
            return (u.x, u.y)
        prog   = max(0.0, min(1.0, veh.progress))
        cur_x  = u.x + (v.x - u.x) * prog
        cur_y  = u.y + (v.y - u.y) * prog
        return (cur_x, cur_y)

    def _get_vehicle_angle(self, veh: Vehicle) -> float:
        """Compute heading angle of vehicle based on edge direction."""
        u = self.circuit.graph.get_vertex(veh.currentVertex)
        if u is None or veh.targetVertex is None:
            return 0.0
        v = self.circuit.graph.get_vertex(veh.targetVertex)
        if v is None:
            return 0.0
        return math.atan2(v.y - u.y, v.x - u.x)

    def _draw_countdown(self, surface: pygame.Surface, W: int, H: int) -> None:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 160), overlay.get_rect())
        surface.blit(overlay, (0, 0))

        n = max(1, int(math.ceil(self._countdown)))
        label = str(n) if self._countdown > 0.3 else "GO!"
        col   = (0, 240, 100) if label == "GO!" else TEXT_GOLD

        font  = get_font(size=120, bold=True)
        pulse = abs(math.sin(self._countdown * math.pi))
        s     = int(100 + 20 * pulse)
        font_big = get_font(size=s, bold=True)
        txt = font_big.render(label, True, col)
        surface.blit(txt, txt.get_rect(center=(W//2, H//2)))

    def _draw_pause_overlay(self, surface: pygame.Surface, W: int, H: int) -> None:
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 0, 140), overlay.get_rect())
        surface.blit(overlay, (0, 0))
        txt = get_font(size=56, bold=True).render("PAUSED", True, TEXT_ACCENT)
        surface.blit(txt, txt.get_rect(center=(W//2, H//2 - 20)))
        sub = get_ui_font(size=18).render("Press  P  or  ESC  to resume", True, TEXT_WHITE)
        surface.blit(sub, sub.get_rect(center=(W//2, H//2 + 42)))
