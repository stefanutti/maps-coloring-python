"""S6: grow an even principal face by merging it with adjacent even faces."""
import collections
import copy
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys

import networkx as nx
import pytest


CT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CT))


@pytest.fixture
def mod():
    spec = importlib.util.spec_from_file_location("fourct_s6", CT / "4ct.py")
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
    pytest.fail("S6 attempted a random choice")


def rebuild_s6(mod, faces, thread, perimeters=None):
    return mod.rebuild_faces(faces, thread, kempe_search_limit=10000, perimeters=perimeters,
                             restore_step=mod.restore_ariadne_step_s6)


def random_faces(mod, number_of_faces, seed):
    random.seed(seed)
    _, faces = mod.create_from_random2(number_of_faces, False)
    return faces


def simulated_even_neighbor(mod, faces, f1_position, edge):
    """Apply the reduction on a copy and inspect the merged face's neighbors."""
    faces = copy.deepcopy(faces)
    f1 = faces[f1_position]
    f2 = next(face for face in faces if face is not f1 and tuple(reversed(edge)) in face)
    merged = mod.join_faces(f1, f2, edge)
    others = [face for face in faces if face is not f1 and face is not f2]
    for face in others:
        for vertex in edge:
            if any(vertex == u for u, _ in face):
                mod.remove_vertex_from_face(face, vertex)
    merged_edges = {tuple(reversed(e)) for e in merged}
    return any(len(face) % 2 == 0 for face in others if merged_edges & set(face))


@pytest.mark.parametrize("graph", [nx.cubical_graph(), nx.dodecahedral_graph(),
                                   nx.truncated_tetrahedron_graph(), nx.truncated_cube_graph()])
def test_even_neighbor_matches_simulated_reduction(mod, graph):
    faces = embedding(graph)
    index = mod.FaceIndex(faces)
    checked = 0
    for position, f1 in enumerate(faces):
        for edge in f1:
            f2 = index.first_face_with_edge(tuple(reversed(edge)), exclude_face=f1)
            if mod.is_the_graph_one_edge_connected(mod.join_faces(f1, f2, edge)):
                continue
            expected = simulated_even_neighbor(mod, faces, position, edge)
            assert mod._even_neighbor_after_merge(f1, f2, edge, index) is expected
            checked += 1
    assert checked > 0
    assert index.validate()


def test_s6_selection_contract_and_read_only(mod):
    faces = embedding(nx.cubical_graph())
    original = copy.deepcopy(faces)
    index = mod.FaceIndex(faces)
    frontier = {0, 1}
    edge, f1, f2, merged, event = mod.select_edge_to_remove_even_faces(faces, 2345, 0, frontier, index)
    assert 2 <= len(f1) <= len(f2)
    assert edge in f1 and tuple(reversed(edge)) in f2
    assert merged == mod.join_faces(f1, f2, edge)
    assert len(merged) % 2 == 0
    assert mod._even_neighbor_after_merge(f1, f2, edge, index)
    assert not mod.is_the_graph_one_edge_connected(merged)
    assert event is None
    assert mod.stats['SELECT-S6-START'] == 1
    assert mod.s6_principal_face is merged
    assert faces == original and frontier == {0, 1}
    assert index.validate()


def test_s6_resets_principal_face_at_the_start_of_each_execution(mod):
    faces = embedding(nx.cubical_graph())
    mod.s6_principal_face = faces[0]
    mod.select_edge_to_remove_even_faces(faces, 2345, 0, None, mod.FaceIndex(faces))
    assert mod.stats['SELECT-S6-CONTINUE'] == 0
    assert mod.stats['SELECT-S6-START'] == 1


