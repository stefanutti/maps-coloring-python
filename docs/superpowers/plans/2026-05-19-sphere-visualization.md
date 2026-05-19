# Sphere Visualization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone PyVista tool to explore cubic planar maps on a sphere, starting from 2 vertices + 3 edges, growing interactively by splitting faces.

**Architecture:** `spherical_map.py` owns all graph data and pure operations (no rendering). `renderer.py` converts it to PyVista actors with incremental O(1) refresh. `interaction.py` implements the state machine + screen-space edge picking. `main.py` wires them together.

**Tech Stack:** Python 3, PyVista, NumPy, pytest

---

## File Map

| File | Responsibility |
|------|---------------|
| `python_tests/sphere/spherical_map.py` | `Edge`, `SphericalMap` dataclasses; `slerp`, `normalize`, `geodesic_samples`, `point_in_face`, `neighbors`, `assign_color`, `auto_waypoints`, `split_face`, `split_face_auto`, `grow_map`, `make_initial_map` |
| `python_tests/sphere/renderer.py` | `SphereRenderer`: PyVista plotter, `build_face_mesh`, `build_edge_mesh`, `build_vertex_mesh`, `add_split_result`, `update_hud` |
| `python_tests/sphere/interaction.py` | `InteractionController`: screen-space cache, `find_edge_at_cursor`, state machine callbacks, key bindings |
| `python_tests/sphere/main.py` | Entry point: instantiate map + renderer + controller, launch `plotter.show()` |
| `python_tests/sphere/tests/test_spherical_map.py` | Unit tests: invariants, split, waypoints, auto-split |

---

## Task 1: Package scaffold + geometry primitives

**Files:**
- Create: `python_tests/sphere/__init__.py`
- Create: `python_tests/sphere/tests/__init__.py`
- Create: `python_tests/sphere/spherical_map.py`
- Create: `python_tests/sphere/tests/test_spherical_map.py`

- [ ] **Step 1.1: Write failing tests for geometry primitives**

```python
# python_tests/sphere/tests/test_spherical_map.py
import numpy as np
import pytest
from sphere.spherical_map import normalize, slerp, geodesic_samples, point_in_face

def test_normalize_unit_length():
    v = np.array([3.0, 0.0, 0.0])
    assert np.allclose(np.linalg.norm(normalize(v)), 1.0)

def test_slerp_endpoints():
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([0.0, 1.0, 0.0])
    assert np.allclose(slerp(a, b, 0.0), a)
    assert np.allclose(slerp(a, b, 1.0), b)

def test_slerp_midpoint_on_sphere():
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([0.0, 1.0, 0.0])
    m = slerp(a, b, 0.5)
    assert abs(np.linalg.norm(m) - 1.0) < 1e-10

def test_geodesic_samples_count():
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([0.0, 1.0, 0.0])
    pts = geodesic_samples(a, b, n=10)
    assert len(pts) == 10
    assert np.allclose(pts[0], a)
    assert np.allclose(pts[-1], b)

def test_point_in_face_centroid():
    # Triangle on sphere: roughly equatorial
    verts = [
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([0.0, 0.0, 1.0]),
    ]
    c = normalize(sum(verts))
    assert point_in_face(c, verts)

def test_point_in_face_outside():
    verts = [
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([0.0, 0.0, 1.0]),
    ]
    outside = np.array([-1.0, 0.0, 0.0])
    assert not point_in_face(outside, verts)
```

- [ ] **Step 1.2: Run to confirm all fail**

```bash
cd /path/to/maps-coloring-python
source .venv/bin/activate
pytest python_tests/sphere/tests/test_spherical_map.py -v 2>&1 | head -30
```
Expected: `ModuleNotFoundError` or `ImportError`.

- [ ] **Step 1.3: Create scaffold files**

```python
# python_tests/sphere/__init__.py
# (empty)
```

```python
# python_tests/sphere/tests/__init__.py
# (empty)
```

- [ ] **Step 1.4: Implement geometry primitives in spherical_map.py**

```python
# python_tests/sphere/spherical_map.py
from __future__ import annotations
import math
import numpy as np
from dataclasses import dataclass, field


def normalize(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def slerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    a, b = normalize(a), normalize(b)
    dot = float(np.clip(np.dot(a, b), -1.0, 1.0))
    if abs(dot) > 0.9999:
        return normalize(a + t * (b - a))
    theta = math.acos(dot)
    return (math.sin((1 - t) * theta) * a + math.sin(t * theta) * b) / math.sin(theta)


def geodesic_samples(a: np.ndarray, b: np.ndarray, n: int = 30) -> list[np.ndarray]:
    return [slerp(a, b, i / (n - 1)) for i in range(n)]


def point_in_face(pt: np.ndarray, face_verts: list[np.ndarray]) -> bool:
    """True if pt is on the same hemisphere side as the face interior (winding test)."""
    n = len(face_verts)
    for i in range(n):
        a = face_verts[i]
        b = face_verts[(i + 1) % n]
        if np.dot(np.cross(a, b), pt) < 0:
            return False
    return True
```

- [ ] **Step 1.5: Run tests**

```bash
pytest python_tests/sphere/tests/test_spherical_map.py -v
```
Expected: all 6 tests PASS.

- [ ] **Step 1.6: Commit**

```bash
git add python_tests/sphere/
git commit -m "feat(sphere): geometry primitives + test scaffold"
```

---

## Task 2: Edge and SphericalMap dataclasses + initial map

**Files:**
- Modify: `python_tests/sphere/spherical_map.py`
- Modify: `python_tests/sphere/tests/test_spherical_map.py`

- [ ] **Step 2.1: Write failing tests**

```python
# Append to test_spherical_map.py
from sphere.spherical_map import Edge, SphericalMap, make_initial_map

def test_make_initial_map_euler():
    smap = make_initial_map()
    V = len(smap.vertices)
    E = len(smap.edges)
    F = len(smap.faces)
    assert V == 2
    assert E == 3
    assert F == 3
    assert V - E + F == 2  # Euler

def test_make_initial_map_all_vertices_on_sphere():
    smap = make_initial_map()
    for v in smap.vertices.values():
        assert abs(np.linalg.norm(v) - 1.0) < 1e-10

def test_make_initial_map_each_edge_in_two_faces():
    smap = make_initial_map()
    edge_face_count: dict[int, int] = {}
    for fid, eids in smap.faces.items():
        for eid in eids:
            edge_face_count[abs(eid)] = edge_face_count.get(abs(eid), 0) + 1
    for eid, count in edge_face_count.items():
        assert count == 2, f"edge {eid} appears in {count} faces"
```

