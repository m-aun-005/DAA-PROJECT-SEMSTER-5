# Smart Racing Championship: The Algorithmic Racing Challenge 🏎️💨

> **Course:** Design and Analysis of Algorithms (CS-2002) — Semester 5  
> **Institution:** FAST National University of Computer & Emerging Sciences (FAST-NUCES)  
> **Academic Session:** Fall 2026  
> **Project Repository:** [https://github.com/m-aun-005/DAA-PROJECT-SEMSTER-5](https://github.com/m-aun-005/DAA-PROJECT-SEMSTER-5)

---

## 👥 Group Members & Registration

| Member Name | Registration Number | Department & Campus |
|:---|:---:|:---|
| **Muhammad Aoun** | `24P-3099` | Department of Computer Science, FAST-NUCES |
| **Abdullah Mohzar** | `24I-3124` | Department of Computer Science, FAST-NUCES |
| **Muhammad Sarim** | `24I-3069` | Department of Computer Science, FAST-NUCES |

---

## 📌 Project Overview

**Smart Racing Championship** is a 2D top-down simulation game and algorithmic laboratory situated on a dynamically evolving road network. Circuits feature intersections, mandatory ordered checkpoints, alternative routes, high-risk shortcuts, refuelling stations, nitro pickups, and road obstacles.

The project demonstrates the practical application, empirical profiling, and integration of **twelve foundational computer science algorithms**. In strict accordance with the project specifications, the system maintains a **"Single Source of Truth"** architecture: every mandatory algorithm has an active functional role in gameplay and is directly observable within the interactive visualizer.

Machine learning and reinforcement learning are strictly avoided; all computer-controlled opponents adhere to **100% deterministic rules and finite-state machines**.

---

## 🎮 The Five Required GUI Screens

1. **Main Menu Screen:** Mode selector (`Quick Race`, `Championship`, `Track Explorer`, `Algorithm Lab`), circuit configuration, and student team credits.
2. **Track Explorer / Route Planner:** Visual topological inspector comparing **BFS**, **DFS**, **Dijkstra**, and **A\*** under four multi-objective presets (`Balanced`, `Speed`, `Economy`, `Safety`). Click any vertex on the map to set custom destinations.
3. **Racing Simulation Screen:** 60 FPS top-down simulation featuring vehicle motion, player controls (Arrow Keys / WASD, Space for Nitro, P/Esc for Pause), live HUD telemetry (Fuel gauge, Nitro dots, Lap timer), and dynamic road event alerts.
4. **Algorithm Lab / Visualizer:** Step-by-step interactive debugger allowing inspection of open/closed frontiers, priority queue states, and operation counters on live circuit graphs.
5. **Championship Dashboard:** Podium awards, full finishing standings, and side-by-side comparison of **Merge Sort**, **Quick Sort (3-way)**, **Heap Sort**, and **Top-k Priority Queue** under the unified Section 4.6 multi-tier comparator.

---

## 🧠 The 12 Mandatory Algorithms Implemented

| # | Algorithm Family | Implementation Class | Role in Gameplay / System | Theoretical Asymptotic Complexity |
|:---:|:---|:---|:---|:---:|
| **1** | **BFS** | `src.core.bfs.BFS` | Reachability analysis & minimum-hop unweighted path | $O(V + E)$ |
| **2** | **DFS** | `src.core.dfs.DFS` | Cycle detection, connected components, dead-end discovery | $O(V + E)$ |
| **3** | **Dijkstra** | `src.core.dijkstra.Dijkstra` | Optimal path with non-negative multi-objective scalar costs | $O((V + E) \log V)$ |
| **4** | **A\*** | `src.core.astar.AStar` | Heuristic-guided search with admissible Euclidean lower bound | $O((V + E) \log V)$ |
| **5** | **0/1 Knapsack DP** | `src.core.knapsack_dp.KnapsackDP` | Optimal pickup selection under detour budget with 2D table trace | $O(m \cdot B)$ |
| **—** | **Refuel DP** *(Bonus)* | `src.core.knapsack_dp.RefuelDP` | Optimal pit-stop refuelling schedule ($dp[j][f]$ state space) | $O(m \cdot C^2)$ |
| **6** | **Greedy Heuristic** | `src.core.greedy.GreedyPlanner` | Benefit/cost ratio pickup packing with documented suboptimality cases | $O(m \log m)$ |
| **7** | **Backtracking** | `src.core.backtracking.TrackPlacer` | Constraint-based checkpoint placement with safety pruning rules | $O(b^d)$ pruned |
| **8** | **Kruskal's MST** | `src.core.mst.KruskalMST` | Undirected backbone with Disjoint Set Union (Union-Find) | $O(E \log E)$ |
| **—** | **Prim's MST** *(Bonus)* | `src.core.mst.PrimMST` | Undirected backbone generation using binary min-heap | $O(E \log V)$ |
| **9** | **Min-Heap Queue** | `src.core.heap.EventQueue` | Dynamic race hazard scheduler with $O(1)$ lazy cancellation | $O(\log M)$ |
| **10**| **Merge Sort** | `src.core.sorting.MergeSort` | Primary tournament ranking (stable divide-and-conquer) | $O(n \log n)$ |
| **11**| **Quick Sort (3-Way)** | `src.core.sorting.QuickSort3Way` | Dutch National Flag partitioning for duplicate point records | $O(n \log n)$ |
| **12**| **Heap Sort** | `src.core.sorting.HeapSortAlgo` | In-place non-recursive sorting benchmark | $O(n \log n)$ |
| **—** | **Top-k Selection** | `src.core.sorting.TopKHeap` | Size-$k$ min-heap live podium retrieval ($k \ll n$) | $O(n \log k)$ |

---

## 🛠️ Installation & Setup Instructions

### 1. Requirements
- Python 3.10+ (tested on **Python 3.14**)
- `pip` package manager

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Project

### Launch the 2D Game & Visualizer
```bash
python main.py
```

### Run the 17 Automated Unit Tests (100% Passing)
```bash
python -m pytest tests/ -v
```

### Run the 5 Empirical Benchmark Experiments
Executes all benchmarks, logs CSV tables, and renders grayscale figures into `src/experiments/results/`:
```bash
python -m src.experiments.run_all
```

### Generate the Academic PDF Technical Report
Produces the black-and-white academic report formatted in Arial 12pt (`Smart_Racing_Championship_Report.pdf`):
```bash
python -m src.report.generate_report
```

---

## 📊 Summary of Experimental Studies

- **Experiment 1 (BFS vs DFS):** Corroborated linear scaling against $O(V + E)$ on sparse graphs up to $V=500, E=1250$.
- **Experiment 2 (Dijkstra vs A\*):** Verified 100.0% path cost optimality match while A* achieved a 33% reduction in vertex expansions.
- **Experiment 3 (DP vs Greedy):** Validated DP against exhaustive brute-force search on small instances; confirmed up to 37.5% suboptimality gap on greedy counterexamples.
- **Experiment 4 (Event Priority Queue):** Verified deterministic tie-breaking across 10,000 events and validated $O(1)$ lazy cancellation efficiency.
- **Experiment 5 (Sorting Suite & Top-k):** Proved size-$k$ min-heap achieves up to **26× speedup** over full sorting for live podium analytics at $N = 25,000$.

---

## 📜 Academic Integrity & License
Developed strictly for educational and demonstration purposes for the Semester 5 **Design and Analysis of Algorithms** course at **FAST-NUCES**. All algorithms and data structures were implemented from foundational mathematical principles without third-party black-box solvers.
