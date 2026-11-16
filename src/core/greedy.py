"""src/core/greedy.py — Greedy Heuristic & Suboptimality Benchmarking (Section 5.3).
Provides ratio-based knapsack selection, deterministic tie-breaking,
and formal counterexamples proving suboptimality against Dynamic Programming.
"""

from __future__ import annotations
import time
from typing import Dict, List, Tuple
from src.core.knapsack_dp import KnapsackItem


class GreedyPlanner:
    """Greedy heuristic for resource and pickup planning.
    
    Sorts items by benefit/cost ratio (v_i / c_i) descending.
    Processes zero-cost positive-benefit items first.
    Breaks equal ratio ties deterministically by lower item ID.
    Time Complexity: O(m log m)
    """

    def __init__(self):
        self.selected_items: List[KnapsackItem] = []
        self.total_benefit: int = 0
        self.execution_time_us: float = 0.0

    def solve(self, items: List[KnapsackItem], budget: int) -> Dict[str, object]:
        """Runs greedy ratio selection."""
        t0 = time.perf_counter()
        
        self.selected_items = []
        self.total_benefit = 0
        remaining_budget = max(0, budget)

        # 1. Process zero-cost items
        zero_cost = [it for it in items if it.cost == 0 and it.benefit > 0]
        zero_cost.sort(key=lambda it: it.id)
        for it in zero_cost:
            self.selected_items.append(it)
            self.total_benefit += it.benefit

        # 2. Sort positive-cost items by ratio v_i / c_i descending, then by lower ID
        positive_cost = [it for it in items if it.cost > 0]
        positive_cost.sort(key=lambda it: (-(it.benefit / it.cost), it.id))

        # 3. Greedy packing
        for it in positive_cost:
            if it.cost <= remaining_budget:
                self.selected_items.append(it)
                self.total_benefit += it.benefit
                remaining_budget -= it.cost

        self.execution_time_us = (time.perf_counter() - t0) * 1e6

        return {
            "total_benefit": self.total_benefit,
            "selected_items": self.selected_items,
            "total_cost": sum(it.cost for it in self.selected_items),
            "remaining_budget": remaining_budget,
            "execution_time_us": round(self.execution_time_us, 2)
        }

    @staticmethod
    def get_documented_counterexamples() -> List[Dict[str, object]]:
        """Returns the three documented counterexamples demonstrating greedy suboptimality:
        1. Spec example (Items A, B, C; Budget 10; Greedy=30, DP=48)
        2. Counterexample 2: Heavy high-ratio trap (Greedy=100, DP=140)
        3. Counterexample 3: Fractional dilemma (Greedy=60, DP=90)
        """
        cases = [
            {
                "name": "Specification Benchmark Example",
                "budget": 10,
                "items": [
                    KnapsackItem(id=1, name="Item A (Nitro)", cost=6, benefit=30),  # ratio 5.0
                    KnapsackItem(id=2, name="Item B (Boost)", cost=5, benefit=24),  # ratio 4.8
                    KnapsackItem(id=3, name="Item C (Super)", cost=5, benefit=24),  # ratio 4.8
                ],
                "expected_greedy_benefit": 30,
                "expected_dp_benefit": 48,
                "suboptimality_gap_pct": 37.5
            },
            {
                "name": "Team Counterexample 2: High-Ratio Capacity Blocker",
                "budget": 12,
                "items": [
                    KnapsackItem(id=1, name="Trap High Ratio", cost=7, benefit=42),  # ratio 6.0
                    KnapsackItem(id=2, name="Solid Dual 1",     cost=6, benefit=33),  # ratio 5.5
                    KnapsackItem(id=3, name="Solid Dual 2",     cost=6, benefit=33),  # ratio 5.5
                ],
                "expected_greedy_benefit": 42,
                "expected_dp_benefit": 66,
                "suboptimality_gap_pct": 36.36
            },
            {
                "name": "Team Counterexample 3: Multi-Item Detour Aggregation",
                "budget": 15,
                "items": [
                    KnapsackItem(id=1, name="Nitro Pack X", cost=8, benefit=56),   # ratio 7.0
                    KnapsackItem(id=2, name="Nitro Pack Y", cost=5, benefit=33),   # ratio 6.6
                    KnapsackItem(id=3, name="Nitro Pack Z", cost=5, benefit=33),   # ratio 6.6
                    KnapsackItem(id=4, name="Nitro Pack W", cost=5, benefit=33),   # ratio 6.6
                ],
                "expected_greedy_benefit": 56 + 33,  # 89 (takes X and Y, 2 budget left, cannot fit Z or W)
                "expected_dp_benefit": 99,           # takes Y, Z, W (cost 15, benefit 99)
                "suboptimality_gap_pct": 10.1
            }
        ]
        return cases

    @staticmethod
    def brute_force_knapsack(items: List[KnapsackItem], budget: int) -> Tuple[int, List[KnapsackItem]]:
        """Exhaustive O(2^N) search for correctness validation on small instances."""
        n = len(items)
        best_val = 0
        best_subset: List[KnapsackItem] = []

        for mask in range(1 << n):
            cost = 0
            val = 0
            subset = []
            for i in range(n):
                if (mask >> i) & 1:
                    cost += items[i].cost
                    val += items[i].benefit
                    subset.append(items[i])
            if cost <= budget and val > best_val:
                best_val = val
                best_subset = subset

        return best_val, best_subset