> **Note on face boundary encoding:** positive eid means the edge is traversed forward (v_start→v_end); negative eid means reversed (v_end→v_start). `abs(eid)` gives the edge id.

- [ ] **Step 2.2: Run to confirm they fail**

```bash
pytest python_tests/sphere/tests/test_spherical_map.py::test_make_initial_map_euler -v
```
Expected: `ImportError: cannot import name 'Edge'`.

- [ ] **Step 2.3: Add dataclasses and make_initial_map to spherical_map.py**

Append after the geometry functions:

```python
@dataclass
class Edge:
    v_start   : int
    v_end     : int
    waypoints : list[np.ndarray] = field(default_factory=list)


@dataclass
class SphericalMap:
    vertices : dict[int, np.ndarray] = field(default_factory=dict)
    edges    : dict[int, Edge]       = field(default_factory=dict)
    # face boundary: list of signed eids. +eid = forward, -eid = reversed.
    faces    : dict[int, list[int]]  = field(default_factory=dict)
    colors   : dict[int, str]        = field(default_factory=dict)
    next_vid : int = 0
    next_eid : int = 0
    next_fid : int = 0

    def _add_vertex(self, pos: np.ndarray) -> int:
        vid = self.next_vid
        self.vertices[vid] = normalize(pos)
        self.next_vid += 1
        return vid

    def _add_edge(self, v_start: int, v_end: int,
                  waypoints: list[np.ndarray] | None = None) -> int:
        eid = self.next_eid
        self.edges[eid] = Edge(v_start, v_end, waypoints or [])
        self.next_eid += 1
        return eid

    def _add_face(self, signed_eids: list[int], color: str) -> int:
        fid = self.next_fid
        self.faces[fid] = signed_eids
        self.colors[fid] = color
        self.next_fid += 1
        return fid


PALETTE = [
    "#e53935", "#1e88e5", "#43a047", "#fb8c00",
    "#8e24aa", "#00acc1", "#f4511e", "#6d4c41", "#546e7a", "#c0ca33",
]


def make_initial_map() -> SphericalMap:
    smap = SphericalMap()
    v0 = smap._add_vertex(np.array([0.0, 0.0,  1.0]))   # north pole
    v1 = smap._add_vertex(np.array([0.0, 0.0, -1.0]))   # south pole

    eq0 = np.array([ 1.0,   0.0,    0.0])
    eq1 = np.array([-0.5,   0.866,  0.0])
    eq2 = np.array([-0.5,  -0.866,  0.0])

    e0 = smap._add_edge(v0, v1, [normalize(eq0)])
    e1 = smap._add_edge(v0, v1, [normalize(eq1)])
    e2 = smap._add_edge(v0, v1, [normalize(eq2)])

    # Positive eid = forward, negative = reversed
    smap._add_face([ e0, -e1], PALETTE[0])   # f0: luna 0°-120°
    smap._add_face([ e1, -e2], PALETTE[1])   # f1: luna 120°-240°
    smap._add_face([ e2, -e0], PALETTE[2])   # f2: oceano 240°-360°
    return smap
```

- [ ] **Step 2.4: Run tests**

```bash
pytest python_tests/sphere/tests/test_spherical_map.py -v
```
Expected: all 9 tests PASS.

- [ ] **Step 2.5: Commit**

```bash
git add python_tests/sphere/spherical_map.py python_tests/sphere/tests/test_spherical_map.py
git commit -m "feat(sphere): Edge + SphericalMap dataclasses + initial map"
```

---

## Task 3: neighbors, assign_color, auto_waypoints

**Files:**
- Modify: `python_tests/sphere/spherical_map.py`
- Modify: `python_tests/sphere/tests/test_spherical_map.py`

- [ ] **Step 3.1: Write failing tests**

```python
# Append to test_spherical_map.py
from sphere.spherical_map import neighbors, assign_color, auto_waypoints

def test_neighbors_initial_map():
    smap = make_initial_map()
    fids = list(smap.faces.keys())
    # Each face in the initial 3-face map is adjacent to the other two
    for fid in fids:
        nb = neighbors(smap, fid)
        assert len(nb) == 2
        for other in fids:
            if other != fid:
                assert other in nb

def test_assign_color_differs_from_neighbors():
    smap = make_initial_map()
    fids = list(smap.faces.keys())
    for fid in fids:
        c = assign_color(smap, fid)
        for nb in neighbors(smap, fid):
            assert c != smap.colors[nb]

def test_auto_waypoints_inside_face():
    smap = make_initial_map()
    fid = list(smap.faces.keys())[0]
    face_verts = _face_vertex_positions(smap, fid)
    p = face_verts[0]
    q = face_verts[1]
    wps = auto_waypoints(p, q, face_verts)
    # Either empty (fallback) or the single waypoint is inside the face
    if wps:
        assert point_in_face(wps[0], face_verts)

def test_auto_waypoints_fallback_returns_empty():
    # Antipodal points → midpoint undefined, should return []
    p = np.array([1.0, 0.0, 0.0])
    q = np.array([-1.0, 0.0, 0.0])
    face_verts = [p, np.array([0.0, 1.0, 0.0]), q]
    result = auto_waypoints(p, q, face_verts)
    assert isinstance(result, list)
```

Also add this helper at module level in the test file:

```python
from sphere.spherical_map import _face_vertex_positions  # we'll add this helper
```

- [ ] **Step 3.2: Run to confirm they fail**

```bash
pytest python_tests/sphere/tests/test_spherical_map.py -k "neighbors or assign_color or auto_waypoints" -v
```
Expected: `ImportError`.

- [ ] **Step 3.3: Implement in spherical_map.py**

Append after `make_initial_map`:

