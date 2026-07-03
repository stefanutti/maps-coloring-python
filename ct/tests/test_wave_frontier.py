# tests/test_wave_frontier.py
"""
Tests for update_wave_frontier — the pure helper that computes the new
wave-frontier set after one reduction step.
"""
import os
import sys
import importlib.util
import pytest


@pytest.fixture(scope="module")
def mod():
    parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if os.path.exists(os.path.join(parent_dir, '4ct.py')):
        ct_path = parent_dir
    else:
        ct_path = os.path.join(parent_dir, 'ct')
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


def _merged_face_example():
    # A merged face with surviving vertices {10, 11, 12, 13}
    # Note: this face does NOT contain v1=1 or v2=2 — they have been collapsed.
    return [(10, 11), (11, 12), (12, 13), (13, 10)]


def test_non_f5_inactive_returns_none(mod):
    """F2/F3/F4 reduction from inactive frontier returns None (wave stays inactive)."""
    result = mod.update_wave_frontier(
        current=None, f1_len=3, f1_plus_f2=_merged_face_example(), v1=1, v2=2
    )
    assert result is None


def test_f5_inactive_activates_frontier(mod):
    """F5 reduction from inactive state activates the frontier with merged-face vertices."""
    result = mod.update_wave_frontier(
        current=None, f1_len=5, f1_plus_f2=_merged_face_example(), v1=1, v2=2
    )
    assert result == {10, 11, 12, 13}


def test_f5_active_extends_frontier(mod):
    """F5 reduction from active state extends the set with new merged-face vertices."""
    seed = {100, 101}
    result = mod.update_wave_frontier(
        current=seed, f1_len=5, f1_plus_f2=_merged_face_example(), v1=1, v2=2
    )
    assert result == {100, 101, 10, 11, 12, 13}


def test_non_f5_active_extends_and_cleans(mod):
    """F2/F3/F4 reduction from active state still extends and cleans (wave already on)."""
    seed = {100, 101}
    result = mod.update_wave_frontier(
        current=seed, f1_len=4, f1_plus_f2=_merged_face_example(), v1=1, v2=2
    )
    assert result == {100, 101, 10, 11, 12, 13}


def test_removed_vertices_stripped_from_input(mod):
    """Ghost-vertex case: v1,v2 already in current must not appear in output."""
    seed = {1, 2, 100}
    result = mod.update_wave_frontier(
        current=seed, f1_len=5, f1_plus_f2=_merged_face_example(), v1=1, v2=2
    )
    assert 1 not in result
    assert 2 not in result
    assert 100 in result


def test_does_not_mutate_input_set(mod):
    """Immutability: the input `current` set is not mutated in place."""
    seed = {100, 101}
    before = set(seed)
    mod.update_wave_frontier(
        current=seed, f1_len=5, f1_plus_f2=_merged_face_example(), v1=1, v2=2
    )
    assert seed == before
