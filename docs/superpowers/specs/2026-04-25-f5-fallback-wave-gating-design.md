# SELECT-S4-F5-FALLBACK wave gating — Design

## Problem

In `ct/4ct.py::select_edge_to_remove_unavoidable_set`, the stat
`SELECT-S4-F5-FALLBACK` is incremented unconditionally whenever the global
F5 search produces an edge (lines 1211 and 1217). The stat is meant to
quantify *wave interruptions* — cases where an active locality wave had to
give up local search and fall back to a global F5 scan — but it currently
also counts the normal opening case where no wave has been started yet.

## Decision

Increment `SELECT-S4-F5-FALLBACK` only when a wave is active at the moment
the global fallback succeeds, i.e. when `recently_modified_vertices is
not None`.

Semantically, the stat then counts only the event:
"a wave was running, no F2/F3/F4 existed, no local F5 (F5-F5 or F5-F6) was
available, so the wave was forced to interrupt and resort to a global F5
search."

When `recently_modified_vertices is None` and the global fallback is taken
(typical opening, before the first F5 has ever been removed) nothing is
counted — that path is not considered an interruption.

## Out of scope

`SELECT-S4-F4-INTERRUPT` (lines 1147 and 1179) is left unchanged. F4 faces
are absorbed into the wave per the existing wave-frontier logic, and the
existing increment for F3/F4 with an active wave is intentionally
preserved.

## Change set

`ct/4ct.py`, function `select_edge_to_remove_unavoidable_set`:

- Line 1211 — guard the increment with `if recently_modified_vertices is
  not None`.
- Line 1217 — same guard.

Logging is unchanged.

## Verification

Run `pytest tests/ -v` to confirm no regression. No new test is added:
the codebase has no existing tests for these telemetry counters, and
adding one purely for a counted-vs-not-counted change is out of scope
for this small fix.