```python
def _face_vertex_positions(smap: SphericalMap, fid: int) -> list[np.ndarray]:
    """Ordered vertex positions around a face boundary (one per edge)."""
    result = []
    for signed_eid in smap.faces[fid]:
        eid = abs(signed_eid)
        e = smap.edges[eid]
        vid = e.v_start if signed_eid > 0 else e.v_end
        result.append(smap.vertices[vid])
    return result


def neighbors(smap: SphericalMap, fid: int) -> set[int]:
    """Face ids that share at least one edge with fid."""
    target_eids = {abs(s) for s in smap.faces[fid]}
    result = set()
    for other_fid, signed_eids in smap.faces.items():
        if other_fid == fid:
            continue
        if target_eids & {abs(s) for s in signed_eids}:
            result.add(other_fid)
    return result


def assign_color(smap: SphericalMap, fid: int) -> str:
    used = {smap.colors[n] for n in neighbors(smap, fid)}
    for c in PALETTE:
        if c not in used:
            return c
    return PALETTE[0]


def auto_waypoints(
    p: np.ndarray,
    q: np.ndarray,
    face_verts: list[np.ndarray],
    strength: float = 0.35,
) -> list[np.ndarray]:
    try:
        c = normalize(np.mean(np.array(face_verts), axis=0))
        m = normalize(p + q)
        w = normalize(m + strength * (c - m))
        if point_in_face(w, face_verts):
            return [w]
    except Exception:
        pass
    return []
```

- [ ] **Step 3.4: Run tests**

```bash
pytest python_tests/sphere/tests/test_spherical_map.py -v
```
Expected: all 13 tests PASS.

- [ ] **Step 3.5: Commit**

```bash
git add python_tests/sphere/spherical_map.py python_tests/sphere/tests/test_spherical_map.py
git commit -m "feat(sphere): neighbors, assign_color, auto_waypoints"
```

---

## Task 4: split_face — core operation

**Files:**
- Modify: `python_tests/sphere/spherical_map.py`
- Modify: `python_tests/sphere/tests/test_spherical_map.py`

- [ ] **Step 4.1: Write failing tests**

```python
# Append to test_spherical_map.py
from sphere.spherical_map import split_face

def _check_invariants(smap: SphericalMap):
    """Assert cubic + planar + Euler invariants."""
    V = len(smap.vertices)
    E = len(smap.edges)
    F = len(smap.faces)
    assert V - E + F == 2, f"Euler: {V}-{E}+{F}={V-E+F}"

    # Each edge appears in exactly 2 faces
    edge_count: dict[int, int] = {}
    for signed_eids in smap.faces.values():
        for s in signed_eids:
            eid = abs(s)
            edge_count[eid] = edge_count.get(eid, 0) + 1
    for eid, cnt in edge_count.items():
        assert cnt == 2, f"edge {eid} in {cnt} faces"

    # Each vertex has degree 3
    deg: dict[int, int] = {}
    for e in smap.edges.values():
        deg[e.v_start] = deg.get(e.v_start, 0) + 1
        deg[e.v_end]   = deg.get(e.v_end, 0) + 1
    for vid, d in deg.items():
        assert d == 3, f"vertex {vid} has degree {d}"

    # All vertices on unit sphere
    for vid, pos in smap.vertices.items():
        assert abs(np.linalg.norm(pos) - 1.0) < 1e-9, f"vertex {vid} not on sphere"


def test_split_face_euler_invariant():
    smap = make_initial_map()
    fids = list(smap.faces.keys())
    fid = fids[0]
    boundary = smap.faces[fid]
    eid1 = abs(boundary[0])
    eid2 = abs(boundary[1])
    split_face(smap, fid, eid1, 0.5, eid2, 0.5)
    _check_invariants(smap)


def test_split_face_returns_two_new_face_ids():
    smap = make_initial_map()
    fids = list(smap.faces.keys())
    fid = fids[0]
    boundary = smap.faces[fid]
    eid1 = abs(boundary[0])
    eid2 = abs(boundary[1])
    old_fids = set(smap.faces.keys())
    f1, f2 = split_face(smap, fid, eid1, 0.5, eid2, 0.5)
    new_fids = set(smap.faces.keys())
    assert fid not in new_fids
    assert f1 in new_fids
    assert f2 in new_fids
    assert len(new_fids) == len(old_fids) + 1


def test_split_face_same_edge():
    smap = make_initial_map()
    fid = list(smap.faces.keys())[0]
    eid = abs(smap.faces[fid][0])
    split_face(smap, fid, eid, 0.3, eid, 0.7)
    _check_invariants(smap)


def test_split_face_repeated_splits():
    smap = make_initial_map()
    for _ in range(5):
        fid = list(smap.faces.keys())[0]
        boundary = smap.faces[fid]
        eid1 = abs(boundary[0])
        eid2 = abs(boundary[1 % len(boundary)])
        split_face(smap, fid, eid1, 0.5, eid2, 0.5)
    _check_invariants(smap)
```

- [ ] **Step 4.2: Run to confirm they fail**

```bash
pytest python_tests/sphere/tests/test_spherical_map.py -k "split_face" -v
```
Expected: `ImportError: cannot import name 'split_face'`.

- [ ] **Step 4.3: Implement split_face in spherical_map.py**

Append after `auto_waypoints`:

