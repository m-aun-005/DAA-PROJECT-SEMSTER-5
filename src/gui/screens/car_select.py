"""src/gui/screens/car_select.py — Asphalt 8-style Car Garage / Selection Screen.

Left carousel navigation, large center car showcase, right stat bars.
"""

from typing import Callable, Dict, List, Tuple
import math
import pygame
from src.gui.components.button import Button
from src.gui.components.car_renderer import draw_garage_car, CAR_DESIGNS
from src.gui.assets.colors import BG_DARK, PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_ACCENT, TEXT_GOLD, TEXT_MUTED
from src.gui.assets.fonts import get_font, get_ui_font


# ─── Car catalogue ────────────────────────────────────────────────────────────
_CARS = [
    {
        "name":        "APEX VIPER",
        "class":       "Class S — Hypercar",
        "desc":        "Raw power and precision handling.\nBuilt for championship circuits.",
        "speed":       88,
        "accel":       76,
        "handling":    82,
        "nitro":       70,
        "top_speed":   "340 km/h",
        "weight":      "1 180 kg",
        "drive":       "RWD",
        "accent":      (220,  40,  40),
        "tier":        "S",
    },
    {
        "name":        "STORM GT",
        "class":       "Class A — Grand Tourer",
        "desc":        "Blazing straight-line speed with\naggressive aerodynamics.",
        "speed":       95,
        "accel":       68,
        "handling":    58,
        "nitro":       80,
        "top_speed":   "368 km/h",
        "weight":      "1 320 kg",
        "drive":       "AWD",
        "accent":      (40,  110, 240),
        "tier":        "A",
    },
    {
        "name":        "SHADOW X",
        "class":       "Class A — Muscle Car",
        "desc":        "Massive nitro reserves and\nbone-crushing acceleration.",
        "speed":       80,
        "accel":       90,
        "handling":    64,
        "nitro":       96,
        "top_speed":   "310 km/h",
        "weight":      "1 540 kg",
        "drive":       "RWD",
        "accent":      (230, 160,  10),
        "tier":        "A",
    },
    {
        "name":        "PHANTOM RS",
        "class":       "Class B — Endurance",
        "desc":        "Superior handling and fuel range.\nMaster of technical circuits.",
        "speed":       74,
        "accel":       72,
        "handling":    95,
        "nitro":       68,
        "top_speed":   "295 km/h",
        "weight":      "1 100 kg",
        "drive":       "FWD",
        "accent":      (40,  200, 110),
        "tier":        "B",
    },
]


