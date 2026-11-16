"""src/core/bfs.py — Breadth-First Search (Section 5.1).
Guarantees unweighted minimum-edge-count path.
"""

from __future__ import annotations
from collections import deque
import time
from typing import Dict, Generator, List, Optional, Set, Tuple
from src.core.graph import Graph


class BFS:
    """Breadth-First Search implementation.
    
    Time Complexity: O(V + E)
    Auxiliary Space: O(V)
    Provides both batch execution and step-by-step generator for Algorithm Lab.
    """

    def __init__(self, graph: Graph):
        self.graph = graph
        self.visited: Set[int] = set()
        self.parent: Dict[int, Optional[int]] = {}
        self.distances: Dict[int, int] = {}  # hop count from source
        self.traversal_order: List[int] = []
        self.queue: deque[int] = deque()
        
        # Operation counters for empirical benchmarks
        self.vertices_visited: int = 0
        self.edges_examined: int = 0
        self.execution_time_us: float = 0.0

    def run(self, start_vid: int, target_vid: Optional[int] = None) -> Dict[str, object]:
        """Executes complete BFS from start_vid to target_vid (or whole component if None)."""
        t0 = time.perf_counter()
        
        self.visited.clear()
        self.parent.clear()
        self.distances.clear()
        self.traversal_order.clear()
        self.queue.clear()
        self.vertices_visited = 0
        self.edges_examined = 0

        if start_vid not in self.graph.vertices:
            self.execution_time_us = (time.perf_counter() - t0) * 1e6
            return {
                "reachable": False,
                "path": [],
                "hop_count": -1,
                "traversal_order": [],
                "stats": self.get_stats()
            }

        self.visited.add(start_vid)
        self.parent[start_vid] = None
        self.distances[start_vid] = 0
        self.queue.append(start_vid)
        self.vertices_visited = 1

        found = False
        while self.queue:
            u = self.queue.popleft()
            self.traversal_order.append(u)

            if target_vid is not None and u == target_vid:
                found = True
                break

            for v, edge in self.graph.get_neighbors(u, traversable_only=True):
                self.edges_examined += 1
                if v not in self.visited:
                    self.visited.add(v)
                    self.parent[v] = u
                    self.distances[v] = self.distances[u] + 1
                    self.queue.append(v)
                    self.vertices_visited += 1

        self.execution_time_us = (time.perf_counter() - t0) * 1e6

        path = []
        if target_vid is not None and (found or target_vid in self.visited):
            curr = target_vid
            while curr is not None:
                path.append(curr)
                curr = self.parent.get(curr)
            path.reverse()

        return {
            "reachable": (target_vid in self.visited) if target_vid is not None else True,
            "path": path,
            "hop_count": len(path) - 1 if path else -1,
            "traversal_order": self.traversal_order,
            "stats": self.get_stats()
        }

    def step_generator(self, start_vid: int, target_vid: Optional[int] = None) -> Generator[Dict[str, object], None, None]:
        """Step-by-step generator for the Algorithm Lab visualization."""
        self.visited.clear()
        self.parent.clear()
        self.distances.clear()
        self.traversal_order.clear()
        self.queue.clear()
        self.vertices_visited = 0
        self.edges_examined = 0

        if start_vid not in self.graph.vertices:
            return

        self.visited.add(start_vid)
        self.parent[start_vid] = None
        self.distances[start_vid] = 0
        self.queue.append(start_vid)
        self.vertices_visited = 1

        yield {
            "current": start_vid,
            "queue": list(self.queue),
            "visited": set(self.visited),
            "parent": dict(self.parent),
            "done": False,
            "stats": self.get_stats()
        }

        while self.queue:
            u = self.queue.popleft()
            self.traversal_order.append(u)

            if target_vid is not None and u == target_vid:
                yield {
                    "current": u,
                    "queue": list(self.queue),
                    "visited": set(self.visited),
                    "parent": dict(self.parent),
                    "done": True,
                    "stats": self.get_stats()
                }
                return

            for v, edge in self.graph.get_neighbors(u, traversable_only=True):
                self.edges_examined += 1
                if v not in self.visited:
                    self.visited.add(v)
                    self.parent[v] = u
                    self.distances[v] = self.distances[u] + 1
                    self.queue.append(v)
                    self.vertices_visited += 1

            yield {
                "current": u,
                "queue": list(self.queue),
                "visited": set(self.visited),
                "parent": dict(self.parent),
                "done": False,
                "stats": self.get_stats()
            }

        yield {
            "current": None,
            "queue": [],
            "visited": set(self.visited),
            "parent": dict(self.parent),
            "done": True,
            "stats": self.get_stats()
        }

    def get_stats(self) -> Dict[str, object]:
        return {
            "vertices_visited": self.vertices_visited,
            "edges_examined": self.edges_examined,
            "execution_time_us": round(self.execution_time_us, 2)
        }
