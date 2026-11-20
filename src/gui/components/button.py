"""src/gui/components/button.py — Asphalt 8-style UI Button component.
"""

from typing import Callable, Optional, Tuple
import pygame
from src.gui.assets.colors import BTN_DEFAULT, BTN_HOVER, BTN_ACTIVE, BTN_TEXT, BTN_BORDER, PANEL_BORDER
from src.gui.assets.fonts import get_ui_font


def _draw_gradient_rect(surface: pygame.Surface, rect: pygame.Rect,
                        col_top: Tuple[int,int,int], col_bot: Tuple[int,int,int],
                        border_radius: int = 8) -> None:
    """Draw a vertical gradient rectangle."""
    clip = surface.get_clip()
    surface.set_clip(rect.inflate(2, 2))
    for y in range(rect.height):
        t = y / max(1, rect.height - 1)
        r = int(col_top[0] + (col_bot[0] - col_top[0]) * t)
        g = int(col_top[1] + (col_bot[1] - col_top[1]) * t)
        b = int(col_top[2] + (col_bot[2] - col_top[2]) * t)
        pygame.draw.line(surface, (r, g, b), (rect.x, rect.y + y), (rect.right, rect.y + y))
    surface.set_clip(clip)
    # rounded mask
    mask_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(mask_surf, (0, 0, 0, 0), mask_surf.get_rect())
    pygame.draw.rect(mask_surf, (255, 255, 255, 255), mask_surf.get_rect(), border_radius=border_radius)
    # apply mask by drawing transparent corners
    for corner_x in [rect.x, rect.right - border_radius]:
        for corner_y in [rect.y, rect.bottom - border_radius]:
            pass  # pygame-ce handles border_radius in draw.rect natively


class Button:
    """Asphalt 8-style clickable button with gradient, glow border, and hover animation."""

    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        text: str,
        callback: Optional[Callable[[], None]] = None,
        font_size: int = 16,
        bold: bool = True,
        icon: str = "",
        accent_color: Tuple[int, int, int] = (255, 160, 0),
    ):
        self.rect         = pygame.Rect(rect)
        self.text         = text
        self.callback     = callback
        self.icon         = icon
        self.accent_color = accent_color
        self.font         = get_ui_font(size=font_size, bold=bold)
        self.is_hovered   = False
        self.is_active    = False
        self._hover_alpha = 0   # animated 0-255

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def update(self, dt: float) -> None:
        target = 255 if (self.is_hovered or self.is_active) else 0
        speed  = 600
        if self._hover_alpha < target:
            self._hover_alpha = min(255, self._hover_alpha + speed * dt)
        elif self._hover_alpha > target:
            self._hover_alpha = max(0,   self._hover_alpha - speed * dt)

    def draw(self, surface: pygame.Surface) -> None:
        r = self.rect

        # Base fill — warm adobe brown (Cars palette)
        pygame.draw.rect(surface, (45, 28, 12), r, border_radius=7)

        # Gradient overlay on hover/active
        if self._hover_alpha > 0:
            ac = self.accent_color
            overlay = pygame.Surface(r.size, pygame.SRCALPHA)
            alpha   = int(self._hover_alpha * 0.35)
            pygame.draw.rect(overlay, (*ac, alpha), overlay.get_rect(), border_radius=7)
            surface.blit(overlay, r.topleft)

        # Left accent bar
        bar_color = self.accent_color if (self.is_hovered or self.is_active) else (90, 60, 24)
        pygame.draw.rect(surface, bar_color, pygame.Rect(r.x, r.y + 4, 4, r.height - 8), border_radius=2)

        # Border
        border_color = self.accent_color if (self.is_hovered or self.is_active) else PANEL_BORDER
        pygame.draw.rect(surface, border_color, r, width=1, border_radius=7)

        # Label
        label = f"{self.icon}  {self.text}" if self.icon else self.text
        txt_surf = self.font.render(label, True, BTN_TEXT)
        t_rect   = txt_surf.get_rect(center=r.center)
        t_rect.x = r.x + 16  # left-aligned with padding
        t_rect.centery = r.centery
        surface.blit(txt_surf, t_rect)


def draw_arrow_button(
    surface: pygame.Surface,
    rect,
    direction: str = "left",
    color: tuple = (255, 180, 40),
    hovered: bool = False,
    active: bool = False,
) -> None:
    """Draw a clean triangle arrow — NO rectangle background, transparent circle only.
    direction: 'left' or 'right'.
    """
    r = pygame.Rect(rect)
    cx, cy = r.centerx, r.centery
    rad = min(r.width, r.height) // 2

    # Subtle semi-transparent circle behind triangle (blends with any bg)
    circ = pygame.Surface((rad*2+2, rad*2+2), pygame.SRCALPHA)
    alpha = 160 if (hovered or active) else 80
    pygame.draw.circle(circ, (0, 0, 0, alpha), (rad+1, rad+1), rad)
    if hovered or active:
        pygame.draw.circle(circ, (*color, 60), (rad+1, rad+1), rad)
    surface.blit(circ, (cx - rad - 1, cy - rad - 1))

    # Filled triangle (the actual arrow)
    hw = max(4, rad * 6 // 10)
    hh = max(4, rad * 7 // 10)
    if direction == "left":
        pts = [(cx + hw, cy - hh), (cx + hw, cy + hh), (cx - hw, cy)]
    else:
        pts = [(cx - hw, cy - hh), (cx - hw, cy + hh), (cx + hw, cy)]
    tri_col = color if (hovered or active) else (200, 160, 60)
    pygame.draw.polygon(surface, tri_col, pts)
    # Outline
    pygame.draw.polygon(surface, (0, 0, 0), pts, 1)


class ArrowButton:
    """A clickable left/right arrow button drawn as a filled triangle polygon."""

    def __init__(
        self,
        rect,
        direction: str = "left",
        callback=None,
        color: tuple = (255, 180, 40),
    ):
        self.rect      = pygame.Rect(rect)
        self.direction = direction
        self.callback  = callback
        self.color     = color
        self.is_hovered = False
        self.is_active  = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def update(self, dt: float) -> None:
        pass  # no animation needed for simple arrows

    def draw(self, surface: pygame.Surface) -> None:
        draw_arrow_button(surface, self.rect, self.direction, self.color,
                          hovered=self.is_hovered, active=self.is_active)
