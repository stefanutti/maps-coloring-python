import numpy as np
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

def test_make_initial_map_directed_edge_invariant():
    smap = make_initial_map()
    forward_count: dict[int, int] = {}
    backward_count: dict[int, int] = {}
    for fid, eids in smap.faces.items():
        for s in eids:
            eid = abs(s)
            if s > 0:
                forward_count[eid] = forward_count.get(eid, 0) + 1
            else:
                backward_count[eid] = backward_count.get(eid, 0) + 1
    for eid in smap.edges:
        assert forward_count.get(eid, 0) == 1, f"edge {eid} forward count != 1"
        assert backward_count.get(eid, 0) == 1, f"edge {eid} backward count != 1"


from sphere.spherical_map import neighbors, assign_color, auto_waypoints, _face_vertex_positions

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
    # Antipodal points → p+q = zero vector → NaN → must fallback to []
    p = np.array([1.0, 0.0, 0.0])
    q = np.array([-1.0, 0.0, 0.0])
    face_verts = [p, np.array([0.0, 1.0, 0.0]), q]
    result = auto_waypoints(p, q, face_verts)
    assert result == [], f"expected [], got {result}"


from sphere.spherical_map import split_face

def _check_invariants(smap):
    """Assert cubic + planar + Euler invariants."""
    V = len(smap.vertices)
    E = len(smap.edges)
    F = len(smap.faces)
    assert V - E + F == 2, f"Euler: {V}-{E}+{F}={V-E+F}"

    # Each edge appears in exactly 2 faces (forward once, backward once)
    forward_count: dict[int, int] = {}
    backward_count: dict[int, int] = {}
    for fid, signed_eids in smap.faces.items():
        for s in signed_eids:
            eid = abs(s)
            if s > 0:
                forward_count[eid] = forward_count.get(eid, 0) + 1
            else:
                backward_count[eid] = backward_count.get(eid, 0) + 1
    for eid in smap.edges:
        assert forward_count.get(eid, 0) == 1, f"edge {eid} forward count != 1"
        assert backward_count.get(eid, 0) == 1, f"edge {eid} backward count != 1"

    # Each vertex has degree exactly 3
    deg: dict[int, int] = {}
    for e in smap.edges.values():
        deg[e.v_start] = deg.get(e.v_start, 0) + 1
        deg[e.v_end]   = deg.get(e.v_end, 0) + 1
    for vid, d in deg.items():
        assert d == 3, f"vertex {vid} has degree {d}"

    # All vertices on unit sphere
    for vid, pos in smap.vertices.items():
        assert abs(np.linalg.norm(pos) - 1.0) < 1e-9, f"vertex {vid} not on sphere"

    # Each face boundary must be a continuous closed walk
    for fid, boundary in smap.faces.items():
        for i, s in enumerate(boundary):
            e = smap.edges[abs(s)]
            end_vid = e.v_end if s > 0 else e.v_start
            ns = boundary[(i + 1) % len(boundary)]
            ne = smap.edges[abs(ns)]
            start_vid = ne.v_start if ns > 0 else ne.v_end
            assert end_vid == start_vid, (
                f"face {fid} boundary broken between position {i} and {i+1}: "
                f"edge {abs(s)} ends at v{end_vid}, next edge {abs(ns)} starts at v{start_vid}"
            )


def test_split_face_euler_invariant():
    smap = make_initial_map()
    fid = list(smap.faces.keys())[0]
    boundary = smap.faces[fid]
    eid1 = abs(boundary[0])
    eid2 = abs(boundary[1])
    split_face(smap, fid, eid1, 0.5, eid2, 0.5)
    _check_invariants(smap)


def test_split_face_returns_two_new_face_ids():
    smap = make_initial_map()
    fid = list(smap.faces.keys())[0]
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
