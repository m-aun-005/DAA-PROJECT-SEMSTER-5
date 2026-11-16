"""src/models/leaderboard.py — Championship Scoring & Multi-tier Comparator (Section 4.6).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# F1 Standard Scoring System (Section 4.6)
POSITION_POINTS: Dict[int, int] = {
    1: 25,
    2: 18,
    3: 15,
    4: 12,
    5: 10,
    6: 8,
    7: 6,
    8: 4,
    9: 2,
    10: 1,
}


@dataclass
class RaceResult:
    """Result of a single race for one competitor."""
    raceId: int
    racerId: int
    racerName: str
    finishPosition: int         # 1-indexed (999 for DNF)
    finishTime: float           # total elapsed race time
    fastestLap: float
    bonusPoints: int = 0
    pointsAwarded: int = 0
    dnf: bool = False

    def __post_init__(self):
        if self.dnf:
            self.pointsAwarded = 0
        else:
            self.pointsAwarded = POSITION_POINTS.get(self.finishPosition, 0) + self.bonusPoints


@dataclass
class ChampionshipEntry:
    """Season standings record for a competitor.
    
    Comparator follows Section 4.6 total order:
    1. Higher championship points
    2. Higher race wins
    3. Lower sum of finish positions
    4. Lower best fastest-lap time
    5. Lower racer ID
    """
    racerId: int
    name: str
    totalPoints: int = 0
    wins: int = 0
    sumOfFinishPositions: int = 0
    bestFastestLap: float = float('inf')
    raceHistory: List[RaceResult] = field(default_factory=list)

    def add_result(self, result: RaceResult) -> None:
        self.raceHistory.append(result)
        self.totalPoints += result.pointsAwarded
        if result.finishPosition == 1 and not result.dnf:
            self.wins += 1
        pos = result.finishPosition if not result.dnf else 20
        self.sumOfFinishPositions += pos
        if result.fastestLap < self.bestFastestLap:
            self.bestFastestLap = result.fastestLap

    def sort_key(self) -> Tuple[int, int, int, float, int]:
        """Returns comparison tuple for sorting algorithms.
        Since standard sorting sorts in ascending order:
        - Points: negated (-totalPoints) so higher points sort first
        - Wins: negated (-wins) so more wins sort first
        - Sum of positions: positive (lower is better)
        - Best fastest lap: positive (lower time is better)
        - Racer ID: positive (lower ID wins final tie-break)
        """
        return (
            -self.totalPoints,
            -self.wins,
            self.sumOfFinishPositions,
            self.bestFastestLap,
            self.racerId
        )

    def is_better_than(self, other: ChampionshipEntry) -> bool:
        """Total strict comparator."""
        return self.sort_key() < other.sort_key()
