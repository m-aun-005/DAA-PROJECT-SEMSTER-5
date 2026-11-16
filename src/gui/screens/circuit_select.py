"""src/gui/screens/circuit_select.py — Asphalt 8-style Track Selection Screen.

3 large card panels with circuit mini-maps, difficulty stars, and descriptions.
"""

from typing import Callable, Dict, List, Tuple
import math
import pygame
from src.gui.components.button import Button
from src.gui.assets.colors import BG_DARK, PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_ACCENT, TEXT_GOLD, TEXT_MUTED
from src.gui.assets.fonts import get_font, get_ui_font
from src.data.circuits import ALL_CIRCUITS


_CIRCUIT_DATA = [
    {
        "name":        "ALPHA RING",
        "subtitle":    "Desert Oval Circuit",
        "difficulty":  2,
        "length":      "4.8 km",
        "corners":     12,
        "description": "High-speed perimeter oval with dangerous\ncentral chord shortcuts and a dead-end\ncanyon trap. Best for drafting.",
        "accent":      (0, 195, 255),
        "tag":         "SPEED",
    },
    {
        "name":        "BETA DELTA",
        "subtitle":    "Mountain Figure-8",
        "difficulty":  3,
        "length":      "6.2 km",
        "corners":     18,
        "description": "Classic figure-8 crossover design with\ndouble loops, bypass bridges, and blind\ncornering. High risk, high reward.",
        "accent":      (255, 160, 0),
        "tag":         "TECHNICAL",
    },
    {
        "name":        "GAMMA GRID",
        "subtitle":    "Urban Street Circuit",
        "difficulty":  4,
        "length":      "5.6 km",
        "corners":     24,
        "description": "Dense downtown street grid with one-way\nthoroughfares, diagonal alleys, and traffic\nblockades. Master every route.",
        "accent":      (40, 220, 100),
        "tag":         "COMPLEX",
    },
]


