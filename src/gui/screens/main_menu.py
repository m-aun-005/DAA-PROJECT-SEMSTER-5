"""src/gui/screens/main_menu.py — Legendary Motors Championship Main Menu.

Sections: Championship, Quick Race, Race Explorer, Garage, Instructions, Scoreboard, Exit.
"""

from typing import Callable, Dict, List
import math
import random
import pygame
from src.gui.components.car_renderer import draw_car_at, CAR_DESIGNS
from src.gui.assets.colors import BG_DARK, TEXT_WHITE, TEXT_ACCENT, TEXT_GOLD, TEXT_MUTED, PANEL_BG, PANEL_BORDER
from src.gui.assets.fonts import get_font, get_ui_font
import os

_ASSETS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets", "images"))

MENU_ITEMS = [
    # (label, screen, context, accent_color, icon)
    ("CHAMPIONSHIP",    "championship",   {},                               (255, 160,   0), "🏆"),
    ("QUICK RACE",      "circuit_select", {"mode": "quick"},                (0,  200, 255), "🏁"),
    ("RACE EXPLORER",   "track_explorer", {"circuit_idx": 0},               (0,  220, 100), "🗺"),
    ("GARAGE",          "garage",         {},                               (200,  60, 255), "🔧"),
    ("SCOREBOARD",      "scoreboard",     {},                               (255, 200,   0), "📊"),
    ("INSTRUCTIONS",    "instructions",   {},                               (100, 180, 255), "📖"),
    ("EXIT",            "EXIT",           {},                               (255,  60,  60), "✕"),
]


