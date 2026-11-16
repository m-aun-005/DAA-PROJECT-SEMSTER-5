"""src/gui/screens/__init__.py — Screen sub-package."""

from src.gui.screens.main_menu import MainMenuScreen
from src.gui.screens.track_explorer import TrackExplorerScreen
from src.gui.screens.racing_screen import RacingScreen
from src.gui.screens.algorithm_lab import AlgorithmLabScreen
from src.gui.screens.dashboard import DashboardScreen

__all__ = [
    "MainMenuScreen",
    "TrackExplorerScreen",
    "RacingScreen",
    "AlgorithmLabScreen",
    "DashboardScreen",
]
