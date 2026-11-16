"""src/engine/event_engine.py — Dynamic Race Event Processor (Section 4.5).
Manages min-heap priority queue, lazy cancellation, deterministic ties,
and overlapping edge effect stacking.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from src.core.graph import Graph
from src.core.heap import EventQueue
from src.models.event import RaceEvent, EventType
from src.models.edge import EdgeStatus


@dataclass
class ActiveEffect:
    """Tracks an ongoing dynamic modifier on an edge or vertex."""
    parent_event_id: int
    event_type: EventType
    target_id: int
    expiry_time: float
    hazard_penalty: float = 0.0
    speed_cap: float = 1.0


class EventEngine:
    """Executes dynamic race events in exact heap order and manages temporary state."""

    def __init__(self, graph: Graph):
        self.graph = graph
        self.queue = EventQueue()
        # Active effects per edge: edge_id -> list of ActiveEffect
        self.active_edge_effects: Dict[int, List[ActiveEffect]] = {}
        self.processed_events: List[RaceEvent] = []
        self.event_log: List[str] = []

    def schedule_event(self, event: RaceEvent) -> None:
        self.queue.enqueue(event)

    def load_events(self, events: List[RaceEvent]) -> None:
        for ev in events:
            self.schedule_event(ev)

    def tick(self, current_time: float) -> List[RaceEvent]:
        """Pops and applies all events whose triggerTime <= current_time in strict priority order."""
        applied: List[RaceEvent] = []

        while not self.queue.is_empty():
            peek_ev = self.queue.peek()
            if peek_ev is None or peek_ev.triggerTime > current_time:
                break

            ev = self.queue.dequeue()
            if ev is None:
                break

            self._apply_event(ev, current_time)
            applied.append(ev)
            self.processed_events.append(ev)

        return applied

    def _apply_event(self, ev: RaceEvent, current_time: float) -> None:
        """Applies event effect or expiry restoration."""
        target_id = ev.targetEdgeOrVertex

        if ev.is_expiry_event:
            self._handle_expiry(ev)
            return

        # 1. Road Blockage (Priority 1)
        if ev.type == EventType.ROAD_BLOCKAGE:
            self.graph.set_edge_status(target_id, EdgeStatus.BLOCKED)
            msg = f"[t={current_time:.1f}s] ROAD CLOSED: Edge {target_id} blocked! {ev.description}"
            self.event_log.append(msg)
            if ev.duration > 0:
                self._schedule_expiry(ev, current_time + ev.duration)

        # 2. Shortcut Toggle (Priority 2)
        elif ev.type == EventType.SHORTCUT_TOGGLE:
            edge = self.graph.get_edge(target_id)
            if edge:
                new_status = EdgeStatus.BLOCKED if edge.status == EdgeStatus.OPEN else EdgeStatus.OPEN
                self.graph.set_edge_status(target_id, new_status)
                msg = f"[t={current_time:.1f}s] SHORTCUT: Edge {target_id} status changed to {new_status.value}."
                self.event_log.append(msg)
                if ev.duration > 0:
                    self._schedule_expiry(ev, current_time + ev.duration)

        # 3. Oil Spill (Priority 3)
        elif ev.type == EventType.OIL_SPILL:
            eff = ActiveEffect(
                parent_event_id=ev.eventId,
                event_type=ev.type,
                target_id=target_id,
                expiry_time=current_time + ev.duration,
                hazard_penalty=0.6,
                speed_cap=0.7
            )
            self._add_edge_effect(target_id, eff)
            msg = f"[t={current_time:.1f}s] HAZARD: Oil spill on Edge {target_id}! Difficulty and speed impacted."
            self.event_log.append(msg)
            if ev.duration > 0:
                self._schedule_expiry(ev, current_time + ev.duration)

        # 4. Speed Restriction (Priority 4)
        elif ev.type == EventType.SPEED_RESTRICTION:
            eff = ActiveEffect(
                parent_event_id=ev.eventId,
                event_type=ev.type,
                target_id=target_id,
                expiry_time=current_time + ev.duration,
                hazard_penalty=0.0,
                speed_cap=0.5
            )
            self._add_edge_effect(target_id, eff)
            msg = f"[t={current_time:.1f}s] SPEED CAP: Edge {target_id} capped at 50% speed."
            self.event_log.append(msg)
            if ev.duration > 0:
                self._schedule_expiry(ev, current_time + ev.duration)

        # 5. Fuel Station Toggle (Priority 5)
        elif ev.type == EventType.FUEL_STATION:
            v = self.graph.get_vertex(target_id)
            if v:
                self.graph.set_vertex_active(target_id, not v.active)
                status_str = "ACTIVE" if v.active else "OFFLINE"
                msg = f"[t={current_time:.1f}s] STATION: Fuel Station {target_id} is now {status_str}."
                self.event_log.append(msg)
                if ev.duration > 0:
                    self._schedule_expiry(ev, current_time + ev.duration)

        # 6. Nitro Booster (Priority 6)
        elif ev.type == EventType.NITRO_BOOSTER:
            self.graph.set_vertex_active(target_id, True)
            msg = f"[t={current_time:.1f}s] PICKUP: Nitro booster spawned at Vertex {target_id}!"
            self.event_log.append(msg)
            if ev.duration > 0:
                self._schedule_expiry(ev, current_time + ev.duration)

    def _schedule_expiry(self, parent_ev: RaceEvent, expiry_time: float) -> None:
        """Schedules a restoration/expiry event deterministically."""
        expiry_ev = RaceEvent(
            eventId=10000 + parent_ev.eventId,
            triggerTime=expiry_time,
            priority=parent_ev.priority,
            insertionSequence=0,
            type=parent_ev.type,
            targetEdgeOrVertex=parent_ev.targetEdgeOrVertex,
            is_expiry_event=True,
            parent_event_id=parent_ev.eventId,
            description=f"Expiry of event {parent_ev.eventId}"
        )
        self.queue.enqueue(expiry_ev)

    def _handle_expiry(self, ev: RaceEvent) -> None:
        """Restores original edge or vertex properties when duration elapses."""
        target_id = ev.targetEdgeOrVertex
        if ev.type == EventType.ROAD_BLOCKAGE:
            self.graph.set_edge_status(target_id, EdgeStatus.OPEN)
            self.event_log.append(f"[t={ev.triggerTime:.1f}s] RESTORED: Road blockage cleared on Edge {target_id}.")

        elif ev.type == EventType.SHORTCUT_TOGGLE:
            edge = self.graph.get_edge(target_id)
            if edge:
                reverted = EdgeStatus.OPEN if edge.status == EdgeStatus.BLOCKED else EdgeStatus.BLOCKED
                self.graph.set_edge_status(target_id, reverted)
                self.event_log.append(f"[t={ev.triggerTime:.1f}s] RESTORED: Shortcut Edge {target_id} restored to {reverted.value}.")

        elif ev.type in (EventType.OIL_SPILL, EventType.SPEED_RESTRICTION):
            # Remove from active effects list
            if target_id in self.active_edge_effects:
                self.active_edge_effects[target_id] = [
                    eff for eff in self.active_edge_effects[target_id]
                    if eff.parent_event_id != ev.parent_event_id
                ]
                self._recalculate_stacked_edge_state(target_id)
            self.event_log.append(f"[t={ev.triggerTime:.1f}s] RESTORED: Hazard/Speed restriction expired on Edge {target_id}.")

        elif ev.type == EventType.FUEL_STATION:
            self.graph.set_vertex_active(target_id, True)
            self.event_log.append(f"[t={ev.triggerTime:.1f}s] RESTORED: Fuel Station {target_id} reopened.")

    def _add_edge_effect(self, edge_id: int, eff: ActiveEffect) -> None:
        if edge_id not in self.active_edge_effects:
            self.active_edge_effects[edge_id] = []
        self.active_edge_effects[edge_id].append(eff)
        self._recalculate_stacked_edge_state(edge_id)

    def _recalculate_stacked_edge_state(self, edge_id: int) -> None:
        """Resolves overlapping effects on an edge according to Section 4.5 rules:
        - Strictest active speed cap
        - Maximum hazard difficulty penalty
        """
        effects = self.active_edge_effects.get(edge_id, [])
        if not effects:
            self.graph.set_edge_hazard(edge_id, 0.0)
            self.graph.set_edge_speed_cap(edge_id, 1.0)
            return

        max_hazard = max(eff.hazard_penalty for eff in effects)
        min_speed_cap = min(eff.speed_cap for eff in effects)

        self.graph.set_edge_hazard(edge_id, max_hazard)
        self.graph.set_edge_speed_cap(edge_id, min_speed_cap)
