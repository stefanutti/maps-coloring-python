# Design: Selection Strategy 4 — Unavoidable Set with Locality

**Date:** 2026-04-14  
**Branch:** feature/new-selection-method  
**Files affected:** `ct/4ct.py`

---

## Overview

Add a fourth edge-selection strategy (`-s4 / --selection4`) to the 4CT reduction algorithm. The strategy implements a priority-based selection across face sizes F2–F5, with a locality constraint that restricts F5 search to the neighborhood of the previously merged face.

---

## Contract

### New function

```python
def select_edge_to_remove_unavoidable_set(g_faces, choices, i_global_counter, prev_face=None):
```

**Inputs:**
- `g_faces`: list of faces (each face is a list of directed edge tuples)
- `choices`: integer encoding face-size priority (e.g. 2345)
- `i_global_counter`: iteration counter for logging
- `prev_face`: the `f1_plus_f2_temp` object returned by the previous call (or `None` on first call). Identity-compared against elements of `g_faces`.

**Returns:** `(edge_to_remove, f1, f2, f1_plus_f2_temp, new_prev_face)`
- `new_prev_face == f1_plus_f2_temp` — the merged face object that `reduce_faces` will insert into `g_faces`. Used by the caller to establish locality for the next iteration.

**Invariant:** `f1_plus_f2_temp` is the same Python object that `reduce_faces` inserts via `g_faces.insert(-1, f1_plus_f2_temp)`. The next call locates it with `next((f for f in g_faces if f is prev_face), None)`.

---

## Algorithm

### Phase F2 / F3 / F4 (global, locality ignored)

For each `target_size` in [2, 3, 4]:
1. Collect all faces of that size.
2. For each face, iterate over its edges.
3. Compute `f2` (adjacent face across the edge) and `f1_plus_f2_temp = join_faces(f1, f2, edge)`.
4. Skip if `is_the_graph_one_edge_connected(f1_plus_f2_temp)` is True.
5. Track the candidate with maximum `len(f2)`.
6. If at least one valid candidate exists for this size, return the best one immediately — do not proceed to the next size.

For F2 faces, use the two-list lookup (edge appears twice) as in the existing strategies.

### Phase F5 (only when no F2/F3/F4 exist)

**Locality filter:**

```python
prev_in_graph = next((f for f in g_faces if f is prev_face), None) if prev_face is not None else None

if prev_in_graph is not None:
    prev_vertices = {v for edge in prev_in_graph for v in edge}
    f5_candidates = [f for f in g_faces if len(f) == 5
                     and any(v in prev_vertices for edge in f for v in edge)]
    if not f5_candidates:
        f5_candidates = [f for f in g_faces if len(f) == 5]  # release constraint
else:
    f5_candidates = [f for f in g_faces if len(f) == 5]
```

**4a. F5-F5 pairs:**

For each F5 in `f5_candidates`:
- For each edge of the F5, find its adjacent face.
- If the adjacent face is also F5, we have a pair sharing edge `(v1, v2)`.
- Collect the 4 edges incident to `v1` and `v2` in the entire graph, excluding the shared edge `(v1, v2)` and its reverse.
- For each of the 4 candidate edges:
  - Find `f1` (face containing the directed edge) and `f2` (adjacent face).
  - Compute `f1_plus_f2_temp = join_faces(f1, f2, edge)`.
  - Skip if `is_the_graph_one_edge_connected(f1_plus_f2_temp)` is True.
  - Track candidate with maximum `len(f2)`.

**4b. F5-F6 pairs:**

Identical logic to 4a, but the adjacent face must have `len == 6` instead of 5.

**4c. Fallback:**

If neither 4a nor 4b produced any valid candidate:
- Apply "max neighbor" rule across all F5 faces in `f5_candidates`.
- If still no candidate and locality was active, release constraint and retry globally.
- For each F5, iterate edges, compute f2, check connectivity, track max `len(f2)`.

---

## State management in `reduce_faces`

`prev_face` is a local variable of `reduce_faces`, initialized before the `while` loop:

```python
prev_face = None
while ...:
    edge_to_remove, f1, f2, f1_plus_f2_temp, prev_face = selection_strategy(
        g_faces, choices, i_global_counter, prev_face
    )
```

No globals, no classes, no function attributes.

---

## Modifications to existing strategies

All three existing strategies receive `prev_face=None` as a new parameter (ignored). Their return value changes from 4 to 5 elements:

```python
return edge_to_remove, f1, f2, f1_plus_f2_temp, None
```

Affected functions:
- `select_edge_to_remove_first_fit`
- `select_edge_to_remove_by_largest_neighbor`
- `select_edge_to_remove_f5_shared_vertex`

---

## CLI

Added to `group_selection` (mutually exclusive with `-s1`/`-s2`/`-s3`):

```python
group_selection.add_argument("-s4", "--selection4",
    help="Edge selection strategy 4: unavoidable set with locality",
    action='store_true', default=False)
```

Dispatch:
```python
elif args.selection4:
    selection_strategy = select_edge_to_remove_unavoidable_set
```

---

## Error handling

- If no valid edge is found across all phases and fallbacks, the function reaches the existing `exit(-1)` path (consistent with other strategies).
- If `prev_face` is not found in `g_faces` (absorbed by a further merge), `prev_face` is treated as `None` and search proceeds globally.

---

## Out of scope

- Changes to `rebuild_faces`, coloring logic, or graph creation.
- Changes to the `choices` parameter encoding (F5 is already in the priority list).
- Tests are a separate task.
