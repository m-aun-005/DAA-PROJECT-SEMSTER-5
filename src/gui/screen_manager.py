"""src/gui/screen_manager.py — Screen Manager and State Router.

Manages all screens in Legendary Motors Championship:
- splash:       Start screen with real racing photo
- main_menu:    Central navigation hub
- championship: Coming-up seasons list
- circuit_select: Circuit / track cards
- car_select:   Car selection before racing
- garage:       3D-style classic muscle car showcase
- scoreboard:   Global championship points & podium
- instructions: How to play & controls
- racing:       Live 2D top-down racing simulation
- track_explorer: DAA route planner & graph explorer
- algorithm_lab: Step-by-step visualizer
- dashboard:    Post-race podium & sorting suite
"""

from typing import Dict
import pygame
from src.gui.screens.splash_screen     import SplashScreen
from src.gui.screens.main_menu         import MainMenuScreen
from src.gui.screens.championship      import ChampionshipScreen
from src.gui.screens.circuit_select    import CircuitSelectScreen
from src.gui.screens.car_select        import CarSelectScreen
from src.gui.screens.garage            import GarageScreen
from src.gui.screens.scoreboard        import ScoreboardScreen
from src.gui.screens.instructions      import InstructionsScreen
from src.gui.screens.track_explorer    import TrackExplorerScreen
from src.gui.screens.racing_screen     import RacingScreen
from src.gui.screens.algorithm_lab     import AlgorithmLabScreen
from src.gui.screens.dashboard         import DashboardScreen


class ScreenManager:
    """Orchestrates transitions between all GUI screens."""

    def __init__(self):
        self.screens: Dict[str, object] = {
            "splash":         SplashScreen(self.switch_to),
            "main_menu":      MainMenuScreen(self.switch_to),
            "championship":   ChampionshipScreen(self.switch_to),
            "circuit_select": CircuitSelectScreen(self.switch_to),
            "car_select":     CarSelectScreen(self.switch_to),
            "garage":         GarageScreen(self.switch_to),
            "scoreboard":     ScoreboardScreen(self.switch_to),
            "instructions":   InstructionsScreen(self.switch_to),
            "track_explorer": TrackExplorerScreen(self.switch_to),
            "racing":         RacingScreen(self.switch_to),
            "algorithm_lab":  AlgorithmLabScreen(self.switch_to),
            "dashboard":      DashboardScreen(self.switch_to),
        }
        self.active_screen_name: str = "splash"
        self.active_screen           = self.screens["splash"]

    def switch_to(self, screen_name: str, context: Dict = None) -> None:
        if screen_name in self.screens:
            self.active_screen_name = screen_name
            self.active_screen      = self.screens[screen_name]
            if context is not None and hasattr(self.active_screen, "set_context"):
                self.active_screen.set_context(context)

    def handle_event(self, event: pygame.event.Event) -> None:
        self.active_screen.handle_event(event)

    def update(self, dt: float) -> None:
        self.active_screen.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.active_screen.draw(surface)
