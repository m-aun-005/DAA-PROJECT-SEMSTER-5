"""src/gui/components/car_renderer.py — Pixar Cars Movie Character Renderer.

Draws iconic Cars-movie characters as 2D cars with pseudo-3D shading.
Characters: Lightning McQueen, Mater, Sally Carrera, Doc Hudson, Chick Hicks,
            Strip Weathers (The King), Ramone, Jackson Storm.
"""
from typing import Tuple, List
import math
import pygame


# ─── Cars Movie Character Catalogue ──────────────────────────────────────────
CAR_DESIGNS = [
    # 0: Lightning McQueen — Rust-eze red with #95 and lightning bolt stripes
    {
        "name":        "Lightning McQueen",
        "year":        "2006",
        "class":       "Stock Car",
        "body":        (200,  25,  15),    # Hot-rod crimson red
        "body_hi":     (255,  80,  50),    # Bright highlight
        "body_lo":     (120,  10,   5),    # Deep shadow
        "roof":        (170,  18,  10),
        "trim":        (255, 200,   0),    # McQueen yellow/gold
        "win":         (140, 190, 220),    # Windshield blue (his eyes)
        "wheel":       (20,   20,  20),
        "rim":         (220, 220, 220),
        "stripe_col":  (255, 220,   0),    # Lightning bolt yellow
        "number":      "95",
        "sponsor":     "Rust-eze",
    },
    # 1: Chick Hicks — Dark green with mustache stripe, dirty player
    {
        "name":        "Chick Hicks",
        "year":        "2006",
        "class":       "Stock Car",
        "body":        (40,   80,  40),    # Murky dark green
        "body_hi":     (70,  120,  70),
        "body_lo":     (20,   50,  20),
        "roof":        (30,   65,  30),
        "trim":        (220, 200,   0),    # Yellow trim (Dinoco rival)
        "win":         (90,  140, 170),
        "wheel":       (20,   20,  20),
        "rim":         (160, 160, 160),
        "stripe_col":  (220, 200,   0),
        "number":      "86",
        "sponsor":     "Hostile Takeover",
    },
    # 2: Strip Weathers "The King" — Dinoco blue legend
    {
        "name":        "The King (#43)",
        "year":        "2006",
        "class":       "Stock Car",
        "body":        (30,   90, 180),    # Dinoco royal blue
        "body_hi":     (80,  150, 230),
        "body_lo":     (15,   55, 110),
        "roof":        (25,   75, 155),
        "trim":        (255, 255, 255),    # White (STP / Dinoco white)
        "win":         (140, 200, 240),
        "wheel":       (20,   20,  20),
        "rim":         (240, 240, 240),
        "stripe_col":  (255, 255, 255),
        "number":      "43",
        "sponsor":     "Dinoco",
    },
    # 3: Doc Hudson "Fabulous Hudson Hornet" — Classic navy blue
    {
        "name":        "Doc Hudson",
        "year":        "1951",
        "class":       "Hudson Hornet",
        "body":        (30,   40,  80),    # Dark navy blue
        "body_hi":     (60,   75, 130),
        "body_lo":     (15,   22,  50),
        "roof":        (22,   32,  65),
        "trim":        (200, 160,  40),    # Gold racing stripes (hidden)
        "win":         (110, 160, 210),
        "wheel":       (20,   20,  20),
        "rim":         (160, 160, 180),
        "stripe_col":  (200, 160,  40),
        "number":      "51",
        "sponsor":     "Hudson Hornet",
    },
    # 4: Sally Carrera — Metallic light blue Porsche
    {
        "name":        "Sally Carrera",
        "year":        "2002",
        "class":       "Porsche 911",
        "body":        (100, 160, 210),    # Metallic light blue
        "body_hi":     (160, 210, 250),
        "body_lo":     (60,  100, 150),
        "roof":        (80,  130, 180),
        "trim":        (220, 220, 230),    # Silver chrome trim
        "win":         (160, 210, 240),
        "wheel":       (20,   20,  20),
        "rim":         (220, 220, 230),
        "stripe_col":  (255, 180, 200),    # Pink tattoo pinstripe
        "number":      "",
        "sponsor":     "Cozy Cone Motel",
    },
    # 5: Ramone — 1959 Impala lowrider, vibrant purple (his ever-changing color)
    {
        "name":        "Ramone",
        "year":        "1959",
        "class":       "Impala Lowrider",
        "body":        (130,  40, 200),    # Ramone deep purple
        "body_hi":     (190,  90, 255),
        "body_lo":     (80,   20, 130),
        "roof":        (100,  30, 160),
        "trim":        (0,   220, 255),    # Neon turquoise pinstriping
        "win":         (100, 170, 220),
        "wheel":       (20,   20,  20),
        "rim":         (220, 180, 255),    # Purple-tinted chrome
        "stripe_col":  (0,   220, 255),
        "number":      "",
        "sponsor":     "Ramone's House of Body Art",
    },
    # 6: Jackson Storm — Sleek next-gen dark carbon racer (Cars 3)
    {
        "name":        "Jackson Storm",
        "year":        "2017",
        "class":       "Next-Gen Racer",
        "body":        (20,   22,  32),    # Midnight black carbon
        "body_hi":     (50,   55,  80),
        "body_lo":     (8,     8,  14),
        "roof":        (14,   16,  24),
        "trim":        (0,   180, 255),    # Ice blue neon trim
        "win":         (50,  130, 200),
        "wheel":       (10,   10,  12),
        "rim":         (100, 160, 220),    # Blue chrome
        "stripe_col":  (0,   160, 255),
        "number":      "20",
        "sponsor":     "Dinoco (Villain)",
    },
    # 7: Mater — Rusted brown 1955 tow truck
    {
        "name":        "Tow Mater",
        "year":        "1955",
        "class":       "Chevy Tow Truck",
        "body":        (130,  80,  40),    # Rusty brown
        "body_hi":     (175, 120,  65),
        "body_lo":     (80,   48,  22),
        "roof":        (100,  62,  30),
        "trim":        (90,   65,  35),    # Faded rust trim
        "win":         (100, 150, 180),    # Mismatched windshield
        "wheel":       (30,   25,  20),    # Worn wheels
        "rim":         (100,  80,  60),    # Rusty hubcap
        "stripe_col":  (160, 110,  60),
        "number":      "",
        "sponsor":     "Radiator Springs",
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
    """Draw a Cars-movie character car with pseudo-3D shading."""
    ci  = max(0, min(len(CAR_DESIGNS)-1, car_index))
    des = CAR_DESIGNS[ci]

    W  = int(13 * scale)   # half-width
    HL = int(24 * scale)   # half-length

    def r(px, py):
        return _rot(cx, cy, cx + px, cy + py, angle)

    # ── Shadow (soft ellipse under car) ──────────────────────────────────────
    if show_shadow:
        shadow = pygame.Surface((W*4+10, HL*2+10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60), shadow.get_rect())
        surface.blit(shadow, (int(cx) - W*2 - 5 + int(4*scale),
                              int(cy) - HL - 5 + int(5*scale)))

    # ── Nitro exhaust (Flo's neon turquoise) ─────────────────────────────────
    if nitro_active:
        for t in range(4):
            rsz = int(W * (2.2 - t * 0.5))
            alpha = max(0, 200 - t * 50)
            exh = pygame.Surface((rsz*2, rsz*2), pygame.SRCALPHA)
            pygame.draw.circle(exh, (0, 220+t*8, 200, alpha), (rsz, rsz), rsz)
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
        pygame.draw.polygon(surface, (40, 40, 40), pts, 1)
        wc = r(wx, wy)
        rim_r = max(2, int(3.5*scale))
        pygame.draw.circle(surface, des["rim"], wc, rim_r)
        pygame.draw.circle(surface, _shade_color(des["rim"], 0.6), wc, rim_r, 1)
        spoke_col = _shade_color(des["rim"], 0.8)
        for sk in range(5):
            ang_sp = angle + sk * math.pi * 2 / 5
            spx = wc[0] + int(math.cos(ang_sp) * rim_r * 0.75)
            spy = wc[1] + int(math.sin(ang_sp) * rim_r * 0.75)
            pygame.draw.line(surface, spoke_col, wc, (spx, spy), 1)

    # ── Fender flares ────────────────────────────────────────────────────────
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

    # ── Car body ─────────────────────────────────────────────────────────────
    body_pts = [
        r(-W,          -int(HL*0.28)),
        r( W,          -int(HL*0.28)),
        r( W,           int(HL*0.52)),
        r( int(W*0.65), int(HL)),
        r(-int(W*0.65), int(HL)),
        r(-W,           int(HL*0.52)),
    ]
    pygame.draw.polygon(surface, des["body"], body_pts)

    # Side shading
    left_shade = [r(-W, -int(HL*0.28)), r(-int(W*0.7), -int(HL*0.28)),
                  r(-int(W*0.7), int(HL*0.52)), r(-W, int(HL*0.52))]
    pygame.draw.polygon(surface, (*des["body_lo"], 180), left_shade)
    right_shade = [r(W, -int(HL*0.28)), r(int(W*0.7), -int(HL*0.28)),
                   r(int(W*0.7), int(HL*0.52)), r(W, int(HL*0.52))]
    pygame.draw.polygon(surface, (*des["body_lo"], 180), right_shade)

    # Center highlight strip
    hi_w = max(2, int(W*0.3))
    hi_pts = [r(-hi_w, -int(HL*0.2)), r(hi_w, -int(HL*0.2)),
              r(hi_w,   int(HL*0.4)), r(-hi_w, int(HL*0.4))]
    pygame.draw.polygon(surface, (*des["body_hi"], 100), hi_pts)

    # ── Racing stripe (the Cars-movie lightning bolt style) ───────────────────
    stripe_w = max(1, int(4*scale))
    # For McQueen, draw a wider central stripe
    if ci == 0:
        # McQueen lightning bolt: wider yellow centre stripe
        stripe_w = max(2, int(6*scale))
    stripe_pts = [r(-stripe_w, -int(HL*0.26)), r(stripe_w, -int(HL*0.26)),
                  r(stripe_w,   int(HL*0.9)),  r(-stripe_w, int(HL*0.9))]
    pygame.draw.polygon(surface, (*des["stripe_col"], 170), stripe_pts)

    # ── Rear section / spoiler ────────────────────────────────────────────────
    spoiler_pts = [r(-W+int(1*scale), -int(HL*0.28)),
                   r( W-int(1*scale), -int(HL*0.28)),
                   r( W-int(1*scale), -int(HL*0.48)),
                   r(-W+int(1*scale), -int(HL*0.48))]
    pygame.draw.polygon(surface, des["trim"], spoiler_pts)
    pygame.draw.line(surface, _shade_color(des["trim"], 1.3),
                     r(-W+int(1*scale), -int(HL*0.48)),
                     r( W-int(1*scale), -int(HL*0.48)), max(1, int(2*scale)))

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

    # ── Front windshield — Cars-movie style: expressive "eyes" ───────────────
    WI_W = int(CW * 0.88)
    wind_pts = [
        r(-WI_W,           int(CH*0.65)),
        r( WI_W,           int(CH*0.65)),
        r( int(WI_W*0.78), int(CH*0.95)),
        r(-int(WI_W*0.78), int(CH*0.95)),
    ]
    pygame.draw.polygon(surface, des["win"], wind_pts)

    # Cars-movie "eyes" on the windshield (white sclera + dark pupil)
    if scale >= 1.5:
        eye_y_base = int(CH * 0.78)
        for ex_off in [-int(WI_W*0.38), int(WI_W*0.38)]:
            ep = r(ex_off, eye_y_base)
            er = max(2, int(5 * scale * 0.5))
            # Sclera (white)
            pygame.draw.circle(surface, (240, 240, 245), ep, er)
            # Iris (dark)
            pygame.draw.circle(surface, (30, 30, 40), ep, max(1, int(er*0.55)))
            # Pupil glint
            pg_pos = (ep[0] + max(1, int(er*0.2)), ep[1] - max(1, int(er*0.2)))
            pygame.draw.circle(surface, (255, 255, 255), pg_pos, max(1, int(er*0.2)))

    # Windshield glare
    glare_pts = [r(-int(WI_W*0.5), int(CH*0.68)),
                 r(-int(WI_W*0.1), int(CH*0.68)),
                 r(-int(WI_W*0.15), int(CH*0.82)),
                 r(-int(WI_W*0.55), int(CH*0.82))]
    pygame.draw.polygon(surface, (220, 240, 255, 100), glare_pts)

    # ── Rear window ──────────────────────────────────────────────────────────
    rw_pts = [r(-int(CW*0.72), int(CH*0.08)), r( int(CW*0.72), int(CH*0.08)),
              r( int(CW*0.76), int(CH*0.32)), r(-int(CW*0.76), int(CH*0.32))]
    pygame.draw.polygon(surface, des["win"], rw_pts)

    # ── Headlights ───────────────────────────────────────────────────────────
    for hx in [-int(W*0.52), int(W*0.52)]:
        hp = r(hx, int(HL*0.9))
        pygame.draw.circle(surface, (255, 250, 200), hp, max(2, int(4*scale)))
        pygame.draw.circle(surface, (255, 255, 255), hp, max(1, int(2*scale)))
        pygame.draw.circle(surface, (200, 200, 200), hp, max(2, int(4*scale)), 1)

    # ── Tail lights (McQueen-style round) ────────────────────────────────────
    for tx in [-int(W*0.6), int(W*0.6)]:
        tp = r(tx, -int(HL*0.4))
        pygame.draw.circle(surface, (200, 20, 10), tp, max(2, int(3*scale)))
        pygame.draw.circle(surface, (255, 80, 60), tp, max(1, int(1.5*scale)))

    # ── Body outline ─────────────────────────────────────────────────────────
    pygame.draw.polygon(surface, _shade_color(des["body_lo"], 0.6), body_pts, max(1, int(scale)))

    # ── Player ring (Piston Cup style) ───────────────────────────────────────
    if is_human:
        pygame.draw.circle(surface, (255, 190, 0), (int(cx), int(cy)),
                           int(HL + 5*scale), 2)
        pygame.draw.circle(surface, (255, 220, 80), (int(cx), int(cy)),
                           int(HL + 7*scale), 1)


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
