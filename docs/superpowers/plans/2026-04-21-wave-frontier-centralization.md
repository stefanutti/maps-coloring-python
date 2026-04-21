# Wave Frontier Centralization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move all writes of `recently_modified_vertices` from `select_edge_to_remove_unavoidable_set` (S4) into `reduce_faces`, and clean removed vertices `(v1, v2)` from the frontier at each reduction step.

**Architecture:** Introduce a pure helper `update_wave_frontier(current, f1_len, f1_plus_f2, v1, v2)` in `ct/4ct.py` next to `_vertices_of`. `reduce_faces` calls it once per loop iteration, right after `selection_strategy(...)`. S4 becomes read-only with respect to the frontier and returns `None` as its 5th tuple element (restoring the documented invariant "`extra` is currently always `None`").

**Tech Stack:** Python 3, pytest, NetworkX (unchanged).

**Spec:** `docs/superpowers/specs/2026-04-21-wave-frontier-centralization-design.md`

---

### Task 1: TDD — write failing tests for `update_wave_frontier`

**Files:**
- Create: `tests/test_wave_frontier.py`

- [ ] **Step 1.1: Write the failing tests**

```python
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
```

- [ ] **Step 1.2: Run tests to verify they fail**

Run: `pytest tests/test_wave_frontier.py -v`
Expected: all 6 tests FAIL with `AttributeError: module 'ct_4ct' has no attribute 'update_wave_frontier'`.

- [ ] **Step 1.3: Commit**

```bash
git add tests/test_wave_frontier.py
git commit -m "test: add failing tests for update_wave_frontier helper"
```

---

### Task 2: Implement `update_wave_frontier`

**Files:**
- Modify: `ct/4ct.py:1068-1069` (add new function right after `_vertices_of`)

- [ ] **Step 2.1: Add `update_wave_frontier` below `_vertices_of`**

Insert these lines in `ct/4ct.py` immediately after the existing `_vertices_of` function (after line 1069):

```python
def update_wave_frontier(current, f1_len, f1_plus_f2, v1, v2):
    """
    Return the new wave-frontier set after reducing one face.

    - F5 reduction: activate or extend the frontier with vertices of the
      merged face, minus the two vertices removed from the graph.
    - Non-F5 reduction with active frontier: extend and clean the same way.
    - Non-F5 reduction with inactive frontier: return None (stays inactive).

    Does not mutate `current`.
    """
    is_f5 = (f1_len == 5)
    was_active = current is not None
    if not (is_f5 or was_active):
        return None
    base = current if was_active else set()
    return (base | _vertices_of(f1_plus_f2)) - {v1, v2}
```

- [ ] **Step 2.2: Run tests to verify they pass**

Run: `pytest tests/test_wave_frontier.py -v`
Expected: all 6 tests PASS.

- [ ] **Step 2.3: Run full test suite to confirm no regressions**

Run: `pytest tests/ -v`
Expected: all previously-passing tests still PASS (the S4 tests from `test_selection4.py` still pass because S4 itself is unchanged).

- [ ] **Step 2.4: Commit**

```bash
git add ct/4ct.py
git commit -m "feat: add update_wave_frontier pure helper"
```

---

### Task 3: Integrate `update_wave_frontier` into `reduce_faces`

**Files:**
- Modify: `ct/4ct.py:1566` (selection_strategy call)
- Modify: `ct/4ct.py:1584-1585` (remove duplicate v1/v2 extraction in F2 branch)
- Modify: `ct/4ct.py:1641-1642` (remove duplicate v1/v2 extraction in F3/F4/F5 branch)

- [ ] **Step 3.1: Update `selection_strategy` call and add frontier update**

In `ct/4ct.py`, replace lines 1566-1571 with:

```python
        # Select an edge from the graph
        # This is one of the most important function to work on, to apply different strategies
        edge_to_remove, f1, f2, f1_plus_f2_temp, _ = selection_strategy(g_faces, choices, i_global_counter, recently_modified_vertices)

        # Since Euler's formula is right :-) an edge to remove must exist, and it means that I made a programming error if I get here without finding it
        if edge_to_remove == ():
            logger.error("Unexpected condition (a suitable edge has not been found). Mario you'd better go back to paper")
            exit(-1)

        # Wave frontier is owned by reduce_faces: selection strategies only read it
        v1, v2 = edge_to_remove
        recently_modified_vertices = update_wave_frontier(recently_modified_vertices, len(f1), f1_plus_f2_temp, v1, v2)
```

