"""Hand-worked oracle examples and automatic keyed reduction/replay checks."""
from collections import Counter
from dataclasses import replace
import importlib.util
from itertools import permutations
from pathlib import Path
import sys

import networkx as nx
import pytest

CT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CT))
from ct_graph_utils import (
    apply_half_kempe_loop_color_switching, graph_add_edge, graph_delete_edge,
    is_the_graph_one_edge_connected, is_well_colored, join_faces,
    kempe_chain_color_swap, remove_vertex_from_face,
)


CASE_NAMES = (
    "theta", "f2", "f3", "f4_two_colors", "f4_three_colors",
    "f4_same_cycle", "f5", "f5_no_direct_witness",
)


@pytest.fixture
def colored_cases():
    theta = (
        ((0, 1, "red"), (1, 0, "green")),
        ((0, 1, "green"), (1, 0, "blue")),
        ((0, 1, "blue"), (1, 0, "red")),
    )
    digons = (
        ((0, 1, "red"), (1, 0, "blue")),
        ((2, 3, "red"), (3, 2, "blue")),
        ((0, 1, "blue"), (1, 3, "green"), (3, 2, "red"), (2, 0, "green")),
        ((1, 0, "red"), (0, 2, "green"), (2, 3, "blue"), (3, 1, "green")),
    )
    tetrahedron = (
        ((0, 1, "blue"), (1, 2, "green"), (2, 0, "red")),
        ((1, 0, "blue"), (0, 3, "green"), (3, 1, "red")),
        ((2, 1, "green"), (1, 3, "red"), (3, 2, "blue")),
        ((0, 2, "red"), (2, 3, "blue"), (3, 0, "green")),
    )
    square = ("red", "green", "red", "green")
    cube = prism_faces(square, square, ("blue",) * 4)
    cube_three = prism_faces(
        ("blue", "green", "red", "green"),
        ("blue", "green", "red", "green"),
        ("red", "red", "blue", "blue"),
    )
    cube_same = prism_faces(
        square, ("green", "red", "green", "red"), ("blue",) * 4,
    )
    pentagon = ("blue", "green", "red", "blue", "green")
    prism = prism_faces(
        pentagon, pentagon, ("red", "red", "blue", "green", "red"),
    )
    return {
        "theta": dict(faces=theta, face_index=0, edge_index=None, multiplicities=[1, 1]),
        "f2": dict(faces=digons, face_index=0, edge_index=0, multiplicities=[1, 1]),
        "f3": dict(faces=tetrahedron, face_index=0, edge_index=0, multiplicities=[1, 1, 1]),
        "f4_two_colors": dict(faces=cube, face_index=0, edge_index=0, multiplicities=[2, 2]),
        "f4_three_colors": dict(faces=cube_three, face_index=0, edge_index=0, multiplicities=[1, 1, 2]),
        "f4_same_cycle": dict(faces=cube_same, face_index=0, edge_index=1, multiplicities=[2, 2]),
        "f5": dict(faces=prism, face_index=0, edge_index=2, multiplicities=[1, 2, 2]),
        "f5_no_direct_witness": dict(faces=prism, face_index=0, edge_index=0, multiplicities=[1, 2, 2]),
    }


def prism_faces(top, bottom, spokes):
    """Assemble the fixed prism embedding, without finding any coloring."""
    size = len(top)
    colors = {}
    for i in range(size):
        following = (i + 1) % size
        colors[tuple(sorted((i, following)))] = top[i]
        colors[tuple(sorted((size + i, size + following)))] = bottom[i]
        colors[i, size + i] = spokes[i]
    cycles = [list(range(size)), list(reversed(range(size, 2 * size)))]
    cycles.extend([((i + 1) % size), i, size + i, size + ((i + 1) % size)]
                  for i in range(size))
    return tuple(tuple((u, v, colors[tuple(sorted((u, v)))])
                       for u, v in zip(cycle, cycle[1:] + cycle[:1]))
                 for cycle in cycles)


def graph_from_faces(faces):
    graph = nx.MultiGraph()
    for face in faces:
        for u, v, color in face:
            if u < v:
                graph_add_edge(graph, u, v, color)
    return graph


def colored_multiset(graph):
    return Counter((min(u, v), max(u, v), data["color"])
                   for u, v, data in graph.edges(data=True))


