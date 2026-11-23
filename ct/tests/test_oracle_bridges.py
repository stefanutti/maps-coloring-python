"""Bridge detection on keyed multigraphs, checked by actual edge deletion."""
from copy import deepcopy
from itertools import combinations, product
from pathlib import Path
import sys

import networkx as nx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from experiments import oracle_reduction as oracle


@pytest.mark.parametrize("edges,expected", [
    ([], False),
    ([(0, 1)], True),
    ([(0, 1), (0, 1)], False),
    ([(0, 1), (0, 1), (0, 1)], False),
    ([(0, 1), (1, 2), (2, 0)], False),
    ([(0, 0)], False),
    ([(0, 0), (0, 1)], True),
    ([(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5), (5, 3)], True),
    ([(0, 1), (0, 1), (2, 3)], True),
    ([(0, 1), (0, 1), (1, 2), (2, 0)], False),
])
def test_bridge_verdict_and_read_only_graph(edges, expected):
    graph = nx.MultiGraph(study={"preserved": [1, 2]})
    graph.add_node(9, label="isolated")
    # Automatically allocated keys repeat across different endpoint pairs.
    for u, v in edges:
        graph.add_edge(u, v, color="red", metadata={"preserved": [u, v]})
    before = deepcopy(nx.node_link_data(graph))

    assert oracle._has_bridge(graph) is expected
    assert nx.node_link_data(graph) == before


def test_all_four_vertex_multigraphs_against_edge_deletion():
    # Each of the six pairs has 0, 1, or 2 edges: 729 distinct multigraphs.
    pairs = list(combinations(range(4), 2))
    for multiplicities in product(range(3), repeat=len(pairs)):
        graph = nx.MultiGraph()
        graph.add_nodes_from(range(4))
        for (u, v), count in zip(pairs, multiplicities):
            for key in range(count):
                graph.add_edge(u, v, key=key)
        components = nx.number_connected_components(graph)
        expected = False
        for u, v, key in list(graph.edges(keys=True)):
            without_edge = graph.copy()
            without_edge.remove_edge(u, v, key)
            expected |= nx.number_connected_components(without_edge) > components

        assert oracle._has_bridge(graph) is expected, multiplicities


def test_long_cycle_and_path_do_not_require_recursion():
    graph = nx.cycle_graph(3000, create_using=nx.MultiGraph)
    assert oracle._has_bridge(graph) is False
    graph.remove_edge(0, 2999)
    assert oracle._has_bridge(graph) is True


def test_empty_graph_has_no_bridge():
    assert oracle._has_bridge(nx.MultiGraph()) is False