Notes:
- The 5th element returned by `selection_strategy` is now discarded (`_`). S4 still computes it at this stage — that calculation becomes dead code, removed in Task 5.
- `v1, v2` are extracted once here, at the top of the loop body.

- [ ] **Step 3.2: Remove duplicate v1/v2 extraction in F2 branch**

In the F2 branch (currently lines 1582-1585), find and remove the two lines:

```python
            # Get the two vertices to join
            # It may also happen that at the end of the process, I'll get a loop: From ---CO to ---O
            v1 = edge_to_remove[0]
            v2 = edge_to_remove[1]
```

Keep only the comment lines immediately above the vertex-search logic. The F2 branch continues with `vertex_to_join_near_v1 = next(edge for edge in f2 if edge[0] == v1)[1]` etc., which references the `v1, v2` already bound at the top of the loop.

- [ ] **Step 3.3: Remove duplicate v1/v2 extraction in F3/F4/F5 branch**

In the F3/F4/F5 branch (currently lines 1639-1642), find and remove the two lines:

```python
            # Get the vertices at the ends of the edge to remove
            # And find the other four neighbors :>.---.<: (If the --- is the removed edge, the four external dots represent the vertices I'm looking for)
            v1 = edge_to_remove[0]
            v2 = edge_to_remove[1]
```

Keep the comment lines. The rest of the branch uses `v1, v2` which are already bound at the top of the loop.

- [ ] **Step 3.4: Run full test suite**

Run: `pytest tests/ -v`
Expected: all tests PASS. S4 tests still pass because S4 is unchanged; the new wave-frontier tests pass; the selection strategies keep working because `reduce_faces` simply ignores whatever S4 returns as 5th element.

- [ ] **Step 3.5: Smoke-run the algorithm**

Run: `cd ct && python3 4ct.py -s4 -r1 20`
Expected: the run completes with a valid coloring (no `exit(-1)` from `is_well_colored`). Small graph keeps this step fast.

- [ ] **Step 3.6: Commit**

```bash
git add ct/4ct.py
git commit -m "refactor: move wave-frontier writes into reduce_faces

reduce_faces now owns all writes of recently_modified_vertices via
update_wave_frontier, which also strips (v1, v2) from the set once
those vertices are removed from the graph. Selection strategies
still read the frontier; S4 still writes it, but its writes are now
discarded (dead code to be removed in a follow-up)."
```

---

### Task 4: TDD — update existing S4 tests to expect `None` as 5th element

**Files:**
- Modify: `tests/test_selection4.py:142-156` (`test_unavoidable_set_phase1_with_nonempty_rmv_returns_union`)
- Modify: `tests/test_selection4.py:192-200` (`test_unavoidable_set_phase2_returns_vertex_set`)

- [ ] **Step 4.1: Rewrite `test_unavoidable_set_phase1_with_nonempty_rmv_returns_union`**

Replace the test body with a version that asserts the 5th element is `None` regardless of the input frontier:

```python
def test_unavoidable_set_phase1_with_nonempty_rmv_returns_none(mod):
    """
    After the refactor, S4 never writes the wave frontier — the 5th return
    value is always None, even when a non-empty frontier is passed in.
    """
    g = make_f3f4_graph()
    seed_vertices = {99, 100}
    edge, f1, f2, f1_plus_f2, rmv = mod.select_edge_to_remove_unavoidable_set(
        g, 2345, 0, recently_modified_vertices=seed_vertices
    )
    assert rmv is None
```

Replace the entire function (including its previous name) with the new one above.

- [ ] **Step 4.2: Rewrite `test_unavoidable_set_phase2_returns_vertex_set`**

Replace with:

```python
def test_unavoidable_set_phase2_returns_none(mod):
    """Phase 2 (all-F5 graph) also returns None as 5th element after the refactor."""
    g = make_f5_f5_faces()
    edge, f1, f2, f1_plus_f2, rmv = mod.select_edge_to_remove_unavoidable_set(g, 2345, 0)
    assert edge is not None
    assert rmv is None
```

- [ ] **Step 4.3: Run tests to verify the two new tests fail**

Run: `pytest tests/test_selection4.py::test_unavoidable_set_phase1_with_nonempty_rmv_returns_none tests/test_selection4.py::test_unavoidable_set_phase2_returns_none -v`
Expected: both tests FAIL. The first one fails with `assert {99, 100, ...} is None` (S4 still returns a set). The second fails similarly.

- [ ] **Step 4.4: Commit**

```bash
git add tests/test_selection4.py
git commit -m "test: update S4 tests to expect None as 5th tuple element"
```

---

