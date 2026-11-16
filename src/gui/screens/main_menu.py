"""src/gui/screens/main_menu.py — Asphalt 8-style Main Menu Screen.

Cinematic dark skyline background, animated racing car, logo with glow,
and vertical stack of metal-gradient menu buttons.
"""

from typing import Callable, Dict, List, Tuple
import math
import random
import pygame
from src.gui.components.button import Button
from src.gui.assets.colors import BG_DARK, TEXT_WHITE, TEXT_ACCENT, TEXT_GOLD, TEXT_MUTED, PANEL_BG, PANEL_BORDER
from src.gui.assets.fonts import get_font, get_ui_font
from src.gui.components.car_renderer import draw_car_at


# ─── Building silhouette data for skyline ────────────────────────────────────
_BUILDINGS = [
    # (x, y_top, width, height) in 1280x720 space
    (0,   460, 60,  260), (60,  440, 80,  280), (140, 400, 55,  320),
    (195, 460, 95,  260), (290, 380, 65,  340), (355, 430, 50,  290),
    (405, 350, 85,  370), (490, 420, 60,  300), (550, 380, 75,  340),
    (625, 400, 55,  320), (680, 440, 90,  280), (770, 360, 70,  360),
    (840, 410, 60,  310), (900, 460, 85,  260), (985, 380, 65,  340),
    (1050,430, 75,  290), (1125,400, 80,  320), (1205,460, 75,  260),
]

# Windows lit in buildings
random.seed(42)
_WINDOWS: List[Tuple[int,int,int,int]] = []
for bx, by, bw, bh in _BUILDINGS:
    for wx in range(bx+6, bx+bw-6, 11):
        for wy in range(by+8, by+bh-10, 14):
            if random.random() > 0.4:
                _WINDOWS.append((wx, wy, 6, 8))


