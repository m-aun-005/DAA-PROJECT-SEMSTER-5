"""src/experiments/run_all.py — Master Benchmark Suite Execution Harness.
Runs all 5 mandatory experimental studies, generates all CSVs and B&W plots.
"""

import sys
import time
from src.experiments.exp1_bfs_dfs import run_experiment_1
from src.experiments.exp2_dijkstra_astar import run_experiment_2
from src.experiments.exp3_dp_greedy import run_experiment_3
from src.experiments.exp4_event_heap import run_experiment_4
from src.experiments.exp5_sorting import run_experiment_5


def run_all():
    print("=" * 70)
    print("SMART RACING CHAMPIONSHIP — DAA EXPERIMENTAL BENCHMARK HARNESS")
    print("=" * 70)
    t0 = time.time()

    print("\n>>> STARTING EXPERIMENT 1 / 5...")
    run_experiment_1()

    print("\n>>> STARTING EXPERIMENT 2 / 5...")
    run_experiment_2()

    print("\n>>> STARTING EXPERIMENT 3 / 5...")
    run_experiment_3()

    print("\n>>> STARTING EXPERIMENT 4 / 5...")
    run_experiment_4()

    print("\n>>> STARTING EXPERIMENT 5 / 5...")
    run_experiment_5()

    elapsed = time.time() - t0
    print("\n" + "=" * 70)
    print(f"ALL 5 EXPERIMENTS COMPLETED IN {elapsed:.2f} SECONDS!")
    print("CSVs and publication-ready B&W plots saved in src/experiments/results/")
    print("=" * 70)


if __name__ == "__main__":
    run_all()
