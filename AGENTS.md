# AGENTS.md

This file contains the repository instructions for coding agents. Detailed
project documentation lives in `docs/` and is the source of truth for the
algorithm, architecture, and development commands.

## Project

Python implementation of an experimental Four Color Theorem algorithm based
on Tait edge-coloring. It reduces a planar cubic graph and reconstructs it
using Kempe-chain and half-cycle color switching.

Homepage and full write-up: https://4coloring.wordpress.com

## Canonical documentation

- `docs/algorithm.md` — mathematical model, reduction, S1-S4, Ariadne, Kempe.
- `docs/architecture.md` — current modules, state, data formats, boundaries.
- `docs/development.md` — environment, `uv`, CLI, converters, tests, debug.

Read the relevant document before changing that area. Keep detailed
explanations in their canonical document instead of copying them here.

## Working rules

- Run the main program and tests with `ct/` as the working directory; the
  program writes relative paths under `ct/debug/`.
- Preserve the names and current roles of `ct/4ct.py` and
  `ct/ct_graph_utils.py` unless the user explicitly requests a refactor.
- Treat `g_faces` as the source of truth during reduction and keep every
  derived `FaceIndex` lookup synchronized with it.
- Preserve user changes and keep generated debug artifacts out of Git.

## Invariants

- Input graphs must be planar, cubic (3-regular), and loop-free.
- Every graph edge represented by `g_faces` must appear once in each
  direction, one occurrence for each adjacent face.
- An accepted reduction must leave the graph bridge-free. S4's F2 branch
  assumes this property is automatic and does not call the bridge check.
- Every selection strategy returns exactly
  `(edge, f1, f2, f1_plus_f2, event)`.
- `event` is `None` for S1/S2/S3. In S4 it is `'fallback'` only when a global
  F5 fallback fires with an active wave; `reduce_faces()` consumes the event.
- Preserve the Ariadne record formats consumed by `rebuild_faces()`.
- The reconstructed graph must retain the original vertex/edge counts and
  pass `is_well_colored()`.

## Coding style

- Prefer clear, linear control flow.
- Use guard clauses only when they improve readability; avoid unnecessary
  nesting, `break`, `continue`, and early returns.
- Reuse the NetworkX wrappers and graph primitives in `ct_graph_utils.py`.
- Do not introduce pure delegation wrappers; `test_no_pure_wrappers.py`
  protects this constraint.

## Verification

From the repository root:

```bash
cd ct
uv run --python ../.venv/bin/python python -m pytest tests -q
uv run --python ../.venv/bin/python python 4ct.py -s1 -r2 10
```

For focused tests, additional smoke tests, setup, and troubleshooting, follow
`docs/development.md`.