def _draw_mini_map(surface: pygame.Surface, cx: int, cy: int, size: int, circuit_idx: int) -> None:
    """Draw a simplified mini-map thumbnail for a circuit."""
    circ = ALL_CIRCUITS[circuit_idx]()
    g = circ.graph

    # Find bounding box of vertices
    xs = [v.x for v in g.vertices.values()]
    ys = [v.y for v in g.vertices.values()]
    if not xs:
        return
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    rng_x = max_x - min_x or 1
    rng_y = max_y - min_y or 1
    pad = 16

    def to_screen(vx, vy):
        nx = (vx - min_x) / rng_x
        ny = (vy - min_y) / rng_y
        sx = int(cx - size//2 + pad + nx * (size - 2*pad))
        sy = int(cy - size//2 + pad + ny * (size - 2*pad))
        return sx, sy

    # Draw edges
    for e in g.edges.values():
        u = g.get_vertex(e.from_vertex)
        v = g.get_vertex(e.to_vertex)
        if u and v:
            col = (60, 65, 85) if not e.isShortcut else (200, 100, 20)
            pygame.draw.line(surface, col, to_screen(u.x, u.y), to_screen(v.x, v.y), 2)

    # Draw vertices
    from src.models.vertex import VertexType
    for v in g.vertices.values():
        sp = to_screen(v.x, v.y)
        if v.type in (VertexType.START, VertexType.FINISH):
            pygame.draw.circle(surface, (50, 220, 100), sp, 4)
        elif v.type == VertexType.CHECKPOINT:
            pygame.draw.circle(surface, (255, 200, 0), sp, 3)
        else:
            pygame.draw.circle(surface, (100, 110, 135), sp, 2)


class CircuitSelectScreen:
    """Screen: Asphalt 8-style track selection with 3 big cards."""

    def __init__(self, switch_screen: Callable[[str, Dict], None]):
        self.switch_screen   = switch_screen
        self.selected_idx    = 0
        self.selected_laps   = 2
        self.time            = 0.0
        self._hover_card     = -1

        # Pre-render mini maps into surfaces
        MAP_SZ = 180
        self._mini_maps: List[pygame.Surface] = []
        for i in range(3):
            ms = pygame.Surface((MAP_SZ, MAP_SZ))
            ms.fill((14, 18, 28))
            pygame.draw.rect(ms, (30, 36, 55), ms.get_rect(), border_radius=8)
            _draw_mini_map(ms, MAP_SZ//2, MAP_SZ//2, MAP_SZ, i)
            self._mini_maps.append(ms)

        # Card layout: 3 cards side by side
        self._card_rects: List[pygame.Rect] = []
        CARD_W, CARD_H = 340, 480
        total_w = 3 * CARD_W + 2 * 24
        x0 = (1280 - total_w) // 2
        for i in range(3):
            self._card_rects.append(pygame.Rect(x0 + i * (CARD_W + 24), 110, CARD_W, CARD_H))

        # Laps buttons
        self._laps_btns = [
            Button((550, 622, 60, 36), "1 LAP",  callback=lambda: self._set_laps(1), font_size=14),
            Button((620, 622, 60, 36), "2 LAPS", callback=lambda: self._set_laps(2), font_size=14),
            Button((690, 622, 60, 36), "3 LAPS", callback=lambda: self._set_laps(3), font_size=14),
        ]
        self._laps_btns[1].is_active = True

        self._race_btn = Button((510, 668, 260, 44), "RACE  ▶",
                                callback=self._go_race, font_size=18, bold=True,
                                accent_color=(0, 220, 80))
        self._back_btn = Button((20, 20, 110, 36), "← BACK",
                                callback=lambda: self.switch_screen("main_menu", {}),
                                font_size=14)

    def set_context(self, context: Dict) -> None:
        self.selected_idx  = context.get("circuit_idx", 0)
        self.selected_laps = context.get("laps", 2)

    def _set_laps(self, n: int) -> None:
        self.selected_laps = n
        for i, btn in enumerate(self._laps_btns):
            btn.is_active = (i == n - 1)

    def _go_race(self) -> None:
        self.switch_screen("car_select", {
            "circuit_idx": self.selected_idx,
            "laps":        self.selected_laps,
        })

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            self._hover_card = -1
            for i, cr in enumerate(self._card_rects):
                if cr.collidepoint(event.pos):
                    self._hover_card = i
                    break

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, cr in enumerate(self._card_rects):
                if cr.collidepoint(event.pos):
                    self.selected_idx = i
                    break

        for btn in self._laps_btns:
            btn.handle_event(event)
        self._race_btn.handle_event(event)
        self._back_btn.handle_event(event)

    def update(self, dt: float) -> None:
        self.time += dt
        for btn in self._laps_btns:
            btn.update(dt)
        self._race_btn.update(dt)
        self._back_btn.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        W, H = surface.get_size()
        surface.fill(BG_DARK)
        self._draw_bg(surface, W, H)

        # Header
        hdr_font = get_font(size=36, bold=True)
        hdr = hdr_font.render("SELECT TRACK", True, TEXT_WHITE)
        surface.blit(hdr, hdr.get_rect(center=(W//2, 62)))
        pygame.draw.line(surface, TEXT_ACCENT, (W//2 - 220, 82), (W//2 + 220, 82), 2)

        # 3 cards
        for i in range(3):
            self._draw_card(surface, i)

        # Laps selector label
        laps_lbl = get_ui_font(size=14).render("LAPS:", True, TEXT_MUTED)
        surface.blit(laps_lbl, (490, 630))
        for btn in self._laps_btns:
            btn.draw(surface)

        # Race button
        self._race_btn.draw(surface)
        self._back_btn.draw(surface)

    def _draw_bg(self, surface: pygame.Surface, W: int, H: int):
        # Subtle diagonal grid
        for x in range(0, W + H, 80):
            alpha = 12
            line_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            pygame.draw.line(line_surf, (0, 180, 255, alpha), (x, 0), (x - H, H), 1)
            surface.blit(line_surf, (0, 0))

    def _draw_card(self, surface: pygame.Surface, idx: int) -> None:
        cr     = self._card_rects[idx]
        data   = _CIRCUIT_DATA[idx]
        accent = data["accent"]
        is_sel = (idx == self.selected_idx)
        is_hov = (idx == self._hover_card)

        # Card background
        card_surf = pygame.Surface(cr.size, pygame.SRCALPHA)
        bg_alpha  = 240 if is_sel else (200 if is_hov else 180)
        pygame.draw.rect(card_surf, (14, 18, 30, bg_alpha), card_surf.get_rect(), border_radius=14)
        surface.blit(card_surf, cr.topleft)

        # Border glow
        border_col = accent if is_sel else ((*accent, 80) if is_hov else (38, 46, 68))
        bwidth = 3 if is_sel else 1
        pygame.draw.rect(surface, border_col, cr, width=bwidth, border_radius=14)

        # Top accent bar
        pygame.draw.rect(surface, accent, (cr.x, cr.y, cr.width, 5), border_radius=14)

        # Tag badge
        tag_font = get_ui_font(size=11, bold=True)
        tag_txt  = tag_font.render(data["tag"], True, BG_DARK)
        tag_w    = tag_txt.get_width() + 16
        pygame.draw.rect(surface, accent, (cr.right - tag_w - 10, cr.y + 14, tag_w, 22), border_radius=11)
        surface.blit(tag_txt, (cr.right - tag_w - 2, cr.y + 17))

        # Mini-map
        ms   = self._mini_maps[idx]
        ms_x = cr.x + (cr.width - ms.get_width()) // 2
        ms_y = cr.y + 20
        surface.blit(ms, (ms_x, ms_y))

        # Border around mini-map
        pygame.draw.rect(surface, (38,46,68), (ms_x-1, ms_y-1, ms.get_width()+2, ms.get_height()+2), 1, border_radius=8)

        # Circuit name
        name_font = get_font(size=22, bold=True)
        name_txt  = name_font.render(data["name"], True, TEXT_WHITE)
        surface.blit(name_txt, name_txt.get_rect(centerx=cr.centerx, y=ms_y + ms.get_height() + 10))

        # Subtitle
        sub_font = get_ui_font(size=13)
        sub_txt  = sub_font.render(data["subtitle"], True, (*accent,))
        surface.blit(sub_txt, sub_txt.get_rect(centerx=cr.centerx, y=ms_y + ms.get_height() + 36))

        # Difficulty stars
        star_y = ms_y + ms.get_height() + 60
        for s in range(5):
            col = TEXT_GOLD if s < data["difficulty"] else (40, 46, 68)
            sx  = cr.centerx - 60 + s * 26
            self._draw_star(surface, sx, star_y, 10, col)

        # Stats row
        stats_y = star_y + 28
        stat_font = get_ui_font(size=11)
        s1 = stat_font.render(f"Length: {data['length']}", True, TEXT_MUTED)
        s2 = stat_font.render(f"Corners: {data['corners']}", True, TEXT_MUTED)
        surface.blit(s1, s1.get_rect(centerx=cr.centerx - 55, y=stats_y))
        surface.blit(s2, s2.get_rect(centerx=cr.centerx + 55, y=stats_y))

        # Separator
        pygame.draw.line(surface, (38,46,68), (cr.x+16, stats_y+22), (cr.right-16, stats_y+22), 1)

        # Description
        desc_font = get_ui_font(size=12)
        for li, line in enumerate(data["description"].split("\n")):
            lt = desc_font.render(line, True, TEXT_WHITE)
            surface.blit(lt, lt.get_rect(centerx=cr.centerx, y=stats_y + 32 + li * 18))

        # Selected indicator
        if is_sel:
            sel_surf = pygame.Surface((cr.width, 36), pygame.SRCALPHA)
            pygame.draw.rect(sel_surf, (*accent, 40), sel_surf.get_rect(), border_radius=8)
            surface.blit(sel_surf, (cr.x, cr.bottom - 46))
            sel_txt = get_ui_font(size=13, bold=True).render("SELECTED", True, accent)
            surface.blit(sel_txt, sel_txt.get_rect(center=(cr.centerx, cr.bottom - 28)))
        else:
            sel_txt = get_ui_font(size=12).render("CLICK TO SELECT", True, TEXT_MUTED)
            surface.blit(sel_txt, sel_txt.get_rect(center=(cr.centerx, cr.bottom - 28)))

    def _draw_star(self, surface: pygame.Surface, cx: int, cy: int, r: int, color) -> None:
        pts = []
        for i in range(10):
            angle = math.pi / 2 + math.pi * 2 * i / 10
            rr = r if i % 2 == 0 else r * 0.45
            pts.append((int(cx + rr*math.cos(angle)), int(cy + rr*math.sin(angle))))
        pygame.draw.polygon(surface, color, pts)
