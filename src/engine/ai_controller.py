"""src/engine/ai_controller.py — Deterministic Computer Opponent AI (Section 4.4).
Implements the 3 mandatory deterministic AI strategies without random or machine learning.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from src.core.graph import Graph
from src.core.dijkstra import Dijkstra
from src.models.vehicle import Vehicle, AIStrategy
from src.models.circuit import Circuit
from src.models.edge import RoutingPreset
from src.engine.route_planner import RoutePlanner


class AIController:
    """Manages deterministic path decisions and recovery for computer racers."""

    def __init__(self, vehicle: Vehicle, circuit: Circuit, route_planner: RoutePlanner):
        self.vehicle = vehicle
        self.circuit = circuit
        self.graph = circuit.graph
        self.planner = route_planner
        self.dijkstra = Dijkstra(self.graph)
        
        # Planned path queue of vertex IDs
        self.planned_path: List[int] = []
        
        # Precomputed baseline route for Opponent 1 & 2
        self.baseline_route: List[int] = []
        self._init_baseline_route()

    def _init_baseline_route(self) -> None:
        """Precomputes standard circuit loop traversing all 10 checkpoints in order."""
        res = self.planner.plan_checkpoint_route(
            current_vid=self.circuit.start_vertex_id,
            remaining_checkpoints=self.circuit.checkpoint_ids,
            finish_vid=self.circuit.finish_vertex_id,
            preset=RoutingPreset.BALANCED
        )
        if res["reachable"]:
            self.baseline_route = res["path"]
            self.planned_path = list(self.baseline_route)

    def decide_next_target(self) -> Optional[int]:
        """Called when vehicle reaches currentVertex and needs to choose next targetVertex."""
        u = self.vehicle.currentVertex

        # Check refuelling priority: below 25% fuel (fuel < 25.0)
        if self.vehicle.fuel < 25.0:
            fuel_res = self.planner.find_nearest_reachable_fuel_station(u)
            if fuel_res is not None:
                st_id, st_path, _ = fuel_res
                if len(st_path) >= 2:
                    return st_path[1]

        # 1. Opponent 1: Fixed Main Route + Fixed Detour
        if self.vehicle.strategyType == AIStrategy.OPPONENT_1_FIXED:
            return self._decide_opponent_1(u)

        # 2. Opponent 2: Shortcut Hunter
        elif self.vehicle.strategyType == AIStrategy.OPPONENT_2_SHORTCUT:
            return self._decide_opponent_2(u)

        # 3. Opponent 3: Dynamic Minimum Distance
        elif self.vehicle.strategyType == AIStrategy.OPPONENT_3_OPTIMAL:
            return self._decide_opponent_3(u)

        # Fallback: first traversable outgoing edge
        out_edges = self.graph.get_outgoing_edges(u, traversable_only=True)
        return out_edges[0].to_vertex if out_edges else None

    def _decide_opponent_1(self, u: int) -> Optional[int]:
        """Opponent 1: Follows stored baseline route; on blockage, recomputes immediate detour."""
        # Find next vertex in planned_path
        if self.planned_path and self.planned_path[0] == u:
            self.planned_path.pop(0)

        if self.planned_path:
            nxt = self.planned_path[0]
            edge = self.graph.edge_between(u, nxt)
            if edge and edge.is_traversable:
                return nxt

        # If blocked or empty, recompute checkpoint-aware path from current checkpoint state
        remaining_cps = self._get_remaining_checkpoints()
        res = self.planner.plan_checkpoint_route(
            current_vid=u,
            remaining_checkpoints=remaining_cps,
            finish_vid=self.circuit.finish_vertex_id,
            preset=RoutingPreset.SAFETY  # Conservative prefers safer detour
        )
        if res["reachable"] and len(res["path"]) >= 2:
            self.planned_path = res["path"][1:]
            return self.planned_path[0]

        return None

    def _decide_opponent_2(self, u: int) -> Optional[int]:
        """Opponent 2: Aggressively uses shortcuts whenever open and legal."""
        # Check if an open shortcut originates at current vertex
        out_edges = self.graph.get_outgoing_edges(u, traversable_only=True)
        for e in out_edges:
            if e.isShortcut:
                return e.to_vertex

        # Otherwise follow remaining checkpoint route with Speed preset
        remaining_cps = self._get_remaining_checkpoints()
        res = self.planner.plan_checkpoint_route(
            current_vid=u,
            remaining_checkpoints=remaining_cps,
            finish_vid=self.circuit.finish_vertex_id,
            preset=RoutingPreset.SPEED
        )
        if res["reachable"] and len(res["path"]) >= 2:
            self.planned_path = res["path"][1:]
            return self.planned_path[0]

        return None

    def _decide_opponent_3(self, u: int) -> Optional[int]:
        """Opponent 3: Dynamic minimum total distance recomputation."""
        remaining_cps = self._get_remaining_checkpoints()
        res = self.planner.plan_checkpoint_route(
            current_vid=u,
            remaining_checkpoints=remaining_cps,
            finish_vid=self.circuit.finish_vertex_id,
            preset=RoutingPreset.BALANCED
        )
        if res["reachable"] and len(res["path"]) >= 2:
            self.planned_path = res["path"][1:]
            return self.planned_path[0]

        return None

    def _get_remaining_checkpoints(self) -> List[int]:
        """Returns list of checkpoint vertex IDs that must still be completed this lap."""
        next_order = self.vehicle.nextCheckpoint
        remaining = []
        for cp_id in self.circuit.checkpoint_ids:
            v = self.graph.get_vertex(cp_id)
            if v and v.checkpointOrder is not None and v.checkpointOrder >= next_order:
                remaining.append(cp_id)
        return remaining
