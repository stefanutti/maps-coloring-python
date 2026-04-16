# Selection Strategy 4 Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite `select_edge_to_remove_unavoidable_set` to use a vertex-set wave frontier, random F2 selection, a corrected F5-F6 rule (edges from F5 face only), and proper F4-interrupt locality.

**Architecture:** Approach A — minimal delta on `ct/4ct.py`. Replace `prev_face` (single face identity) with `recently_modified_vertices` (set of vertex IDs). Add `_select_f5_f6_edge` helper. Phase 1 F2 becomes random. Phase 1 returns the vertex union when a Phase-2 wave was active. Phase 2 F5-F6 picks only from the F5 face side.

**Tech Stack:** Python 3, NetworkX, pytest

---

## File Map

| File | Change |
|------|--------|
| `ct/4ct.py` | Rename `prev_face` → `recently_modified_vertices` (2 call-site lines), fix F2 rule, update Phase 1 return value, add `_select_f5_f6_edge` helper, rewrite Phase 2 block, add stats counter |
| `tests/test_selection4.py` | Update `mod` fixture to init stats, update 2 tests for new contract, add 4 new tests |

---

## Task 1: Write all failing tests

**Files:**
- Modify: `tests/test_selection4.py`

- [ ] **Step 1: Update the `mod` fixture to initialize stats**

`stats` is only set inside `if __name__ == '__main__':` in `4ct.py`, so it doesn't exist when the module is imported by tests. Any test that reaches Phase 2 or uses the F4-interrupt path will crash without it. Replace the existing `mod` fixture:

```python
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
```

- [ ] **Step 2: Update `test_unavoidable_set_returns_5_values_and_new_prev_face_is_f1_plus_f2`**

Rename and update the assertion — Phase 1 now returns `None` as the 5th value (wave not started), not `f1_plus_f2`. Replace the existing test:

```python
def test_unavoidable_set_phase1_returns_none_as_fifth(mod):
    """Phase 1 returns None as 5th value when recently_modified_vertices was None on entry."""
    g = make_f3f4_graph()
    result = mod.select_edge_to_remove_unavoidable_set(g, 2345, 0)
    assert len(result) == 5
    edge, f1, f2, f1_plus_f2, rmv = result
    assert rmv is None
```

- [ ] **Step 3: Update `test_unavoidable_set_locality_uses_prev_face_identity`**

Replace with a test for the new vertex-set behaviour. Phase 1 fires with a non-empty `recently_modified_vertices`, and the result must be the union with the merged face's vertices:

```python
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
```

- [ ] **Step 4: Add test for F2 random selection**

Add helper `make_f2_graph()` and the test. The face list has one F2 face (multi-edge 10↔11) and two surrounding faces — one for each direction of the multi-edge:

```python
def make_f2_graph():
    """
    F2 face: [(10,11),(11,10)] — the two parallel directed edges.
    face2 uses edge direction (11,10): goes 11→10→12→13→11.
    face3 uses edge direction (10,11): goes 10→11→13→12→10.
    Either random choice from f2_face finds its f2 in this list.
    """
    f2_face = [(10,11),(11,10)]
    face2   = [(11,10),(10,12),(12,13),(13,11)]
    face3   = [(10,11),(11,13),(13,12),(12,10)]
    return [f2_face, face2, face3]


def test_unavoidable_set_f2_returns_edge_from_f2_face(mod):
    """F2 rule: the returned edge and f1 must belong to the F2 face."""
    g = make_f2_graph()
    f2_face = g[0]
    edge, f1, f2, f1_plus_f2, rmv = mod.select_edge_to_remove_unavoidable_set(g, 2345, 0)
    assert f1 is f2_face
    assert edge in f2_face
    assert rmv is None
```

- [ ] **Step 5: Add test for `_select_f5_f6_edge` helper**

Add helper `make_f5_f6_faces()` and the test. Two candidate edges from the F5 face: `(0,1)` adjacent to an F6 (size 6) and `(2,3)` adjacent to an F4 (size 4). The function must pick `(0,1)`.

