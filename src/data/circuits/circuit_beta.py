"""src/data/circuits/circuit_beta.py — Circuit 2: "Beta Delta" (Figure-8 Topology).
Contains 10 mandatory checkpoints, figure-8 central crossover, 2 shortcuts, 2 dead ends,
3 fuel stations, 4 nitro pickups, and scheduled dynamic events.
"""

from __future__ import annotations
import math
from src.core.graph import Graph
from src.models.vertex import Vertex, VertexType
from src.models.edge import Edge, EdgeStatus
from src.models.event import RaceEvent, EventType
from src.models.circuit import Circuit


def build_circuit_beta() -> Circuit:
    g = Graph()

    vertices_data = [
        # West Loop (Start + CP1..CP5 + Center Crossing)
        (1,  350.0, 360.0, VertexType.START, None, "START/FINISH"),
        (2,  400.0, 220.0, VertexType.CHECKPOINT, 1, "CP1"),
        (3,  540.0, 180.0, VertexType.CHECKPOINT, 2, "CP2"),
        (4,  680.0, 260.0, VertexType.CHECKPOINT, 3, "CP3"),
        
        # Central Crossover Intersection
        (5,  750.0, 360.0, VertexType.INTERSECTION, None, "CROSSING"),

        # East Loop (CP4..CP8)
        (6,  820.0, 260.0, VertexType.CHECKPOINT, 4, "CP4"),
        (7,  960.0, 180.0, VertexType.CHECKPOINT, 5, "CP5"),
        (8, 1100.0, 240.0, VertexType.CHECKPOINT, 6, "CP6"),
        (9, 1120.0, 420.0, VertexType.CHECKPOINT, 7, "CP7"),
        (10, 980.0, 520.0, VertexType.CHECKPOINT, 8, "CP8"),
        (11, 830.0, 460.0, VertexType.CHECKPOINT, 9, "CP9"),

        # West Return Loop (CP10)
        (12, 650.0, 480.0, VertexType.CHECKPOINT, 10, "CP10"),
        (13, 480.0, 540.0, VertexType.INTERSECTION, None, "WEST-TURN"),
        (14, 380.0, 480.0, VertexType.INTERSECTION, None, "RETURN-CHUTE"),

        # Dead-Ends (2 dead ends)
        (15, 1190.0, 150.0, VertexType.DEAD_END, None, "DEAD-EAST"),
        (16,  310.0, 170.0, VertexType.DEAD_END, None, "DEAD-WEST"),

        # Fuel Stations (3 stations)
        (17,  460.0, 200.0, VertexType.FUEL_STATION, None, "GAS-1"),
        (18,  890.0, 210.0, VertexType.FUEL_STATION, None, "GAS-2"),
        (19,  570.0, 520.0, VertexType.FUEL_STATION, None, "GAS-3"),

        # Nitro Pickups (4 pickups)
        (20,  600.0, 220.0, VertexType.NITRO_PICKUP, None, "NITRO-1"),
        (21, 1050.0, 200.0, VertexType.NITRO_PICKUP, None, "NITRO-2"),
        (22, 1050.0, 480.0, VertexType.NITRO_PICKUP, None, "NITRO-3"),
        (23,  420.0, 520.0, VertexType.NITRO_PICKUP, None, "NITRO-4"),

        # Shortcut Connectors
        (24,  750.0, 200.0, VertexType.INTERSECTION, None, "BRIDGE-N"),
        (25,  750.0, 520.0, VertexType.INTERSECTION, None, "BRIDGE-S"),
    ]

    for vid, x, y, vtype, cp_ord, lbl in vertices_data:
        g.add_vertex(Vertex(id=vid, x=x, y=y, type=vtype, checkpointOrder=cp_ord, label=lbl))

    edge_id_counter = 1
    shortcut_edge_ids = []

    def make_edge(u: int, v: int, diff: int = 1, is_sc: bool = False, directed: bool = False) -> Edge:
        nonlocal edge_id_counter
        vu = g.vertices[u]
        vv = g.vertices[v]
        dist = math.hypot(vv.x - vu.x, vv.y - vu.y)
        base_time = dist / 110.0
        fuel_cost = (dist / 100.0) * 8.5
        e = Edge(
            id=edge_id_counter,
            from_vertex=u,
            to_vertex=v,
            distance=round(dist, 1),
            baseTime=round(base_time, 2),
            fuelCost=round(fuel_cost, 2),
            difficulty=diff,
            isShortcut=is_sc,
            directed=directed
        )
        edge_id_counter += 1
        if is_sc:
            shortcut_edge_ids.append(e.id)
        g.add_edge(e)
        return e

    # Main track edges
    make_edge(1, 2, diff=1)    # Start -> CP1
    make_edge(2, 17, diff=1)   # CP1 -> Gas 1
    make_edge(17, 3, diff=2)   # Gas 1 -> CP2
    make_edge(3, 20, diff=2)   # CP2 -> Nitro 1
    make_edge(20, 4, diff=2)   # Nitro 1 -> CP3
    make_edge(4, 5, diff=2)    # CP3 -> Crossing
    make_edge(5, 6, diff=2)    # Crossing -> CP4
    make_edge(6, 18, diff=1)   # CP4 -> Gas 2
    make_edge(18, 7, diff=1)   # Gas 2 -> CP5
    make_edge(7, 21, diff=2)   # CP5 -> Nitro 2
    make_edge(21, 8, diff=3)   # Nitro 2 -> CP6
    make_edge(8, 9, diff=2)    # CP6 -> CP7
    make_edge(9, 22, diff=2)   # CP7 -> Nitro 3
    make_edge(22, 10, diff=1)  # Nitro 3 -> CP8
    make_edge(10, 11, diff=2)  # CP8 -> CP9
    make_edge(11, 5, diff=2)   # CP9 -> Crossing
    make_edge(5, 12, diff=2)   # Crossing -> CP10
    make_edge(12, 19, diff=1)  # CP10 -> Gas 3
    make_edge(19, 13, diff=1)  # Gas 3 -> West Turn
    make_edge(13, 23, diff=1)  # West Turn -> Nitro 4
    make_edge(23, 14, diff=1)  # Nitro 4 -> Chute
    make_edge(14, 1, diff=1)   # Chute -> Start

    # Shortcuts (2 shortcuts)
    # Shortcut 1: North Bypass Bridge connecting CP3 (4) directly to CP5 (7) via Bridge-N (24)
    make_edge(4, 24, diff=4, is_sc=True)
    make_edge(24, 7, diff=4, is_sc=True)

    # Shortcut 2: South Bypass Bridge connecting CP9 (11) directly to Chute (14) via Bridge-S (25)
    make_edge(11, 25, diff=5, is_sc=True)
    make_edge(25, 14, diff=4, is_sc=True)

    # Dead Ends (2 dead ends)
    make_edge(8, 15, diff=1, directed=False)  # East dead end off CP6
    make_edge(2, 16, diff=1, directed=False)  # West dead end off CP1

    # Scheduled dynamic events
    events = [
        RaceEvent(
            eventId=1,
            triggerTime=15.0,
            priority=1,
            insertionSequence=1,
            type=EventType.ROAD_BLOCKAGE,
            targetEdgeOrVertex=6,  # Crossing to CP4 blocked!
            duration=18.0,
            description="Accident at Central Crossover! East entry blocked."
        ),
        RaceEvent(
            eventId=2,
            triggerTime=25.0,
            priority=2,
            insertionSequence=2,
            type=EventType.SHORTCUT_TOGGLE,
            targetEdgeOrVertex=shortcut_edge_ids[0],
            duration=20.0,
            description="North Bypass Bridge opened for traffic!"
        ),
        RaceEvent(
            eventId=3,
            triggerTime=38.0,
            priority=3,
            insertionSequence=3,
            type=EventType.OIL_SPILL,
            targetEdgeOrVertex=11,
            duration=22.0,
            description="Oil slick on East Hairpin! Speed reduced."
        ),
        RaceEvent(
            eventId=4,
            triggerTime=50.0,
            priority=5,
            insertionSequence=4,
            type=EventType.FUEL_STATION,
            targetEdgeOrVertex=18,
            duration=30.0,
            description="Pit Station 2 temporarily closed for maintenance."
        ),
    ]

    return Circuit(
        id=2,
        name="Beta Delta",
        description="Figure-8 crossover circuit with double loops, two high-speed bridges, and dead-end alleys.",
        graph=g,
        start_vertex_id=1,
        finish_vertex_id=1,
        checkpoint_ids=[2, 3, 4, 6, 7, 8, 9, 10, 11, 12],
        shortcut_edge_ids=shortcut_edge_ids,
        fuel_station_ids=[17, 18, 19],
        nitro_pickup_ids=[20, 21, 22, 23],
        dead_end_ids=[15, 16],
        scheduled_events=events
    )
