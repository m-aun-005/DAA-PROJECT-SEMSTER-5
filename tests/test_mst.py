"""tests/test_mst.py — Unit tests for Kruskal and Prim MST (Act 4).
"""

import pytest
from src.core.graph import Graph
from src.core.mst import KruskalMST, PrimMST, DisjointSetUnion
from src.models.vertex import Vertex
from src.models.edge import Edge


def test_dsu_union_find():
    dsu = DisjointSetUnion([0, 1, 2, 3])
    assert dsu.num_components == 4
    assert dsu.union(0, 1) is True
    assert dsu.union(2, 3) is True
    assert dsu.num_components == 2
    assert dsu.union(0, 1) is False  # Already connected
    assert dsu.union(1, 2) is True
    assert dsu.num_components == 1


def test_kruskal_and_prim_agree():
    g = Graph()
    for i in range(4):
        g.add_vertex(Vertex(i, i * 20, 0))

    # Triangle with center
    g.add_edge(Edge(1, 0, 1, 10.0, 1, 1, directed=False))
    g.add_edge(Edge(2, 1, 2, 20.0, 1, 1, directed=False))
    g.add_edge(Edge(3, 2, 3, 30.0, 1, 1, directed=False))
    g.add_edge(Edge(4, 3, 0, 40.0, 1, 1, directed=False))
    g.add_edge(Edge(5, 0, 2, 15.0, 1, 1, directed=False))

    kruskal = KruskalMST(g)
    prim = PrimMST(g)

    res_k = kruskal.run()
    res_p = prim.run(start_vid=0)

    assert res_k["is_connected_tree"] is True
    assert res_p["is_connected_tree"] is True
    assert res_k["edge_count"] == 3
    assert res_p["edge_count"] == 3
    # Kruskal and Prim must produce identical minimum total weights
    assert abs(res_k["total_weight"] - res_p["total_weight"]) < 1e-4
