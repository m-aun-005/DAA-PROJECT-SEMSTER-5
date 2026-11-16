"""src/gui/components/car_renderer.py — Car and Vehicle Sprite Renderer.
"""

from typing import Tuple
import math
import pygame
from src.models.vehicle import Vehicle


class CarRenderer:
    """Renders top-down 2D car bodies, rotation, and particle effects."""

    def __init__(self, surface: pygame.Surface):
        self.surface = surface

    def draw_car(self, pos: Tuple[int, int], color: Tuple[int, int, int], is_human: bool = False, nitro_active: bool = False) -> None:
        px, py = pos

        # Nitro flame
        if nitro_active:
            pygame.draw.circle(self.surface, (0, 210, 255), (px, py), 16, 2)
            pygame.draw.circle(self.surface, (255, 255, 255), (px, py), 8)

        # Car circle/body
        radius = 10 if is_human else 8
        pygame.draw.circle(self.surface, (12, 14, 20), (px, py), radius + 2)
        pygame.draw.circle(self.surface, color, (px, py), radius)
