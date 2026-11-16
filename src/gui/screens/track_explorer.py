"""src/gui/screens/track_explorer.py — Screen 2: Track Explorer & Route Planner (Section 2.1).
Compares BFS, DFS, Dijkstra, and A* shortest paths under Balanced, Speed, Economy, and Safety presets.
"""

from typing import Callable, Dict, List, Optional
import pygame
from src.core.graph import Graph
from src.core.bfs import BFS
from src.core.dfs import DFS
from src.core.dijkstra import Dijkstra
from src.core.astar import AStar
from src.models.circuit import Circuit
from src.models.edge import RoutingPreset
from src.data.circuits import ALL_CIRCUITS
from src.gui.components.button import Button
from src.gui.components.graph_renderer import GraphRenderer
from src.gui.assets.colors import BG_DARK, PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_MUTED, TEXT_ACCENT
from src.gui.assets.fonts import get_font


class TrackExplorerScreen:
    """Screen 2: Interactive circuit analysis, route planning, and algorithm comparison."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.circuit_idx: int = 0
        self.circuit: Circuit = ALL_CIRCUITS[0]()
        self.renderer = GraphRenderer(pygame.display.get_surface(), self.circuit.graph)

        self.start_vid: int = self.circuit.start_vertex_id
        self.target_vid: int = self.circuit.checkpoint_ids[4]
        self.preset: RoutingPreset = RoutingPreset.BALANCED

        self.dijkstra_res: Optional[Dict] = None
        self.astar_res: Optional[Dict] = None
        self.active_algo: str = "Dijkstra"

        # Buttons
        self.buttons: List[Button] = [
            Button((20, 20, 110, 34), "← MENU", lambda: self.switch_screen("main_menu", {})),
            Button((140, 20, 120, 34), "RUN BFS", lambda: self._run_bfs()),
            Button((270, 20, 120, 34), "RUN DFS", lambda: self._run_dfs()),
            Button((400, 20, 140, 34), "RUN DIJKSTRA", lambda: self._run_dijkstra()),
            Button((550, 20, 120, 34), "RUN A*", lambda: self._run_astar()),
            
            # Presets
            Button((20, 480, 110, 30), "Balanced", lambda: self._set_preset(RoutingPreset.BALANCED)),
            Button((140, 480, 110, 30), "Speed", lambda: self._set_preset(RoutingPreset.SPEED)),
            Button((20, 520, 110, 30), "Economy", lambda: self._set_preset(RoutingPreset.ECONOMY)),
            Button((140, 520, 110, 30), "Safety", lambda: self._set_preset(RoutingPreset.SAFETY)),
        ]
        self._update_preset_buttons()
        self._run_dijkstra()

    def set_context(self, context: Dict) -> None:
        self.circuit_idx = context.get("circuit_idx", 0)
        self.circuit = ALL_CIRCUITS[self.circuit_idx]()
        self.renderer = GraphRenderer(pygame.display.get_surface(), self.circuit.graph)
        self.start_vid = self.circuit.start_vertex_id
        self.target_vid = self.circuit.checkpoint_ids[min(4, len(self.circuit.checkpoint_ids) - 1)]
        self._run_dijkstra()

    def _set_preset(self, preset: RoutingPreset) -> None:
        self.preset = preset
        self._update_preset_buttons()
        if self.active_algo == "Dijkstra":
            self._run_dijkstra()
        elif self.active_algo == "A*":
            self._run_astar()

    def _update_preset_buttons(self) -> None:
        self.buttons[5].is_active = (self.preset == RoutingPreset.BALANCED)
        self.buttons[6].is_active = (self.preset == RoutingPreset.SPEED)
        self.buttons[7].is_active = (self.preset == RoutingPreset.ECONOMY)
        self.buttons[8].is_active = (self.preset == RoutingPreset.SAFETY)

    def _run_dijkstra(self) -> None:
        self.active_algo = "Dijkstra"
        d = Dijkstra(self.circuit.graph)
        self.dijkstra_res = d.run(self.start_vid, self.target_vid, preset=self.preset)
        self.renderer.set_path_highlight(self.dijkstra_res["path"], color=(0, 150, 255))

    def _run_astar(self) -> None:
        self.active_algo = "A*"
        a = AStar(self.circuit.graph)
        self.astar_res = a.run(self.start_vid, self.target_vid, preset=self.preset)
        self.renderer.set_path_highlight(self.astar_res["path"], color=(50, 220, 120))

    def _run_bfs(self) -> None:
        self.active_algo = "BFS"
        b = BFS(self.circuit.graph)
        res = b.run(self.start_vid, self.target_vid)
        self.renderer.set_path_highlight(res["path"], color=(255, 180, 0))

    def _run_dfs(self) -> None:
        self.active_algo = "DFS"
        d = DFS(self.circuit.graph)
        paths = d.find_bounded_paths(self.start_vid, self.target_vid, max_depth=15, max_paths=1)
        path = paths[0] if paths else []
        self.renderer.set_path_highlight(path, color=(220, 80, 220))

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

        # Allow user to click vertices on the map to set Start or Target
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for vid, v in self.circuit.graph.vertices.items():
                if (mx - v.x) ** 2 + (my - v.y) ** 2 <= 16 ** 2:
                    if vid != self.start_vid:
                        self.target_vid = vid
                        if self.active_algo == "Dijkstra":
                            self._run_dijkstra()
                        elif self.active_algo == "A*":
                            self._run_astar()
                        elif self.active_algo == "BFS":
                            self._run_bfs()
                        else:
                            self._run_dfs()
                    break

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self.renderer.surface = surface

        # Draw Graph
        self.renderer.draw()

        # Draw Navigation Buttons
        for btn in self.buttons:
            btn.draw(surface)

        # Left Analytics Panel
        panel = pygame.Rect(20, 70, 250, 390)
        pygame.draw.rect(surface, PANEL_BG, panel, border_radius=8)
        pygame.draw.rect(surface, PANEL_BORDER, panel, width=1, border_radius=8)

        font_hdr = get_font(size=15, bold=True)
        font_body = get_font(size=12, bold=True)
        font_sm = get_font(size=11)

        surface.blit(font_hdr.render("ROUTE PLANNER", True, TEXT_ACCENT), (32, 80))
        surface.blit(font_sm.render(f"Circuit: {self.circuit.name}", True, TEXT_MUTED), (32, 102))
        surface.blit(font_body.render(f"From: V{self.start_vid}  →  To: V{self.target_vid}", True, (255, 200, 0)), (32, 122))
        surface.blit(font_sm.render("(Click any node to change destination)", True, TEXT_MUTED), (32, 142))

        # Metrics for active algorithm
        surface.blit(font_hdr.render(f"ACTIVE: {self.active_algo}", True, (50, 220, 120)), (32, 175))
        
        path_len = len(self.renderer.highlighted_path)
        cost_str = f"Path Nodes: {path_len}"
        surface.blit(font_sm.render(cost_str, True, TEXT_WHITE), (32, 200))

        if self.dijkstra_res and self.active_algo == "Dijkstra":
            stats = self.dijkstra_res["stats"]
            surface.blit(font_sm.render(f"Scalar Cost: {self.dijkstra_res['cost']:.3f}", True, TEXT_WHITE), (32, 220))
            surface.blit(font_sm.render(f"Nodes Expanded: {stats['expanded_vertices']}", True, TEXT_WHITE), (32, 240))
            surface.blit(font_sm.render(f"Edges Relaxed: {stats['relaxed_edges']}", True, TEXT_WHITE), (32, 260))
            surface.blit(font_sm.render(f"Heap Ops: {stats['heap_operations']}", True, TEXT_WHITE), (32, 280))
            surface.blit(font_sm.render(f"Runtime: {stats['execution_time_us']:.1f} μs", True, TEXT_WHITE), (32, 300))

        elif self.astar_res and self.active_algo == "A*":
            stats = self.astar_res["stats"]
            surface.blit(font_sm.render(f"Scalar Cost: {self.astar_res['cost']:.3f}", True, TEXT_WHITE), (32, 220))
            surface.blit(font_sm.render(f"Nodes Expanded: {stats['expanded_vertices']}", True, TEXT_WHITE), (32, 240))
            surface.blit(font_sm.render(f"Edges Relaxed: {stats['relaxed_edges']}", True, TEXT_WHITE), (32, 260))
            surface.blit(font_sm.render(f"Heap Ops: {stats['heap_operations']}", True, TEXT_WHITE), (32, 280))
            surface.blit(font_sm.render(f"Runtime: {stats['execution_time_us']:.1f} μs", True, TEXT_WHITE), (32, 300))

        # Preset Selector Header
        surface.blit(font_hdr.render("COST PRESETS:", True, TEXT_ACCENT), (32, 455))
