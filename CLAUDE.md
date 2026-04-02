# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python implementation of an algorithm to 4-color planar graphs (Four Color Theorem). It uses Tait edge coloring (3-edge-coloring) combined with a modified Kempe reduction method. The project blog is at https://4coloring.wordpress.com.

## Running the Main Algorithm

All commands are run from the `ct/` directory:

```bash
# Random graph: dual of a triangulation with N vertices
python3 4ct.py -r1 100

# Random graph: subdivision of faces (directly planar) with N faces
python3 4ct.py -r2 100

# Load a planar embedding file
python3 4ct.py -p file.planar

# Load an edgelist file (NetworkX format)
python3 4ct.py -e file.edgelist

# Save output (generates .edgelist and .dot files)
python3 4ct.py -r1 100 -o output_name

# Choose Kempe sequence order (helps with infinite loop cases)
python3 4ct.py -r1 100 -c 2354

# Shuffle faces at start (often resolves infinite loop conditions)
python3 4ct.py -r1 100 -s

# Run the entire process N times
python3 4ct.py -r1 100 -n 10

# Choose edge selection strategy (default: -s1)
python3 4ct.py -r1 100 -s1   # first fit: first valid edge in the first face of the right priority (default)
python3 4ct.py -r1 100 -s2   # best adjacent face: maximizes f2 size across all candidates
```

## Utility Scripts

```bash
# Generate random planar graphs (run from ct/ directory)
python3 converters/ct_create_random_maps_from_2v.py -v 100 -o new_map.planar

# Convert planar embedding to edgelist/dot formats
python3 converters/ct_convert_planar_to_other.py -p file.planar -o output_name
```

## Linting

```bash
flake8 ct/
```

Config is in `tox.ini`: ignores E402, E501, E701; max complexity 10.

## Dependencies

- `networkx` — core graph library
- `numpy` — random number generation
- `pydot` — DOT format export
- `torch` + `torch_geometric` — only for ML experiments in `ct/machine_learning/`
- `flask` — only for web interfaces in `ct/web_*`

## Architecture

### Core Files

**`ct/4ct.py`** — Main algorithm entry point. Orchestrates the reduction/reconstruction loop:
1. Reads graph (random, edgelist, or planar format)
2. Reduces the graph iteratively by removing edges from F2/F3/F4/F5 faces
3. Colors the base case
4. Reconstructs by restoring edges and applying Kempe chain color swaps

**`ct/ct_graph_utils.py`** — All graph utility functions used by `4ct.py`. Key concepts:
- Graph is a NetworkX `MultiDiGraph` with edge labels storing colors (`c1`, `c2`, `c3`)
- Planar faces stored as lists of directed edge tuples: `[(v1, v2), (v2, v3), ...]`
- Kempe chains: cycles of two alternating colors used for color swapping

### Graph Representation

- **Vertices**: integer IDs
- **Edges**: stored with color labels in the MultiDiGraph
- **Faces**: lists of directed edges (clockwise ordering of neighbors = planar embedding)
- **Planar input format** (`.planar`): JSON representation of `G.faces()` output

### Key Algorithm Concepts

- **F2/F3/F4/F5**: faces with 2/3/4/5 edges — the "unavoidable set" for reduction
- **Kempe chain**: alternating color cycle; swapping half of a loop recolors without conflicts
- **Infinite loop risk**: F5 cases may loop indefinitely — use `-s` (shuffle) or `-c` (different sequence) to escape

### Converters (`ct/converters/`)

- `ct_create_random_maps_from_2v.py` — `PlanarGraphGenerator` class; generates random cubic planar graphs without Sage
- `ct_convert_planar_to_other.py` — converts `.planar` JSON to `.edgelist` and `.dot`
- `ct_convert_gml_to_planar.py` — converts GML format to `.planar`

### ML Experiments (`ct/machine_learning/`)

Experimental DQN (Double Deep Q-Network) agent using PyTorch Geometric. Not part of the core algorithm.

## Known Limitations

- The F5 reduction case can enter an infinite loop for certain graphs. This is a known open problem. Use `-s` (shuffle) to randomize face order, which resolves it in most cases.
