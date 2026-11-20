"""src/gui/screens/main_menu.py — Pixar Cars / Radiator Springs Main Menu.

Route 66 road-sign style menu on a desert sunset background.
Animated McQueen drives across bottom. Menu items styled as vintage road signs.
"""

from typing import Callable, Dict, List
import math
import random
import os
import pygame
from src.gui.components.car_renderer import draw_car_at, CAR_DESIGNS
from src.gui.assets.colors import BG_DARK, TEXT_WHITE, TEXT_ACCENT, TEXT_GOLD, TEXT_MUTED, PANEL_BG, PANEL_BORDER
from src.gui.assets.fonts import get_font, get_ui_font

_ASSETS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets", "images"))

MENU_ITEMS = [
    # (label, screen, context, accent_color, icon, sign_style)
    ("CHAMPIONSHIP",    "championship",   {},                               (255, 160,   0), "TROPHY",    "hexagon"),
    ("QUICK RACE",      "circuit_select", {"mode": "quick"},                (220,  60,  20), "RACE",      "rect"),
    ("RACE EXPLORER",   "track_explorer", {"circuit_idx": 0},               (40,  160,  60), "MAP",       "rect"),
    ("GARAGE",          "garage",         {},                               (200,  80, 255), "GARAGE",    "rect"),
    ("SCOREBOARD",      "scoreboard",     {},                               (255, 200,   0), "SCORE",     "rect"),
    ("INSTRUCTIONS",    "instructions",   {},                               (100, 170, 255), "INFO",      "rect"),
    ("EXIT",            "EXIT",           {},                               (200,  40,  20), "EXIT",      "stop"),
]


