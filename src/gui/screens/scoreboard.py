"""src/gui/screens/scoreboard.py — Global Scoreboard Screen.

Tracks race wins, podiums, and championship points across all sessions.
Data persists in a simple JSON file on disk.
"""

from typing import Callable, Dict, List
import json
import os
import math
import pygame
from src.gui.assets.colors import BG_DARK, PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_ACCENT, TEXT_GOLD, TEXT_MUTED
from src.gui.assets.fonts import get_font, get_ui_font
from src.gui.components.button import Button
from src.gui.components.car_renderer import CAR_DESIGNS

_SAVE_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "scoreboard.json"
)

_DEFAULT_SCORES: List[Dict] = [
    {"rank":1,"name":"El Maestro","car":"Ford GT40 Mk.II",    "pts":248,"wins":7,"races":12,"best_lap":"1:34.2"},
    {"rank":2,"name":"Chrome King","car":"Ferrari 250 GTO",   "pts":196,"wins":5,"races":12,"best_lap":"1:36.1"},
    {"rank":3,"name":"Iron Hawk",  "car":"Shelby GT500",      "pts":172,"wins":4,"races":10,"best_lap":"1:37.8"},
    {"rank":4,"name":"Venom",      "car":"Dodge Charger R/T", "pts":141,"wins":3,"races":11,"best_lap":"1:38.5"},
    {"rank":5,"name":"Ghost Rider","car":"Pontiac GTO",       "pts":118,"wins":2,"races":10,"best_lap":"1:39.9"},
    {"rank":6,"name":"The Judge",  "car":"Chevy Camaro Z28",  "pts":96, "wins":2,"races":9, "best_lap":"1:41.2"},
    {"rank":7,"name":"Sidewinder", "car":"AC Cobra 427",      "pts":74, "wins":1,"races":8, "best_lap":"1:42.7"},
    {"rank":8,"name":"Silver Fox", "car":"Jaguar E-Type",     "pts":52, "wins":0,"races":7, "best_lap":"1:44.1"},
    {"rank":9,"name":"YOU",        "car":"—",                 "pts":0,  "wins":0,"races":0, "best_lap":"—"},
]


def _load_scores() -> List[Dict]:
    path = os.path.normpath(_SAVE_FILE)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return [dict(e) for e in _DEFAULT_SCORES]


def save_race_result(player_pts: int, wins: int, best_lap: str, car_name: str) -> None:
    """Update 'YOU' row and re-rank. Called from racing/dashboard."""
    scores = _load_scores()
    for row in scores:
        if row["name"] == "YOU":
            row["pts"]      += player_pts
            row["wins"]     += wins
            row["races"]    += 1
            row["car"]       = car_name
            if best_lap != "—" and (row["best_lap"] == "—" or best_lap < row["best_lap"]):
                row["best_lap"] = best_lap
            break
    # Re-rank by points
    scores.sort(key=lambda x: -x["pts"])
    for i, row in enumerate(scores):
        row["rank"] = i + 1
    path = os.path.normpath(_SAVE_FILE)
    try:
        with open(path, "w") as f:
            json.dump(scores, f, indent=2)
    except Exception:
        pass