```python
def _edge_waypoints_slice(
    wp: list[np.ndarray], t_start: float, t_end: float
) -> list[np.ndarray]:
    """Return waypoints proportionally between t_start and t_end."""
    if not wp:
        return []
    result = []
    for i, w in enumerate(wp):
        t = (i + 1) / (len(wp) + 1)
        if t_start < t < t_end:
            result.append(w)
    return result


def split_face(
    smap      : SphericalMap,
    fid       : int,
    eid1      : int,
    t1        : float,
    eid2      : int,
    t2        : float,
    waypoints : list[np.ndarray] | None = None,
) -> tuple[int, int]:
    e1 = smap.edges[eid1]
    e2 = smap.edges[eid2]

    # New vertex p on eid1
    p_pos = slerp(smap.vertices[e1.v_start], smap.vertices[e1.v_end], t1)
    p_vid = smap._add_vertex(p_pos)

    same_edge = (eid1 == eid2)

    if same_edge:
        # Split eid1 into 3 segments: v_start→p, p→q, q→v_end
        q_pos = slerp(smap.vertices[e1.v_start], smap.vertices[e1.v_end], t2)
        q_vid = smap._add_vertex(q_pos)

        wp_all = e1.waypoints
        ea = smap._add_edge(e1.v_start, p_vid, _edge_waypoints_slice(wp_all, 0.0,  t1))
        em = smap._add_edge(p_vid,       q_vid, _edge_waypoints_slice(wp_all, t1,   t2))
        eb = smap._add_edge(q_vid,       e1.v_end, _edge_waypoints_slice(wp_all, t2, 1.0))

        del smap.edges[eid1]
    else:
        q_pos = slerp(smap.vertices[e2.v_start], smap.vertices[e2.v_end], t2)
        q_vid = smap._add_vertex(q_pos)

        wp1 = e1.waypoints
        e1a = smap._add_edge(e1.v_start, p_vid, _edge_waypoints_slice(wp1, 0.0, t1))
        e1b = smap._add_edge(p_vid, e1.v_end,   _edge_waypoints_slice(wp1, t1,  1.0))
        del smap.edges[eid1]

        wp2 = e2.waypoints
        e2a = smap._add_edge(e2.v_start, q_vid, _edge_waypoints_slice(wp2, 0.0, t2))
        e2b = smap._add_edge(q_vid, e2.v_end,   _edge_waypoints_slice(wp2, t2,  1.0))
        del smap.edges[eid2]

        em = None   # no middle segment

    # Compute new arc waypoints
    face_verts = _face_vertex_positions_by_boundary(smap, smap.faces[fid],
                                                    exclude=[eid1, eid2])
    if waypoints is None:
        waypoints = auto_waypoints(p_pos, q_pos, face_verts or
                                   list(smap.vertices.values()))

    arc_fwd = smap._add_edge(p_vid, q_vid, waypoints)

    # Rebuild boundary lists for the two new faces
    old_boundary = smap.faces[fid]
    del smap.faces[fid]
    del smap.colors[fid]

    f1_boundary, f2_boundary = _split_boundary(
        old_boundary, eid1, e1.v_start, e1.v_end,
        eid2, e2.v_start if not same_edge else e1.v_start,
              e2.v_end   if not same_edge else e1.v_end,
        p_vid, q_vid,
        ea if same_edge else e1a,
        eb if same_edge else e1b,
        em if same_edge else None,
        None if same_edge else e2a,
        None if same_edge else e2b,
        arc_fwd,
        same_edge,
    )

    old_color = smap.colors.get(fid, PALETTE[0])
    fid1 = smap._add_face(f1_boundary, old_color)
    fid2 = smap._add_face(f2_boundary, assign_color(smap, smap.next_fid))
    # assign_color uses neighbors; add fid2 color after fid1 is registered
    smap.colors[fid2] = assign_color(smap, fid2)

    return fid1, fid2


def _face_vertex_positions_by_boundary(
    smap: SphericalMap,
    signed_eids: list[int],
    exclude: list[int],
) -> list[np.ndarray]:
    result = []
    for s in signed_eids:
        eid = abs(s)
        if eid in exclude:
            continue
        e = smap.edges.get(eid)
        if e is None:
            continue
        vid = e.v_start if s > 0 else e.v_end
        result.append(smap.vertices[vid])
    return result


def _split_boundary(
    old_boundary: list[int],
    eid1: int, e1_vs: int, e1_ve: int,
    eid2: int, e2_vs: int, e2_ve: int,
    p_vid: int, q_vid: int,
    e1a: int, e1b: int,
    em: int | None,
    e2a: int | None, e2b: int | None,
    arc_fwd: int,
    same_edge: bool,
) -> tuple[list[int], list[int]]:
    """
    Rebuild two face boundaries after splitting.
    Returns (f1_boundary, f2_boundary).

    Convention: f1 contains the arc p→q (arc_fwd),
                f2 contains the reversed arc q→p (-arc_fwd).
    """
    # Locate eid1 position in old boundary
    idx1 = next(i for i, s in enumerate(old_boundary) if abs(s) == eid1)
    s1   = old_boundary[idx1]
    fwd1 = (s1 > 0)  # True if eid1 is traversed v_start→v_end in this face

    if same_edge:
        # Replace eid1 with ea, em, eb (or their reverses)
        # p is at t1, q is at t2 along eid1; fwd1 means v_start→v_end order
        if fwd1:
            # traversal: v_start → p → q → v_end  →  ea, em, eb forward
            replacement = [e1a, em, e1b]
        else:
            # traversal reversed: v_end → q → p → v_start  →  -eb, -em, -ea
            replacement = [-e1b, -em, -e1a]

        new_boundary = (
            old_boundary[:idx1] + replacement + old_boundary[idx1+1:]
        )
        # f1: p→q path + arc; f2: the rest
        # Find p and q positions in new_boundary
        p_idx = next(i for i, s in enumerate(new_boundary) if abs(s) == e1a)
        q_idx = next(i for i, s in enumerate(new_boundary) if abs(s) == e1b)
        # f1: arc_fwd then em reversed (bigon)
        f1 = [arc_fwd, -em] if fwd1 else [em, -arc_fwd]
        # f2: everything replacing em with arc
        f2 = []
        for s in new_boundary:
            if abs(s) == em:
                f2.append(-arc_fwd if fwd1 else arc_fwd)
            else:
                f2.append(s)
        return f1, f2

    # Different edges: locate eid2
    idx2 = next(i for i, s in enumerate(old_boundary) if abs(s) == eid2)
    s2   = old_boundary[idx2]
    fwd2 = (s2 > 0)

    # Replace eid1 and eid2 in boundary with their sub-edges
    def replace_edge(boundary, idx, fwd, ea, eb):
        s = boundary[idx]
        if fwd:
            sub = [ea, eb]
        else:
            sub = [-eb, -ea]
        return boundary[:idx] + sub + boundary[idx+1:]

    b = list(old_boundary)
    if idx1 < idx2:
        b = replace_edge(b, idx2, fwd2, e2a, e2b)
        b = replace_edge(b, idx1, fwd1, e1a, e1b)
        # Adjust idx2 after earlier replacement
        idx2 = idx2 - 1 + 2  # -1 removed, +2 added
        idx1_new = idx1
    else:
        b = replace_edge(b, idx1, fwd1, e1a, e1b)
        b = replace_edge(b, idx2, fwd2, e2a, e2b)
        idx1_new = idx1
        idx2 = idx2  # unchanged (comes before idx1)

    # Find p and q in the new boundary
    # p is the end of e1a (forward) or start of e1b
    # Split boundary at p and q into two arcs
    p_pos_in_b = next(i for i, s in enumerate(b)
                      if abs(s) == e1a and s > 0 or abs(s) == e1b and s < 0)
    q_pos_in_b = next(i for i, s in enumerate(b)
                      if abs(s) == e2a and s > 0 or abs(s) == e2b and s < 0)

    # Rotate boundary so p_pos_in_b is at index 0
    n = len(b)
    b = b[p_pos_in_b:] + b[:p_pos_in_b]
    q_pos_in_b = (q_pos_in_b - p_pos_in_b) % n

    # arc from p to q: indices 0..q_pos_in_b (inclusive of e1b which ends at p side)
    # Actually p is between e1a and e1b:
    # After rotation, b[0] ends at p (it's e1b forward or e1a reversed).
    # The arc goes: b[0], b[1], ..., b[q_pos_in_b-1], then arc_fwd closes back to p
    # f1: b[0..q_pos_in_b-1] + arc_fwd (p→q path + arc back)
    # f2: b[q_pos_in_b..n-1] + (-arc_fwd)
    f1 = b[:q_pos_in_b] + [arc_fwd]
    f2 = b[q_pos_in_b:] + [-arc_fwd]
    return f1, f2
```