```python
def make_f5_f6_faces():
    """
    face_a (F5): [(0,1),(1,2),(2,3),(3,4),(4,0)]
      shared edge with face_b: (1,2) at index 1 (v1=1, v2=2)
    face_b (F6): [(2,1),(1,9),(9,8),(8,7),(7,6),(6,2)]

    Two candidate edges from F5 at endpoints v1=1, v2=2:
      cand1: face_a[index 0] = (0,1)  → adjacent face_c (F6, size 6) — larger
      cand2: face_a[index 2] = (2,3)  → adjacent face_d (F4, size 4) — smaller
    Expected: cand1 chosen.
    """
    face_a = [(0,1),(1,2),(2,3),(3,4),(4,0)]
    face_b = [(2,1),(1,9),(9,8),(8,7),(7,6),(6,2)]
    face_c = [(1,0),(0,12),(12,11),(11,10),(10,9),(9,1)]  # F6, contains rotate((0,1))=(1,0)
    face_d = [(3,2),(2,6),(6,5),(5,3)]                    # F4, contains rotate((2,3))=(3,2)
    return [face_a, face_b, face_c, face_d]


def test_select_f5_f6_picks_f5_edge_with_largest_neighbor(mod):
    """_select_f5_f6_edge picks from the F5 face, choosing the edge with the largest f2."""
    g = make_f5_f6_faces()
    face_a = g[0]
    best_edge, best_f1, best_f2, best_joined = mod._select_f5_f6_edge(g, [face_a])
    assert best_edge == (0, 1)      # f2 size 6 beats f2 size 4
    assert best_f1 is face_a        # edge came from F5, not F6
    assert len(best_f2) == 6
    assert best_joined is not None
```

- [ ] **Step 6: Add test for Phase 2 returning a vertex set**

Add helper `make_f5_f5_faces()` and the test. All faces are F5, so the function reaches Phase 2 directly.

```python
def make_f5_f5_faces():
    """
    face_a (F5) and face_b (F5) share edge (1,2)/(2,1).
    face_c..face_f are the 4 candidate adjacent faces (also F5),
    each containing the reverse of one candidate edge.

    face_a = [(0,1),(1,2),(2,3),(3,4),(4,0)]
    face_b = [(2,1),(1,20),(20,21),(21,22),(22,2)]
    face_c — contains rotate((0,1))=(1,0)
    face_d — contains rotate((2,3))=(3,2)
    face_e — contains rotate((22,2))=(2,22)
    face_f — contains rotate((1,20))=(20,1)
    """
    face_a = [(0,1),(1,2),(2,3),(3,4),(4,0)]
    face_b = [(2,1),(1,20),(20,21),(21,22),(22,2)]
    face_c = [(1,0),(0,30),(30,31),(31,32),(32,1)]
    face_d = [(3,2),(2,40),(40,41),(41,42),(42,3)]
    face_e = [(2,22),(22,50),(50,51),(51,52),(52,2)]
    face_f = [(20,1),(1,32),(32,31),(31,30),(30,20)]
    return [face_a, face_b, face_c, face_d, face_e, face_f]


def test_unavoidable_set_phase2_returns_vertex_set(mod):
    """When only F5 faces exist (Phase 2), the 5th return is a non-empty set."""
    g = make_f5_f5_faces()
    edge, f1, f2, f1_plus_f2, rmv = mod.select_edge_to_remove_unavoidable_set(g, 2345, 0)
    assert edge is not None
    assert isinstance(rmv, set)
    assert len(rmv) > 0
    merged_vertices = {v for e in f1_plus_f2 for v in e}
    assert merged_vertices.issubset(rmv)
```

- [ ] **Step 7: Run tests to confirm failures**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python
python -m pytest tests/test_selection4.py -v 2>&1 | tail -40
```

Expected: multiple FAILED — `test_unavoidable_set_phase1_returns_none_as_fifth` (5th is currently `f1_plus_f2`), `test_unavoidable_set_phase1_with_nonempty_rmv_returns_union` (wrong param name `prev_face`), `test_select_f5_f6_picks_f5_edge_with_largest_neighbor` (`_select_f5_f6_edge` not found), `test_unavoidable_set_phase2_returns_vertex_set` (5th is `f1_plus_f2` not a set).

---

## Task 2: Add randint import and stats counter

**Files:**
- Modify: `ct/4ct.py` line 116 and line ~222

- [ ] **Step 1: Add `randint` to the random import at line 116**

```python
# Before:
from random import shuffle

