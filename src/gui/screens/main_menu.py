"""src/gui/screens/main_menu.py — Main Menu & Circuit Selector (Section 2.1).
"""

from typing import Callable, Dict, List
import pygame
from src.gui.components.button import Button
from src.gui.assets.colors import BG_DARK, PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_MUTED, TEXT_ACCENT
from src.gui.assets.fonts import get_font


class MainMenuScreen:
    """Screen 1: Main Menu for mode selection, circuit configuration, and student credits."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.selected_circuit_idx: int = 0
        self.circuit_names = [
            ("Circuit 1: Alpha Ring", "Perimeter oval with high-risk central chord shortcuts and dead-end canyon."),
            ("Circuit 2: Beta Delta", "Figure-8 crossover circuit with double loops and bypass bridges."),
            ("Circuit 3: Gamma Grid", "Complex downtown street grid with one-way thoroughfares and diagonal alleys.")
        ]

        self.buttons: List[Button] = [
            Button((490, 290, 300, 44), "START RACE (Quick Race)", lambda: self._start_race(quick=True)),
            Button((490, 345, 300, 44), "TRACK EXPLORER / PLANNER", lambda: self.switch_screen("track_explorer", {"circuit_idx": self.selected_circuit_idx})),
            Button((490, 400, 300, 44), "ALGORITHM LAB (Visualizer)", lambda: self.switch_screen("algorithm_lab", {"circuit_idx": self.selected_circuit_idx})),
            Button((490, 455, 300, 44), "CHAMPIONSHIP STANDINGS", lambda: self.switch_screen("dashboard", {})),
            
            # Circuit selector buttons
            Button((240, 560, 240, 38), "Alpha Ring", lambda: self._select_circuit(0)),
            Button((520, 560, 240, 38), "Beta Delta", lambda: self._select_circuit(1)),
            Button((800, 560, 240, 38), "Gamma Grid", lambda: self._select_circuit(2)),
        ]
        self._update_circuit_buttons()

    def _select_circuit(self, idx: int) -> None:
        self.selected_circuit_idx = idx
        self._update_circuit_buttons()

    def _update_circuit_buttons(self) -> None:
        self.buttons[4].is_active = (self.selected_circuit_idx == 0)
        self.buttons[5].is_active = (self.selected_circuit_idx == 1)
        self.buttons[6].is_active = (self.selected_circuit_idx == 2)

    def _start_race(self, quick: bool = True) -> None:
        self.switch_screen("racing", {"circuit_idx": self.selected_circuit_idx, "laps": 2})

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

    def update(self, dt: float) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)

        # Title Card
        title_font = get_font(size=36, bold=True)
        sub_font = get_font(size=16)
        team_font = get_font(size=14, bold=True)

        txt_title = title_font.render("SMART RACING CHAMPIONSHIP", True, TEXT_ACCENT)
        surface.blit(txt_title, txt_title.get_rect(center=(640, 100)))

        txt_sub = sub_font.render("Design and Analysis of Algorithms — Semester 5 Final Project", True, TEXT_MUTED)
        surface.blit(txt_sub, txt_sub.get_rect(center=(640, 140)))

        # Group Members Banner
        members_str = "Group: Muhammad Aoun (24P-3099) | Abdullah Mohzar (24I-3124) | Muhammad Sarim (24I-3069)"
        txt_team = team_font.render(members_str, True, (220, 230, 250))
        surface.blit(txt_team, txt_team.get_rect(center=(640, 180)))

        # Center Menu Panel
        menu_card = pygame.Rect(440, 250, 400, 270)
        pygame.draw.rect(surface, PANEL_BG, menu_card, border_radius=10)
        pygame.draw.rect(surface, PANEL_BORDER, menu_card, width=1, border_radius=10)

        # Draw Buttons
        for btn in self.buttons:
            btn.draw(surface)

        # Circuit Description Box
        name, desc = self.circuit_names[self.selected_circuit_idx]
        desc_box = pygame.Rect(200, 615, 880, 55)
        pygame.draw.rect(surface, PANEL_BG, desc_box, border_radius=8)
        pygame.draw.rect(surface, PANEL_BORDER, desc_box, width=1, border_radius=8)

        lbl_cname = get_font(size=14, bold=True).render(f"SELECTED: {name}", True, (255, 200, 0))
        lbl_cdesc = get_font(size=12).render(desc, True, TEXT_WHITE)
        surface.blit(lbl_cname, (220, 622))
        surface.blit(lbl_cdesc, (220, 644))