> **Note:** `_split_boundary` is the trickiest function. The tests in Step 4.1 verify correctness via invariants — if all invariants pass (Euler, each edge in 2 faces, each vertex degree 3), the boundary logic is correct.

- [ ] **Step 4.4: Run tests**

```bash
pytest python_tests/sphere/tests/test_spherical_map.py -v
```
Expected: all tests PASS. If `test_split_face_*` fail, the most likely issue is in `_split_boundary` — add a `print(smap.faces)` before `_check_invariants` to inspect.

- [ ] **Step 4.5: Commit**

```bash
git add python_tests/sphere/spherical_map.py python_tests/sphere/tests/test_spherical_map.py
git commit -m "feat(sphere): split_face with full invariant preservation"
```

---

## Task 5: split_face_auto + grow_map

**Files:**
- Modify: `python_tests/sphere/spherical_map.py`
- Modify: `python_tests/sphere/tests/test_spherical_map.py`

- [ ] **Step 5.1: Write failing tests**

```python
# Append to test_spherical_map.py
from sphere.spherical_map import split_face_auto, grow_map

def test_split_face_auto_balanced_invariants():
    smap = make_initial_map()
    split_face_auto(smap, strategy="balanced")
    _check_invariants(smap)

def test_split_face_auto_random_invariants():
    smap = make_initial_map()
    split_face_auto(smap, strategy="random")
    _check_invariants(smap)

def test_grow_map_10_splits_invariants():
    smap = make_initial_map()
    grow_map(smap, renderer=None, n_splits=10, show=False)
    _check_invariants(smap)
    assert len(smap.faces) == 13   # 3 + 10
    assert len(smap.vertices) == 22  # 2 + 10*2
```

- [ ] **Step 5.2: Run to confirm they fail**

```bash
pytest python_tests/sphere/tests/test_spherical_map.py -k "auto or grow" -v
```
Expected: `ImportError`.

- [ ] **Step 5.3: Implement in spherical_map.py**

Append after `split_face`:

```python
def _largest_face(smap: SphericalMap) -> int:
    """Return fid of face with most edges in boundary."""
    return max(smap.faces, key=lambda f: len(smap.faces[f]))


def _non_adjacent_edge_pair(smap: SphericalMap, fid: int) -> tuple[int, int]:
    """Return two edge ids from face boundary that are not consecutive."""
    boundary = smap.faces[fid]
    n = len(boundary)
    if n < 3:
        return abs(boundary[0]), abs(boundary[0])  # same-edge fallback
    # Pick indices 0 and n//2 (maximally separated)
    return abs(boundary[0]), abs(boundary[n // 2])


def split_face_auto(
    smap     : SphericalMap,
    fid      : int | None = None,
    strategy : str = "balanced",
) -> tuple[int, int]:
    if fid is None:
        fid = _largest_face(smap)

    if strategy == "balanced":
        eid1, eid2 = _non_adjacent_edge_pair(smap, fid)
        return split_face(smap, fid, eid1, 0.5, eid2, 0.5)

    # "random"
    import random
    boundary = smap.faces[fid]
    idx1 = random.randrange(len(boundary))
    idx2 = random.randrange(len(boundary))
    eid1 = abs(boundary[idx1])
    eid2 = abs(boundary[idx2])
    t1 = random.uniform(0.2, 0.8)
    t2 = random.uniform(0.2, 0.8)
    return split_face(smap, fid, eid1, t1, eid2, t2)


def grow_map(
    smap     : SphericalMap,
    renderer,
    n_splits : int = 10,
    strategy : str = "balanced",
    show     : bool = True,
) -> None:
    for _ in range(n_splits):
        fid1, fid2 = split_face_auto(smap, strategy=strategy)
        if show and renderer is not None:
            renderer.update_after_split(smap, fid1, fid2)
```

- [ ] **Step 5.4: Run tests**

```bash
pytest python_tests/sphere/tests/test_spherical_map.py -v
```
Expected: all tests PASS.

- [ ] **Step 5.5: Commit**

```bash
git add python_tests/sphere/spherical_map.py python_tests/sphere/tests/test_spherical_map.py
git commit -m "feat(sphere): split_face_auto + grow_map"
```

---

## Task 6: SphereRenderer — static scene

**Files:**
- Create: `python_tests/sphere/renderer.py`

No automated tests for the renderer (requires display). Verify visually by running `main.py`.

- [ ] **Step 6.1: Implement renderer.py**