@pytest.fixture
def mod():
    spec = importlib.util.spec_from_file_location("fourct_oracle_examples", CT / "4ct.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("name", CASE_NAMES)
def test_colored_case_fixtures_are_valid(colored_cases, name):
    # Catches a malformed worked example before later transformation tests
    # can incorrectly treat it as an admissible colored planar input.
    assert name in colored_cases, "Missing hand-worked example"
    case = colored_cases[name]
    faces = case["faces"]
    graph = graph_from_faces(faces)
    assert is_well_colored(graph)
    assert nx.is_connected(graph)
    assert nx.check_planarity(graph)[0]
    assert nx.number_of_selfloops(graph) == 0
    assert not list(nx.bridges(graph))
    assert len(graph) - graph.number_of_edges() + len(faces) == 2
    darts = Counter(edge for face in faces for edge in face)
    assert all(count == 1 for count in darts.values())
    assert darts == Counter((v, u, color) for u, v, color in darts)
    rotation = {}
    for face in faces:
        for (u, v, color), (a, b, other) in zip(face, face[1:] + face[:1]):
            assert v == a and color != other
            rotation[v, u, color] = (a, b, other)
    for dart in darts:
        assert rotation[rotation[rotation[dart]]] == dart
        assert rotation[dart] != dart
    face = faces[case["face_index"]]
    assert sorted(Counter(color for _, _, color in face).values()) == case["multiplicities"]


@pytest.mark.parametrize("name,connected", [
    ("f4_two_colors", False), ("f4_same_cycle", True),
    ("f5", True), ("f5_no_direct_witness", False),
])
def test_selected_edge_complementary_cycles(colored_cases, name, connected):
    case = colored_cases[name]
    graph = graph_from_faces(case["faces"])
    u, v, omitted = case["faces"][case["face_index"]][case["edge_index"]]
    complementary = nx.Graph()
    complementary.add_nodes_from(graph)
    complementary.add_edges_from((a, b) for a, b, data in graph.edges(data=True)
                                 if data["color"] != omitted)
    assert nx.has_path(complementary, u, v) == connected


@pytest.mark.parametrize("name,expected", [
    ("f4_two_colors", {frozenset((0, 1, 4, 5)), frozenset((2, 3, 6, 7))}),
    ("f4_same_cycle", {frozenset(range(8))}),
])
def test_opposite_red_edges_explain_f4_subcase(colored_cases, name, expected):
    graph = graph_from_faces(colored_cases[name]["faces"])
    complementary = nx.Graph((u, v) for u, v, data in graph.edges(data=True)
                             if data["color"] in ("red", "blue"))
    assert {frozenset(c) for c in nx.connected_components(complementary)} == expected


# Hand-derived answers, not computed from the transformation under test.
REDUCED_CUBE = (
    (2, 3, "green"), (4, 5, "blue"), (5, 6, "green"),
    (6, 7, "red"), (4, 7, "green"), (2, 6, "blue"),
    (3, 7, "blue"), (3, 4, "red"), (2, 5, "red"),
)
WORKED_STEPS = {
    "f3": dict(
        ariadne=[3, 0, 1, 2, 2, 3, 3], path=(0, 2, 1),
        pair=("red", "green"), fused=("green", "red"),
        expected=((2, 3, "red"), (2, 3, "green"), (2, 3, "blue")),
    ),
    "f4_three_colors": dict(
        ariadne=[4, 0, 1, 3, 2, 4, 5], path=(0, 3, 2, 1),
        pair=("green", "red"), fused=("red", "red"), expected=REDUCED_CUBE,
    ),
    "f4_two_colors": dict(
        ariadne=[4, 0, 1, 3, 2, 4, 5], path=(0, 3, 2, 1),
        pair=("green", "red"), fused=("red", "red"), expected=REDUCED_CUBE,
    ),
    "f4_same_cycle": dict(
        ariadne=[4, 1, 2, 0, 3, 5, 6], path=(1, 0, 4, 7, 3, 2),
        pair=("red", "blue"), fused=("blue", "blue"),
        expected=((0, 3, "green"), (4, 5, "green"), (5, 6, "red"),
                  (6, 7, "green"), (4, 7, "blue"), (0, 4, "red"),
                  (3, 7, "red"), (0, 5, "blue"), (3, 6, "blue")),
    ),
}


def check_reduced_structure(graph, original_faces, face_number, edge_number, mod):
    """Independent face-surgery check using the existing production primitives."""
    faces = [[(u, v) for u, v, _ in face] for face in original_faces]
    face = faces[face_number]
    u, v = face[edge_number]
    neighbor = next(other for other in faces if other is not face and (v, u) in other)
    merged = join_faces(face, neighbor, (u, v))
    assert not is_the_graph_one_edge_connected(merged)
    reduced_faces = [merged]
    for other in faces:
        if other is not face and other is not neighbor:
            remaining = other[:]
            for vertex in (u, v):
                if any(a == vertex for a, _ in remaining):
                    remove_vertex_from_face(remaining, vertex)
            reduced_faces.append(remaining)
    expected = Counter()
    for a, b in graph.edges():
        expected[a, b] += 1
        expected[b, a] += 1
    assert Counter(edge for other in reduced_faces for edge in other) == expected
    assert len(reduced_faces) == len(original_faces) - 1
    assert mod.FaceIndex(reduced_faces).validate()
    assert is_well_colored(graph)
    assert nx.is_connected(graph) and nx.check_planarity(graph)[0]
    assert nx.number_of_selfloops(graph) == 0 and not list(nx.bridges(graph))
    for other in reduced_faces:
        assert all(v == a for (_, v), (a, _) in zip(other, other[1:] + other[:1]))


@pytest.mark.parametrize("renamed", permutations(("red", "green", "blue")))
@pytest.mark.parametrize("name", WORKED_STEPS)
def test_hand_worked_f3_f4_reduction_and_inverse(colored_cases, mod, name, renamed):
    # Catches wrong Kempe/half-cycle colors or wrong face surgery on literal
    # examples. This intentionally does not implement candidate discovery.
    colors = dict(zip(("red", "green", "blue"), renamed))
    case = colored_cases[name]
    faces = tuple(tuple((u, v, colors[c]) for u, v, c in face) for face in case["faces"])
    graph = graph_from_faces(faces)
    original = colored_multiset(graph)
    original_vertices = set(graph)
    step = WORKED_STEPS[name]
    _, u, v, on_u, on_v, off_u, off_v = step["ariadne"]
    if name == "f4_two_colors":
        kempe_chain_color_swap(graph, (0, 1), colors["red"], colors["blue"])
        prepared = graph_from_faces(colored_cases["f4_three_colors"]["faces"])
        assert colored_multiset(graph) == Counter(
            (a, b, colors[c]) for a, b, c in colored_multiset(prepared).elements())
        assert is_well_colored(graph)
    assert len(graph[u][v]) == 1
    deleted_color = next(iter(graph[u][v].values()))["color"]
    graph_delete_edge(graph, u, v, deleted_color)
    pair = tuple(colors[c] for c in step["pair"])
    path = step["path"]
    for a, b in zip(path, path[1:]):
        assert len(graph[a][b]) == 1
        data = next(iter(graph[a][b].values()))
        assert data["color"] in pair
        data["color"] = pair[1] if data["color"] == pair[0] else pair[0]
    fused = tuple(colors[c] for c in step["fused"])
    for vertex, on_face, off_face, color in (
            (u, on_u, off_u, fused[0]), (v, on_v, off_v, fused[1])):
        assert {data["color"] for _, _, data in graph.edges(vertex, data=True)} == {color}
        graph.remove_node(vertex)
        graph_add_edge(graph, on_face, off_face, color)
    assert set(graph) == original_vertices - {u, v}
    assert graph.number_of_edges() == sum(original.values()) - 3
    assert colored_multiset(graph) == Counter((min(a, b), max(a, b), colors[c])
                                             for a, b, c in step["expected"])
    check_reduced_structure(graph, faces, case["face_index"], case["edge_index"], mod)

    inverse_other = next(c for c in pair if c != fused[0])
    apply_half_kempe_loop_color_switching(graph, step["ariadne"], *fused,
                                         fused[0], inverse_other)
    if name == "f4_two_colors":
        kempe_chain_color_swap(graph, (0, 1), colors["blue"], colors["red"])
    assert set(graph) == original_vertices
    assert colored_multiset(graph) == original
    assert is_well_colored(graph)


@pytest.mark.parametrize("renamed", permutations(("red", "green", "blue")))
def test_hand_worked_f2_reduction_and_inverse(colored_cases, mod, renamed):
    colors = dict(zip(("red", "green", "blue"), renamed))
    faces = tuple(tuple((u, v, colors[c]) for u, v, c in face)
                  for face in colored_cases["f2"]["faces"])
    graph = graph_from_faces(faces)
    original = colored_multiset(graph)
    assert next(iter(graph[0][2].values()))["color"] == colors["green"]
    assert next(iter(graph[1][3].values()))["color"] == colors["green"]
    graph.remove_nodes_from((0, 1))
    graph_add_edge(graph, 2, 3, colors["green"])
    assert set(graph) == {2, 3}
    assert colored_multiset(graph) == Counter((2, 3, colors[c]) for c in ("red", "green", "blue"))
    check_reduced_structure(graph, faces, 0, 0, mod)
    # Select the fused edge by its known color, not the first parallel key.
    graph_delete_edge(graph, 2, 3, colors["green"])
    for a, b, color in ((0, 2, "green"), (1, 3, "green"),
                        (0, 1, "red"), (0, 1, "blue")):
        graph_add_edge(graph, a, b, colors[color])
    assert set(graph) == {0, 1, 2, 3}
    assert colored_multiset(graph) == original
    assert is_well_colored(graph)


def test_theta_is_terminal_in_existing_pipeline(colored_cases, mod):
    faces = [[(u, v) for u, v, _ in face] for face in colored_cases["theta"]["faces"]]
    original = [face[:] for face in faces]
    mod.stats = {}
    mod.initialize_statistics()
    mod.init_f_distribution(faces)

    def no_further_selection(*args):
        pytest.fail("Theta must not select another F2 reduction")

    assert mod.reduce_faces(faces, 2345, no_further_selection) == []
    assert faces == original
    assert len({id(face) for face in faces}) == 3


@pytest.fixture
def oracle():
    # Import at test execution so a missing module does not hide Task 1 tests.
    return importlib.import_module("experiments.oracle_reduction")


def snapshot_state(state):
    """Independent semantic snapshot, excluding ephemeral Python object IDs."""
    return (
        tuple(sorted(state.graph.nodes())),
        tuple(sorted((min(u, v), max(u, v), key, data["color"])
                     for u, v, key, data in state.graph.edges(keys=True, data=True))),
        tuple(tuple(face) for face in state.g_faces), tuple(state.face_ids),
        tuple(sorted((fid, tuple(ids)) for fid, ids in state.face_edge_ids.items())),
        tuple(sorted(state.edge_endpoints.items())),
        state.next_edge_id, state.next_face_id,
    )


@pytest.fixture
def f2_certificate(oracle, colored_cases):
    before = oracle.make_state(colored_cases["f2"]["faces"])
    # Literal result: keep red/blue edges 2/3, create green edge 6.
    graph = nx.MultiGraph()
    for eid, color in ((2, "red"), (3, "blue"), (6, "green")):
        graph.add_edge(2, 3, key=eid, color=color)
    after = oracle.OracleState(
        graph=graph,
        g_faces=[[(2, 3), (3, 2)], [(2, 3), (3, 2)], [(3, 2), (2, 3)]],
        face_ids=[1, 2, 4], face_edge_ids={1: [2, 3], 2: [6, 2], 4: [6, 3]},
        edge_endpoints={2: (2, 3), 3: (2, 3), 6: (2, 3)},
        next_edge_id=7, next_face_id=5,
    )
    witness = oracle.StepWitness(
        candidate=oracle.Candidate(face_id=0, edge_id=0),
        ariadne=(2, 0, 1, 2, 3),
        before_edges=(oracle.EdgeRecord(0, 0, 1, "red"),
                      oracle.EdgeRecord(1, 0, 1, "blue"),
                      oracle.EdgeRecord(4, 1, 3, "green"),
                      oracle.EdgeRecord(5, 0, 2, "green")),
        after_edges=(oracle.EdgeRecord(6, 2, 3, "green"),),
        before_faces=(
            oracle.FaceRecord(0, 0, ((0, 1, 0), (1, 0, 1))),
            oracle.FaceRecord(2, 2, ((0, 1, 1), (1, 3, 4), (3, 2, 2), (2, 0, 5))),
            oracle.FaceRecord(3, 3, ((1, 0, 0), (0, 2, 5), (2, 3, 3), (3, 1, 4))),
        ),
        after_faces=(oracle.FaceRecord(2, 1, ((2, 3, 6), (3, 2, 2))),
                     oracle.FaceRecord(4, 2, ((3, 2, 6), (2, 3, 3)))),
        before_next_ids=(6, 4), after_next_ids=(7, 5),
        before_fingerprint=oracle.state_fingerprint(before),
        after_fingerprint=oracle.state_fingerprint(after), swaps=(),
    )
    return before, witness, after


def test_theta_keeps_three_edge_ids_and_three_face_ids(oracle, colored_cases):
    state = oracle.make_state(colored_cases["theta"]["faces"])
    assert len(state.edge_endpoints) == 3
    assert len(set(state.face_ids)) == 3
    assert len({id(face) for face in state.g_faces}) == 3
    assert state.g_faces[0] == state.g_faces[1] == state.g_faces[2]
    assert set(state.graph[0][1]) == set(state.edge_endpoints)
    for eid in state.edge_endpoints:
        occurrences = [(u, v) for fid, face in zip(state.face_ids, state.g_faces)
                       for (u, v), item in zip(face, state.face_edge_ids[fid]) if item == eid]
        assert sorted(occurrences) == [(0, 1), (1, 0)]
    oracle.assert_state_invariants(state)


def test_make_state_does_not_alias_input(oracle, colored_cases):
    raw = [[list(edge) for edge in face] for face in colored_cases["theta"]["faces"]]
    first = oracle.make_state(raw)
    second = oracle.make_state(raw)
    before = snapshot_state(first)
    raw[0][0][2] = "invalid"
    second.g_faces[0].clear()
    second.face_edge_ids[second.face_ids[1]].clear()
    second.graph[0][1][0]["color"] = "invalid"
    assert snapshot_state(first) == before
    oracle.assert_state_invariants(first)


def test_witness_roundtrip_restores_full_state(oracle, f2_certificate):
    state, witness, expected = f2_certificate
    before = snapshot_state(state)
    oracle.apply_step(state, witness)
    assert snapshot_state(state) == snapshot_state(expected)
    oracle.assert_state_invariants(state)
    oracle.undo_step(state, witness)
    assert snapshot_state(state) == before
    oracle.assert_state_invariants(state)
    # Certificates are reusable after exact undo, including allocation counters.
    oracle.apply_step(state, witness)
    assert snapshot_state(state) == snapshot_state(expected)


def test_stale_witness_does_not_mutate_state(oracle, f2_certificate):
    state, witness, _ = f2_certificate
    before = snapshot_state(state)
    with pytest.raises(ValueError, match="precondition"):
        oracle.undo_step(state, witness)
    assert snapshot_state(state) == before
    oracle.apply_step(state, witness)
    reduced = snapshot_state(state)
    graph, faces, index = state.graph, state.g_faces, state.face_index
    with pytest.raises(ValueError, match="precondition"):
        oracle.apply_step(state, witness)
    assert snapshot_state(state) == reduced
    assert state.graph is graph and state.g_faces is faces and state.face_index is index


def test_invalid_witness_result_is_atomic(oracle, f2_certificate):
    state, witness, expected = f2_certificate
    # A syntactically applicable patch whose result has two red parallel edges.
    expected.graph[2][3][6]["color"] = "red"
    invalid = replace(witness, after_edges=(oracle.EdgeRecord(6, 2, 3, "red"),),
                      after_fingerprint=oracle.state_fingerprint(expected))
    before = snapshot_state(state)
    graph, faces, index = state.graph, state.g_faces, state.face_index
    with pytest.raises(AssertionError):
        oracle.apply_step(state, invalid)
    assert snapshot_state(state) == before
    assert state.graph is graph and state.g_faces is faces and state.face_index is index
    oracle.assert_state_invariants(state)


def test_corrupted_occurrence_is_detected_with_unchanged_counts(oracle, colored_cases):
    state = oracle.make_state(colored_cases["theta"]["faces"])
    state.face_edge_ids[0][0] = state.face_edge_ids[0][1]
    assert (len(state.graph), state.graph.number_of_edges(), len(state.g_faces)) == (2, 3, 3)
    with pytest.raises(AssertionError, match="occurrence"):
        oracle.assert_state_invariants(state)


@pytest.mark.parametrize("corruption", ["endpoint", "length", "rotation", "closure", "index"])
def test_state_invariants_reject_corrupted_embedding(oracle, colored_cases, corruption):
    state = oracle.make_state(colored_cases["theta"]["faces"])
    if corruption == "endpoint":
        state.g_faces[0][0] = (0, 99)
    elif corruption == "length":
        state.face_edge_ids[0].append(0)
    elif corruption == "rotation":
        # Still two occurrences per edge and Euler=2, but three disjoint
        # one-dart rotations at each supposed cubic vertex: not this embedding.
        state.face_edge_ids = {0: [0, 0], 1: [1, 1], 2: [2, 2]}
    elif corruption == "closure":
        state.g_faces[0][1] = (0, 1)
    else:
        state.face_index.face_positions.clear()
    with pytest.raises(AssertionError):
        oracle.assert_state_invariants(state)


def test_wrong_ariadne_neighbors_are_rejected(oracle, f2_certificate):
    state, witness, _ = f2_certificate
    bad = replace(witness, ariadne=(2, 0, 1, 2, 999))
    before = snapshot_state(state)
    with pytest.raises(ValueError, match="Ariadne"):
        oracle.apply_step(state, bad)
    assert snapshot_state(state) == before


@pytest.fixture
def f3_certificate(oracle, colored_cases):
    before = oracle.make_state(colored_cases["f3"]["faces"])
    graph = nx.MultiGraph()
    for eid, color in ((5, "blue"), (6, "green"), (7, "red")):
        graph.add_edge(2, 3, key=eid, color=color)
    after = oracle.OracleState(
        graph=graph, g_faces=[[(2, 3), (3, 2)] for _ in range(3)],
        face_ids=[2, 3, 4], face_edge_ids={2: [7, 5], 3: [5, 6], 4: [6, 7]},
        edge_endpoints={5: (2, 3), 6: (2, 3), 7: (2, 3)},
        next_edge_id=8, next_face_id=5,
    )
    witness = oracle.StepWitness(
        candidate=oracle.Candidate(0, 0), ariadne=(3, 0, 1, 2, 2, 3, 3),
        before_edges=(oracle.EdgeRecord(0, 0, 1, "blue"),
                      oracle.EdgeRecord(1, 1, 2, "green"),
                      oracle.EdgeRecord(2, 0, 2, "red"),
                      oracle.EdgeRecord(3, 0, 3, "green"),
                      oracle.EdgeRecord(4, 1, 3, "red")),
        after_edges=(oracle.EdgeRecord(6, 2, 3, "green"), oracle.EdgeRecord(7, 2, 3, "red")),
        before_faces=(
            oracle.FaceRecord(0, 0, ((0, 1, 0), (1, 2, 1), (2, 0, 2))),
            oracle.FaceRecord(1, 1, ((1, 0, 0), (0, 3, 3), (3, 1, 4))),
            oracle.FaceRecord(2, 2, ((2, 1, 1), (1, 3, 4), (3, 2, 5))),
            oracle.FaceRecord(3, 3, ((0, 2, 2), (2, 3, 5), (3, 0, 3))),
        ),
        after_faces=(oracle.FaceRecord(2, 0, ((2, 3, 7), (3, 2, 5))),
                     oracle.FaceRecord(3, 1, ((2, 3, 5), (3, 2, 6))),
                     oracle.FaceRecord(4, 2, ((2, 3, 6), (3, 2, 7)))),
        before_next_ids=(6, 4), after_next_ids=(8, 5),
        before_fingerprint=oracle.state_fingerprint(before),
        after_fingerprint=oracle.state_fingerprint(after),
        swaps=(oracle.ColorSwap(("red", "green"), ((0, 2, 2), (2, 1, 1)), "path"),),
    )
    return before, witness, after


def test_witness_f3_replays_colors_and_persistent_ids(oracle, f3_certificate):
    state, witness, expected = f3_certificate
    before = snapshot_state(state)
    oracle.apply_step(state, witness)
    assert snapshot_state(state) == snapshot_state(expected)
    assert state.graph[2][3][5]["color"] == "blue"  # The untouched parallel edge.
    oracle.undo_step(state, witness)
    assert snapshot_state(state) == before
    oracle.assert_state_invariants(state)


@pytest.mark.parametrize("corruption", ["missing", "colors", "edge_id", "order", "kind"])
def test_witness_rejects_inconsistent_swap_trace(oracle, f3_certificate, corruption):
    state, witness, _ = f3_certificate
    swap = witness.swaps[0]
    if corruption == "missing":
        changes = ()
    elif corruption == "colors":
        changes = (replace(swap, colors=("blue", "green")),)
    elif corruption == "edge_id":
        changes = (replace(swap, darts=((0, 2, 5), (2, 1, 1))),)
    elif corruption == "order":
        changes = (replace(swap, darts=tuple(reversed(swap.darts))),)
    else:
        changes = (replace(swap, kind="cycle"),)
    before = snapshot_state(state)
    with pytest.raises(ValueError, match="swap"):
        oracle.apply_step(state, replace(witness, swaps=changes))
    assert snapshot_state(state) == before


def test_step_attempt_keeps_unknown_separate_from_certificate(oracle, f2_certificate):
    _, witness, _ = f2_certificate
    assert oracle.StepAttempt("certified", "explicit witness", witness).witness is witness
    for status in ("no_witness", "unsupported_case", "structurally_rejected"):
        assert oracle.StepAttempt(status, "not resolved").witness is None
        with pytest.raises(ValueError):
            oracle.StepAttempt(status, "not resolved", witness)
    with pytest.raises(ValueError):
        oracle.StepAttempt("certified", "missing certificate")
    with pytest.raises(ValueError):
        oracle.StepAttempt("impossible", "not an experimental outcome")


def test_witness_rejects_swapped_on_off_ariadne_neighbors(oracle, f3_certificate):
    state, witness, _ = f3_certificate
    before = snapshot_state(state)
    with pytest.raises(ValueError, match="Ariadne"):
        oracle.apply_step(state, replace(witness, ariadne=(3, 0, 1, 3, 2, 2, 3)))
    assert snapshot_state(state) == before


@pytest.fixture
def f4_certificate(oracle, colored_cases):
    before = oracle.make_state(colored_cases["f4_two_colors"]["faces"])
    graph = nx.MultiGraph()
    records = ((2, 2, 3, "green"), (4, 6, 7, "red"), (5, 5, 6, "green"),
               (6, 4, 5, "blue"), (7, 4, 7, "green"), (10, 2, 6, "blue"),
               (11, 3, 7, "blue"), (12, 3, 4, "red"), (13, 2, 5, "red"))
    for eid, u, v, color in records:
        graph.add_edge(u, v, key=eid, color=color)
    after = oracle.OracleState(
        graph=graph,
        g_faces=[[(7, 6), (6, 5), (5, 4), (4, 7)],
                 [(2, 5), (5, 6), (6, 2)],
                 [(3, 2), (2, 6), (6, 7), (7, 3)],
                 [(4, 3), (3, 7), (7, 4)],
                 [(3, 4), (4, 5), (5, 2), (2, 3)]],
        face_ids=[1, 3, 4, 5, 6],
        face_edge_ids={1: [4, 5, 6, 7], 3: [13, 5, 10], 4: [2, 10, 4, 11],
                       5: [12, 11, 7], 6: [12, 6, 13, 2]},
        edge_endpoints={eid: (u, v) for eid, u, v, _ in records},
        next_edge_id=14, next_face_id=7,
    )
    witness = oracle.StepWitness(
        candidate=oracle.Candidate(0, 0), ariadne=(4, 0, 1, 3, 2, 4, 5),
        before_edges=(oracle.EdgeRecord(0, 0, 1, "red"),
                      oracle.EdgeRecord(1, 1, 2, "green"),
                      oracle.EdgeRecord(2, 2, 3, "red"),
                      oracle.EdgeRecord(3, 0, 3, "green"),
                      oracle.EdgeRecord(6, 4, 5, "red"),
                      oracle.EdgeRecord(8, 0, 4, "blue"),
                      oracle.EdgeRecord(9, 1, 5, "blue")),
        after_edges=(oracle.EdgeRecord(2, 2, 3, "green"),
                     oracle.EdgeRecord(6, 4, 5, "blue"),
                     oracle.EdgeRecord(12, 3, 4, "red"),
                     oracle.EdgeRecord(13, 2, 5, "red")),
        before_faces=(
            oracle.FaceRecord(0, 0, ((0, 1, 0), (1, 2, 1), (2, 3, 2), (3, 0, 3))),
            oracle.FaceRecord(2, 2, ((1, 0, 0), (0, 4, 8), (4, 5, 6), (5, 1, 9))),
            oracle.FaceRecord(3, 3, ((2, 1, 1), (1, 5, 9), (5, 6, 5), (6, 2, 10))),
            oracle.FaceRecord(5, 5, ((0, 3, 3), (3, 7, 11), (7, 4, 7), (4, 0, 8))),
        ),
        after_faces=(oracle.FaceRecord(3, 1, ((2, 5, 13), (5, 6, 5), (6, 2, 10))),
                     oracle.FaceRecord(5, 3, ((4, 3, 12), (3, 7, 11), (7, 4, 7))),
                     oracle.FaceRecord(6, 4, ((3, 4, 12), (4, 5, 6), (5, 2, 13), (2, 3, 2)))),
        before_next_ids=(12, 6), after_next_ids=(14, 7),
        before_fingerprint=oracle.state_fingerprint(before),
        after_fingerprint=oracle.state_fingerprint(after),
        swaps=(oracle.ColorSwap(("red", "blue"), ((0, 1, 0), (1, 5, 9), (5, 4, 6), (4, 0, 8)), "cycle"),
               oracle.ColorSwap(("green", "red"), ((0, 3, 3), (3, 2, 2), (2, 1, 1)), "path")),
    )
    return before, witness, after


def test_witness_f4_replays_ordered_swaps_and_unchanged_face_ids(oracle, f4_certificate):
    state, witness, expected = f4_certificate
    before = snapshot_state(state)
    oracle.apply_step(state, witness)
    assert snapshot_state(state) == snapshot_state(expected)
    assert state.graph[4][5][6]["color"] == "blue"  # Same ID, new color, outside F4.
    assert state.face_ids[0] == 1 and state.face_edge_ids[1] == [4, 5, 6, 7]
    oracle.undo_step(state, witness)
    assert snapshot_state(state) == before
    oracle.assert_state_invariants(state)


@pytest.mark.parametrize("change", ["omit_cycle", "reverse_order", "reverse_cycle_dart"])
def test_witness_rejects_wrong_preliminary_swap(oracle, f4_certificate, change):
    state, witness, _ = f4_certificate
    cycle, path = witness.swaps
    if change == "omit_cycle":
        swaps = (path,)
    elif change == "reverse_order":
        swaps = (path, cycle)
    else:
        swaps = (replace(cycle, darts=((1, 0, 0),) + cycle.darts[1:]), path)
    before = snapshot_state(state)
    with pytest.raises(ValueError, match="swap"):
        oracle.apply_step(state, replace(witness, swaps=swaps))
    assert snapshot_state(state) == before


def test_witness_binds_remote_colors_not_just_local_patch(oracle, f4_certificate):
    state, witness, _ = f4_certificate
    # A valid global permutation keeps all counts but is a different oracle state.
    for _, _, data in state.graph.edges(data=True):
        data["color"] = {"red": "green", "green": "blue", "blue": "red"}[data["color"]]
    oracle.assert_state_invariants(state)
    before = snapshot_state(state)
    with pytest.raises(ValueError, match="precondition"):
        oracle.apply_step(state, witness)
    assert snapshot_state(state) == before


@pytest.mark.parametrize("counter", ["next_edge_id", "next_face_id"])
def test_witness_rejects_fractional_allocator_atomically(oracle, f2_certificate, counter):
    state, witness, expected = f2_certificate
    setattr(expected, counter, getattr(expected, counter) + 0.5)
    invalid = replace(witness,
                      after_next_ids=(expected.next_edge_id, expected.next_face_id),
                      after_fingerprint=oracle.state_fingerprint(expected))
    before = snapshot_state(state)
    graph, faces, index = state.graph, state.g_faces, state.face_index
    with pytest.raises(AssertionError, match="allocator"):
        oracle.apply_step(state, invalid)
    assert snapshot_state(state) == before
    assert state.graph is graph and state.g_faces is faces and state.face_index is index


SUPPORTED_CASES = ("f2", "f3", "f4_three_colors", "f4_two_colors", "f4_same_cycle", "f5")


@pytest.mark.parametrize("renamed", permutations(("red", "green", "blue")))
@pytest.mark.parametrize("name", SUPPORTED_CASES)
def test_each_supported_family_reduces_and_replays(oracle, colored_cases, name, renamed):
    # A wrong fusion, omitted preliminary swap or lost occurrence must fail
    # against these hand-derived answers, even if undo repeats the same bug.
    case = colored_cases[name]
    colors = dict(zip(("red", "green", "blue"), renamed))
    faces = tuple(tuple((u, v, colors[c]) for u, v, c in face) for face in case["faces"])
    state = oracle.make_state(faces)
    fid = state.face_ids[case["face_index"]]
    candidate = oracle.Candidate(fid, state.face_edge_ids[fid][case["edge_index"]])
    before = snapshot_state(state)
    references = (state.graph, state.g_faces, state.face_index)
    n, m, f = len(state.graph), state.graph.number_of_edges(), len(state.g_faces)
    attempt = oracle.plan_step(state, candidate)
    assert snapshot_state(state) == before
    assert all(current is original for current, original in
               zip((state.graph, state.g_faces, state.face_index), references))
    assert attempt.status == "certified", attempt.reason
    witness = attempt.witness
    assert witness.candidate == candidate
    assert oracle.plan_step(state, candidate) == attempt  # Deterministic, read-only planning.
    if name == "f2":
        expected = ((2, 3, "red"), (2, 3, "green"), (2, 3, "blue"))
        assert witness.ariadne == (2, 0, 1, 2, 3)
        assert witness.swaps == ()
    elif name == "f5":
        expected = ((0, 1, "green"), (0, 4, "blue"), (5, 6, "blue"),
                    (6, 7, "green"), (7, 8, "red"), (8, 9, "blue"),
                    (5, 9, "green"), (0, 5, "red"), (1, 6, "red"),
                    (4, 9, "red"), (1, 7, "blue"), (4, 8, "green"))
        assert witness.ariadne == (5, 2, 3, 1, 4, 7, 8)
        assert [swap.kind for swap in witness.swaps] == ["path"]
    else:
        expected = WORKED_STEPS[name]["expected"]
        assert witness.ariadne == tuple(WORKED_STEPS[name]["ariadne"])
        assert [swap.kind for swap in witness.swaps] == (
            ["cycle", "path"] if name == "f4_two_colors" else ["path"])
    oracle.apply_step(state, witness)
    assert (len(state.graph), state.graph.number_of_edges(), len(state.g_faces)) == (n - 2, m - 3, f - 1)
    assert colored_multiset(state.graph) == Counter((min(a, b), max(a, b), colors[c])
                                                   for a, b, c in expected)
    oracle.assert_state_invariants(state)
    assert state.face_index.validate()
    oracle.undo_step(state, witness)
    assert snapshot_state(state) == before
    oracle.assert_state_invariants(state)


@pytest.mark.parametrize("selection,status", [
    ("theta", "unsupported_case"), ("unknown_face", "structurally_rejected"),
    ("unknown_edge", "structurally_rejected"), ("nonincident", "structurally_rejected"),
    ("parallel_endpoint", "structurally_rejected"), ("large_face", "unsupported_case"),
])
def test_rejected_attempt_is_read_only(oracle, colored_cases, selection, status):
    # Refusing an invalid/local-degenerate choice must not update any object.
    faces = colored_cases["theta" if selection == "theta" else "f2"]["faces"]
    if selection == "large_face":
        faces = prism_faces(("red", "green") * 3, ("red", "green") * 3, ("blue",) * 6)
    state = oracle.make_state(faces)
    candidate = oracle.Candidate(0, state.face_edge_ids[0][0])
    if selection == "unknown_face":
        candidate = oracle.Candidate(999, 0)
    elif selection == "unknown_edge":
        candidate = oracle.Candidate(0, 999)
    elif selection == "nonincident":
        candidate = oracle.Candidate(0, state.face_edge_ids[1][0])
    elif selection == "parallel_endpoint":
        candidate = oracle.Candidate(2, state.face_edge_ids[2][1])  # Would create two loops.
    before = snapshot_state(state)
    graph, faces, index = state.graph, state.g_faces, state.face_index
    attempt = oracle.plan_step(state, candidate)
    assert attempt.status == status
    assert attempt.witness is None and attempt.reason
    assert snapshot_state(state) == before
    assert state.graph is graph and state.g_faces is faces and state.face_index is index
    oracle.assert_state_invariants(state)


def test_unavailable_witness_is_not_impossibility(oracle, colored_cases):
    case = colored_cases["f5_no_direct_witness"]
    state = oracle.make_state(case["faces"])
    candidate = oracle.Candidate(0, state.face_edge_ids[0][0])
    before = snapshot_state(state)
    attempt = oracle.plan_step(state, candidate)
    assert attempt.status == "no_witness"
    assert attempt.witness is None and attempt.reason
    assert snapshot_state(state) == before
    # A different side of the same face is certifiable; no silent substitution.
    supported = oracle.Candidate(0, state.face_edge_ids[0][2])
    alternative = oracle.plan_step(state, supported)
    assert alternative.status == "certified"
    assert alternative.witness.candidate == supported


def test_parallel_path_uses_edge_ids(oracle, colored_cases):
    # Replace red edge 4--7 by a red/digon/red chain. The red/blue
    # partial path must cross only the BLUE 8--9 edge, preserving GREEN.
    faces = []
    for face in colored_cases["f4_same_cycle"]["faces"]:
        expanded = []
        for dart in face:
            if dart == (4, 7, "red"):
                expanded.extend(((4, 8, "red"), (8, 9, "blue"), (9, 7, "red")))
            elif dart == (7, 4, "red"):
                expanded.extend(((7, 9, "red"), (9, 8, "green"), (8, 4, "red")))
            else:
                expanded.append(dart)
        faces.append(expanded)
    faces.append([(8, 9, "green"), (9, 8, "blue")])
    state = oracle.make_state(faces)
    oracle.assert_state_invariants(state)
    before = snapshot_state(state)
    parallel = {data["color"]: eid for eid, data in state.graph[8][9].items()}
    candidate = oracle.Candidate(0, state.face_edge_ids[0][1])
    attempt = oracle.plan_step(state, candidate)
    assert attempt.status == "certified", attempt.reason
    traversed = {eid for swap in attempt.witness.swaps for _, _, eid in swap.darts}
    assert parallel["blue"] in traversed and parallel["green"] not in traversed
    assert snapshot_state(state) == before
    oracle.apply_step(state, attempt.witness)
    assert state.graph[8][9][parallel["blue"]]["color"] == "red"
    assert state.graph[8][9][parallel["green"]]["color"] == "green"
    oracle.assert_state_invariants(state)
    oracle.undo_step(state, attempt.witness)
    assert snapshot_state(state) == before


@pytest.mark.parametrize("name", ["f2", "f3"])
def test_coincident_neighbors_keep_face_index_consistent(oracle, colored_cases, name):
    # F2 updates the same third face twice; F3 has coincident external
    # neighbors. Both produce three equal-by-value faces with distinct IDs.
    state = oracle.make_state(colored_cases[name]["faces"])
    before = snapshot_state(state)
    untouched = set(state.face_ids) - {0}
    attempt = oracle.plan_step(state, oracle.Candidate(0, state.face_edge_ids[0][0]))
    assert attempt.status == "certified", attempt.reason
    oracle.apply_step(state, attempt.witness)
    assert len(state.face_ids) == len(set(state.face_ids)) == 3
    assert len({frozenset(face) for face in state.g_faces}) == 1
    assert len(set(state.face_ids) & untouched) == 2
    assert state.face_index.validate()
    oracle.assert_state_invariants(state)
    oracle.undo_step(state, attempt.witness)
    assert snapshot_state(state) == before
    assert state.face_index.validate()


@pytest.mark.parametrize("name", CASE_NAMES)
@pytest.mark.parametrize("renamed", list(permutations(("red", "green", "blue"))))
def test_small_chain_reaches_theta_and_replays(oracle, colored_cases, name, renamed):
    colors = dict(zip(("red", "green", "blue"), renamed))
    faces = [[(u, v, colors[c]) for u, v, c in face] for face in colored_cases[name]["faces"]]
    state = oracle.make_state(faces)
    before = snapshot_state(state)
    steps = (len(state.graph) - 2) // 2
    result = oracle.run_chain(state, steps)
    assert result.status == "theta_reached"
    assert len(result.witnesses) == steps
    assert (len(state.graph), state.graph.number_of_edges(), len(state.g_faces)) == (2, 3, 3)
    assert sum(result.family_counts.values()) == steps
    assert result.swap_counts == dict(Counter(s.kind for w in result.witnesses for s in w.swaps))
    terminal = snapshot_state(state)
    restored = oracle.replay_exact(state, result.witnesses)
    assert snapshot_state(restored) == before
    assert snapshot_state(state) == terminal
    assert restored.graph is not state.graph
    oracle.assert_state_invariants(restored)


@pytest.mark.parametrize("limit", [0, 1, 2])
def test_step_limit_is_inconclusive(oracle, colored_cases, limit):
    state = oracle.make_state(colored_cases["f4_two_colors"]["faces"])
    before = snapshot_state(state)
    result = oracle.run_chain(state, limit)
    assert result.status == "step_limit"
    assert len(result.witnesses) == limit
    assert snapshot_state(oracle.replay_exact(state, result.witnesses)) == before


@pytest.mark.parametrize("limit", [-1, 1.5, True])
def test_chain_rejects_invalid_limit_before_mutation(oracle, colored_cases, limit):
    state = oracle.make_state(colored_cases["f3"]["faces"])
    before = snapshot_state(state)
    with pytest.raises(ValueError):
        oracle.run_chain(state, limit)
    assert snapshot_state(state) == before


def test_candidate_policy_orders_families_ids_and_unique_f5_color(oracle, colored_cases):
    state = oracle.make_state(colored_cases["f5"]["faces"])
    candidates = list(oracle.ordered_candidates(state))
    assert candidates[:4] == [oracle.Candidate(2, eid) for eid in sorted(state.face_edge_ids[2])]
    assert [c.edge_id for c in candidates if c.face_id == 0] == [2, 0, 1, 3, 4]
    state.g_faces.reverse()
    state.face_ids.reverse()
    state.face_index = oracle._fourct.FaceIndex(state.g_faces)
    assert list(oracle.ordered_candidates(state)) == candidates


def test_no_certified_candidate_is_inconclusive(oracle, colored_cases, monkeypatch):
    state = oracle.make_state(colored_cases["f3"]["faces"])
    before = snapshot_state(state)
    # No real all-candidate obstruction is known: inject only the planner outcome.
    monkeypatch.setattr(oracle, "plan_step", lambda state, candidate:
                        oracle.StepAttempt("no_witness", "Injected unavailable construction"))
    result = oracle.run_chain(state, 5)
    assert result.status == "no_certified_candidate"
    assert result.witnesses == []
    assert len(result.rejections) == 12
    assert all(r.status == "no_witness" and r.reason for r in result.rejections)
    assert snapshot_state(state) == before


def test_chain_tries_next_candidate_and_propagates_invariant_errors(oracle, colored_cases, monkeypatch):
    state = oracle.make_state(colored_cases["f4_two_colors"]["faces"])
    planner = oracle.plan_step
    def reject_first(current, candidate):
        if candidate == oracle.Candidate(0, 0):
            return oracle.StepAttempt("no_witness", "Injected unavailable first choice")
        return planner(current, candidate)
    monkeypatch.setattr(oracle, "plan_step", reject_first)
    result = oracle.run_chain(state, 1)
    assert result.witnesses[0].candidate == oracle.Candidate(0, 1)
    state.next_edge_id = -1
    with pytest.raises(AssertionError):
        oracle.run_chain(state, 1)


@pytest.fixture
def runner():
    return importlib.import_module("experiments.oracle_reduction_run")


@pytest.mark.parametrize("name,limit", [("theta", 0), ("f2", 1), ("f4_two_colors", 3), ("f5", 1)])
def test_json_roundtrip_preserves_ids_and_colors(oracle, runner, colored_cases, tmp_path, name, limit):
    colors = {"red": "green", "green": "blue", "blue": "red"}
    faces = [[(u, v, colors[c]) for u, v, c in f] for f in colored_cases[name]["faces"]]
    state = oracle.make_state(faces)
    before = snapshot_state(state)
    result = oracle.run_chain(state, limit)
    provenance = {"source": {"map_number": 1}, "configuration": {"max_steps": limit}}
    runner.save_run(tmp_path / "run", state, result, provenance)
    terminal, loaded, origin = runner.load_run(tmp_path / "run")
    assert loaded == result and origin == provenance
    assert snapshot_state(terminal) == snapshot_state(state)
    assert snapshot_state(oracle.replay_exact(terminal, loaded.witnesses)) == before
    terminal.face_index.validate()
    assert terminal.face_index.g_faces is terminal.g_faces


def test_existing_run_directory_is_not_overwritten(oracle, runner, colored_cases, tmp_path):
    state = oracle.make_state(colored_cases["f2"]["faces"])
    result = oracle.run_chain(state, 1)
    directory = tmp_path / "existing-run"
    directory.mkdir()
    (directory / "sentinel").write_bytes(b"preserve me")
    with pytest.raises(FileExistsError):
        runner.save_run(directory, state, result, {})
    assert {p.name: p.read_bytes() for p in directory.iterdir()} == {"sentinel": b"preserve me"}


@pytest.mark.parametrize("corruption", ["schema", "missing", "truncated", "terminal", "status"])
def test_json_loader_rejects_incomplete_or_corrupt_run(oracle, runner, colored_cases, tmp_path, corruption):
    import json
    state = oracle.make_state(colored_cases["f4_two_colors"]["faces"])
    result = oracle.run_chain(state, 1)
    runner.save_run(tmp_path / "run", state, result, {})
    directory = tmp_path / "run"
    manifest_path = directory / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    if corruption == "schema":
        manifest["schema_version"] = 999
    elif corruption == "missing":
        (directory / "steps.jsonl").unlink()
    elif corruption == "truncated":
        (directory / "steps.jsonl").write_text("")
    elif corruption == "terminal":
        path = directory / "terminal.json"
        path.write_text(path.read_text().replace('"red"', '"green"'))
    else:
        manifest["result"]["status"] = "theta_reached"
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises((ValueError, FileNotFoundError)):
        runner.load_run(directory)


@pytest.mark.parametrize("name", ["theta", "f2", "f3", "f4_two_colors", "f4_three_colors", "f5"])
def test_ordinary_rebuild_is_separate(oracle, runner, colored_cases, monkeypatch, name):
    from copy import deepcopy
    original = oracle.make_state(colored_cases[name]["faces"])
    state = oracle.make_state(colored_cases[name]["faces"])
    result = oracle.run_chain(state, 10)
    before, certificates = snapshot_state(state), deepcopy(result)
    real_rebuild = runner._fourct.rebuild_faces
    def structural_rebuild(faces, stack, *, kempe_search_limit):
        assert all(len(edge) == 2 for face in faces for edge in face)
        assert faces is not state.g_faces and kempe_search_limit == 7
        graph = real_rebuild(faces, stack, kempe_search_limit=kempe_search_limit)
        assert stack == []
        return graph
    monkeypatch.setattr(runner._fourct, "rebuild_faces", structural_rebuild)
    ordinary = runner.ordinary_rebuild(state, result, original, 7)
    assert ordinary["status"] == "success"
    assert ordinary["topology_matches"] and ordinary["well_colored"]
    assert ordinary["kempe_search_limit"] == 7
    assert snapshot_state(state) == before and result == certificates
    assert snapshot_state(oracle.replay_exact(state, result.witnesses)) == snapshot_state(original)
    def forbidden(*args, **kwargs):
        pytest.fail("Nonterminal prefix must not call rebuild_faces")
    monkeypatch.setattr(runner._fourct, "rebuild_faces", forbidden)
    partial = oracle.make_state(colored_cases["f4_two_colors"]["faces"])
    prefix = oracle.run_chain(partial, 1)
    assert runner.ordinary_rebuild(partial, prefix, original, 7)["status"] == "not_run_nonterminal"


def test_ordinary_rebuild_distinguishes_search_stop_from_software_error(oracle, runner, colored_cases, monkeypatch):
    from ct_graph_utils import KempeSearchExhausted
    original = oracle.make_state(colored_cases["f3"]["faces"])
    state = oracle.make_state(colored_cases["f3"]["faces"])
    result = oracle.run_chain(state, 1)
    def exhausted(*args, **kwargs):
        raise KempeSearchExhausted("Injected budget exhaustion")
    monkeypatch.setattr(runner._fourct, "rebuild_faces", exhausted)
    outcome = runner.ordinary_rebuild(state, result, original, 1)
    assert outcome["status"] == "search_exhausted" and outcome["reason"]
    def broken(*args, **kwargs):
        raise RuntimeError("Unexpected defect")
    monkeypatch.setattr(runner._fourct, "rebuild_faces", broken)
    with pytest.raises(RuntimeError, match="Unexpected defect"):
        runner.ordinary_rebuild(state, result, original, 1)


def test_cli_json_replay_in_fresh_process(
        oracle, runner, colored_cases, tmp_path, isolated_workdir):
    import hashlib
    import json
    import subprocess
    source = tmp_path / "small.colored.planar"
    raw = (json.dumps(colored_cases["f4_two_colors"]["faces"]) + "\n").encode()
    source.write_bytes(b"unselected line is not JSON\n" + raw + b"unselected line is not JSON\n")
    original_bytes = source.read_bytes()
    output = tmp_path / "run"
    command = [sys.executable, str(CT / "experiments/oracle_reduction_run.py")]
    first = subprocess.run(command + ["--input", str(source), "--map-number", "2", "--max-steps", "3",
                           "--output", str(output), "--ordinary-rebuild", "--kempe-search-limit", "7"],
                           cwd=isolated_workdir, capture_output=True, text=True)
    assert first.returncode == 0, first.stderr
    terminal, result, provenance = runner.load_run(output)
    assert result.status == "theta_reached"
    assert provenance["source"]["map_number"] == 2
    assert provenance["source"]["line_sha256"] == hashlib.sha256(raw).hexdigest()
    assert provenance["ordinary"]["status"] == "success"
    assert provenance["code_sha256"] and provenance["git_revision"]
    second = subprocess.run(command + ["--replay", str(output)],
                            cwd=isolated_workdir, capture_output=True, text=True)
    assert second.returncode == 0, second.stderr
    report = json.loads(second.stdout)
    assert report["exact_replay"] and report["edge_multiset_matches"] and report["source_matches"]
    assert source.read_bytes() == original_bytes
    restored = oracle.replay_exact(terminal, result.witnesses)
    assert snapshot_state(restored) == snapshot_state(oracle.make_state(colored_cases["f4_two_colors"]["faces"]))
    source.write_bytes(original_bytes.replace(b'"red"', b'"blue"'))
    changed = subprocess.run(command + ["--replay", str(output)],
                             cwd=isolated_workdir, capture_output=True, text=True)
    assert changed.returncode != 0 and "SHA-256" in changed.stderr


@pytest.mark.parametrize("args", [[], ["--max-steps", "-1"], ["--map-number", "0"],
                                  ["--kempe-search-limit", "0"], ["--replay", "x", "--max-steps", "0"],
                                  ["--replay", "x", "--input", "y"]])
def test_cli_rejects_invalid_modes_and_limits(runner, args):
    with pytest.raises(SystemExit) as error:
        runner.main(args)
    assert error.value.code == 2


def test_dodecahedron_chain_includes_f5_and_replays_json(oracle, runner, tmp_path):
    import json
    faces = json.loads((CT / "examples/planar/oracle-study-dodecahedron.colored.planar").read_text())
    original = oracle.make_state(faces)
    assert (len(original.graph), original.graph.number_of_edges(), len(faces)) == (20, 30, 12)
    assert {len(face) for face in faces} == {5}
    terminal = oracle.make_state(faces)
    result = oracle.run_chain(terminal, 9)
    assert result.status == "theta_reached" and len(result.witnesses) == 9
    assert result.witnesses[0].ariadne[0] == 5
    assert result.witnesses[0].candidate.face_id == 0
    selected = result.witnesses[0].candidate.edge_id
    u, v = original.edge_endpoints[selected]
    color = original.graph[u][v][selected]["color"]
    assert sum(c == color for _, _, c in faces[0]) == 1
    runner.save_run(tmp_path / "dodecahedron", terminal, result, {})
    loaded, chain, _ = runner.load_run(tmp_path / "dodecahedron")
    assert snapshot_state(oracle.replay_exact(loaded, chain.witnesses)) == snapshot_state(original)
    assert runner.ordinary_rebuild(loaded, chain, original, 100)["status"] == "success"


def test_failed_replay_does_not_mutate_terminal_or_witnesses(oracle, colored_cases):
    from copy import deepcopy
    state = oracle.make_state(colored_cases["f4_two_colors"]["faces"])
    result = oracle.run_chain(state, 3)
    before, witnesses = snapshot_state(state), deepcopy(result.witnesses)
    with pytest.raises(ValueError):
        oracle.replay_exact(state, list(reversed(result.witnesses)))
    assert snapshot_state(state) == before and result.witnesses == witnesses
