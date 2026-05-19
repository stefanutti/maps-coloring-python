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
