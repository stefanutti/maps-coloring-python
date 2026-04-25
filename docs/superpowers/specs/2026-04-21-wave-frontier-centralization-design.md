# Wave frontier centralization in `reduce_faces`

## Context

The selection strategy `select_edge_to_remove_unavoidable_set` (S4) uses a set of vertex IDs, `recently_modified_vertices`, as a "wave frontier" to prioritize F5 faces that touch recently-modified areas of the graph. Today this set is both **read and written** inside S4, and is threaded through `reduce_faces` as the 5th element of the selection-strategy return tuple.

Two problems with the current arrangement:

1. **Stale vertices accumulate.** When an edge `(v1, v2)` is removed, `v1` and `v2` disappear from the graph (their incident faces are merged and their references stripped by `remove_vertex_from_face`). But the wave frontier set only grows — via `recently_modified_vertices | _vertices_of(best_f1_plus_f2)` — and never discards removed vertices. These "ghost" vertices are filtered out implicitly by the `v in recently_modified_vertices` check at line 1169 (because current faces no longer contain them), so there is no functional bug, but the set grows monotonically with session length and the semantics of its name drift from reality.

2. **Responsibility leak.** The selection strategy's job is to *choose an edge*, not to know that the graph will subsequently be modified. Mutating the wave frontier inside the strategy couples selection with bookkeeping about graph state.

## Goal

Move all wave-frontier writes into `reduce_faces`. The selection strategy reads the frontier (for locality filtering) but does not return an updated one. The frontier is cleaned of removed vertices at each iteration.

## Non-goals

- No change to the selection behavior of S1, S2, S3.
- No change to S4's *selection* logic (locality filter, step ordering F5-F5 → F5-F6 → global fallback).
- No change to the 5-tuple return contract of selection strategies. The 5th element (`extra`) simply returns to being always `None`, as documented in CLAUDE.md.

## Design

### 1. Responsibility split

- `reduce_faces` becomes the single writer of `recently_modified_vertices`.
- `select_edge_to_remove_unavoidable_set` reads the parameter (unchanged: used for `local_f5` filtering at line 1169 and for the `SELECT-S4-F4-INTERRUPT` stat at lines 1125, 1159). It no longer computes or returns a new set.
- All selection strategies return `(edge, f1, f2, f1_plus_f2, None)`. The CLAUDE.md invariant "`extra` is currently always `None`" becomes true again.

### 2. Update logic in `reduce_faces`

Extract a pure helper function:

```python
def update_wave_frontier(current, f1_len, f1_plus_f2, v1, v2):
    """
    Return the new wave frontier after reducing one face.

    - If f1_len == 5 (F5 reduction), activate or extend the frontier with the
      surviving vertices of the merged face, minus the vertices that were
      removed from the graph.
    - If f1_len < 5 but the frontier was already active, keep extending and
      cleaning.
    - Otherwise, return None (frontier remains inactive).
    """
    is_f5 = (f1_len == 5)
    was_active = current is not None
    if not (is_f5 or was_active):
        return None
    base = current if was_active else set()
    return (base | _vertices_of(f1_plus_f2)) - {v1, v2}
```

This preserves S4's current activation semantics (wave activates the first time F5 phase is reached; once active, stays active across F2/F3/F4 interruptions) and adds the `- {v1, v2}` cleanup.

`reduce_faces` calls it once per iteration, right after `selection_strategy(...)`:

```python
edge_to_remove, f1, f2, f1_plus_f2_temp, _ = selection_strategy(
    g_faces, choices, i_global_counter, recently_modified_vertices
)

if edge_to_remove == ():
    logger.error(...); exit(-1)

v1, v2 = edge_to_remove
recently_modified_vertices = update_wave_frontier(
    recently_modified_vertices, len(f1), f1_plus_f2_temp, v1, v2
)
```

The duplicate local assignments `v1 = edge_to_remove[0]` and `v2 = edge_to_remove[1]` inside the F2 branch (lines 1584-1585) and the F3/F4/F5 branch (lines 1641-1642) are removed — `v1` and `v2` are now computed once at the top of the loop body.

Immutability is preserved: `update_wave_frontier` returns a new set; `reduce_faces` re-binds the variable, does not mutate in place.

### 3. S4 edits

In `select_edge_to_remove_unavoidable_set`:

- Remove the `new_rmv = ...` computations at lines 1126, 1160, 1178, 1187.
- Replace all six `return` statements that currently return `new_rmv` or `_vertices_of(...)` as the 5th element with `None`.
- Keep the reads of `recently_modified_vertices` (line 1124 gate, line 1168 locality filter) exactly as they are.
- Update the docstring: remove the "Return: None when wave not active..." and "Return: input | vertices(merged_face)" lines.

The `_vertices_of` helper (line 1068) stays in `4ct.py`: it is no longer used by S4 after this refactor, but it is reused by `update_wave_frontier` (see Section 2). Keeping it as a named helper rather than inlining the set comprehension preserves readability.

### 4. Testing

**Update existing tests** in `tests/test_selection4.py`: the assertions that inspect the 5th return element as a set must change to `assert extra is None`.

**Add new tests** on `update_wave_frontier` (pure function, easy to test):

- F5 reduction from inactive state → returns union of merged-face vertices minus `{v1, v2}`.
- F5 reduction from active state → extends existing set, removes `{v1, v2}`.
- F2/F3/F4 reduction from inactive state → returns `None`.
- F2/F3/F4 reduction from active state → extends and cleans.
- `v1, v2` already present in `current` (the ghost-vertex case) → they are removed from the output set.

**Behavioral smoke test:** run `python3 4ct.py -s4 -r1 100` (or a deterministic seed) before and after the refactor. The final coloring must be identical. The counters `SELECT-S4-F5-F5`, `SELECT-S4-F5-F6`, `SELECT-S4-F5-FALLBACK`, `SELECT-S4-F4-INTERRUPT` may change slightly because the frontier is now cleaner — this is expected and semantically more correct, not a regression.

## Open questions

None — all points resolved during brainstorming.