# After:
from random import shuffle, randint
```

- [ ] **Step 2: Add `SELECT-S4-F4-INTERRUPT` stat at line ~222**

After the three existing S4 stat lines:

```python
    stats['SELECT-S4-F5-F5'] = 0
    stats['SELECT-S4-F5-F6'] = 0
    stats['SELECT-S4-F5-FALLBACK'] = 0
    stats['SELECT-S4-F4-INTERRUPT'] = 0    # new line
```

- [ ] **Step 3: Confirm no new failures**

```bash
python -m pytest tests/test_selection4.py -v 2>&1 | tail -20
```

Expected: same set of failures as after Task 1 — no regressions introduced.

---

## Task 3: Fix Phase 1 — F2 random rule + signature + return value

**Files:**
- Modify: `ct/4ct.py` lines 1166–1244

- [ ] **Step 1: Replace function signature and docstring (lines 1166–1194)**

```python
def select_edge_to_remove_unavoidable_set(g_faces, choices, i_global_counter, recently_modified_vertices=None):
    """
    Selection strategy 4: unavoidable set with wave-like locality.

    Phase 1 (F2/F3/F4): processes smallest faces first.
      F2: picks one random face and one random edge.
      F3/F4: picks the valid edge whose adjacent face is largest.
      Return: None when wave not active; union of input + merged vertices when wave active.

    Phase 2 (F5 only):
      Local: restrict to F5 faces adjacent to recently_modified_vertices.
        Step 1 — F5-F5: _select_from_f5_pairs (4-edge scan, max-neighbor).
        Step 2 — F5-F6: _select_f5_f6_edge (2-edge scan on F5 side, max-neighbor).
      Global fallback (Step 4): scan all F5 globally, same priority order.
      Return: input | vertices(merged_face).

    Parameters
    ----------
        g_faces: list of faces (each face is a list of directed-edge tuples)
        choices: integer (must be 2345; warned otherwise)
        i_global_counter: for logging
        recently_modified_vertices: set of vertex IDs representing the wave frontier, or None

    Returns
    -------
        edge_to_remove, f1, f2, f1_plus_f2_temp, recently_modified_vertices
    """
```

- [ ] **Step 2: Replace the Phase 1 block (lines ~1201–1244)**

Replace everything from `# Phase F2 / F3 / F4` through the final `return` of the Phase 1 block with:

```python
    # -------------------------------------------------------------------------
    # Phase F2 / F3 / F4  — global, locality ignored
    # -------------------------------------------------------------------------
    for target_size in [2, 3, 4]:

        faces_of_this_size = [f for f in g_faces if len(f) == target_size]
        if not faces_of_this_size:
            continue

        # F2: pick a random face and a random edge (both parallel edges are always valid)
        if target_size == 2:
            candidate_f1 = faces_of_this_size[randint(0, len(faces_of_this_size) - 1)]
            i_edge = randint(0, 1)
            edge = candidate_f1[i_edge]
            rotated_edge = rotate(edge, 1)
            temp = [face for face in g_faces if rotated_edge in face]
            temp.remove(candidate_f1)
            candidate_f2 = temp[0]
            candidate_joined = join_faces(candidate_f1, candidate_f2, edge)
            if recently_modified_vertices is not None:
                stats['SELECT-S4-F4-INTERRUPT'] += 1
                new_rmv = recently_modified_vertices | {v for e in candidate_joined for v in e}
            else:
                new_rmv = None
            logger.info("END %s: found in F2 phase (random). Edge: %s", i_global_counter, edge)
            return edge, candidate_f1, candidate_f2, candidate_joined, new_rmv

        # F3/F4: pick the valid edge whose adjacent face is largest
        best_edge = None
        best_f1 = None
        best_f2 = None
        best_f1_plus_f2 = None
        best_f2_len = 0

        for candidate_f1 in faces_of_this_size:
            for i_edge in range(len(candidate_f1)):
                edge = candidate_f1[i_edge]
                rotated_edge = rotate(edge, 1)
                candidate_f2 = next((face for face in g_faces if rotated_edge in face), None)
                if candidate_f2 is None:
                    continue
                candidate_joined = join_faces(candidate_f1, candidate_f2, edge)
                if is_the_graph_one_edge_connected(candidate_joined):
                    continue
                if len(candidate_f2) > best_f2_len:
                    best_f2_len = len(candidate_f2)
                    best_edge = edge
                    best_f1 = candidate_f1
                    best_f2 = candidate_f2
                    best_f1_plus_f2 = candidate_joined

        if best_edge is not None:
            if recently_modified_vertices is not None:
                stats['SELECT-S4-F4-INTERRUPT'] += 1
                new_rmv = recently_modified_vertices | {v for e in best_f1_plus_f2 for v in e}
            else:
                new_rmv = None
            logger.info("END %s: found in F%s phase. Edge: %s (f2 size: %s)",
                        i_global_counter, target_size, best_edge, best_f2_len)
            return best_edge, best_f1, best_f2, best_f1_plus_f2, new_rmv
```

