"""src/gui/screens/__init__.py — Screen sub-package."""

from src.gui.screens.splash_screen    import SplashScreen
from src.gui.screens.main_menu        import MainMenuScreen
from src.gui.screens.championship     import ChampionshipScreen
from src.gui.screens.circuit_select   import CircuitSelectScreen
from src.gui.screens.car_select       import CarSelectScreen
from src.gui.screens.garage           import GarageScreen
from src.gui.screens.scoreboard       import ScoreboardScreen
from src.gui.screens.instructions     import InstructionsScreen
from src.gui.screens.track_explorer   import TrackExplorerScreen
from src.gui.screens.racing_screen    import RacingScreen
from src.gui.screens.algorithm_lab    import AlgorithmLabScreen
from src.gui.screens.dashboard        import DashboardScreen

__all__ = [
    "SplashScreen",
    "MainMenuScreen",
    "ChampionshipScreen",
    "CircuitSelectScreen",
    "CarSelectScreen",
    "GarageScreen",
    "ScoreboardScreen",
    "InstructionsScreen",
    "TrackExplorerScreen",
    "RacingScreen",
    "AlgorithmLabScreen",
    "DashboardScreen",
]
