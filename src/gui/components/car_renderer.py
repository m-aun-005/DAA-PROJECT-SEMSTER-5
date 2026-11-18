"""src/gui/components/car_renderer.py — Classic Muscle Car Renderer with pseudo-3D look.

Draws detailed 2D cars that evoke a 3D feel through:
- Gradient shading (lighter top, darker sides)
- Drop shadows
- Detailed polygon shapes matching real classic muscle car proportions
- Roof perspective distortion
- Metallic highlight strips
"""

from typing import Tuple, List
import math
import pygame


# ─── Legendary Classic Car Catalogue (1960s-70s) ─────────────────────────────
CAR_DESIGNS = [
    # 0: Ford GT40 Mk.II (1966 Le Mans winner) — Gulf livery blue/orange
    {
        "name":        "Ford GT40 Mk.II",
        "year":        "1966",
        "class":       "GT",
        "body":        (0,   75,  135),    # Gulf blue
        "body_hi":     (20,  120, 190),    # highlight
        "body_lo":     (0,   40,   80),    # shadow
        "roof":        (0,   50,  100),
        "trim":        (255, 120,   0),    # Gulf orange accent
        "win":         (100, 180, 220),
        "wheel":       (20,   20,  20),
        "rim":         (200, 200, 200),
        "stripe_col":  (255, 120,   0),
    },
    # 1: Shelby Mustang GT500 (1967) — Black & gold
    {
        "name":        "Shelby GT500",
        "year":        "1967",
        "class":       "Pony Car",
        "body":        (20,  20,  20),
        "body_hi":     (60,  60,  60),
        "body_lo":     (5,    5,   5),
        "roof":        (10,  10,  10),
        "trim":        (200, 160,   0),    # gold
        "win":         (80,  120, 160),
        "wheel":       (15,  15,  15),
        "rim":         (220, 180,  20),
        "stripe_col":  (200, 160,   0),
    },
    # 2: Dodge Charger R/T (1969) — General Lee orange
    {
        "name":        "Dodge Charger R/T",
        "year":        "1969",
        "class":       "Muscle",
        "body":        (220,  70,   0),
        "body_hi":     (255, 120,  20),
        "body_lo":     (140,  40,   0),
        "roof":        (180,  50,   0),
        "trim":        (240, 240, 240),
        "win":         (90,  140, 180),
        "wheel":       (20,  20,  20),
        "rim":         (220, 220, 220),
        "stripe_col":  (240, 240, 240),
    },
    # 3: Ferrari 250 GTO (1962) — Rosso Corsa red
    {
        "name":        "Ferrari 250 GTO",
        "year":        "1962",
        "class":       "GT",
        "body":        (200,  10,   10),
        "body_hi":     (255,  60,   40),
        "body_lo":     (120,   5,    5),
        "roof":        (160,   8,    8),
        "trim":        (220, 220, 220),
        "win":         (100, 160, 200),
        "wheel":       (20,  20,  20),
        "rim":         (200, 200, 200),
        "stripe_col":  (255, 220, 220),
    },
    # 4: Pontiac GTO (1969) — 'The Judge' orange/black
    {
        "name":        "Pontiac GTO",
        "year":        "1969",
        "class":       "Muscle",
        "body":        (230, 110,   0),
        "body_hi":     (255, 160,  20),
        "body_lo":     (160,  70,   0),
        "roof":        (20,   20,  20),
        "trim":        (20,   20,  20),
        "win":         (80,  130, 160),
        "wheel":       (20,  20,  20),
        "rim":         (180, 180, 180),
        "stripe_col":  (255, 255, 100),
    },
    # 5: Chevrolet Camaro Z28 (1969) — Hugger orange with black stripes
    {
        "name":        "Chevy Camaro Z28",
        "year":        "1969",
        "class":       "Pony Car",
        "body":        (200,  80,   0),
        "body_hi":     (240, 130,  20),
        "body_lo":     (120,  40,   0),
        "roof":        (10,   10,  10),
        "trim":        (10,   10,  10),
        "win":         (80,  130, 165),
        "wheel":       (20,  20,  20),
        "rim":         (200, 200, 200),
        "stripe_col":  (20,   20,  20),
    },
    # 6: AC Cobra 427 (1965) — British racing green
    {
        "name":        "AC Cobra 427",
        "year":        "1965",
        "class":       "Roadster",
        "body":        (20,   80,  20),
        "body_hi":     (50,  130,  50),
        "body_lo":     (5,    40,   5),
        "roof":        (10,   10,  10),
        "trim":        (220, 220, 220),
        "win":         (80,  160, 200),
        "wheel":       (20,  20,  20),
        "rim":         (220, 220, 220),
        "stripe_col":  (220, 220, 220),
    },
    # 7: Jaguar E-Type (1961) — British Racing Silver
    {
        "name":        "Jaguar E-Type",
        "year":        "1961",
        "class":       "GT",
        "body":        (180, 180, 185),
        "body_hi":     (230, 230, 235),
        "body_lo":     (100, 100, 110),
        "roof":        (140, 140, 145),
        "trim":        (20,   20,  20),
        "win":         (100, 160, 210),
        "wheel":       (20,  20,  20),
        "rim":         (200, 200, 200),
        "stripe_col":  (220, 180,  20),
    },
]


