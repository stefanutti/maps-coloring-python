# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Python implementation of a Four Color Theorem algorithm. The approach uses Tait edge-coloring equivalency: a 3-edge-coloring of a planar cubic graph is equivalent to a 4-face-coloring. The algorithm reduces the graph by removing edges (Kempe-style), then reconstructs with half-cycle Kempe chain color switching.

Homepage and full write-up: https://4coloring.wordpress.com

## Environment

```bash
source .venv/bin/activate          # activate virtualenv (Python 3)
pip install networkx numpy pydot   # core runtime deps
pip install pytest                 # for running tests (not pre-installed)
```

All commands below assume the virtualenv is active and CWD is `ct/`.

## Commands

```bash
# Run the algorithm
python3 4ct.py --help
python3 4ct.py -r1 100             # random graph: dual of a triangulation of 100 vertices
python3 4ct.py -r2 100             # random graph: face subdivision with 100 faces
python3 4ct.py -p <file.planar>    # load planar embedding (JSON)
python3 4ct.py -e <file.edgelist>  # load NetworkX edgelist
python3 4ct.py -s4 -r1 100         # use selection strategy 4

# Flags
#   -o <name>       save .edgelist + .dot output
#   -c {2345,...}   face priority sequence (permutations of 3,4,5 with 2 first)
#   -s              shuffle face list at start
#   -n N            repeat N times
#   -s1|-s2|-s3|-s4 edge selection strategy

# Converters
python3 converters/ct_create_random_maps_from_2v.py -v 100 -o map.planar
python3 converters/ct_convert_planar_to_other.py -p map.planar -o map

# Tests
pytest tests/ -v
```

## Architecture

### Core data structure: `g_faces`

The entire graph is represented as a list of faces. Each face is a list of directed edges (tuples), ordered clockwise. The last face is always the "ocean" (outer face, counter-clockwise):

```python
g_faces = [
    [(0,1), (1,2), (2,0)],           # triangle face
    [(0,2), (2,4), (4,3), (3,0)],    # quad face
    ...                              # last entry = ocean
]
```

An edge `(u, v)` in face A appears as `(v, u)` in the adjacent face B. This rotated form is used throughout to find the neighboring face of any edge.

### Main flow (`ct/4ct.py`)

1. **Graph creation** — generate or load a planar cubic (3-regular) graph
2. **Face extraction** — convert to `g_faces` planar embedding
3. **Reduction loop** — iteratively pick an edge, verify removing it doesn't leave the graph 1-edge-connected (`is_the_graph_one_edge_connected`), merge the two adjacent faces, and push the removed edge onto a stack
4. **Reconstruction (Ariadne)** — pop edges off the stack, re-insert each, recolor with Kempe chain / half-cycle switching
5. **Validation** — `is_well_colored()` checks final coloring

### Edge selection strategies (the active research area)

Each strategy selects which edge to remove at each reduction step. All return `(edge_to_remove, f1, f2, f1_plus_f2_temp, extra)`:

| Strategy | Function | Behavior |
|----------|----------|----------|
| S1 | `select_edge_to_remove` | First valid edge of first face in priority order |
| S2 | `select_edge_to_remove_by_largest_neighbor` | Valid edge whose adjacent face f2 is largest |
| S3 | `select_edge_to_remove_f5_shared_vertex` | For F5: prefer edges sharing exactly one vertex with an adjacent F5/F6 |
| S4 | `select_edge_to_remove_selection4` | Locality-aware: prioritizes faces containing recently-modified vertices (wave frontier) |

Face priority (`choices` parameter): F2 always first, then a permutation of F3/F4/F5. Encoded as an integer, e.g. `2345`.

### Key files

- **`ct/4ct.py`** — entry point, main loop, all selection strategies, Ariadne reconstruction
- **`ct/ct_graph_utils.py`** — all graph primitives: `create_graph_from_planar_representation`, `kempe_chain_color_swap`, `apply_half_kempe_loop_color_switching`, `is_well_colored`, `check_graph_planarity_3_regularity_no_loops`, and NetworkX wrappers
- **`ct/converters/`** — standalone tools to generate and convert graph formats
- **`tests/`** — pytest suite; `test_selection4.py` covers the S4 return contract and F5/F6 edge cases

### Invariants to preserve

- Every graph processed must be planar, cubic (3-regular), and loop-free — enforced by `check_graph_planarity_3_regularity_no_loops`
- `g_faces` must always cover every edge exactly twice (once per direction)
- After removal, the reduced graph must not be 1-edge-connected (bridge-free)
- All selection strategy functions must return a 5-tuple `(edge, f1, f2, f1_plus_f2, event)` — `event` is a selection-event signal consumed by `reduce_faces`. `None` for S1/S2/S3. For S4 it is `'fallback'` when the global F5 fallback fires with an active wave (the caller resets the wave), otherwise `None`.

## Coding Style
- Write code with clear, linear control flow that minimizes break, continue, and early return, allowing them only when they clearly improve readability (e.g., simple guard clauses) and avoiding unnecessary nesting or complex jumps.