class ScoreboardScreen:
    """Global leaderboard screen."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.time          = 0.0
        self._scores       = _load_scores()
        self._btn_back     = Button((20, 20, 110, 36), "← BACK",
                                    callback=lambda: self.switch_screen("main_menu", {}), font_size=14)
        self._btn_reset    = Button((1140, 20, 120, 36), "RESET DATA",
                                    callback=self._reset, font_size=13, accent_color=(255,60,60))

    def _reset(self) -> None:
        self._scores = [dict(e) for e in _DEFAULT_SCORES]
        path = os.path.normpath(_SAVE_FILE)
        try:
            os.remove(path)
        except Exception:
            pass

    def set_context(self, ctx: Dict) -> None:
        self._scores = _load_scores()

    def handle_event(self, event: pygame.event.Event) -> None:
        self._btn_back.handle_event(event)
        self._btn_reset.handle_event(event)

    def update(self, dt: float) -> None:
        self.time += dt
        self._btn_back.update(dt)
        self._btn_reset.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        W, H = surface.get_size()
        self._draw_bg(surface, W, H)

        # Header
        hdr = get_font(size=38, bold=True).render("GLOBAL SCOREBOARD", True, TEXT_WHITE)
        surface.blit(hdr, hdr.get_rect(center=(W//2, 54)))
        sub = get_ui_font(size=13).render("All-time championship rankings", True, TEXT_MUTED)
        surface.blit(sub, sub.get_rect(center=(W//2, 78)))
        pygame.draw.line(surface, TEXT_GOLD, (W//2-260, 90), (W//2+260, 90), 2)

        # Podium
        self._draw_podium(surface, W)

        # Main table
        self._draw_table(surface, W)

        self._btn_back.draw(surface)
        self._btn_reset.draw(surface)

    def _draw_bg(self, surface: pygame.Surface, W: int, H: int) -> None:
        surface.fill(BG_DARK)
        for x in range(-H, W+H, 80):
            ls = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.line(ls, (255, 200, 0, 6), (x, 0), (x-H, H), 1)
            surface.blit(ls, (0, 0))

    def _draw_podium(self, surface: pygame.Surface, W: int) -> None:
        """Draw top-3 large podium blocks."""
        if len(self._scores) < 3:
            return
        podium_data = [
            (self._scores[1], W//2 - 220, 108, 150, 120, (160,170,180)),  # 2nd Silver
            (self._scores[0], W//2 - 90,  94,  180, 134, (220,170,0)),    # 1st Gold
            (self._scores[2], W//2 + 100, 120, 150, 108, (180,110,50)),   # 3rd Bronze
        ]
        for row, bx, by, bw, bh, col in podium_data:
            pygame.draw.rect(surface, col, (bx, by, bw, bh), border_radius=8)
            # Dark overlay for readability
            ov = pygame.Surface((bw, bh), pygame.SRCALPHA)
            pygame.draw.rect(ov, (0,0,0,80), ov.get_rect(), border_radius=8)
            surface.blit(ov, (bx, by))

            pos_lbl = get_font(size=24, bold=True).render(
                f"P{row['rank']}", True, (10,10,10))
            surface.blit(pos_lbl, pos_lbl.get_rect(center=(bx+bw//2, by+24)))

            nm = get_ui_font(size=13, bold=True).render(row["name"][:14], True, (10,10,10))
            surface.blit(nm, nm.get_rect(center=(bx+bw//2, by+50)))

            pt = get_ui_font(size=12).render(f"{row['pts']} pts", True, (20,20,20))
            surface.blit(pt, pt.get_rect(center=(bx+bw//2, by+70)))

            cr = get_ui_font(size=10).render(row["car"][:18], True, (30,30,30))
            surface.blit(cr, cr.get_rect(center=(bx+bw//2, by+88)))

    def _draw_table(self, surface: pygame.Surface, W: int) -> None:
        table_x, table_y, table_w = 160, 250, W - 320
        col_xs = [table_x+16, table_x+70, table_x+310, table_x+510,
                  table_x+590, table_x+660, table_x+750]
        hdrs   = ["#", "DRIVER", "CAR", "POINTS", "WINS", "RACES", "BEST LAP"]

        # Header row
        hdr_f = get_ui_font(size=12, bold=True)
        for h, cx in zip(hdrs, col_xs):
            surface.blit(hdr_f.render(h, True, TEXT_ACCENT), (cx, table_y))
        pygame.draw.line(surface, (38,46,68), (table_x, table_y+20),
                         (table_x+table_w, table_y+20), 1)

        row_f  = get_ui_font(size=13)
        bold_f = get_ui_font(size=13, bold=True)
        rank_colors = {1:(220,170,0), 2:(160,170,180), 3:(180,110,50)}

        for i, row in enumerate(self._scores[:10]):
            ry = table_y + 32 + i*42
            is_you = (row["name"] == "YOU")

            # Row background
            row_surf = pygame.Surface((table_w, 36), pygame.SRCALPHA)
            bg_col   = (20,25,42,220) if is_you else ((16,20,34,180) if i%2==0 else (12,15,26,160))
            pygame.draw.rect(row_surf, bg_col, row_surf.get_rect(), border_radius=6)
            if is_you:
                pygame.draw.rect(row_surf, (0,180,255,80), row_surf.get_rect(), width=1, border_radius=6)
            surface.blit(row_surf, (table_x, ry))

            vals = [
                str(row["rank"]),
                row["name"],
                row["car"][:20],
                str(row["pts"]),
                str(row["wins"]),
                str(row["races"]),
                row["best_lap"],
            ]
            rc = rank_colors.get(row["rank"], TEXT_WHITE)
            for vi, (val, cx) in enumerate(zip(vals, col_xs)):
                f = bold_f if (vi == 0 or is_you) else row_f
                c = rc if vi == 0 else (TEXT_ACCENT if is_you else TEXT_WHITE)
                surface.blit(f.render(val, True, c), (cx, ry+10))