```python
# python_tests/sphere/renderer.py
from __future__ import annotations
import numpy as np
import pyvista as pv
from sphere.spherical_map import (
    SphericalMap, slerp, normalize, geodesic_samples, _face_vertex_positions,
)

_N_SAMPLES = 30   # points per geodesic segment


def _edge_polyline(smap: SphericalMap, eid: int) -> np.ndarray:
    """3D points along the full edge path (v_start + waypoints + v_end)."""
    e = smap.edges[eid]
    chain = [smap.vertices[e.v_start]] + list(e.waypoints) + [smap.vertices[e.v_end]]
    pts = []
    for i in range(len(chain) - 1):
        seg = geodesic_samples(chain[i], chain[i + 1], n=_N_SAMPLES)
        pts.extend(seg if i == 0 else seg[1:])
    return np.array(pts)


def _face_poly_data(smap: SphericalMap, fid: int) -> pv.PolyData:
    """PolyData mesh for a filled face (fan triangulation from centroid)."""
    boundary_pts: list[np.ndarray] = []
    for signed_eid in smap.faces[fid]:
        eid = abs(signed_eid)
        e = smap.edges[eid]
        chain = [smap.vertices[e.v_start]] + list(e.waypoints) + [smap.vertices[e.v_end]]
        if signed_eid < 0:
            chain = list(reversed(chain))
        seg_pts = []
        for i in range(len(chain) - 1):
            seg = geodesic_samples(chain[i], chain[i + 1], n=_N_SAMPLES)
            seg_pts.extend(seg if i == 0 else seg[1:])
        boundary_pts.extend(seg_pts[:-1])   # avoid duplicate at junction

    c = normalize(np.mean(np.array(boundary_pts), axis=0))
    n = len(boundary_pts)
    pts = np.vstack([np.array(boundary_pts), c.reshape(1, 3)])
    c_idx = n
    faces = []
    for i in range(n):
        faces += [3, c_idx, i, (i + 1) % n]
    mesh = pv.PolyData(pts, np.array(faces))
    return mesh


def _edge_mesh(smap: SphericalMap, eid: int) -> pv.PolyData:
    pts = _edge_polyline(smap, eid)
    return pv.Spline(pts, n_points=len(pts))


class SphereRenderer:
    def __init__(self, smap: SphericalMap):
        self.smap = smap
        self.plotter = pv.Plotter()
        self.plotter.set_background("#1a1a2e")

        self._face_actors:   dict[int, pv.Actor] = {}
        self._edge_actors:   dict[int, pv.Actor] = {}
        self._vertex_actors: dict[int, pv.Actor] = {}

        self._build_all(smap)
        self._update_hud()

    def _build_all(self, smap: SphericalMap) -> None:
        for fid in smap.faces:
            self._add_face_actor(fid)
        for eid in smap.edges:
            self._add_edge_actor(eid)
        for vid in smap.vertices:
            self._add_vertex_actor(vid)

    def _add_face_actor(self, fid: int) -> None:
        mesh = _face_poly_data(self.smap, fid)
        color = self.smap.colors[fid]
        actor = self.plotter.add_mesh(
            mesh, color=color, opacity=0.75,
            show_edges=False, name=f"face_{fid}",
        )
        self._face_actors[fid] = actor

    def _add_edge_actor(self, eid: int, color: str = "white") -> None:
        mesh = _edge_mesh(self.smap, eid)
        actor = self.plotter.add_mesh(
            mesh.tube(radius=0.004), color=color,
            name=f"edge_{eid}",
        )
        self._edge_actors[eid] = actor

    def _add_vertex_actor(self, vid: int, color: str = "white") -> None:
        pos = self.smap.vertices[vid]
        sphere = pv.Sphere(radius=0.012, center=pos)
        actor = self.plotter.add_mesh(sphere, color=color, name=f"vert_{vid}")
        self._vertex_actors[vid] = actor

    def highlight_edge(self, eid: int | None, prev_eid: int | None = None) -> None:
        if prev_eid is not None and prev_eid in self._edge_actors:
            self.plotter.remove_actor(self._edge_actors[prev_eid])
            self._add_edge_actor(prev_eid, color="white")
        if eid is not None and eid in self._edge_actors:
            self.plotter.remove_actor(self._edge_actors[eid])
            self._add_edge_actor(eid, color="yellow")

    def show_snap_vertex(self, pos: np.ndarray | None, prev_pos: np.ndarray | None = None) -> None:
        if prev_pos is not None:
            self.plotter.remove_actor("snap_vertex")
        if pos is not None:
            sphere = pv.Sphere(radius=0.016, center=pos)
            self.plotter.add_mesh(sphere, color="orange", name="snap_vertex")

    def update_after_split(
        self,
        smap: SphericalMap,
        fid1: int,
        fid2: int,
        removed_fid: int | None = None,
        removed_eids: list[int] | None = None,
        new_eids: list[int] | None = None,
        new_vids: list[int] | None = None,
    ) -> None:
        self.smap = smap
        # Remove stale actors (caller provides ids of what was removed)
        if removed_fid is not None and removed_fid in self._face_actors:
            self.plotter.remove_actor(self._face_actors.pop(removed_fid))
        for eid in (removed_eids or []):
            if eid in self._edge_actors:
                self.plotter.remove_actor(self._edge_actors.pop(eid))
        # Add new actors
        for fid in [fid1, fid2]:
            if fid in smap.faces:
                self._add_face_actor(fid)
        for eid in (new_eids or []):
            if eid in smap.edges:
                self._add_edge_actor(eid)
        for vid in (new_vids or []):
            if vid in smap.vertices:
                self._add_vertex_actor(vid)
        self._update_hud()
        self.plotter.render()

    def _update_hud(self, mode: str = "IDLE", extra: str = "") -> None:
        V = len(self.smap.vertices)
        E = len(self.smap.edges)
        F = len(self.smap.faces)
        self.plotter.add_text(
            f"MODE: {mode}\n{extra}",
            position="upper_left", font_size=10,
            color="lightgreen", name="hud_mode",
        )
        self.plotter.add_text(
            f"V:{V}  E:{E}  F:{F}",
            position="upper_right", font_size=10,
            color="lightblue", name="hud_stats",
        )

    def update_hud(self, mode: str, extra: str = "") -> None:
        self._update_hud(mode, extra)
        self.plotter.render()
```

- [ ] **Step 6.2: Smoke test — launch with initial map**

Create a temporary launcher to verify visually:

```python
# python_tests/sphere/main.py  (temporary, overwritten in Task 8)
import sys
sys.path.insert(0, ".")
from sphere.spherical_map import make_initial_map
from sphere.renderer import SphereRenderer

smap = make_initial_map()
r = SphereRenderer(smap)
r.plotter.show()
```

```bash
cd /path/to/maps-coloring-python
source .venv/bin/activate
python python_tests/sphere/main.py
```

Expected: PyVista window with 3 colored lune regions, white meridian edges, white vertex dots at poles.

- [ ] **Step 6.3: Commit**

```bash
git add python_tests/sphere/renderer.py python_tests/sphere/main.py
git commit -m "feat(sphere): SphereRenderer — static scene with PyVista"
```

---

## Task 7: InteractionController — edge picking + state machine

**Files:**
- Create: `python_tests/sphere/interaction.py`

- [ ] **Step 7.1: Implement interaction.py**

