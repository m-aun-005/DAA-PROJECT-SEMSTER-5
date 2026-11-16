"""src/experiments/exp4_event_heap.py — Experiment 4: Min-Heap Event Queue (Section 7).
Benchmarks heap insertion/extraction scaling O(M log M), tie-breaking, and O(1) lazy deletion.
"""

import csv
import os
import random
import time
from typing import Dict, List
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from src.core.heap import EventQueue
from src.models.event import RaceEvent, EventType


def run_experiment_4(output_dir: str = "src/experiments/results") -> List[Dict]:
    os.makedirs(output_dir, exist_ok=True)
    event_counts = [10, 100, 500, 1000, 5000, 10000]
    records = []

    print("[EXP 4] Running Min-Heap Event Queue Benchmarking...")

    for m in event_counts:
        eq = EventQueue()
        
        # 1. Insertion timing
        t_start_push = time.perf_counter()
        events_generated: List[RaceEvent] = []
        for i in range(1, m + 1):
            # Introduce intentional duplicate timestamps and priorities to test deterministic tie-breaking
            t_trig = round(random.uniform(1.0, 100.0), 1)
            prio = random.randint(1, 6)
            ev = RaceEvent(
                eventId=i,
                triggerTime=t_trig,
                priority=prio,
                insertionSequence=0,
                type=EventType(prio),
                targetEdgeOrVertex=random.randint(1, 50),
                duration=random.uniform(5.0, 20.0),
                description=f"Event {i}"
            )
            eq.enqueue(ev)
            events_generated.append(ev)
        push_time_us = (time.perf_counter() - t_start_push) * 1e6

        # 2. Cancel 20% of events randomly to test lazy deletion
        cancel_count = m // 5
        cancelled_indices = random.sample(range(m), cancel_count)
        for idx in cancelled_indices:
            eq.cancel_event(events_generated[idx].eventId)

        # 3. Extraction timing and order verification
        t_start_pop = time.perf_counter()
        dequeued = []
        order_valid = True
        last_key = None

        while not eq.is_empty():
            ev = eq.dequeue()
            if ev is not None:
                current_key = (ev.triggerTime, ev.priority, ev.insertionSequence)
                if last_key is not None and current_key < last_key:
                    order_valid = False
                last_key = current_key
                dequeued.append(ev)
        pop_time_us = (time.perf_counter() - t_start_pop) * 1e6

        stats = eq.get_stats()
        rec = {
            "M_events": m,
            "push_time_us": round(push_time_us, 1),
            "pop_time_us": round(pop_time_us, 1),
            "total_time_us": round(push_time_us + pop_time_us, 1),
            "comparisons": stats["comparisons"],
            "lazy_deleted": stats["lazy_deleted_count"],
            "order_verified": order_valid
        }
        records.append(rec)
        print(f"  M={m:<6} | Push: {rec['push_time_us']:>7.1f} μs | Pop: {rec['pop_time_us']:>7.1f} μs | Comparisons: {rec['comparisons']:<8} | Order OK: {order_valid}")

    # Save to CSV
    csv_path = os.path.join(output_dir, "exp4_event_heap.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    # Plot (Black & White style)
    plt.figure(figsize=(7, 4.5))
    m_vals = [r["M_events"] for r in records]
    tot_t = [r["total_time_us"] for r in records]

    plt.plot(m_vals, tot_t, marker='o', linestyle='-', color='black', label='Heap Push+Pop Total Time (μs)')

    plt.title("Experiment 4: Event Queue Heap Runtime vs Number of Events (M)", fontsize=11, fontweight='bold', fontfamily='Arial')
    plt.xlabel("Total Scheduled Events (M)", fontsize=10, fontfamily='Arial')
    plt.ylabel("Execution Time (μs)", fontsize=10, fontfamily='Arial')
    plt.grid(True, linestyle=':', color='gray', alpha=0.6)
    plt.legend(frameon=True)
    plt.tight_layout()

    plot_path = os.path.join(output_dir, "exp4_plot.png")
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"[EXP 4] Output written to {csv_path} and {plot_path}")
    return records


if __name__ == "__main__":
    run_experiment_4()
