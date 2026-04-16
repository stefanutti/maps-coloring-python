# Selection Strategy 4 — Redesign Spec

**Date:** 2026-04-16
**Branch:** feature/new-selection-method
**Function:** `select_edge_to_remove_unavoidable_set` in `ct/4ct.py`

---

## Context

The graph is planar, 3-regular (cubic), and embedded. Faces are explicitly available as lists of directed-edge tuples `[(v1, v2), (v2, v3), ...]`. The algorithm iteratively removes edges to reduce the graph. This function is the edge-selection strategy used with `--selection4` / `-s4`.

---

## Signature Change

```python
# Before
def select_edge_to_remove_unavoidable_set(g_faces, choices, i_global_counter, prev_face=None):
    ...
    return edge, f1, f2, f1_plus_f2, prev_face

# After
def select_edge_to_remove_unavoidable_set(g_faces, choices, i_global_counter, recently_modified_vertices=None):
    ...
    return edge, f1, f2, f1_plus_f2, recently_modified_vertices
```

`recently_modified_vertices` is a `set` of vertex IDs (integers) representing the wave frontier, or `None`. It is passed in from the previous call's return value by the main loop (same pattern as the old `prev_face`). The main loop rename: `prev_face` → `recently_modified_vertices` at the call site.

---

## Phase 1 — F2 / F3 / F4

Runs at the top of every call. Exhausts size class 2, then 3, then 4.

### F2 rule
- Pick **one F2 face at random** from all F2 faces.
- Pick **one of its two edges at random**.
- No validity check needed beyond not making the graph 1-edge-connected.

### F3 / F4 rule (unchanged from current)
- Among all faces of that size, scan every edge of every face.
- Pick the valid edge (removal does not make graph 1-edge-connected) whose adjacent face `f2` is **largest**.

### Return value from Phase 1
- If `recently_modified_vertices` was `None` on entry: return `None` (wave not started yet).
- If `recently_modified_vertices` was non-empty on entry (F4 interrupt during Phase 2 run): return `recently_modified_vertices | vertices(f1_plus_f2)` — keeps the wave alive.

---

## Phase 2 — F5 (only reached when no F2/F3/F4 remain)

### Local candidate selection

Compute the set of local F5 candidate faces:
- If `recently_modified_vertices` is non-empty: `[f for f in g_faces if len(f) == 5 and any(v in recently_modified_vertices for edge in f for v in edge)]`
- If empty or `None`: no local candidates → go directly to **Step 4 (global fallback)**.

### Step 1 — F5-F5 (local, highest priority)

From local candidates, call `_select_from_f5_pairs(g_faces, local_f5, pair_neighbor_size=5)`.

Rule (unchanged): for each F5-F5 adjacent pair, evaluate the 4 edges incident to the shared edge's two endpoints (2 from each face, excluding the shared edge). Pick the valid edge with the largest adjacent face `f2`.

### Step 2 — F5-F6 (local)

From local candidates, scan for F5 faces adjacent to an F6.

**New rule** (replaces the old 4-edge scan):
- Identify the shared edge between F5 and F6: `shared_edge = (v1, v2)` as it appears in F5.
- The two candidate edges are the edges of **F5 only** that touch `v1` or `v2`:
  - `face_a[(i_shared - 1) % n_a]` — edge ending at `v1`
  - `face_a[(i_shared + 1) % n_a]` — edge starting at `v2`
- For each candidate edge, find its adjacent face `f2` (the face containing the rotated edge).
- Skip if removal makes graph 1-edge-connected.
- Pick the valid candidate whose `f2` is **largest**.

### Return value from Phase 2 (Steps 1 & 2)

`recently_modified_vertices = recently_modified_vertices | vertices(f1_plus_f2)`

where `vertices(face) = {v for edge in face for v in edge}`.

### Step 4 — Global fallback

Triggered when: no local candidates exist, or local search found nothing.

- Scan all `g_faces` globally for the **first** F5-F5 pair; apply the F5-F5 rule above.
- If none found, scan for the **first** F5-F6 pair; apply the F5-F6 rule above.
- Return `recently_modified_vertices = vertices(f1_plus_f2)` (fresh wave start).

---

## F4 Interrupt

No special logic required. Because Phase 1 runs at the top of every call, any F4 that re-emerged from a prior Phase 2 removal is automatically caught on the next call. The only new behavior: when Phase 1 fires while `recently_modified_vertices` is non-empty, the return value unions the merged face vertices in (see Phase 1 return value above).

---

## Helper Changes

### `_select_from_f5_pairs` — unchanged

Used for F5-F5 only. Signature and logic stay the same.

### New helper: `_select_f5_f6_edge`

```python
def _select_f5_f6_edge(g_faces, f5_candidates):
    """
    For each F5 in f5_candidates adjacent to an F6, evaluate the 2 edges of the F5
    face at the shared edge's endpoints. Return the valid edge with the largest f2.
    Returns (best_edge, best_f1, best_f2, best_f1_plus_f2) or (None, None, None, None).
    """
```

### `_select_max_neighbor_from_candidates` — removed from F5-F6 path

No longer used for F5-F6. Kept only if needed elsewhere (currently used in fallback for F5; evaluate whether it can be removed entirely).

---

## Statistics Counters

Existing counters kept:
- `stats['SELECT-S4-F5-F5']`
- `stats['SELECT-S4-F5-F6']`
- `stats['SELECT-S4-F5-FALLBACK']`

Add:
- `stats['SELECT-S4-F4-INTERRUPT']` — incremented when Phase 1 fires while `recently_modified_vertices` is non-empty.

---

## Constraints

- The function must never mutate `g_faces` — selection only, no removal.
- All existing callers of the function are unaffected except the main loop renaming `prev_face` → `recently_modified_vertices`.
- `choices` parameter is still accepted (and warned about if not 2345) for compatibility.
