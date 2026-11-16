"""src/gui/components/graph_renderer.py — Graph Rendering Component for Pygame.
"""

from __future__ import annotations
import math
from typing import Dict, List, Optional, Set, Tuple
import pygame
from src.core.graph import Graph
from src.models.vertex import Vertex, VertexType
from src.models.edge import Edge, EdgeStatus
from src.gui.assets.colors import (
    ROAD_COLOR, ROAD_BLOCKED, ROAD_RESTRICTED, ROAD_SHORTCUT,
    VERTEX_NORMAL, VERTEX_CHECKPOINT, VERTEX_START_FINISH,
    VERTEX_FUEL, VERTEX_NITRO, VERTEX_DEAD_END,
    COLOR_VISITED, COLOR_FRONTIER, COLOR_CURRENT,
    TEXT_WHITE, TEXT_MUTED
)
from src.gui.assets.fonts import get_font


class GraphRenderer:
    """Renders a circuit Graph onto a Pygame surface with custom highlights."""

    def __init__(self, surface: pygame.Surface, graph: Graph):
        self.surface = surface
        self.graph = graph
        self.font = get_font(size=11, bold=True)
        self.font_large = get_font(size=13, bold=True)

        # Highlight overlays
        self.highlighted_path: List[int] = []
        self.path_color: Tuple[int, int, int] = (0, 200, 255)
        self.visited_nodes: Set[int] = set()
        self.frontier_nodes: Set[int] = set()
        self.current_node: Optional[int] = None
        self.mst_edges: Set[int] = set()

    def set_path_highlight(self, path: List[int], color: Tuple[int, int, int] = (0, 200, 255)) -> None:
        self.highlighted_path = list(path)
        self.path_color = color

    def set_algorithm_state(self, visited: Set[int], frontier: Set[int], current: Optional[int]) -> None:
        self.visited_nodes = set(visited)
        self.frontier_nodes = set(frontier)
        self.current_node = current

    def set_mst_highlight(self, edges: List[Edge]) -> None:
        self.mst_edges = {e.id for e in edges}

    def clear_highlights(self) -> None:
        self.highlighted_path.clear()
        self.visited_nodes.clear()
        self.frontier_nodes.clear()
        self.current_node = None
        self.mst_edges.clear()

    def draw(self) -> None:
        self._draw_edges()
        self._draw_highlighted_path()
        self._draw_vertices()

    def _draw_edges(self) -> None:
        drawn_edges = set()
        for e in self.graph.edges.values():
            if e.id in drawn_edges:
                continue
            drawn_edges.add(e.id)

            u = self.graph.get_vertex(e.from_vertex)
            v = self.graph.get_vertex(e.to_vertex)
            if not u or not v:
                continue

            # Determine color
            if e.id in self.mst_edges:
                color = (120, 220, 255)
                width = 5
            elif e.status == EdgeStatus.BLOCKED:
                color = ROAD_BLOCKED
                width = 4
            elif e.status == EdgeStatus.RESTRICTED:
                color = ROAD_RESTRICTED
                width = 4
            elif e.isShortcut:
                color = ROAD_SHORTCUT
                width = 4
            else:
                color = ROAD_COLOR
                width = 3

            p1 = (int(u.x), int(u.y))
            p2 = (int(v.x), int(v.y))
            pygame.draw.line(self.surface, color, p1, p2, width)

            # If one-way, draw directional arrowhead
            if e.directed:
                self._draw_arrow(p1, p2, color)

    def _draw_highlighted_path(self) -> None:
        if len(self.highlighted_path) < 2:
            return
        for i in range(len(self.highlighted_path) - 1):
            u = self.graph.get_vertex(self.highlighted_path[i])
            v = self.graph.get_vertex(self.highlighted_path[i + 1])
            if u and v:
                p1 = (int(u.x), int(u.y))
                p2 = (int(v.x), int(v.y))
                pygame.draw.line(self.surface, self.path_color, p1, p2, 6)

    def _draw_vertices(self) -> None:
        for v in self.graph.vertices.values():
            pos = (int(v.x), int(v.y))
            radius = 12

            # Determine color based on algorithm state or vertex type
            if v.id == self.current_node:
                color = COLOR_CURRENT
                radius = 16
            elif v.id in self.frontier_nodes:
                color = COLOR_FRONTIER
                radius = 14
            elif v.id in self.visited_nodes:
                color = COLOR_VISITED
            elif v.type in (VertexType.START, VertexType.FINISH):
                color = VERTEX_START_FINISH
                radius = 14
            elif v.type == VertexType.CHECKPOINT:
                color = VERTEX_CHECKPOINT
                radius = 13
            elif v.type == VertexType.FUEL_STATION:
                color = VERTEX_FUEL if v.active else (80, 80, 80)
                radius = 13
            elif v.type == VertexType.NITRO_PICKUP:
                color = VERTEX_NITRO if v.active else (80, 80, 80)
                radius = 12
            elif v.type == VertexType.DEAD_END:
                color = VERTEX_DEAD_END
                radius = 12
            else:
                color = VERTEX_NORMAL
                radius = 10

            # Outer ring + fill
            pygame.draw.circle(self.surface, (30, 35, 48), pos, radius + 2)
            pygame.draw.circle(self.surface, color, pos, radius)

            # Text Label inside or next to vertex
            label = str(v.checkpointOrder) if v.is_mandatory_checkpoint() else str(v.id)
            txt = self.font.render(label, True, (15, 15, 20) if color in (VERTEX_CHECKPOINT, COLOR_FRONTIER, COLOR_CURRENT) else TEXT_WHITE)
            t_rect = txt.get_rect(center=pos)
            self.surface.blit(txt, t_rect)

    def _draw_arrow(self, p1: Tuple[int, int], p2: Tuple[int, int], color: Tuple[int, int, int]) -> None:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dist = math.hypot(dx, dy)
        if dist < 30:
            return
        # Position arrowhead at 65% of the edge
        mx = p1[0] + dx * 0.65
        my = p1[1] + dy * 0.65
        angle = math.atan2(dy, dx)
        arrow_size = 8
        left_angle = angle + math.pi * 0.8
        right_angle = angle - math.pi * 0.8
        p_left = (int(mx + arrow_size * math.cos(left_angle)), int(my + arrow_size * math.sin(left_angle)))
        p_right = (int(mx + arrow_size * math.cos(right_angle)), int(my + arrow_size * math.sin(right_angle)))
        pygame.draw.polygon(self.surface, color, [(int(mx), int(my)), p_left, p_right])