def spy_reduction(mod, faces):
    """Run reduce_faces() with S6 and check the rule each selection applied."""
    observed = collections.Counter()

    def spy(g_faces, choices, i_global_counter, frontier, face_index):
        had_f2 = bool(face_index.faces_of_size(2))
        principal = mod.s6_principal_face
        before = dict(mod.stats)
        edge, f1, f2, merged, event = mod.select_edge_to_remove_even_faces(
            g_faces, choices, i_global_counter, frontier, face_index)
        (stat,) = [key for key in before if key.startswith('SELECT-S6-') and mod.stats[key] != before[key]]
        observed[stat] += 1
        assert event is None
        # f1, the face recorded by Ariadne, is the smaller face and has at most five sides
        assert 2 <= len(f1) <= min(len(f2), mod.S6_MAX_REDUCED_FACE)
        assert not mod.is_the_graph_one_edge_connected(merged)
        assert (len(f1) == 2) == had_f2
        assert (stat == 'SELECT-S6-F2') == had_f2
        if stat in ('SELECT-S6-CONTINUE', 'SELECT-S6-START'):
            assert len(merged) % 2 == 0
            assert mod._even_neighbor_after_merge(f1, f2, edge, face_index)
        if stat == 'SELECT-S6-CONTINUE':
            assert principal is f1 or principal is f2
            assert len(f1) % 2 == 0 and len(f2) % 2 == 0
        return edge, f1, f2, merged, event

    mod.init_f_distribution(faces)
    thread = mod.reduce_faces(faces, 2345, spy)
    return thread, observed


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_s6_rules_hold_on_random_maps(mod, seed):
    faces = random_faces(mod, 150, seed)
    thread, observed = spy_reduction(mod, faces)
    assert len(faces) == 3
    assert sum(observed.values()) == len(thread)
    assert observed['SELECT-S6-CONTINUE'] > 0


@pytest.mark.parametrize("graph", [nx.tetrahedral_graph(), nx.cubical_graph(), nx.dodecahedral_graph(),
                                   nx.truncated_cube_graph()])
def test_s6_rebuild_preserves_topology(mod, monkeypatch, graph):
    monkeypatch.setattr(mod, "randint", forbid_random)
    monkeypatch.setattr(mod, "graph_random_edge", forbid_random)
    faces = embedding(graph)
    thread, _ = spy_reduction(mod, faces)
    rebuilt = rebuild_s6(mod, faces, thread)
    assert not thread
    assert mod.is_well_colored(rebuilt)
    assert edge_multiset(rebuilt) == edge_multiset(graph)


def test_s6_rebuilds_random_maps_deterministically(mod, monkeypatch):
    monkeypatch.setattr(mod, "randint", forbid_random)
    monkeypatch.setattr(mod, "graph_random_edge", forbid_random)
    largest_record = 0
    for seed in (11, 12, 13, 14, 15):  # several maps, so that F5 records appear
        random.seed(seed)
        _, faces = mod.create_from_random2(200, False)
        graph = mod.create_graph_from_planar_representation(faces)
        mod.initialize_statistics()
        mod.init_f_distribution(faces)
        thread = mod.reduce_faces(faces, 2345, mod.select_edge_to_remove_even_faces)
        largest_record = max(largest_record, max(step[0] for step in thread))
        rebuilt = rebuild_s6(mod, faces, thread)
        assert mod.is_well_colored(rebuilt)
        assert edge_multiset(rebuilt) == edge_multiset(graph)
        assert mod.stats['TOTAL_RANDOM_KEMPE_SWITCHES'] == 0
    assert largest_record == mod.S6_MAX_REDUCED_FACE


def test_classic_rebuild_rejects_records_without_a_handler(mod):
    theta = [[(0, 1), (1, 0)], [(0, 1), (1, 0)], [(0, 1), (1, 0)]]
    with pytest.raises(SystemExit):
        mod.rebuild_faces(theta, [[6, 10, 11, 0, 1, 1, 0]])


