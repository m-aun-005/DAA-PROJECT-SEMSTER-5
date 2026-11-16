"""src/core/knapsack_dp.py — Resource Planning via Dynamic Programming (Section 5.3).
Implements both Problem A (0/1 Knapsack for Pickups) and Problem B (Refuelling DP).
"""

from __future__ import annotations
from dataclasses import dataclass
import time
from typing import Dict, List, Optional, Tuple


@dataclass
class KnapsackItem:
    """Represents an optional pickup item (nitro charge or boost)."""
    id: int
    name: str
    cost: int      # integer detour penalty (e.g. scaled fuel or detour seconds)
    benefit: int   # integer benefit value (e.g. time saved)


@dataclass
class FuelStationStop:
    """Represents a scheduled stop along a fixed route."""
    stop_index: int
    vertex_id: int
    name: str
    fuel_to_next: int    # fuel required to reach the next stop
    is_station: bool     # False for final destination


class KnapsackDP:
    """Problem A: 0/1 Knapsack Dynamic Programming with table reconstruction.
    
    Time Complexity: O(m * B)
    Space Complexity: O(m * B)
    """

    def __init__(self):
        self.table: List[List[int]] = []
        self.selected_items: List[KnapsackItem] = []
        self.total_benefit: int = 0
        self.table_entries_evaluated: int = 0
        self.execution_time_us: float = 0.0

    def solve(self, items: List[KnapsackItem], budget: int) -> Dict[str, object]:
        """Computes optimal selection of items within integer budget B."""
        t0 = time.perf_counter()
        m = len(items)
        B = max(0, budget)

        # Initialize DP table (m+1) x (B+1)
        self.table = [[0] * (B + 1) for _ in range(m + 1)]
        self.table_entries_evaluated = 0

        # Fill table
        for i in range(1, m + 1):
            item = items[i - 1]
            c_i = item.cost
            v_i = item.benefit
            for b in range(B + 1):
                self.table_entries_evaluated += 1
                if c_i > b:
                    self.table[i][b] = self.table[i - 1][b]
                else:
                    self.table[i][b] = max(
                        self.table[i - 1][b],
                        self.table[i - 1][b - c_i] + v_i
                    )

        self.total_benefit = self.table[m][B]

        # Backtrack to reconstruct optimal item subset
        self.selected_items = []
        curr_b = B
        for i in range(m, 0, -1):
            if self.table[i][curr_b] != self.table[i - 1][curr_b]:
                item = items[i - 1]
                self.selected_items.append(item)
                curr_b -= item.cost

        self.selected_items.reverse()
        self.execution_time_us = (time.perf_counter() - t0) * 1e6

        return {
            "total_benefit": self.total_benefit,
            "selected_items": self.selected_items,
            "total_cost": sum(it.cost for it in self.selected_items),
            "table_entries_evaluated": self.table_entries_evaluated,
            "execution_time_us": round(self.execution_time_us, 2),
            "dp_table": self.table
        }


class RefuelDP:
    """Problem B: Optimal Refuelling Plan Dynamic Programming.
    
    State: dp[j][f] = minimum additional pit-stop delay on arrival at stop j with f fuel.
    Capacity C (default 100). Purchase bound 0 <= a <= min(C - f, max_purchase).
    Time Complexity: O(m * C^2)
    """

    def __init__(self, capacity: int = 100, max_purchase: int = 40, fixed_stop_time: float = 3.0):
        self.capacity = capacity
        self.max_purchase = max_purchase
        self.fixed_stop_time = fixed_stop_time
        self.table_entries_evaluated: int = 0
        self.execution_time_us: float = 0.0

    def solve(self, stops: List[FuelStationStop], initial_fuel: int) -> Dict[str, object]:
        """Calculates optimal refuelling decisions for each fuel station along a fixed route."""
        t0 = time.perf_counter()
        m = len(stops)
        C = self.capacity
        self.table_entries_evaluated = 0

        # dp[j][f] = min total pit time to reach destination from stop j with f fuel
        # Backward dynamic programming: from destination back to start
        dp: List[Dict[int, float]] = [{} for _ in range(m)]
        decision: List[Dict[int, int]] = [{} for _ in range(m)]

        # Base case: At final stop (destination, index m-1), delay is 0.0 for any non-negative fuel
        for f in range(C + 1):
            dp[m - 1][f] = 0.0

        # Backward transitions
        for j in range(m - 2, -1, -1):
            stop = stops[j]
            d_j = stop.fuel_to_next

            for f in range(C + 1):
                best_cost = float('inf')
                best_a = 0

                # If this stop is a fuel station, consider purchases a in [0, min(C-f, max_purchase)]
                max_a = min(C - f, self.max_purchase) if stop.is_station else 0
                for a in range(max_a + 1):
                    self.table_entries_evaluated += 1
                    fuel_after = f + a
                    if fuel_after >= d_j:
                        fuel_next = fuel_after - d_j
                        if fuel_next in dp[j + 1]:
                            pit_delay = self.fixed_stop_time if a > 0 else 0.0
                            total_cost = pit_delay + dp[j + 1][fuel_next]
                            if total_cost < best_cost:
                                best_cost = total_cost
                                best_a = a

                if best_cost < float('inf'):
                    dp[j][f] = best_cost
                    decision[j][f] = best_a

        self.execution_time_us = (time.perf_counter() - t0) * 1e6

        # Forward trace starting with initial_fuel
        feasible = initial_fuel in dp[0] and dp[0][initial_fuel] < float('inf')
        plan: List[Dict[str, object]] = []

        if feasible:
            curr_f = initial_fuel
            for j in range(m - 1):
                a = decision[j][curr_f]
                plan.append({
                    "stop_index": j,
                    "vertex_id": stops[j].vertex_id,
                    "name": stops[j].name,
                    "fuel_on_arrival": curr_f,
                    "fuel_purchased": a,
                    "fuel_after_purchase": curr_f + a,
                    "pit_delay": self.fixed_stop_time if a > 0 else 0.0
                })
                curr_f = curr_f + a - stops[j].fuel_to_next

        return {
            "feasible": feasible,
            "total_pit_delay": dp[0].get(initial_fuel, float('inf')) if feasible else float('inf'),
            "plan": plan,
            "table_entries_evaluated": self.table_entries_evaluated,
            "execution_time_us": round(self.execution_time_us, 2)
        }
