"""src/engine/route_planner.py — Checkpoint-Aware Route Planner & Dynamic Replanner.
Satisfies Section 5.2.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from src.core.graph import Graph
from src.core.dijkstra import Dijkstra
from src.core.astar import AStar
from src.models.edge import RoutingPreset
from src.models.vertex import VertexType


class RoutePlanner:
    """Manages pathfinding and dynamic replanning for racers."""

    def __init__(self, graph: Graph):
        self.graph = graph
        self.dijkstra = Dijkstra(graph)
        self.astar = AStar(graph)

    def plan_checkpoint_route(
        self,
        current_vid: int,
        remaining_checkpoints: List[int],
        finish_vid: int,
        preset: RoutingPreset = RoutingPreset.BALANCED,
        use_astar: bool = True
    ) -> Dict[str, object]:
        """Plans complete route visiting all remaining mandatory checkpoints in order,
        then proceeding to the finish line.
        """
        waypoints = list(remaining_checkpoints) + [finish_vid]
        full_path: List[int] = []
        total_cost: float = 0.0

        curr = current_vid
        for wp in waypoints:
            if curr == wp:
                continue
            if use_astar:
                res = self.astar.run(curr, wp, preset=preset)
            else:
                res = self.dijkstra.run(curr, wp, preset=preset)

            if not res["reachable"] or not res["path"]:
                return {
                    "reachable": False,
                    "path": [],
                    "cost": float('inf')
                }

            leg = res["path"]
            if not full_path:
                full_path.extend(leg)
            else:
                full_path.extend(leg[1:])
            total_cost += res["cost"]
            curr = wp

        return {
            "reachable": True,
            "path": full_path,
            "cost": total_cost
        }

    def find_nearest_reachable_fuel_station(
        self,
        current_vid: int,
        preset: RoutingPreset = RoutingPreset.ECONOMY
    ) -> Optional[Tuple[int, List[int], float]]:
        """Finds the nearest active fuel station reachable from current_vid."""
        stations = [v for v in self.graph.get_fuel_stations() if v.active]
        if not stations:
            return None

        best_station: Optional[int] = None
        best_path: List[int] = []
        best_cost = float('inf')

        for st in stations:
            res = self.dijkstra.run(current_vid, st.id, preset=preset)
            if res["reachable"] and res["cost"] < best_cost:
                best_cost = res["cost"]
                best_station = st.id
                best_path = res["path"]

        if best_station is not None:
            return best_station, best_path, best_cost
        return None
