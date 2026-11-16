"""src/core/mst.py — Minimum Spanning Tree Algorithms: Kruskal and Prim (Section 5.4).
Provides both algorithms along with Union-Find Disjoint Set for track backbone generation.
"""

from __future__ import annotations
import heapq
import time
from typing import Dict, Generator, List, Optional, Set, Tuple
from src.core.graph import Graph
from src.models.edge import Edge


class DisjointSetUnion:
    """Disjoint Set Union (DSU / Union-Find) with path compression and union by rank."""

    def __init__(self, elements: List[int]):
        self.parent: Dict[int, int] = {x: x for x in elements}
        self.rank: Dict[int, int] = {x: 0 for x in elements}
        self.num_components: int = len(elements)

    def find(self, x: int) -> int:
        """Find representative with path compression."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """Union sets containing x and y by rank. Returns True if merged, False if already connected."""
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            return False

        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        self.num_components -= 1
        return True


class KruskalMST:
    """Kruskal's Algorithm using Disjoint Set Union.
    
    Time Complexity: O(E log E)
    Auxiliary Space: O(V)
    """

    def __init__(self, graph: Graph):
        self.graph = graph
        self.mst_edges: List[Edge] = []
        self.total_weight: float = 0.0
        self.edges_examined: int = 0
        self.comparisons: int = 0
        self.execution_time_us: float = 0.0

    def run(self) -> Dict[str, object]:
        """Builds MST backbone over all vertices."""
        t0 = time.perf_counter()
        
        self.mst_edges = []
        self.total_weight = 0.0
        self.edges_examined = 0
        self.comparisons = 0

        # Unique edges (undirected)
        unique_edges = list(self.graph.edges.values())
        # Sort edges by distance
        unique_edges.sort(key=lambda e: e.distance)
        self.comparisons = len(unique_edges)  # approximation of sorting comparisons

        dsu = DisjointSetUnion(list(self.graph.vertices.keys()))

        for edge in unique_edges:
            self.edges_examined += 1
            if dsu.union(edge.from_vertex, edge.to_vertex):
                self.mst_edges.append(edge)
                self.total_weight += edge.distance
                if len(self.mst_edges) == len(self.graph.vertices) - 1:
                    break

        self.execution_time_us = (time.perf_counter() - t0) * 1e6

        return {
            "mst_edges": self.mst_edges,
            "total_weight": round(self.total_weight, 2),
            "edge_count": len(self.mst_edges),
            "is_connected_tree": len(self.mst_edges) == max(0, len(self.graph.vertices) - 1),
            "stats": self.get_stats()
        }

    def get_stats(self) -> Dict[str, object]:
        return {
            "mst_edge_count": len(self.mst_edges),
            "total_weight": round(self.total_weight, 2),
            "edges_examined": self.edges_examined,
            "comparisons": self.comparisons,
            "execution_time_us": round(self.execution_time_us, 2)
        }

    def step_generator(self) -> Generator[Dict[str, object], None, None]:
        """Step-by-step generator for visualizer."""
        unique_edges = list(self.graph.edges.values())
        unique_edges.sort(key=lambda e: e.distance)
        dsu = DisjointSetUnion(list(self.graph.vertices.keys()))
        mst_edges: List[Edge] = []
        total_w = 0.0

        for edge in unique_edges:
            accepted = dsu.union(edge.from_vertex, edge.to_vertex)
            if accepted:
                mst_edges.append(edge)
                total_w += edge.distance

            yield {
                "current_edge": edge,
                "accepted": accepted,
                "mst_edges": list(mst_edges),
                "total_weight": total_w,
                "done": len(mst_edges) == len(self.graph.vertices) - 1
            }

            if len(mst_edges) == len(self.graph.vertices) - 1:
                break


class PrimMST:
    """Prim's Algorithm using Binary Min-Heap.
    
    Time Complexity: O(E log V)
    Auxiliary Space: O(V)
    """

    def __init__(self, graph: Graph):
        self.graph = graph
        self.mst_edges: List[Edge] = []
        self.total_weight: float = 0.0
        self.heap_operations: int = 0
        self.execution_time_us: float = 0.0

    def run(self, start_vid: Optional[int] = None) -> Dict[str, object]:
        t0 = time.perf_counter()
        
        self.mst_edges = []
        self.total_weight = 0.0
        self.heap_operations = 0

        if not self.graph.vertices:
            return {"mst_edges": [], "total_weight": 0.0, "stats": self.get_stats()}

        if start_vid is None or start_vid not in self.graph.vertices:
            start_vid = next(iter(self.graph.vertices.keys()))

        visited: Set[int] = {start_vid}
        # Heap format: (weight, edge_id, from_v, to_v)
        pq: List[Tuple[float, int, int, int]] = []

        for v, edge in self.graph.get_neighbors(start_vid, traversable_only=False):
            heapq.heappush(pq, (edge.distance, edge.id, start_vid, v))
            self.heap_operations += 1

        while pq and len(visited) < len(self.graph.vertices):
            w, eid, u, v = heapq.heappop(pq)
            self.heap_operations += 1

            if v in visited:
                continue

            visited.add(v)
            edge = self.graph.edges[eid]
            self.mst_edges.append(edge)
            self.total_weight += w

            for nxt, nxt_edge in self.graph.get_neighbors(v, traversable_only=False):
                if nxt not in visited:
                    heapq.heappush(pq, (nxt_edge.distance, nxt_edge.id, v, nxt))
                    self.heap_operations += 1

        self.execution_time_us = (time.perf_counter() - t0) * 1e6

        return {
            "mst_edges": self.mst_edges,
            "total_weight": round(self.total_weight, 2),
            "edge_count": len(self.mst_edges),
            "is_connected_tree": len(self.mst_edges) == max(0, len(self.graph.vertices) - 1),
            "stats": self.get_stats()
        }

    def get_stats(self) -> Dict[str, object]:
        return {
            "mst_edge_count": len(self.mst_edges),
            "total_weight": round(self.total_weight, 2),
            "edges_examined": self.edges_examined,
            "comparisons": self.comparisons,
            "execution_time_us": round(self.execution_time_us, 2)
        }

    def get_stats(self) -> Dict[str, object]:
        return {
            "mst_edge_count": len(self.mst_edges),
            "total_weight": round(self.total_weight, 2),
            "heap_operations": self.heap_operations,
            "execution_time_us": round(self.execution_time_us, 2)
        }
