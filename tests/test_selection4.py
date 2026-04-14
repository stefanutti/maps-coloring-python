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


# ---------------------------------------------------------------------------
# Tests: new strategy — F2/F3/F4 phase selects max-neighbor edge
# ---------------------------------------------------------------------------

def test_unavoidable_set_returns_5_values_and_new_prev_face_is_f1_plus_f2(mod):
    """5th return value must be the same object as 4th (new_prev_face == f1_plus_f2_temp)."""
    g = make_f3f4_graph()
    result = mod.select_edge_to_remove_unavoidable_set(g, 2345, 0)
    assert len(result) == 5
    edge, f1, f2, f1_plus_f2, new_prev_face = result
    assert new_prev_face is f1_plus_f2


def test_unavoidable_set_f3_picks_max_neighbor(mod):
    """With two F3 and two F4 faces, strategy must choose an edge whose f2 is F4 (size 4)."""
    g = make_f3f4_graph()
    _, _, f2, _, _ = mod.select_edge_to_remove_unavoidable_set(g, 2345, 0)
    assert len(f2) == 4  # maximum possible neighbor in this graph



# ---------------------------------------------------------------------------
# Tests: locality constraint — new_prev_face is identity-tracked across calls
# ---------------------------------------------------------------------------

def test_unavoidable_set_locality_uses_prev_face_identity(mod):
    """
    When prev_face is provided and exists in g_faces (by identity),
    new_prev_face returned is the same object as f1_plus_f2_temp.
    Simulate what reduce_faces does between calls.
    """
    g = make_f3f4_graph()

    # First call — no prev_face
    _, f1_a, f2_a, joined_a, new_prev_a = mod.select_edge_to_remove_unavoidable_set(g, 2345, 0)

    # Simulate reduce_faces: insert joined face into g_faces (same object, identity preserved)
    g.remove(f1_a)
    g.remove(f2_a)
    g.insert(-1, joined_a)

    # joined_a must now be in g_faces (identity check)
    assert any(f is new_prev_a for f in g)

    # Second call — pass new_prev_a as prev_face
    _, f1_b, f2_b, joined_b, new_prev_b = mod.select_edge_to_remove_unavoidable_set(g, 2345, 1, prev_face=new_prev_a)

    # new_prev_b must be the same object as joined_b
    assert new_prev_b is joined_b