- [ ] **Step 3: Run tests**

```bash
python -m pytest tests/test_selection4.py -v 2>&1 | tail -30
```

Expected to now PASS:
- `test_unavoidable_set_phase1_returns_none_as_fifth`
- `test_unavoidable_set_phase1_with_nonempty_rmv_returns_union`
- `test_unavoidable_set_f3_picks_max_neighbor`
- `test_unavoidable_set_f2_returns_edge_from_f2_face`

Still FAILING: `test_select_f5_f6_picks_f5_edge_with_largest_neighbor`, `test_unavoidable_set_phase2_returns_vertex_set`.

---

## Task 4: Add `_select_f5_f6_edge` helper

**Files:**
- Modify: `ct/4ct.py` — insert after `_select_from_f5_pairs` (around line 1129)

- [ ] **Step 1: Insert `_select_f5_f6_edge` after `_select_from_f5_pairs`**

After the `return best_edge, best_f1, best_f2, best_f1_plus_f2` line that closes `_select_from_f5_pairs`, insert:

```python

def _select_f5_f6_edge(g_faces, f5_candidates):
    """
    For each F5 in f5_candidates adjacent to an F6, evaluate the 2 edges of the F5
    face at the shared edge's endpoints (excluding the shared edge itself).
    Returns the valid edge (removal not a bridge) with the largest adjacent face f2.
    Returns (best_edge, best_f1, best_f2, best_f1_plus_f2) or (None, None, None, None).
    """
    best_edge = None
    best_f1 = None
    best_f2 = None
    best_f1_plus_f2 = None
    best_f2_len = 0

    for face_a in f5_candidates:
        n_a = len(face_a)
        for i_shared in range(n_a):
            shared_edge = face_a[i_shared]
            rotated_shared = rotate(shared_edge, 1)
            face_b = next((f for f in g_faces if rotated_shared in f), None)
            if face_b is None or len(face_b) != 6:
                continue

            # Two candidate edges: edges of F5 at v1 and v2 of the shared edge
            candidate_edges = [
                face_a[(i_shared - 1) % n_a],   # edge ending at v1
                face_a[(i_shared + 1) % n_a],   # edge starting at v2
            ]

            for edge in candidate_edges:
                rotated_edge = rotate(edge, 1)
                candidate_f2 = next((f for f in g_faces if rotated_edge in f), None)
                if candidate_f2 is None:
                    continue
                candidate_joined = join_faces(face_a, candidate_f2, edge)
                if is_the_graph_one_edge_connected(candidate_joined):
                    continue
                if len(candidate_f2) > best_f2_len:
                    best_f2_len = len(candidate_f2)
                    best_edge = edge
                    best_f1 = face_a
                    best_f2 = candidate_f2
                    best_f1_plus_f2 = candidate_joined

    return best_edge, best_f1, best_f2, best_f1_plus_f2
```

- [ ] **Step 2: Run the F5-F6 test**

```bash
python -m pytest tests/test_selection4.py::test_select_f5_f6_picks_f5_edge_with_largest_neighbor -v
```

Expected: PASS

- [ ] **Step 3: Run all tests**

```bash
python -m pytest tests/test_selection4.py -v 2>&1 | tail -30
```

Expected: only `test_unavoidable_set_phase2_returns_vertex_set` still failing.

---

## Task 5: Rewrite Phase 2 block + rename call-site variable

**Files:**
- Modify: `ct/4ct.py` lines ~1246–1297 (Phase 2 block)
- Modify: `ct/4ct.py` lines ~1627 and ~1655 (main reduction loop)

- [ ] **Step 1: Replace the entire Phase 2 block**

Replace everything from `# Phase F5  — only reached when no F2/F3/F4 exist` through `exit(-1)` with:

