"""src/gui/components/car_renderer.py — Detailed polygon car sprite renderer.

Draws top-down vector cars for each of the 4 car types (Asphalt 8-style look).
Each car is a composition of pygame.draw primitives — no external image files needed.
"""

from typing import Tuple
import math
import pygame


# ─── Car Design Catalogue ────────────────────────────────────────────────────
# Each entry: (body_color, roof_color, window_color, wheel_color, name)
CAR_DESIGNS = [
    # 0 Apex Viper  — sportcar
    {"body": (220,  40,  40), "roof": (160,  20,  20), "win": (100, 180, 220), "trim": (255, 200, 200)},
    # 1 Storm GT    — hypercar
    {"body": (40,  110, 240), "roof": (20,   60, 160), "win": (160, 220, 255), "trim": (200, 230, 255)},
    # 2 Shadow X    — muscle
    {"body": (230, 160,  10), "roof": (160, 100,   5), "win": (220, 240, 180), "trim": (255, 220, 100)},
    # 3 Phantom RS  — endurance
    {"body": (40,  200, 110), "roof": (20,  130,  70), "win": (160, 240, 200), "trim": (180, 255, 220)},
]


def _rot_pt(cx: float, cy: float, px: float, py: float, angle: float) -> Tuple[int, int]:
    """Rotate point (px, py) around center (cx, cy) by angle (radians)."""
    dx, dy = px - cx, py - cy
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    rx = cx + dx * cos_a - dy * sin_a
    ry = cy + dx * sin_a + dy * cos_a
    return (int(rx), int(ry))


