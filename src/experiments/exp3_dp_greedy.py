"""src/experiments/exp3_dp_greedy.py — Experiment 3: 0/1 Knapsack DP vs Greedy Heuristic (Section 7).
Empirically benchmarks optimality gap, state evaluations, and compares against exhaustive search.
"""

import csv
import os
import random
import time
from typing import Dict, List
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.core.knapsack_dp import KnapsackDP, KnapsackItem
from src.core.greedy import GreedyPlanner


def run_experiment_3(output_dir: str = "src/experiments/results") -> List[Dict]:
    os.makedirs(output_dir, exist_ok=True)
    configurations = [
        (5, 20),
        (10, 50),
        (20, 100),
        (30, 150),
        (50, 250),
        (100, 500)
    ]
    records = []

    print("[EXP 3] Running Knapsack DP vs Greedy Benchmarking...")

    # First, test the 3 documented counterexamples
    ce_cases = GreedyPlanner.get_documented_counterexamples()
    dp_solver = KnapsackDP()
    greedy_solver = GreedyPlanner()

    for ce in ce_cases:
        dp_res = dp_solver.solve(ce["items"], ce["budget"])
        gr_res = greedy_solver.solve(ce["items"], ce["budget"])
        gap = ((dp_res["total_benefit"] - gr_res["total_benefit"]) / dp_res["total_benefit"]) * 100
        print(f"  Counterexample: {ce['name']} | DP: {dp_res['total_benefit']} | Greedy: {gr_res['total_benefit']} | Gap: {gap:.1f}%")

    # Scaled configurations
    for n_items, budget in configurations:
        dp_benefits = []
        gr_benefits = []
        dp_times = []
        gr_times = []
        state_counts = []
        brute_force_matches = 0

        runs = 5
        for _ in range(runs):
            items = [
                KnapsackItem(id=i, name=f"Pickup_{i}", cost=random.randint(2, 30), benefit=random.randint(10, 100))
                for i in range(1, n_items + 1)
            ]

            dp_res = dp_solver.solve(items, budget)
            gr_res = greedy_solver.solve(items, budget)

            dp_benefits.append(dp_res["total_benefit"])
            gr_benefits.append(gr_res["total_benefit"])
            dp_times.append(dp_res["execution_time_us"])
            gr_times.append(gr_res["execution_time_us"])
            state_counts.append(dp_res["table_entries_evaluated"])

            # Verify against brute force on small instances
            if n_items <= 10:
                bf_val, _ = GreedyPlanner.brute_force_knapsack(items, budget)
                if bf_val == dp_res["total_benefit"]:
                    brute_force_matches += 1

        avg_dp_b = sum(dp_benefits) / runs
        avg_gr_b = sum(gr_benefits) / runs
        gap_pct = ((avg_dp_b - avg_gr_b) / avg_dp_b * 100) if avg_dp_b > 0 else 0.0

        rec = {
            "N_items": n_items,
            "budget": budget,
            "dp_benefit": round(avg_dp_b, 1),
            "greedy_benefit": round(avg_gr_b, 1),
            "optimality_gap_pct": round(gap_pct, 2),
            "dp_states_evaluated": int(sum(state_counts) / runs),
            "dp_time_us": round(sum(dp_times) / runs, 1),
            "greedy_time_us": round(sum(gr_times) / runs, 1),
            "brute_force_verified": (brute_force_matches == runs) if n_items <= 10 else "N/A"
        }
        records.append(rec)
        print(f"  N={n_items:<3} | Budget={budget:<4} | DP Benefit: {rec['dp_benefit']:>6.1f} | Greedy: {rec['greedy_benefit']:>6.1f} | Gap: {rec['optimality_gap_pct']:>5.2f}%")

    # Save to CSV
    csv_path = os.path.join(output_dir, "exp3_dp_greedy.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    # Plot (Black & White style)
    plt.figure(figsize=(7, 4.5))
    n_vals = [r["N_items"] for r in records]
    dp_t = [r["dp_time_us"] for r in records]
    gr_t = [r["greedy_time_us"] for r in records]

    plt.plot(n_vals, dp_t, marker='o', linestyle='-', color='black', label='0/1 Knapsack DP (μs)')
    plt.plot(n_vals, gr_t, marker='s', linestyle='--', color='black', label='Greedy Heuristic (μs)')

    plt.title("Experiment 3: DP vs Greedy Execution Time vs Item Count", fontsize=11, fontweight='bold', fontfamily='Arial')
    plt.xlabel("Number of Pickup Items (N)", fontsize=10, fontfamily='Arial')
    plt.ylabel("Execution Time (μs)", fontsize=10, fontfamily='Arial')
    plt.grid(True, linestyle=':', color='gray', alpha=0.6)
    plt.legend(frameon=True)
    plt.tight_layout()

    plot_path = os.path.join(output_dir, "exp3_plot.png")
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"[EXP 3] Output written to {csv_path} and {plot_path}")
    return records


if __name__ == "__main__":
    run_experiment_3()
