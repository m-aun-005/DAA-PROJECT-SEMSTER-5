"""src/core/dfs.py — Depth-First Search (Section 5.1).
Supports traversal, cycle detection, connected components, dead-end analysis,
and bounded alternative route enumeration.
"""

from __future__ import annotations
import time
from typing import Dict, Generator, List, Optional, Set, Tuple
from src.core.graph import Graph


class DFS:
    """Depth-First Search implementation.
    
    Time Complexity: O(V + E) for standard traversal.
    Auxiliary Space: O(V)
    Provides cycle detection, connected components, dead-end discovery,
    and bounded alternative-path search.
    """

    def __init__(self, graph: Graph):
        self.graph = graph
        self.visited: Set[int] = set()
        self.traversal_order: List[int] = []
        self.parent: Dict[int, Optional[int]] = {}
        
        # Operation counters
        self.vertices_visited: int = 0
        self.edges_examined: int = 0
        self.execution_time_us: float = 0.0

    def run(self, start_vid: int) -> Dict[str, object]:
        """Standard DFS traversal from start_vid."""
        t0 = time.perf_counter()
        self.visited.clear()
        self.traversal_order.clear()
        self.parent.clear()
        self.vertices_visited = 0
        self.edges_examined = 0

        if start_vid in self.graph.vertices:
            self._dfs_visit(start_vid, None)

        self.execution_time_us = (time.perf_counter() - t0) * 1e6
        return {
            "traversal_order": self.traversal_order,
            "visited_count": self.vertices_visited,
            "stats": self.get_stats()
        }

    def _dfs_visit(self, u: int, p: Optional[int]) -> None:
        self.visited.add(u)
        self.parent[u] = p
        self.traversal_order.append(u)
        self.vertices_visited += 1

        for v, edge in self.graph.get_neighbors(u, traversable_only=True):
            self.edges_examined += 1
            if v not in self.visited:
                self._dfs_visit(v, u)

    def detect_cycles(self) -> List[List[int]]:
        """Detects directed/undirected cycles using 3-color state tracking (WHITE=0, GRAY=1, BLACK=2).
        Returns list of cycle paths found.
        """
        color: Dict[int, int] = {vid: 0 for vid in self.graph.vertices}
        cycle_parent: Dict[int, Optional[int]] = {vid: None for vid in self.graph.vertices}
        cycles: List[List[int]] = []

        def dfs_cycle(u: int, p: Optional[int]):
            color[u] = 1  # Gray: currently visiting
            for v, edge in self.graph.get_neighbors(u, traversable_only=True):
                # For undirected edges, ignore immediate parent
                if not edge.directed and v == p:
                    continue
                if color[v] == 1:
                    # Back edge detected -> cycle found!
                    cycle = [v, u]
                    curr = u
                    while curr != v and curr is not None:
                        curr = cycle_parent[curr]
                        if curr is not None:
                            cycle.append(curr)
                    cycles.append(cycle)
                elif color[v] == 0:
                    cycle_parent[v] = u
                    dfs_cycle(v, u)
            color[u] = 2  # Black: finished

        for vid in self.graph.vertices:
            if color[vid] == 0:
                dfs_cycle(vid, None)

        return cycles

    def find_connected_components(self) -> List[List[int]]:
        """Computes all connected components of the graph."""
        visited: Set[int] = set()
        components: List[List[int]] = []

        for vid in self.graph.vertices:
            if vid not in visited:
                comp: List[int] = []
                stack = [vid]
                visited.add(vid)
                while stack:
                    u = stack.pop()
                    comp.append(u)
                    for v, _ in self.graph.get_neighbors(u, traversable_only=True):
                        if v not in visited:
                            visited.add(v)
                            stack.append(v)
                components.append(comp)

        return components

    def find_dead_ends(self, finish_vid: int) -> List[int]:
        """Finds dead-end vertices.
        A dead end is defined in Section 5.1 as:
        A non-mandatory vertex from which the finish cannot be reached without reversing.
        """
        # Determine all vertices that CAN reach the finish line via traversable edges
        # We search backwards from finish using graph.in_adj
        can_reach_finish: Set[int] = set()
        queue = [finish_vid]
        can_reach_finish.add(finish_vid)

        while queue:
            curr = queue.pop(0)
            for e in self.graph.in_adj.get(curr, []):
                if self.graph.edges[e.id].is_traversable:
                    u = e.from_vertex
                    if u not in can_reach_finish:
                        can_reach_finish.add(u)
                        queue.append(u)

        dead_ends: List[int] = []
        for vid, v in self.graph.vertices.items():
            if not v.is_mandatory_checkpoint() and v.id != finish_vid:
                if vid not in can_reach_finish:
                    dead_ends.append(vid)

        return dead_ends

    def find_bounded_paths(self, start: int, target: int, max_depth: int = 15, max_paths: int = 5) -> List[List[int]]:
        """Finds up to max_paths alternative simple paths from start to target bounded by max_depth.
        Guarantees avoidance of worst-case exponential state explosion.
        """
        paths: List[List[int]] = []
        current_path = [start]
        visited_in_path = {start}

        def backtrack(u: int):
            if len(paths) >= max_paths:
                return
            if u == target:
                paths.append(list(current_path))
                return
            if len(current_path) >= max_depth:
                return

            for v, edge in self.graph.get_neighbors(u, traversable_only=True):
                if v not in visited_in_path:
                    visited_in_path.add(v)
                    current_path.append(v)
                    backtrack(v)
                    current_path.pop()
                    visited_in_path.remove(v)

        backtrack(start)
        return paths

    def step_generator(self, start_vid: int) -> Generator[Dict[str, object], None, None]:
        """Interactive step-by-step generator for the Algorithm Lab visualization."""
        self.visited.clear()
        self.traversal_order.clear()
        self.vertices_visited = 0
        self.edges_examined = 0

        stack: List[Tuple[int, Optional[int]]] = [(start_vid, None)]

        while stack:
            u, p = stack.pop()
            if u not in self.visited:
                self.visited.add(u)
                self.traversal_order.append(u)
                self.vertices_visited += 1

                for v, edge in reversed(self.graph.get_neighbors(u, traversable_only=True)):
                    self.edges_examined += 1
                    if v not in self.visited:
                        stack.append((v, u))

                yield {
                    "current": u,
                    "stack": [node for node, _ in stack],
                    "visited": set(self.visited),
                    "done": False,
                    "stats": self.get_stats()
                }

        yield {
            "current": None,
            "stack": [],
            "visited": set(self.visited),
            "done": True,
            "stats": self.get_stats()
        }

    def get_stats(self) -> Dict[str, object]:
        return {
            "vertices_visited": self.vertices_visited,
            "edges_examined": self.edges_examined,
            "execution_time_us": round(self.execution_time_us, 2)
        }
