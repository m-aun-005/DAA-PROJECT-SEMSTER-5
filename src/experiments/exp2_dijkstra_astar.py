"""src/experiments/exp2_dijkstra_astar.py — Experiment 2: Dijkstra vs A* Empirical Study (Section 7).
Compares runtime, vertex expansions, edge relaxations, and verifies optimality invariance.
"""

import csv
import math
import os
import random
import time
from typing import Dict, List
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.core.graph import Graph
from src.core.dijkstra import Dijkstra
from src.core.astar import AStar
from src.models.vertex import Vertex, VertexType
from src.models.edge import Edge, RoutingPreset
from src.experiments.exp1_bfs_dfs import generate_random_connected_graph


def run_experiment_2(output_dir: str = "src/experiments/results") -> List[Dict]:
    os.makedirs(output_dir, exist_ok=True)
    vertex_sizes = [20, 50, 100, 200, 500, 1000]
    records = []

    print("[EXP 2] Running Dijkstra vs A* Benchmarking...")

    for v_count in vertex_sizes:
        d_times = []
        a_times = []
        d_exp = []
        a_exp = []
        d_relax = []
        a_relax = []
        d_heap = []
        a_heap = []
        cost_matches = 0

        runs = 5
        for _ in range(runs):
            g = generate_random_connected_graph(v_count, edge_factor=3.0)
            start_node = 0
            target_node = v_count - 1

            dijkstra = Dijkstra(g)
            d_res = dijkstra.run(start_node, target_node, preset=RoutingPreset.BALANCED)

            astar = AStar(g)
            a_res = astar.run(start_node, target_node, preset=RoutingPreset.BALANCED)

            d_times.append(d_res["stats"]["execution_time_us"])
            a_times.append(a_res["stats"]["execution_time_us"])
            d_exp.append(d_res["stats"]["expanded_vertices"])
            a_exp.append(a_res["stats"]["expanded_vertices"])
            d_relax.append(d_res["stats"]["relaxed_edges"])
            a_relax.append(a_res["stats"]["relaxed_edges"])
            d_heap.append(d_res["stats"]["heap_operations"])
            a_heap.append(a_res["stats"]["heap_operations"])

            if abs(d_res["cost"] - a_res["cost"]) < 1e-4:
                cost_matches += 1

        rec = {
            "V": v_count,
            "dijkstra_time_us": round(sum(d_times) / runs, 1),
            "astar_time_us": round(sum(a_times) / runs, 1),
            "dijkstra_expanded": round(sum(d_exp) / runs, 1),
            "astar_expanded": round(sum(a_exp) / runs, 1),
            "dijkstra_relaxed": round(sum(d_relax) / runs, 1),
            "astar_relaxed": round(sum(a_relax) / runs, 1),
            "dijkstra_heap_ops": round(sum(d_heap) / runs, 1),
            "astar_heap_ops": round(sum(a_heap) / runs, 1),
            "cost_match_pct": round((cost_matches / runs) * 100, 1)
        }
        records.append(rec)
        print(f"  V={v_count:<4} | Dijkstra Exp: {rec['dijkstra_expanded']:>5.1f} | A* Exp: {rec['astar_expanded']:>5.1f} | Optimality: {rec['cost_match_pct']}%")

    # Save to CSV
    csv_path = os.path.join(output_dir, "exp2_dijkstra_astar.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    # Plot (Black & White style)
    plt.figure(figsize=(7, 4.5))
    v_vals = [r["V"] for r in records]
    d_exp_vals = [r["dijkstra_expanded"] for r in records]
    a_exp_vals = [r["astar_expanded"] for r in records]

    plt.plot(v_vals, d_exp_vals, marker='o', linestyle='-', color='black', label='Dijkstra Expansions')
    plt.plot(v_vals, a_exp_vals, marker='^', linestyle='--', color='black', label='A* Heuristic Expansions')

    plt.title("Experiment 2: Node Expansions Comparison (Dijkstra vs A*)", fontsize=11, fontweight='bold', fontfamily='Arial')
    plt.xlabel("Graph Vertices (|V|)", fontsize=10, fontfamily='Arial')
    plt.ylabel("Expanded Vertices Count", fontsize=10, fontfamily='Arial')
    plt.grid(True, linestyle=':', color='gray', alpha=0.6)
    plt.legend(frameon=True)
    plt.tight_layout()

    plot_path = os.path.join(output_dir, "exp2_plot.png")
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"[EXP 2] Output written to {csv_path} and {plot_path}")
    return records


if __name__ == "__main__":
    run_experiment_2()
