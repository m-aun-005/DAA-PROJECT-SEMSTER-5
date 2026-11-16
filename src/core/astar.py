"""src/core/astar.py — A* Heuristic Search Algorithm (Section 5.2).
Uses an admissible and consistent Euclidean lower-bound heuristic.
"""

from __future__ import annotations
import heapq
import math
import time
from typing import Dict, Generator, List, Optional, Set, Tuple
from src.core.graph import Graph
from src.models.edge import RoutingPreset


class AStar:
    """A* Shortest Path Search.
    
    Heuristic: h(u, goal) = Euclidean_distance(u, goal) * min_cost_per_distance_ratio
    Guarantees admissibility (never overestimates) and consistency.
    """

    def __init__(self, graph: Graph):
        self.graph = graph
        self.g_score: Dict[int, float] = {}  # Cost from start to node
        self.f_score: Dict[int, float] = {}  # Estimated total cost: g + h
        self.parent: Dict[int, Optional[int]] = {}
        self.visited: Set[int] = set()

        # Operation counters for empirical benchmarks (Experiment 2)
        self.expanded_vertices: int = 0
        self.relaxed_edges: int = 0
        self.heap_operations: int = 0
        self.execution_time_us: float = 0.0
        self.final_path_cost: float = float('inf')

    def _compute_min_cost_ratio(self, preset: RoutingPreset) -> float:
        """Finds minimum cost-per-distance ratio across all valid edges to ensure heuristic admissibility."""
        min_ratio = float('inf')
        for e in self.graph.edges.values():
            if e.is_traversable and e.distance > 0:
                cost = e.compute_scalar_cost(preset)
                ratio = cost / e.distance
                if ratio < min_ratio:
                    min_ratio = ratio
        return min_ratio if min_ratio < float('inf') else 0.0

    def heuristic(self, u_id: int, goal_id: int, min_ratio: float) -> float:
        """Admissible Euclidean lower bound on scalar cost."""
        u = self.graph.get_vertex(u_id)
        goal = self.graph.get_vertex(goal_id)
        if not u or not goal:
            return 0.0
        euclidean_dist = math.hypot(u.x - goal.x, u.y - goal.y)
        return euclidean_dist * min_ratio

    def run(self, start_vid: int, target_vid: int, preset: RoutingPreset = RoutingPreset.BALANCED) -> Dict[str, object]:
        """Runs A* search from start_vid to target_vid."""
        t0 = time.perf_counter()

        self.g_score = {vid: float('inf') for vid in self.graph.vertices}
        self.f_score = {vid: float('inf') for vid in self.graph.vertices}
        self.parent = {vid: None for vid in self.graph.vertices}
        self.visited = set()

        self.expanded_vertices = 0
        self.relaxed_edges = 0
        self.heap_operations = 0

        if start_vid not in self.graph.vertices or target_vid not in self.graph.vertices:
            self.execution_time_us = (time.perf_counter() - t0) * 1e6
            return {
                "reachable": False,
                "path": [],
                "cost": float('inf'),
                "stats": self.get_stats()
            }

        min_ratio = self._compute_min_cost_ratio(preset)
        self.g_score[start_vid] = 0.0
        self.f_score[start_vid] = self.heuristic(start_vid, target_vid, min_ratio)

        # Heap items: (f_score, g_score, vid)
        open_set: List[Tuple[float, float, int]] = [(self.f_score[start_vid], 0.0, start_vid)]
        self.heap_operations += 1

        found = False
        while open_set:
            f_u, g_u, u = heapq.heappop(open_set)
            self.heap_operations += 1

            if u in self.visited:
                continue

            self.visited.add(u)
            self.expanded_vertices += 1

            if u == target_vid:
                found = True
                break

            for v, edge in self.graph.get_neighbors(u, traversable_only=True):
                if v in self.visited:
                    continue

                cost_e = edge.compute_scalar_cost(preset)
                if cost_e == float('inf'):
                    continue

                self.relaxed_edges += 1
                tentative_g = g_u + cost_e

                if tentative_g < self.g_score[v]:
                    self.g_score[v] = tentative_g
                    h_v = self.heuristic(v, target_vid, min_ratio)
                    self.f_score[v] = tentative_g + h_v
                    self.parent[v] = u
                    heapq.heappush(open_set, (self.f_score[v], tentative_g, v))
                    self.heap_operations += 1

        self.execution_time_us = (time.perf_counter() - t0) * 1e6

        path: List[int] = []
        if found:
            curr = target_vid
            while curr is not None:
                path.append(curr)
                curr = self.parent[curr]
            path.reverse()
            self.final_path_cost = self.g_score[target_vid]
        else:
            self.final_path_cost = float('inf')

        return {
            "reachable": found,
            "path": path,
            "cost": self.final_path_cost,
            "stats": self.get_stats()
        }

    def checkpoint_aware_route(self, start_vid: int, waypoints: List[int], preset: RoutingPreset = RoutingPreset.BALANCED) -> Dict[str, object]:
        """Checkpoint-aware routing using A* across sequential legs."""
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
                full_path.extend(leg_path[1:])
            total_cost += res["cost"]
            leg_stats.append(res["stats"])
            current_node = wp

        return {
            "reachable": True,
            "path": full_path,
            "cost": total_cost,
            "leg_stats": leg_stats
        }

    def step_generator(self, start_vid: int, target_vid: int, preset: RoutingPreset = RoutingPreset.BALANCED) -> Generator[Dict[str, object], None, None]:
        """Step-by-step generator for Algorithm Lab visualizer."""
        self.g_score = {vid: float('inf') for vid in self.graph.vertices}
        self.f_score = {vid: float('inf') for vid in self.graph.vertices}
        self.parent = {vid: None for vid in self.graph.vertices}
        self.visited = set()
        self.expanded_vertices = 0
        self.relaxed_edges = 0
        self.heap_operations = 0

        if start_vid not in self.graph.vertices or target_vid not in self.graph.vertices:
            return

        min_ratio = self._compute_min_cost_ratio(preset)
        self.g_score[start_vid] = 0.0
        self.f_score[start_vid] = self.heuristic(start_vid, target_vid, min_ratio)

        open_set: List[Tuple[float, float, int]] = [(self.f_score[start_vid], 0.0, start_vid)]
        self.heap_operations += 1

        while open_set:
            f_u, g_u, u = heapq.heappop(open_set)
            self.heap_operations += 1

            if u in self.visited:
                continue

            self.visited.add(u)
            self.expanded_vertices += 1

            if u == target_vid:
                yield {
                    "current": u,
                    "visited": set(self.visited),
                    "g_score": dict(self.g_score),
                    "f_score": dict(self.f_score),
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
                tentative_g = g_u + cost_e

                if tentative_g < self.g_score[v]:
                    self.g_score[v] = tentative_g
                    h_v = self.heuristic(v, target_vid, min_ratio)
                    self.f_score[v] = tentative_g + h_v
                    self.parent[v] = u
                    heapq.heappush(open_set, (self.f_score[v], tentative_g, v))
                    self.heap_operations += 1

            yield {
                "current": u,
                "visited": set(self.visited),
                "g_score": dict(self.g_score),
                "f_score": dict(self.f_score),
                "done": False,
                "stats": self.get_stats()
            }

        yield {
            "current": None,
            "visited": set(self.visited),
            "g_score": dict(self.g_score),
            "f_score": dict(self.f_score),
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
