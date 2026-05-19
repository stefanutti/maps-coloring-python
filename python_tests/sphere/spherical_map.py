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
