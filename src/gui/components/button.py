"""src/gui/components/button.py — Interactive Button UI component for Pygame.
"""

from typing import Callable, Optional, Tuple
import pygame
from src.gui.assets.colors import BTN_DEFAULT, BTN_HOVER, BTN_ACTIVE, BTN_TEXT
from src.gui.assets.fonts import get_font


class Button:
    """Rectangular clickable button."""

    def __init__(
        self,
        rect: Tuple[int, int, int, int],
        text: str,
        callback: Optional[Callable[[], None]] = None,
        font_size: int = 15,
        bold: bool = True
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.font = get_font(size=font_size, bold=bold)
        self.is_hovered: bool = False
        self.is_active: bool = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        color = BTN_ACTIVE if self.is_active else (BTN_HOVER if self.is_hovered else BTN_DEFAULT)
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, (80, 90, 120), self.rect, width=1, border_radius=6)

        text_surf = self.font.render(self.text, True, BTN_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
