# Select Functions Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace verbose index-based while loops, boolean flags, and duplicated choices-parsing branches in S1/S2/S3 with `next()` generators and `for item in collection` iteration.

**Architecture:** Pure in-place refactor of three functions in `ct/4ct.py`. S1 gets choices-list parsing + flat `next()` for face and edge selection. S2/S3 each gain a local closure that encapsulates the per-size scan, making the top-level a single `next()` over sizes. S4 is unchanged.

**Tech Stack:** Python 3, NetworkX — no new dependencies.

---

## Files

- Modify: `ct/4ct.py` lines 708–831 (S1), 835–939 (S2), 943–1075 (S3)
- Test: `tests/test_selection4.py`, `tests/test_no_pure_wrappers.py`

---

### Task 0: Baseline — verify tests pass before touching anything

**Files:**
- Test: `tests/test_selection4.py`, `tests/test_no_pure_wrappers.py`

- [ ] **Step 1: Run the full test suite from `ct/`**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct
source ../.venv/bin/activate
pytest ../tests/ -v
```

Expected: all tests PASS. If any fail, stop — do not proceed until baseline is green.

---

### Task 1: Refactor S1 — `select_edge_to_remove_first_fit`

**Files:**
- Modify: `ct/4ct.py:708-831`

- [ ] **Step 1: Replace the entire function body**

Replace the function at lines 708–831 with:

```python
def select_edge_to_remove_first_fit(g_faces, choices, i_global_counter, prev_face=None):
    """
    Select an edge, that if removed doesn't have to leave the graph as 1-edge-connected.

    Parameters
    ----------
        g_faces: The entire graph from which the edge has to be selected
        choices: 2 + the permutations of 3 4 5
        i_global_counter: for debugging

    Returns
    -------
        edge_to_remove: The selected edge or, if not found, ()
        f1: The face of the selected edge
        f2: One edge separetes two faces
        f1_plus_f2_temp: It is used to speed up computation. I need it here and and it will be used outside this funcion
    """

    logger.info("BEGIN %s: Search the right edge to remove (faces left: %s)", i_global_counter, len(g_faces))

    choices_str = str(choices)
    if len(choices_str) != 4 or choices_str[0] != '2':
        logger.error("Value for choices (%s) not expected", choices)
        exit(-1)
    face_size_priority = [int(c) for c in choices_str]

    f1 = next(
        (f for size in face_size_priority for f in g_faces if len(f) == size),
        g_faces[0],
    )

    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("Selected face: %s", f1)

    result = next(
        (
            (edge, f2, joined)
            for edge in f1
            for f2 in [
                next(f for f in g_faces if rotate(edge, 1) in f and f is not f1)
                if len(f1) == 2
                else next(f for f in g_faces if rotate(edge, 1) in f)
            ]
            for joined in [join_faces(f1, f2, edge)]
            if not is_the_graph_one_edge_connected(joined)
        ),
        None,
    )

    if result is None:
        logger.error("END %s: Search the right edge to remove. NOT Found. It should not be possible", i_global_counter)
        exit(-1)

    edge_to_remove, f2, f1_plus_f2_temp = result
    logger.info("END %s: Search the right edge to remove. Found: %s (case: %s, %s)", i_global_counter, edge_to_remove, len(f1), len(f2))

    return edge_to_remove, f1, f2, f1_plus_f2_temp, None
```

- [ ] **Step 2: Run tests**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct
pytest ../tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 3: Smoke-test S1 end-to-end**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct
python3 4ct.py -s1 -r1 30
```

Expected: terminates without error, prints coloring result.

- [ ] **Step 4: Commit**

```bash
git add ct/4ct.py
git commit -m "refactor: simplify select_edge_to_remove_first_fit with next() generators"
```

---

### Task 2: Refactor S2 — `select_edge_to_remove_by_largest_neighbor`

**Files:**
- Modify: `ct/4ct.py:835-939`

- [ ] **Step 1: Replace the entire function body**

Replace the function at lines 835–939 with:

