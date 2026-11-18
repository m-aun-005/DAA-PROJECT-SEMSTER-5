"""src/gui/screens/instructions.py — How to Play / Instructions Screen."""

from typing import Callable, Dict
import pygame
from src.gui.assets.colors import BG_DARK, PANEL_BG, TEXT_WHITE, TEXT_ACCENT, TEXT_GOLD, TEXT_MUTED, PANEL_BORDER
from src.gui.assets.fonts import get_font, get_ui_font
from src.gui.components.button import Button

SECTIONS = [
    {
        "title": "CONTROLS",
        "accent": (0, 200, 255),
        "items": [
            ("ARROW KEYS / WASD",   "Steer your car at junctions"),
            ("SPACE",               "Activate Nitro Boost"),
            ("P  or  ESC",         "Pause / Resume race"),
            ("R",                   "Restart race"),
            ("Mouse Click",         "Navigate menus and select options"),
        ],
    },
    {
        "title": "GAMEPLAY",
        "accent": (255, 160, 0),
        "items": [
            ("Checkpoints",         "Hit all mandatory checkpoints in order to complete a lap"),
            ("Fuel Stations",       "Stop at fuel nodes before your tank runs dry"),
            ("Nitro Pickups",       "Collect lightning bolt nodes to gain Nitro charges"),
            ("Road Hazards",        "Some roads become blocked mid-race — reroute fast"),
            ("Laps",                "Complete the required laps before your opponents"),
        ],
    },
    {
        "title": "CHAMPIONSHIP",
        "accent": (255, 200, 0),
        "items": [
            ("Seasons",             "5 seasons of increasing difficulty and prize cars"),
            ("Points System",       "P1=25, P2=18, P3=15, P4=12, P5=10, P6=8, P7=6, P8=4"),
            ("Car Classes",         "Some seasons require specific car classes (GT, Muscle, Open)"),
            ("Unlock Cars",         "Win seasons to unlock legendary cars for your garage"),
            ("Season Title",        "Score the most points across all season rounds to win"),
        ],
    },
    {
        "title": "ALGORITHMS (Academic)",
        "accent": (100, 180, 255),
        "items": [
            ("Dijkstra / A*",       "AI opponents find optimal routes using weighted graphs"),
            ("BFS / DFS",           "Circuit analysis: reachability, components, dead-ends"),
            ("Knapsack DP",         "Optimal pickup selection within fuel detour budget"),
            ("Kruskal / Prim MST",  "Minimum spanning tree backbone for the circuit graph"),
            ("Min-Heap / Sorting",  "Event scheduling and championship leaderboard ranking"),
        ],
    },
    {
        "title": "TIPS & TRICKS",
        "accent": (50, 220, 100),
        "items": [
            ("Shortcuts",           "Orange edges are shortcuts — high risk, high reward"),
            ("Slipstream",          "Draft close behind opponents on long straights"),
            ("Nitro Timing",        "Save all 3 Nitro charges for the final lap's straights"),
            ("Algorithm Lab",       "Use Race Explorer to plan the best route before racing"),
            ("Car Choice",          "High-handling cars shine on Gamma Grid; speed on Alpha Ring"),
        ],
    },
]


class InstructionsScreen:
    """How to play screen with tabbed sections."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen  = switch_screen
        self.active_section = 0
        self.time           = 0.0

        self._btn_back = Button((20, 20, 110, 36), "← BACK",
                                callback=lambda: self.switch_screen("main_menu", {}), font_size=14)
        # Tab buttons
        self._tab_rects = []
        tab_w = 220
        for i in range(len(SECTIONS)):
            self._tab_rects.append(pygame.Rect(60 + i*(tab_w+10), 90, tab_w, 42))

    def handle_event(self, event: pygame.event.Event) -> None:
        self._btn_back.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._tab_rects):
                if r.collidepoint(event.pos):
                    self.active_section = i
                    break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                self.active_section = (self.active_section + 1) % len(SECTIONS)
            elif event.key == pygame.K_LEFT:
                self.active_section = (self.active_section - 1) % len(SECTIONS)

    def update(self, dt: float) -> None:
        self.time += dt
        self._btn_back.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        W, H = surface.get_size()
        surface.fill(BG_DARK)
        self._draw_bg(surface, W, H)

        # Main header
        hdr = get_font(size=36, bold=True).render("HOW TO PLAY", True, TEXT_WHITE)
        surface.blit(hdr, hdr.get_rect(center=(W//2, 46)))

        # Tabs
        for i, (r, sec) in enumerate(zip(self._tab_rects, SECTIONS)):
            is_active = (i == self.active_section)
            bg_col = sec["accent"] if is_active else (20, 24, 38)
            pygame.draw.rect(surface, bg_col, r, border_radius=8)
            if not is_active:
                pygame.draw.rect(surface, (38, 46, 68), r, width=1, border_radius=8)
            tab_txt = get_ui_font(size=12, bold=True).render(
                sec["title"], True, (10, 10, 10) if is_active else TEXT_MUTED)
            surface.blit(tab_txt, tab_txt.get_rect(center=r.center))

        # Content card
        sec    = SECTIONS[self.active_section]
        accent = sec["accent"]
        card   = pygame.Rect(60, 148, W - 120, H - 200)

        card_surf = pygame.Surface(card.size, pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (12, 15, 28, 230), card_surf.get_rect(), border_radius=14)
        surface.blit(card_surf, card.topleft)
        pygame.draw.rect(surface, accent, (card.x, card.y, card.width, 5), border_radius=14)
        pygame.draw.rect(surface, (38, 46, 68), card, width=1, border_radius=14)

        # Section title
        title_txt = get_font(size=26, bold=True).render(sec["title"], True, accent)
        surface.blit(title_txt, (card.x + 30, card.y + 24))
        pygame.draw.line(surface, (38, 46, 68),
                         (card.x+30, card.y+58), (card.right-30, card.y+58), 1)

        # Items
        key_f = get_ui_font(size=15, bold=True)
        val_f = get_ui_font(size=15)
        for i, (key, val) in enumerate(sec["items"]):
            iy = card.y + 72 + i * 72

            # Item background strip
            item_surf = pygame.Surface((card.width - 60, 56), pygame.SRCALPHA)
            pygame.draw.rect(item_surf, (20, 26, 44, 200), item_surf.get_rect(), border_radius=10)
            surface.blit(item_surf, (card.x + 30, iy))

            # Accent bullet
            pygame.draw.rect(surface, accent, (card.x+30, iy+8, 4, 40), border_radius=2)

            key_txt = key_f.render(key, True, TEXT_WHITE)
            val_txt = val_f.render(val, True, TEXT_MUTED)
            surface.blit(key_txt, (card.x + 48, iy + 10))
            surface.blit(val_txt, (card.x + 48, iy + 32))

        # Page dots
        for i in range(len(SECTIONS)):
            col = accent if i == self.active_section else (38, 46, 68)
            pygame.draw.circle(surface, col, (W//2 - len(SECTIONS)*16 + i*32, H - 28), 7)

        self._btn_back.draw(surface)

    def _draw_bg(self, surface: pygame.Surface, W: int, H: int) -> None:
        for x in range(-H, W+H, 90):
            ls = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.line(ls, (100, 180, 255, 7), (x, 0), (x-H, H), 1)
            surface.blit(ls, (0, 0))
