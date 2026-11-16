"""src/gui/assets/fonts.py — Font loading helper for Pygame.
"""

from typing import Dict, Optional
import pygame


_FONT_CACHE: Dict[Tuple[str, int, bool], pygame.font.Font] = {}


def get_font(size: int = 16, bold: bool = False, family: str = "Arial") -> pygame.font.Font:
    """Returns a cached SysFont instance."""
    if not pygame.font.get_init():
        pygame.font.init()

    key = (family, size, bold)
    if key not in _FONT_CACHE:
        try:
            _FONT_CACHE[key] = pygame.font.SysFont(family, size, bold=bold)
        except Exception:
            _FONT_CACHE[key] = pygame.font.Font(None, size)

    return _FONT_CACHE[key]
