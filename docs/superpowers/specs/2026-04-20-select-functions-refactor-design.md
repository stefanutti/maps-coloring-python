# Select Functions Refactor — Design Spec

**Date:** 2026-04-20  
**Scope:** `ct/4ct.py` — four edge-selection functions  
**Type:** Pure refactor — no behavior change

## Goal

Eliminate verbose index-based while loops, boolean flag variables, and duplicated choices-parsing branches across the four edge-selection functions. Replace with `next()` generator expressions and `for item in collection` iteration, consistent with the style already used in S2/S3.

## Functions in Scope

- `select_edge_to_remove_first_fit` (S1)
- `select_edge_to_remove_by_largest_neighbor` (S2)
- `select_edge_to_remove_f5_shared_vertex` (S3)
- `select_edge_to_remove_unavoidable_set` (S4) — no changes needed

## Constraints

- Pure refactor: identical behavior, identical return contract `(edge, f1, f2, f1_plus_f2, None)`
- No new module-level helper functions; local closures within a function body are allowed
- No new shared state between functions
- No break/continue — use `next()` generators for short-circuit "find first/best" patterns

---

## S1 — `select_edge_to_remove_first_fit`

### Change 1: Choices parsing

**Before:** 6-branch `if choices == 2345 / elif choices == 2354 / ...` block selecting `f1` via a 4-deep nested `next(..., next(...))` chain.

**After:** Parse once into a priority list (same pattern as S2/S3), then select `f1` with a flat generator:

```python
choices_str = str(choices)
if len(choices_str) != 4 or choices_str[0] != '2':
    logger.error("Value for choices (%s) not expected", choices)
    exit(-1)
face_size_priority = [int(c) for c in choices_str]

f1 = next(
    (f for size in face_size_priority for f in g_faces if len(f) == size),
    g_faces[0]
)
```

### Change 2: Edge scan

**Before:** `while is_the_edge_to_remove_found is False and i_edge < len_of_the_face_to_reduce` with a boolean flag and index counter.

**After:** `next()` generator that binds `f2` and `joined` inline via the list-in-generator trick:

```python
result = next(
    (
        (edge, f2, joined)
        for edge in f1
        for f2 in [<f2_lookup_inline>]
        for joined in [join_faces(f1, f2, edge)]
        if not is_the_graph_one_edge_connected(joined)
    ),
    None,
)
```

Where `<f2_lookup_inline>` is the F2 special-case expression inlined:
- F2: `next(f for f in g_faces if rotate(edge, 1) in f and f is not f1)` — identity check, equivalent to original's `.remove(f1)`: for F2 the rotated edge appears in exactly two faces, so excluding `f1` by identity leaves exactly one.
- Other: `next(f for f in g_faces if rotate(edge, 1) in f)`

Combined as a ternary conditional in the for-clause:

```python
for f2 in [
    next(f for f in g_faces if rotate(edge, 1) in f and f is not f1)
    if len(f1) == 2
    else next(f for f in g_faces if rotate(edge, 1) in f)
]
```

The error/success logging and final return remain identical.

---

## S2 — `select_edge_to_remove_by_largest_neighbor`

### Change 1: Outer while loop → local closure + next()

**Before:** `while best_edge_to_remove is None and i_size < len(face_size_priority): i_size += 1` with 4 accumulator variables reset per iteration.

**After:** Extract the per-size scan into a local closure `_best_for_size(size)` → returns `(edge, f1, f2, joined)` or `None`. Top level becomes:

```python
result = next(
    (r for size in face_size_priority for r in [_best_for_size(size)] if r is not None),
    None,
)
```

### Change 2: Inner index loop → for-each

**Before:** `for i_edge in range(len(candidate_f1)): edge = candidate_f1[i_edge]`

**After:** `for edge in candidate_f1:`

The F2 adjacency lookup and bridge check logic inside the closure are unchanged.

---

## S3 — `select_edge_to_remove_f5_shared_vertex`

### Change: All nested `while result is None and i_xxx` loops

**Before:** Three levels of `while result is None and i_xxx < len(...)` + `i_xxx += 1` for the outer size loop, per-face loop, and per-edge loop.

**After:** Extract per-size logic into a local closure `_try_for_size(size)` → returns a 4-tuple or `None`. Top level:

```python
result = next(
    (r for size in face_size_priority for r in [_try_for_size(size)] if r is not None),
    None,
)
```

Inside `_try_for_size`:
- F2/F3/F4 path: `for candidate_f1 in faces_of_this_size: for edge in candidate_f1:` (no index variables)
- F5 path: same structure as today — find adjacent F5/F6, select shared-vertex edge, fallback — but using `for` iteration instead of while+index throughout

The F5 shared-vertex logic (adjacency search, vertex set, exactly-one-shared-vertex filter, fallback scan) is preserved exactly.

---

## S4 — `select_edge_to_remove_unavoidable_set`

No changes. Already uses `for` iteration, `next()` generators, and no index-based while loops.

---

## Testing

- All existing tests in `tests/` must pass unchanged after the refactor.
- Run `pytest tests/ -v` to verify.
- Spot-check with `python3 4ct.py -r1 100 -s1`, `-s2`, `-s3`, `-s4` to confirm identical behavior.
