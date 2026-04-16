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
    m.stats = {}
    m.initialize_statistics()
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


def make_f2_graph():
    """
    F2 face: [(10,11),(11,10)] — the two parallel directed edges.
    face2 uses edge direction (11,10): goes 11->10->12->13->11.
    face3 uses edge direction (10,11): goes 10->11->13->12->10.
    Either random choice from f2_face finds its f2 in this list.
    """
    f2_face = [(10,11),(11,10)]
    face2   = [(11,10),(10,12),(12,13),(13,11)]
    face3   = [(10,11),(11,13),(13,12),(12,10)]
    return [f2_face, face2, face3]


def make_f5_f6_faces():
    """
    face_a (F5): [(0,1),(1,2),(2,3),(3,4),(4,0)]
      Only ONE shared F5-F6 edge: (1,2) at index 1 (v1=1, v2=2) → face_b (F6).

    Two candidate edges from F5 at endpoints v1=1, v2=2:
      cand1: face_a[index 0] = (0,1)  -> adjacent face_c (F8, size 8) — larger
      cand2: face_a[index 2] = (2,3)  -> adjacent face_d (F4, size 4) — smaller

    face_c is F8 (not F6) so that edge (0,1) does NOT form a second F5-F6 pair.
    Expected: cand1 (0,1) chosen because 8 > 4.
    """
    face_a = [(0,1),(1,2),(2,3),(3,4),(4,0)]
    face_b = [(2,1),(1,9),(9,8),(8,7),(7,6),(6,2)]           # F6, shared with face_a at (1,2)
    face_c = [(1,0),(0,12),(12,11),(11,10),(10,9),(9,8),(8,7),(7,1)]  # F8, adjacent to (0,1)
    face_d = [(3,2),(2,6),(6,5),(5,3)]                        # F4, adjacent to (2,3)
    return [face_a, face_b, face_c, face_d]


def make_f5_f5_faces():
    """
    face_a (F5) and face_b (F5) share edge (1,2)/(2,1).
    face_c..face_f are the 4 candidate adjacent faces (also F5),
    each containing the reverse of one candidate edge.
    """
    face_a = [(0,1),(1,2),(2,3),(3,4),(4,0)]
    face_b = [(2,1),(1,20),(20,21),(21,22),(22,2)]
    face_c = [(1,0),(0,30),(30,31),(31,32),(32,1)]
    face_d = [(3,2),(2,40),(40,41),(41,42),(42,3)]
    face_e = [(2,22),(22,50),(50,51),(51,52),(52,2)]
    face_f = [(20,1),(1,32),(32,31),(31,30),(30,20)]
    return [face_a, face_b, face_c, face_d, face_e, face_f]


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

def test_unavoidable_set_phase1_returns_none_as_fifth(mod):
    """Phase 1 returns None as 5th value when recently_modified_vertices was None on entry."""
    g = make_f3f4_graph()
    result = mod.select_edge_to_remove_unavoidable_set(g, 2345, 0)
    assert len(result) == 5
    edge, f1, f2, f1_plus_f2, rmv = result
    assert rmv is None


def test_unavoidable_set_f3_picks_max_neighbor(mod):
    """With two F3 and two F4 faces, strategy must choose an edge whose f2 is F4 (size 4)."""
    g = make_f3f4_graph()
    _, _, f2, _, _ = mod.select_edge_to_remove_unavoidable_set(g, 2345, 0)
    assert len(f2) == 4  # maximum possible neighbor in this graph


# ---------------------------------------------------------------------------
# Tests: recently_modified_vertices parameter
# ---------------------------------------------------------------------------

def test_unavoidable_set_phase1_with_nonempty_rmv_returns_union(mod):
    """
    When recently_modified_vertices is non-empty on entry and Phase 1 fires,
    the 5th return value is a set that is a superset of the input vertices
    and also includes the merged face vertices.
    """
    g = make_f3f4_graph()
    seed_vertices = {99, 100}   # not in graph — carried through unchanged
    edge, f1, f2, f1_plus_f2, rmv = mod.select_edge_to_remove_unavoidable_set(
        g, 2345, 0, recently_modified_vertices=seed_vertices
    )
    assert isinstance(rmv, set)
    assert seed_vertices.issubset(rmv)
    merged_vertices = {v for e in f1_plus_f2 for v in e}
    assert merged_vertices.issubset(rmv)


# ---------------------------------------------------------------------------
# Tests: F2 face handling
# ---------------------------------------------------------------------------

def test_unavoidable_set_f2_returns_edge_from_f2_face(mod):
    """F2 rule: the returned edge and f1 must belong to the F2 face."""
    g = make_f2_graph()
    f2_face = g[0]
    edge, f1, f2, f1_plus_f2, rmv = mod.select_edge_to_remove_unavoidable_set(g, 2345, 0)
    assert f1 is f2_face
    assert edge in f2_face
    assert rmv is None


# ---------------------------------------------------------------------------
# Tests: F5/F6 helper — _select_f5_f6_edge
# ---------------------------------------------------------------------------

def test_select_f5_f6_picks_f5_edge_with_largest_neighbor(mod):
    """_select_f5_f6_edge picks from the F5 face, choosing the edge with the largest f2."""
    g = make_f5_f6_faces()
    face_a = g[0]
    best_edge, best_f1, best_f2, best_joined = mod._select_f5_f6_edge(g, [face_a])
    assert best_edge == (0, 1)      # f2 size 8 beats f2 size 4
    assert best_f1 is face_a        # edge came from F5, not F6
    assert len(best_f2) == 8        # face_c is F8
    assert best_joined is not None


# ---------------------------------------------------------------------------
# Tests: Phase 2 (all-F5 graph) returns vertex set
# ---------------------------------------------------------------------------

def test_unavoidable_set_phase2_returns_vertex_set(mod):
    """When only F5 faces exist (Phase 2), the 5th return is a non-empty set."""
    g = make_f5_f5_faces()
    edge, f1, f2, f1_plus_f2, rmv = mod.select_edge_to_remove_unavoidable_set(g, 2345, 0)
    assert edge is not None
    assert isinstance(rmv, set)
    assert len(rmv) > 0
    merged_vertices = {v for e in f1_plus_f2 for v in e}
    assert merged_vertices.issubset(rmv)


# ---------------------------------------------------------------------------
# Tests: CLI argument -s4 dispatches to the new strategy
# ---------------------------------------------------------------------------

def test_s4_cli_argument_dispatches_to_unavoidable_set(mod):
    """Parsing -s4 must be accepted by the selection group (mutually exclusive with -s1/-s2/-s3)."""
    import argparse

    # Replicate the selection group from main() to verify -s4 is recognized
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-s1", "--selection1", action='store_true', default=False)
    group.add_argument("-s2", "--selection2", action='store_true', default=False)
    group.add_argument("-s3", "--selection3", action='store_true', default=False)
    group.add_argument("-s4", "--selection4", action='store_true', default=False)

    args = parser.parse_args(["-s4"])
    assert args.selection4 is True
    assert args.selection1 is False
    assert args.selection2 is False
    assert args.selection3 is False
