"""src/models/edge.py — Edge definition matching Project Specification Section 3.1 & 3.3.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple


class EdgeStatus(str, Enum):
    """Status of an edge in the road network."""
    OPEN = "Open"
    BLOCKED = "Blocked"
    RESTRICTED = "Restricted"


class RoutingPreset(str, Enum):
    """Presets for multi-objective route cost optimization."""
    BALANCED = "Balanced"
    SPEED = "Speed"
    ECONOMY = "Economy"
    SAFETY = "Safety"


# Documented preset weights: (w_d, w_t, w_f, w_r, w_o)
PRESET_WEIGHTS: Dict[RoutingPreset, Tuple[float, float, float, float, float]] = {
    RoutingPreset.BALANCED: (0.25, 0.25, 0.25, 0.15, 0.10),
    RoutingPreset.SPEED:    (0.10, 0.60, 0.10, 0.10, 0.10),
    RoutingPreset.ECONOMY:  (0.15, 0.15, 0.60, 0.05, 0.05),
    RoutingPreset.SAFETY:   (0.10, 0.10, 0.10, 0.40, 0.30),
}

# Empirical normalization reference values (Section 3.3)
REF_DISTANCE: float = 300.0   # Reference max edge distance in pixels
REF_TIME: float = 10.0        # Reference max edge base travel time in seconds
REF_FUEL: float = 25.0        # Reference max fuel cost per edge


@dataclass
class Edge:
    """Represents a road edge in the graph G = (V, E).
    
    Attributes:
        id: Unique integer identifier.
        from_vertex: Source vertex ID.
        to_vertex: Target vertex ID.
        distance: Non-negative road length.
        baseTime: Estimated travel time at nominal speed (seconds).
        fuelCost: Base fuel consumption for the edge.
        difficulty: Integer difficulty from 1 (easy) to 5 (extreme).
        status: EdgeStatus (OPEN, BLOCKED, or RESTRICTED).
        isShortcut: Whether the road is a high-risk / high-reward shortcut.
        directed: True if one-way (from_vertex -> to_vertex), False if bidirectional.
        hazard_level: Obstacle/hazard penalty in [0.0, 1.0] (e.g. from oil spills).
        speed_cap: Optional speed multiplier restriction (e.g. 0.5 for half speed).
    """
    id: int
    from_vertex: int
    to_vertex: int
    distance: float
    baseTime: float
    fuelCost: float
    difficulty: int = 1
    status: EdgeStatus = EdgeStatus.OPEN
    isShortcut: bool = False
    directed: bool = False
    hazard_level: float = 0.0
    speed_cap: float = 1.0

    def __post_init__(self):
        if self.distance < 0:
            raise ValueError(f"Edge {self.id}: distance must be non-negative ({self.distance})")
        if self.baseTime < 0:
            raise ValueError(f"Edge {self.id}: baseTime must be non-negative ({self.baseTime})")
        if self.fuelCost < 0:
            raise ValueError(f"Edge {self.id}: fuelCost must be non-negative ({self.fuelCost})")
        if not (1 <= self.difficulty <= 5):
            raise ValueError(f"Edge {self.id}: difficulty must be between 1 and 5 ({self.difficulty})")

    @property
    def is_traversable(self) -> bool:
        """Blocked edges are strictly impassable in routing."""
        return self.status != EdgeStatus.BLOCKED

    def effective_fuel_consumption(self) -> float:
        """Computes fuel consumption applying the difficulty formula:
        Fuel = fuelCost * (1.0 + 0.1 * (difficulty - 1))
        """
        multiplier = 1.0 + 0.1 * (self.difficulty - 1)
        return self.fuelCost * multiplier

    def effective_travel_time(self) -> float:
        """Computes effective travel time considering RESTRICTED status and speed caps."""
        time = self.baseTime
        if self.status == EdgeStatus.RESTRICTED:
            time *= 1.5  # 50% time penalty under restriction
        if self.speed_cap < 1.0 and self.speed_cap > 0:
            time /= self.speed_cap
        if self.hazard_level > 0:
            time *= (1.0 + 0.3 * self.hazard_level)
        return time

    def compute_scalar_cost(self, preset: RoutingPreset = RoutingPreset.BALANCED) -> float:
        """Computes the normalized scalar edge cost:
        cost(e) = w_d * D(e) + w_t * T(e) + w_f * F(e) + w_r * R(e) + w_o * O(e)
        Guaranteed non-negative to satisfy Dijkstra invariants.
        """
        if self.status == EdgeStatus.BLOCKED:
            return float('inf')

        w_d, w_t, w_f, w_r, w_o = PRESET_WEIGHTS[preset]

        # Normalized dimensionless attributes
        norm_d = min(1.0, self.distance / REF_DISTANCE)
        norm_t = min(1.0, self.effective_travel_time() / REF_TIME)
        norm_f = min(1.0, self.effective_fuel_consumption() / REF_FUEL)
        norm_r = (self.difficulty - 1) / 4.0  # Maps 1..5 to 0.0..1.0
        norm_o = min(1.0, max(0.0, self.hazard_level))

        # Scalar combined cost (always non-negative)
        cost = (w_d * norm_d +
                w_t * norm_t +
                w_f * norm_f +
                w_r * norm_r +
                w_o * norm_o)
        return max(0.0, cost)
