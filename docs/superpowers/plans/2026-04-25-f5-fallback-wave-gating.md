# SELECT-S4-F5-FALLBACK wave gating Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Increment the `SELECT-S4-F5-FALLBACK` stat only when a wave is active at the moment the global F5 fallback succeeds.

**Architecture:** Two-line guard added in `select_edge_to_remove_unavoidable_set` in `ct/4ct.py`. No new tests — the codebase has no tests for these telemetry counters, and the spec explicitly scopes test additions out. Verification is the existing pytest suite passing.

**Tech Stack:** Python 3, pytest.

---

### Task 1: Guard both fallback increments with the wave-active check

**Files:**
- Modify: `ct/4ct.py:1211` and `ct/4ct.py:1217`
- Test: `tests/` (existing suite, no new test file)

- [ ] **Step 1: Apply the guard at line 1211 (global F5-F5 fallback)**

Replace:

```python
    best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_from_f5_pairs(g_faces, all_f5, pair_neighbor_size=5)
    if best_edge is not None:
        stats['SELECT-S4-F5-FALLBACK'] += 1
        logger.info("END %s: found via global F5-F5 fallback. Edge: %s", i_global_counter, best_edge)
        return best_edge, best_f1, best_f2, best_f1_plus_f2, None
```

With:

```python
    best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_from_f5_pairs(g_faces, all_f5, pair_neighbor_size=5)
    if best_edge is not None:
        if recently_modified_vertices is not None:
            stats['SELECT-S4-F5-FALLBACK'] += 1
        logger.info("END %s: found via global F5-F5 fallback. Edge: %s", i_global_counter, best_edge)
        return best_edge, best_f1, best_f2, best_f1_plus_f2, None
```

- [ ] **Step 2: Apply the guard at line 1217 (global F5-F6 fallback)**

Replace:

```python
    best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_f5_f6_edge(g_faces, all_f5)
    if best_edge is not None:
        stats['SELECT-S4-F5-FALLBACK'] += 1
        logger.info("END %s: found via global F5-F6 fallback. Edge: %s", i_global_counter, best_edge)
        return best_edge, best_f1, best_f2, best_f1_plus_f2, None
```

With:

```python
    best_edge, best_f1, best_f2, best_f1_plus_f2 = _select_f5_f6_edge(g_faces, all_f5)
    if best_edge is not None:
        if recently_modified_vertices is not None:
            stats['SELECT-S4-F5-FALLBACK'] += 1
        logger.info("END %s: found via global F5-F6 fallback. Edge: %s", i_global_counter, best_edge)
        return best_edge, best_f1, best_f2, best_f1_plus_f2, None
```

- [ ] **Step 3: Run the existing test suite**

Run: `cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python && source .venv/bin/activate && pytest tests/ -v`
Expected: all tests PASS (same set that was passing before the change).

- [ ] **Step 4: Smoke-run the algorithm with strategy 4**

Run: `cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct && python3 4ct.py -s4 -r1 100`
Expected: completes without error, prints stats including `SELECT-S4-F5-FALLBACK` (value may be 0 or higher; what matters is the run completes and the counter shows up in the printed stats block).

- [ ] **Step 5: Commit**

```bash
git add ct/4ct.py
git commit -m "feat: gate SELECT-S4-F5-FALLBACK on active wave"
```