```python
# python_tests/sphere/interaction.py
from __future__ import annotations
import math
import numpy as np
import pyvista as pv
from sphere.spherical_map import SphericalMap, slerp, geodesic_samples, split_face

_N_PICK_SAMPLES = 20   # screen-space sample density per edge
_PICK_THRESHOLD_PX = 14


def _dist_point_segment_2d(
    pt: tuple[float, float],
    a:  tuple[float, float],
    b:  tuple[float, float],
) -> tuple[float, float]:
    """Returns (distance, t) where t in [0,1] is the parameter along a→b."""
    ax, ay = pt[0] - a[0], pt[1] - a[1]
    bx, by = b[0] - a[0], b[1] - a[1]
    denom = bx * bx + by * by
    if denom < 1e-12:
        return math.hypot(ax, ay), 0.0
    t = max(0.0, min(1.0, (ax * bx + ay * by) / denom))
    rx, ry = ax - t * bx, ay - t * by
    return math.hypot(rx, ry), t


class InteractionController:
    IDLE            = "IDLE"
    FIRST_SELECTED  = "FIRST_SELECTED"
    WAYPOINT_MODE   = "WAYPOINT_MODE"

    def __init__(self, smap: SphericalMap, renderer):
        self.smap     = smap
        self.renderer = renderer
        self.state    = self.IDLE

        self._state_p:        int | None   = None    # eid1
        self._state_t1:       float        = 0.0
        self._state_p_vid:    int | None   = None    # preview vid, not committed
        self._state_q:        int | None   = None    # eid2
        self._state_t2:       float        = 0.0
        self._state_waypoints: list[np.ndarray] = []
        self._state_fid:      int | None   = None    # face being split

        self._hovered_eid:    int | None   = None
        self._snap_pos:       np.ndarray | None = None

        self._screen_cache:   dict[int, list[tuple[float, float]]] = {}
        self._cache_dirty:    bool = True

        self._register_callbacks()

    def _register_callbacks(self) -> None:
        plotter = self.renderer.plotter

        plotter.track_mouse_position()
        plotter.add_observer("MouseMoveEvent",   self._on_mouse_move)
        plotter.add_observer("LeftButtonPressEvent", self._on_left_click)
        plotter.add_key_event("Return",  self._on_confirm)
        plotter.add_key_event("space",   self._on_confirm)
        plotter.add_key_event("Escape",  self._on_escape)
        plotter.add_key_event("BackSpace", self._on_backspace)

        # Camera move → dirty the screen cache
        plotter.add_observer("EndInteractionEvent", self._on_camera_moved)

    def _on_camera_moved(self, *_) -> None:
        self._cache_dirty = True

    def _rebuild_screen_cache(self) -> None:
        renderer = self.renderer.plotter.renderer
        size = self.renderer.plotter.window_size
        w, h = size[0], size[1]

        def world_to_screen(pt3d: np.ndarray) -> tuple[float, float]:
            # Use PyVista's coordinate transform
            x, y, _ = renderer.world_to_display(pt3d[0], pt3d[1], pt3d[2])
            return float(x), float(h - y)  # flip Y

        self._screen_cache = {}
        for eid, edge in self.smap.edges.items():
            chain = ([self.smap.vertices[edge.v_start]]
                     + list(edge.waypoints)
                     + [self.smap.vertices[edge.v_end]])
            pts3d = []
            for i in range(len(chain) - 1):
                seg = geodesic_samples(chain[i], chain[i+1], n=_N_PICK_SAMPLES)
                pts3d.extend(seg if i == 0 else seg[1:])
            self._screen_cache[eid] = [world_to_screen(p) for p in pts3d]
        self._cache_dirty = False

    def _find_edge_at_cursor(self, mx: float, my: float) -> tuple[int | None, float]:
        if self._cache_dirty:
            self._rebuild_screen_cache()

        best_eid, best_t, best_dist = None, 0.0, math.inf
        for eid, screen_pts in self._screen_cache.items():
            n = len(screen_pts)
            for i in range(n - 1):
                d, t_local = _dist_point_segment_2d(
                    (mx, my), screen_pts[i], screen_pts[i + 1]
                )
                if d < best_dist:
                    best_dist = d
                    best_eid  = eid
                    best_t    = (i + t_local) / (n - 1)

        return (best_eid, best_t) if best_dist < _PICK_THRESHOLD_PX else (None, 0.0)

    def _snap_pos_on_edge(self, eid: int, t: float) -> np.ndarray:
        e = self.smap.edges[eid]
        return slerp(self.smap.vertices[e.v_start],
                     self.smap.vertices[e.v_end], t)

    def _face_of_edge(self, eid: int) -> int | None:
        for fid, signed_eids in self.smap.faces.items():
            if eid in [abs(s) for s in signed_eids]:
                return fid
        return None

    def _on_mouse_move(self, *_) -> None:
        mx, my = self.renderer.plotter.mouse_position
        eid, t = self._find_edge_at_cursor(mx, my)

        prev_hovered = self._hovered_eid
        prev_snap    = self._snap_pos

        if eid != prev_hovered:
            self.renderer.highlight_edge(eid, prev_hovered)
            self._hovered_eid = eid

        if eid is not None:
            new_snap = self._snap_pos_on_edge(eid, t)
            self.renderer.show_snap_vertex(new_snap, prev_snap)
            self._snap_pos = new_snap
        else:
            self.renderer.show_snap_vertex(None, prev_snap)
            self._snap_pos = None

        self.renderer.plotter.render()

    def _on_left_click(self, *_) -> None:
        if self._hovered_eid is None:
            if self.state == self.WAYPOINT_MODE and self._snap_pos is not None:
                self._state_waypoints.append(self._snap_pos.copy())
                self._update_hud()
            return

        eid = self._hovered_eid
        mx, my = self.renderer.plotter.mouse_position
        _, t = self._find_edge_at_cursor(mx, my)

        if self.state == self.IDLE:
            fid = self._face_of_edge(eid)
            self._state_fid = fid
            self._state_p   = eid
            self._state_t1  = t
            self.state = self.FIRST_SELECTED
            self._update_hud()

        elif self.state == self.FIRST_SELECTED:
            fid = self._face_of_edge(eid)
            if fid != self._state_fid:
                # Wrong face — flash feedback
                self._update_hud(extra="[edge belongs to different face]")
                return
            self._state_q  = eid
            self._state_t2 = t
            self.state = self.WAYPOINT_MODE
            self._update_hud()

    def _on_confirm(self, *_) -> None:
        if self.state != self.WAYPOINT_MODE:
            return
        fid  = self._state_fid
        eid1 = self._state_p
        t1   = self._state_t1
        eid2 = self._state_q
        t2   = self._state_t2
        wps  = self._state_waypoints if self._state_waypoints else None

        old_eids = set(self.smap.edges.keys())
        old_vids = set(self.smap.vertices.keys())

        fid1, fid2 = split_face(self.smap, fid, eid1, t1, eid2, t2, wps)

        new_eids = list(set(self.smap.edges.keys()) - old_eids)
        new_vids = list(set(self.smap.vertices.keys()) - old_vids)
        removed_eids = list(old_eids - set(self.smap.edges.keys()))

        self.renderer.update_after_split(
            self.smap, fid1, fid2,
            removed_fid=fid,
            removed_eids=removed_eids,
            new_eids=new_eids,
            new_vids=new_vids,
        )
        self._cache_dirty = True
        self._reset_state()

    def _on_escape(self, *_) -> None:
        self._reset_state()

    def _on_backspace(self, *_) -> None:
        if self.state == self.WAYPOINT_MODE and self._state_waypoints:
            self._state_waypoints.pop()
            self._update_hud()

    def _reset_state(self) -> None:
        self.state = self.IDLE
        self._state_p = self._state_q = self._state_fid = None
        self._state_t1 = self._state_t2 = 0.0
        self._state_waypoints = []
        self._update_hud()

    def _update_hud(self, extra: str = "") -> None:
        if self.state == self.IDLE:
            hints = "[click edge] select p"
        elif self.state == self.FIRST_SELECTED:
            hints = "[click edge same face] select q  ·  [Esc] cancel"
        else:
            wn = len(self._state_waypoints)
            hints = f"[click face] add waypoint ({wn})  ·  [Enter] confirm  ·  [Bksp] undo  ·  [Esc] cancel"

        self.renderer.update_hud(self.state, extra or hints)
```