class MainMenuScreen:
    """Screen 1: Asphalt 8-style cinematic main menu."""

    MENU_ITEMS = [
        ("QUICK RACE",         "racing",        {"circuit_idx": 0, "laps": 2}, (0, 195, 255)),
        ("CHAMPIONSHIP",       "circuit_select", {},                           (255, 160,  0)),
        ("TRACK EXPLORER",     "track_explorer",  {"circuit_idx": 0},          (0, 220, 100)),
        ("ALGORITHM LAB",      "algorithm_lab",   {"circuit_idx": 0},          (200, 60,  255)),
        ("STANDINGS",          "dashboard",       {},                           (255,  80,  80)),
    ]

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.time          = 0.0

        # Animated car X position (scrolls left-to-right across the bottom)
        self._car_x = -100.0
        self._car_y = 630.0
        self._car_speed = 180.0   # px per second
        self._car_idx   = 0

        # Build buttons
        btn_x, btn_y0, btn_w, btn_h, btn_gap = 60, 190, 320, 52, 14
        self.buttons: List[Button] = []
        for i, (label, screen, ctx, accent) in enumerate(self.MENU_ITEMS):
            y = btn_y0 + i * (btn_h + btn_gap)
            self.buttons.append(
                Button((btn_x, y, btn_w, btn_h), label,
                       callback=lambda s=screen, c=ctx: self.switch_screen(s, c),
                       font_size=17, bold=True, accent_color=accent)
            )

        # Stars background
        random.seed(7)
        self._stars = [(random.randint(0,1280), random.randint(0,440),
                        random.random()*1.5+0.5) for _ in range(80)]

        # Pre-rendered background (static)
        self._bg_surf: pygame.Surface | None = None

    # ── Event / Update / Draw ─────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

    def update(self, dt: float) -> None:
        self.time += dt
        for btn in self.buttons:
            btn.update(dt)

        # Drive animated car
        self._car_x += self._car_speed * dt
        if self._car_x > 1400:
            self._car_x  = -120.0
            self._car_idx = (self._car_idx + 1) % 4

    def draw(self, surface: pygame.Surface) -> None:
        W, H = surface.get_size()

        # ── Background ─────────────────────────────────────────────────────
        if self._bg_surf is None:
            self._bg_surf = self._build_bg(W, H)
        surface.blit(self._bg_surf, (0, 0))

        # ── Twinkling stars ─────────────────────────────────────────────────
        for sx, sy, sr in self._stars:
            brightness = int(160 + 80 * math.sin(self.time * 2.0 + sx * 0.1))
            pygame.draw.circle(surface, (brightness, brightness, brightness), (sx, sy), int(sr))

        # ── Ground / Road strip ─────────────────────────────────────────────
        pygame.draw.rect(surface, (20, 23, 35), (0, H - 110, W, 110))
        pygame.draw.line(surface, (0, 200, 255), (0, H - 110), (W, H - 110), 2)
        # Road markings
        for rx in range(0, W + 80, 100):
            ox = int((rx - self.time * 80) % (W + 80)) - 40
            pygame.draw.rect(surface, (60, 65, 85), (ox, H-70, 60, 8), border_radius=2)

        # ── Animated car ───────────────────────────────────────────────────
        draw_car_at(surface, self._car_x, self._car_y,
                    car_index=self._car_idx, angle=0.0, scale=1.6,
                    nitro_active=(self.time % 3.0 < 0.4), is_human=False, show_shadow=True)

        # ── Logo Panel ─────────────────────────────────────────────────────
        self._draw_logo(surface, W)

        # ── Left side menu panel ────────────────────────────────────────────
        panel_rect = pygame.Rect(40, 170, 360, 340)
        panel_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (8, 10, 20, 210), panel_surf.get_rect(), border_radius=12)
        pygame.draw.rect(panel_surf, (0, 180, 255, 60), panel_surf.get_rect(), width=1, border_radius=12)
        surface.blit(panel_surf, panel_rect.topleft)

        for btn in self.buttons:
            btn.draw(surface)

        # ── Credits ────────────────────────────────────────────────────────
        self._draw_credits(surface, W, H)

        # ── Right info card ────────────────────────────────────────────────
        self._draw_info_card(surface, W)

    # ── Helpers ────────────────────────────────────────────────────────────

    def _build_bg(self, W: int, H: int) -> pygame.Surface:
        bg = pygame.Surface((W, H))
        # Deep gradient sky
        for y in range(H - 110):
            t = y / (H - 110)
            r = int(5  + 10  * t)
            g = int(5  + 12  * t)
            b = int(16 + 30  * t)
            pygame.draw.line(bg, (r, g, b), (0, y), (W, y))

        # Building silhouettes
        for bx, by, bw, bh in _BUILDINGS:
            pygame.draw.rect(bg, (18, 20, 32), (bx, by, bw, bh))
            # Roofline detail
            pygame.draw.rect(bg, (28, 32, 48), (bx, by, bw, 4))

        # Window lights
        for wx, wy, ww, wh in _WINDOWS:
            lum = random.randint(180, 255)
            col = (lum, lum - 20, max(0, lum - 60))
            pygame.draw.rect(bg, col, (wx, wy, ww, wh), border_radius=1)

        # Horizon glow
        glow_surf = pygame.Surface((W, 60), pygame.SRCALPHA)
        for gy in range(60):
            alpha = int(80 * (1 - gy / 60))
            pygame.draw.line(glow_surf, (0, 150, 220, alpha), (0, gy), (W, gy))
        bg.blit(glow_surf, (0, H - 170))

        return bg

    def _draw_logo(self, surface: pygame.Surface, W: int):
        # Main title
        font_title = get_font(size=58, bold=True, family="auto")
        font_sub   = get_ui_font(size=18, bold=True)

        title_txt  = "SMART RACING"
        sub_txt    = "CHAMPIONSHIP"

        # Glow effect — render shadow layers
        glow_col = (0, 180, 255)
        for offset in [(3,3),(2,2),(1,1)]:
            shadow = font_title.render(title_txt, True, (0, 60, 100))
            surface.blit(shadow, shadow.get_rect(center=(W//2 + offset[0], 68 + offset[1])))

        txt_main = font_title.render(title_txt, True, (240, 244, 255))
        surface.blit(txt_main, txt_main.get_rect(center=(W//2, 68)))

        # Subtitle with cyan accent
        txt_sub = font_sub.render(sub_txt, True, TEXT_ACCENT)
        surface.blit(txt_sub, txt_sub.get_rect(center=(W//2, 112)))

        # Underline bar
        bar_w = 400
        pygame.draw.rect(surface, TEXT_ACCENT, (W//2 - bar_w//2, 128, bar_w, 3), border_radius=2)

        # Pulsing glow on bar
        pulse = abs(math.sin(self.time * 2.0))
        glow_bar = pygame.Surface((bar_w, 10), pygame.SRCALPHA)
        pygame.draw.rect(glow_bar, (*TEXT_ACCENT, int(100*pulse)), glow_bar.get_rect(), border_radius=5)
        surface.blit(glow_bar, (W//2 - bar_w//2, 125))

        # DAA badge
        badge_txt = get_ui_font(size=13).render("Design and Analysis of Algorithms — FAST-NUCES", True, TEXT_MUTED)
        surface.blit(badge_txt, badge_txt.get_rect(center=(W//2, 148)))

    def _draw_credits(self, surface: pygame.Surface, W: int, H: int):
        font = get_ui_font(size=12)
        members = [
            "Muhammad Aoun  24P-3099",
            "Abdullah Mohzar  24I-3124",
            "Muhammad Sarim  24I-3069",
        ]
        y_start = H - 100
        for i, m in enumerate(members):
            txt = font.render(m, True, TEXT_MUTED)
            surface.blit(txt, (W - txt.get_width() - 20, y_start + i * 18))

    def _draw_info_card(self, surface: pygame.Surface, W: int):
        """Right-side info card: controls cheat-sheet."""
        cx = W - 200
        card = pygame.Rect(cx - 160, 170, 340, 240)
        card_surf = pygame.Surface(card.size, pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (8,10,20,200), card_surf.get_rect(), border_radius=12)
        pygame.draw.rect(card_surf, (0,180,255,50), card_surf.get_rect(), width=1, border_radius=12)
        surface.blit(card_surf, card.topleft)

        hdr = get_ui_font(size=14, bold=True).render("CONTROLS", True, TEXT_ACCENT)
        surface.blit(hdr, (card.x + 16, card.y + 14))
        pygame.draw.line(surface, (0,180,255), (card.x+16, card.y+32), (card.right-16, card.y+32), 1)

        lines = [
            ("ARROW/WASD", "Steer car"),
            ("SPACE",      "Nitro boost"),
            ("P / ESC",    "Pause"),
            ("R",          "Restart"),
        ]
        font_key = get_ui_font(size=12, bold=True)
        font_val = get_ui_font(size=12)
        for i, (key, val) in enumerate(lines):
            y = card.y + 46 + i * 26
            k_surf = font_key.render(key, True, TEXT_GOLD)
            v_surf = font_val.render(val, True, TEXT_WHITE)
            surface.blit(k_surf, (card.x + 16,  y))
            surface.blit(v_surf, (card.x + 140, y))

        # Algorithm count badge
        badge = get_ui_font(size=12, bold=True).render("12 Algorithms  |  3 Circuits  |  4 Cars", True, (100,220,160))
        surface.blit(badge, badge.get_rect(center=(card.centerx, card.y + card.height - 24)))