```python
def select_edge_to_remove_by_largest_neighbor(g_faces, choices, i_global_counter, prev_face=None):
    """
    Select an edge, that if removed doesn't have to leave the graph as 1-edge-connected.

    Among all faces of the same type (same size), this function evaluates every edge of every face,
    and selects the valid edge whose adjacent face (f2) is the largest.

    Parameters
    ----------
        g_faces: The entire graph from which the edge has to be selected
        choices: 2 + the permutations of 3 4 5
        i_global_counter: for debugging

    Returns
    -------
        edge_to_remove: The selected edge or, if not found, ()
        f1: The face of the selected edge
        f2: One edge separetes two faces
        f1_plus_f2_temp: It is used to speed up computation. I need it here and and it will be used outside this funcion
    """

    logger.info("BEGIN %s: Search the right edge to remove (faces left: %s)", i_global_counter, len(g_faces))

    choices_str = str(choices)
    if len(choices_str) != 4 or choices_str[0] != '2':
        logger.error("Value for choices (%s) not expected", choices)
        exit(-1)
    face_size_priority = [int(c) for c in choices_str]

    def _best_for_size(target_size):
        faces = [f for f in g_faces if len(f) == target_size]
        best_edge = best_f1 = best_f2 = best_joined = None
        best_f2_len = 0
        for candidate_f1 in faces:
            for edge in candidate_f1:
                rotated = rotate(edge, 1)
                if target_size == 2:
                    temp = [f for f in g_faces if rotated in f]
                    temp.remove(candidate_f1)
                    candidate_f2 = temp[0]
                else:
                    candidate_f2 = next(f for f in g_faces if rotated in f)
                candidate_joined = join_faces(candidate_f1, candidate_f2, edge)
                if not is_the_graph_one_edge_connected(candidate_joined) and len(candidate_f2) > best_f2_len:
                    best_f2_len = len(candidate_f2)
                    best_edge = edge
                    best_f1 = candidate_f1
                    best_f2 = candidate_f2
                    best_joined = candidate_joined
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("New best edge found: %s (f2 size: %s)", edge, best_f2_len)
        return (best_edge, best_f1, best_f2, best_joined) if best_edge is not None else None

    result = next(
        (r for size in face_size_priority for r in [_best_for_size(size)] if r is not None),
        None,
    )

    if result is None:
        logger.error("END %s: Search the right edge to remove. NOT Found. It should not be possible", i_global_counter)
        exit(-1)

    edge_to_remove, f1, f2, f1_plus_f2_temp = result
    logger.info("END %s: Search the right edge to remove. Found: %s (case: %s, %s)", i_global_counter, edge_to_remove, len(f1), len(f2))

    return edge_to_remove, f1, f2, f1_plus_f2_temp, None
```