def draw_car_at(surface: pygame.Surface,
                cx: float, cy: float,
                car_index: int,
                angle: float = 0.0,
                scale: float = 1.0,
                nitro_active: bool = False,
                is_human: bool = False,
                show_shadow: bool = True) -> None:
    """
    Draw a detailed top-down car at world coords (cx, cy).
    angle = radians (0 = facing right/east).
    scale = 1.0 for normal race size, ~3.0 for garage preview.
    """
    ci   = max(0, min(3, car_index))
    des  = CAR_DESIGNS[ci]
    body = des["body"]
    roof = des["roof"]
    win  = des["win"]
    trim = des["trim"]

    W  = int(14 * scale)   # half-width
    HL = int(22 * scale)   # half-length

    def r(px, py):
        return _rot_pt(cx, cy, cx + px, cy + py, angle)

    # ── Shadow ──────────────────────────────────────────────────────────────
    if show_shadow:
        shadow_surf = pygame.Surface((HL*4, HL*4), pygame.SRCALPHA)
        pts_s = [r(-W+2, -HL+2), r(W+2, -HL+2), r(W+2, HL+2), r(-W+2, HL+2)]
        pygame.draw.polygon(surface, (0, 0, 0, 60), pts_s)

    # ── Nitro exhaust ────────────────────────────────────────────────────────
    if nitro_active:
        for t in range(3):
            flm = pygame.Surface((int(W*4), int(W*4)), pygame.SRCALPHA)
            rad = int(W * (2.0 - t * 0.5))
            alpha = max(0, 180 - t * 60)
            col_flame = (0, 180 + t*20, 255, alpha)
            pygame.draw.circle(flm, col_flame, (flm.get_width()//2, flm.get_height()//2), rad)
            # offset backward
            bx = int(cx - math.cos(angle) * (HL + t * int(W * 0.8)))
            by = int(cy - math.sin(angle) * (HL + t * int(W * 0.8)))
            surface.blit(flm, (bx - flm.get_width()//2, by - flm.get_height()//2))

    # ── Wheels ────────────────────────────────────────────────────────────────
    wheel_col = (20, 20, 20)
    rim_col   = (160, 160, 170)
    WW = int(5 * scale); WL = int(7 * scale)
    wheel_positions = [
        (-W + int(2*scale),  -int(HL * 0.6)),   # Front-left
        ( W - int(2*scale),  -int(HL * 0.6)),   # Front-right
        (-W + int(2*scale),   int(HL * 0.6)),   # Rear-left
        ( W - int(2*scale),   int(HL * 0.6)),   # Rear-right
    ]
    for wx, wy in wheel_positions:
        pts_w = [r(wx-WW, wy-WL), r(wx+WW, wy-WL), r(wx+WW, wy+WL), r(wx-WW, wy+WL)]
        pygame.draw.polygon(surface, wheel_col, pts_w)
        # Rim highlight
        wc = r(wx, wy)
        pygame.draw.circle(surface, rim_col, wc, max(1, int(3*scale)))

    # ── Body (main hull) ─────────────────────────────────────────────────────
    # Tapered nose at front
    pts_body = [
        r(-W,          -int(HL * 0.3)),   # Rear-left wide
        r( W,          -int(HL * 0.3)),   # Rear-right wide
        r( W,           int(HL * 0.55)),  # Front-right mid
        r( int(W*0.6),  int(HL)),         # Front-right nose
        r(-int(W*0.6),  int(HL)),         # Front-left nose
        r(-W,           int(HL * 0.55)),  # Front-left mid
    ]
    pygame.draw.polygon(surface, body, pts_body)

    # Rear spoiler
    pts_spoiler = [
        r(-W,          -int(HL * 0.3)),
        r( W,          -int(HL * 0.3)),
        r( W,          -int(HL * 0.5)),
        r(-W,          -int(HL * 0.5)),
    ]
    pygame.draw.polygon(surface, trim, pts_spoiler)
    pygame.draw.rect(surface, (10, 10, 10),
                     pygame.Rect(int(cx - W - 2), int(cy - int(HL*0.52)), int((W*2+4)), int(2*scale)),
                     1)

    # Side stripes
    stripe_col = (min(255, body[0]+40), min(255, body[1]+40), min(255, body[2]+40))
    pts_stripe_l = [r(-W+int(2*scale), int(HL*0.6)), r(-W+int(5*scale), int(HL*0.6)),
                    r(-W+int(5*scale), -int(HL*0.2)), r(-W+int(2*scale), -int(HL*0.2))]
    pts_stripe_r = [r(W-int(2*scale), int(HL*0.6)),  r(W-int(5*scale),  int(HL*0.6)),
                    r(W-int(5*scale), -int(HL*0.2)),  r(W-int(2*scale), -int(HL*0.2))]
    pygame.draw.polygon(surface, stripe_col, pts_stripe_l)
    pygame.draw.polygon(surface, stripe_col, pts_stripe_r)

    # ── Roof / Cabin ─────────────────────────────────────────────────────────
    CW = int(W * 0.72)
    CH = int(HL * 0.52)
    pts_roof = [
        r(-CW, int(CH * 0.1)),
        r( CW, int(CH * 0.1)),
        r( int(CW*0.75), int(CH * 0.9)),
        r(-int(CW*0.75), int(CH * 0.9)),
    ]
    pygame.draw.polygon(surface, roof, pts_roof)

    # ── Windshield (front) ──────────────────────────────────────────────────
    WI_W = int(CW * 0.85)
    pts_wind = [
        r(-WI_W,        int(CH * 0.65)),
        r( WI_W,        int(CH * 0.65)),
        r( int(WI_W*0.8), int(CH * 0.95)),
        r(-int(WI_W*0.8), int(CH * 0.95)),
    ]
    pygame.draw.polygon(surface, win, pts_wind)

    # ── Rear Window ──────────────────────────────────────────────────────────
    pts_rear_win = [
        r(-int(CW*0.7), int(CH * 0.1)),
        r( int(CW*0.7), int(CH * 0.1)),
        r( int(CW*0.75), int(CH * 0.3)),
        r(-int(CW*0.75), int(CH * 0.3)),
    ]
    pygame.draw.polygon(surface, win, pts_rear_win)

    # ── Headlights ─────────────────────────────────────────────────────────
    HL_W = int(5 * scale)
    for hx in [-int(W*0.55), int(W*0.55)]:
        h_pt = r(hx, int(HL * 0.9))
        pygame.draw.circle(surface, (255, 250, 200), h_pt, int(3*scale))
        pygame.draw.circle(surface, (255, 255, 255), h_pt, max(1, int(1.5*scale)))

    # ── Tail Lights ────────────────────────────────────────────────────────
    for tx in [-int(W*0.6), int(W*0.6)]:
        t_pt = r(tx, -int(HL * 0.42))
        pygame.draw.circle(surface, (255, 20, 20), t_pt, int(3*scale))

    # ── Body outline ─────────────────────────────────────────────────────────
    pygame.draw.polygon(surface, (10, 10, 20), pts_body, 1)

    # ── Player indicator ring ─────────────────────────────────────────────
    if is_human:
        pygame.draw.circle(surface, (0, 230, 255), (int(cx), int(cy)), int(HL + 5*scale), 2)


def draw_garage_car(surface: pygame.Surface,
                    cx: float, cy: float,
                    car_index: int,
                    scale: float = 3.5) -> None:
    """Draw a large showcase car (for Car Select screen), facing up (north)."""
    draw_car_at(surface, cx, cy, car_index,
                angle=math.pi / 2,   # face up
                scale=scale, nitro_active=False, is_human=False, show_shadow=True)


class CarRenderer:
    """Car and Vehicle Sprite Renderer wrapper for backward compatibility."""

    def __init__(self, surface: pygame.Surface):
        self.surface = surface

    def draw_car(self, pos: Tuple[int, int], color: Tuple[int, int, int], is_human: bool = False, nitro_active: bool = False, car_index: int = 0) -> None:
        draw_car_at(self.surface, pos[0], pos[1], car_index=car_index, angle=0.0, scale=1.0, nitro_active=nitro_active, is_human=is_human)

