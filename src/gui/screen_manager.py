"""src/gui/screen_manager.py — Screen Manager and State Router.
"""

from typing import Dict
import pygame
from src.gui.screens.main_menu import MainMenuScreen
from src.gui.screens.track_explorer import TrackExplorerScreen
from src.gui.screens.racing_screen import RacingScreen
from src.gui.screens.algorithm_lab import AlgorithmLabScreen
from src.gui.screens.dashboard import DashboardScreen


class ScreenManager:
    """Orchestrates transitions between the 5 required GUI screens."""

    def __init__(self):
        self.screens: Dict[str, object] = {
            "main_menu": MainMenuScreen(self.switch_to),
            "track_explorer": TrackExplorerScreen(self.switch_to),
            "racing": RacingScreen(self.switch_to),
            "algorithm_lab": AlgorithmLabScreen(self.switch_to),
            "dashboard": DashboardScreen(self.switch_to),
        }
        self.active_screen_name: str = "main_menu"
        self.active_screen = self.screens["main_menu"]

    def switch_to(self, screen_name: str, context: Dict = None) -> None:
        if screen_name in self.screens:
            self.active_screen_name = screen_name
            self.active_screen = self.screens[screen_name]
            if context and hasattr(self.active_screen, "set_context"):
                self.active_screen.set_context(context)

    def handle_event(self, event: pygame.event.Event) -> None:
        self.active_screen.handle_event(event)

    def update(self, dt: float) -> None:
        self.active_screen.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.active_screen.draw(surface)
