"""src/gui/screens/algorithm_lab.py — Screen 4: Integrated Algorithm Lab & Visualizer (Section 2.1 & 6).
Calls the EXACT SAME production algorithm classes as gameplay:
BFS, DFS, Dijkstra, A*, Kruskal, Prim, Knapsack DP, and Sorting Suite.
"""

from typing import Callable, Dict, Generator, List, Optional, Set
import pygame
from src.core.graph import Graph
from src.core.bfs import BFS
from src.core.dfs import DFS
from src.core.dijkstra import Dijkstra
from src.core.astar import AStar
from src.core.mst import KruskalMST, PrimMST
from src.core.knapsack_dp import KnapsackDP, KnapsackItem
from src.core.sorting import MergeSort, QuickSort3Way, HeapSortAlgo
from src.data.circuits import ALL_CIRCUITS
from src.models.circuit import Circuit
from src.gui.components.button import Button
from src.gui.components.graph_renderer import GraphRenderer
from src.gui.assets.colors import BG_DARK, PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_MUTED, TEXT_ACCENT
from src.gui.assets.fonts import get_font


class AlgorithmLabScreen:
    """Screen 4: Step-by-step interactive debugger and visualizer for all algorithms."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.circuit_idx: int = 0
        self.circuit: Circuit = ALL_CIRCUITS[0]()
        self.renderer = GraphRenderer(pygame.display.get_surface(), self.circuit.graph)

        self.selected_algo: str = "Dijkstra"
        self.generator: Optional[Generator] = None
        self.current_state: Dict = {}
        self.is_playing: bool = False
        self.step_timer: float = 0.0
        self.step_delay: float = 0.25  # seconds per step
        self.step_count: int = 0
        self.is_done: bool = False

        # Navigation & Control Buttons
        self.buttons: List[Button] = [
            Button((20, 20, 110, 32), "← MENU", lambda: self.switch_screen("main_menu", {})),
            Button((140, 20, 100, 32), "STEP ▶", lambda: self._step_algorithm()),
            Button((250, 20, 100, 32), "PLAY", lambda: self._toggle_play()),
            Button((360, 20, 100, 32), "RESET", lambda: self._reset_algorithm()),
            
            # Algorithm Selector Buttons (Column on left)
            Button((20, 110, 130, 30), "Dijkstra", lambda: self._select_algo("Dijkstra")),
            Button((20, 145, 130, 30), "A* Search", lambda: self._select_algo("A*")),
            Button((20, 180, 130, 30), "BFS", lambda: self._select_algo("BFS")),
            Button((20, 215, 130, 30), "DFS", lambda: self._select_algo("DFS")),
            Button((20, 250, 130, 30), "Kruskal MST", lambda: self._select_algo("Kruskal")),
            Button((20, 285, 130, 30), "Prim MST", lambda: self._select_algo("Prim")),
            Button((20, 320, 130, 30), "Knapsack DP", lambda: self._select_algo("Knapsack")),
            Button((20, 355, 130, 30), "Sorting Suite", lambda: self._select_algo("Sorting")),
        ]
        self._update_algo_buttons()
        self._init_algorithm()

    def set_context(self, context: Dict) -> None:
        self.circuit_idx = context.get("circuit_idx", 0)
        self.circuit = ALL_CIRCUITS[self.circuit_idx]()
        self.renderer = GraphRenderer(pygame.display.get_surface(), self.circuit.graph)
        self._init_algorithm()

    def _select_algo(self, algo_name: str) -> None:
        self.selected_algo = algo_name
        self._update_algo_buttons()
        self._init_algorithm()

    def _update_algo_buttons(self) -> None:
        algos = ["Dijkstra", "A*", "BFS", "DFS", "Kruskal", "Prim", "Knapsack", "Sorting"]
        for idx, name in enumerate(algos):
            self.buttons[4 + idx].is_active = (self.selected_algo == name)

    def _init_algorithm(self) -> None:
        self.renderer.clear_highlights()
        self.is_done = False
        self.step_count = 0
        self.is_playing = False
        self.buttons[2].text = "PLAY"
        
        start_v = self.circuit.start_vertex_id
        target_v = self.circuit.checkpoint_ids[4]

        if self.selected_algo == "Dijkstra":
            d = Dijkstra(self.circuit.graph)
            self.generator = d.step_generator(start_v, target_v)
        elif self.selected_algo == "A*":
            a = AStar(self.circuit.graph)
            self.generator = a.step_generator(start_v, target_v)
        elif self.selected_algo == "BFS":
            b = BFS(self.circuit.graph)
            self.generator = b.step_generator(start_v, target_v)
        elif self.selected_algo == "DFS":
            dfs = DFS(self.circuit.graph)
            self.generator = dfs.step_generator(start_v)
        elif self.selected_algo == "Kruskal":
            km = KruskalMST(self.circuit.graph)
            self.generator = km.step_generator()
        elif self.selected_algo == "Prim":
            # Direct run with MST highlight
            pm = PrimMST(self.circuit.graph)
            res = pm.run(start_v)
            self.renderer.set_mst_highlight(res["mst_edges"])
            self.current_state = {"done": True, "stats": pm.get_stats()}
            self.is_done = True
            return
        elif self.selected_algo == "Knapsack":
            dp = KnapsackDP()
            items = [
                KnapsackItem(1, "Nitro 1", 6, 30),
                KnapsackItem(2, "Nitro 2", 5, 24),
                KnapsackItem(3, "Nitro 3", 5, 24),
                KnapsackItem(4, "Boost", 8, 40),
            ]
            res = dp.solve(items, budget=10)
            self.current_state = res
            self.is_done = True
            return
        elif self.selected_algo == "Sorting":
            ms = MergeSort()
            qs = QuickSort3Way()
            hs = HeapSortAlgo()
            sample = [45, 12, 85, 32, 89, 39, 69, 44, 42, 1, 10, 20]
            r1 = ms.sort(sample)
            r2 = qs.sort(sample)
            r3 = hs.sort(sample)
            self.current_state = {
                "original": sample,
                "merge_sorted": r1,
                "merge_cmp": ms.comparisons,
                "quick_cmp": qs.comparisons,
                "heap_cmp": hs.comparisons,
                "done": True
            }
            self.is_done = True
            return

        self._step_algorithm()

    def _step_algorithm(self) -> None:
        if self.generator is None or self.is_done:
            return
        try:
            state = next(self.generator)
            self.current_state = state
            self.step_count += 1
            
            # Update renderer highlights
            visited = state.get("visited", set())
            frontier = set()
            if "pq" in state:
                frontier = {item[1] for item in state["pq"]}
            elif "queue" in state:
                frontier = set(state["queue"])
            elif "stack" in state:
                frontier = set(state["stack"])

            cur = state.get("current")
            self.renderer.set_algorithm_state(visited, frontier, cur)

            if "mst_edges" in state:
                self.renderer.set_mst_highlight(state["mst_edges"])

            if state.get("done", False):
                self.is_done = True
                self.is_playing = False
                self.buttons[2].text = "PLAY"
        except StopIteration:
            self.is_done = True
            self.is_playing = False
            self.buttons[2].text = "PLAY"

    def _toggle_play(self) -> None:
        self.is_playing = not self.is_playing
        self.buttons[2].text = "PAUSE" if self.is_playing else "PLAY"

    def _reset_algorithm(self) -> None:
        self._init_algorithm()

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._step_algorithm()

    def update(self, dt: float) -> None:
        if self.is_playing and not self.is_done:
            self.step_timer += dt
            if self.step_timer >= self.step_delay:
                self.step_timer = 0.0
                self._step_algorithm()

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self.renderer.surface = surface

        # 1. Draw Graph on Right / Center
        self.renderer.draw()

        # 2. Draw Navigation Buttons
        for btn in self.buttons:
            btn.draw(surface)

        # 3. Algorithm Statistics Card (Bottom Left)
        stats_rect = pygame.Rect(20, 400, 240, 290)
        pygame.draw.rect(surface, PANEL_BG, stats_rect, border_radius=8)
        pygame.draw.rect(surface, PANEL_BORDER, stats_rect, width=1, border_radius=8)

        f_hdr = get_font(size=14, bold=True)
        f_b = get_font(size=12, bold=True)
        f_s = get_font(size=11)

        surface.blit(f_hdr.render("ALGORITHM LAB", True, TEXT_ACCENT), (32, 410))
        surface.blit(f_b.render(f"Algo: {self.selected_algo}", True, (255, 200, 0)), (32, 430))
        surface.blit(f_s.render(f"Step Count: {self.step_count}", True, TEXT_WHITE), (32, 452))
        surface.blit(f_s.render("Status: " + ("COMPLETED" if self.is_done else "RUNNING..."), True, (50, 220, 100) if self.is_done else (240, 180, 20)), (32, 472))

        # Operation Counters Display
        y = 500
        stats = self.current_state.get("stats", {})
        if stats:
            surface.blit(f_hdr.render("OPERATION COUNTERS:", True, TEXT_ACCENT), (32, y))
            y += 22
            for k, val in stats.items():
                lbl = k.replace("_", " ").title()
                surface.blit(f_s.render(f"{lbl}: {val}", True, TEXT_WHITE), (32, y))
                y += 20
        elif self.selected_algo == "Knapsack":
            surface.blit(f_hdr.render("KNAPSACK DP RESULTS:", True, TEXT_ACCENT), (32, y))
            y += 22
            surface.blit(f_s.render(f"Total Benefit: {self.current_state.get('total_benefit', 0)}", True, (50, 220, 100)), (32, y))
            y += 20
            surface.blit(f_s.render(f"Table Entries: {self.current_state.get('table_entries_evaluated', 0)}", True, TEXT_WHITE), (32, y))
            y += 20
            surface.blit(f_s.render(f"Runtime: {self.current_state.get('execution_time_us', 0)} μs", True, TEXT_WHITE), (32, y))
        elif self.selected_algo == "Sorting":
            surface.blit(f_hdr.render("SORT COMPARISONS:", True, TEXT_ACCENT), (32, y))
            y += 22
            surface.blit(f_s.render(f"Merge Sort Cmp: {self.current_state.get('merge_cmp', 0)}", True, TEXT_WHITE), (32, y))
            y += 20
            surface.blit(f_s.render(f"Quick 3-Way Cmp: {self.current_state.get('quick_cmp', 0)}", True, TEXT_WHITE), (32, y))
            y += 20
            surface.blit(f_s.render(f"Heap Sort Cmp: {self.current_state.get('heap_cmp', 0)}", True, TEXT_WHITE), (32, y))
