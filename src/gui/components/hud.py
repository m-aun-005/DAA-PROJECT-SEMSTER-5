"""src/gui/components/hud.py — In-Game Heads-Up Display (HUD).
"""

from typing import List, Tuple
import pygame
from src.models.vehicle import Vehicle, VehicleState
from src.models.circuit import Circuit
from src.gui.assets.colors import PANEL_BG, PANEL_BORDER, TEXT_WHITE, TEXT_MUTED, TEXT_ACCENT
from src.gui.assets.fonts import get_font


class HUD:
    """Renders real-time telemetry, lap status, fuel gauge, nitro charges, and alerts."""

    def __init__(self, surface: pygame.Surface):
        self.surface = surface
        self.font_title = get_font(size=18, bold=True)
        self.font_body = get_font(size=14, bold=True)
        self.font_small = get_font(size=12)

    def draw(
        self,
        player_veh: Vehicle,
        vehicles: List[Vehicle],
        circuit: Circuit,
        current_time: float,
        active_alerts: List[str]
    ) -> None:
        # 1. Top-Left Player Telemetry Card
        self._draw_player_telemetry(player_veh, current_time)

        # 2. Top-Right Mini Leaderboard
        self._draw_mini_leaderboard(vehicles)

        # 3. Bottom Event Notification Banner
        self._draw_event_alerts(active_alerts)

    def _draw_player_telemetry(self, veh: Vehicle, current_time: float) -> None:
        rect = pygame.Rect(15, 15, 260, 150)
        pygame.draw.rect(self.surface, PANEL_BG, rect, border_radius=8)
        pygame.draw.rect(self.surface, PANEL_BORDER, rect, width=1, border_radius=8)

        # Header
        txt_title = self.font_title.render("TELEMETRY", True, TEXT_ACCENT)
        self.surface.blit(txt_title, (rect.x + 12, rect.y + 10))

        # Time & Lap
        time_str = f"Time: {current_time:.1f}s | Lap: {veh.lap} / 2"
        txt_time = self.font_body.render(time_str, True, TEXT_WHITE)
        self.surface.blit(txt_time, (rect.x + 12, rect.y + 36))

        # Next Checkpoint
        cp_str = f"Next Target: CP{veh.nextCheckpoint}" if veh.nextCheckpoint <= 10 else "Head to FINISH!"
        txt_cp = self.font_small.render(cp_str, True, (255, 200, 0))
        self.surface.blit(txt_cp, (rect.x + 12, rect.y + 58))

        # Fuel Bar
        lbl_fuel = self.font_small.render(f"Fuel: {veh.fuel:.0f}%", True, TEXT_WHITE)
        self.surface.blit(lbl_fuel, (rect.x + 12, rect.y + 80))

        bar_rect = pygame.Rect(rect.x + 12, rect.y + 98, 236, 14)
        pygame.draw.rect(self.surface, (40, 45, 60), bar_rect, border_radius=3)
        fuel_w = int(236 * (max(0.0, min(100.0, veh.fuel)) / 100.0))
        if fuel_w > 0:
            fuel_color = (50, 220, 100) if veh.fuel > 50 else ((240, 200, 30) if veh.fuel > 25 else (240, 50, 50))
            pygame.draw.rect(self.surface, fuel_color, (bar_rect.x, bar_rect.y, fuel_w, bar_rect.height), border_radius=3)

        # Nitro Charges
        lbl_nitro = self.font_small.render("Nitro (SPACE):", True, TEXT_WHITE)
        self.surface.blit(lbl_nitro, (rect.x + 12, rect.y + 120))
        for i in range(3):
            cx = rect.x + 115 + i * 22
            cy = rect.y + 128
            color = (0, 210, 255) if i < veh.nitroCharges else (60, 70, 90)
            pygame.draw.circle(self.surface, color, (cx, cy), 7)
            pygame.draw.circle(self.surface, (120, 140, 180), (cx, cy), 8, 1)

    def _draw_mini_leaderboard(self, vehicles: List[Vehicle]) -> None:
        rect = pygame.Rect(1005, 15, 260, 150)
        pygame.draw.rect(self.surface, PANEL_BG, rect, border_radius=8)
        pygame.draw.rect(self.surface, PANEL_BORDER, rect, width=1, border_radius=8)

        txt_hdr = self.font_title.render("LIVE STANDINGS", True, TEXT_ACCENT)
        self.surface.blit(txt_hdr, (rect.x + 12, rect.y + 10))

        # Sort racers by position
        sorted_vehs = sorted(
            vehicles,
            key=lambda v: (
                1 if v.dnf else 0,
                v.finishPosition if v.finishPosition is not None else 999,
                -v.lap,
                -len(v.checkpoints_visited_this_lap),
                v.totalTime
            )
        )

        for idx, v in enumerate(sorted_vehs):
            y_pos = rect.y + 38 + idx * 26
            # Color dot
            pygame.draw.circle(self.surface, v.color, (rect.x + 20, y_pos + 8), 5)
            # Racer info
            status = "DNF" if v.dnf else (f"P{v.finishPosition}" if v.finishPosition else f"Lap {v.lap}")
            line = f"{v.name[:16]:<16} {status}"
            txt = self.font_small.render(line, True, TEXT_WHITE)
            self.surface.blit(txt, (rect.x + 35, y_pos))

    def _draw_event_alerts(self, alerts: List[str]) -> None:
        if not alerts:
            return
        last_alert = alerts[-1]
        banner_rect = pygame.Rect(320, 670, 640, 36)
        pygame.draw.rect(self.surface, (180, 40, 40), banner_rect, border_radius=6)
        pygame.draw.rect(self.surface, (255, 150, 150), banner_rect, width=1, border_radius=6)

        txt = self.font_body.render(f"EVENT: {last_alert}", True, (255, 255, 255))
        t_rect = txt.get_rect(center=banner_rect.center)
        self.surface.blit(txt, t_rect)