def test_common_kempe_cycle_returns_half_switch_arguments(mod):
    graph = colored_prism()
    assert mod._find_common_kempe_cycle(graph, (0, 1), (2, 3)) == (("red", "red"), ("red", "green"))
    # (0,1) red and (5,6) green: different red/green squares, and green is not on any red/blue cycle
    assert mod._find_common_kempe_cycle(graph, (0, 1), (5, 6)) is None


def test_any_face_handler_splits_a_face_with_one_half_switch(mod):
    graph = colored_prism()
    # Split the top face 0-1-2-3 with a chord from edge (0,1) to edge (3,2): f1 = 98-0-3-99, f2 = 99-2-1-98
    mod.ariadne_case_any_face(graph, [4, 98, 99, 0, 3, 1, 2], 100)
    assert mod.is_well_colored(graph)
    assert graph.number_of_nodes() == 10 and graph.number_of_edges() == 15
    assert all(degree == 3 for _, degree in graph.degree())
    assert mod.stats['S6-REBUILD-DIRECT'] == 1 and mod.stats['S6-REBUILD-SEARCHED'] == 0


def test_s6_reduction_is_deterministic(mod):
    threads = []
    for _ in range(2):
        faces = embedding(nx.truncated_cube_graph())
        mod.initialize_statistics()
        mod.init_f_distribution(faces)
        threads.append(mod.reduce_faces(faces, 2345, mod.select_edge_to_remove_even_faces))
    assert threads[0] == threads[1]


