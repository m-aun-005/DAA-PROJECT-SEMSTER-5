"""src/engine/race_engine.py — Core Racing Simulation Engine (Section 4).
Orchestrates vehicle physics, checkpoint tracking, pit stops, dynamic event queue,
and race results generation.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from src.core.graph import Graph
from src.models.circuit import Circuit
from src.models.vehicle import Vehicle, VehicleState, AIStrategy
from src.models.vertex import VertexType
from src.models.leaderboard import RaceResult, ChampionshipEntry
from src.engine.event_engine import EventEngine
from src.engine.route_planner import RoutePlanner
from src.engine.ai_controller import AIController


class RaceEngine:
    """Complete simulation manager for the Smart Racing Championship."""

    def __init__(self, circuit: Circuit, total_laps: int = 2):
        self.circuit = circuit
        self.graph = circuit.graph
        self.total_laps = total_laps
        self.current_time: float = 0.0
        self.is_running: bool = False
        self.is_finished: bool = False

        self.route_planner = RoutePlanner(self.graph)
        self.event_engine = EventEngine(self.graph)
        self.event_engine.load_events(circuit.scheduled_events)

        # Competitors: 1 Human + 3 AI opponents
        self.vehicles: List[Vehicle] = self._create_racers()
        self.ai_controllers: Dict[int, AIController] = {}
        for veh in self.vehicles:
            if not veh.isHuman:
                self.ai_controllers[veh.id] = AIController(veh, circuit, self.route_planner)

        # Race tracking
        self.next_finish_position: int = 1
        self.results: List[RaceResult] = []
        self.leaderboard_records: List[ChampionshipEntry] = []

    def _create_racers(self) -> List[Vehicle]:
        """Creates the 4 default competitors."""
        start_v = self.circuit.start_vertex_id
        return [
            Vehicle(
                id=1,
                name="Player (Human)",
                isHuman=True,
                strategyType=AIStrategy.HUMAN,
                color=(230, 50, 50),     # Red
                currentVertex=start_v,
                fuel=100.0,
                nitroCharges=2
            ),
            Vehicle(
                id=2,
                name="Racer 2 (Conservative)",
                isHuman=False,
                strategyType=AIStrategy.OPPONENT_1_FIXED,
                color=(50, 120, 240),    # Blue
                currentVertex=start_v,
                fuel=100.0,
                nitroCharges=1
            ),
            Vehicle(
                id=3,
                name="Racer 3 (Aggressive)",
                isHuman=False,
                strategyType=AIStrategy.OPPONENT_2_SHORTCUT,
                color=(240, 180, 20),    # Yellow
                currentVertex=start_v,
                fuel=100.0,
                nitroCharges=2
            ),
            Vehicle(
                id=4,
                name="Racer 4 (Optimal Distance)",
                isHuman=False,
                strategyType=AIStrategy.OPPONENT_3_OPTIMAL,
                color=(50, 200, 120),    # Green
                currentVertex=start_v,
                fuel=100.0,
                nitroCharges=1
            ),
        ]

    def start_race(self) -> None:
        """Starts the race."""
        self.is_running = True
        self.is_finished = False
        self.current_time = 0.0

        for veh in self.vehicles:
            veh.state = VehicleState.RACING
            veh.currentVertex = self.circuit.start_vertex_id
            veh.targetVertex = None
            veh.progress = 0.0
            veh.lap = 1
            veh.nextCheckpoint = 1
            veh.checkpoints_visited_this_lap.clear()
            veh.totalTime = 0.0
            veh.currentLapTime = 0.0
            veh.bestFastestLap = float('inf')
            veh.finishPosition = None
            veh.dnf = False

            # Assign first target vertex
            if veh.isHuman:
                out = self.graph.get_outgoing_edges(veh.currentVertex, traversable_only=True)
                if out:
                    veh.targetVertex = out[0].to_vertex
                    veh.current_edge_id = out[0].id
            else:
                ai = self.ai_controllers.get(veh.id)
                if ai:
                    tgt = ai.decide_next_target()
                    if tgt is not None:
                        e = self.graph.edge_between(veh.currentVertex, tgt)
                        if e:
                            veh.targetVertex = tgt
                            veh.current_edge_id = e.id

    def tick(self, dt: float) -> None:
        """Advances simulation by dt seconds."""
        if not self.is_running or self.is_finished:
            return

        self.current_time += dt

        # Process dynamic race events from min-heap
        self.event_engine.tick(self.current_time)

        all_done = True
        for veh in self.vehicles:
            if veh.state in (VehicleState.FINISHED, VehicleState.DNF):
                continue

            all_done = False
            active_edge = self.graph.get_edge(veh.current_edge_id) if veh.current_edge_id else None

            # Advance vehicle physics
            arrived = veh.update_physics(dt, active_edge)

            if arrived:
                self._handle_vertex_arrival(veh)

        if all_done and not self.is_finished:
            self._finalize_race()

    def _handle_vertex_arrival(self, veh: Vehicle) -> None:
        """Processes logic when a vehicle reaches its targetVertex."""
        u = veh.currentVertex
        v_obj = self.graph.get_vertex(u)

        if v_obj is None:
            return

        # 1. Checkpoint Check (Invariant: in order 1..10)
        if v_obj.is_mandatory_checkpoint():
            veh.record_checkpoint(v_obj.checkpointOrder)

        # 2. Start / Finish Line Crossing Check
        if u == self.circuit.finish_vertex_id:
            if len(veh.checkpoints_visited_this_lap) >= len(self.circuit.checkpoint_ids):
                veh.complete_lap(total_checkpoints=len(self.circuit.checkpoint_ids))
                if veh.lap > self.total_laps:
                    # Vehicle has finished the race!
                    veh.state = VehicleState.FINISHED
                    veh.finishPosition = self.next_finish_position
                    self.next_finish_position += 1
                    return

        # 3. Service Vertices: Fuel Station & Nitro Pickups
        if v_obj.type == VertexType.FUEL_STATION and v_obj.active:
            if veh.fuel < 70.0:  # Take refuel stop
                purchase = min(100.0 - veh.fuel, 40.0)
                veh.fuel += purchase
                veh.refuelTimer = 2.0  # 2.0s pit stop delay
                veh.state = VehicleState.REFUELLING

        elif v_obj.type == VertexType.NITRO_PICKUP and v_obj.active:
            if veh.nitroCharges < 3:
                veh.nitroCharges += 1

        # 4. Choose next target vertex
        if veh.isHuman:
            out_edges = self.graph.get_outgoing_edges(u, traversable_only=True)
            if out_edges:
                veh.targetVertex = out_edges[0].to_vertex
                veh.current_edge_id = out_edges[0].id
            else:
                veh.state = VehicleState.DNF
                veh.dnf = True
        else:
            ai = self.ai_controllers.get(veh.id)
            if ai:
                tgt = ai.decide_next_target()
                if tgt is not None:
                    e = self.graph.edge_between(u, tgt)
                    if e and e.is_traversable:
                        veh.targetVertex = tgt
                        veh.current_edge_id = e.id
                    else:
                        veh.state = VehicleState.DNF
                        veh.dnf = True
                else:
                    veh.state = VehicleState.DNF
                    veh.dnf = True

    def _finalize_race(self) -> None:
        """Assigns points, ranks finishers, and computes official results."""
        self.is_running = False
        self.is_finished = True

        # Sort finishers: by finishPosition (DNF goes last, ordered by laps completed descending)
        ranked = sorted(
            self.vehicles,
            key=lambda v: (
                1 if v.dnf else 0,
                v.finishPosition if v.finishPosition is not None else 999,
                -v.lap,
                -len(v.checkpoints_visited_this_lap),
                v.totalTime,
                v.id
            )
        )

        self.results.clear()
        for pos, v in enumerate(ranked, start=1):
            res = RaceResult(
                raceId=1,
                racerId=v.id,
                racerName=v.name,
                finishPosition=pos if not v.dnf else 999,
                finishTime=round(v.totalTime, 2),
                fastestLap=round(v.bestFastestLap, 2) if v.bestFastestLap < float('inf') else 999.0,
                dnf=v.dnf
            )
            self.results.append(res)
