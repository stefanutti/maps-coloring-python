from __future__ import annotations
import math
import numpy as np
from dataclasses import dataclass, field


def normalize(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def slerp(a: np.ndarray, b: np.ndarray, t: float) -> np.ndarray:
    a, b = normalize(a), normalize(b)
    dot = float(np.clip(np.dot(a, b), -1.0, 1.0))
    if dot > 0.9999:
        # Nearly identical vectors: linear blend is safe
        return normalize(a + t * (b - a))
    if dot < -0.9999:
        # Nearly antipodal: pick an arbitrary perpendicular axis to rotate around
        perp = np.array([1.0, 0.0, 0.0])
        if abs(np.dot(a, perp)) > 0.9:
            perp = np.array([0.0, 1.0, 0.0])
        axis = normalize(np.cross(a, perp))
        theta = math.pi
        return (math.sin((1 - t) * theta) * a + math.sin(t * theta) * axis) / math.sin(theta)
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


@dataclass
class Edge:
    v_start   : int
    v_end     : int
    waypoints : list[np.ndarray] = field(default_factory=list)

    def __post_init__(self):
        if self.waypoints is None:
            self.waypoints = []


@dataclass
class SphericalMap:
    vertices : dict[int, np.ndarray] = field(default_factory=dict)
    edges    : dict[int, Edge]       = field(default_factory=dict)
    # face boundary: list of signed eids. +eid = forward, -eid = reversed.
    faces    : dict[int, list[int]]  = field(default_factory=dict)
    colors   : dict[int, str]        = field(default_factory=dict)
    next_vid : int = 0
    next_eid : int = 1   # eid 0 reserved: signed encoding requires -eid != +eid
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

    eq0 = np.array([ 1.0,   0.0,           0.0])
    eq1 = np.array([-0.5,   np.sqrt(3)/2,  0.0])
    eq2 = np.array([-0.5,  -np.sqrt(3)/2,  0.0])

    e0 = smap._add_edge(v0, v1, [normalize(eq0)])
    e1 = smap._add_edge(v0, v1, [normalize(eq1)])
    e2 = smap._add_edge(v0, v1, [normalize(eq2)])

    # Positive eid = forward, negative = reversed
    smap._add_face([ e0, -e1], PALETTE[0])   # f0: luna 0°-120°
    smap._add_face([ e1, -e2], PALETTE[1])   # f1: luna 120°-240°
    smap._add_face([ e2, -e0], PALETTE[2])   # f2: oceano 240°-360°
    return smap


def _face_vertex_positions(smap: SphericalMap, fid: int) -> list[np.ndarray]:
    """Ordered vertex positions around a face boundary (one per edge, the start vertex)."""
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
        if not np.any(np.isnan(w)) and point_in_face(w, face_verts):
            return [w]
    except Exception:
        pass
    return []


def _split_waypoints(waypoints: list[np.ndarray], t_split: float) -> tuple[list[np.ndarray], list[np.ndarray]]:
    """Split waypoints at parameter t_split. Returns (before, after) sublists."""
    before, after = [], []
    n = len(waypoints)
    for i, w in enumerate(waypoints):
        t = (i + 1) / (n + 1)
        if t < t_split:
            before.append(w)
        else:
            after.append(w)
    return before, after


def _rebuild_boundary_same_edge(
    old_boundary: list[int],
    eid1: int,
    e1a: int, e1m: int, e1b: int,
    arc_fwd: int,
    e1_v_start: int,
) -> tuple[list[int], list[int]]:
    """Rebuild boundaries when both new vertices are on the same edge.
    Returns (bigon_boundary, main_boundary).

    arc_fwd connects p->q (same direction as e1m).
    The bigon is bounded by e1m (p->q) and -arc_fwd (q->p): [e1m, -arc_fwd].
    The main face replaces eid1 with [e1a, arc_fwd, e1b] (using arc forward).

    If the face traversed eid1 backward (-eid1), the bigon becomes [-e1m, arc_fwd]
    and the main face replaces -eid1 with [-e1b, -arc_fwd, -e1a].
    """
    idx = next(i for i, s in enumerate(old_boundary) if abs(s) == eid1)
    s = old_boundary[idx]
    fwd = (s > 0)

    if fwd:
        # face traverses v_start->p->q->v_end (forward)
        # bigon: p->q via e1m, then q->p via -arc_fwd
        f1 = [e1m, -arc_fwd]
        # main face: replace eid1 with e1a, arc_fwd, e1b
        replacement = [e1a, arc_fwd, e1b]
    else:
        # face traverses v_end->q->p->v_start (reversed)
        # bigon: q->p via -e1m, then p->q via arc_fwd
        f1 = [-e1m, arc_fwd]
        # main face: replace -eid1 with -e1b, -arc_fwd, -e1a
        replacement = [-e1b, -arc_fwd, -e1a]

    f2 = old_boundary[:idx] + replacement + old_boundary[idx + 1:]
    return f1, f2


def _rebuild_boundary_diff_edges(
    old_boundary: list[int],
    eid1: int, e1a: int, e1b: int,
    eid2: int, e2a: int, e2b: int,
    arc_fwd: int,
) -> tuple[list[int], list[int]]:
    """Rebuild boundaries when the two new vertices are on different edges.

    The boundary contains eid1 and eid2 at some positions.
    We replace each with its two sub-edges, then cut at p and q.
    F1 gets the arc p->q (arc_fwd), F2 gets the arc q->p (-arc_fwd).
    """
    idx1 = next(i for i, s in enumerate(old_boundary) if abs(s) == eid1)
    idx2 = next(i for i, s in enumerate(old_boundary) if abs(s) == eid2)
    s1 = old_boundary[idx1]
    s2 = old_boundary[idx2]
    fwd1 = (s1 > 0)
    fwd2 = (s2 > 0)

    if fwd1:
        sub1_to_p = e1a    # e1.v_start -> p (forward)
        sub1_from_p = e1b  # p -> e1.v_end (forward)
    else:
        sub1_to_p = -e1b   # e1.v_end -> p (= e1b reversed)
        sub1_from_p = -e1a  # p -> e1.v_start (= e1a reversed)

    if fwd2:
        sub2_to_q = e2a
        sub2_from_q = e2b
    else:
        sub2_to_q = -e2b
        sub2_from_q = -e2a

    expanded = list(old_boundary)
    if idx1 < idx2:
        # Replace higher index first to avoid shifting lower index
        expanded = expanded[:idx2] + [sub2_to_q, sub2_from_q] + expanded[idx2 + 1:]
        expanded = expanded[:idx1] + [sub1_to_p, sub1_from_p] + expanded[idx1 + 1:]
        # p is at end of expanded[idx1] (sub1_to_p ends at p)
        # idx2 shifted by +1 because we inserted one extra element before it
        p_after_idx = idx1
        q_after_idx = idx2 + 1
    else:
        # Replace higher index (idx1) first
        expanded = expanded[:idx1] + [sub1_to_p, sub1_from_p] + expanded[idx1 + 1:]
        expanded = expanded[:idx2] + [sub2_to_q, sub2_from_q] + expanded[idx2 + 1:]
        p_after_idx = idx1 + 1   # shifted by the earlier idx2 insertion
        q_after_idx = idx2

    n = len(expanded)
    p_cut = p_after_idx + 1  # index of first element AFTER p
    q_cut = q_after_idx + 1  # index of first element AFTER q

    # Normalize so p_cut <= q_cut (rotate boundary so p comes first)
    if p_cut > q_cut:
        expanded = expanded[p_cut:] + expanded[:p_cut]
        q_cut = (q_cut - p_cut) % n
        p_cut = 0

    # F1: path from p to q (exclusive) + arc closing q->p (-arc_fwd)
    # F2: path from q to p (exclusive) + arc closing p->q (arc_fwd)
    f1 = expanded[p_cut:q_cut] + [-arc_fwd]
    f2 = expanded[q_cut:] + expanded[:p_cut] + [arc_fwd]
    return f1, f2


def _replace_edge_in_face(boundary: list[int], old_eid: int, replacement_fwd: list[int]) -> list[int]:
    """Replace old_eid (or -old_eid) in boundary with the given replacement sub-edges.
    If the original edge was traversed forward (+old_eid), uses replacement_fwd directly.
    If traversed backward (-old_eid), uses the reversal of replacement_fwd.
    """
    result = []
    for s in boundary:
        if abs(s) == old_eid:
            if s > 0:
                result.extend(replacement_fwd)
            else:
                result.extend(-e for e in reversed(replacement_fwd))
        else:
            result.append(s)
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
    """Split face fid by placing new vertex p on eid1 at t1 and q on eid2 at t2.
    Returns (fid1, fid2) — the two new face ids.
    If eid1==eid2, places both vertices on the same edge (creates a bigon face).
    """
    # Collect face vertex positions before any edge deletion
    face_verts = _face_vertex_positions(smap, fid)

    e1 = smap.edges[eid1]
    p_pos = slerp(smap.vertices[e1.v_start], smap.vertices[e1.v_end], t1)
    p_vid = smap._add_vertex(p_pos)

    same_edge = (eid1 == eid2)

    if same_edge:
        # Ensure t1 < t2 for clean splitting
        if t1 > t2:
            t1, t2 = t2, t1
            p_pos = slerp(smap.vertices[e1.v_start], smap.vertices[e1.v_end], t1)
            smap.vertices[p_vid] = normalize(p_pos)

        q_pos = slerp(smap.vertices[e1.v_start], smap.vertices[e1.v_end], t2)
        q_vid = smap._add_vertex(q_pos)

        wp_before, wp_rest = _split_waypoints(e1.waypoints, t1)
        wp_mid, wp_after   = _split_waypoints(wp_rest, (t2 - t1) / (1 - t1) if t1 < 1.0 else 0.5)

        e1a = smap._add_edge(e1.v_start, p_vid, wp_before)
        e1m = smap._add_edge(p_vid, q_vid, wp_mid)
        e1b = smap._add_edge(q_vid, e1.v_end, wp_after)
        # sub-edges in forward order: e1a, e1m, e1b
        e1_sub_fwd = [e1a, e1m, e1b]
        del smap.edges[eid1]
        e2_sub_fwd = None  # no separate eid2 in same_edge case
    else:
        e2 = smap.edges[eid2]
        q_pos = slerp(smap.vertices[e2.v_start], smap.vertices[e2.v_end], t2)
        q_vid = smap._add_vertex(q_pos)

        wp1_before, wp1_after = _split_waypoints(e1.waypoints, t1)
        e1a = smap._add_edge(e1.v_start, p_vid, wp1_before)
        e1b = smap._add_edge(p_vid, e1.v_end, wp1_after)
        e1_sub_fwd = [e1a, e1b]
        del smap.edges[eid1]

        wp2_before, wp2_after = _split_waypoints(e2.waypoints, t2)
        e2a = smap._add_edge(e2.v_start, q_vid, wp2_before)
        e2b = smap._add_edge(q_vid, e2.v_end, wp2_after)
        e2_sub_fwd = [e2a, e2b]
        del smap.edges[eid2]

    # Patch all OTHER faces that reference eid1 or eid2 (adjacent faces)
    for other_fid, other_boundary in list(smap.faces.items()):
        if other_fid == fid:
            continue
        new_boundary = other_boundary
        if any(abs(s) == eid1 for s in new_boundary):
            new_boundary = _replace_edge_in_face(new_boundary, eid1, e1_sub_fwd)
        if not same_edge and e2_sub_fwd is not None and any(abs(s) == eid2 for s in new_boundary):
            new_boundary = _replace_edge_in_face(new_boundary, eid2, e2_sub_fwd)
        smap.faces[other_fid] = new_boundary

    # Compute new arc waypoints (face_verts was captured before edge deletion)
    arc_waypoints = waypoints if waypoints is not None else auto_waypoints(p_pos, q_pos, face_verts)
    arc_fwd = smap._add_edge(p_vid, q_vid, arc_waypoints)

    # Rebuild the two face boundaries
    old_boundary = list(smap.faces[fid])
    old_color = smap.colors[fid]
    del smap.faces[fid]
    del smap.colors[fid]

    if same_edge:
        f1_boundary, f2_boundary = _rebuild_boundary_same_edge(
            old_boundary, eid1, e1a, e1m, e1b, arc_fwd, e1.v_start
        )
    else:
        f1_boundary, f2_boundary = _rebuild_boundary_diff_edges(
            old_boundary, eid1, e1a, e1b, eid2, e2a, e2b, arc_fwd
        )

    fid1 = smap._add_face(f1_boundary, old_color)
    fid2 = smap._add_face(f2_boundary, old_color)
    smap.colors[fid1] = assign_color(smap, fid1)
    smap.colors[fid2] = assign_color(smap, fid2)
    return fid1, fid2


def _largest_face(smap: SphericalMap) -> int:
    """Return fid of face with most edges in boundary."""
    return max(smap.faces, key=lambda f: len(smap.faces[f]))


def _non_adjacent_edge_pair(smap: SphericalMap, fid: int) -> tuple[int, int]:
    """Return two edge ids from face boundary that are not consecutive (maximally separated)."""
    boundary = smap.faces[fid]
    n = len(boundary)
    if n < 3:
        return abs(boundary[0]), abs(boundary[0])  # same-edge fallback
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
