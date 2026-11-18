# Legendary Motors Championship: The Algorithmic Racing Challenge 🏎️💨

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

**Legendary Motors Championship** is a top-down arcade racing simulator and algorithmic laboratory inspired by vintage endurance championships (Le Mans, Trans-Am, GT World Series). The game features legendary 1960s–1970s muscle and sports cars—including the **Ford GT40 Mk.II**, **Shelby Mustang GT500**, **Dodge Charger R/T**, **Ferrari 250 GTO**, **Pontiac GTO**, **Chevy Camaro Z28**, **AC Cobra 427**, and **Jaguar E-Type**.

The project demonstrates the practical application, empirical profiling, and integration of **twelve foundational computer science algorithms**. In strict accordance with the project specifications, the system maintains a **"Single Source of Truth"** architecture: every mandatory algorithm has an active functional role in gameplay and is directly observable within the interactive visualizer.

Machine learning and reinforcement learning are strictly avoided; all computer-controlled opponents adhere to **100% deterministic rules and finite-state machines**.

---

## 🎮 Game Modes & Comprehensive Screen Suite

The application delivers a commercial-grade pseudo-3D retro arcade racing experience:

1. **Cinematic Splash / Start Screen (`splash_screen.py`):** Real vintage racing photography background from historic endurance racing archives, cinematic letterboxing, pulsing "PRESS ANY KEY" prompt, and animated silhouettes.
2. **Main Navigation Hub (`main_menu.py`):** Interactive menu featuring high-contrast neon styling, interactive vehicle showcase carousel, and one-click navigation across all game modes:
   - `🏆 CHAMPIONSHIP`
   - `🏁 QUICK RACE`
   - `🗺 RACE EXPLORER`
   - `🔧 GARAGE`
   - `📊 SCOREBOARD`
   - `📖 INSTRUCTIONS`
   - `✕ EXIT`
3. **Championship Seasons Selector (`championship.py`):** Structured multi-season campaign mode with 5 distinct seasons:
   - **Season 1: Road to Glory (1962)** — 4 rounds, Open class, unlocks Jaguar E-Type.
   - **Season 2: Italian Fire (1964)** — 5 rounds, GT class, unlocks Ferrari 250 GTO.
   - **Season 3: American Muscle (1967)** — 5 rounds, Muscle class, unlocks Shelby GT500.
   - **Season 4: 24 Hours Legend (1966)** — 6 rounds, GT endurance, unlocks Ford GT40 Mk.II.
   - **Season 5: Grand Finale (1969)** — 7 rounds on mixed circuits to claim the overall crown.
4. **Classic Car Garage (`garage.py` & `car_select.py`):** 3D-styled top-down showcase of 8 legendary cars with detailed vector styling (chassis reflections, drop shadows, wheel spoke geometry, fender flares, and racing liveries), accompanied by animated performance telemetry (Speed, Acceleration, Handling, Nitro Boost) and mechanical specifications (Engine displacement, Horsepower, Curb weight, Drivetrain).
5. **Track Selection Screen (`circuit_select.py`):** Card-based track carousel displaying vector mini-maps, corner counts, length, difficulty stars (1–5), and custom lap configuration (1, 2, or 3 laps).
6. **Track Explorer / Route Planner (`track_explorer.py`):** Visual topological inspector comparing **BFS**, **DFS**, **Dijkstra**, and **A\*** under four multi-objective presets (`Balanced`, `Speed`, `Economy`, `Safety`). Click any vertex on the map to set custom destinations.
7. **Racing Simulation Screen (`racing_screen.py`):** 60 FPS top-down simulation featuring pseudo-3D shaded muscle cars, tire rims, rear spoilers, exhaust nitro plumes, radial arc speedometer, 3-segment neon nitro gauge, live positions indicator, checkpoint hints, and dynamic hazard alerts. Controls: `WASD / Arrows` for steering, `Space` for Nitro, `P / Esc` to Pause.
8. **Global Scoreboard (`scoreboard.py`):** Persistent season leaderboard with multi-tiered podium (1st Gold, 2nd Silver, 3rd Bronze), tracking all-time driver points, race victories, total completed races, and fastest lap records stored on disk (`scoreboard.json`).
9. **How to Play & Instructions (`instructions.py`):** Comprehensive tabbed guide covering vehicle controls, racing mechanics, championship structure, academic algorithm mappings, and driving tips.
10. **Algorithm Lab / Visualizer (`algorithm_lab.py`):** Step-by-step interactive debugger allowing inspection of open/closed frontiers, priority queue states, and operation counters on live circuit graphs.
11. **Championship Dashboard (`dashboard.py`):** 3D podium awards, finishing standings, and side-by-side comparison of **Merge Sort**, **Quick Sort (3-way)**, **Heap Sort**, and **Top-k Priority Queue** under the unified Section 4.6 multi-tier comparator.

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
