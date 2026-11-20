"""src/gui/screens/splash_screen.py — Cinematic Splash / Start Screen.

Shows a real downloaded racing photograph as the background, with a dramatic
title overlay and PRESS START prompt.
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


class SplashScreen:
    """Cinematic start screen with real racing photo background."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.time = 0.0
        self._bg: pygame.Surface | None = None
        self._bg_loaded = False
        self._alpha_in = 0.0        # fade-in alpha 0→255
        self._prompt_blink = 0.0

        # Try multiple images in priority order
        self._image_names = [
            "home_bg.jpg",
            "images.jpg",
            "background.jpg",
            "vintage_race.jpg",
            "classic_car.jpg",
            "splash_bg.jpg",
            "racetrack_crowd.jpg",
        ]

    def _ensure_bg(self, W: int, H: int) -> None:
        if self._bg_loaded:
            return
        self._bg_loaded = True
        for name in self._image_names:
            img = _load_image_or_fallback(name)
            if img is not None:
                # Scale to cover the screen
                img_w, img_h = img.get_size()
                scale = max(W / img_w, H / img_h)
                new_w, new_h = int(img_w * scale), int(img_h * scale)
                img = pygame.transform.smoothscale(img, (new_w, new_h))
                # Center crop
                x_off = (new_w - W) // 2
                y_off = (new_h - H) // 2
                crop = img.subsurface(pygame.Rect(x_off, y_off, W, H))
                self._bg = crop.copy()
                # Apply vintage/cinematic filter: darken + desaturate slightly
                dark = pygame.Surface((W, H), pygame.SRCALPHA)
                pygame.draw.rect(dark, (0, 0, 0, 160), dark.get_rect())
                self._bg.blit(dark, (0, 0))
                # Add a bottom vignette
                vig = pygame.Surface((W, H), pygame.SRCALPHA)
                for y in range(H):
                    if y > H * 0.5:
                        a = int(140 * ((y - H*0.5) / (H*0.5)))
                        pygame.draw.line(vig, (0, 0, 0, a), (0, y), (W, y))
                self._bg.blit(vig, (0, 0))
                return
        # Fallback: dark gradient
        self._bg = pygame.Surface((W, H))
        for y in range(H):
            t = y / H
            r_ = int(5 + 20 * t); g_ = int(5 + 15 * t); b_ = int(10 + 30 * t)
            pygame.draw.line(self._bg, (r_, g_, b_), (0, y), (W, y))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.switch_screen("main_menu", {})

    def update(self, dt: float) -> None:
        self.time += dt
        self._alpha_in = min(255, self._alpha_in + dt * 180)
        self._prompt_blink = (self._prompt_blink + dt) % 1.6

    def draw(self, surface: pygame.Surface) -> None:
        W, H = surface.get_size()
        self._ensure_bg(W, H)

        surface.fill((0, 0, 0))

        # Background photo with fade-in
        if self._bg:
            if self._alpha_in < 255:
                bg_copy = self._bg.copy()
                bg_copy.set_alpha(int(self._alpha_in))
                surface.blit(bg_copy, (0, 0))
            else:
                surface.blit(self._bg, (0, 0))

        # Title overlay
        self._draw_title(surface, W, H)

    def _draw_title(self, surface: pygame.Surface, W: int, H: int) -> None:
        # Cinematic letterbox bars
        bar_h = int(H * 0.12)
        pygame.draw.rect(surface, (0, 0, 0), (0, 0, W, bar_h))
        pygame.draw.rect(surface, (0, 0, 0), (0, H - bar_h, W, bar_h))

        # Era badge
        era_font = get_ui_font(size=14, bold=True)
        era_txt  = era_font.render("LEGENDARY MOTORS CHAMPIONSHIP  ·  Est. 1962", True, TEXT_GOLD)
        surface.blit(era_txt, era_txt.get_rect(center=(W//2, 42)))

        # Main TITLE with glow
        title_font = get_font(size=76, bold=True)
        title_txt  = "LEGENDARY MOTORS"
        for off in [(4,4), (3,3), (2,2), (1,1)]:
            shadow = title_font.render(title_txt, True, (0, 60, 120))
            surface.blit(shadow, shadow.get_rect(center=(W//2+off[0], H//2 - 80 + off[1])))
        txt = title_font.render(title_txt, True, TEXT_WHITE)
        surface.blit(txt, txt.get_rect(center=(W//2, H//2 - 80)))

        # Sub-title
        sub_font = get_font(size=34, bold=True)
        sub_txt  = sub_font.render("GRAND CHAMPIONSHIP", True, TEXT_ACCENT)
        surface.blit(sub_txt, sub_txt.get_rect(center=(W//2, H//2 - 20)))

        # Underline
        bar_w = 540
        pygame.draw.rect(surface, TEXT_GOLD, (W//2 - bar_w//2, H//2 + 14, bar_w, 3), border_radius=2)

        # Cars of legend caption
        cars_font = get_ui_font(size=15)
        cars_txt  = cars_font.render(
            "Ford GT40  ·  Shelby GT500  ·  Dodge Charger  ·  Ferrari 250 GTO  ·  Pontiac GTO  ·  Cobra 427",
            True, (200, 200, 200))
        surface.blit(cars_txt, cars_txt.get_rect(center=(W//2, H//2 + 36)))

        # Pulsing PRESS ANY KEY
        if self._prompt_blink < 1.0:
            alpha = int(255 * math.sin(self._prompt_blink * math.pi))
            prompt_surf = pygame.Surface((500, 36), pygame.SRCALPHA)
            prompt_font = get_ui_font(size=22, bold=True)
            prompt_txt  = prompt_font.render("PRESS ANY KEY TO CONTINUE", True, (255, 255, 255))
            prompt_surf.set_alpha(alpha)
            prompt_surf.blit(prompt_txt, (0, 4))
            surface.blit(prompt_surf, prompt_surf.get_rect(center=(W//2, H - bar_h - 44)))

        # Copyright / credits bar
        cr_font = get_ui_font(size=11)
        cr_txt  = cr_font.render(
            "DAA Semester 5 Project  ·  Muhammad Aoun 24P-3099  ·  Abdullah Mohzar 24I-3124  ·  Muhammad Sarim 24I-3069",
            True, (100, 100, 100))
        surface.blit(cr_txt, cr_txt.get_rect(center=(W//2, H - 18)))

        # Animated car silhouettes crossing bottom
        self._draw_car_silhouettes(surface, W, H)

    def _draw_car_silhouettes(self, surface: pygame.Surface, W: int, H: int) -> None:
        """Draw simple animated silhouettes at the bottom."""
        speeds = [60, 90, 50, 110]
        offsets = [0.0, 0.3, 0.6, 0.15]
        bar_h = int(H * 0.12)
        y_base = H - bar_h - 10
        for i, (spd, off) in enumerate(zip(speeds, offsets)):
            x = int(((self.time * spd + off * W) % (W + 200)) - 100)
            y = y_base - i * 14
            # Simple silhouette rectangle car
            car_col = (20, 20, 20)
            pygame.draw.rect(surface, car_col, (x, y, 60, 12), border_radius=4)
            pygame.draw.rect(surface, car_col, (x+10, y-7, 36, 8), border_radius=3)
            pygame.draw.circle(surface, (30, 30, 30), (x+12, y+13), 7)
            pygame.draw.circle(surface, (30, 30, 30), (x+46, y+13), 7)