class MainMenuScreen:
    """Legendary Motors Championship — Cinematic main menu."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.time          = 0.0
        self._bg: pygame.Surface | None = None

        # Animated showcase car
        self._car_x    = 1500.0
        self._car_y    = 560.0
        self._car_idx  = 0
        self._car_dir  = -1   # going left
        self._showcasing = True
        self._showcase_x = 920.0
        self._showcase_alpha = 0.0

        random.seed(12)
        self._stars = [(random.randint(0,1280), random.randint(0,420),
                        random.random()*1.4+0.4) for _ in range(60)]

        # Menu buttons — stored as rects + labels; drawn manually for custom look
        self._hovered = -1
        self._btn_rects: List[pygame.Rect] = []
        btn_x, btn_y0, btn_w, btn_h, gap = 48, 148, 290, 54, 10
        for i in range(len(MENU_ITEMS)):
            self._btn_rects.append(pygame.Rect(btn_x, btn_y0 + i*(btn_h+gap), btn_w, btn_h))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self._hovered = -1
            for i, r in enumerate(self._btn_rects):
                if r.collidepoint(event.pos):
                    self._hovered = i
                    break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._btn_rects):
                if r.collidepoint(event.pos):
                    label, screen, ctx, _, _ = MENU_ITEMS[i]
                    if screen == "EXIT":
                        import sys; pygame.quit(); sys.exit(0)
                    self.switch_screen(screen, ctx)
                    break

    def update(self, dt: float) -> None:
        self.time += dt
        # Showcase car drives in from right
        if self._showcasing:
            target = self._showcase_x
            if self._car_x > target + 10:
                self._car_x -= 220 * dt
            else:
                self._car_x = target
                self._showcasing = False
        # Rotate through cars every 4s
        if int(self.time) % 5 == 0 and not self._showcasing:
            pass  # could auto-rotate
        self._showcase_alpha = min(255.0, self._showcase_alpha + dt * 200)

    def draw(self, surface: pygame.Surface) -> None:
        W, H = surface.get_size()
        self._ensure_bg(surface, W, H)

        # ── Background ────────────────────────────────────────────────────────
        surface.blit(self._bg, (0, 0))

        # Stars
        for sx, sy, sr in self._stars:
            b = int(140 + 90 * math.sin(self.time*1.8 + sx*0.08))
            pygame.draw.circle(surface, (b, b, b), (sx, sy), int(sr))

        # Ground strip
        pygame.draw.rect(surface, (10, 12, 20), (0, H - 120, W, 120))
        pygame.draw.line(surface, (0, 180, 255), (0, H - 120), (W, H - 120), 2)
        # Animated road lines
        for lx in range(-80, W + 80, 100):
            ox = int((lx + self.time * 55) % (W + 100)) - 50
            pygame.draw.rect(surface, (45, 50, 65), (ox, H-80, 55, 7), border_radius=2)

        # ── Showcase car ──────────────────────────────────────────────────────
        if self._showcase_alpha > 0:
            showcase_surf = pygame.Surface((260, 220), pygame.SRCALPHA)
            # Glow halo behind car
            glow = pygame.Surface((240, 160), pygame.SRCALPHA)
            ac = CAR_DESIGNS[self._car_idx]["body"]
            for gr in range(70, 0, -4):
                pygame.draw.ellipse(glow, (*ac, max(0, gr-50)), (40-gr//2, 50-gr//4, 160+gr, 80+gr//2))
            surface.blit(glow, (int(self._car_x)-120, int(self._car_y)-80))

            draw_car_at(surface, int(self._car_x), int(self._car_y),
                        self._car_idx, angle=math.pi, scale=2.4,
                        nitro_active=False, is_human=False, show_shadow=True)

        # ── Car name below ────────────────────────────────────────────────────
        car = CAR_DESIGNS[self._car_idx]
        name_font = get_ui_font(size=14, bold=True)
        n_txt = name_font.render(f"{car['year']}  {car['name']}", True, TEXT_GOLD)
        surface.blit(n_txt, n_txt.get_rect(center=(int(self._showcase_x), int(self._car_y) + 90)))

        # Arrow nav for showcase car
        self._draw_car_arrows(surface)

        # ── Left panel + buttons ──────────────────────────────────────────────
        panel_surf = pygame.Surface((340, H - 60), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (5, 7, 16, 230), panel_surf.get_rect(), border_radius=14)
        pygame.draw.rect(panel_surf, (0, 180, 255, 40), panel_surf.get_rect(), width=1, border_radius=14)
        surface.blit(panel_surf, (30, 30))

        self._draw_logo(surface, W)

        for i, (label, screen, ctx, accent, icon) in enumerate(MENU_ITEMS):
            self._draw_menu_btn(surface, i, label, icon, accent)

        # ── Bottom credits ────────────────────────────────────────────────────
        cr = get_ui_font(size=11).render(
            "FAST-NUCES  ·  DAA Semester 5  ·  Muhammad Aoun  |  Abdullah Mohzar  |  Muhammad Sarim",
            True, (60, 65, 85))
        surface.blit(cr, cr.get_rect(center=(W//2, H - 12)))

    def _draw_logo(self, surface: pygame.Surface, W: int) -> None:
        y0 = 48
        font_big = get_font(size=26, bold=True)
        font_sub = get_ui_font(size=12, bold=True)

        t1 = font_big.render("LEGENDARY", True, TEXT_GOLD)
        t2 = font_big.render("MOTORS", True, TEXT_WHITE)
        t3 = font_sub.render("GRAND CHAMPIONSHIP", True, TEXT_ACCENT)

        surface.blit(t1, t1.get_rect(centerx=188, y=y0))
        surface.blit(t2, t2.get_rect(centerx=188, y=y0+34))
        surface.blit(t3, t3.get_rect(centerx=188, y=y0+68))
        pygame.draw.line(surface, TEXT_ACCENT, (50, y0+86), (326, y0+86), 2)

    def _draw_menu_btn(self, surface: pygame.Surface, idx: int,
                        label: str, icon: str, accent: tuple) -> None:
        r   = self._btn_rects[idx]
        hov = (idx == self._hovered)

        # Background
        bg_col  = (20, 26, 42) if not hov else (28, 36, 58)
        pygame.draw.rect(surface, bg_col, r, border_radius=8)

        # Accent left bar
        bar_col = accent if hov else (38, 46, 68)
        pygame.draw.rect(surface, bar_col, (r.x, r.y+6, 4, r.h-12), border_radius=2)

        # Glow overlay on hover
        if hov:
            glow_surf = pygame.Surface(r.size, pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*accent, 35), glow_surf.get_rect(), border_radius=8)
            surface.blit(glow_surf, r.topleft)

        # Border
        bc = accent if hov else (38, 46, 68)
        pygame.draw.rect(surface, bc, r, width=1, border_radius=8)

        # Label
        font = get_ui_font(size=18, bold=True)
        col  = TEXT_WHITE if not hov else (255, 255, 255)
        txt  = font.render(label, True, col)
        surface.blit(txt, (r.x + 20, r.centery - txt.get_height()//2))

        # Arrow indicator on hover
        if hov:
            arr = get_ui_font(size=16, bold=True).render("▶", True, accent)
            surface.blit(arr, (r.right - arr.get_width() - 14, r.centery - arr.get_height()//2))

    def _draw_car_arrows(self, surface: pygame.Surface) -> None:
        """Draw ◀ ▶ arrows to cycle through showcase cars."""
        ax, ay = int(self._showcase_x), int(self._car_y) + 100
        f = get_ui_font(size=20, bold=True)
        lt = f.render("◀", True, (100, 120, 160))
        rt = f.render("▶", True, (100, 120, 160))
        surface.blit(lt, (ax - 70, ay))
        surface.blit(rt, (ax + 50, ay))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self._hovered = -1
            for i, r in enumerate(self._btn_rects):
                if r.collidepoint(event.pos):
                    self._hovered = i
                    break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Check showcase arrow clicks
            ax, ay = int(self._showcase_x), int(self._car_y) + 100
            if pygame.Rect(ax-80, ay-10, 36, 36).collidepoint(mx, my):
                self._car_idx = (self._car_idx - 1) % len(CAR_DESIGNS)
                self._showcasing = True
                self._car_x = 1400.0
                return
            if pygame.Rect(ax+42, ay-10, 36, 36).collidepoint(mx, my):
                self._car_idx = (self._car_idx + 1) % len(CAR_DESIGNS)
                self._showcasing = True
                self._car_x = 1400.0
                return

            for i, r in enumerate(self._btn_rects):
                if r.collidepoint(event.pos):
                    label, screen, ctx, _, _ = MENU_ITEMS[i]
                    if screen == "EXIT":
                        import sys; pygame.quit(); sys.exit(0)
                    self.switch_screen(screen, ctx)
                    break

    def _ensure_bg(self, surface: pygame.Surface, W: int, H: int) -> None:
        if self._bg is not None:
            return
        # Dark gradient + cityscape
        self._bg = pygame.Surface((W, H))
        for y in range(H):
            t = y / H
            r = int(4 + 12*t); g = int(4+10*t); b = int(10+28*t)
            pygame.draw.line(self._bg, (r, g, b), (0, y), (W, y))
        # Building silhouettes (right side only since left is panel)
        buildings = [
            (350,480,70,240),(420,440,90,280),(510,400,65,320),
            (575,460,80,260),(655,380,75,340),(730,430,60,290),
            (790,360,90,360),(880,420,65,300),(945,380,80,340),
            (1025,400,60,320),(1085,440,100,280),(1185,460,95,260),
        ]
        for bx,by,bw,bh in buildings:
            pygame.draw.rect(self._bg, (14,16,26), (bx,by,bw,bh))
            pygame.draw.rect(self._bg, (22,26,40), (bx,by,bw,3))
        # Windows
        random.seed(99)
        for bx,by,bw,bh in buildings:
            for wx in range(bx+6, bx+bw-6, 11):
                for wy in range(by+8, by+bh-10, 14):
                    if random.random() > 0.4:
                        lum = random.randint(160,240)
                        pygame.draw.rect(self._bg, (lum, lum-20, max(0,lum-70)), (wx,wy,6,8), border_radius=1)
