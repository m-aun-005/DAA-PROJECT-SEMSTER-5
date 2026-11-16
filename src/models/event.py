"""src/models/event.py — Dynamic Race Event model matching Section 4.5.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional


class EventType(IntEnum):
    """Dynamic race events and their mandatory priorities from Section 4.5."""
    ROAD_BLOCKAGE = 1         # Priority 1: Set edge Blocked; exclude from routing
    SHORTCUT_TOGGLE = 2       # Priority 2: Toggle shortcut Open/Blocked
    OIL_SPILL = 3             # Priority 3: Increase effective difficulty/reduce speed
    SPEED_RESTRICTION = 4     # Priority 4: Cap speed on an edge/region
    FUEL_STATION = 5          # Priority 5: Activate/deactivate station
    NITRO_BOOSTER = 6         # Priority 6: Activate pickup vertex


@dataclass(order=True)
class RaceEvent:
    """Represents a scheduled dynamic event in the race min-heap.
    
    Order is strictly defined by the tuple:
    (triggerTime, priority, insertionSequence)
    """
    # Sort keys for min-heap
    triggerTime: float
    priority: int
    insertionSequence: int

    # Non-compared fields
    eventId: int = field(compare=False)
    type: EventType = field(compare=False)
    targetEdgeOrVertex: int = field(compare=False)
    duration: float = field(compare=False, default=0.0)
    cancelled: bool = field(compare=False, default=False)
    description: str = field(compare=False, default="")
    is_expiry_event: bool = field(compare=False, default=False)
    parent_event_id: Optional[int] = field(compare=False, default=None)

    def cancel(self) -> None:
        """Applies lazy deletion by flagging event as cancelled."""
        self.cancelled = True
