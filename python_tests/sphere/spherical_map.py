from __future__ import annotations
import math
import numpy as np


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
