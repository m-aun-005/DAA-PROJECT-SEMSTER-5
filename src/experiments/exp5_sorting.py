"""src/experiments/exp5_sorting.py — Experiment 5: Sorting Suite & Top-k Retrieval (Section 7).
Compares Merge Sort, Quick Sort (3-Way), Heap Sort, and Size-k Priority Queue
across Random, Sorted, Reverse, and Duplicate-heavy input distributions.
"""

import csv
import os
import random
import time
from typing import Dict, List
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.core.sorting import MergeSort, QuickSort3Way, HeapSortAlgo, TopKHeap
from src.models.leaderboard import ChampionshipEntry


def run_experiment_5(output_dir: str = "src/experiments/results") -> List[Dict]:
    os.makedirs(output_dir, exist_ok=True)
    sizes = [10, 100, 500, 1000, 5000, 10000, 25000]
    distributions = ["RANDOM", "SORTED", "REVERSE", "DUPLICATE_HEAVY"]
    records = []

    ms = MergeSort()
    qs = QuickSort3Way()
    hs = HeapSortAlgo()
    topk = TopKHeap()

    print("[EXP 5] Running Sorting Suite & Top-k Benchmarking...")

    for n in sizes:
        for dist in distributions:
            # Generate championship entry dataset
            raw_entries = []
            for i in range(1, n + 1):
                if dist == "RANDOM":
                    pts = random.randint(0, 500)
                    wins = random.randint(0, 10)
                elif dist == "SORTED":
                    pts = i * 10
                    wins = i // 10
                elif dist == "REVERSE":
                    pts = (n - i) * 10
                    wins = (n - i) // 10
                elif dist == "DUPLICATE_HEAVY":
                    pts = random.choice([50, 100, 150])  # Only 3 unique point tiers
                    wins = random.choice([1, 2])

                entry = ChampionshipEntry(
                    racerId=i,
                    name=f"Racer_{i}",
                    totalPoints=pts,
                    wins=wins,
                    sumOfFinishPositions=random.randint(5, 50),
                    bestFastestLap=round(random.uniform(30.0, 60.0), 2)
                )
                raw_entries.append(entry)

            key_fn = lambda e: e.sort_key()

            # Merge Sort
            res_m = ms.sort(raw_entries, key=key_fn)
            m_time = ms.execution_time_ms
            m_cmp = ms.comparisons

            # Quick Sort (3-Way)
            res_q = qs.sort(raw_entries, key=key_fn)
            q_time = qs.execution_time_ms
            q_cmp = qs.comparisons

            # Heap Sort
            res_h = hs.sort(raw_entries, key=key_fn)
            h_time = hs.execution_time_ms
            h_cmp = hs.comparisons

            # Top-3 Heap
            res_k3 = topk.get_top_k(raw_entries, k=3, key=key_fn)
            k3_time = topk.execution_time_ms
            k3_cmp = topk.comparisons

            # Verify identical ranking order across all sorts
            all_agree = (
                [e.racerId for e in res_m] == [e.racerId for e in res_q] == [e.racerId for e in res_h]
            )
            top3_agree = (
                [e.racerId for e in res_k3] == [e.racerId for e in res_m[:3]]
            )

            rec = {
                "N": n,
                "distribution": dist,
                "merge_time_ms": round(m_time, 2),
                "quick_time_ms": round(q_time, 2),
                "heap_time_ms": round(h_time, 2),
                "top3_heap_time_ms": round(k3_time, 2),
                "merge_comparisons": m_cmp,
                "quick_comparisons": q_cmp,
                "heap_comparisons": h_cmp,
                "top3_comparisons": k3_cmp,
                "all_sorts_match": all_agree,
                "top3_matches_full_sort": top3_agree
            }
            records.append(rec)

        print(f"  N={n:<6} | Merge: {rec['merge_time_ms']:>6.2f} ms | Quick: {rec['quick_time_ms']:>6.2f} ms | Heap: {rec['heap_time_ms']:>6.2f} ms | Top-3: {rec['top3_heap_time_ms']:>5.2f} ms")

    # Save to CSV
    csv_path = os.path.join(output_dir, "exp5_sorting.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    # Plot (Black & White style for Random distribution)
    random_records = [r for r in records if r["distribution"] == "RANDOM"]
    plt.figure(figsize=(7, 4.5))
    n_vals = [r["N"] for r in random_records]
    m_t = [r["merge_time_ms"] for r in random_records]
    q_t = [r["quick_time_ms"] for r in random_records]
    h_t = [r["heap_time_ms"] for r in random_records]
    k_t = [r["top3_heap_time_ms"] for r in random_records]

    plt.plot(n_vals, m_t, marker='o', linestyle='-', color='black', label='Merge Sort (ms)')
    plt.plot(n_vals, q_t, marker='s', linestyle='--', color='black', label='Quick Sort 3-Way (ms)')
    plt.plot(n_vals, h_t, marker='^', linestyle='-.', color='black', label='Heap Sort (ms)')
    plt.plot(n_vals, k_t, marker='d', linestyle=':', color='black', label='Top-3 Min-Heap (ms)')

    plt.title("Experiment 5: Sorting Suite Execution Time vs Array Size (N)", fontsize=11, fontweight='bold', fontfamily='Arial')
    plt.xlabel("Array Elements (N)", fontsize=10, fontfamily='Arial')
    plt.ylabel("Execution Time (ms)", fontsize=10, fontfamily='Arial')
    plt.grid(True, linestyle=':', color='gray', alpha=0.6)
    plt.legend(frameon=True)
    plt.tight_layout()

    plot_path = os.path.join(output_dir, "exp5_plot.png")
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"[EXP 5] Output written to {csv_path} and {plot_path}")
    return records


if __name__ == "__main__":
    run_experiment_5()
