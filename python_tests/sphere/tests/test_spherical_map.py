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
