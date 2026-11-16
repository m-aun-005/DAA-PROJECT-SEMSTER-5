"""tests/test_heap.py — Unit tests for Min-Heap and EventQueue.
"""

import pytest
from src.core.heap import MinHeap, EventQueue
from src.models.event import RaceEvent, EventType


def test_min_heap_operations():
    heap = MinHeap()
    heap.push(10, "item10")
    heap.push(3, "item3")
    heap.push(7, "item7")
    heap.push(1, "item1")

    assert len(heap) == 4
    assert heap.peek() == (1, "item1")
    assert heap.pop() == (1, "item1")
    assert heap.pop() == (3, "item3")
    assert heap.pop() == (7, "item7")
    assert heap.pop() == (10, "item10")


def test_event_queue_priority_and_lazy_delete():
    eq = EventQueue()
    ev1 = RaceEvent(eventId=1, triggerTime=10.0, priority=2, insertionSequence=0, type=EventType.SHORTCUT_TOGGLE, targetEdgeOrVertex=1)
    ev2 = RaceEvent(eventId=2, triggerTime=10.0, priority=1, insertionSequence=0, type=EventType.ROAD_BLOCKAGE, targetEdgeOrVertex=2)
    ev3 = RaceEvent(eventId=3, triggerTime=15.0, priority=3, insertionSequence=0, type=EventType.OIL_SPILL, targetEdgeOrVertex=3)

    eq.enqueue(ev1)
    eq.enqueue(ev2)
    eq.enqueue(ev3)

    # Cancel ev1 (lazy deletion)
    eq.cancel_event(1)

    # ev2 has priority 1, fires first at t=10.0
    popped1 = eq.dequeue()
    assert popped1.eventId == 2

    # ev1 was cancelled, so next popped must be ev3 at t=15.0
    popped2 = eq.dequeue()
    assert popped2.eventId == 3
    assert eq.is_empty() is True
