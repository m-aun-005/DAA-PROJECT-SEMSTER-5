"""src/gui/screens/scoreboard.py — Global Scoreboard Screen.

Tracks race wins, podiums, and championship points for YOU and the AI opponents
across all race sessions. Data persists in a JSON file on disk.
"""

from typing import Callable, Dict, List, Optional
import json
import os
import math
import pygame
from src.gui.assets.colors import BG_DARK, PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_ACCENT, TEXT_GOLD, TEXT_MUTED
from src.gui.assets.fonts import get_font, get_ui_font
from src.gui.components.button import Button

_SAVE_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "scoreboard.json"
)

# Real championship roster: YOU + AI bots (Cars character racers)
_DEFAULT_SCORES: List[Dict] = [
    {"rank": 1, "name": "YOU",                "car": "Lightning McQueen", "pts": 0, "wins": 0, "races": 0, "best_lap": "—"},
    {"rank": 2, "name": "Chick Hicks (AI)",   "car": "Chick Hicks",       "pts": 0, "wins": 0, "races": 0, "best_lap": "—"},
    {"rank": 3, "name": "The King (AI)",      "car": "The King (#43)",    "pts": 0, "wins": 0, "races": 0, "best_lap": "—"},
    {"rank": 4, "name": "Doc Hudson (AI)",    "car": "Doc Hudson",        "pts": 0, "wins": 0, "races": 0, "best_lap": "—"},
    {"rank": 5, "name": "Jackson Storm (AI)", "car": "Jackson Storm",     "pts": 0, "wins": 0, "races": 0, "best_lap": "—"},
    {"rank": 6, "name": "Sally Carrera (AI)", "car": "Sally Carrera",     "pts": 0, "wins": 0, "races": 0, "best_lap": "—"},
    {"rank": 7, "name": "Ramone (AI)",        "car": "Ramone",            "pts": 0, "wins": 0, "races": 0, "best_lap": "—"},
    {"rank": 8, "name": "Tow Mater (AI)",     "car": "Tow Mater",         "pts": 0, "wins": 0, "races": 0, "best_lap": "—"},
]


def _load_scores() -> List[Dict]:
    path = os.path.normpath(_SAVE_FILE)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if data and isinstance(data, list):
                    # Verify it doesn't contain obsolete fake names
                    if not any("El Maestro" in str(x) for x in data):
                        return data
        except Exception:
            pass
    # Initialize fresh default
    return [dict(e) for e in _DEFAULT_SCORES]