```python
    # -------------------------------------------------------------------------
    # Phase F5  — only reached when no F2/F3/F4 exist
    # -------------------------------------------------------------------------

    def _vertices_of(face):
        return {v for edge in face for v in edge}

    # Locality: restrict to F5 faces touching the wave frontier
    if recently_modified_vertices:
        local_f5 = [f for f in g_faces if len(f) == 5 and
                    any(v in recently_modified_vertices for edge in f for v in edge)]
    else:
        local_f5 = []

    # Step 1 — local F5-F5 (highest priority)
    if local_f5:
        best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_from_f5_pairs(
            g_faces, local_f5, pair_neighbor_size=5
        )
        if best_edge is not None:
            stats['SELECT-S4-F5-F5'] += 1
            new_rmv = (recently_modified_vertices or set()) | _vertices_of(best_f1_plus_f2)
            logger.info("END %s: found via local F5-F5 pair. Edge: %s", i_global_counter, best_edge)
            return best_edge, best_f1, best_f2, best_f1_plus_f2, new_rmv

    # Step 2 — local F5-F6
    if local_f5:
        best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_f5_f6_edge(g_faces, local_f5)
        if best_edge is not None:
            stats['SELECT-S4-F5-F6'] += 1
            new_rmv = (recently_modified_vertices or set()) | _vertices_of(best_f1_plus_f2)
            logger.info("END %s: found via local F5-F6 pair. Edge: %s", i_global_counter, best_edge)
            return best_edge, best_f1, best_f2, best_f1_plus_f2, new_rmv

    # Step 4 — global fallback (no local candidates, or local search found nothing)
    all_f5 = [f for f in g_faces if len(f) == 5]

    best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_from_f5_pairs(
        g_faces, all_f5, pair_neighbor_size=5
    )
    if best_edge is not None:
        stats['SELECT-S4-F5-FALLBACK'] += 1
        logger.info("END %s: found via global F5-F5 fallback. Edge: %s", i_global_counter, best_edge)
        return best_edge, best_f1, best_f2, best_f1_plus_f2, _vertices_of(best_f1_plus_f2)

    best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_f5_f6_edge(g_faces, all_f5)
    if best_edge is not None:
        stats['SELECT-S4-F5-FALLBACK'] += 1
        logger.info("END %s: found via global F5-F6 fallback. Edge: %s", i_global_counter, best_edge)
        return best_edge, best_f1, best_f2, best_f1_plus_f2, _vertices_of(best_f1_plus_f2)

    # Should never reach here — Euler guarantees a face < F6 always exists
    logger.error("END %s: no valid edge found in select_edge_to_remove_unavoidable_set", i_global_counter)
    exit(-1)
```

- [ ] **Step 2: Rename `prev_face` in the main reduction loop (line ~1627)**

```python
# Before:
    prev_face = None

# After:
    recently_modified_vertices = None
```

- [ ] **Step 3: Rename `prev_face` in the strategy call (line ~1655)**

```python
# Before:
        edge_to_remove, f1, f2, f1_plus_f2_temp, prev_face = selection_strategy(g_faces, choices, i_global_counter, prev_face)

# After:
        edge_to_remove, f1, f2, f1_plus_f2_temp, recently_modified_vertices = selection_strategy(g_faces, choices, i_global_counter, recently_modified_vertices)
```

- [ ] **Step 4: Run all tests**

```bash
python -m pytest tests/test_selection4.py -v 2>&1 | tail -30
```

Expected: ALL PASS

- [ ] **Step 5: Run the full test suite**

```bash
python -m pytest tests/ -v 2>&1 | tail -30
```

Expected: ALL PASS

---

## Task 6: Commit

- [ ] **Step 1: Verify changed files**

```bash
git diff --stat
```

Expected output includes only `ct/4ct.py` and `tests/test_selection4.py`.

- [ ] **Step 2: Stage and commit**

```bash
git add ct/4ct.py tests/test_selection4.py
git commit -m "$(cat <<'EOF'
feat: rewrite selection4 with vertex-set wave frontier and corrected F5-F6 rule

- Replace prev_face (identity) with recently_modified_vertices (vertex set)
- F2 rule: random face + random edge
- Phase 1 return: union with wave when active (F4 interrupt), None otherwise
- Add _select_f5_f6_edge helper: 2 edges from F5 face only, max-neighbor
- Phase 2 local/global fallback uses vertex-set frontier
- Add SELECT-S4-F4-INTERRUPT stat counter

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```