### Task 5: Remove frontier writes from `select_edge_to_remove_unavoidable_set`

**Files:**
- Modify: `ct/4ct.py:1072-1208` (S4 function body and docstring)

- [ ] **Step 5.1: Update the docstring**

In `ct/4ct.py`, inside `select_edge_to_remove_unavoidable_set`, replace the current docstring (lines 1073-1098) with:

```python
    """
    Selection strategy 4: unavoidable set with wave-like locality.

    Phase 1 (F2/F3/F4): processes smallest faces first.
      F2: picks one random face and one random edge.
      F3/F4: picks the valid edge whose adjacent face f2 is largest.

    Phase 2 (F5 only):
      Local: restrict to F5 faces adjacent to recently_modified_vertices.
        Step 1 — F5-F5: _select_from_f5_pairs (4-edge scan, max-neighbor).
        Step 2 — F5-F6: _select_f5_f6_edge (2-edge scan on F5 side, max-neighbor).
      Global fallback (Step 4): scan all F5 globally, same priority order.

    This function is read-only with respect to `recently_modified_vertices`:
    it uses the parameter for locality filtering and for incrementing the
    SELECT-S4-F4-INTERRUPT stat, but never writes it. The caller
    (`reduce_faces`) is the sole writer via `update_wave_frontier`.

    Parameters
    ----------
        g_faces: list of faces (each face is a list of directed-edge tuples)
        choices: integer (must be 2345; warned otherwise)
        i_global_counter: for logging
        recently_modified_vertices: set of vertex IDs representing the wave frontier, or None

    Returns
    -------
        edge_to_remove, f1, f2, f1_plus_f2_temp, None
    """
```

- [ ] **Step 5.2: Remove `new_rmv` calculation and update return in F2 phase**

Find the block at lines 1123-1131:

```python
            # TODO: verify this happen. It should not, because when a wave is active, only F4 can appear after having removed an F5 edge
            if recently_modified_vertices is not None:
                stats['SELECT-S4-F4-INTERRUPT'] += 1
                new_rmv = recently_modified_vertices | {v for e in candidate_joined for v in e}
                logger.info("aaaaaaaaaaaaaaaaaaa")
            else:
                new_rmv = None
            logger.info("END %s: found in F2 phase (random). Edge: %s", i_global_counter, edge)
            return edge, candidate_f1, candidate_f2, candidate_joined, new_rmv
```

Replace with:

```python
            # TODO: verify this happen. It should not, because when a wave is active, only F4 can appear after having removed an F5 edge
            if recently_modified_vertices is not None:
                stats['SELECT-S4-F4-INTERRUPT'] += 1
                logger.info("aaaaaaaaaaaaaaaaaaa")
            logger.info("END %s: found in F2 phase (random). Edge: %s", i_global_counter, edge)
            return edge, candidate_f1, candidate_f2, candidate_joined, None
```

- [ ] **Step 5.3: Remove `new_rmv` calculation and update return in F3/F4 phase**

Find the block at lines 1157-1164:

```python
        if best_edge is not None:
            if recently_modified_vertices is not None:
                stats['SELECT-S4-F4-INTERRUPT'] += 1
                new_rmv = recently_modified_vertices | {v for e in best_f1_plus_f2 for v in e}
            else:
                new_rmv = None
            logger.info("END %s: found in F%s phase. Edge: %s (f2 size: %s)", i_global_counter, target_size, best_edge, best_f2_len)
            return best_edge, best_f1, best_f2, best_f1_plus_f2, new_rmv
```

Replace with:

```python
        if best_edge is not None:
            if recently_modified_vertices is not None:
                stats['SELECT-S4-F4-INTERRUPT'] += 1
            logger.info("END %s: found in F%s phase. Edge: %s (f2 size: %s)", i_global_counter, target_size, best_edge, best_f2_len)
            return best_edge, best_f1, best_f2, best_f1_plus_f2, None
```

- [ ] **Step 5.4: Remove `new_rmv` calculation in local F5-F5 step**

Find the block at lines 1174-1180:

```python
    if local_f5:
        best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_from_f5_pairs(g_faces, local_f5, pair_neighbor_size=5)
        if best_edge is not None:
            stats['SELECT-S4-F5-F5'] += 1
            new_rmv = (recently_modified_vertices or set()) | _vertices_of(best_f1_plus_f2)
            logger.info("END %s: found via local F5-F5 pair. Edge: %s", i_global_counter, best_edge)
            return best_edge, best_f1, best_f2, best_f1_plus_f2, new_rmv
```

Replace with:

