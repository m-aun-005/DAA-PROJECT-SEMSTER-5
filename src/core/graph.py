"""src/core/graph.py — Adjacency list track graph representation G = (V, E).
Satisfies Section 3.1 & 3.3.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple
from src.models.vertex import Vertex, VertexType
from src.models.edge import Edge, EdgeStatus, RoutingPreset


class Graph:
    """Directed/undirected road network represented as an adjacency list.
    
    Memory complexity: O(V + E)
    Neighbor query complexity: O(deg(v))
    Supports dynamic edge blocking/unblocking and service toggling in O(1)
    without graph reconstruction.
    """

    def __init__(self):
        self.vertices: Dict[int, Vertex] = {}
        self.edges: Dict[int, Edge] = {}
        # Adjacency list: vertex_id -> list of outgoing edges
        self.adj: Dict[int, List[Edge]] = {}
        # Reverse adjacency for directed reachability analysis
        self.in_adj: Dict[int, List[Edge]] = {}

    def add_vertex(self, vertex: Vertex) -> None:
        """Adds a vertex to the graph."""
        if vertex.id not in self.vertices:
            self.vertices[vertex.id] = vertex
            self.adj[vertex.id] = []
            self.in_adj[vertex.id] = []

    def add_edge(self, edge: Edge) -> None:
        """Adds an edge to the graph. If not directed, adds reciprocal edge in adjacency."""
        if edge.from_vertex not in self.vertices or edge.to_vertex not in self.vertices:
            raise ValueError(f"Endpoints {edge.from_vertex} -> {edge.to_vertex} must exist before adding edge.")

        self.edges[edge.id] = edge
        self.adj[edge.from_vertex].append(edge)
        self.in_adj[edge.to_vertex].append(edge)

        # For undirected edges, add reciprocal traversal in adjacency
        if not edge.directed:
            # Create a reciprocal representation pointing from to_vertex to from_vertex
            reciprocal_edge = Edge(
                id=edge.id,
                from_vertex=edge.to_vertex,
                to_vertex=edge.from_vertex,
                distance=edge.distance,
                baseTime=edge.baseTime,
                fuelCost=edge.fuelCost,
                difficulty=edge.difficulty,
                status=edge.status,
                isShortcut=edge.isShortcut,
                directed=False,
                hazard_level=edge.hazard_level,
                speed_cap=edge.speed_cap
            )
            self.adj[edge.to_vertex].append(reciprocal_edge)
            self.in_adj[edge.from_vertex].append(reciprocal_edge)

    def get_vertex(self, vid: int) -> Optional[Vertex]:
        return self.vertices.get(vid)

    def get_edge(self, eid: int) -> Optional[Edge]:
        return self.edges.get(eid)

    def get_outgoing_edges(self, vid: int, traversable_only: bool = True) -> List[Edge]:
        """Returns all outgoing edges from vid, optionally filtering out blocked edges."""
        if vid not in self.adj:
            return []
        if traversable_only:
            return [e for e in self.adj[vid] if self.edges[e.id].is_traversable]
        return list(self.adj[vid])

    def get_neighbors(self, vid: int, traversable_only: bool = True) -> List[Tuple[int, Edge]]:
        """Returns list of (neighbor_vid, edge) tuples from vid."""
        edges = self.get_outgoing_edges(vid, traversable_only=traversable_only)
        return [(e.to_vertex, self.edges[e.id]) for e in edges]

    def set_edge_status(self, eid: int, status: EdgeStatus) -> bool:
        """Dynamically updates edge status in O(1)."""
        edge = self.edges.get(eid)
        if edge:
            edge.status = status
            # Also update any reciprocal edges in adj lists
            for v_edges in self.adj.values():
                for e in v_edges:
                    if e.id == eid:
                        e.status = status
            return True
        return False

    def set_edge_hazard(self, eid: int, hazard: float) -> bool:
        """Sets obstacle hazard level on an edge."""
        edge = self.edges.get(eid)
        if edge:
            edge.hazard_level = hazard
            for v_edges in self.adj.values():
                for e in v_edges:
                    if e.id == eid:
                        e.hazard_level = hazard
            return True
        return False

    def set_edge_speed_cap(self, eid: int, speed_cap: float) -> bool:
        """Sets speed cap modifier on an edge."""
        edge = self.edges.get(eid)
        if edge:
            edge.speed_cap = speed_cap
            for v_edges in self.adj.values():
                for e in v_edges:
                    if e.id == eid:
                        e.speed_cap = speed_cap
            return True
        return False

    def set_vertex_active(self, vid: int, active: bool) -> bool:
        """Dynamically activates or deactivates a service vertex (FuelStation, NitroPickup)."""
        v = self.vertices.get(vid)
        if v:
            v.active = active
            return True
        return False

    def get_checkpoints_in_order(self) -> List[Vertex]:
        """Returns all mandatory checkpoints sorted by checkpointOrder."""
        cps = [v for v in self.vertices.values() if v.is_mandatory_checkpoint()]
        cps.sort(key=lambda v: v.checkpointOrder if v.checkpointOrder is not None else 999)
        return cps

    def get_shortcuts(self) -> List[Edge]:
        """Returns all designated shortcut edges."""
        return [e for e in self.edges.values() if e.isShortcut]

    def get_fuel_stations(self) -> List[Vertex]:
        """Returns all fuel station vertices."""
        return [v for v in self.vertices.values() if v.type == VertexType.FUEL_STATION]

    def get_nitro_pickups(self) -> List[Vertex]:
        """Returns all nitro pickup vertices."""
        return [v for v in self.vertices.values() if v.type == VertexType.NITRO_PICKUP]

    def edge_between(self, u: int, v: int) -> Optional[Edge]:
        """Finds direct edge from u to v if one exists."""
        for e in self.get_outgoing_edges(u, traversable_only=False):
            if e.to_vertex == v:
                return self.edges[e.id]
        return None
