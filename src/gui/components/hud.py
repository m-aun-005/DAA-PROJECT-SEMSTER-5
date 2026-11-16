"""src/gui/components/hud.py — Asphalt 8-style In-Game HUD.

Cinematic overlays: arc speedometer, nitro bar, position badge, lap counter,
and animated event alerts.
"""

from typing import List, Optional, Tuple
import math
import pygame
from src.models.vehicle import Vehicle, VehicleState
from src.models.circuit import Circuit
from src.gui.assets.colors import PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_MUTED, TEXT_ACCENT, TEXT_GOLD, HUD_BG, NITRO_BLUE
from src.gui.assets.fonts import get_font, get_ui_font


class HUD:
    """Asphalt 8-style cinematic HUD overlay."""

    def __init__(self, surface: pygame.Surface):
        self.surface   = surface
        self._alert_txt = ""
        self._alert_timer = 0.0
        self._alert_slide = 0.0   # 0=hidden, 1=shown

    def update(self, dt: float) -> None:
        if self._alert_timer > 0:
            self._alert_timer  = max(0, self._alert_timer - dt)
            self._alert_slide  = min(1.0, self._alert_slide + dt * 6)
        else:
            self._alert_slide  = max(0.0, self._alert_slide - dt * 4)

    def show_alert(self, text: str, duration: float = 2.5) -> None:
        self._alert_txt   = text
        self._alert_timer = duration
        self._alert_slide = 0.0

    def draw(
        self,
        player_veh: Vehicle,
        vehicles: List[Vehicle],
        circuit: Circuit,
        current_time: float,
        active_alerts: List[str],
    ) -> None:
        W, H = self.surface.get_size()

        # 1. Bottom-center speedometer arc
        self._draw_speedometer(W, H, player_veh)

        # 2. Bottom-left nitro bar
        self._draw_nitro_bar(H, player_veh)

        # 3. Top-center position badge
        self._draw_position_badge(W, vehicles, player_veh)

        # 4. Top-right lap + time
        self._draw_lap_time(W, player_veh, current_time)

        # 5. Mini standings on top-left
        self._draw_mini_standings(vehicles)

        # 6. Alert banner
        if active_alerts:
            last = active_alerts[-1]
            if last != self._alert_txt:
                self.show_alert(last)
        self._draw_alert(W, H)

        # 7. Checkpoint target
        self._draw_checkpoint_hint(W, H, player_veh)

    # ── Individual elements ───────────────────────────────────────────────────

    def _draw_speedometer(self, W: int, H: int, veh: Vehicle) -> None:
        cx   = W // 2
        cy   = H - 60
        R    = 70    # outer radius
        # Semi-arc bottom-center

        # Background arc
        pygame.draw.arc(self.surface, (22, 26, 42),
                        (cx-R, cy-R, R*2, R*2),
                        math.radians(200), math.radians(340), 14)

        # Speed fill arc (0–240 km/h → 0–1.0)
        speed_kmh = min(240, int(veh.speed * 3.6)) if hasattr(veh, "speed") else int(min(240, veh.fuel))
        # Use fuel as proxy if speed not set — but try speed attr first
        if hasattr(veh, "speed"):
            spd = getattr(veh, "speed", 0)
            speed_kmh = min(240, int(spd * 3.6))
        else:
            speed_kmh = 60

        frac = speed_kmh / 240.0
        arc_start = math.radians(200)
        arc_end   = math.radians(200 + frac * 140)

        if frac > 0.001:
            # Color gradient: green → yellow → red
            if frac < 0.5:
                r = int(frac * 2 * 255);  g = 220; b = 50
            else:
                r = 255; g = int((1 - (frac-0.5)*2) * 220); b = 50

            pygame.draw.arc(self.surface, (r, g, b),
                            (cx-R, cy-R, R*2, R*2),
                            arc_start, arc_end, 12)

        # Needle
        angle  = math.radians(200 + frac * 140)
        nx = cx + int((R-14) * math.cos(angle))
        ny = cy - int((R-14) * math.sin(angle))
        pygame.draw.line(self.surface, (255,255,255), (cx, cy), (nx, ny), 3)
        pygame.draw.circle(self.surface, (200,200,200), (cx, cy), 6)

        # Speed text
        spd_font = get_font(size=24, bold=True)
        spd_txt  = spd_font.render(str(speed_kmh), True, TEXT_WHITE)
        surface_blit_center(self.surface, spd_txt, cx, cy - 4)

        unit_txt = get_ui_font(size=10).render("km/h", True, TEXT_MUTED)
        surface_blit_center(self.surface, unit_txt, cx, cy + 20)

    def _draw_nitro_bar(self, H: int, veh: Vehicle) -> None:
        x, y = 32, H - 150
        bar_w, bar_h = 22, 110

        # Background
        pygame.draw.rect(self.surface, (18, 22, 36), (x, y, bar_w, bar_h), border_radius=11)
        pygame.draw.rect(self.surface, (40, 50, 80), (x, y, bar_w, bar_h), width=1, border_radius=11)

        # Nitro charges (3 segments)
        total_charges = 3
        seg_h  = (bar_h - 8) // total_charges
        filled = max(0, min(total_charges, veh.nitroCharges)) if hasattr(veh, "nitroCharges") else 0
        for i in range(total_charges):
            seg_y = y + bar_h - 4 - (i + 1) * (seg_h + 2) + 2
            col   = NITRO_BLUE if i < filled else (28, 36, 58)
            pygame.draw.rect(self.surface, col, (x+4, seg_y, bar_w-8, seg_h), border_radius=5)

        # Nitro label
        lbl = get_ui_font(size=10, bold=True).render("N", True, NITRO_BLUE)
        surface_blit_center(self.surface, lbl, x + bar_w//2, y - 12)

        lbl2 = get_ui_font(size=9).render("SPACE", True, TEXT_MUTED)
        surface_blit_center(self.surface, lbl2, x + bar_w//2, H - 30)

    def _draw_position_badge(self, W: int, vehicles: List[Vehicle], player: Vehicle) -> None:
        # Rank player
        sorted_v = sorted(vehicles,
            key=lambda v: (
                1 if v.dnf else 0,
                v.finishPosition if v.finishPosition is not None else 999,
                -v.lap,
                -len(v.checkpoints_visited_this_lap),
                v.totalTime,
            ))
        rank = next((i+1 for i, v in enumerate(sorted_v) if v.name == player.name), 1)

        # Badge
        bx, by = W//2 - 60, 10
        badge = pygame.Surface((120, 44), pygame.SRCALPHA)
        pygame.draw.rect(badge, (8,10,20,220), badge.get_rect(), border_radius=10)
        pygame.draw.rect(badge, (0,180,255,80), badge.get_rect(), width=1, border_radius=10)
        self.surface.blit(badge, (bx, by))

        pos_font = get_font(size=26, bold=True)
        pos_txt  = pos_font.render(f"P{rank}", True, TEXT_GOLD)
        surface_blit_center(self.surface, pos_txt, W//2 - 20, by + 22)

        of_txt = get_ui_font(size=12).render(f"/{len(vehicles)}", True, TEXT_MUTED)
        surface_blit_center(self.surface, of_txt, W//2 + 30, by + 24)

    def _draw_lap_time(self, W: int, veh: Vehicle, current_time: float) -> None:
        x = W - 200
        # Panel
        panel = pygame.Surface((190, 80), pygame.SRCALPHA)
        pygame.draw.rect(panel, (8,10,20,200), panel.get_rect(), border_radius=10)
        pygame.draw.rect(panel, (38,46,68,100), panel.get_rect(), width=1, border_radius=10)
        self.surface.blit(panel, (x, 10))

        lap_font = get_font(size=20, bold=True)
        lap_txt  = lap_font.render(f"LAP  {veh.lap} / 2", True, TEXT_WHITE)
        self.surface.blit(lap_txt, (x+14, 20))

        mins  = int(current_time) // 60
        secs  = current_time % 60
        t_str = f"{mins:01d}:{secs:05.2f}"
        t_txt = get_ui_font(size=16, bold=True).render(t_str, True, TEXT_ACCENT)
        self.surface.blit(t_txt, (x+14, 46))

    def _draw_mini_standings(self, vehicles: List[Vehicle]) -> None:
        x, y = 10, 10
        sorted_v = sorted(vehicles,
            key=lambda v: (
                1 if v.dnf else 0,
                v.finishPosition if v.finishPosition is not None else 999,
                -v.lap,
                -len(v.checkpoints_visited_this_lap),
                v.totalTime,
            ))

        panel = pygame.Surface((210, 14 + len(sorted_v)*26), pygame.SRCALPHA)
        pygame.draw.rect(panel, (8,10,20,200), panel.get_rect(), border_radius=10)
        pygame.draw.rect(panel, (38,46,68,80), panel.get_rect(), width=1, border_radius=10)
        self.surface.blit(panel, (x, y))

        hdr = get_ui_font(size=10, bold=True).render("LIVE  STANDINGS", True, TEXT_ACCENT)
        self.surface.blit(hdr, (x+10, y+6))

        for idx, v in enumerate(sorted_v):
            vy = y + 20 + idx*24
            # Color dot
            pygame.draw.circle(self.surface, v.color, (x+18, vy+8), 5)
            # Name + status
            status = "DNF" if v.dnf else (f"P{v.finishPosition}" if v.finishPosition else f"L{v.lap}")
            line   = f"{v.name[:12]:<12} {status}"
            lbl    = get_ui_font(size=11).render(line, True, TEXT_WHITE)
            self.surface.blit(lbl, (x+30, vy))

    def _draw_alert(self, W: int, H: int) -> None:
        if self._alert_slide < 0.01:
            return
        slide_y = H//2 - 90 - int((1.0 - self._alert_slide) * 60)
        alpha   = int(255 * min(1.0, self._alert_slide))

        banner = pygame.Surface((540, 46), pygame.SRCALPHA)
        pygame.draw.rect(banner, (160, 20, 20, int(alpha*0.9)), banner.get_rect(), border_radius=10)
        pygame.draw.rect(banner, (255, 80, 80, alpha), banner.get_rect(), width=1, border_radius=10)

        txt = get_font(size=16, bold=True).render(f"⚡  {self._alert_txt}", True, (255,255,255))
        t_r = txt.get_rect(center=(270, 23))
        banner.blit(txt, t_r)

        self.surface.blit(banner, (W//2 - 270, slide_y), special_flags=pygame.BLEND_ALPHA_SDL2)

    def _draw_checkpoint_hint(self, W: int, H: int, veh: Vehicle) -> None:
        if not hasattr(veh, "nextCheckpoint"):
            return
        cp  = veh.nextCheckpoint
        txt = f"→ CP {cp}" if cp <= 10 else "→ FINISH LINE"
        lbl = get_ui_font(size=13, bold=True).render(txt, True, TEXT_GOLD)
        self.surface.blit(lbl, lbl.get_rect(center=(W//2, H - 110)))


def surface_blit_center(surface: pygame.Surface, txt: pygame.Surface, cx: int, cy: int) -> None:
    r = txt.get_rect(center=(cx, cy))
    surface.blit(txt, r)
