"""src/gui/assets/colors.py — Color palette for the Pygame UI (Asphalt 8 dark cinematic theme).
"""

from typing import Tuple

RGB = Tuple[int, int, int]

# ── Core Background Layers ────────────────────────────────────────────────────
BG_DARK:        RGB = (8,  10,  16)       # Deepest background (near-black blue)
BG_LAYER:       RGB = (14, 17,  26)       # Secondary panel bg
PANEL_BG:       RGB = (20, 24,  36)       # Card / panel fill
PANEL_BORDER:   RGB = (38, 46,  68)       # Subtle panel border
PANEL_GLOW:     RGB = (0,  180, 255)      # Cyan accent border glow

# ── Typography ────────────────────────────────────────────────────────────────
TEXT_WHITE:     RGB = (240, 244, 255)     # Primary text
TEXT_MUTED:     RGB = (120, 132, 160)     # Secondary / disabled text
TEXT_ACCENT:    RGB = (0,   210, 255)     # Cyan highlight (Asphalt signature)
TEXT_GOLD:      RGB = (255, 196,  0)      # Gold / ranking
TEXT_RED:       RGB = (255,  56,  56)     # Danger / warning

# ── Road / Track ──────────────────────────────────────────────────────────────
ROAD_COLOR:     RGB = (52,  58,  78)      # Asphalt grey road
ROAD_SURFACE:   RGB = (40,  45,  62)      # Road inner fill
ROAD_LINE:      RGB = (230, 230, 230)     # White center dash
ROAD_GRASS:     RGB = (18,  42,  22)      # Grass/terrain behind track
ROAD_RESTRICTED:RGB = (220, 150, 40)
ROAD_BLOCKED:   RGB = (220,  50,  50)
ROAD_SHORTCUT:  RGB = (255, 120,   0)

# ── Vertices ─────────────────────────────────────────────────────────────────
VERTEX_NORMAL:        RGB = (80,  90, 115)
VERTEX_CHECKPOINT:    RGB = (255, 200,   0)
VERTEX_START_FINISH:  RGB = (50,  220, 100)
VERTEX_FUEL:          RGB = (0,   200, 150)
VERTEX_NITRO:         RGB = (0,   180, 255)
VERTEX_DEAD_END:      RGB = (180,  50,  50)

# ── Algorithm Visualizer States ───────────────────────────────────────────────
COLOR_VISITED:       RGB = (60,  70,  95)
COLOR_FRONTIER:      RGB = (255, 200,   0)
COLOR_CURRENT:       RGB = (255, 255, 255)
COLOR_PATH_DIJKSTRA: RGB = (0,  150, 255)
COLOR_PATH_ASTAR:    RGB = (50, 220, 120)
COLOR_PATH_BFS:      RGB = (255, 180,   0)
COLOR_PATH_DFS:      RGB = (220,  80, 220)
COLOR_MST:           RGB = (120, 220, 255)

# ── Car Palette ───────────────────────────────────────────────────────────────
CAR_PLAYER: RGB = (220,  40,  40)      # Apex Viper — Red
CAR_AI_1:   RGB = (40,  110, 240)     # Storm GT  — Blue
CAR_AI_2:   RGB = (240, 170,  10)     # Shadow X  — Gold
CAR_AI_3:   RGB = (40,  200, 110)     # Phantom RS — Green

# ── UI Controls ───────────────────────────────────────────────────────────────
BTN_DEFAULT:   RGB = (28,  34,  52)
BTN_HOVER:     RGB = (0,  140, 210)
BTN_ACTIVE:    RGB = (0,  195, 255)
BTN_TEXT:      RGB = (255, 255, 255)
BTN_BORDER:    RGB = (0,  180, 255)

# ── HUD ───────────────────────────────────────────────────────────────────────
HUD_BG:       RGB = (8,   10,  18)
NITRO_BLUE:   RGB = (0,   220, 255)
SPEED_AMBER:  RGB = (255, 165,   0)
HEALTH_GREEN: RGB = (40,  220,  80)