- [ ] **Step 2: Run tests**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct
pytest ../tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 3: Smoke-test S2 end-to-end**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct
python3 4ct.py -s2 -r1 30
```

Expected: terminates without error, prints coloring result.

- [ ] **Step 4: Commit**

```bash
git add ct/4ct.py
git commit -m "refactor: simplify select_edge_to_remove_by_largest_neighbor with local closure"
```

---

### Task 3: Refactor S3 — `select_edge_to_remove_f5_shared_vertex`

**Files:**
- Modify: `ct/4ct.py:943-1075`

- [ ] **Step 1: Replace the entire function body**

Replace the function at lines 943–1075 with:

```python
def select_edge_to_remove_f5_shared_vertex(g_faces, choices, i_global_counter, prev_face=None):
    """
    Select an edge to remove using a strategy tailored for F5 faces.

    For F2/F3/F4 faces, behaves like first-fit.
    For F5 faces: finds an adjacent F5 or F6 face, then selects an edge from the F5
    that shares exactly one vertex with the neighboring face (not the shared border edge).

    Parameters
    ----------
        g_faces: The entire graph from which the edge has to be selected
        choices: 2 + the permutations of 3 4 5
        i_global_counter: for debugging

    Returns
    -------
        edge_to_remove: The selected edge or, if not found, ()
        f1: The face of the selected edge
        f2: One edge separates two faces
        f1_plus_f2_temp: It is used to speed up computation
    """

    logger.info("BEGIN %s: Search the right edge to remove - f5_shared_vertex (faces left: %s)", i_global_counter, len(g_faces))

    choices_str = str(choices)
    if len(choices_str) != 4 or choices_str[0] != '2':
        logger.error("Value for choices (%s) not expected", choices)
        exit(-1)
    face_size_priority = [int(c) for c in choices_str]

    log_suffix = ""

    def _try_for_size(target_size):
        nonlocal log_suffix
        faces = [f for f in g_faces if len(f) == target_size]

        if target_size <= 4:
            for candidate_f1 in faces:
                for edge in candidate_f1:
                    rotated = rotate(edge, 1)
                    if target_size == 2:
                        temp = [f for f in g_faces if rotated in f]
                        temp.remove(candidate_f1)
                        candidate_f2 = temp[0]
                    else:
                        candidate_f2 = next(f for f in g_faces if rotated in f)
                    candidate_joined = join_faces(candidate_f1, candidate_f2, edge)
                    if not is_the_graph_one_edge_connected(candidate_joined):
                        return (edge, candidate_f1, candidate_f2, candidate_joined)
            return None

        # F5: find an adjacent F5 or F6 and select an edge with exactly one shared vertex
        for candidate_f1 in faces:
            adjacent_target = next(
                (
                    neighbor
                    for edge in candidate_f1
                    for neighbor in [next(face for face in g_faces if rotate(edge, 1) in face)]
                    if len(neighbor) in (5, 6)
                ),
                None,
            )

            if adjacent_target is not None:
                adj_vertices = {v for e in adjacent_target for v in e}
                for edge in candidate_f1:
                    v1_shared = edge[0] in adj_vertices
                    v2_shared = edge[1] in adj_vertices
                    if v1_shared != v2_shared:
                        candidate_f2 = next(f for f in g_faces if rotate(edge, 1) in f)
                        candidate_joined = join_faces(candidate_f1, candidate_f2, edge)
                        if not is_the_graph_one_edge_connected(candidate_joined):
                            log_suffix = " [f5_shared_vertex: adj=%s]" % len(adjacent_target)
                            return (edge, candidate_f1, candidate_f2, candidate_joined)

        # Fallback for F5: any valid edge
        for candidate_f1 in faces:
            for edge in candidate_f1:
                candidate_f2 = next(f for f in g_faces if rotate(edge, 1) in f)
                candidate_joined = join_faces(candidate_f1, candidate_f2, edge)
                if not is_the_graph_one_edge_connected(candidate_joined):
                    log_suffix = " [f5_shared_vertex: fallback]"
                    return (edge, candidate_f1, candidate_f2, candidate_joined)

        return None

    result = next(
        (r for size in face_size_priority for r in [_try_for_size(size)] if r is not None),
        None,
    )

    if result is None:
        logger.error("END %s: Search the right edge to remove. NOT Found. It should not be possible", i_global_counter)
        exit(-1)

    edge_to_remove, f1, f2, f1_plus_f2_temp = result
    logger.info("END %s: Search the right edge to remove. Found: %s (case: %s, %s)%s", i_global_counter, edge_to_remove, len(f1), len(f2), log_suffix)
    return edge_to_remove, f1, f2, f1_plus_f2_temp, None
```

- [ ] **Step 2: Run tests**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct
pytest ../tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 3: Smoke-test S3 end-to-end**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct
python3 4ct.py -s3 -r1 30
```

Expected: terminates without error, prints coloring result.

- [ ] **Step 4: Commit**

```bash
git add ct/4ct.py
git commit -m "refactor: simplify select_edge_to_remove_f5_shared_vertex with local closure"
```

---

### Task 4: Final verification across all strategies

- [ ] **Step 1: Run full test suite one last time**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct
pytest ../tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 2: Smoke-test all four strategies**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct
python3 4ct.py -s1 -r1 50
python3 4ct.py -s2 -r1 50
python3 4ct.py -s3 -r1 50
python3 4ct.py -s4 -r1 50
```

Expected: each terminates without error and reports a valid coloring.
