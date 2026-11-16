"""src/core/heap.py — Custom Min-Heap and Deterministic Race Event Queue (Section 4.5 & 5.4).
Implements explicit binary heap operations with counters and lazy deletion.
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional, Tuple
from src.models.event import RaceEvent, EventType


class MinHeap:
    """Explicit Binary Min-Heap implementation with operation counters."""

    def __init__(self):
        # List of (key, item) tuples
        self.heap: List[Tuple[Any, Any]] = []
        self.push_count: int = 0
        self.pop_count: int = 0
        self.comparisons: int = 0

    def push(self, key: Any, item: Any) -> None:
        """Inserts an element and restores heap property via sift-up in O(log n)."""
        self.heap.append((key, item))
        self.push_count += 1
        self._sift_up(len(self.heap) - 1)

    def pop(self) -> Tuple[Any, Any]:
        """Extracts minimum element in O(log n)."""
        if not self.heap:
            raise IndexError("pop from empty heap")
        self.pop_count += 1
        min_elem = self.heap[0]
        last_elem = self.heap.pop()
        if self.heap:
            self.heap[0] = last_elem
            self._sift_down(0)
        return min_elem

    def peek(self) -> Optional[Tuple[Any, Any]]:
        """Returns root element without removing it in O(1)."""
        return self.heap[0] if self.heap else None

    def __len__(self) -> int:
        return len(self.heap)

    def _sift_up(self, idx: int) -> None:
        while idx > 0:
            parent = (idx - 1) // 2
            self.comparisons += 1
            if self.heap[idx][0] < self.heap[parent][0]:
                self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
                idx = parent
            else:
                break

    def _sift_down(self, idx: int) -> None:
        n = len(self.heap)
        while True:
            smallest = idx
            left = 2 * idx + 1
            right = 2 * idx + 2

            if left < n:
                self.comparisons += 1
                if self.heap[left][0] < self.heap[smallest][0]:
                    smallest = left

            if right < n:
                self.comparisons += 1
                if self.heap[right][0] < self.heap[smallest][0]:
                    smallest = right

            if smallest != idx:
                self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
                idx = smallest
            else:
                break


class EventQueue:
    """Race dynamic event scheduler.
    
    Heap key: (triggerTime, priority, insertionSequence)
    Lower priority number fires first when trigger times tie.
    Insertion sequence guarantees complete determinism.
    Supports O(1) lazy deletion for cancelled events.
    """

    def __init__(self):
        self._heap = MinHeap()
        self._events_by_id: Dict[int, RaceEvent] = {}
        self.seq_counter: int = 0
        self.lazy_deleted_count: int = 0

    def enqueue(self, event: RaceEvent) -> None:
        """Schedules a race event."""
        self.seq_counter += 1
        event.insertionSequence = self.seq_counter
        key = (event.triggerTime, event.priority, event.insertionSequence)
        self._events_by_id[event.eventId] = event
        self._heap.push(key, event)

    def dequeue(self) -> Optional[RaceEvent]:
        """Extracts the next active event, silently discarding cancelled events via lazy deletion."""
        while len(self._heap) > 0:
            _, event = self._heap.pop()
            if event.cancelled:
                self.lazy_deleted_count += 1
                continue
            return event
        return None

    def peek(self) -> Optional[RaceEvent]:
        """Peeks at next active event skipping cancelled ones."""
        while len(self._heap) > 0:
            _, event = self._heap.peek()
            if event.cancelled:
                self._heap.pop()
                self.lazy_deleted_count += 1
                continue
            return event
        return None

    def cancel_event(self, event_id: int) -> bool:
        """Applies lazy cancellation in O(1)."""
        event = self._events_by_id.get(event_id)
        if event and not event.cancelled:
            event.cancel()
            return True
        return False

    def is_empty(self) -> bool:
        return self.peek() is None

    def get_stats(self) -> Dict[str, object]:
        return {
            "queue_size": len(self._heap),
            "push_count": self._heap.push_count,
            "pop_count": self._heap.pop_count,
            "comparisons": self._heap.comparisons,
            "lazy_deleted_count": self.lazy_deleted_count
        }
