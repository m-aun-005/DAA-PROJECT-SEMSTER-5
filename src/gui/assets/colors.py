"""src/gui/assets/colors.py — Pixar Cars / Radiator Springs colour palette.

Warm desert Americana — terracotta rust, desert sand, Route 66 amber, neon
turquoise night accents, and chrome highlights.
"""
from typing import Tuple
RGB = Tuple[int, int, int]

# ── Core Background Layers ────────────────────────────────────────────────────
BG_DARK:        RGB = (28,  18,  10)       # Deep burnt sienna dark
BG_LAYER:       RGB = (42,  28,  14)       # Secondary layer — warm brown
PANEL_BG:       RGB = (54,  36,  18)       # Card / panel fill — adobe brown
PANEL_BORDER:   RGB = (140, 90,  40)       # Warm rust border
PANEL_GLOW:     RGB = (255, 160,  0)       # Amber / orange accent glow

# ── Typography ────────────────────────────────────────────────────────────────
TEXT_WHITE:     RGB = (255, 245, 220)      # Warm cream / parchment white
TEXT_MUTED:     RGB = (170, 130,  80)      # Dusty tan / muted sand
TEXT_ACCENT:    RGB = (255, 180,   0)      # Route 66 amber — primary accent
TEXT_GOLD:      RGB = (255, 210,  40)      # Piston Cup gold
TEXT_RED:       RGB = (220,  40,  20)      # Lightning McQueen red

# ── Road / Track ──────────────────────────────────────────────────────────────
ROAD_COLOR:     RGB = (58,  50,  40)       # Desert asphalt / weathered tarmac
ROAD_SURFACE:   RGB = (45,  38,  28)       # Road inner fill
ROAD_LINE:      RGB = (255, 230, 100)      # Yellow road markings (Route 66 style)
ROAD_GRASS:     RGB = (140, 100,  40)      # Desert sand / dry scrub
ROAD_RESTRICTED:RGB = (200, 120,  30)
ROAD_BLOCKED:   RGB = (200,  40,  20)
ROAD_SHORTCUT:  RGB = (255, 160,   0)      # Amber shortcut

# ── Vertices ─────────────────────────────────────────────────────────────────
VERTEX_NORMAL:        RGB = (110,  80,  50)
VERTEX_CHECKPOINT:    RGB = (255, 190,   0)
VERTEX_START_FINISH:  RGB = (200, 220, 200)   # Finish-line checker white
VERTEX_FUEL:          RGB = (0,   190, 160)   # Flo's V8 Cafe teal
VERTEX_NITRO:         RGB = (60,  180, 255)   # Ramone neon blue
VERTEX_DEAD_END:      RGB = (200,  60,  40)

# ── Algorithm Visualizer States ───────────────────────────────────────────────
COLOR_VISITED:       RGB = (90,   65,  40)
COLOR_FRONTIER:      RGB = (255, 195,   0)
COLOR_CURRENT:       RGB = (255, 255, 220)
COLOR_PATH_DIJKSTRA: RGB = (0,   160, 220)
COLOR_PATH_ASTAR:    RGB = (80,  210, 120)
COLOR_PATH_BFS:      RGB = (255, 170,   0)
COLOR_PATH_DFS:      RGB = (220,  80, 220)
COLOR_MST:           RGB = (200, 230, 255)

# ── Car Palette ───────────────────────────────────────────────────────────────
CAR_PLAYER: RGB = (200,  25,  15)      # Lightning McQueen Red
CAR_AI_1:   RGB = (40,   80, 140)     # Dinoco Blue
CAR_AI_2:   RGB = (90,  120,  60)     # Army Olive (Sarge)
CAR_AI_3:   RGB = (100,  60, 170)     # Ramone Purple

# ── UI Controls ───────────────────────────────────────────────────────────────
BTN_DEFAULT:   RGB = (60,   38,  18)   # Adobe brick
BTN_HOVER:     RGB = (180,  90,  20)   # Rust orange hover
BTN_ACTIVE:    RGB = (255, 140,   0)   # Amber active
BTN_TEXT:      RGB = (255, 245, 220)   # Warm cream text
BTN_BORDER:    RGB = (200, 120,  40)   # Rusted chrome border

# ── HUD ───────────────────────────────────────────────────────────────────────
HUD_BG:       RGB = (20,  12,   6)
NITRO_BLUE:   RGB = (0,   220, 255)    # Flo's neon turquoise
SPEED_AMBER:  RGB = (255, 165,   0)
HEALTH_GREEN: RGB = (60,  200,  80)
