"""src/gui/screens/dashboard.py — Screen 5: Championship Leaderboard & Sorting Suite (Section 2.1 & 5.5).
Compares Merge Sort, Quick Sort (3-Way), Heap Sort, and Size-k Priority Queue
under the unified multi-tier championship comparator.
"""

from typing import Callable, Dict, List, Optional
import pygame
from src.models.leaderboard import RaceResult, ChampionshipEntry
from src.core.sorting import MergeSort, QuickSort3Way, HeapSortAlgo, TopKHeap
from src.gui.components.button import Button
from src.gui.assets.colors import BG_DARK, PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_MUTED, TEXT_ACCENT
from src.gui.assets.fonts import get_font, get_ui_font


class DashboardScreen:
    """Screen 5: Post-race podium, season leaderboard, and sorting algorithm benchmarking."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.results: List[RaceResult] = []
        self.entries: List[ChampionshipEntry] = self._create_sample_entries()
        
        # Sorting algorithms
        self.merge_sorter = MergeSort()
        self.quick_sorter = QuickSort3Way()
        self.heap_sorter = HeapSortAlgo()
        self.topk_heap = TopKHeap()

        self.active_sort_method: str = "Merge Sort"
        self.sorted_entries: List[ChampionshipEntry] = []
        self.sort_stats: Dict[str, Dict] = {}

        self.buttons: List[Button] = [
            Button((20, 20, 110, 34), "← MENU", lambda: self.switch_screen("main_menu", {})),
            Button((140, 20, 120, 34), "RACE AGAIN", lambda: self.switch_screen("racing", {})),
            
            # Sorting algorithm comparison tabs
            Button((450, 20, 140, 34), "Merge Sort", lambda: self._select_sort("Merge Sort")),
            Button((600, 20, 140, 34), "Quick Sort (3W)", lambda: self._select_sort("Quick Sort")),
            Button((750, 20, 140, 34), "Heap Sort", lambda: self._select_sort("Heap Sort")),
            Button((900, 20, 140, 34), "Top-3 (Min-Heap)", lambda: self._select_sort("Top-k Heap")),
        ]
        self._select_sort("Merge Sort")

    def _create_sample_entries(self) -> List[ChampionshipEntry]:
        """Creates championship entries from the persistent scoreboard (no fake players)."""
        try:
            from src.gui.screens.scoreboard import _load_scores
            scores = _load_scores()
            entries = []
            for i, row in enumerate(scores):
                lap_str = row.get("best_lap", "—")
                if lap_str != "—" and ":" in lap_str:
                    try:
                        m, s = lap_str.split(":")
                        best_lap = float(m) * 60 + float(s)
                    except Exception:
                        best_lap = 45.0 + i * 1.5
                else:
                    best_lap = 45.0 + i * 1.5

                ce = ChampionshipEntry(
                    racerId=i + 1,
                    name=row["name"],
                    totalPoints=row["pts"],
                    wins=row["wins"],
                    sumOfFinishPositions=row["rank"] * max(1, row["races"]),
                    bestFastestLap=best_lap
                )
                entries.append(ce)
            return entries
        except Exception:
            entries = []
            cars = ["YOU", "Chick Hicks (AI)", "The King (AI)", "Doc Hudson (AI)",
                    "Jackson Storm (AI)", "Sally Carrera (AI)", "Ramone (AI)", "Tow Mater (AI)"]
            for i, name in enumerate(cars):
                ce = ChampionshipEntry(
                    racerId=i + 1,
                    name=name,
                    totalPoints=0,
                    wins=0,
                    sumOfFinishPositions=i + 1,
                    bestFastestLap=45.0 + i * 1.5
                )
                entries.append(ce)
            return entries

    def set_context(self, context: Dict) -> None:
        new_res = context.get("results")
        if new_res:
            self.results = new_res

        # Persist championship scores (for BOTH player and AI bots) to global scoreboard JSON
        try:
            from src.gui.screens.scoreboard import save_championship_results
            if self.results:
                save_championship_results(
                    results=self.results,
                    player_car=context.get("car_name", "Lightning McQueen"),
                    vehicles=context.get("vehicles", [])
                )
        except Exception:
            pass  # Never crash the UI over scoreboard persistence

        # Reload live entries directly from persistent scoreboard
        self.entries = self._create_sample_entries()
        self._select_sort(self.active_sort_method)

    def _select_sort(self, method: str) -> None:
        self.active_sort_method = method
        self.buttons[2].is_active = (method == "Merge Sort")
        self.buttons[3].is_active = (method == "Quick Sort")
        self.buttons[4].is_active = (method == "Heap Sort")
        self.buttons[5].is_active = (method == "Top-k Heap")

        # Run all sorts with the exact same comparator (Section 4.6)
        key_fn = lambda ce: ce.sort_key()

        m_res = self.merge_sorter.sort(self.entries, key=key_fn)
        q_res = self.quick_sorter.sort(self.entries, key=key_fn)
        h_res = self.heap_sorter.sort(self.entries, key=key_fn)
        top3 = self.topk_heap.get_top_k(self.entries, k=3, key=key_fn)

        self.sort_stats = {
            "Merge Sort": {"time_ms": self.merge_sorter.execution_time_ms, "cmp": self.merge_sorter.comparisons, "stable": True},
            "Quick Sort": {"time_ms": self.quick_sorter.execution_time_ms, "cmp": self.quick_sorter.comparisons, "stable": False},
            "Heap Sort": {"time_ms": self.heap_sorter.execution_time_ms, "cmp": self.heap_sorter.comparisons, "stable": False},
            "Top-k Heap": {"time_ms": self.topk_heap.execution_time_ms, "cmp": self.topk_heap.comparisons, "size_k": 3},
        }

        if method == "Merge Sort":
            self.sorted_entries = m_res
        elif method == "Quick Sort":
            self.sorted_entries = q_res
        elif method == "Heap Sort":
            self.sorted_entries = h_res
        elif method == "Top-k Heap":
            self.sorted_entries = top3

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

    def update(self, dt: float) -> None:
        for btn in self.buttons:
            if hasattr(btn, "update"):
                btn.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)

        for btn in self.buttons:
            btn.draw(surface)

        # 1. Podium Display (Top 3)
        self._draw_podium(surface)

        # 2. Main Standings Table
        self._draw_leaderboard_table(surface)

        # 3. Sorting Benchmarking Analytics Card
        self._draw_sorting_analytics(surface)

    def _draw_podium(self, surface: pygame.Surface) -> None:
        f_name = get_font(size=14, bold=True)
        f_pts = get_font(size=12)

        # If race results are present, show the finishers of this race
        if self.results and len(self.results) >= 3:
            ranked = sorted(self.results, key=lambda r: (1 if r.dnf else 0, r.finishPosition if r.finishPosition else 999))
            p1_name = ranked[0].racerName
            p1_sub  = f"{ranked[0].finishTime:.1f}s" if not ranked[0].dnf else "DNF"
            p2_name = ranked[1].racerName
            p2_sub  = f"{ranked[1].finishTime:.1f}s" if not ranked[1].dnf else "DNF"
            p3_name = ranked[2].racerName
            p3_sub  = f"{ranked[2].finishTime:.1f}s" if not ranked[2].dnf else "DNF"
        elif len(self.sorted_entries) >= 3:
            p1_name = self.sorted_entries[0].name
            p1_sub  = f"{self.sorted_entries[0].totalPoints} Pts"
            p2_name = self.sorted_entries[1].name
            p2_sub  = f"{self.sorted_entries[1].totalPoints} Pts"
            p3_name = self.sorted_entries[2].name
            p3_sub  = f"{self.sorted_entries[2].totalPoints} Pts"
        else:
            return

        # 2nd Place (Silver)
        r2 = pygame.Rect(400, 140, 130, 80)
        pygame.draw.rect(surface, (180, 190, 200), r2, border_radius=6)
        txt2 = f_name.render("2nd", True, (30, 30, 40))
        surface.blit(txt2, txt2.get_rect(center=(r2.centerx, r2.y + 20)))
        n2 = f_pts.render(p2_name[:12], True, (20, 20, 30))
        surface.blit(n2, n2.get_rect(center=(r2.centerx, r2.y + 45)))
        s2 = f_pts.render(p2_sub, True, (40, 40, 50))
        surface.blit(s2, s2.get_rect(center=(r2.centerx, r2.y + 64)))

        # 1st Place (Gold)
        r1 = pygame.Rect(545, 110, 150, 110)
        pygame.draw.rect(surface, (255, 215, 0), r1, border_radius=8)
        txt1 = get_font(size=18, bold=True).render("1st WINNER", True, (30, 25, 0))
        surface.blit(txt1, txt1.get_rect(center=(r1.centerx, r1.y + 25)))
        n1 = f_name.render(p1_name[:14], True, (20, 20, 20))
        surface.blit(n1, n1.get_rect(center=(r1.centerx, r1.y + 55)))
        p1 = f_pts.render(p1_sub, True, (40, 40, 40))
        surface.blit(p1, p1.get_rect(center=(r1.centerx, r1.y + 80)))

        # 3rd Place (Bronze)
        r3 = pygame.Rect(710, 160, 130, 60)
        pygame.draw.rect(surface, (205, 127, 50), r3, border_radius=6)
        txt3 = f_name.render("3rd", True, (30, 30, 40))
        surface.blit(txt3, txt3.get_rect(center=(r3.centerx, r3.y + 18)))
        n3 = f_pts.render(p3_name[:12], True, (20, 20, 30))
        surface.blit(n3, n3.get_rect(center=(r3.centerx, r3.y + 40)))

    def _draw_leaderboard_table(self, surface: pygame.Surface) -> None:
        table_rect = pygame.Rect(100, 245, 780, 450)
        pygame.draw.rect(surface, PANEL_BG, table_rect, border_radius=8)
        pygame.draw.rect(surface, PANEL_BORDER, table_rect, width=1, border_radius=8)

        f_hdr = get_font(size=13, bold=True)
        f_row = get_font(size=12)

        # Table Headers
        headers = ["Pos", "Racer Name", "Points", "Wins", "Sum Pos", "Best Lap", "Tie-Break ID"]
        col_x = [120, 180, 380, 470, 560, 660, 770]

        for h, x in zip(headers, col_x):
            txt = f_hdr.render(h, True, TEXT_ACCENT)
            surface.blit(txt, (x, 260))

        pygame.draw.line(surface, PANEL_BORDER, (110, 285), (870, 285), 1)

        # Rows
        for i, entry in enumerate(self.sorted_entries[:10]):
            y = 295 + i * 36
            cols = [
                f"P{i+1}",
                entry.name,
                str(entry.totalPoints),
                str(entry.wins),
                str(entry.sumOfFinishPositions),
                f"{entry.bestFastestLap:.1f}s",
                f"ID #{entry.racerId}"
            ]
            for val, x in zip(cols, col_x):
                txt = f_row.render(val, True, TEXT_WHITE if i > 0 else (255, 220, 80))
                surface.blit(txt, (x, y))

    def _draw_sorting_analytics(self, surface: pygame.Surface) -> None:
        card = pygame.Rect(900, 245, 340, 450)
        pygame.draw.rect(surface, PANEL_BG, card, border_radius=8)
        pygame.draw.rect(surface, PANEL_BORDER, card, width=1, border_radius=8)

        f_hdr = get_font(size=15, bold=True)
        f_sub = get_font(size=13, bold=True)
        f_txt = get_font(size=12)

        surface.blit(f_hdr.render("SORTING BENCHMARK", True, TEXT_ACCENT), (920, 260))
        surface.blit(f_txt.render("Unified Comparator (Sec 4.6):", True, TEXT_MUTED), (920, 285))
        surface.blit(f_txt.render("1. Points (Desc)", True, TEXT_WHITE), (930, 305))
        surface.blit(f_txt.render("2. Wins (Desc)", True, TEXT_WHITE), (930, 325))
        surface.blit(f_txt.render("3. Sum of Finish Pos (Asc)", True, TEXT_WHITE), (930, 345))
        surface.blit(f_txt.render("4. Best Fastest Lap (Asc)", True, TEXT_WHITE), (930, 365))
        surface.blit(f_txt.render("5. Racer ID (Asc)", True, (255, 200, 0)), (930, 385))

        pygame.draw.line(surface, PANEL_BORDER, (910, 415), (1230, 415), 1)

        surface.blit(f_sub.render(f"ACTIVE: {self.active_sort_method}", True, (50, 220, 100)), (920, 430))

        y = 460
        for method, st in self.sort_stats.items():
            surface.blit(f_sub.render(method, True, TEXT_ACCENT), (920, y))
            y += 20
            surface.blit(f_txt.render(f"Comparisons: {st.get('cmp', 0)}", True, TEXT_WHITE), (930, y))
            y += 18
            surface.blit(f_txt.render(f"Runtime: {st.get('time_ms', 0):.3f} ms", True, TEXT_WHITE), (930, y))
            y += 24