```python
    if local_f5:
        best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_from_f5_pairs(g_faces, local_f5, pair_neighbor_size=5)
        if best_edge is not None:
            stats['SELECT-S4-F5-F5'] += 1
            logger.info("END %s: found via local F5-F5 pair. Edge: %s", i_global_counter, best_edge)
            return best_edge, best_f1, best_f2, best_f1_plus_f2, None
```

- [ ] **Step 5.5: Remove `new_rmv` calculation in local F5-F6 step**

Find the block at lines 1183-1189:

```python
    if local_f5:
        best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_f5_f6_edge(g_faces, local_f5)
        if best_edge is not None:
            stats['SELECT-S4-F5-F6'] += 1
            new_rmv = (recently_modified_vertices or set()) | _vertices_of(best_f1_plus_f2)
            logger.info("END %s: found via local F5-F6 pair. Edge: %s", i_global_counter, best_edge)
            return best_edge, best_f1, best_f2, best_f1_plus_f2, new_rmv
```

Replace with:

```python
    if local_f5:
        best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_f5_f6_edge(g_faces, local_f5)
        if best_edge is not None:
            stats['SELECT-S4-F5-F6'] += 1
            logger.info("END %s: found via local F5-F6 pair. Edge: %s", i_global_counter, best_edge)
            return best_edge, best_f1, best_f2, best_f1_plus_f2, None
```

- [ ] **Step 5.6: Update returns in global fallback steps**

Find lines 1194-1198:

```python
    best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_from_f5_pairs(g_faces, all_f5, pair_neighbor_size=5)
    if best_edge is not None:
        stats['SELECT-S4-F5-FALLBACK'] += 1
        logger.info("END %s: found via global F5-F5 fallback. Edge: %s", i_global_counter, best_edge)
        return best_edge, best_f1, best_f2, best_f1_plus_f2, _vertices_of(best_f1_plus_f2)
```

Replace the last line (`return ..., _vertices_of(best_f1_plus_f2)`) with:

```python
        return best_edge, best_f1, best_f2, best_f1_plus_f2, None
```

Then find lines 1200-1204:

```python
    best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_f5_f6_edge(g_faces, all_f5)
    if best_edge is not None:
        stats['SELECT-S4-F5-FALLBACK'] += 1
        logger.info("END %s: found via global F5-F6 fallback. Edge: %s", i_global_counter, best_edge)
        return best_edge, best_f1, best_f2, best_f1_plus_f2, _vertices_of(best_f1_plus_f2)
```

Replace the last line with:

```python
        return best_edge, best_f1, best_f2, best_f1_plus_f2, None
```

- [ ] **Step 5.7: Run full test suite**

Run: `pytest tests/ -v`
Expected: all tests PASS — including the two rewritten S4 tests (`test_unavoidable_set_phase1_with_nonempty_rmv_returns_none`, `test_unavoidable_set_phase2_returns_none`) and the `update_wave_frontier` tests and all pre-existing tests.

- [ ] **Step 5.8: Commit**

```bash
git add ct/4ct.py
git commit -m "refactor: remove wave-frontier writes from S4 strategy

select_edge_to_remove_unavoidable_set is now read-only w.r.t.
recently_modified_vertices. All 6 return statements yield None as
the 5th tuple element, restoring the documented invariant that
'extra' is currently always None. Docstring updated."
```

---

### Task 6: End-to-end behavioral verification

**Files:** none modified.

- [ ] **Step 6.1: Run a medium-sized algorithm run with S4**

Run: `cd ct && python3 4ct.py -s4 -r1 50`
Expected: the run completes with a valid coloring. No `exit(-1)`. Final log line confirms completion.

- [ ] **Step 6.2: Run a medium-sized algorithm run with S1 (regression check)**

Run: `cd ct && python3 4ct.py -s1 -r1 50`
Expected: the run completes with a valid coloring. S1/S2/S3 were untouched; this confirms the tuple-unpacking change in `reduce_faces` did not break them.

- [ ] **Step 6.3: Run the full test suite one final time**

Run: `pytest tests/ -v`
Expected: all tests PASS.

- [ ] **Step 6.4: No commit**

This task is verification-only. Proceed to completion.

---

## Summary of files touched

| File | Change |
|---|---|
| `tests/test_wave_frontier.py` | **Created.** 6 unit tests for `update_wave_frontier`. |
| `ct/4ct.py` | **Modified.** New `update_wave_frontier` helper; `reduce_faces` calls it; S4 returns `None` as 5th element. |
| `tests/test_selection4.py` | **Modified.** Two tests rewritten to expect `None` as 5th element. |
