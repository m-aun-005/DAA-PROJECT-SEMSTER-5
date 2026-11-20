"""src/gui/screens/garage.py — Classic Muscle Car Garage Screen.

Shows all 8 legendary cars with 2D pseudo-3D look, stats, and specs.
"""

from typing import Callable, Dict, List
import math
import pygame
from src.gui.components.car_renderer import draw_garage_car, CAR_DESIGNS
from src.gui.assets.colors import BG_DARK, PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_ACCENT, TEXT_GOLD, TEXT_MUTED
from src.gui.assets.fonts import get_font, get_ui_font
from src.gui.components.button import Button, ArrowButton

CAR_STATS = [
    {"speed":85,"accel":78,"handling":80,"nitro":72,"weight":"1050 kg","engine":"4.7L V8","power":"485 hp","drive":"RWD"},
    {"speed":82,"accel":80,"handling":76,"nitro":74,"weight":"1320 kg","engine":"7.0L V8","power":"355 hp","drive":"RWD"},
    {"speed":88,"accel":85,"handling":70,"nitro":90,"weight":"1670 kg","engine":"7.0L V8","power":"425 hp","drive":"RWD"},
    {"speed":84,"accel":76,"handling":88,"nitro":68,"weight":"880 kg", "engine":"3.0L V12","power":"302 hp","drive":"RWD"},
    {"speed":86,"accel":88,"handling":72,"nitro":85,"weight":"1590 kg","engine":"6.6L V8","power":"370 hp","drive":"RWD"},
    {"speed":83,"accel":87,"handling":74,"nitro":82,"weight":"1510 kg","engine":"5.0L V8","power":"360 hp","drive":"RWD"},
    {"speed":90,"accel":92,"handling":78,"nitro":70,"weight":"1050 kg","engine":"7.0L V8","power":"485 hp","drive":"RWD"},
    {"speed":80,"accel":74,"handling":90,"nitro":65,"weight":"1310 kg","engine":"3.8L I6", "power":"265 hp","drive":"RWD"},
]


