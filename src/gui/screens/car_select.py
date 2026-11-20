"""src/gui/screens/car_select.py — Classic Muscle Car Garage / Selection Screen.

Left carousel navigation, large center showcase, right stat bars.
Works with 8 legendary classic cars.
"""

from typing import Callable, Dict, List
import math
import pygame
from src.gui.components.button import Button, ArrowButton
from src.gui.components.car_renderer import draw_garage_car, draw_car_at, CAR_DESIGNS
from src.gui.assets.colors import BG_DARK, PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_ACCENT, TEXT_GOLD, TEXT_MUTED
from src.gui.assets.fonts import get_font, get_ui_font

CAR_STAT_DATA = [
    {"speed":85,"accel":78,"handling":80,"nitro":72,"weight":"1050 kg","engine":"4.7L V8","power":"485 hp","drive":"RWD"},
    {"speed":82,"accel":80,"handling":76,"nitro":74,"weight":"1320 kg","engine":"7.0L V8","power":"355 hp","drive":"RWD"},
    {"speed":88,"accel":85,"handling":70,"nitro":90,"weight":"1670 kg","engine":"7.0L V8","power":"425 hp","drive":"RWD"},
    {"speed":84,"accel":76,"handling":88,"nitro":68,"weight":"880 kg", "engine":"3.0L V12","power":"302 hp","drive":"RWD"},
    {"speed":86,"accel":88,"handling":72,"nitro":85,"weight":"1590 kg","engine":"6.6L V8","power":"370 hp","drive":"RWD"},
    {"speed":83,"accel":87,"handling":74,"nitro":82,"weight":"1510 kg","engine":"5.0L V8","power":"360 hp","drive":"RWD"},
    {"speed":90,"accel":92,"handling":78,"nitro":70,"weight":"1050 kg","engine":"7.0L V8","power":"485 hp","drive":"RWD"},
    {"speed":80,"accel":74,"handling":90,"nitro":65,"weight":"1310 kg","engine":"3.8L I6", "power":"265 hp","drive":"RWD"},
]

NUM_CARS = len(CAR_DESIGNS)


