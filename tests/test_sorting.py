"""tests/test_sorting.py — Unit tests for Sorting Suite and Top-k Priority Queue (Act 5).
"""

import pytest
from src.core.sorting import MergeSort, QuickSort3Way, HeapSortAlgo, TopKHeap
from src.models.leaderboard import ChampionshipEntry


def test_sorting_algorithms_agree():
    ms = MergeSort()
    qs = QuickSort3Way()
    hs = HeapSortAlgo()
    topk = TopKHeap()

    # Create test entries with duplicate points to test tie-breaking
    entries = [
        ChampionshipEntry(racerId=1, name="A", totalPoints=25, wins=1, sumOfFinishPositions=5, bestFastestLap=40.0),
        ChampionshipEntry(racerId=2, name="B", totalPoints=25, wins=1, sumOfFinishPositions=5, bestFastestLap=39.5),  # B has better lap
        ChampionshipEntry(racerId=3, name="C", totalPoints=30, wins=1, sumOfFinishPositions=4, bestFastestLap=41.0),  # C has more points
        ChampionshipEntry(racerId=4, name="D", totalPoints=10, wins=0, sumOfFinishPositions=10, bestFastestLap=42.0),
    ]

    key_fn = lambda e: e.sort_key()

    res_m = ms.sort(entries, key=key_fn)
    res_q = qs.sort(entries, key=key_fn)
    res_h = hs.sort(entries, key=key_fn)
    res_k3 = topk.get_top_k(entries, k=3, key=key_fn)

    ids_m = [e.racerId for e in res_m]
    ids_q = [e.racerId for e in res_q]
    ids_h = [e.racerId for e in res_h]
    ids_k3 = [e.racerId for e in res_k3]

    # C is 1st (30 pts), B is 2nd (25 pts, better lap 39.5), A is 3rd (25 pts, lap 40.0), D is 4th
    assert ids_m == [3, 2, 1, 4]
    assert ids_q == [3, 2, 1, 4]
    assert ids_h == [3, 2, 1, 4]
    assert ids_k3 == [3, 2, 1]
