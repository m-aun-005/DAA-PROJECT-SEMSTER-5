"""src/gui/assets/fonts.py — Font loading helper with game-style fallbacks.
"""

from typing import Dict, Tuple
import pygame

_FONT_CACHE: Dict[Tuple[str, int, bool], pygame.font.Font] = {}  # cleared on every import

# Priority font families for in-game UI (cinematic/bold feel)
_GAME_FAMILIES = ["Arial Black", "Franklin Gothic Heavy", "Agency FB", "Arial", "sans-serif"]
_UI_FAMILIES   = ["Segoe UI", "Arial", "Helvetica", "sans-serif"]


def get_font(size: int = 16, bold: bool = False, family: str = "auto") -> pygame.font.Font:
    """Returns a cached SysFont. 'auto' selects the best available game font."""
    if not pygame.font.get_init():
        pygame.font.init()

    resolved_family = family
    if family == "auto":
        available = pygame.font.get_fonts()
        for f in _GAME_FAMILIES:
            if f.lower().replace(" ", "") in available:
                resolved_family = f
                break
        else:
            resolved_family = "Arial"

    key = (resolved_family, size, bold)
    if key not in _FONT_CACHE:
        try:
            _FONT_CACHE[key] = pygame.font.SysFont(resolved_family, size, bold=bold)
        except Exception:
            _FONT_CACHE[key] = pygame.font.Font(None, size + 4)

    return _FONT_CACHE[key]


def get_ui_font(size: int = 16, bold: bool = False) -> pygame.font.Font:
    """Clean UI font (Segoe UI / Arial)."""
    if not pygame.font.get_init():
        pygame.font.init()
    available = pygame.font.get_fonts()
    for f in _UI_FAMILIES:
        if f.lower().replace(" ", "") in available:
            return get_font(size=size, bold=bold, family=f)
    return get_font(size=size, bold=bold, family="Arial")