class CarSelectScreen:
    """Car selection screen featuring 8 legendary classic muscle cars."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.selected_car  = 0
        self.circuit_idx   = 0
        self.laps          = 2
        self.time          = 0.0

        self._btn_left  = ArrowButton((42, 318, 52, 52), direction="left", callback=self._prev)
        self._btn_right = ArrowButton((1186, 318, 52, 52), direction="right", callback=self._next)
        self._race_btn  = Button((490, 648, 300, 48), "SELECT & RACE  ▶",
                                 callback=self._go_race, font_size=18, bold=True,
                                 accent_color=(0, 220, 80))
        self._back_btn  = Button((20, 20, 110, 36), "← BACK",
                                 callback=lambda: self.switch_screen("circuit_select", {}),
                                 font_size=14)

        # Thumbnail rects
        self._thumb_rects: List[pygame.Rect] = []
        tw, gap = 120, 10
        x0 = (1280 - NUM_CARS*(tw+gap) + gap) // 2
        for i in range(NUM_CARS):
            self._thumb_rects.append(pygame.Rect(x0 + i*(tw+gap), 592, tw, 44))

    def set_context(self, ctx: Dict) -> None:
        self.circuit_idx  = ctx.get("circuit_idx", 0)
        self.laps         = ctx.get("laps", 2)
        self.selected_car = ctx.get("car_idx", 0)

    def _prev(self): self.selected_car = (self.selected_car - 1) % NUM_CARS
    def _next(self): self.selected_car = (self.selected_car + 1) % NUM_CARS

    def _go_race(self):
        self.switch_screen("racing", {
            "circuit_idx": self.circuit_idx,
            "laps":        self.laps,
            "car_idx":     self.selected_car,
        })

    def handle_event(self, event: pygame.event.Event) -> None:
        self._btn_left.handle_event(event)
        self._btn_right.handle_event(event)
        self._race_btn.handle_event(event)
        self._back_btn.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._thumb_rects):
                if r.collidepoint(event.pos):
                    self.selected_car = i
                    break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  self._prev()
            if event.key == pygame.K_RIGHT: self._next()

    def update(self, dt: float) -> None:
        self.time += dt
        for b in [self._btn_left, self._btn_right, self._race_btn, self._back_btn]:
            b.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        W, H = surface.get_size()
        car    = CAR_DESIGNS[self.selected_car]
        stats  = CAR_STAT_DATA[self.selected_car]
        accent = car["body_hi"]

        self._draw_bg(surface, W, H, car)

        # Header
        hdr = get_font(size=34, bold=True).render("SELECT YOUR MACHINE", True, TEXT_WHITE)
        surface.blit(hdr, hdr.get_rect(center=(W//2, 44)))
        pygame.draw.line(surface, accent, (W//2-240, 64), (W//2+240, 64), 2)

        # Left specs panel
        self._draw_left(surface, car, stats, accent)

        # Center showcase
        self._draw_showcase(surface, W, H, car, accent)

        # Right stats panel
        self._draw_right(surface, stats, accent, W)

        # Thumbnails
        self._draw_thumbs(surface)

        # Buttons
        for b in [self._btn_left, self._btn_right, self._race_btn, self._back_btn]:
            b.draw(surface)

    def _draw_bg(self, surface: pygame.Surface, W: int, H: int, car: dict) -> None:
        surface.fill((6, 8, 14))
        ac = car["body"]
        glow = pygame.Surface((760, 760), pygame.SRCALPHA)
        for r in range(360, 0, -6):
            a = int(20*(1-r/360))
            pygame.draw.circle(glow, (*ac, a), (380, 380), r)
        surface.blit(glow, (W//2-380, H//2-400))
        pygame.draw.rect(surface, (10, 12, 20), (0, H-170, W, 170))
        pygame.draw.line(surface, (0, 180, 255), (0, H-170), (W, H-170), 1)
        # Side panels
        for px, pw in [(108, 310), (862, 310)]:
            ps = pygame.Surface((pw, 490), pygame.SRCALPHA)
            pygame.draw.rect(ps, (10, 13, 24, 215), ps.get_rect(), border_radius=14)
            surface.blit(ps, (px, 80))
            pygame.draw.rect(surface, car["body"], (px, 80, pw, 4), border_radius=14)

    def _draw_showcase(self, surface: pygame.Surface, W: int, H: int, car: dict, accent: tuple) -> None:
        cx, cy = W//2, H//2 - 20
        sh = pygame.Surface((300, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 100), sh.get_rect())
        surface.blit(sh, (cx-150, cy+100))

        ref = pygame.Surface((280, 50), pygame.SRCALPHA)
        for ry in range(50):
            a = max(0, 50 - ry*5)
            pygame.draw.ellipse(ref, (*accent, a), (0, ry, 280, 50-ry))
        surface.blit(ref, (cx-140, cy+100))

        angle = math.pi/2 + math.sin(self.time*0.4)*0.07
        draw_car_at(surface, cx, cy, self.selected_car,
                    angle=angle, scale=4.0, nitro_active=False, is_human=False, show_shadow=False)

        nm = get_font(size=42, bold=True).render(car["name"], True, TEXT_WHITE)
        for off in [(2,2),(1,1)]:
            shadow = get_font(size=42, bold=True).render(car["name"], True, (*accent,))
            surface.blit(shadow, shadow.get_rect(center=(W//2+off[0], cy+152+off[1])))
        surface.blit(nm, nm.get_rect(center=(W//2, cy+152)))

        sub_txt = get_ui_font(size=15, bold=True).render(
            f"{car['year']}  ·  {car['class']}", True, (*accent,))
        surface.blit(sub_txt, sub_txt.get_rect(center=(W//2, cy+184)))

    def _draw_left(self, surface, car, stats, accent):
        x, y = 122, 94
        f_hdr = get_ui_font(size=12, bold=True)
        f_val = get_ui_font(size=14, bold=True)
        rows  = [("ENGINE", stats["engine"]), ("POWER", stats["power"]),
                 ("WEIGHT", stats["weight"]), ("DRIVE", stats["drive"])]
        yy = y + 14
        for lbl, val in rows:
            surface.blit(f_hdr.render(lbl, True, TEXT_MUTED), (x+12, yy))
            surface.blit(f_val.render(val, True, TEXT_WHITE), (x+12, yy+16))
            yy += 56
        # Class badge
        tier_map = {"GT":"GT","Pony Car":"PC","Muscle":"V8","Roadster":"RS"}
        tier = tier_map.get(car["class"], "GT")
        pygame.draw.rect(surface, car["body"], (x+252, y+14, 44, 44), border_radius=8)
        surface.blit(get_font(size=20,bold=True).render(tier,True,(255,255,255)),
                     pygame.Rect(x+252,y+14,44,44).move(0,0).move(44//2-10,44//2-14).move(0,0))

    def _draw_right(self, surface, stats, accent, W):
        x, y = 876, 94
        surface.blit(get_ui_font(size=13,bold=True).render("PERFORMANCE", True, TEXT_ACCENT), (x+12, y+12))
        pygame.draw.line(surface, (38,46,68), (x+12, y+30), (x+275, y+30), 1)
        stat_defs = [
            ("SPEED",        stats["speed"],    (0,  200, 255)),
            ("ACCELERATION", stats["accel"],    (255,160,   0)),
            ("HANDLING",     stats["handling"], (50, 220, 100)),
            ("NITRO",        stats["nitro"],    (200, 60, 255)),
        ]
        for i, (name, val, col) in enumerate(stat_defs):
            yy = y + 46 + i*68
            surface.blit(get_ui_font(size=12).render(name, True, TEXT_MUTED), (x+12, yy))
            bar_max = 240
            fill_w  = int(bar_max * val / 100)
            pygame.draw.rect(surface, (28,32,48), (x+12, yy+20, bar_max, 18), border_radius=9)
            if fill_w > 0:
                pygame.draw.rect(surface, col, (x+12, yy+20, fill_w, 18), border_radius=9)
            surface.blit(get_ui_font(size=11,bold=True).render(str(val), True, col),
                         (x+12+bar_max+8, yy+20))

    def _draw_thumbs(self, surface):
        for i, r in enumerate(self._thumb_rects):
            car   = CAR_DESIGNS[i]
            is_sel = (i == self.selected_car)
            bg = pygame.Surface(r.size, pygame.SRCALPHA)
            pygame.draw.rect(bg, (20,25,40,220) if is_sel else (12,15,24,180), bg.get_rect(), border_radius=8)
            surface.blit(bg, r.topleft)
            bc = car["body"] if is_sel else (38,46,68)
            pygame.draw.rect(surface, bc, r, width=1, border_radius=8)
            draw_car_at(surface, r.centerx, r.centery, i,
                        angle=math.pi/2, scale=0.9, nitro_active=False,
                        is_human=False, show_shadow=False)
