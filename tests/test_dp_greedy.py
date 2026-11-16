"""tests/test_dp_greedy.py — Unit tests for DP vs Greedy (Act 3).
"""

import pytest
from src.core.knapsack_dp import KnapsackDP, RefuelDP, KnapsackItem, FuelStationStop
from src.core.greedy import GreedyPlanner


def test_knapsack_dp_optimal():
    dp = KnapsackDP()
    # Case: items A(6, 30), B(5, 24), C(5, 24), Budget 10
    items = [
        KnapsackItem(1, "A", 6, 30),
        KnapsackItem(2, "B", 5, 24),
        KnapsackItem(3, "C", 5, 24)
    ]
    res = dp.solve(items, budget=10)
    assert res["total_benefit"] == 48
    selected_ids = {it.id for it in res["selected_items"]}
    assert selected_ids == {2, 3}


def test_greedy_suboptimal_counterexample():
    greedy = GreedyPlanner()
    items = [
        KnapsackItem(1, "A", 6, 30),  # Ratio 5.0
        KnapsackItem(2, "B", 5, 24),  # Ratio 4.8
        KnapsackItem(3, "C", 5, 24)   # Ratio 4.8
    ]
    res = greedy.solve(items, budget=10)
    # Greedy picks A (cost 6, benefit 30), then stops
    assert res["total_benefit"] == 30
    assert len(res["selected_items"]) == 1
    assert res["selected_items"][0].id == 1


def test_refuel_dp():
    rdp = RefuelDP(capacity=100, max_purchase=40, fixed_stop_time=3.0)
    stops = [
        FuelStationStop(0, 10, "Gas1", fuel_to_next=50, is_station=True),
        FuelStationStop(1, 11, "Gas2", fuel_to_next=40, is_station=True),
        FuelStationStop(2, 12, "Finish", fuel_to_next=0, is_station=False)
    ]
    # Starts with 60 fuel -> reaches Gas2 with 10 fuel -> purchases 40 -> reaches finish
    res = rdp.solve(stops, initial_fuel=60)
    assert res["feasible"] is True
    assert res["total_pit_delay"] >= 3.0