class GarageScreen:
    """Classic car garage with 2D pseudo-3D car showcase."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.selected      = 0
        self.time          = 0.0
        self._rotation     = 0.0

        self._btn_back  = Button((20, 20, 110, 36), "← BACK",
                                 callback=lambda: self.switch_screen("main_menu", {}), font_size=14)
        self._btn_prev  = ArrowButton((42, 330, 50, 50), direction="left", callback=self._prev)
        self._btn_next  = ArrowButton((1188, 330, 50, 50), direction="right", callback=self._next)
        self._btn_race  = Button((490, 660, 300, 46), "RACE THIS CAR  ▶",
                                 callback=self._race, font_size=18, bold=True, accent_color=(0,220,80))

        # Thumbnail rects
        self._thumb_rects: List[pygame.Rect] = []
        tw, gap = 120, 14
        x0 = (1280 - 8*(tw+gap) + gap) // 2
        for i in range(8):
            self._thumb_rects.append(pygame.Rect(x0 + i*(tw+gap), 596, tw, 50))

    def _prev(self): self.selected = (self.selected - 1) % len(CAR_DESIGNS)
    def _next(self): self.selected = (self.selected + 1) % len(CAR_DESIGNS)
    def _race(self): self.switch_screen("circuit_select", {"car_idx": self.selected})

    def set_context(self, ctx: Dict) -> None:
        self.selected = ctx.get("car_idx", 0)

    def handle_event(self, event: pygame.event.Event) -> None:
        self._btn_back.handle_event(event)
        self._btn_prev.handle_event(event)
        self._btn_next.handle_event(event)
        self._btn_race.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._thumb_rects):
                if r.collidepoint(event.pos):
                    self.selected = i
                    break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:  self._prev()
            if event.key == pygame.K_RIGHT: self._next()

    def update(self, dt: float) -> None:
        self.time += dt
        self._rotation += dt * 0.5
        for b in [self._btn_back, self._btn_prev, self._btn_next, self._btn_race]:
            b.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        W, H = surface.get_size()
        self._draw_bg(surface, W, H)
        car = CAR_DESIGNS[self.selected]
        stats = CAR_STATS[self.selected]
        accent = car["body_hi"]

        # Header
        hdr = get_font(size=36, bold=True).render("GARAGE", True, TEXT_WHITE)
        surface.blit(hdr, hdr.get_rect(center=(W//2, 46)))
        sub = get_ui_font(size=13).render("Select your legendary machine", True, TEXT_MUTED)
        surface.blit(sub, sub.get_rect(center=(W//2, 70)))
        pygame.draw.line(surface, accent, (W//2-200, 82), (W//2+200, 82), 2)

        # Left specs panel
        self._draw_specs(surface, car, stats, accent)

        # Center showcase
        self._draw_showcase(surface, W, H, car, accent)

        # Right performance panel
        self._draw_performance(surface, stats, accent, W)

        # Thumbnails
        self._draw_thumbnails(surface)

        # Buttons
        self._btn_back.draw(surface)
        self._btn_prev.draw(surface)
        self._btn_next.draw(surface)
        self._btn_race.draw(surface)

    def _draw_bg(self, surface: pygame.Surface, W: int, H: int) -> None:
        surface.fill((6, 8, 14))
        car = CAR_DESIGNS[self.selected]
        ac  = car["body"]
        # Radial spotlight
        glow = pygame.Surface((800, 800), pygame.SRCALPHA)
        for r in range(380, 0, -6):
            a = int(22 * (1 - r/380))
            pygame.draw.circle(glow, (*ac, a), (400, 400), r)
        surface.blit(glow, (W//2 - 400, H//2 - 420))
        # Garage floor grid
        pygame.draw.rect(surface, (10, 12, 20), (0, H - 170, W, 170))
        pygame.draw.line(surface, (0, 180, 255), (0, H-170), (W, H-170), 1)
        # Side panels
        for panel_x, panel_w in [(108, 300), (872, 300)]:
            ps = pygame.Surface((panel_w, 490), pygame.SRCALPHA)
            pygame.draw.rect(ps, (10, 13, 24, 215), ps.get_rect(), border_radius=14)
            surface.blit(ps, (panel_x, 94))
            pygame.draw.rect(surface, car["body"], (panel_x, 94, panel_w, 4), border_radius=14)

    def _draw_showcase(self, surface: pygame.Surface, W: int, H: int, car: dict, accent: tuple) -> None:
        cx, cy = W//2, H//2 - 30

        # Ground shadow ellipse
        sh = pygame.Surface((300, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 100), sh.get_rect())
        surface.blit(sh, (cx - 150, cy + 100))

        # Reflection streak
        ref = pygame.Surface((280, 50), pygame.SRCALPHA)
        for ry in range(50):
            a = max(0, 50 - ry * 5)
            pygame.draw.ellipse(ref, (*accent, a), (0, ry, 280, 50-ry))
        surface.blit(ref, (cx-140, cy+100))

        # Draw big showcase car (facing north, slightly angled for 3D feel)
        angle = math.pi/2 + math.sin(self.time * 0.3) * 0.06
        from src.gui.components.car_renderer import draw_car_at
        draw_car_at(surface, cx, cy, self.selected,
                    angle=angle, scale=4.2, nitro_active=False, is_human=False, show_shadow=False)

        # Car name
        nm = get_font(size=44, bold=True).render(car["name"], True, TEXT_WHITE)
        for off in [(2,2),(1,1)]:
            sh_nm = get_font(size=44, bold=True).render(car["name"], True, (*accent,))
            surface.blit(sh_nm, sh_nm.get_rect(center=(W//2+off[0], cy+152+off[1])))
        surface.blit(nm, nm.get_rect(center=(W//2, cy+152)))

        yr = get_ui_font(size=16, bold=True).render(car["year"] + "  —  " + car["class"], True, (*accent,))
        surface.blit(yr, yr.get_rect(center=(W//2, cy+184)))

    def _draw_specs(self, surface: pygame.Surface, car: dict, stats: dict, accent: tuple) -> None:
        x, y = 122, 108
        f_hdr = get_ui_font(size=12, bold=True)
        f_val = get_ui_font(size=14, bold=True)

        rows = [
            ("ENGINE",   stats["engine"]),
            ("POWER",    stats["power"]),
            ("WEIGHT",   stats["weight"]),
            ("DRIVE",    stats["drive"]),
        ]
        yy = y + 14
        for lbl, val in rows:
            surface.blit(f_hdr.render(lbl, True, TEXT_MUTED), (x + 12, yy))
            surface.blit(f_val.render(val, True, TEXT_WHITE), (x + 12, yy + 16))
            yy += 56

        # Tier badge
        tier_map = {"GT":"GT","Pony Car":"PC","Muscle":"V8","Roadster":"RS"}
        tier = tier_map.get(car["class"], "GT")
        badge_x, badge_y = x + 250, y + 14
        pygame.draw.rect(surface, car["body"], (badge_x, badge_y, 44, 44), border_radius=8)
        t_txt = get_font(size=20, bold=True).render(tier, True, (255,255,255))
        surface.blit(t_txt, t_txt.get_rect(center=(badge_x+22, badge_y+22)))

    def _draw_performance(self, surface: pygame.Surface, stats: dict, accent: tuple, W: int) -> None:
        x, y = 886, 108
        hdr = get_ui_font(size=13, bold=True).render("PERFORMANCE", True, TEXT_ACCENT)
        surface.blit(hdr, (x+12, y+12))
        pygame.draw.line(surface, (38,46,68), (x+12, y+30), (x+275, y+30), 1)

        stat_defs = [
            ("SPEED",        stats["speed"],    (0,  200, 255)),
            ("ACCELERATION", stats["accel"],    (255,160,   0)),
            ("HANDLING",     stats["handling"], (50, 220, 100)),
            ("NITRO",        stats["nitro"],    (200, 60, 255)),
        ]
        for i, (name, val, col) in enumerate(stat_defs):
            yy = y + 46 + i * 68
            surface.blit(get_ui_font(size=12).render(name, True, TEXT_MUTED), (x+12, yy))
            bar_max = 240
            fill_w  = int(bar_max * val / 100)
            pygame.draw.rect(surface, (28,32,48), (x+12, yy+20, bar_max, 18), border_radius=9)
            if fill_w > 0:
                pygame.draw.rect(surface, col, (x+12, yy+20, fill_w, 18), border_radius=9)
                pygame.draw.rect(surface, (255,255,255,50), (x+12, yy+20, fill_w, 7), border_radius=9)
            surface.blit(get_ui_font(size=11,bold=True).render(str(val), True, col),
                         (x+12+bar_max+8, yy+20))

    def _draw_thumbnails(self, surface: pygame.Surface) -> None:
        for i, r in enumerate(self._thumb_rects):
            car   = CAR_DESIGNS[i]
            is_sel = (i == self.selected)
            bg    = pygame.Surface(r.size, pygame.SRCALPHA)
            pygame.draw.rect(bg, (20,25,40,220) if is_sel else (12,15,24,180), bg.get_rect(), border_radius=8)
            surface.blit(bg, r.topleft)
            bc = car["body"] if is_sel else (38,46,68)
            pygame.draw.rect(surface, bc, r, width=1, border_radius=8)
            # Mini car
            from src.gui.components.car_renderer import draw_car_at
            draw_car_at(surface, r.centerx, r.centery, i, angle=math.pi/2, scale=1.1,
                        nitro_active=False, is_human=False, show_shadow=False)