class CarSelectScreen:
    """Asphalt 8-style car selection / garage screen."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen  = switch_screen
        self.selected_car   = 0
        self.circuit_idx    = 0
        self.laps           = 2
        self.time           = 0.0
        self._showcase_angle = 0.0   # slow rotation of showcase car

        # Arrow buttons
        self._btn_left  = Button((54, 320, 54, 54), "◀", callback=self._prev_car,
                                 font_size=22, bold=True, accent_color=(0,180,255))
        self._btn_right = Button((1172, 320, 54, 54), "▶", callback=self._next_car,
                                 font_size=22, bold=True, accent_color=(0,180,255))

        # Race button
        self._race_btn = Button((490, 646, 300, 50), "SELECT & RACE  ▶",
                                callback=self._go_race, font_size=18, bold=True,
                                accent_color=(0, 220, 80))

        # Back button
        self._back_btn = Button((20, 20, 110, 36), "← BACK",
                                callback=lambda: self.switch_screen("circuit_select", {}),
                                font_size=14)

        # Car thumbnail buttons (bottom strip)
        self._thumb_btns: List[Button] = []
        thumb_w, gap = 120, 20
        x0 = (1280 - 4*(thumb_w+gap) + gap) // 2
        for i in range(4):
            x = x0 + i*(thumb_w+gap)
            self._thumb_btns.append(
                Button((x, 590, thumb_w, 44), _CARS[i]["name"][:10],
                       callback=lambda idx=i: self._select_car(idx),
                       font_size=12, bold=True,
                       accent_color=_CARS[i]["accent"])
            )
        self._update_thumb_active()

    def set_context(self, context: Dict) -> None:
        self.circuit_idx = context.get("circuit_idx", 0)
        self.laps        = context.get("laps", 2)
        car_idx          = context.get("car_idx", 0)
        self.selected_car = car_idx

    def _prev_car(self):
        self._select_car((self.selected_car - 1) % 4)

    def _next_car(self):
        self._select_car((self.selected_car + 1) % 4)

    def _select_car(self, idx: int):
        self.selected_car = idx
        self._update_thumb_active()

    def _update_thumb_active(self):
        for i, b in enumerate(self._thumb_btns):
            b.is_active = (i == self.selected_car)

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
        for btn in self._thumb_btns:
            btn.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._prev_car()
            elif event.key == pygame.K_RIGHT:
                self._next_car()

    def update(self, dt: float) -> None:
        self.time += dt
        self._showcase_angle += dt * 0.6   # slow rotation
        self._btn_left.update(dt)
        self._btn_right.update(dt)
        self._race_btn.update(dt)
        self._back_btn.update(dt)
        for btn in self._thumb_btns:
            btn.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        W, H = surface.get_size()
        surface.fill((6, 8, 14))
        self._draw_bg(surface, W, H)

        car_data = _CARS[self.selected_car]
        accent   = car_data["accent"]

        # Header
        hdr_font = get_font(size=34, bold=True)
        hdr = hdr_font.render("GARAGE", True, TEXT_WHITE)
        surface.blit(hdr, hdr.get_rect(center=(W//2, 46)))
        pygame.draw.line(surface, accent, (W//2-200, 66), (W//2+200, 66), 2)

        # ── LEFT: Car info panel ────────────────────────────────────────────
        self._draw_left_panel(surface, car_data, accent)

        # ── CENTER: Car showcase ────────────────────────────────────────────
        self._draw_showcase(surface, W, H, accent)

        # ── RIGHT: Stat bars panel ──────────────────────────────────────────
        self._draw_right_panel(surface, car_data, accent, W)

        # ── Arrow nav buttons ───────────────────────────────────────────────
        self._btn_left.draw(surface)
        self._btn_right.draw(surface)

        # ── Thumbnail strip ─────────────────────────────────────────────────
        self._draw_thumb_strip(surface, W)
        for btn in self._thumb_btns:
            btn.draw(surface)

        # ── Race button ─────────────────────────────────────────────────────
        self._race_btn.draw(surface)
        self._back_btn.draw(surface)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _draw_bg(self, surface: pygame.Surface, W: int, H: int):
        # Radial spotlight on center
        car_data = _CARS[self.selected_car]
        accent   = car_data["accent"]
        glow = pygame.Surface((700, 700), pygame.SRCALPHA)
        for r in range(340, 0, -4):
            alpha = int(28 * (1 - r/340))
            pygame.draw.circle(glow, (*accent, alpha), (350, 350), r)
        surface.blit(glow, (W//2 - 350, H//2 - 350 + 20))

        # Ground reflection strip
        pygame.draw.rect(surface, (10, 12, 20), (0, H - 160, W, 160))
        pygame.draw.line(surface, (*accent, 80), (0, H-160), (W, H-160), 1)

        # Side panel BGs
        left_surf = pygame.Surface((340, 500), pygame.SRCALPHA)
        pygame.draw.rect(left_surf, (10, 13, 24, 210), left_surf.get_rect(), border_radius=14)
        surface.blit(left_surf, (110, 90))

        right_surf = pygame.Surface((300, 500), pygame.SRCALPHA)
        pygame.draw.rect(right_surf, (10, 13, 24, 210), right_surf.get_rect(), border_radius=14)
        surface.blit(right_surf, (870, 90))

        pygame.draw.rect(surface, car_data["accent"],
                         pygame.Rect(110, 90, 340, 4), border_radius=14)
        pygame.draw.rect(surface, car_data["accent"],
                         pygame.Rect(870, 90, 300, 4), border_radius=14)

    def _draw_showcase(self, surface: pygame.Surface, W: int, H: int, accent):
        cx, cy = W//2, H//2 - 10
        # Reflection
        refl = pygame.Surface((300, 60), pygame.SRCALPHA)
        for ry in range(60):
            alpha = max(0, 60 - ry * 5)
            pygame.draw.ellipse(refl, (*accent, alpha), (0, ry, 300, 60-ry))
        surface.blit(refl, (cx - 150, cy + 100))

        # Ground shadow ellipse
        shadow_surf = pygame.Surface((260, 50), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 120), shadow_surf.get_rect())
        surface.blit(shadow_surf, (cx - 130, cy + 85))

        # Oscillate angle slightly for living feel
        angle = math.pi/2 + math.sin(self.time * 0.4) * 0.08
        draw_garage_car(surface, cx, cy, self.selected_car, scale=4.0)

        # Car name big
        name_font = get_font(size=46, bold=True)
        name_txt  = name_font.render(_CARS[self.selected_car]["name"], True, TEXT_WHITE)
        # Glow
        for off in [(2,2),(1,1)]:
            shadow_txt = name_font.render(_CARS[self.selected_car]["name"], True, accent)
            surface.blit(shadow_txt, shadow_txt.get_rect(center=(W//2+off[0], cy + 140+off[1])))
        surface.blit(name_txt, name_txt.get_rect(center=(W//2, cy + 140)))

        # Class label
        class_font = get_ui_font(size=15)
        class_txt  = class_font.render(_CARS[self.selected_car]["class"], True, (*accent,))
        surface.blit(class_txt, class_txt.get_rect(center=(W//2, cy + 174)))

    def _draw_left_panel(self, surface: pygame.Surface, car_data: Dict, accent: Tuple):
        x, y = 124, 108
        font_hdr = get_ui_font(size=12, bold=True)
        font_val = get_ui_font(size=14, bold=True)
        font_lbl = get_ui_font(size=12)

        # Description
        for li, line in enumerate(car_data["desc"].split("\n")):
            lt = get_ui_font(size=13).render(line, True, TEXT_MUTED)
            surface.blit(lt, (x + 12, y + 16 + li * 20))

        # Specs table
        specs = [
            ("TOP SPEED",  car_data["top_speed"]),
            ("WEIGHT",     car_data["weight"]),
            ("DRIVETRAIN", car_data["drive"]),
            ("CLASS",      car_data["tier"]),
        ]
        y_off = y + 68
        for lbl, val in specs:
            lbl_txt = font_hdr.render(lbl, True, TEXT_MUTED)
            val_txt = font_val.render(val, True, TEXT_WHITE)
            surface.blit(lbl_txt, (x + 12, y_off))
            surface.blit(val_txt, (x + 12, y_off + 16))
            y_off += 56

        # Tier badge
        tier = car_data["tier"]
        badge_x, badge_y = x + 270, y + 16
        pygame.draw.rect(surface, accent, (badge_x, badge_y, 40, 40), border_radius=8)
        tier_txt = get_font(size=24, bold=True).render(tier, True, (10,10,10))
        surface.blit(tier_txt, tier_txt.get_rect(center=(badge_x+20, badge_y+20)))

    def _draw_right_panel(self, surface: pygame.Surface, car_data: Dict, accent: Tuple, W: int):
        x, y = 884, 108
        font_hdr = get_ui_font(size=13, bold=True)
        font_lbl = get_ui_font(size=12)

        hdr_txt = font_hdr.render("PERFORMANCE STATS", True, TEXT_ACCENT)
        surface.blit(hdr_txt, (x + 12, y + 12))
        pygame.draw.line(surface, (38,46,68), (x+12, y+30), (x+275, y+30), 1)

        stat_names = ["SPEED", "ACCELERATION", "HANDLING", "NITRO"]
        stat_vals  = [car_data["speed"], car_data["accel"],
                      car_data["handling"], car_data["nitro"]]
        stat_cols  = [
            (0, 200, 255),
            (255, 180, 0),
            (50, 220, 100),
            (200, 60, 255),
        ]

        bar_max_w = 240
        for i, (name, val, col) in enumerate(zip(stat_names, stat_vals, stat_cols)):
            yy = y + 46 + i * 68
            lbl = font_lbl.render(name, True, TEXT_MUTED)
            surface.blit(lbl, (x + 12, yy))

            # Animated fill (ease-in from 0)
            fill_pct = min(1.0, val / 100.0)
            fill_w   = int(bar_max_w * fill_pct)

            # Track
            pygame.draw.rect(surface, (28, 32, 48), (x+12, yy+20, bar_max_w, 18), border_radius=9)
            # Fill
            if fill_w > 0:
                pygame.draw.rect(surface, col, (x+12, yy+20, fill_w, 18), border_radius=9)
                # Shimmer highlight
                pygame.draw.rect(surface, (255,255,255,60),
                                 (x+12, yy+20, fill_w, 7), border_radius=9)

            # Value label
            val_txt = get_ui_font(size=11, bold=True).render(str(val), True, col)
            surface.blit(val_txt, (x + 12 + bar_max_w + 8, yy + 20))

    def _draw_thumb_strip(self, surface: pygame.Surface, W: int):
        """Draw the 4 car thumbnail previews above the select buttons."""
        thumb_w, gap = 120, 20
        x0 = (W - 4*(thumb_w+gap) + gap) // 2
        for i in range(4):
            x = x0 + i*(thumb_w+gap)
            # Small car preview
            thumb = pygame.Surface((thumb_w, 44), pygame.SRCALPHA)
            is_sel = (i == self.selected_car)
            bg_col = (20, 25, 40, 220) if is_sel else (12, 15, 24, 180)
            pygame.draw.rect(thumb, bg_col, thumb.get_rect(), border_radius=8)
            border_col = _CARS[i]["accent"] if is_sel else (38,46,68)
            pygame.draw.rect(thumb, border_col, thumb.get_rect(), width=1, border_radius=8)
            surface.blit(thumb, (x, 590))
            # Draw tiny car
            draw_garage_car(surface, x + thumb_w//2, 612, i, scale=1.3)