def _draw_desert_bg(surface: pygame.Surface, W: int, H: int, time: float) -> None:
    """Draw the Radiator Springs desert sunset background."""
    sky_bands = [
        (0.00, (12,  6,  2)),
        (0.15, (40, 18,  6)),
        (0.30, (100, 48, 14)),
        (0.45, (180, 90, 22)),
        (0.60, (210, 120, 30)),
        (0.72, (170, 80, 18)),
        (0.82, (100, 44, 12)),
        (1.00, (40,  18,  6)),
    ]
    for i in range(len(sky_bands)-1):
        t0, c0 = sky_bands[i]
        t1, c1 = sky_bands[i+1]
        y0, y1 = int(t0 * H), int(t1 * H)
        for y in range(y0, y1):
            t = (y - y0) / max(1, y1 - y0)
            r_ = int(c0[0] + (c1[0]-c0[0])*t)
            g_ = int(c0[1] + (c1[1]-c0[1])*t)
            b_ = int(c0[2] + (c1[2]-c0[2])*t)
            pygame.draw.line(surface, (r_, g_, b_), (0, y), (W, y))

    # Glowing sun
    sun_x, sun_y = int(W * 0.68), int(H * 0.40)
    for sr in range(100, 0, -5):
        a = max(0, int(80 - sr * 0.5))
        s = pygame.Surface((sr*2+2, sr*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 215, 70, a), (sr+1, sr+1), sr)
        surface.blit(s, (sun_x - sr - 1, sun_y - sr - 1))
    pygame.draw.circle(surface, (255, 245, 160), (sun_x, sun_y), 38)
    pygame.draw.circle(surface, (255, 255, 220), (sun_x, sun_y), 24)

    # Rock formations — Willy's Butte / Monument Valley
    rock_col = (18, 10, 4)
    buttes = [
        (int(W*0.42), H, 160, 280, 'mesa'),
        (int(W*0.55), H,  90, 200, 'spire'),
        (int(W*0.65), H, 120, 240, 'mesa'),
        (int(W*0.78), H,  80, 160, 'spire'),
        (int(W*0.88), H, 110, 200, 'mesa'),
        (int(W*0.96), H,  70, 140, 'spire'),
    ]
    for bx, by, bw, bh, style in buttes:
        if style == 'mesa':
            pts = [(bx-bw//2, by), (bx-bw*2//3, by-bh), (bx+bw*2//3, by-bh), (bx+bw//2, by)]
        else:
            pts = [(bx-bw//2, by), (bx-bw//5, by-bh), (bx+bw//5, by-bh), (bx+bw//2, by)]
        pygame.draw.polygon(surface, rock_col, pts)
        pygame.draw.line(surface, (45, 25, 10), pts[1], pts[2], 2)

    # Ground / desert floor
    ground_y = int(H * 0.72)
    pygame.draw.rect(surface, (25, 16, 6), (0, ground_y, W, H - ground_y))

    # Route 66 road (perspective) — right side
    road_pts = [
        (int(W*0.42), ground_y),
        (int(W*0.68), ground_y),
        (W, H),
        (int(W*0.42), H),
    ]
    pygame.draw.polygon(surface, (35, 28, 16), road_pts)

    # Road dashes (animated)
    for d in range(6):
        t = ((d / 6) + time * 0.12) % 1.0
        gy = ground_y + int((H - ground_y) * t)
        road_right = int(W*0.42 + (W - W*0.42) * t)
        cx_ = (int(W*0.55) + road_right) // 2
        dash_w = max(2, int((road_right - int(W*0.55)) * 0.04))
        a_ = int(180 * t)
        ds = pygame.Surface((dash_w*2, 10), pygame.SRCALPHA)
        pygame.draw.rect(ds, (255, 210, 60, a_), ds.get_rect(), border_radius=1)
        surface.blit(ds, (cx_ - dash_w, gy))

    # Cactus silhouettes
    for cx_, cy_ in [(int(W*0.40), ground_y - 20), (int(W*0.72), ground_y - 15)]:
        # Trunk
        pygame.draw.rect(surface, rock_col, (cx_-4, cy_-40, 8, 40))
        # Arms
        pygame.draw.rect(surface, rock_col, (cx_-16, cy_-28, 14, 6))
        pygame.draw.rect(surface, rock_col, (cx_+2,  cy_-24, 14, 6))
        pygame.draw.rect(surface, rock_col, (cx_-16, cy_-40, 6, 14))
        pygame.draw.rect(surface, rock_col, (cx_+10, cy_-36, 6, 14))


class MainMenuScreen:
    """Radiator Springs Legendary Motors Grand Championship — Cinematic main menu."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.time          = 0.0
        self._bg: pygame.Surface | None = None
        self._photo_bg: pygame.Surface | None = None
        self._photo_checked = False

        # Lightning McQueen drives in from right
        self._mcqueen_x  = 1500.0
        self._mcqueen_y  = 0.0        # set in first draw
        self._car_idx    = 0
        self._car_dir    = -1
        self._showcase_x = 920.0
        self._showcasing = True

        # Menu hover state
        self._hovered = -1
        self._btn_rects: List[pygame.Rect] = []
        btn_x, btn_y0, btn_w, btn_h, gap = 48, 148, 300, 52, 8
        for i in range(len(MENU_ITEMS)):
            self._btn_rects.append(pygame.Rect(btn_x, btn_y0 + i*(btn_h+gap), btn_w, btn_h))

    def _check_photo(self, W: int, H: int) -> None:
        # Photo background disabled — always use procedural desert sunset
        self._photo_checked = True
        self._photo_bg = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self._hovered = -1
            for i, r in enumerate(self._btn_rects):
                if r.collidepoint(event.pos):
                    self._hovered = i
                    break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # Showcase car arrow clicks
            ax, ay = int(self._showcase_x), int(self._mcqueen_y) + 100
            if pygame.Rect(ax-80, ay-10, 36, 36).collidepoint(mx, my):
                self._car_idx = (self._car_idx - 1) % len(CAR_DESIGNS)
                self._showcasing = True; self._mcqueen_x = 1400.0
                return
            if pygame.Rect(ax+42, ay-10, 36, 36).collidepoint(mx, my):
                self._car_idx = (self._car_idx + 1) % len(CAR_DESIGNS)
                self._showcasing = True; self._mcqueen_x = 1400.0
                return
            for i, r in enumerate(self._btn_rects):
                if r.collidepoint(event.pos):
                    label, screen, ctx, _, _, _ = MENU_ITEMS[i]
                    if screen == "EXIT":
                        import sys; pygame.quit(); sys.exit(0)
                    self.switch_screen(screen, ctx)
                    break

    def update(self, dt: float) -> None:
        self.time += dt
        if self._showcasing:
            target = self._showcase_x
            if self._mcqueen_x > target + 10:
                self._mcqueen_x -= 240 * dt
            else:
                self._mcqueen_x = target
                self._showcasing = False

    def draw(self, surface: pygame.Surface) -> None:
        W, H = surface.get_size()
        self._mcqueen_y = H * 0.60
        self._check_photo(W, H)

        # ── Background ────────────────────────────────────────────────────────
        if self._photo_bg is not None:
            surface.blit(self._photo_bg, (0, 0))
        else:
            _draw_desert_bg(surface, W, H, self.time)

        # ── Animated dust cloud when car arrives ─────────────────────────────
        if self._showcasing:
            for d in range(3):
                dr = int(14 + d * 8)
                dx = int(self._mcqueen_x) + int(math.cos(self.time * 8 + d) * 6)
                dy = int(self._mcqueen_y) + 20 + d * 4
                dust = pygame.Surface((dr*2, dr*2), pygame.SRCALPHA)
                pygame.draw.circle(dust, (160, 120, 60, max(0, 100-d*25)), (dr, dr), dr)
                surface.blit(dust, (dx - dr, dy - dr))

        # ── Ground strip at bottom ────────────────────────────────────────────
        gnd_y = int(H * 0.72)
        # Route 66 road dashes at the bottom
        for lx in range(-80, W + 80, 100):
            ox = int((lx + self.time * 55) % (W + 100)) - 50
            pygame.draw.rect(surface, (60, 50, 28), (ox, int(H - 80), 55, 7), border_radius=2)

        # ── Showcase car (Lightning McQueen by default) ───────────────────────
        car = CAR_DESIGNS[self._car_idx]
        draw_car_at(surface, int(self._mcqueen_x), int(self._mcqueen_y),
                    self._car_idx, angle=math.pi, scale=2.6,
                    nitro_active=False, is_human=False, show_shadow=True)

        # Car name below
        name_f = get_ui_font(size=16, bold=True)
        n_txt = name_f.render(f"{car['year']}  {car['name']}", True, (255, 200, 60))
        surface.blit(n_txt, n_txt.get_rect(center=(int(self._showcase_x), int(self._mcqueen_y) + 90)))

        # Arrow nav for showcase car
        ax, ay = int(self._showcase_x), int(self._mcqueen_y) + 100
        from src.gui.components.button import draw_arrow_button
        draw_arrow_button(surface, (ax-82, ay-8, 36, 36), "left",  color=(255,180,40), hovered=False)
        draw_arrow_button(surface, (ax+46, ay-8, 36, 36), "right", color=(255,180,40), hovered=False)

        # ── LEFT PANEL — Radiator Springs wooden sign board ───────────────────
        panel_surf = pygame.Surface((360, H - 60), pygame.SRCALPHA)
        # Dark wooden plank effect
        pygame.draw.rect(panel_surf, (28, 16, 6, 240), panel_surf.get_rect(), border_radius=10)
        # Wood grain lines
        for gy in range(0, H, 18):
            pygame.draw.line(panel_surf, (40, 24, 10, 60), (0, gy), (360, gy), 1)
        # Border — weathered metal frame
        pygame.draw.rect(panel_surf, (120, 76, 28, 220), panel_surf.get_rect(), width=3, border_radius=10)
        surface.blit(panel_surf, (22, 30))

        # ── LOGO — Cars-movie style title ────────────────────────────────────
        self._draw_logo(surface)

        # ── MENU BUTTONS — Route 66 road signs ───────────────────────────────
        for i, (label, screen, ctx, accent, icon, sign_style) in enumerate(MENU_ITEMS):
            self._draw_road_sign_btn(surface, i, label, icon, accent, sign_style)

        # ── Bottom credits ────────────────────────────────────────────────────
        cr = get_ui_font(size=11).render(
            "FAST-NUCES  DAA Semester 5  ·  Muhammad Aoun  |  Abdullah Mohzar  |  Muhammad Sarim",
            True, (100, 65, 28))
        surface.blit(cr, cr.get_rect(center=(W//2, H - 12)))

    def _draw_logo(self, surface: pygame.Surface) -> None:
        """Cars-movie style 'Legendary Motors' logo with metallic glow."""
        cx = 202   # center of left panel

        # Piston Cup badge at top
        self._draw_piston_cup_badge(surface, cx, 56)

        # Title
        f_big = get_font(size=24, bold=True)
        f_sub = get_ui_font(size=12, bold=True)

        # Glow
        for off in [3, 2]:
            g = f_big.render("LEGENDARY", True, (140, 60, 0))
            g.set_alpha(50)
            surface.blit(g, g.get_rect(center=(cx, 94 + off)))

        t1 = f_big.render("LEGENDARY", True, (255, 200, 50))
        t2 = f_big.render("MOTORS", True, (255, 240, 180))
        t3 = f_sub.render("GRAND  CHAMPIONSHIP", True, (200, 140, 40))

        surface.blit(t1, t1.get_rect(center=(cx, 94)))
        surface.blit(t2, t2.get_rect(center=(cx, 122)))

        # Route 66 divider
        pygame.draw.line(surface, (140, 90, 24), (60, 140), (344, 140), 1)
        pygame.draw.line(surface, (80,  50, 12), (60, 141), (344, 141), 1)

        surface.blit(t3, t3.get_rect(center=(cx, 154)))

    def _draw_piston_cup_badge(self, surface: pygame.Surface, cx: int, cy: int) -> None:
        """Draw a small Piston Cup trophy badge."""
        # Cup body
        pygame.draw.rect(surface, (180, 130, 20), (cx-14, cy-16, 28, 20), border_radius=4)
        # Handles
        pygame.draw.line(surface, (140, 100, 10), (cx-14, cy-10), (cx-22, cy-6), 3)
        pygame.draw.line(surface, (140, 100, 10), (cx+14, cy-10), (cx+22, cy-6), 3)
        # Base
        pygame.draw.rect(surface, (200, 150, 30), (cx-10, cy+4,  20, 5))
        pygame.draw.rect(surface, (200, 150, 30), (cx-16, cy+9,  32, 4))
        # Shine
        pygame.draw.rect(surface, (255, 230, 100), (cx-6, cy-14, 6, 10), border_radius=2)
        # Text
        f = get_ui_font(size=8, bold=True)
        t = f.render("PISTON CUP", True, (255, 230, 80))
        surface.blit(t, t.get_rect(center=(cx, cy + 20)))

    def _draw_road_sign_btn(self, surface: pygame.Surface, i: int, label: str,
                             icon: str, accent: tuple, sign_style: str) -> None:
        """Draw a menu item styled as a vintage road sign."""
        r = self._btn_rects[i]
        is_hov = (i == self._hovered)

        # Sign background
        if sign_style == 'stop':
            # Stop sign octagon
            pts = self._octagon_pts(r.centerx, r.centery, r.height//2 - 2)
            bg_col = (160, 20, 10) if not is_hov else (220, 40, 20)
            pygame.draw.polygon(surface, bg_col, pts)
            pygame.draw.polygon(surface, (240, 240, 240) if is_hov else (200, 180, 160), pts, 2)
        elif sign_style == 'hexagon':
            # Championship hexagon
            pts = self._hex_pts(r.centerx, r.centery, r.height//2 - 2)
            bg_col = (120, 80, 10) if not is_hov else (180, 130, 20)
            pygame.draw.polygon(surface, bg_col, pts)
            pygame.draw.polygon(surface, (255, 210, 60) if is_hov else (180, 140, 40), pts, 2)
        else:
            # Standard rectangle road sign
            bg_col = (28, 50, 20) if not is_hov else (40, 80, 30)
            if sign_style == 'rect' and label == "GARAGE":
                bg_col = (50, 20, 70) if not is_hov else (80, 30, 110)
            elif label == "SCOREBOARD":
                bg_col = (70, 50, 10) if not is_hov else (110, 80, 15)
            elif label == "INSTRUCTIONS":
                bg_col = (20, 40, 80) if not is_hov else (30, 60, 120)
            elif label == "QUICK RACE":
                bg_col = (80, 20, 10) if not is_hov else (120, 30, 15)
            elif label == "RACE EXPLORER":
                bg_col = (20, 60, 30) if not is_hov else (30, 90, 45)
            pygame.draw.rect(surface, bg_col, r, border_radius=6)
            # Metal frame border
            bc = accent if is_hov else (100, 70, 30)
            pygame.draw.rect(surface, bc, r, width=2, border_radius=6)
            # Rivet corners
            for rx, ry in [(r.x+6, r.y+6), (r.right-6, r.y+6),
                           (r.x+6, r.bottom-6), (r.right-6, r.bottom-6)]:
                pygame.draw.circle(surface, (140, 100, 40), (rx, ry), 3)
                pygame.draw.circle(surface, (200, 160, 80), (rx, ry), 2)

        # Hover glow
        if is_hov:
            gl = pygame.Surface(r.size, pygame.SRCALPHA)
            pygame.draw.rect(gl, (*accent, 40), gl.get_rect(), border_radius=6)
            surface.blit(gl, r.topleft)

        # Label text
        f = get_ui_font(size=16, bold=True)
        col = accent if is_hov else (220, 200, 150)
        txt = f.render(label, True, col)
        # Left-padded (not on stop/hex signs)
        if sign_style in ('stop', 'hexagon'):
            surface.blit(txt, txt.get_rect(center=r.center))
        else:
            t_rect = txt.get_rect(centery=r.centery, x=r.x + 36)
            surface.blit(txt, t_rect)
            # Left accent bar
            bar_col = accent if is_hov else (80, 55, 20)
            pygame.draw.rect(surface, bar_col, (r.x + 2, r.y + 6, 4, r.height - 12), border_radius=2)

    def _octagon_pts(self, cx, cy, r):
        pts = []
        for i in range(8):
            a = math.pi / 8 + i * math.pi / 4
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        return pts

    def _hex_pts(self, cx, cy, r):
        pts = []
        for i in range(6):
            a = math.pi / 6 + i * math.pi / 3
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        return pts
