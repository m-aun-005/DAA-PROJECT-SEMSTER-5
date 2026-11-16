"""tests/test_graph.py — Unit tests for Graph data structure and edge cost normalization.
"""

import pytest
from src.core.graph import Graph
from src.models.vertex import Vertex, VertexType
from src.models.edge import Edge, EdgeStatus, RoutingPreset


def test_add_vertex_and_edge():
    g = Graph()
    v1 = Vertex(id=1, x=100, y=100, type=VertexType.START)
    v2 = Vertex(id=2, x=200, y=200, type=VertexType.CHECKPOINT, checkpointOrder=1)
    g.add_vertex(v1)
    g.add_vertex(v2)

    e = Edge(id=1, from_vertex=1, to_vertex=2, distance=141.4, baseTime=1.4, fuelCost=10.0, difficulty=1, directed=False)
    g.add_edge(e)

    assert len(g.vertices) == 2
    assert len(g.edges) == 1
    assert len(g.get_outgoing_edges(1)) == 1
    assert len(g.get_outgoing_edges(2)) == 1  # undirected has reciprocal


def test_edge_blocking_dynamic():
    g = Graph()
    v1 = Vertex(id=1, x=0, y=0)
    v2 = Vertex(id=2, x=10, y=10)
    g.add_vertex(v1)
    g.add_vertex(v2)
    e = Edge(id=1, from_vertex=1, to_vertex=2, distance=14.1, baseTime=1.0, fuelCost=2.0)
    g.add_edge(e)

    assert len(g.get_outgoing_edges(1, traversable_only=True)) == 1
    g.set_edge_status(1, EdgeStatus.BLOCKED)
    assert len(g.get_outgoing_edges(1, traversable_only=True)) == 0
    g.set_edge_status(1, EdgeStatus.OPEN)
    assert len(g.get_outgoing_edges(1, traversable_only=True)) == 1


def test_routing_preset_costs():
    e = Edge(id=1, from_vertex=1, to_vertex=2, distance=100.0, baseTime=5.0, fuelCost=15.0, difficulty=3)
    c_bal = e.compute_scalar_cost(RoutingPreset.BALANCED)
    c_spd = e.compute_scalar_cost(RoutingPreset.SPEED)
    c_eco = e.compute_scalar_cost(RoutingPreset.ECONOMY)
    c_saf = e.compute_scalar_cost(RoutingPreset.SAFETY)

    assert c_bal > 0
    assert c_spd > 0
    assert c_eco > 0
    assert c_saf > 0
    # Different weight profiles must produce distinct scalar costs
    assert len({round(c_bal, 4), round(c_spd, 4), round(c_eco, 4), round(c_saf, 4)}) >= 3
