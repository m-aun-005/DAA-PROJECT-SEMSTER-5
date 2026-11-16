"""src/models/circuit.py — Circuit representation and registry.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from src.core.graph import Graph
from src.models.event import RaceEvent


@dataclass
class Circuit:
    """Represents a playable racing track topology with pre-scheduled dynamic events."""
    id: int
    name: str
    description: str
    graph: Graph
    start_vertex_id: int
    finish_vertex_id: int
    checkpoint_ids: List[int]        # Ordered list of 10 mandatory checkpoint vertex IDs
    shortcut_edge_ids: List[int]     # Edge IDs marked as shortcuts
    fuel_station_ids: List[int]      # Vertex IDs hosting fuel stations
    nitro_pickup_ids: List[int]      # Vertex IDs hosting nitro pickups
    dead_end_ids: List[int]          # Vertex IDs that are dead ends
    scheduled_events: List[RaceEvent] = field(default_factory=list)