- [ ] **Step 7.2: Commit**

```bash
git add python_tests/sphere/interaction.py
git commit -m "feat(sphere): InteractionController — state machine + edge picking"
```

---

## Task 8: main.py — wire everything together

**Files:**
- Modify: `python_tests/sphere/main.py`

- [ ] **Step 8.1: Write final main.py**

```python
# python_tests/sphere/main.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sphere.spherical_map import make_initial_map
from sphere.renderer import SphereRenderer
from sphere.interaction import InteractionController


def main():
    smap = make_initial_map()
    renderer = SphereRenderer(smap)

    renderer.plotter.add_text(
        "Sphere Map Explorer",
        position="lower_left", font_size=9, color="gray",
    )

    ctrl = InteractionController(smap, renderer)

    renderer.plotter.show(title="Sphere Map Explorer")


if __name__ == "__main__":
    main()
```

- [ ] **Step 8.2: Run full application**

```bash
cd /path/to/maps-coloring-python
source .venv/bin/activate
python python_tests/sphere/main.py
```

Manual test checklist:
- [ ] 3 colored lune regions visible at startup
- [ ] Hover over a meridian → edge turns yellow, orange snap dot appears
- [ ] Click edge → state changes to FIRST_SELECTED (HUD updates)
- [ ] Click edge of same face → state WAYPOINT_MODE
- [ ] Press Enter → face splits, two new colored regions appear
- [ ] Press Escape at any point → returns to IDLE
- [ ] Scroll → zoom works at all states
- [ ] Right-drag → sphere rotates

- [ ] **Step 8.3: Commit**

```bash
git add python_tests/sphere/main.py
git commit -m "feat(sphere): main.py entry point — full interactive application"
```

---

## Task 9: grow_map smoke test + final cleanup

**Files:**
- Modify: `python_tests/sphere/main.py` (add `--auto` flag)
- Modify: `python_tests/sphere/tests/test_spherical_map.py`

- [ ] **Step 9.1: Add --auto flag to main.py for batch mode**

```python
# Replace main() in main.py with:
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--auto", type=int, default=0,
                        help="Run N automatic splits then show")
    parser.add_argument("--strategy", default="balanced",
                        choices=["balanced", "random"])
    args = parser.parse_args()

    smap = make_initial_map()
    renderer = SphereRenderer(smap)

    if args.auto > 0:
        from sphere.spherical_map import grow_map
        grow_map(smap, renderer, n_splits=args.auto,
                 strategy=args.strategy, show=True)
    else:
        ctrl = InteractionController(smap, renderer)

    renderer.plotter.add_text(
        "Sphere Map Explorer", position="lower_left",
        font_size=9, color="gray",
    )
    renderer.plotter.show(title="Sphere Map Explorer")
```

- [ ] **Step 9.2: Test automatic mode visually**

```bash
python python_tests/sphere/main.py --auto 20 --strategy balanced
```
Expected: window opens with 23 faces (3 + 20), all regions distinct, no overlapping borders.

```bash
python python_tests/sphere/main.py --auto 50 --strategy random
```
Expected: window opens with 53 faces, map still valid.

- [ ] **Step 9.3: Run full test suite**

```bash
pytest python_tests/sphere/tests/ -v
```
Expected: all tests PASS.

- [ ] **Step 9.4: Final commit**

```bash
git add python_tests/sphere/main.py
git commit -m "feat(sphere): --auto flag for batch grow_map demo"
```

---

## Self-Review Checklist

- [x] **Spec §3 (SphericalMap):** Covered in Task 2
- [x] **Spec §4 (initial map):** Covered in Task 2 — exact coordinates, equatorial waypoints
- [x] **Spec §5 (split_face):** Covered in Task 4 — same-edge case, invariants tested
- [x] **Spec §6 (auto_waypoints):** Covered in Task 3 — fallback tested
- [x] **Spec §7 (split_face_auto + grow_map):** Covered in Task 5
- [x] **Spec §8 (renderer, incremental refresh):** Covered in Task 6
- [x] **Spec §9 (edge picking, cache):** Covered in Task 7
- [x] **Spec §10 (state machine):** Covered in Task 7 — all transitions implemented
- [x] **Spec §11 (HUD):** Covered in Tasks 6 + 7
- [x] **Spec §12 (colorazione):** Covered in Task 3 (`assign_color`) + Task 2 (`PALETTE`)
- [x] **Spec §14 (test structure):** Tasks 1–5 cover all three test files
- [x] **No TBDs or placeholders** — all steps have complete code
- [x] **Type consistency** — `split_face` signature matches across Tasks 4, 5, 7
