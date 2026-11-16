"""src/data/circuits/circuit_alpha.py — Circuit 1: "Alpha Ring" (High-Speed Ring).
Contains 10 mandatory checkpoints, 2 shortcuts, 1 dead end, 2 fuel stations, 3 nitro pickups,
and pre-scheduled dynamic events.
"""

from __future__ import annotations
import math
from src.core.graph import Graph
from src.models.vertex import Vertex, VertexType
from src.models.edge import Edge, EdgeStatus
from src.models.event import RaceEvent, EventType
from src.models.circuit import Circuit


def build_circuit_alpha() -> Circuit:
    g = Graph()

    # Vertices (10 mandatory checkpoints + Start/Finish + Services + Dead End)
    vertices_data = [
        # (id, x, y, type, cp_order, label)
        (1,  350.0, 360.0, VertexType.START, None, "START/FINISH"),
        (2,  420.0, 220.0, VertexType.CHECKPOINT, 1, "CP1"),
        (3,  580.0, 140.0, VertexType.CHECKPOINT, 2, "CP2"),
        (4,  750.0, 130.0, VertexType.CHECKPOINT, 3, "CP3"),
        (5,  950.0, 180.0, VertexType.CHECKPOINT, 4, "CP4"),
        (6, 1080.0, 300.0, VertexType.CHECKPOINT, 5, "CP5"),
        (7, 1080.0, 450.0, VertexType.CHECKPOINT, 6, "CP6"),
        (8,  960.0, 580.0, VertexType.CHECKPOINT, 7, "CP7"),
        (9,  750.0, 600.0, VertexType.CHECKPOINT, 8, "CP8"),
        (10, 550.0, 580.0, VertexType.CHECKPOINT, 9, "CP9"),
        (11, 390.0, 480.0, VertexType.CHECKPOINT, 10, "CP10"),
        
        # Dead End vertex
        (12, 1180.0, 160.0, VertexType.DEAD_END, None, "DEAD-END"),

        # Fuel Stations
        (13, 500.0, 180.0, VertexType.FUEL_STATION, None, "GAS-NORTH"),
        (14, 850.0, 590.0, VertexType.FUEL_STATION, None, "GAS-SOUTH"),

        # Nitro Pickups
        (15, 850.0, 150.0, VertexType.NITRO_PICKUP, None, "NITRO-1"),
        (16, 650.0, 590.0, VertexType.NITRO_PICKUP, None, "NITRO-2"),
        (17, 1080.0, 375.0, VertexType.NITRO_PICKUP, None, "NITRO-3"),
        
        # Intersections
        (18, 660.0, 260.0, VertexType.INTERSECTION, None, "CHORD-N"),
        (19, 660.0, 460.0, VertexType.INTERSECTION, None, "CHORD-S"),
    ]

    for vid, x, y, vtype, cp_ord, lbl in vertices_data:
        g.add_vertex(Vertex(id=vid, x=x, y=y, type=vtype, checkpointOrder=cp_ord, label=lbl))

    # Helper function to add edges
    edge_id_counter = 1
    shortcut_edge_ids = []

    def make_edge(u: int, v: int, diff: int = 1, is_sc: bool = False, directed: bool = False) -> Edge:
        nonlocal edge_id_counter
        vu = g.vertices[u]
        vv = g.vertices[v]
        dist = math.hypot(vv.x - vu.x, vv.y - vu.y)
        base_time = dist / 100.0
        fuel_cost = (dist / 100.0) * 8.0
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

    # Main Ring track edges
    make_edge(1, 2, diff=1)    # Start -> CP1
    make_edge(2, 13, diff=1)   # CP1 -> Gas North
    make_edge(13, 3, diff=1)   # Gas North -> CP2
    make_edge(3, 4, diff=2)    # CP2 -> CP3
    make_edge(4, 15, diff=2)   # CP3 -> Nitro 1
    make_edge(15, 5, diff=2)   # Nitro 1 -> CP4
    make_edge(5, 6, diff=2)    # CP4 -> CP5
    make_edge(6, 17, diff=1)   # CP5 -> Nitro 3
    make_edge(17, 7, diff=1)   # Nitro 3 -> CP6
    make_edge(7, 8, diff=2)    # CP6 -> CP7
    make_edge(8, 14, diff=1)   # CP7 -> Gas South
    make_edge(14, 9, diff=1)   # Gas South -> CP8
    make_edge(9, 16, diff=1)   # CP8 -> Nitro 2
    make_edge(16, 10, diff=1)  # Nitro 2 -> CP9
    make_edge(10, 11, diff=1)  # CP9 -> CP10
    make_edge(11, 1, diff=1)   # CP10 -> START

    # Alternative Route & Shortcuts (>= 2 shortcuts)
    # Shortcut 1: Cut across North Loop from CP2 (3) to CP4 (5) via Chord-N (18)
    make_edge(3, 18, diff=3, is_sc=True)
    make_edge(18, 5, diff=4, is_sc=True)

    # Shortcut 2: Cut across South Loop from CP7 (8) to CP10 (11) via Chord-S (19)
    make_edge(8, 19, diff=4, is_sc=True)
    make_edge(19, 11, diff=3, is_sc=True)

    # Dead end branch (from CP4 to Dead-end 12)
    make_edge(5, 12, diff=1, directed=False)

    # Scheduled dynamic events (Section 4.5)
    events = [
        RaceEvent(
            eventId=1,
            triggerTime=12.0,
            priority=1,
            insertionSequence=1,
            type=EventType.ROAD_BLOCKAGE,
            targetEdgeOrVertex=4,  # Blocks edge between CP3 and Nitro 1
            duration=15.0,
            description="Rock slide on North Curve! Road blocked."
        ),
        RaceEvent(
            eventId=2,
            triggerTime=22.0,
            priority=3,
            insertionSequence=2,
            type=EventType.OIL_SPILL,
            targetEdgeOrVertex=9,  # Oil on South Straight
            duration=20.0,
            description="Oil spill on South Sector! Hazard increased."
        ),
        RaceEvent(
            eventId=3,
            triggerTime=35.0,
            priority=2,
            insertionSequence=3,
            type=EventType.SHORTCUT_TOGGLE,
            targetEdgeOrVertex=shortcut_edge_ids[0],
            duration=25.0,
            description="North Shortcut closed due to debris!"
        ),
        RaceEvent(
            eventId=4,
            triggerTime=48.0,
            priority=4,
            insertionSequence=4,
            type=EventType.SPEED_RESTRICTION,
            targetEdgeOrVertex=7,
            duration=15.0,
            description="Yellow flag speed cap in Sector 2!"
        ),
    ]

    return Circuit(
        id=1,
        name="Alpha Ring",
        description="High-speed perimeter oval with high-risk central chord shortcuts and north dead-end canyon.",
        graph=g,
        start_vertex_id=1,
        finish_vertex_id=1,
        checkpoint_ids=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        shortcut_edge_ids=shortcut_edge_ids,
        fuel_station_ids=[13, 14],
        nitro_pickup_ids=[15, 16, 17],
        dead_end_ids=[12],
        scheduled_events=events
    )
