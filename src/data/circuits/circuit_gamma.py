"""src/data/circuits/circuit_gamma.py — Circuit 3: "Gamma Grid" (Urban Grid Network).
Features urban street grid layout with one-way avenues, multiple alternative routes,
3 diagonal alley shortcuts, 1 dead-end alley, 3 fuel stations, 4 nitro pickups, and dynamic events.
"""

from __future__ import annotations
import math
from src.core.graph import Graph
from src.models.vertex import Vertex, VertexType
from src.models.edge import Edge, EdgeStatus
from src.models.event import RaceEvent, EventType
from src.models.circuit import Circuit


def build_circuit_gamma() -> Circuit:
    g = Graph()

    # 5x4 Grid layout vertices
    # Columns: 350, 525, 700, 875, 1050
    # Rows: 150, 300, 450, 600
    vertices_data = [
        # Row 0 (y = 150)
        (1,   350.0, 150.0, VertexType.START, None, "START/FINISH"),
        (2,   525.0, 150.0, VertexType.CHECKPOINT, 1, "CP1"),
        (3,   700.0, 150.0, VertexType.CHECKPOINT, 2, "CP2"),
        (4,   875.0, 150.0, VertexType.CHECKPOINT, 3, "CP3"),
        (5,  1050.0, 150.0, VertexType.INTERSECTION, None, "CORNER-NE"),

        # Row 1 (y = 300)
        (6,   350.0, 300.0, VertexType.CHECKPOINT, 10, "CP10"),
        (7,   525.0, 300.0, VertexType.INTERSECTION, None, "INT-11"),
        (8,   700.0, 300.0, VertexType.CHECKPOINT, 4, "CP4"),
        (9,   875.0, 300.0, VertexType.INTERSECTION, None, "INT-13"),
        (10, 1050.0, 300.0, VertexType.CHECKPOINT, 5, "CP5"),

        # Row 2 (y = 450)
        (11,  350.0, 450.0, VertexType.CHECKPOINT, 9, "CP9"),
        (12,  525.0, 450.0, VertexType.INTERSECTION, None, "INT-21"),
        (13,  700.0, 450.0, VertexType.CHECKPOINT, 7, "CP7"),
        (14,  875.0, 450.0, VertexType.CHECKPOINT, 6, "CP6"),
        (15, 1050.0, 450.0, VertexType.INTERSECTION, None, "CORNER-SE"),

        # Row 3 (y = 600)
        (16,  350.0, 600.0, VertexType.INTERSECTION, None, "CORNER-SW"),
        (17,  525.0, 600.0, VertexType.CHECKPOINT, 8, "CP8"),
        (18,  700.0, 600.0, VertexType.INTERSECTION, None, "INT-32"),
        (19,  875.0, 600.0, VertexType.INTERSECTION, None, "INT-33"),
        (20, 1050.0, 600.0, VertexType.INTERSECTION, None, "SUBURB"),

        # Dead End (Cul-de-sac)
        (21, 1150.0, 600.0, VertexType.DEAD_END, None, "DEAD-END"),

        # Fuel Stations (3 stations)
        (22,  610.0, 150.0, VertexType.FUEL_STATION, None, "GAS-NORTH"),
        (23, 1050.0, 375.0, VertexType.FUEL_STATION, None, "GAS-EAST"),
        (24,  610.0, 600.0, VertexType.FUEL_STATION, None, "GAS-SOUTH"),

        # Nitro Pickups (4 pickups)
        (25,  780.0, 150.0, VertexType.NITRO_PICKUP, None, "NITRO-1"),
        (26,  700.0, 375.0, VertexType.NITRO_PICKUP, None, "NITRO-2"),
        (27,  960.0, 450.0, VertexType.NITRO_PICKUP, None, "NITRO-3"),
        (28,  350.0, 525.0, VertexType.NITRO_PICKUP, None, "NITRO-4"),
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

    # Perimeter and arterial streets
    # Top Avenue: Start (1) -> CP1 (2) -> Gas-N (22) -> CP2 (3) -> Nitro-1 (25) -> CP3 (4) -> Corner-NE (5)
    make_edge(1, 2, diff=1, directed=True)
    make_edge(2, 22, diff=1, directed=True)
    make_edge(22, 3, diff=1, directed=True)
    make_edge(3, 25, diff=1, directed=True)
    make_edge(25, 4, diff=1, directed=True)
    make_edge(4, 5, diff=1, directed=True)

    # East Boulevard: Corner-NE (5) -> CP5 (10) -> Gas-East (23) -> Corner-SE (15) -> Suburb (20)
    make_edge(5, 10, diff=2, directed=True)
    make_edge(10, 23, diff=1, directed=True)
    make_edge(23, 15, diff=1, directed=True)
    make_edge(15, 20, diff=2, directed=False)

    # South Avenue: Suburb (20) -> INT-33 (19) -> INT-32 (18) -> Gas-South (24) -> CP8 (17) -> Corner-SW (16)
    make_edge(20, 19, diff=1, directed=True)
    make_edge(19, 18, diff=1, directed=True)
    make_edge(18, 24, diff=1, directed=True)
    make_edge(24, 17, diff=1, directed=True)
    make_edge(17, 16, diff=1, directed=True)

    # West Boulevard: Corner-SW (16) -> Nitro-4 (28) -> CP9 (11) -> CP10 (6) -> Start (1)
    make_edge(16, 28, diff=1, directed=True)
    make_edge(28, 11, diff=1, directed=True)
    make_edge(11, 6, diff=1, directed=True)
    make_edge(6, 1, diff=1, directed=True)

    # Internal Grid connectors (intersections & checkpoint links)
    make_edge(4, 8, diff=2, directed=True)      # CP3 -> CP4
    make_edge(8, 10, diff=2, directed=False)    # CP4 <-> CP5
    make_edge(10, 14, diff=2, directed=True)    # CP5 -> CP6
    make_edge(14, 27, diff=2, directed=True)    # CP6 -> Nitro-3
    make_edge(27, 13, diff=2, directed=True)    # Nitro-3 -> CP7
    make_edge(13, 17, diff=2, directed=True)    # CP7 -> CP8
    make_edge(17, 11, diff=2, directed=False)   # CP8 <-> CP9
    make_edge(8, 26, diff=2, directed=True)     # CP4 -> Nitro-2
    make_edge(26, 13, diff=2, directed=True)    # Nitro-2 -> CP7

    # Additional cross streets
    make_edge(2, 7, diff=1, directed=False)
    make_edge(7, 12, diff=1, directed=False)
    make_edge(12, 17, diff=1, directed=False)
    make_edge(7, 8, diff=2, directed=False)
    make_edge(12, 13, diff=2, directed=False)
    make_edge(9, 14, diff=1, directed=False)

    # 3 High-Speed Shortcuts (Diagonals through alleys)
    make_edge(2, 8, diff=4, is_sc=True, directed=True)    # CP1 directly to CP4
    make_edge(8, 14, diff=4, is_sc=True, directed=True)   # CP4 directly to CP6
    make_edge(13, 11, diff=4, is_sc=True, directed=True)  # CP7 directly to CP9

    # Dead End off Suburb (20)
    make_edge(20, 21, diff=1, directed=False)

    # Scheduled dynamic events
    events = [
        RaceEvent(
            eventId=1,
            triggerTime=10.0,
            priority=1,
            insertionSequence=1,
            type=EventType.ROAD_BLOCKAGE,
            targetEdgeOrVertex=2,  # Blocks North Avenue segment
            duration=20.0,
            description="Water main break on North Avenue! Road closed."
        ),
        RaceEvent(
            eventId=2,
            triggerTime=18.0,
            priority=2,
            insertionSequence=2,
            type=EventType.SHORTCUT_TOGGLE,
            targetEdgeOrVertex=shortcut_edge_ids[0],
            duration=25.0,
            description="Urban diagonal shortcut open for traffic!"
        ),
        RaceEvent(
            eventId=3,
            triggerTime=30.0,
            priority=3,
            insertionSequence=3,
            type=EventType.OIL_SPILL,
            targetEdgeOrVertex=14,
            duration=18.0,
            description="Oil slick detected at Downtown intersection!"
        ),
        RaceEvent(
            eventId=4,
            triggerTime=45.0,
            priority=4,
            insertionSequence=4,
            type=EventType.SPEED_RESTRICTION,
            targetEdgeOrVertex=9,
            duration=20.0,
            description="School zone 30 km/h speed cap active!"
        ),
    ]

    return Circuit(
        id=3,
        name="Gamma Grid",
        description="Complex downtown grid network featuring one-way thoroughfares, diagonal alleys, and detour labyrinths.",
        graph=g,
        start_vertex_id=1,
        finish_vertex_id=1,
        checkpoint_ids=[2, 3, 4, 8, 10, 14, 13, 17, 11, 6],
        shortcut_edge_ids=shortcut_edge_ids,
        fuel_station_ids=[22, 23, 24],
        nitro_pickup_ids=[25, 26, 27, 28],
        dead_end_ids=[21],
        scheduled_events=events
    )
