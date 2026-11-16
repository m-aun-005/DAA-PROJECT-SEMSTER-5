"""src/models/vertex.py — Vertex definition matching Project Specification Section 3.1.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class VertexType(str, Enum):
    """Types of vertices supported in track graphs."""
    START = "Start"
    FINISH = "Finish"
    CHECKPOINT = "Checkpoint"
    INTERSECTION = "Intersection"
    FUEL_STATION = "FuelStation"
    NITRO_PICKUP = "NitroPickup"
    DEAD_END = "DeadEnd"


@dataclass
class Vertex:
    """Represents a node in the road network graph G = (V, E).
    
    Attributes:
        id: Unique integer identifier.
        x: Map x-coordinate (for rendering and Euclidean A* heuristic).
        y: Map y-coordinate (for rendering and Euclidean A* heuristic).
        type: VertexType classification.
        checkpointOrder: Required ordering (1..10) for mandatory checkpoints; None otherwise.
        active: Whether a service vertex (FuelStation, NitroPickup) is currently active.
        label: Optional human-readable display label.
    """
    id: int
    x: float
    y: float
    type: VertexType = VertexType.INTERSECTION
    checkpointOrder: Optional[int] = None
    active: bool = True
    label: str = ""

    def __post_init__(self):
        if not self.label:
            if self.type == VertexType.CHECKPOINT and self.checkpointOrder is not None:
                self.label = f"CP{self.checkpointOrder}"
            elif self.type == VertexType.START:
                self.label = "START"
            elif self.type == VertexType.FINISH:
                self.label = "FINISH"
            elif self.type == VertexType.FUEL_STATION:
                self.label = f"GAS-{self.id}"
            elif self.type == VertexType.NITRO_PICKUP:
                self.label = f"NITRO-{self.id}"
            elif self.type == VertexType.DEAD_END:
                self.label = f"DEAD-{self.id}"
            else:
                self.label = f"V{self.id}"

    def is_service(self) -> bool:
        """Returns True if vertex provides a pit stop or pickup."""
        return self.type in (VertexType.FUEL_STATION, VertexType.NITRO_PICKUP)

    def is_mandatory_checkpoint(self) -> bool:
        """Returns True if vertex is an ordered checkpoint."""
        return self.type == VertexType.CHECKPOINT and self.checkpointOrder is not None

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Vertex):
            return self.id == other.id
        return False
