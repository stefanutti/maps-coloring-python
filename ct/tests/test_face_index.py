"""Bulk index construction: identity, ordering, rebuilding and scaling."""
import cProfile
import importlib.util
from pathlib import Path
import sys

import pytest


@pytest.fixture(scope="module")
def mod():
    ct = Path(__file__).resolve().parents[1]
    if str(ct) not in sys.path:
        sys.path.insert(0, str(ct))
    spec = importlib.util.spec_from_file_location("fourct_face_index_tests", ct / "4ct.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bulk_index_keeps_equal_faces_distinct_and_deduplicates_occurrences(mod):
    first = [(0, 1), (1, 0)]
    equal = first[:]
    repeated = [(0, 2), (2, 0), (0, 2), (2, 0)]
    faces = [first, repeated, equal]
    index = mod.FaceIndex(faces)

    assert index.g_faces is faces
    assert index.face_positions == {id(first): 0, id(repeated): 1, id(equal): 2}
    assert {k: list(map(id, v)) for k, v in index.faces_by_len.items()} == {
        2: [id(first), id(equal)], 4: [id(repeated)]}
    assert {k: list(map(id, v)) for k, v in index.edge_to_faces.items()} == {
        (0, 1): [id(first), id(equal)], (1, 0): [id(first), id(equal)],
        (0, 2): [id(repeated)], (2, 0): [id(repeated)]}
    assert {k: list(map(id, v)) for k, v in index.vertex_to_faces.items()} == {
        0: [id(first), id(repeated), id(equal)], 1: [id(first), id(equal)],
        2: [id(repeated)]}
    assert index.first_face_with_edge((0, 1), exclude_face=first) is equal
    assert list(map(id, index.faces_touching_vertices({1, 2}))) == list(map(id, faces))
    assert index.validate()


def test_rebuild_replaces_stale_buckets_and_handles_empty_source(mod):
    removed = [(0, 1), (1, 0)]
    kept = [(2, 3), (3, 2)]
    added = [(4, 5), (5, 6), (6, 4)]
    faces = [removed, kept]
    index = mod.FaceIndex(faces)
    faces[:] = [added, kept]
    index.rebuild()

    assert index.face_positions == {id(added): 0, id(kept): 1}
    assert index.first_face_with_edge((0, 1)) is None
    assert index.first_face_with_vertex(0) is None
    assert index.first_face_with_vertex(4) is added
    assert list(map(id, index.faces_of_size(2))) == [id(kept)]
    assert list(map(id, index.faces_of_size(3))) == [id(added)]
    assert index.validate()

    faces.clear()
    index.rebuild()
    assert index.face_positions == {}
    assert index.faces_by_len == {}
    assert index.edge_to_faces == {}
    assert index.vertex_to_faces == {}
    assert index.validate()


def test_bulk_index_preserves_last_position_for_repeated_object(mod):
    first = [(0, 1), (1, 0)]
    equal = first[:]
    index = mod.FaceIndex([first, equal, first])

    assert index.face_positions == {id(first): 2, id(equal): 1}
    assert list(map(id, index.faces_of_size(2))) == [id(equal), id(first)]
    assert list(map(id, index.edge_to_faces[(0, 1)])) == [id(equal), id(first)]
    assert list(map(id, index.vertex_to_faces[0])) == [id(equal), id(first)]
    assert index.validate()


def test_incremental_reinsertion_after_bulk_build_keeps_order_and_identity(mod):
    first = [(0, 1), (1, 0)]
    second, third = first[:], first[:]
    faces = [first, second, third]
    index = mod.FaceIndex(faces)
    index.unindex_face(first)
    index.unindex_face(second)
    index.index_face(second)
    index.index_face(first)
    index.index_face(first)

    assert list(map(id, index.faces_of_size(2))) == list(map(id, faces))
    assert list(map(id, index.edge_to_faces[(0, 1)])) == list(map(id, faces))
    assert list(map(id, index.vertex_to_faces[0])) == list(map(id, faces))
    assert index.validate()


@pytest.mark.parametrize("mapping,key", [
    ("faces_by_len", 2), ("edge_to_faces", (0, 1)), ("vertex_to_faces", 0),
])
def test_validate_detects_wrong_bucket_order_after_bulk_build(mod, mapping, key):
    first = [(0, 1), (1, 0)]
    index = mod.FaceIndex([first, first[:]])
    getattr(index, mapping)[key].reverse()
    with pytest.raises(SystemExit):
        index.validate()


@pytest.mark.parametrize("shared_edges", [False, True])
def test_bulk_construction_work_scales_linearly(mod, shared_edges):
    # Count actual interpreter calls instead of machine-dependent wall time.
    # Reintroducing repeated scans over growing buckets gives ~4x work when
    # the input doubles; a single traversal stays near 2x. These are synthetic
    # index inputs, not a graph-validation test or a dataset benchmark.
    work = []
    for size in (128, 256):
        faces = [[(0, 1), (1, 0)] if shared_edges else
                 [(2 * i, 2 * i + 1), (2 * i + 1, 2 * i)] for i in range(size)]
        profiler = cProfile.Profile()
        index = profiler.runcall(mod.FaceIndex, faces)
        work.append(sum(entry.callcount for entry in profiler.getstats()))
        assert list(map(id, index.faces_of_size(2))) == list(map(id, faces))
    assert work[1] < 2.5 * work[0], work
