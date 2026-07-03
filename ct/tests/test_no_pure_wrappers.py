# tests/test_no_pure_wrappers.py
"""
Test di non-regressione: verifica che le funzioni wrapper pure
NON esistano più in ct_graph_utils e che le API nx dirette
producano i risultati attesi.
"""
import sys
import os

# Configure path to find ct_graph_utils regardless of execution directory
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if os.path.exists(os.path.join(parent_dir, 'ct_graph_utils.py')):
    sys.path.insert(0, parent_dir)
else:
    sys.path.insert(0, os.path.join(parent_dir, 'ct'))

import pytest
import networkx as nx
import ct_graph_utils


def test_is_graph_planar_wrapper_removed():
    """is_graph_planar non deve esistere in ct_graph_utils."""
    assert not hasattr(ct_graph_utils, 'is_graph_planar'), \
        "is_graph_planar è ancora presente — rimuoverla"


def test_graph_degree_wrapper_removed():
    """graph_degree non deve esistere in ct_graph_utils."""
    assert not hasattr(ct_graph_utils, 'graph_degree'), \
        "graph_degree è ancora presente — rimuoverla"


def test_graph_order_wrapper_removed():
    """graph_order non deve esistere in ct_graph_utils."""
    assert not hasattr(ct_graph_utils, 'graph_order'), \
        "graph_order è ancora presente — rimuoverla"


def test_graph_size_wrapper_removed():
    """graph_size non deve esistere in ct_graph_utils."""
    assert not hasattr(ct_graph_utils, 'graph_size'), \
        "graph_size è ancora presente — rimuoverla"


def test_create_networkx_graph_wrapper_removed():
    """create_networkx_graph non deve esistere in ct_graph_utils."""
    assert not hasattr(ct_graph_utils, 'create_networkx_graph'), \
        "create_networkx_graph è ancora presente — rimuoverla"


# --- Test che le API nx dirette funzionano correttamente ---

def test_nx_is_planar_works():
    g = nx.MultiGraph()
    g.add_edges_from([(0, 1), (1, 2), (2, 0)])
    assert nx.is_planar(g) is True


def test_nx_degree_works():
    g = nx.MultiGraph()
    g.add_edges_from([(0, 1), (0, 2), (0, 3)])
    assert g.degree(0) == 3


def test_nx_number_of_nodes_works():
    g = nx.MultiGraph()
    g.add_nodes_from([0, 1, 2])
    assert g.number_of_nodes() == 3


def test_nx_number_of_edges_works():
    g = nx.MultiGraph()
    g.add_edges_from([(0, 1), (1, 2)])
    assert g.number_of_edges() == 2


def test_nx_multigraph_creation():
    g = nx.MultiGraph()
    assert isinstance(g, nx.MultiGraph)
