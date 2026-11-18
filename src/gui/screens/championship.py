"""src/gui/screens/championship.py — Championship Seasons Selection Screen.

Shows available championship seasons with race counts, locked/unlocked status,
and car class requirements. The user picks a season, then proceeds to circuit
selection with championship context.
"""

from typing import Callable, Dict, List
import math
import pygame
from src.gui.assets.colors import BG_DARK, PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_ACCENT, TEXT_GOLD, TEXT_MUTED
from src.gui.assets.fonts import get_font, get_ui_font
from src.gui.components.button import Button

# ─── Season definitions ───────────────────────────────────────────────────────
SEASONS = [
    {
        "id":       1,
        "name":     "Season 1  —  Road to Glory",
        "year":     "1962",
        "races":    4,
        "circuits": ["Alpha Ring", "Gamma Grid", "Alpha Ring", "Beta Delta"],
        "laps":     2,
        "car_class":"Open",
        "reward":   "Unlock: Jaguar E-Type",
        "desc":     "Start your legend. Compete across 4 races on mixed circuits\nand prove you belong among the greats.",
        "locked":   False,
        "accent":   (0, 200, 255),
        "points_target": 50,
    },
    {
        "id":       2,
        "name":     "Season 2  —  Italian Fire",
        "year":     "1964",
        "races":    5,
        "circuits": ["Beta Delta","Alpha Ring","Gamma Grid","Beta Delta","Alpha Ring"],
        "laps":     2,
        "car_class":"GT",
        "reward":   "Unlock: Ferrari 250 GTO",
        "desc":     "Race through the technical figure-8 and street circuits\nwhere Italian engineering was forged in fire.",
        "locked":   False,
        "accent":   (220, 40, 40),
        "points_target": 90,
    },
    {
        "id":       3,
        "name":     "Season 3  —  American Muscle",
        "year":     "1967",
        "races":    5,
        "circuits": ["Alpha Ring","Gamma Grid","Beta Delta","Alpha Ring","Gamma Grid"],
        "laps":     3,
        "car_class":"Muscle",
        "reward":   "Unlock: Shelby GT500",
        "desc":     "V8 thunder on every straight. Brute force meets circuit\ncraft as the Pony Cars dominate the grid.",
        "locked":   False,
        "accent":   (255, 140, 0),
        "points_target": 120,
    },
    {
        "id":       4,
        "name":     "Season 4  —  24 Hours Legend",
        "year":     "1966",
        "races":    6,
        "circuits": ["Beta Delta","Beta Delta","Gamma Grid","Alpha Ring","Gamma Grid","Beta Delta"],
        "laps":     3,
        "car_class":"GT",
        "reward":   "Unlock: Ford GT40 Mk.II",
        "desc":     "Endurance. Precision. Courage. Ford vs Ferrari,\nthe circuit that defined an era. Can you last?",
        "locked":   False,
        "accent":   (0, 160, 255),
        "points_target": 165,
    },
    {
        "id":       5,
        "name":     "Season 5  —  Grand Finale",
        "year":     "1969",
        "races":    7,
        "circuits": ["Alpha Ring","Beta Delta","Gamma Grid","Beta Delta","Alpha Ring","Gamma Grid","Beta Delta"],
        "laps":     3,
        "car_class":"Open",
        "reward":   "Champion Trophy + All Cars",
        "desc":     "Every circuit. Every legend. All 7 rounds to decide\nthe greatest driver of a legendary era.",
        "locked":   False,
        "accent":   (255, 200, 0),
        "points_target": 220,
    },
]


