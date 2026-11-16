"""tests/test_dijkstra_astar.py — Unit tests for Dijkstra and A* (Act 2).
"""

import pytest
from src.core.graph import Graph
from src.core.dijkstra import Dijkstra
from src.core.astar import AStar
from src.models.vertex import Vertex
from src.models.edge import Edge, RoutingPreset


def test_dijkstra_optimality():
    g = Graph()
    g.add_vertex(Vertex(0, 0, 0))
    g.add_vertex(Vertex(1, 10, 0))
    g.add_vertex(Vertex(2, 20, 0))

    # Path 0 -> 1 -> 2: length 5 + 5 = 10
    # Direct 0 -> 2: length 25
    g.add_edge(Edge(1, 0, 1, 50.0, 1.0, 1.0, directed=True))
    g.add_edge(Edge(2, 1, 2, 50.0, 1.0, 1.0, directed=True))
    g.add_edge(Edge(3, 0, 2, 250.0, 10.0, 10.0, directed=True))

    dijkstra = Dijkstra(g)
    res = dijkstra.run(0, 2, preset=RoutingPreset.BALANCED)
    assert res["reachable"] is True
    assert res["path"] == [0, 1, 2]


def test_astar_agrees_with_dijkstra():
    g = Graph()
    for i in range(5):
        g.add_vertex(Vertex(i, i * 50.0, 0.0))
    for i in range(4):
        g.add_edge(Edge(i + 1, i, i + 1, 50.0, 1.0, 1.0, directed=False))

    d = Dijkstra(g)
    a = AStar(g)

    res_d = d.run(0, 4, preset=RoutingPreset.BALANCED)
    res_a = a.run(0, 4, preset=RoutingPreset.BALANCED)

    assert res_d["reachable"] is True
    assert res_a["reachable"] is True
    assert abs(res_d["cost"] - res_a["cost"]) < 1e-4
    assert res_d["path"] == res_a["path"]


def test_checkpoint_aware_route():
    g = Graph()
    for i in range(4):
        g.add_vertex(Vertex(i, i * 50, 0))
    g.add_edge(Edge(1, 0, 1, 10, 1, 1, directed=True))
    g.add_edge(Edge(2, 1, 2, 10, 1, 1, directed=True))
    g.add_edge(Edge(3, 2, 3, 10, 1, 1, directed=True))

    d = Dijkstra(g)
    # Checkpoint order 0 -> 1 -> 2 -> 3
    res = d.checkpoint_aware_route(0, [1, 2, 3])
    assert res["reachable"] is True
    assert res["path"] == [0, 1, 2, 3]