def save_championship_results(results: list, player_car: str = "Lightning McQueen", vehicles: Optional[list] = None) -> None:
    """Updates scoreboard with results for BOTH the human player and all participating AI bots.
    Accumulates points, wins, races, and best lap times across multiple races.
    """
    scores = _load_scores()
    pts_table = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1]

    # Map vehicle id to vehicle object
    veh_map = {getattr(v, "id", i): v for i, v in enumerate(vehicles or [])}

    for r in results:
        pos = getattr(r, "finishPosition", None)
        pts = pts_table[pos - 1] if (pos is not None and 1 <= pos <= len(pts_table)) else 0
        won = 1 if pos == 1 else 0

        # Calculate lap time string
        lap_secs = getattr(r, "finishTime", None) or getattr(r, "totalTime", 0.0) or 0.0
        best_lap_str = "—"
        if lap_secs > 0 and not getattr(r, "dnf", False):
            mins = int(lap_secs) // 60
            secs = lap_secs % 60
            best_lap_str = f"{mins}:{secs:05.2f}"

        r_name = getattr(r, "racerName", "") or ""
        r_id   = getattr(r, "racerId", 0)
        is_player = (r_id == 1 or "YOU" in r_name or "Player" in r_name)

        target = None
        if is_player:
            for row in scores:
                if "YOU" in row["name"]:
                    target = row
                    break
            car_name = player_car
            display_name = "YOU"
        else:
            # AI bot: find matching entry in scores
            clean_name = r_name if r_name.endswith("(AI)") else f"{r_name} (AI)"
            display_name = clean_name
            for row in scores:
                if row["name"] == clean_name or row["name"].replace(" (AI)", "") == r_name.replace(" (AI)", ""):
                    target = row
                    break
            car_name = r_name.replace(" (AI)", "")
            if r_id in veh_map:
                v = veh_map[r_id]
                car_name = getattr(v, "car_name", None) or v.name.replace(" (AI)", "")

        if target is None:
            target = {
                "rank": len(scores) + 1,
                "name": display_name,
                "car": car_name,
                "pts": 0,
                "wins": 0,
                "races": 0,
                "best_lap": "—",
            }
            scores.append(target)

        # Accumulate stats across multiple races
        target["pts"]   += pts
        target["wins"]  += won
        target["races"] += 1
        if car_name and car_name != "—":
            target["car"] = car_name
        if best_lap_str != "—":
            if target["best_lap"] == "—" or best_lap_str < target["best_lap"]:
                target["best_lap"] = best_lap_str

    # Re-rank by points (descending), wins (descending), best_lap (ascending)
    def _rank_key(row):
        lap_val = (1, "") if row["best_lap"] == "—" else (0, row["best_lap"])
        return (-row["pts"], -row["wins"], lap_val)

    scores.sort(key=_rank_key)
    for i, row in enumerate(scores):
        row["rank"] = i + 1

    path = os.path.normpath(_SAVE_FILE)
    try:
        with open(path, "w") as f:
            json.dump(scores, f, indent=2)
    except Exception:
        pass


