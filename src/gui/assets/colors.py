"""src/gui/assets/colors.py — Color palette for the Pygame UI.
"""

from typing import Dict, Tuple

RGB = Tuple[int, int, int]

# Dark modern arcade theme
BG_DARK: RGB = (18, 20, 28)
PANEL_BG: RGB = (28, 32, 45)
PANEL_BORDER: RGB = (48, 55, 75)
TEXT_WHITE: RGB = (240, 242, 248)
TEXT_MUTED: RGB = (140, 148, 168)
TEXT_ACCENT: RGB = (0, 210, 255)

# Game entities
ROAD_COLOR: RGB = (65, 72, 92)
ROAD_RESTRICTED: RGB = (220, 150, 40)
ROAD_BLOCKED: RGB = (220, 50, 50)
ROAD_SHORTCUT: RGB = (255, 120, 0)

# Vertices
VERTEX_NORMAL: RGB = (100, 110, 135)
VERTEX_CHECKPOINT: RGB = (255, 200, 0)
VERTEX_START_FINISH: RGB = (50, 220, 100)
VERTEX_FUEL: RGB = (0, 200, 150)
VERTEX_NITRO: RGB = (0, 180, 255)
VERTEX_DEAD_END: RGB = (180, 50, 50)

# Algorithms / Visualizer states
COLOR_VISITED: RGB = (80, 90, 115)
COLOR_FRONTIER: RGB = (255, 200, 0)
COLOR_CURRENT: RGB = (255, 255, 255)
COLOR_PATH_DIJKSTRA: RGB = (0, 150, 255)
COLOR_PATH_ASTAR: RGB = (50, 220, 120)
COLOR_PATH_BFS: RGB = (255, 180, 0)
COLOR_PATH_DFS: RGB = (220, 80, 220)
COLOR_MST: RGB = (120, 220, 255)

# Car colors (Player + 3 AIs)
CAR_PLAYER: RGB = (240, 50, 50)       # Red
CAR_AI_1: RGB = (50, 120, 240)        # Blue
CAR_AI_2: RGB = (240, 180, 20)        # Yellow
CAR_AI_3: RGB = (50, 200, 120)        # Green

# Buttons
BTN_DEFAULT: RGB = (45, 52, 72)
BTN_HOVER: RGB = (65, 75, 105)
BTN_ACTIVE: RGB = (0, 160, 220)
BTN_TEXT: RGB = (255, 255, 255)
