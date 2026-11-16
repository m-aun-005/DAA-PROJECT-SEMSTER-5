"""src/core/dijkstra.py — Dijkstra's Shortest Path Algorithm (Section 5.2).
Guarantees optimal path for non-negative scalar edge costs using binary min-heap.
Supports checkpoint-aware multi-leg route staging.
"""

from __future__ import annotations
import heapq
import time
from typing import Dict, Generator, List, Optional, Set, Tuple
from src.core.graph import Graph
from src.models.edge import RoutingPreset


class Dijkstra:
    """Dijkstra's Algorithm with binary heap priority queue.
    
    Time Complexity: O((V + E) log V)
    Auxiliary Space: O(V)
    Optimizes the exact multi-objective scalar cost function.
    """

    def __init__(self, graph: Graph):
        self.graph = graph
        self.distances: Dict[int, float] = {}
        self.parent: Dict[int, Optional[int]] = {}
        self.parent_edge: Dict[int, Optional[int]] = {}
        self.visited: Set[int] = set()

        # Operation counters for empirical benchmarks (Experiment 2)
        self.expanded_vertices: int = 0
        self.relaxed_edges: int = 0
        self.heap_operations: int = 0
        self.execution_time_us: float = 0.0
        self.final_path_cost: float = float('inf')

    def run(self, start_vid: int, target_vid: Optional[int] = None, preset: RoutingPreset = RoutingPreset.BALANCED) -> Dict[str, object]:
        """Computes single-source shortest path to target_vid (or all reachable nodes)."""
        t0 = time.perf_counter()
        
        self.distances = {vid: float('inf') for vid in self.graph.vertices}
        self.parent = {vid: None for vid in self.graph.vertices}
        self.parent_edge = {vid: None for vid in self.graph.vertices}
        self.visited = set()
        
        self.expanded_vertices = 0
        self.relaxed_edges = 0
        self.heap_operations = 0

        if start_vid not in self.graph.vertices:
            self.execution_time_us = (time.perf_counter() - t0) * 1e6
            return {
                "reachable": False,
                "path": [],
                "cost": float('inf'),
                "stats": self.get_stats()
            }

        self.distances[start_vid] = 0.0
        pq: List[Tuple[float, int]] = [(0.0, start_vid)]
        self.heap_operations += 1

        found = False
        while pq:
            d_u, u = heapq.heappop(pq)
            self.heap_operations += 1

            if u in self.visited:
                continue

            self.visited.add(u)
            self.expanded_vertices += 1

            if target_vid is not None and u == target_vid:
                found = True
                break

            for v, edge in self.graph.get_neighbors(u, traversable_only=True):
                if v in self.visited:
                    continue

                cost_e = edge.compute_scalar_cost(preset)
                if cost_e == float('inf'):
                    continue

                self.relaxed_edges += 1
                new_dist = d_u + cost_e

                if new_dist < self.distances[v]:
                    self.distances[v] = new_dist
                    self.parent[v] = u
                    self.parent_edge[v] = edge.id
                    heapq.heappush(pq, (new_dist, v))
                    self.heap_operations += 1

        self.execution_time_us = (time.perf_counter() - t0) * 1e6

        path: List[int] = []
        if target_vid is not None and (found or self.distances[target_vid] < float('inf')):
            curr = target_vid
            while curr is not None:
                path.append(curr)
                curr = self.parent[curr]
            path.reverse()
            self.final_path_cost = self.distances[target_vid]
        else:
            self.final_path_cost = float('inf')

        return {
            "reachable": len(path) > 0 if target_vid is not None else True,
            "path": path,
            "cost": self.final_path_cost,
            "distances": self.distances,
            "stats": self.get_stats()
        }

    def checkpoint_aware_route(self, start_vid: int, waypoints: List[int], preset: RoutingPreset = RoutingPreset.BALANCED) -> Dict[str, object]:
        """Plans a continuous route visiting all waypoints in strict sequence:
        start_vid -> waypoints[0] -> waypoints[1] -> ... -> waypoints[-1]
        """
        full_path: List[int] = []
        total_cost: float = 0.0
        leg_stats: List[Dict[str, object]] = []

        current_node = start_vid
        for wp in waypoints:
            res = self.run(current_node, wp, preset=preset)
            if not res["reachable"]:
                return {
                    "reachable": False,
                    "path": [],
                    "cost": float('inf'),
                    "leg_stats": leg_stats
                }
            leg_path = res["path"]
            if not full_path:
                full_path.extend(leg_path)
            else:
                full_path.extend(leg_path[1:])  # Avoid duplicate boundary vertex
            total_cost += res["cost"]
            leg_stats.append(res["stats"])
            current_node = wp

        return {
            "reachable": True,
            "path": full_path,
            "cost": total_cost,
            "leg_stats": leg_stats
        }

    def step_generator(self, start_vid: int, target_vid: Optional[int] = None, preset: RoutingPreset = RoutingPreset.BALANCED) -> Generator[Dict[str, object], None, None]:
        """Step-by-step generator for Algorithm Lab visualizer."""
        self.distances = {vid: float('inf') for vid in self.graph.vertices}
        self.parent = {vid: None for vid in self.graph.vertices}
        self.visited = set()
        self.expanded_vertices = 0
        self.relaxed_edges = 0
        self.heap_operations = 0

        if start_vid not in self.graph.vertices:
            return

        self.distances[start_vid] = 0.0
        pq: List[Tuple[float, int]] = [(0.0, start_vid)]
        self.heap_operations += 1

        while pq:
            d_u, u = heapq.heappop(pq)
            self.heap_operations += 1

            if u in self.visited:
                continue

            self.visited.add(u)
            self.expanded_vertices += 1

            if target_vid is not None and u == target_vid:
                yield {
                    "current": u,
                    "visited": set(self.visited),
                    "distances": dict(self.distances),
                    "pq": list(pq),
                    "done": True,
                    "stats": self.get_stats()
                }
                return

            for v, edge in self.graph.get_neighbors(u, traversable_only=True):
                if v in self.visited:
                    continue

                cost_e = edge.compute_scalar_cost(preset)
                if cost_e == float('inf'):
                    continue

                self.relaxed_edges += 1
                new_dist = d_u + cost_e

                if new_dist < self.distances[v]:
                    self.distances[v] = new_dist
                    self.parent[v] = u
                    heapq.heappush(pq, (new_dist, v))
                    self.heap_operations += 1

            yield {
                "current": u,
                "visited": set(self.visited),
                "distances": dict(self.distances),
                "pq": list(pq),
                "done": False,
                "stats": self.get_stats()
            }

        yield {
            "current": None,
            "visited": set(self.visited),
            "distances": dict(self.distances),
            "pq": [],
            "done": True,
            "stats": self.get_stats()
        }

    def get_stats(self) -> Dict[str, object]:
        return {
            "expanded_vertices": self.expanded_vertices,
            "relaxed_edges": self.relaxed_edges,
            "heap_operations": self.heap_operations,
            "final_path_cost": round(self.final_path_cost, 4),
            "execution_time_us": round(self.execution_time_us, 2)
        }
