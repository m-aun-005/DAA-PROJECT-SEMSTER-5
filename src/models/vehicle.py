"""src/models/vehicle.py — Vehicle and Racer state modeling matching Section 3.2 & 4.3.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple
from src.models.edge import Edge


class VehicleState(str, Enum):
    IDLE = "Idle"
    RACING = "Racing"
    REFUELLING = "Refuelling"
    NITRO_ACTIVE = "NitroActive"
    FINISHED = "Finished"
    DNF = "DidNotFinish"


class AIStrategy(str, Enum):
    HUMAN = "Human"
    OPPONENT_1_FIXED = "FixedMainRoute"          # Fixed main route + fixed detour
    OPPONENT_2_SHORTCUT = "ShortcutHunter"       # Uses shortcuts whenever open
    OPPONENT_3_OPTIMAL = "DynamicShortestPath"   # Minimum distance dynamic recalculation


@dataclass
class Vehicle:
    """Represents a racing competitor (human or computer opponent).
    
    Attributes matching Section 3.2:
        id: Unique racer identifier (also used as final tie-breaker).
        name: Racer display name.
        isHuman: True if user-controlled.
        strategyType: AIStrategy classification.
        currentVertex: Vertex currently occupying or last departed from.
        targetVertex: Vertex currently travelling toward.
        progress: Fractional distance travelled on current edge [0.0, 1.0].
        fuel: Current fuel level (0.0 to 100.0).
        nitroCharges: Available nitro charges (0 to 3).
        nitroTimer: Remaining time for active nitro boost (seconds).
        lap: Current lap number (1-indexed).
        nextCheckpoint: Next required mandatory checkpoint index (1..10).
        totalTime: Cumulative race elapsed time (seconds).
        currentLapTime: Time spent on current lap.
        bestFastestLap: Best single lap time (infinity if none completed).
        finishPosition: Assigned finishing position (1st, 2nd, etc.) or None.
        dnf: True if Did Not Finish due to fuel starvation or impassable road.
        color: RGB tuple for rendering.
        current_edge_id: ID of the active edge being traversed.
        checkpoints_visited_this_lap: Set of checkpoint orders completed this lap.
    """
    id: int
    name: str
    isHuman: bool = False
    strategyType: AIStrategy = AIStrategy.OPPONENT_1_FIXED
    color: Tuple[int, int, int] = (255, 255, 255)
    
    # State & Location
    currentVertex: int = 0
    targetVertex: Optional[int] = None
    previousVertex: Optional[int] = None
    steer_intent: Optional[str] = None
    progress: float = 0.0
    current_edge_id: Optional[int] = None
    state: VehicleState = VehicleState.IDLE

    # Resources
    fuel: float = 100.0
    nitroCharges: int = 1
    nitroTimer: float = 0.0
    refuelTimer: float = 0.0

    # Race Progress
    lap: int = 1
    nextCheckpoint: int = 1
    checkpoints_visited_this_lap: List[int] = field(default_factory=list)
    totalTime: float = 0.0
    currentLapTime: float = 0.0
    bestFastestLap: float = float('inf')
    finishPosition: Optional[int] = None
    dnf: bool = False

    # Base physics
    base_speed: float = 120.0  # pixels per second

    @property
    def current_speed(self) -> float:
        """Computes current speed applying nitro (1.5x) or refuelling (0.0)."""
        if self.state in (VehicleState.DNF, VehicleState.FINISHED, VehicleState.IDLE):
            return 0.0
        if self.state == VehicleState.REFUELLING:
            return 0.0
        speed = self.base_speed
        if self.nitroTimer > 0:
            speed *= 1.5  # 1.5x speed during nitro
        return speed

    def activate_nitro(self) -> bool:
        """Activates one nitro charge for 4.0 seconds if available."""
        if self.nitroCharges > 0 and self.nitroTimer <= 0 and self.state == VehicleState.RACING:
            self.nitroCharges -= 1
            self.nitroTimer = 4.0
            self.state = VehicleState.NITRO_ACTIVE
            return True
        return False

    def update_physics(self, dt: float, edge: Optional[Edge] = None) -> bool:
        """Updates vehicle position, fuel, nitro, and lap timers over timestep dt.
        Returns True if vehicle arrived at targetVertex this tick.
        """
        if self.state in (VehicleState.DNF, VehicleState.FINISHED, VehicleState.IDLE):
            return False

        self.totalTime += dt
        self.currentLapTime += dt

        # Handle refuelling pause
        if self.state == VehicleState.REFUELLING:
            self.refuelTimer -= dt
            if self.refuelTimer <= 0:
                self.state = VehicleState.RACING
            return False

        # Handle nitro timer
        if self.nitroTimer > 0:
            self.nitroTimer -= dt
            if self.nitroTimer <= 0:
                self.nitroTimer = 0.0
                if self.state == VehicleState.NITRO_ACTIVE:
                    self.state = VehicleState.RACING

        # Check edge traversal
        if edge is None or self.targetVertex is None or edge.distance <= 0:
            return False

        # Calculate movement
        effective_speed = self.current_speed * edge.speed_cap
        dist_moved = effective_speed * dt
        fraction_moved = dist_moved / edge.distance

        # Fuel consumption
        # Nitro incurs 2x fuel penalty
        nitro_penalty = 2.0 if self.nitroTimer > 0 else 1.0
        fuel_rate = edge.effective_fuel_consumption() / edge.distance  # fuel per pixel
        consumed = fuel_rate * dist_moved * nitro_penalty
        self.fuel = max(0.0, self.fuel - consumed)

        # Starvation check
        if self.fuel <= 0.0:
            self.fuel = 0.0
            self.state = VehicleState.DNF
            self.dnf = True
            return False

        # Advance along edge
        self.progress += fraction_moved
        if self.progress >= 1.0:
            self.progress = 0.0
            self.previousVertex = self.currentVertex
            self.currentVertex = self.targetVertex
            self.targetVertex = None
            self.current_edge_id = None
            return True

        return False

    def record_checkpoint(self, checkpoint_order: int) -> bool:
        """Records visiting a mandatory checkpoint.
        Strict sequential ordering invariant: checkpoint must equal nextCheckpoint.
        """
        if checkpoint_order == self.nextCheckpoint:
            self.checkpoints_visited_this_lap.append(checkpoint_order)
            self.nextCheckpoint += 1
            return True
        return False

    def complete_lap(self, total_checkpoints: int = 10) -> bool:
        """Called when crossing the finish line. Lap counts ONLY if all checkpoints visited."""
        if len(self.checkpoints_visited_this_lap) >= total_checkpoints:
            if self.currentLapTime < self.bestFastestLap:
                self.bestFastestLap = self.currentLapTime
            self.currentLapTime = 0.0
            self.checkpoints_visited_this_lap.clear()
            self.nextCheckpoint = 1
            self.lap += 1
            return True
        return False