def _rot(cx, cy, px, py, angle):
    dx, dy = px - cx, py - cy
    ca, sa = math.cos(angle), math.sin(angle)
    return (int(cx + dx*ca - dy*sa), int(cy + dx*sa + dy*ca))


def _shade_color(col: Tuple, factor: float) -> Tuple:
    return (min(255, max(0, int(col[0]*factor))),
            min(255, max(0, int(col[1]*factor))),
            min(255, max(0, int(col[2]*factor))))


def draw_car_at(surface: pygame.Surface,
                cx: float, cy: float,
                car_index: int,
                angle: float = 0.0,
                scale: float = 1.0,
                nitro_active: bool = False,
                is_human: bool = False,
                show_shadow: bool = True) -> None:
    """Draw a classic muscle car with pseudo-3D shading."""
    ci  = max(0, min(len(CAR_DESIGNS)-1, car_index))
    des = CAR_DESIGNS[ci]

    W  = int(13 * scale)   # half-width
    HL = int(24 * scale)   # half-length

    def r(px, py):
        return _rot(cx, cy, cx + px, cy + py, angle)

    # ── Shadow (soft ellipse) ────────────────────────────────────────────────
    if show_shadow:
        shadow = pygame.Surface((W*4+10, HL*2+10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 55), shadow.get_rect())
        surface.blit(shadow, (int(cx) - W*2 - 5 + int(4*scale),
                              int(cy) - HL - 5 + int(5*scale)))

    # ── Nitro exhaust ────────────────────────────────────────────────────────
    if nitro_active:
        for t in range(4):
            rsz = int(W * (2.2 - t * 0.5))
            alpha = max(0, 200 - t * 50)
            exh = pygame.Surface((rsz*2, rsz*2), pygame.SRCALPHA)
            pygame.draw.circle(exh, (0, 160+t*20, 255, alpha), (rsz, rsz), rsz)
            bx = int(cx - math.cos(angle) * (HL + t * int(W*0.7))) - rsz
            by = int(cy - math.sin(angle) * (HL + t * int(W*0.7))) - rsz
            surface.blit(exh, (bx, by))

    # ── Wheels (thick, with rim detail) ─────────────────────────────────────
    WW, WL = int(5*scale), int(8*scale)
    wheels = [
        (-W + int(2*scale), -int(HL*0.62)),
        ( W - int(2*scale), -int(HL*0.62)),
        (-W + int(2*scale),  int(HL*0.52)),
        ( W - int(2*scale),  int(HL*0.52)),
    ]
    for wx, wy in wheels:
        pts = [r(wx-WW, wy-WL), r(wx+WW, wy-WL), r(wx+WW, wy+WL), r(wx-WW, wy+WL)]
        pygame.draw.polygon(surface, des["wheel"], pts)
        # Tire sidewall highlight
        pygame.draw.polygon(surface, (40, 40, 40), pts, 1)
        # Rim
        wc = r(wx, wy)
        rim_r = max(2, int(3.5*scale))
        pygame.draw.circle(surface, des["rim"], wc, rim_r)
        pygame.draw.circle(surface, _shade_color(des["rim"], 0.6), wc, rim_r, 1)
        # Spoke detail
        spoke_col = _shade_color(des["rim"], 0.8)
        for sk in range(5):
            ang_sp = angle + sk * math.pi * 2 / 5
            spx = wc[0] + int(math.cos(ang_sp) * rim_r * 0.75)
            spy = wc[1] + int(math.sin(ang_sp) * rim_r * 0.75)
            pygame.draw.line(surface, spoke_col, wc, (spx, spy), 1)

    # ── Fender flares (wide body) ────────────────────────────────────────────
    fender_col = _shade_color(des["body_lo"], 0.8)
    fenders = [
        [r(-W-int(2*scale), -int(HL*0.72)), r(-W-int(2*scale), -int(HL*0.48)),
         r(-W, -int(HL*0.4)), r(-W, -int(HL*0.68))],
        [r( W+int(2*scale), -int(HL*0.72)), r( W+int(2*scale), -int(HL*0.48)),
         r( W,  -int(HL*0.4)), r( W, -int(HL*0.68))],
        [r(-W-int(2*scale), int(HL*0.4)), r(-W-int(2*scale), int(HL*0.62)),
         r(-W,  int(HL*0.56)), r(-W, int(HL*0.36))],
        [r( W+int(2*scale), int(HL*0.4)), r( W+int(2*scale), int(HL*0.62)),
         r( W,  int(HL*0.56)), r( W, int(HL*0.36))],
    ]
    for fender in fenders:
        pygame.draw.polygon(surface, fender_col, fender)

    # ── Car body — base color ────────────────────────────────────────────────
    body_pts = [
        r(-W,          -int(HL*0.28)),
        r( W,          -int(HL*0.28)),
        r( W,           int(HL*0.52)),
        r( int(W*0.65), int(HL)),
        r(-int(W*0.65), int(HL)),
        r(-W,           int(HL*0.52)),
    ]
    pygame.draw.polygon(surface, des["body"], body_pts)

    # ── Body side shading (gradient simulation via layered horizontal strips) ─
    # Left darker shade
    left_shade = [r(-W, -int(HL*0.28)), r(-int(W*0.7), -int(HL*0.28)),
                  r(-int(W*0.7), int(HL*0.52)), r(-W, int(HL*0.52))]
    shade_surf = pygame.Surface((int(W*0.3*2)+10, HL*2+10), pygame.SRCALPHA)
    pygame.draw.polygon(surface, (*des["body_lo"], 180), left_shade)

    # Right darker shade
    right_shade = [r(W, -int(HL*0.28)), r(int(W*0.7), -int(HL*0.28)),
                   r(int(W*0.7), int(HL*0.52)), r(W, int(HL*0.52))]
    pygame.draw.polygon(surface, (*des["body_lo"], 180), right_shade)

    # Center highlight strip
    hi_w = max(2, int(W*0.3))
    hi_pts = [r(-hi_w, -int(HL*0.2)), r(hi_w, -int(HL*0.2)),
              r(hi_w,   int(HL*0.4)), r(-hi_w, int(HL*0.4))]
    hi_surf = pygame.Surface((hi_w*2+10, HL+10), pygame.SRCALPHA)
    pygame.draw.polygon(surface, (*des["body_hi"], 100), hi_pts)

    # ── Rear spoiler / trunk ─────────────────────────────────────────────────
    spoiler_pts = [r(-W+int(1*scale), -int(HL*0.28)),
                   r( W-int(1*scale), -int(HL*0.28)),
                   r( W-int(1*scale), -int(HL*0.48)),
                   r(-W+int(1*scale), -int(HL*0.48))]
    pygame.draw.polygon(surface, des["trim"], spoiler_pts)
    # Spoiler wing lip
    pygame.draw.line(surface, _shade_color(des["trim"], 1.3),
                     r(-W+int(1*scale), -int(HL*0.48)),
                     r( W-int(1*scale), -int(HL*0.48)), max(1, int(2*scale)))

    # ── Racing stripe ────────────────────────────────────────────────────────
    stripe_w = max(1, int(4*scale))
    stripe_pts = [r(-stripe_w, -int(HL*0.26)), r(stripe_w, -int(HL*0.26)),
                  r(stripe_w,   int(HL*0.9)),  r(-stripe_w, int(HL*0.9))]
    stripe_surf = pygame.Surface((stripe_w*4, HL*3), pygame.SRCALPHA)
    pygame.draw.polygon(surface, (*des["stripe_col"], 160), stripe_pts)

    # ── Cabin / Roofline ─────────────────────────────────────────────────────
    CW, CH = int(W*0.75), int(HL*0.52)
    roof_pts = [
        r(-CW,          int(CH*0.08)),
        r( CW,          int(CH*0.08)),
        r( int(CW*0.78), int(CH*0.9)),
        r(-int(CW*0.78), int(CH*0.9)),
    ]
    pygame.draw.polygon(surface, des["roof"], roof_pts)

    # Roof highlight
    rhi_w = int(CW * 0.4)
    rhi_pts = [r(-rhi_w, int(CH*0.1)), r(rhi_w, int(CH*0.1)),
               r(rhi_w, int(CH*0.4)), r(-rhi_w, int(CH*0.4))]
    pygame.draw.polygon(surface, (*_shade_color(des["roof"], 2.0), 70), rhi_pts)

    # ── Front windshield ─────────────────────────────────────────────────────
    WI_W = int(CW * 0.88)
    wind_pts = [
        r(-WI_W,           int(CH*0.65)),
        r( WI_W,           int(CH*0.65)),
        r( int(WI_W*0.78), int(CH*0.95)),
        r(-int(WI_W*0.78), int(CH*0.95)),
    ]
    pygame.draw.polygon(surface, des["win"], wind_pts)
    # Windshield glare
    glare_pts = [r(-int(WI_W*0.5), int(CH*0.68)),
                 r(-int(WI_W*0.1), int(CH*0.68)),
                 r(-int(WI_W*0.15), int(CH*0.82)),
                 r(-int(WI_W*0.55), int(CH*0.82))]
    pygame.draw.polygon(surface, (220, 240, 255, 120), glare_pts)

    # ── Rear window ──────────────────────────────────────────────────────────
    rw_pts = [r(-int(CW*0.72), int(CH*0.08)), r( int(CW*0.72), int(CH*0.08)),
              r( int(CW*0.76), int(CH*0.32)), r(-int(CW*0.76), int(CH*0.32))]
    pygame.draw.polygon(surface, des["win"], rw_pts)

    # ── Headlights (round) ───────────────────────────────────────────────────
    for hx in [-int(W*0.52), int(W*0.52)]:
        hp = r(hx, int(HL*0.9))
        pygame.draw.circle(surface, (255, 250, 210), hp, max(2, int(4*scale)))
        pygame.draw.circle(surface, (255, 255, 255), hp, max(1, int(2*scale)))
        pygame.draw.circle(surface, (200, 200, 200), hp, max(2, int(4*scale)), 1)

    # ── Tail lights ───────────────────────────────────────────────────────────
    for tx in [-int(W*0.6), int(W*0.6)]:
        tp = r(tx, -int(HL*0.4))
        pygame.draw.circle(surface, (220, 20, 20), tp, max(2, int(3*scale)))
        pygame.draw.circle(surface, (255, 80, 80), tp, max(1, int(1.5*scale)))

    # ── Body outline ─────────────────────────────────────────────────────────
    pygame.draw.polygon(surface, _shade_color(des["body_lo"], 0.6), body_pts, max(1, int(scale)))

    # ── Player ring ──────────────────────────────────────────────────────────
    if is_human:
        pygame.draw.circle(surface, (0, 230, 255), (int(cx), int(cy)),
                           int(HL + 5*scale), 2)


def draw_garage_car(surface: pygame.Surface,
                    cx: float, cy: float,
                    car_index: int,
                    scale: float = 4.0) -> None:
    """Draw a large showcase car (for Car Select screen), facing north."""
    draw_car_at(surface, cx, cy, car_index,
                angle=math.pi / 2,
                scale=scale, nitro_active=False, is_human=False, show_shadow=True)


class CarRenderer:
    """Backward-compatible wrapper."""
    def __init__(self, surface: pygame.Surface):
        self.surface = surface

    def draw_car(self, pos, color, is_human=False, nitro_active=False, car_index=0):
        draw_car_at(self.surface, pos[0], pos[1], car_index=car_index,
                    angle=0.0, scale=1.0, nitro_active=nitro_active, is_human=is_human)