def test_s6_cli_rebuilds_map(tmp_path, isolated_workdir):
    planar = tmp_path / "dodecahedron.planar"
    planar.write_text(json.dumps(embedding(nx.dodecahedral_graph())) + "\n")
    result = subprocess.run(
        [sys.executable, str(CT / "4ct.py"), "-s6", "-p", str(planar)],
        cwd=isolated_workdir, text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Stats: SELECT-S6-START" in result.stdout
    assert "Stats: S6-MEASURE-STEPS = 0" not in result.stdout
    assert "Stats: TOTAL_RANDOM_KEMPE_SWITCHES = 0" in result.stdout
    assert "ERROR" not in result.stdout


def colored_prism():
    """Cube as a square prism: squares alternate red/green, verticals are blue."""
    graph = nx.MultiGraph()
    for offset in (0, 4):
        for i in range(4):
            graph.add_edge(offset + i, offset + (i + 1) % 4, color="red" if i % 2 == 0 else "green")
    for i in range(4):
        graph.add_edge(i, i + 4, color="blue")
    return graph


S6_MEASURES = ['S6-MEASURE-STEPS', 'S6-MEASURE-UNKNOWN', 'S6-MEASURE-M-EVEN', 'S6-MEASURE-M-EVEN-BICHROMATIC',
               'S6-MEASURE-M-EVEN-SAME-KEMPE', 'S6-MEASURE-M-ODD', 'S6-MEASURE-M-ODD-SAME-KEMPE'] + [
    'S6-MEASURE-%s-M-EVEN%s' % (size, suffix) for size in ('F3', 'F4', 'F5', 'F6+') for suffix in ('', '-SAME-KEMPE')]


def measures(mod):
    return {key: mod.stats[key] for key in S6_MEASURES}


@pytest.mark.parametrize("perimeter,step,expected", [
    # Top square, red/green: bichromatic, and (0,1), (2,3) are on its Kempe cycle.
    ([(0, 1), (1, 2), (2, 3), (3, 0)], [4, 98, 99, 0, 2, 1, 3],
     {'S6-MEASURE-STEPS': 1, 'S6-MEASURE-M-EVEN': 1, 'S6-MEASURE-M-EVEN-BICHROMATIC': 1,
      'S6-MEASURE-M-EVEN-SAME-KEMPE': 1, 'S6-MEASURE-F4-M-EVEN': 1, 'S6-MEASURE-F4-M-EVEN-SAME-KEMPE': 1}),
    # Even hexagon with three colors; (0,1) and (5,6) lie on different red/green squares.
    ([(0, 1), (1, 5), (5, 6), (6, 2), (2, 3), (3, 0)], [4, 98, 99, 0, 5, 1, 6],
     {'S6-MEASURE-STEPS': 1, 'S6-MEASURE-M-EVEN': 1, 'S6-MEASURE-F4-M-EVEN': 1}),
    # F2 records subdivide a single edge: not measured.
    ([(0, 1), (1, 2), (2, 3), (3, 0)], [2, 98, 99, 0, 1], {}),
])
def test_measure_s6_reinsertion_is_read_only(mod, perimeter, step, expected):
    graph = colored_prism()
    original = copy.deepcopy(graph)
    mod.measure_s6_reinsertion(graph, step, perimeter)
    assert measures(mod) == {key: expected.get(key, 0) for key in S6_MEASURES}
    assert nx.utils.graphs_equal(graph, original)


def test_measure_s6_reinsertion_marks_multiple_edges_unknown(mod):
    graph = nx.MultiGraph()
    for color in ("red", "green", "blue"):
        graph.add_edge(0, 1, color=color)
    mod.measure_s6_reinsertion(graph, [3, 98, 99, 0, 1, 1, 0], [(0, 1), (1, 0)])
    assert measures(mod) == {key: int(key in ('S6-MEASURE-STEPS', 'S6-MEASURE-UNKNOWN')) for key in S6_MEASURES}


def colored_edges(graph):
    return sorted((min(u, v), max(u, v), data["color"]) for u, v, data in graph.edges(data=True))


@pytest.mark.parametrize("seed", [21, 22, 23])
def test_s6_measurement_is_consistent_and_does_not_change_the_coloring(mod, seed):
    results = []
    for perimeters in (None, []):
        faces = random_faces(mod, 200, seed)
        mod.initialize_statistics()
        mod.init_f_distribution(faces)
        thread = mod.reduce_faces(faces, 2345, mod.select_edge_to_remove_even_faces, perimeters)
        non_f2_steps = sum(step[0] != 2 for step in thread)
        random.seed(seed)
        rebuilt = rebuild_s6(mod, faces, thread, perimeters)
        results.append(colored_edges(rebuilt))
    assert results[0] == results[1]
    assert perimeters == []
    counts = measures(mod)
    assert counts['S6-MEASURE-STEPS'] == non_f2_steps > 0
    assert counts['S6-MEASURE-M-EVEN'] + counts['S6-MEASURE-M-ODD'] + counts['S6-MEASURE-UNKNOWN'] == non_f2_steps
    assert counts['S6-MEASURE-M-EVEN-BICHROMATIC'] <= counts['S6-MEASURE-M-EVEN-SAME-KEMPE'] <= counts['S6-MEASURE-M-EVEN']
    assert counts['S6-MEASURE-M-ODD-SAME-KEMPE'] <= counts['S6-MEASURE-M-ODD']
    for suffix in ('', '-SAME-KEMPE'):
        assert sum(counts['S6-MEASURE-%s-M-EVEN%s' % (size, suffix)] for size in ('F3', 'F4', 'F5', 'F6+')) == \
            counts['S6-MEASURE-M-EVEN' + suffix]


def test_other_strategies_do_not_measure(mod):
    faces = embedding(nx.dodecahedral_graph())
    mod.init_f_distribution(faces)
    thread = mod.reduce_faces(faces, 2345, mod.select_edge_to_remove_first_fit)
    mod.rebuild_faces(faces, thread)
    assert all(value == 0 for value in measures(mod).values())



# Map 3 of maps_3000_maps_of_8000_faces.planar, 14th S6 reinsertion: the coloring built by the
# previous reinsertions lies in a Kempe class of 36 colorings, none of which allows the half switch
# (the other class of this graph has 96 good colorings out of 174).
MAP3_STEP = [5, 7970, 10318, 7960, 10989, 4718, 9023]
MAP3_EDGES = [
    (4718, 4993, 'r'), (4718, 7960, 'g'), (4718, 9546, 'b'), (4993, 5771, 'g'), (4993, 5855, 'b'), (5771, 7019, 'r'),
    (5771, 7960, 'b'), (5855, 9130, 'r'), (5855, 9393, 'g'), (7019, 9393, 'b'), (7019, 9764, 'g'), (7960, 10454, 'r'),
    (9023, 9546, 'g'), (9023, 10989, 'r'), (9023, 11537, 'b'), (9130, 9472, 'b'), (9130, 10439, 'g'), (9393, 10397, 'r'),
    (9472, 10397, 'g'), (9472, 10601, 'r'), (9546, 10439, 'r'), (9764, 10892, 'r'), (9764, 10967, 'b'), (10395, 10397, 'b'),
    (10395, 10892, 'g'), (10395, 11755, 'r'), (10439, 10628, 'b'), (10454, 10967, 'g'), (10454, 10989, 'b'), (10601, 10628, 'g'),
    (10601, 11755, 'b'), (10628, 11787, 'r'), (10892, 14535, 'b'), (10967, 12803, 'r'), (10989, 12515, 'g'), (11537, 11787, 'g'),
    (11537, 12515, 'r'), (11755, 13316, 'g'), (11787, 13316, 'b'), (12515, 12803, 'b'), (12803, 14535, 'g'), (13316, 14535, 'r'),
]


def map3_graph():
    names = {'r': 'red', 'g': 'green', 'b': 'blue'}
    graph = nx.MultiGraph()
    for u, v, c in MAP3_EDGES:
        graph.add_edge(u, v, color=names[c])
    return graph


def test_map3_kempe_class_is_exhausted(mod):
    graph = map3_graph()
    assert mod.is_well_colored(graph)
    with pytest.raises(mod.KempeClassExhausted, match="exhausted"):
        mod.find_kempe_repair(graph, (7960, 4718), (10989, 9023), 10000)


def test_map3_exhausted_class_is_recolored_exactly(mod):
    graph = map3_graph()
    before = edge_multiset(graph)
    mod.ariadne_case_any_face(graph, MAP3_STEP, 10000)
    assert mod.is_well_colored(graph)
    assert graph.number_of_nodes() == 30 and graph.number_of_edges() == 45
    assert all(degree == 3 for _, degree in graph.degree())
    # The two split edges are replaced by their halves; the new edge joins v1 and v2
    expected = before - collections.Counter([(4718, 7960), (9023, 10989)]) + collections.Counter(
        [(4718, 7970), (7960, 7970), (9023, 10318), (10318, 10989), (7970, 10318)])
    assert edge_multiset(graph) == expected
    assert mod.stats['S6-EXACT-RECOLORINGS'] == 1 and mod.stats['S6-EXACT-MAX-VERTICES'] == 30


def test_three_edge_coloring_keeps_a_proper_coloring(mod):
    graph = colored_prism()
    coloring = mod.find_three_edge_coloring(graph)
    assert coloring == {(min(u, v), max(u, v), k): c for u, v, k, c in graph.edges(keys=True, data='color')}


@pytest.mark.parametrize("graph", [nx.tetrahedral_graph(), nx.dodecahedral_graph(), nx.truncated_cube_graph()])
def test_three_edge_coloring_colors_uncolored_graphs(mod, graph):
    coloring = mod.find_three_edge_coloring(nx.MultiGraph(graph))
    colored = nx.MultiGraph()
    for (u, v, _), color in coloring.items():
        colored.add_edge(u, v, color=color)
    assert mod.is_well_colored(colored)
    assert edge_multiset(colored) == edge_multiset(graph)


def test_three_edge_coloring_reports_impossible_graphs(mod):
    # The Petersen graph is cubic but not 3-edge-colorable
    assert mod.find_three_edge_coloring(nx.MultiGraph(nx.petersen_graph())) is None
