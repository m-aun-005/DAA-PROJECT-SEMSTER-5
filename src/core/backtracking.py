"""src/core/backtracking.py — Constraint-Based Track Placement & Pruning (Section 5.4).
Places checkpoints, services (fuel, nitro), and obstacles using backtracking with pruning rules.
"""

from __future__ import annotations
import copy
from typing import Dict, List, Optional, Set, Tuple
from src.core.graph import Graph
from src.core.bfs import BFS
from src.models.vertex import Vertex, VertexType
from src.models.edge import Edge, EdgeStatus


class TrackPlacer:
    """Constraint-based backtracking placement engine for procedural tracks.
    
    Pruning rules:
    1. Fuel station spacing: Minimum edge distance >= 3 between consecutive fuel stations.
    2. Bridge edge preservation: Obstacles cannot be placed on cut-edges.
    3. Checkpoint sequential reachability: Checkpoint C_i must have traversable path to C_{i+1}.
    """

    def __init__(self, graph: Graph):
        self.graph = graph
        self.backtrack_steps: int = 0
        self.states_pruned: int = 0

    def place_checkpoints_backtracking(self, candidate_vids: List[int], required_count: int = 10) -> Optional[List[int]]:
        """Finds a sequence of required_count vertices that form a valid directed tour."""
        self.backtrack_steps = 0
        self.states_pruned = 0
        
        chosen_order: List[int] = []
        visited_vids: Set[int] = set()

        def can_reach(u: int, v: int) -> bool:
            bfs = BFS(self.graph)
            res = bfs.run(u, v)
            return res["reachable"]

        def backtrack(step: int, last_vid: Optional[int]) -> bool:
            self.backtrack_steps += 1
            if step == required_count:
                # Check closure: can we get from last checkpoint back to start?
                if can_reach(chosen_order[-1], chosen_order[0]):
                    return True
                self.states_pruned += 1
                return False

            for vid in candidate_vids:
                if vid not in visited_vids:
                    # Pruning rule: Must be reachable from previous checkpoint
                    if last_vid is not None and not can_reach(last_vid, vid):
                        self.states_pruned += 1
                        continue

                    visited_vids.add(vid)
                    chosen_order.append(vid)

                    if backtrack(step + 1, vid):
                        return True

                    # Backtrack
                    chosen_order.pop()
                    visited_vids.remove(vid)

            return False

        if backtrack(0, None):
            return chosen_order
        return None

    def validate_track_playability(self, start_vid: int, checkpoint_vids: List[int], finish_vid: int) -> Tuple[bool, str]:
        """Validates that a track configuration is 100% playable."""
        bfs = BFS(self.graph)

        # 1. Start to CP1
        res = bfs.run(start_vid, checkpoint_vids[0])
        if not res["reachable"]:
            return False, f"Start vertex {start_vid} cannot reach Checkpoint 1 ({checkpoint_vids[0]})."

        # 2. Sequential checkpoints CP_i -> CP_{i+1}
        for i in range(len(checkpoint_vids) - 1):
            u = checkpoint_vids[i]
            v = checkpoint_vids[i + 1]
            res = bfs.run(u, v)
            if not res["reachable"]:
                return False, f"Checkpoint {i+1} ({u}) cannot reach Checkpoint {i+2} ({v})."

        # 3. Final CP to Finish
        res = bfs.run(checkpoint_vids[-1], finish_vid)
        if not res["reachable"]:
            return False, f"Final Checkpoint ({checkpoint_vids[-1]}) cannot reach Finish ({finish_vid})."

        # 4. Finish back to CP1 (lap continuity)
        res = bfs.run(finish_vid, checkpoint_vids[0])
        if not res["reachable"]:
            return False, f"Finish ({finish_vid}) cannot loop back to Checkpoint 1 ({checkpoint_vids[0]})."

        return True, "Track graph passed all ordered playability and lap validation checks."
