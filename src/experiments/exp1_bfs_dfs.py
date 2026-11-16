"""src/experiments/exp1_bfs_dfs.py — Experiment 1: BFS vs DFS Empirical Study (Section 7).
Measures runtime growth against O(V + E), visited vertices, and examined edges on sparse & dense graphs.
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
from src.core.bfs import BFS
from src.core.dfs import DFS
from src.models.vertex import Vertex, VertexType
from src.models.edge import Edge


def generate_random_connected_graph(num_vertices: int, edge_factor: float = 2.0) -> Graph:
    """Generates a connected random graph with V vertices and approx edge_factor * V edges."""
    g = Graph()
    for i in range(num_vertices):
        x = random.uniform(50, 1200)
        y = random.uniform(50, 700)
        g.add_vertex(Vertex(id=i, x=x, y=y, type=VertexType.INTERSECTION))

    eid = 1
    # First build spanning tree to ensure connectivity
    nodes = list(range(num_vertices))
    random.shuffle(nodes)
    for i in range(1, num_vertices):
        u = nodes[i]
        v = nodes[random.randint(0, i - 1)]
        dist = math.hypot(g.vertices[u].x - g.vertices[v].x, g.vertices[u].y - g.vertices[v].y)
        g.add_edge(Edge(id=eid, from_vertex=u, to_vertex=v, distance=dist, baseTime=dist/100, fuelCost=dist/10, difficulty=1, directed=False))
        eid += 1

    # Add extra edges up to edge_factor * V
    target_edges = int(num_vertices * edge_factor)
    existing_pairs = set()
    for e in g.edges.values():
        existing_pairs.add((min(e.from_vertex, e.to_vertex), max(e.from_vertex, e.to_vertex)))

    attempts = 0
    while len(existing_pairs) < target_edges and attempts < target_edges * 4:
        attempts += 1
        u = random.randint(0, num_vertices - 1)
        v = random.randint(0, num_vertices - 1)
        if u != v:
            pair = (min(u, v), max(u, v))
            if pair not in existing_pairs:
                existing_pairs.add(pair)
                dist = math.hypot(g.vertices[u].x - g.vertices[v].x, g.vertices[u].y - g.vertices[v].y)
                g.add_edge(Edge(id=eid, from_vertex=u, to_vertex=v, distance=dist, baseTime=dist/100, fuelCost=dist/10, difficulty=random.randint(1, 4), directed=False))
                eid += 1

    return g


def run_experiment_1(output_dir: str = "src/experiments/results") -> List[Dict]:
    os.makedirs(output_dir, exist_ok=True)
    vertex_sizes = [10, 50, 100, 200, 300, 500]
    records = []

    print("[EXP 1] Running BFS vs DFS Benchmarking...")

    for v_count in vertex_sizes:
        bfs_times = []
        dfs_times = []
        bfs_nodes = []
        dfs_nodes = []
        bfs_edges_list = []
        dfs_edges_list = []

        # 5 repetitions for stability
        for _ in range(5):
            g = generate_random_connected_graph(v_count, edge_factor=2.5)
            start_node = 0
            target_node = v_count - 1

            # BFS
            bfs = BFS(g)
            b_res = bfs.run(start_node, target_node)
            bfs_times.append(b_res["stats"]["execution_time_us"])
            bfs_nodes.append(b_res["stats"]["vertices_visited"])
            bfs_edges_list.append(b_res["stats"]["edges_examined"])

            # DFS
            dfs = DFS(g)
            d_res = dfs.run(start_node)
            dfs_times.append(d_res["stats"]["execution_time_us"])
            dfs_nodes.append(d_res["stats"]["vertices_visited"])
            dfs_edges_list.append(d_res["stats"]["edges_examined"])

        rec = {
            "V": v_count,
            "E": len(g.edges),
            "bfs_time_us": round(sum(bfs_times) / len(bfs_times), 1),
            "bfs_visited_vertices": int(sum(bfs_nodes) / len(bfs_nodes)),
            "bfs_examined_edges": int(sum(bfs_edges_list) / len(bfs_edges_list)),
            "dfs_time_us": round(sum(dfs_times) / len(dfs_times), 1),
            "dfs_visited_vertices": int(sum(dfs_nodes) / len(dfs_nodes)),
            "dfs_examined_edges": int(sum(dfs_edges_list) / len(dfs_edges_list)),
        }
        records.append(rec)
        print(f"  V={v_count:<4} | E={rec['E']:<5} | BFS Time: {rec['bfs_time_us']:>6.1f} μs | DFS Time: {rec['dfs_time_us']:>6.1f} μs")

    # Save to CSV
    csv_path = os.path.join(output_dir, "exp1_bfs_dfs.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    # Plot (Black and White style for academic print)
    plt.figure(figsize=(7, 4.5))
    v_vals = [r["V"] for r in records]
    bfs_t = [r["bfs_time_us"] for r in records]
    dfs_t = [r["dfs_time_us"] for r in records]

    plt.plot(v_vals, bfs_t, marker='o', linestyle='-', color='black', label='BFS Runtime (μs)')
    plt.plot(v_vals, dfs_t, marker='s', linestyle='--', color='black', label='DFS Runtime (μs)')

    plt.title("Experiment 1: BFS vs DFS Execution Time vs Graph Size (|V|)", fontsize=11, fontweight='bold', fontfamily='Arial')
    plt.xlabel("Graph Vertices (|V|)", fontsize=10, fontfamily='Arial')
    plt.ylabel("Execution Time (μs)", fontsize=10, fontfamily='Arial')
    plt.grid(True, linestyle=':', color='gray', alpha=0.6)
    plt.legend(frameon=True)
    plt.tight_layout()

    plot_path = os.path.join(output_dir, "exp1_plot.png")
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"[EXP 1] Output written to {csv_path} and {plot_path}")
    return records


if __name__ == "__main__":
    run_experiment_1()
