"""src/gui/screens/splash_screen.py — Pixar Cars-style Cinematic Splash Screen.

Desert sunset sky, Radiator Springs silhouette, Cars-style title card.
Checks for user-provided background image first (images.jpg / home_bg.jpg).
"""

from typing import Callable, Dict
import math
import pygame
from src.gui.assets.colors import TEXT_WHITE, TEXT_ACCENT, TEXT_GOLD, BG_DARK
from src.gui.assets.fonts import get_font, get_ui_font
import os

_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "images")


def _load_image_or_fallback(name: str) -> pygame.Surface:
    """Load image from assets or project root, or return None if not found."""
    root_dir = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    root_path = os.path.join(root_dir, name)
    if os.path.exists(root_path):
        try:
            return pygame.image.load(root_path).convert()
        except Exception:
            pass
    path = os.path.normpath(os.path.join(_ASSETS_DIR, name))
    if os.path.exists(path):
        try:
            return pygame.image.load(path).convert()
        except Exception:
            pass
    return None


def _draw_desert_bg(surface: pygame.Surface, W: int, H: int, time: float) -> None:
    """Draw a Radiator Springs desert-sunset sky background."""
    # Sky gradient — golden hour desert sunset
    sky_colors = [
        (20, 10, 5),       # Deep horizon dark
        (60, 30, 10),      # Burnt sienna
        (140, 70, 20),     # Desert amber
        (200, 110, 30),    # Warm orange horizon
        (220, 160, 60),    # Golden horizon glow
        (200, 100, 40),    # Lower amber
        (140, 60, 20),     # Rust
        (60, 25, 8),       # Ground dark
    ]
    band = H // len(sky_colors)
    for i, col in enumerate(sky_colors):
        y0 = i * band
        y1 = (i + 1) * band if i < len(sky_colors)-1 else H
        # Blend between this colour and next
        if i < len(sky_colors)-1:
            nc = sky_colors[i+1]
            for y in range(y0, y1):
                t = (y - y0) / max(1, band)
                r_ = int(col[0] + (nc[0]-col[0])*t)
                g_ = int(col[1] + (nc[1]-col[1])*t)
                b_ = int(col[2] + (nc[2]-col[2])*t)
                pygame.draw.line(surface, (r_, g_, b_), (0, y), (W, y))

    # Sun on the horizon
    sun_x, sun_y = W * 2 // 3, int(H * 0.42)
    for sr in range(80, 0, -4):
        a = max(0, int(90 - sr * 0.6))
        s = pygame.Surface((sr*2, sr*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 220, 80, a), (sr, sr), sr)
        surface.blit(s, (sun_x - sr, sun_y - sr))
    pygame.draw.circle(surface, (255, 240, 140), (sun_x, sun_y), 36)
    pygame.draw.circle(surface, (255, 255, 200), (sun_x, sun_y), 22)

    # Monument Valley / Willy's Butte rock formations silhouette
    buttes = [
        # (x, ground_y, width, height, style)
        (W*0.08, H, 90, 190, 'mesa'),
        (W*0.18, H, 60, 150, 'spire'),
        (W*0.26, H, 110, 220, 'mesa'),
        (W*0.60, H, 140, 240, 'mesa'),   # Willy's Butte
        (W*0.72, H, 70, 160, 'spire'),
        (W*0.82, H, 100, 180, 'mesa'),
        (W*0.92, H, 80, 130, 'spire'),
    ]
    rock_col = (22, 12, 6)
    for bx, by, bw, bh, style in buttes:
        bx = int(bx); by = int(by); bw = int(bw); bh = int(bh)
        if style == 'mesa':
            # Flat-top mesa
            pts = [
                (bx - bw//2, by),
                (bx - bw*2//3, by - bh),
                (bx + bw*2//3, by - bh),
                (bx + bw//2, by),
            ]
        else:
            # Narrow spire
            pts = [
                (bx - bw//2, by),
                (bx - bw//5, by - bh),
                (bx + bw//5, by - bh),
                (bx + bw//2, by),
            ]
        pygame.draw.polygon(surface, rock_col, pts)
        # Rim highlight
        pygame.draw.line(surface, (50, 28, 12), pts[1], pts[2], 2)

    # Ground / Route 66 road perspective
    ground_y = int(H * 0.72)
    pygame.draw.rect(surface, (30, 20, 10), (0, ground_y, W, H - ground_y))
    # Road strip (perspective)
    road_pts = [
        (W//2 - 60, ground_y),
        (W//2 + 60, ground_y),
        (W, H),
        (0, H),
    ]
    pygame.draw.polygon(surface, (40, 32, 20), road_pts)
    # Yellow center dashes (animated)
    num_dashes = 8
    for d in range(num_dashes):
        t = (d / num_dashes + time * 0.15) % 1.0
        # Perspective interpolation
        gy = ground_y + int((H - ground_y) * t)
        road_w = int(120 * t)
        cx = W // 2
        dash_w = max(2, int(road_w * 0.06))
        dash_h = max(4, int((H - ground_y) / num_dashes * 0.5))
        a_col = int(200 * t)
        ds = pygame.Surface((dash_w*2, dash_h), pygame.SRCALPHA)
        pygame.draw.rect(ds, (255, 210, 60, a_col), ds.get_rect(), border_radius=1)
        surface.blit(ds, (cx - dash_w, gy))

    # Radiator Springs power lines (telegraph poles along the road)
    for px in [W//4, W*3//4]:
        pygame.draw.line(surface, (20, 14, 8), (px, ground_y - 10), (px, ground_y + 80), 3)
        pygame.draw.line(surface, (20, 14, 8), (px - 20, ground_y + 10), (px + 20, ground_y + 10), 2)

    # Stars in the upper sky (barely visible in golden hour)
    import random as _r
    _r.seed(42)
    for _ in range(30):
        sx = _r.randint(0, W)
        sy = _r.randint(0, int(H * 0.3))
        b = int(60 + 60 * math.sin(time * 2.0 + sx * 0.1))
        pygame.draw.circle(surface, (b, b, int(b * 0.8)), (sx, sy), 1)


class SplashScreen:
    """Cinematic Cars-movie start screen with Radiator Springs desert sunset."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.time = 0.0
        self._bg: pygame.Surface | None = None
        self._bg_loaded = False
        self._alpha_in = 0.0
        self._prompt_blink = 0.0
        self._use_photo = False

        self._photo_names = [
            "home_bg.jpg",
            "images.jpg",
            "background.jpg",
            "vintage_race.jpg",
        ]

    def _ensure_bg(self, W: int, H: int) -> None:
        if self._bg_loaded:
            return
        self._bg_loaded = True
        # Try user photo first
        for name in self._photo_names:
            img = _load_image_or_fallback(name)
            if img is not None:
                img_w, img_h = img.get_size()
                scale = max(W / img_w, H / img_h)
                nw, nh = int(img_w * scale), int(img_h * scale)
                img = pygame.transform.smoothscale(img, (nw, nh))
                xo = (nw - W) // 2
                yo = (nh - H) // 2
                self._bg = img.subsurface(pygame.Rect(xo, yo, W, H)).copy()
                # Warm cinematic overlay
                dark = pygame.Surface((W, H), pygame.SRCALPHA)
                pygame.draw.rect(dark, (20, 10, 0, 170), dark.get_rect())
                self._bg.blit(dark, (0, 0))
                self._use_photo = True
                return
        # No photo — will draw procedurally each frame

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.switch_screen("main_menu", {})

    def update(self, dt: float) -> None:
        self.time += dt
        self._alpha_in = min(255, self._alpha_in + dt * 160)
        self._prompt_blink = (self._prompt_blink + dt) % 1.8

    def draw(self, surface: pygame.Surface) -> None:
        W, H = surface.get_size()
        self._ensure_bg(W, H)

        surface.fill((10, 5, 2))

        # Background
        if self._use_photo and self._bg:
            if self._alpha_in < 255:
                bg_copy = self._bg.copy()
                bg_copy.set_alpha(int(self._alpha_in))
                surface.blit(bg_copy, (0, 0))
            else:
                surface.blit(self._bg, (0, 0))
        else:
            # Procedural Radiator Springs desert sunset
            if self._alpha_in < 255:
                proc = pygame.Surface((W, H))
                _draw_desert_bg(proc, W, H, self.time)
                proc.set_alpha(int(self._alpha_in))
                surface.blit(proc, (0, 0))
            else:
                _draw_desert_bg(surface, W, H, self.time)

        # ── CARS-movie style title ────────────────────────────────────────────
        # Outer glow
        for goff in [6, 4, 2]:
            gl = get_font(size=84+goff, bold=True).render("LEGENDARY MOTORS", True, (140, 60, 0))
            gl.set_alpha(40)
            surface.blit(gl, gl.get_rect(center=(W//2, H//2 - 50)))

        # Main title — metallic chrome gradient effect via layered blits
        title_font = get_font(size=84, bold=True)
        title_colors = [(180, 100, 20), (255, 200, 60), (255, 240, 140), (255, 200, 60)]
        for i, col in enumerate(title_colors):
            ty = H//2 - 50 + i
            t1 = title_font.render("LEGENDARY MOTORS", True, col)
            if i == 2:  # top highlight brightest
                surface.blit(t1, t1.get_rect(center=(W//2, ty)))
            else:
                t1.set_alpha(160 + i*20)
                surface.blit(t1, t1.get_rect(center=(W//2, ty)))

        sub_font = get_font(size=36, bold=True)
        sub = sub_font.render("GRAND CHAMPIONSHIP", True, (255, 180, 0))
        surface.blit(sub, sub.get_rect(center=(W//2, H//2 + 42)))

        # Route 66 shield decoration
        shield_x, shield_y = W//2 - 320, H//2 - 72
        self._draw_route66_shield(surface, shield_x, shield_y, 46)
        self._draw_route66_shield(surface, W//2 + 300, H//2 - 72, 46)

        # Piston Cup divider line
        for dy in range(-1, 2):
            lc = (200, 120, 20) if dy == 0 else (100, 60, 10)
            pygame.draw.line(surface, lc, (W//2 - 320, H//2 + 78 + dy), (W//2 + 320, H//2 + 78 + dy), 1)

        # "PRESS ANY KEY" blinking prompt
        if self._prompt_blink < 1.1:
            alpha = int(255 * min(1.0, 2.0 * self._prompt_blink) if self._prompt_blink < 0.55
                        else 255 * max(0.0, 1.0 - (self._prompt_blink - 0.55) * 2.5))
            prompt = get_ui_font(size=20, bold=True).render(
                "PRESS ANY KEY  TO  START  YOUR  ENGINE", True, (255, 220, 100))
            prompt.set_alpha(alpha)
            surface.blit(prompt, prompt.get_rect(center=(W//2, H//2 + 108)))

        # Corner credits
        cr = get_ui_font(size=11).render(
            "FAST-NUCES  DAA Semester 5  |  Aoun  |  Mohzar  |  Sarim",
            True, (120, 80, 40))
        surface.blit(cr, cr.get_rect(center=(W//2, H - 18)))

    def _draw_route66_shield(self, surface: pygame.Surface, cx: int, cy: int, size: int) -> None:
        """Draw an iconic Route 66 road shield badge."""
        # Outer black shield
        pts = [
            (cx, cy - size),
            (cx + size*0.7, cy - size*0.3),
            (cx + size*0.7, cy + size*0.5),
            (cx, cy + size*0.9),
            (cx - size*0.7, cy + size*0.5),
            (cx - size*0.7, cy - size*0.3),
        ]
        pts = [(int(x), int(y)) for x, y in pts]
        pygame.draw.polygon(surface, (20, 10, 5), pts)
        pygame.draw.polygon(surface, (180, 100, 20), pts, 2)
        # Inner "66" text
        f = get_ui_font(size=12, bold=True)
        t = f.render("66", True, (255, 200, 60))
        surface.blit(t, t.get_rect(center=(cx, cy + 2)))
        t2 = get_ui_font(size=7).render("ROUTE", True, (200, 150, 60))
        surface.blit(t2, t2.get_rect(center=(cx, cy - 10)))
