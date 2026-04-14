# tests/test_selection4.py
"""
Tests for selection strategy 4 (unavoidable set with locality)
and for the 5-value return contract on all existing strategies.
"""
import os
import sys
import importlib.util
import pytest

# ---------------------------------------------------------------------------
# Module loader (4ct.py starts with a digit so cannot be imported normally)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def mod():
    ct_path = os.path.join(os.path.dirname(__file__), '..', 'ct')
    sys.path.insert(0, ct_path)
    spec = importlib.util.spec_from_file_location(
        "ct_4ct",
        os.path.join(ct_path, '4ct.py')
    )
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

# ---------------------------------------------------------------------------
# Shared fixture: K4 with one edge subdivided (vertices 0-4)
#   faceA (F3): [(0,1),(1,2),(2,0)]
#   faceB (F4): [(0,2),(2,4),(4,3),(3,0)]
#   faceC (F3): [(0,3),(3,1),(1,0)]
#   faceD (F4): [(1,3),(3,4),(4,2),(2,1)]
# ---------------------------------------------------------------------------

def make_f3f4_graph():
    return [
        [(0,1),(1,2),(2,0)],
        [(0,2),(2,4),(4,3),(3,0)],
        [(0,3),(3,1),(1,0)],
        [(1,3),(3,4),(4,2),(2,1)],
    ]


# ---------------------------------------------------------------------------
# Tests: existing strategies return 5 values, 5th is None
# ---------------------------------------------------------------------------

def test_first_fit_returns_5_values(mod):
    g = make_f3f4_graph()
    result = mod.select_edge_to_remove_first_fit(g, 2345, 0)
    assert len(result) == 5
    assert result[4] is None


def test_largest_neighbor_returns_5_values(mod):
    g = make_f3f4_graph()
    result = mod.select_edge_to_remove_by_largest_neighbor(g, 2345, 0)
    assert len(result) == 5
    assert result[4] is None


def test_f5_shared_vertex_returns_5_values(mod):
    g = make_f3f4_graph()
    result = mod.select_edge_to_remove_f5_shared_vertex(g, 2345, 0)
    assert len(result) == 5
    assert result[4] is None