def save_race_result(player_pts: int, wins: int, best_lap: str, car_name: str) -> None:
    """Legacy backward-compatible wrapper."""
    scores = _load_scores()
    for row in scores:
        if "YOU" in row["name"]:
            row["pts"]   += player_pts
            row["wins"]  += wins
            row["races"] += 1
            row["car"]    = car_name
            if best_lap != "—" and (row["best_lap"] == "—" or best_lap < row["best_lap"]):
                row["best_lap"] = best_lap
            break
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
    """Global championship leaderboard screen tracking real players and AI bots."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen = switch_screen
        self.time          = 0.0
        self._scores       = _load_scores()
        self._btn_back     = Button((20, 20, 110, 36), "← BACK",
                                    callback=lambda: self.switch_screen("main_menu", {}), font_size=14)
        self._btn_reset    = Button((1130, 20, 130, 36), "RESET SEASON",
                                    callback=self._reset, font_size=13, accent_color=(255, 60, 60))

    def _reset(self) -> None:
        self._scores = [dict(e) for e in _DEFAULT_SCORES]
        path = os.path.normpath(_SAVE_FILE)
        try:
            with open(path, "w") as f:
                json.dump(self._scores, f, indent=2)
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
        hdr = get_font(size=36, bold=True).render("CHAMPIONSHIP SCOREBOARD", True, TEXT_WHITE)
        surface.blit(hdr, hdr.get_rect(center=(W//2, 50)))
        sub = get_ui_font(size=13).render("Real-time accumulated standings: You vs AI Opponents", True, TEXT_MUTED)
        surface.blit(sub, sub.get_rect(center=(W//2, 74)))
        pygame.draw.line(surface, TEXT_GOLD, (W//2-280, 86), (W//2+280, 86), 2)

        # Podium
        self._draw_podium(surface, W)

        # Main table
        self._draw_table(surface, W)

        self._btn_back.draw(surface)
        self._btn_reset.draw(surface)

    def _draw_bg(self, surface: pygame.Surface, W: int, H: int) -> None:
        surface.fill(BG_DARK)
        # Desert dust / warm stripes
        for x in range(-H, W+H, 80):
            ls = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.line(ls, (255, 180, 0, 8), (x, 0), (x-H, H), 1)
            surface.blit(ls, (0, 0))

    def _draw_podium(self, surface: pygame.Surface, W: int) -> None:
        """Draw top-3 large podium blocks."""
        if len(self._scores) < 3:
            return
        podium_data = [
            (self._scores[1], W//2 - 220, 104, 150, 120, (170, 175, 185)),  # 2nd Silver
            (self._scores[0], W//2 - 90,   90, 180, 134, (220, 170,   0)),  # 1st Gold
            (self._scores[2], W//2 + 100, 116, 150, 108, (190, 120,  55)),  # 3rd Bronze
        ]
        for row, bx, by, bw, bh, col in podium_data:
            pygame.draw.rect(surface, col, (bx, by, bw, bh), border_radius=8)
            ov = pygame.Surface((bw, bh), pygame.SRCALPHA)
            pygame.draw.rect(ov, (0, 0, 0, 75), ov.get_rect(), border_radius=8)
            surface.blit(ov, (bx, by))

            pos_lbl = get_font(size=24, bold=True).render(f"P{row['rank']}", True, (10, 10, 10))
            surface.blit(pos_lbl, pos_lbl.get_rect(center=(bx+bw//2, by+24)))

            nm = get_ui_font(size=13, bold=True).render(row["name"][:16], True, (10, 10, 10))
            surface.blit(nm, nm.get_rect(center=(bx+bw//2, by+50)))

            pt = get_ui_font(size=12).render(f"{row['pts']} pts  ({row['wins']}W)", True, (20, 20, 20))
            surface.blit(pt, pt.get_rect(center=(bx+bw//2, by+70)))

            cr = get_ui_font(size=10).render(row["car"][:18], True, (30, 30, 30))
            surface.blit(cr, cr.get_rect(center=(bx+bw//2, by+88)))

    def _draw_table(self, surface: pygame.Surface, W: int) -> None:
        table_x, table_y, table_w = 140, 246, W - 280
        col_xs = [table_x+16, table_x+70, table_x+330, table_x+540,
                  table_x+630, table_x+710, table_x+810]
        hdrs   = ["#", "RACER", "MACHINE", "POINTS", "WINS", "RACES", "BEST LAP"]

        # Header row
        hdr_f = get_ui_font(size=12, bold=True)
        for h, cx in zip(hdrs, col_xs):
            surface.blit(hdr_f.render(h, True, TEXT_ACCENT), (cx, table_y))
        pygame.draw.line(surface, (120, 80, 30), (table_x, table_y+20),
                         (table_x+table_w, table_y+20), 1)

        row_f  = get_ui_font(size=13)
        bold_f = get_ui_font(size=13, bold=True)
        rank_colors = {1:(255, 210, 40), 2:(190, 195, 205), 3:(205, 135, 65)}

        for i, row in enumerate(self._scores[:10]):
            ry = table_y + 30 + i*42
            is_you = ("YOU" in row["name"])

            # Row background
            row_surf = pygame.Surface((table_w, 36), pygame.SRCALPHA)
            bg_col   = (65, 42, 18, 230) if is_you else ((45, 28, 12, 190) if i%2==0 else (35, 20, 8, 160))
            pygame.draw.rect(row_surf, bg_col, row_surf.get_rect(), border_radius=6)
            if is_you:
                pygame.draw.rect(row_surf, (255, 180, 0, 200), row_surf.get_rect(), width=2, border_radius=6)
            surface.blit(row_surf, (table_x, ry))

            vals = [
                str(row["rank"]),
                row["name"],
                row["car"][:22],
                str(row["pts"]),
                str(row["wins"]),
                str(row["races"]),
                row["best_lap"],
            ]
            rc = rank_colors.get(row["rank"], TEXT_WHITE)
            for vi, (val, cx) in enumerate(zip(vals, col_xs)):
                f = bold_f if (vi == 0 or is_you) else row_f
                c = rc if vi == 0 else (TEXT_GOLD if is_you else TEXT_WHITE)
                surface.blit(f.render(val, True, c), (cx, ry+10))