class ChampionshipScreen:
    """Season selection carousel screen."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen  = switch_screen
        self.selected_idx   = 0
        self.time           = 0.0
        self._hovered_card  = -1

        # Scroll offset for card strip
        self._scroll_x = 0.0
        self._target_scroll = 0.0

        # Buttons
        self._btn_back = Button((20, 20, 110, 36), "← BACK",
                                callback=lambda: self.switch_screen("main_menu", {}),
                                font_size=14)
        self._btn_start = Button((490, 660, 300, 46), "START SEASON  ▶",
                                 callback=self._start_season,
                                 font_size=18, bold=True, accent_color=(255, 180, 0))
        self._btn_left  = Button((30, 320, 46, 46), "◀",
                                 callback=self._prev, font_size=20, bold=True)
        self._btn_right = Button((1204, 320, 46, 46), "▶",
                                 callback=self._next, font_size=20, bold=True)

    def _prev(self):
        self.selected_idx = max(0, self.selected_idx - 1)
        self._target_scroll = self.selected_idx * -380.0

    def _next(self):
        self.selected_idx = min(len(SEASONS)-1, self.selected_idx + 1)
        self._target_scroll = self.selected_idx * -380.0

    def _start_season(self):
        s = SEASONS[self.selected_idx]
        self.switch_screen("circuit_select", {
            "circuit_idx":  0,
            "laps":         s["laps"],
            "championship": True,
            "season":       s,
        })

    def set_context(self, ctx: Dict) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        self._btn_back.handle_event(event)
        self._btn_start.handle_event(event)
        self._btn_left.handle_event(event)
        self._btn_right.handle_event(event)

        if event.type == pygame.MOUSEMOTION:
            self._hovered_card = -1
            mx, my = event.pos
            for i in range(len(SEASONS)):
                card_r = self._card_rect(i)
                if card_r.collidepoint(mx, my):
                    self._hovered_card = i
                    break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i in range(len(SEASONS)):
                if self._card_rect(i).collidepoint(mx, my):
                    self.selected_idx = i
                    self._target_scroll = i * -380.0
                    break

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._prev()
            elif event.key == pygame.K_RIGHT:
                self._next()
            elif event.key == pygame.K_RETURN:
                self._start_season()

    def update(self, dt: float) -> None:
        self.time += dt
        self._btn_back.update(dt)
        self._btn_start.update(dt)
        self._btn_left.update(dt)
        self._btn_right.update(dt)
        # Smooth scroll
        self._scroll_x += (self._target_scroll - self._scroll_x) * min(1.0, dt * 10)

    def _card_rect(self, idx: int) -> pygame.Rect:
        cx = 640 + idx * 380 + int(self._scroll_x)
        return pygame.Rect(cx - 170, 100, 340, 520)

    def draw(self, surface: pygame.Surface) -> None:
        W, H = surface.get_size()
        self._draw_bg(surface, W, H)

        # Header
        hdr_font = get_font(size=38, bold=True)
        hdr = hdr_font.render("CHAMPIONSHIP SEASONS", True, TEXT_WHITE)
        surface.blit(hdr, hdr.get_rect(center=(W//2, 54)))
        sub = get_ui_font(size=14).render(
            "Choose your season and chase the championship title", True, TEXT_MUTED)
        surface.blit(sub, sub.get_rect(center=(W//2, 82)))
        pygame.draw.line(surface, TEXT_GOLD, (W//2-280, 94), (W//2+280, 94), 2)

        # Cards (clipped)
        clip = surface.get_clip()
        surface.set_clip(pygame.Rect(80, 95, W-160, 540))
        for i in range(len(SEASONS)):
            self._draw_card(surface, i)
        surface.set_clip(clip)

        # Nav buttons + race button
        self._btn_left.draw(surface)
        self._btn_right.draw(surface)
        self._btn_start.draw(surface)
        self._btn_back.draw(surface)

        # Season progress dots
        dot_y = 648
        for i in range(len(SEASONS)):
            col = TEXT_GOLD if i == self.selected_idx else (40, 46, 68)
            pygame.draw.circle(surface, col, (W//2 - len(SEASONS)*14 + i*28, dot_y), 6)

    def _draw_bg(self, surface: pygame.Surface, W: int, H: int) -> None:
        surface.fill(BG_DARK)
        # Subtle diagonal lines
        for x in range(-H, W+H, 70):
            line_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.line(line_surf, (0, 180, 255, 8), (x, 0), (x-H, H), 1)
            surface.blit(line_surf, (0, 0))

    def _draw_card(self, surface: pygame.Surface, idx: int) -> None:
        s      = SEASONS[idx]
        cr     = self._card_rect(idx)
        accent = s["accent"]
        is_sel = (idx == self.selected_idx)
        is_hov = (idx == self._hovered_card)

        # Scale selected card slightly
        if is_sel:
            expand = 8
            cr = cr.inflate(expand, expand)

        # Card background
        card_surf = pygame.Surface(cr.size, pygame.SRCALPHA)
        bg_alpha  = 245 if is_sel else (210 if is_hov else 185)
        pygame.draw.rect(card_surf, (14, 18, 32, bg_alpha), card_surf.get_rect(), border_radius=16)
        surface.blit(card_surf, cr.topleft)

        # Top accent bar
        pygame.draw.rect(surface, accent, (cr.x, cr.y, cr.width, 6), border_radius=16)

        # Border
        bwidth = 2 if is_sel else 1
        pygame.draw.rect(surface, accent if is_sel else (38,46,68), cr, width=bwidth, border_radius=16)

        # Year badge
        year_font = get_font(size=58, bold=True)
        year_txt  = year_font.render(s["year"], True, (*accent, 60))
        yr = year_txt.get_rect(center=(cr.centerx, cr.y + 68))
        surface.blit(year_txt, yr)

        # Season number
        num_font = get_ui_font(size=12, bold=True)
        num_txt  = num_font.render(f"SEASON  {s['id']}", True, accent)
        surface.blit(num_txt, num_txt.get_rect(centerx=cr.centerx, y=cr.y + 20))

        # Season name
        name_font = get_font(size=18, bold=True)
        name_txt  = name_font.render(s["name"].split("—")[1].strip(), True, TEXT_WHITE)
        surface.blit(name_txt, name_txt.get_rect(centerx=cr.centerx, y=cr.y + 108))

        # Separator
        pygame.draw.line(surface, (38,46,68), (cr.x+16, cr.y+136), (cr.right-16, cr.y+136), 1)

        # Description
        desc_font = get_ui_font(size=12)
        for li, line in enumerate(s["desc"].split("\n")):
            lt = desc_font.render(line, True, TEXT_WHITE)
            surface.blit(lt, lt.get_rect(centerx=cr.centerx, y=cr.y + 148 + li*18))

        # Stats grid
        stats = [
            ("ROUNDS",  str(s["races"]) + " Races"),
            ("LAPS",    str(s["laps"]) + " per race"),
            ("CLASS",   s["car_class"]),
            ("TARGET",  str(s["points_target"]) + " pts"),
        ]
        sg_y = cr.y + 198
        pygame.draw.line(surface, (38,46,68), (cr.x+16, sg_y-4), (cr.right-16, sg_y-4), 1)
        label_f = get_ui_font(size=10, bold=True)
        val_f   = get_ui_font(size=12, bold=True)
        col_w   = cr.width // 2
        for si, (lbl, val) in enumerate(stats):
            col = si % 2
            row = si // 2
            sx  = cr.x + 16 + col * col_w
            sy  = sg_y + row * 40
            lt  = label_f.render(lbl, True, TEXT_MUTED)
            vt  = val_f.render(val, True, TEXT_WHITE)
            surface.blit(lt, (sx, sy))
            surface.blit(vt, (sx, sy + 14))

        # Reward
        pygame.draw.line(surface, (38,46,68), (cr.x+16, cr.y+304), (cr.right-16, cr.y+304), 1)
        rew_font = get_ui_font(size=11, bold=True)
        rew_txt  = rew_font.render(f"🏆  {s['reward']}", True, TEXT_GOLD)
        surface.blit(rew_txt, rew_txt.get_rect(centerx=cr.centerx, y=cr.y + 310))

        # Race circuit list
        rc_y = cr.y + 338
        rc_f = get_ui_font(size=11)
        rc_lbl = rc_f.render("CIRCUITS:", True, TEXT_MUTED)
        surface.blit(rc_lbl, (cr.x+16, rc_y))
        for ri, circuit_name in enumerate(s["circuits"]):
            rt = rc_f.render(f"R{ri+1}:  {circuit_name}", True, TEXT_WHITE)
            surface.blit(rt, (cr.x+20, rc_y + 16 + ri*16))

        # SELECT indicator
        if is_sel:
            sel_bg = pygame.Surface((cr.width-16, 34), pygame.SRCALPHA)
            pygame.draw.rect(sel_bg, (*accent, 55), sel_bg.get_rect(), border_radius=8)
            surface.blit(sel_bg, (cr.x+8, cr.bottom - 44))
            sel_txt = get_ui_font(size=13, bold=True).render("SELECTED — PRESS START", True, accent)
            surface.blit(sel_txt, sel_txt.get_rect(center=(cr.centerx, cr.bottom - 26)))
