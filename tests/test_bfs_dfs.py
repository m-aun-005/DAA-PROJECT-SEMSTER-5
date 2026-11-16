"""tests/test_bfs_dfs.py — Unit tests for BFS & DFS (Act 1).
"""

import pytest
from src.core.graph import Graph
from src.core.bfs import BFS
from src.core.dfs import DFS
from src.models.vertex import Vertex, VertexType
from src.models.edge import Edge


def build_test_graph():
    # 0 -> 1 -> 2 -> 3
    # 0 -> 4 -> 3 (shortcut in edges)
    # 3 -> 5 (dead end)
    g = Graph()
    for i in range(6):
        g.add_vertex(Vertex(id=i, x=i*50, y=100))

    g.add_edge(Edge(1, 0, 1, 10.0, 1.0, 1.0, directed=True))
    g.add_edge(Edge(2, 1, 2, 10.0, 1.0, 1.0, directed=True))
    g.add_edge(Edge(3, 2, 3, 10.0, 1.0, 1.0, directed=True))
    g.add_edge(Edge(4, 0, 4, 100.0, 10.0, 10.0, directed=True))
    g.add_edge(Edge(5, 4, 3, 100.0, 10.0, 10.0, directed=True))
    g.add_edge(Edge(6, 3, 5, 10.0, 1.0, 1.0, directed=True))  # dead end
    return g


def test_bfs_minimum_edge_path():
    g = build_test_graph()
    bfs = BFS(g)
    res = bfs.run(0, 3)

    assert res["reachable"] is True
    # Path via 4 has 2 edges [0, 4, 3], path via 1,2 has 3 edges [0, 1, 2, 3]
    # BFS guarantees MINIMUM EDGE COUNT (2 edges), ignoring weights
    assert res["path"] == [0, 4, 3]
    assert res["hop_count"] == 2


def test_dfs_cycle_detection():
    g = Graph()
    g.add_vertex(Vertex(0, 0, 0))
    g.add_vertex(Vertex(1, 10, 0))
    g.add_vertex(Vertex(2, 10, 10))
    g.add_edge(Edge(1, 0, 1, 10, 1, 1, directed=True))
    g.add_edge(Edge(2, 1, 2, 10, 1, 1, directed=True))
    g.add_edge(Edge(3, 2, 0, 10, 1, 1, directed=True))

    dfs = DFS(g)
    cycles = dfs.detect_cycles()
    assert len(cycles) >= 1


def test_dfs_dead_end_analysis():
    g = build_test_graph()
    dfs = DFS(g)
    # Finish line is vertex 3. Node 5 has no path to 3 -> dead end!
    dead_ends = dfs.find_dead_ends(finish_vid=3)
    assert 5 in dead_ends
