"""S5: positive corners guide reduction; reconstruction never samples RNG."""
import collections
import copy
import importlib.util
import json
from pathlib import Path
import sys
import subprocess

import networkx as nx
import pytest


CT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CT))


@pytest.fixture
def mod():
    spec = importlib.util.spec_from_file_location("fourct_s5", CT / "4ct.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.stats = {}
    module.initialize_statistics()
    return module


def embedding(graph):
    planar, rotation = nx.check_planarity(graph)
    assert planar
    seen = set()
    faces = []
    for u, v in rotation.edges():
        if (u, v) not in seen:
            vertices = rotation.traverse_face(u, v, seen)
            faces.append(list(zip(vertices, vertices[1:] + vertices[:1])))
    return faces


def edge_multiset(graph):
    return collections.Counter(tuple(sorted((u, v))) for u, v in graph.edges())


def forbid_random(*args, **kwargs):
    pytest.fail("S5 attempted a random choice")


@pytest.mark.parametrize("sizes,positive", [
    ((5, 5, 5), True), ((5, 5, 6), True), ((5, 5, 7), True),
    ((5, 5, 8), True), ((5, 5, 9), True), ((5, 6, 6), True),
    ((5, 6, 7), True), ((5, 5, 10), False), ((5, 6, 8), False),
    ((6, 6, 6), False), ((4, 6, 6), False),
])
def test_positive_corner_classification(mod, sizes, positive):
    # Three distinct faces incident at 0; only their lengths matter here.
    faces = []
    for i, size in enumerate(sizes):
        vertices = [0] + list(range(100 * (i + 1), 100 * (i + 1) + size - 1))
        faces.append(list(zip(vertices, vertices[1:] + vertices[:1])))
    corners = mod.positive_corners(mod.FaceIndex(faces))
    assert (0 in corners) == positive
    if positive:
        assert corners[0] == sizes


def test_s5_selection_is_read_only_and_uses_positive_corner(mod, monkeypatch):
    faces = embedding(nx.dodecahedral_graph())
    original = copy.deepcopy(faces)
    index = mod.FaceIndex(faces)
    frontier = {0, 1}
    monkeypatch.setattr(mod, "randint", forbid_random)
    edge, f1, f2, merged, event = mod.select_edge_to_remove_positive_corner(
        faces, 2345, 0, frontier, index)
    assert len(f1) == 5
    assert any(v in mod.positive_corners(index) for v, _ in f1)
    assert edge in f1 and tuple(reversed(edge)) in f2
    assert not mod.is_the_graph_one_edge_connected(merged)
    assert event is None
    assert faces == original and frontier == {0, 1}
    assert index.validate()


@pytest.mark.parametrize("graph", [nx.tetrahedral_graph(), nx.cubical_graph(), nx.dodecahedral_graph()])
def test_s5_rebuild_preserves_topology_without_randomness(mod, monkeypatch, graph):
    monkeypatch.setattr(mod, "randint", forbid_random)
    monkeypatch.setattr(mod, "graph_random_edge", forbid_random)
    faces = embedding(graph)
    mod.init_f_distribution(faces)
    thread = mod.reduce_faces(faces, 2345, mod.select_edge_to_remove_positive_corner)
    rebuilt = mod.rebuild_faces(faces, thread, kempe_search_limit=1000)
    assert not thread
    assert mod.is_well_colored(rebuilt)
    assert edge_multiset(rebuilt) == edge_multiset(graph)
    assert mod.stats["TOTAL_RANDOM_KEMPE_SWITCHES"] == 0


def colored_prism():
    graph = nx.MultiGraph()
    for offset in (0, 4):
        for i in range(4):
            graph.add_edge(offset + i, offset + (i + 1) % 4,
                           color="red" if i % 2 == 0 else "green")
    for i in range(4):
        graph.add_edge(i, i + 4, color="blue")
    return graph


def test_deterministic_search_repairs_separated_cycles(mod):
    graph = colored_prism()
    original = copy.deepcopy(graph)
    assert not mod.are_edges_on_the_same_kempe_cycle(graph, (0, 1), (5, 6), "red", "green")
    switches, colors, pair, states = mod.find_kempe_repair(graph, (0, 1), (5, 6), 1000)
    assert switches and states > 1
    assert nx.utils.graphs_equal(graph, original), "Search must not mutate its input"
    for c1, c2, cycle in switches:
        for u, v, key in cycle:
            old = graph[u][v][key]["color"]
            graph[u][v][key]["color"] = c2 if old == c1 else c1
        assert mod.is_well_colored(graph)
    assert mod.are_edges_on_the_same_kempe_cycle(graph, (0, 1), (5, 6), *pair)
    assert colors == (mod.get_edge_color(graph, (0, 1)), mod.get_edge_color(graph, (5, 6)))


def test_search_budget_is_reported_without_mutating_graph(mod):
    graph = colored_prism()
    original = copy.deepcopy(graph)
    with pytest.raises(mod.KempeSearchExhausted, match="budget"):
        mod.find_kempe_repair(graph, (0, 1), (5, 6), 1)
    assert nx.utils.graphs_equal(graph, original)


def test_search_retains_parallel_edge_identity(mod):
    graph = nx.MultiGraph()
    for color in ("red", "green", "blue"):
        graph.add_edge(0, 1, color=color)
        graph.add_edge(2, 3, color=color)
    # Different connected components can never be joined by cycle switches.
    # All 36 labelled colorings must be exhausted, not just their boundary words.
    with pytest.raises(mod.KempeSearchExhausted, match="exhausted.*36"):
        mod.find_kempe_repair(graph, (0, 1), (2, 3), 100)
    assert mod.is_well_colored(graph)


def test_s5_cli_rebuilds_map(tmp_path):
    planar = tmp_path / "dodecahedron.planar"
    planar.write_text(json.dumps(embedding(nx.dodecahedral_graph())) + "\n")
    result = subprocess.run(
        [sys.executable, "4ct.py", "-s5", "-p", str(planar)],
        cwd=CT, text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Stats: TOTAL_RANDOM_KEMPE_SWITCHES = 0" in result.stdout
    assert "ERROR" not in result.stdout


@pytest.mark.parametrize("face,expected", [
    ([(0, 1), (1, 0)], False),
    ([(0, 1), (1, 2), (2, 0)], False),
    ([(7, 6), (6, 1), (1, 2), (2, 4), (4, 3), (3, 2), (2, 1), (1, 5), (5, 7)], True),
])
def test_bridge_check_preserves_digon_exception(mod, face, expected):
    assert mod.is_the_graph_one_edge_connected(face) is expected


def test_search_checks_queued_states_before_reporting_budget(mod):
    graph = colored_prism()
    switches, _, _, examined = mod.find_kempe_repair(graph, (0, 1), (5, 6), 2)
    assert len(switches) == 1 and examined == 2
