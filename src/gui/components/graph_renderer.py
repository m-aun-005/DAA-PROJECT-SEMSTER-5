"""src/gui/components/graph_renderer.py — Asphalt 8-style Track & Graph Renderer.
"""

from __future__ import annotations
import math
from typing import Dict, List, Optional, Set, Tuple
import pygame
from src.core.graph import Graph
from src.models.vertex import Vertex, VertexType
from src.models.edge import Edge, EdgeStatus
from src.gui.assets.colors import (
    ROAD_COLOR, ROAD_SURFACE, ROAD_LINE, ROAD_GRASS,
    ROAD_BLOCKED, ROAD_RESTRICTED, ROAD_SHORTCUT,
    VERTEX_NORMAL, VERTEX_CHECKPOINT, VERTEX_START_FINISH,
    VERTEX_FUEL, VERTEX_NITRO, VERTEX_DEAD_END,
    COLOR_VISITED, COLOR_FRONTIER, COLOR_CURRENT,
    TEXT_WHITE, TEXT_MUTED, PANEL_BG, PANEL_BORDER, TEXT_ACCENT
)
from src.gui.assets.fonts import get_font, get_ui_font


class GraphRenderer:
    """Renders a circuit Graph onto a Pygame surface with Asphalt 8-style racetrack visuals."""

    def __init__(self, surface: pygame.Surface, graph: Graph):
        self.surface  = surface
        self.graph    = graph
        self.font     = get_ui_font(size=10, bold=True)
        self.font_lrg = get_ui_font(size=13, bold=True)

        # Highlight overlays
        self.highlighted_path: List[int]    = []
        self.path_color: Tuple[int,int,int] = (0, 200, 255)
        self.visited_nodes:  Set[int]        = set()
        self.frontier_nodes: Set[int]        = set()
        self.current_node:  Optional[int]    = None
        self.mst_edges:     Set[int]         = set()

    # ── Public API ────────────────────────────────────────────────────────────

    def set_path_highlight(self, path: List[int], color=(0,200,255)):
        self.highlighted_path = list(path)
        self.path_color = color

    def set_algorithm_state(self, visited: Set[int], frontier: Set[int], current: Optional[int]):
        self.visited_nodes  = set(visited)
        self.frontier_nodes = set(frontier)
        self.current_node   = current

    def set_mst_highlight(self, edges: List[Edge]):
        self.mst_edges = {e.id for e in edges}

    def clear_highlights(self):
        self.highlighted_path.clear()
        self.visited_nodes.clear()
        self.frontier_nodes.clear()
        self.current_node = None
        self.mst_edges.clear()

    def draw(self):
        self._draw_road_surfaces()
        self._draw_edges()
        self._draw_road_markings()
        self._draw_highlighted_path()
        self._draw_vertices()

    # ── Private Drawing ───────────────────────────────────────────────────────

    def _draw_road_surfaces(self):
        """Draw thick road surfaces (grey fill beneath edges) for racetrack feel."""
        road_width = 18
        for e in self.graph.edges.values():
            u = self.graph.get_vertex(e.from_vertex)
            v = self.graph.get_vertex(e.to_vertex)
            if not u or not v:
                continue
            p1 = (int(u.x), int(u.y))
            p2 = (int(v.x), int(v.y))
            if e.status == EdgeStatus.BLOCKED:
                col = ROAD_BLOCKED
            elif e.status == EdgeStatus.RESTRICTED:
                col = ROAD_RESTRICTED
            elif e.isShortcut:
                col = ROAD_SHORTCUT
            else:
                col = ROAD_COLOR
            pygame.draw.line(self.surface, col, p1, p2, road_width)

    def _draw_road_markings(self):
        """Draw white center dashes on normal roads."""
        for e in self.graph.edges.values():
            if e.status == EdgeStatus.BLOCKED or e.isShortcut:
                continue
            u = self.graph.get_vertex(e.from_vertex)
            v = self.graph.get_vertex(e.to_vertex)
            if not u or not v:
                continue
            # Draw dashed center line
            self._draw_dashed_line((int(u.x), int(u.y)), (int(v.x), int(v.y)),
                                   ROAD_LINE, dash_len=12, gap_len=10, width=2)
            # Direction arrow on one-way edges
            if e.directed:
                self._draw_arrow((int(u.x), int(u.y)), (int(v.x), int(v.y)), (255, 160, 0), size=10)

    def _draw_dashed_line(self, p1, p2, color, dash_len=12, gap_len=10, width=2):
        dx = p2[0] - p1[0]; dy = p2[1] - p1[1]
        dist = math.hypot(dx, dy)
        if dist < 1:
            return
        ux, uy = dx/dist, dy/dist
        step = dash_len + gap_len
        pos  = step * 0.5   # start midway
        while pos + dash_len < dist:
            ax = p1[0] + ux * pos;        ay = p1[1] + uy * pos
            bx = p1[0] + ux * (pos+dash_len); by = p1[1] + uy * (pos+dash_len)
            pygame.draw.line(self.surface, color, (int(ax), int(ay)), (int(bx), int(by)), width)
            pos += step

    def _draw_edges(self):
        """Draw algorithm-state overlays on top of road surfaces."""
        for e in self.graph.edges.values():
            if e.id not in self.mst_edges and not self.highlighted_path:
                continue
            u = self.graph.get_vertex(e.from_vertex)
            v = self.graph.get_vertex(e.to_vertex)
            if not u or not v:
                continue
            if e.id in self.mst_edges:
                pygame.draw.line(self.surface, (120, 220, 255),
                                 (int(u.x), int(u.y)), (int(v.x), int(v.y)), 5)

    def _draw_highlighted_path(self):
        if len(self.highlighted_path) < 2:
            return
        for i in range(len(self.highlighted_path) - 1):
            u = self.graph.get_vertex(self.highlighted_path[i])
            v = self.graph.get_vertex(self.highlighted_path[i+1])
            if u and v:
                pygame.draw.line(self.surface, self.path_color,
                                 (int(u.x), int(u.y)), (int(v.x), int(v.y)), 7)

    def _draw_vertices(self):
        for v in self.graph.vertices.values():
            pos = (int(v.x), int(v.y))
            self._draw_vertex(v, pos)

    def _draw_vertex(self, v: Vertex, pos: Tuple[int,int]):
        """Draw a single vertex with its type icon."""
        # Determine style
        if v.id == self.current_node:
            color, radius, ring = COLOR_CURRENT, 16, (255,255,255)
        elif v.id in self.frontier_nodes:
            color, radius, ring = COLOR_FRONTIER, 14, (255, 220, 0)
        elif v.id in self.visited_nodes:
            color, radius, ring = COLOR_VISITED, 11, VERTEX_NORMAL
        elif v.type in (VertexType.START, VertexType.FINISH):
            color, radius, ring = VERTEX_START_FINISH, 15, (80, 255, 140)
        elif v.type == VertexType.CHECKPOINT:
            color, radius, ring = VERTEX_CHECKPOINT, 14, (255, 230, 50)
        elif v.type == VertexType.FUEL_STATION:
            color = VERTEX_FUEL if v.active else (60,60,60)
            radius, ring = 13, VERTEX_FUEL
        elif v.type == VertexType.NITRO_PICKUP:
            color = VERTEX_NITRO if v.active else (60,60,60)
            radius, ring = 12, VERTEX_NITRO
        elif v.type == VertexType.DEAD_END:
            color, radius, ring = VERTEX_DEAD_END, 12, (200, 50, 50)
        else:
            color, radius, ring = VERTEX_NORMAL, 10, PANEL_BORDER

        # Outer glow ring
        pygame.draw.circle(self.surface, ring, pos, radius + 4, 2)
        # Dark halo
        pygame.draw.circle(self.surface, (12, 14, 22), pos, radius + 2)
        # Fill
        pygame.draw.circle(self.surface, color, pos, radius)

        # Type icon
        if v.type == VertexType.CHECKPOINT and v.is_mandatory_checkpoint():
            lbl = str(v.checkpointOrder)
            txt = self.font.render(lbl, True, (10,10,10))
            self.surface.blit(txt, txt.get_rect(center=pos))
        elif v.type in (VertexType.START, VertexType.FINISH):
            lbl = "S" if v.type == VertexType.START else "F"
            txt = self.font.render(lbl, True, (10,10,10))
            self.surface.blit(txt, txt.get_rect(center=pos))
        elif v.type == VertexType.FUEL_STATION:
            self._draw_fuel_icon(pos)
        elif v.type == VertexType.NITRO_PICKUP:
            self._draw_nitro_icon(pos)
        elif v.type == VertexType.DEAD_END:
            txt = self.font.render("X", True, (255,255,255))
            self.surface.blit(txt, txt.get_rect(center=pos))
        else:
            lbl = str(v.id)
            txt = self.font.render(lbl, True, TEXT_WHITE if color == VERTEX_NORMAL else (10,10,10))
            self.surface.blit(txt, txt.get_rect(center=pos))

        # Checkpoint rings (decorative)
        if v.type == VertexType.CHECKPOINT:
            pygame.draw.circle(self.surface, (255, 200, 0, 60), pos, radius + 10, 1)

    def _draw_fuel_icon(self, pos: Tuple[int,int]):
        """Draw tiny gas-pump icon."""
        x, y = pos[0]-4, pos[1]-5
        pygame.draw.rect(self.surface, (200, 200, 200), (x,   y,   8,  10))  # body
        pygame.draw.rect(self.surface, (200, 200, 200), (x+6, y+2, 4,  3))   # nozzle arm
        pygame.draw.rect(self.surface, (200, 200, 200), (x-1, y+8, 10, 2))   # base

    def _draw_nitro_icon(self, pos: Tuple[int,int]):
        """Draw tiny lightning bolt."""
        bx, by = pos[0], pos[1]
        pts = [(bx-2, by-6), (bx+3, by-1), (bx, by-1), (bx+2, by+6), (bx-3, by+1), (bx, by+1)]
        pygame.draw.polygon(self.surface, (230, 230, 50), pts)

    def _draw_arrow(self, p1, p2, color, size=8):
        dx = p2[0]-p1[0]; dy = p2[1]-p1[1]
        dist = math.hypot(dx, dy)
        if dist < 20:
            return
        mx = p1[0] + dx*0.6;  my = p1[1] + dy*0.6
        angle = math.atan2(dy, dx)
        la, ra = angle + math.pi*0.75, angle - math.pi*0.75
        pl = (int(mx + size*math.cos(la)), int(my + size*math.sin(la)))
        pr = (int(mx + size*math.cos(ra)), int(my + size*math.sin(ra)))
        pygame.draw.polygon(self.surface, color, [(int(mx), int(my)), pl, pr])
