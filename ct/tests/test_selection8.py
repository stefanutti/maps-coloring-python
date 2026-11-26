"""S8: even-face chains with restarts away from the previous principal face."""
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
    spec = importlib.util.spec_from_file_location("fourct_s8", CT / "4ct.py")
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


def seeded_map(mod, generator, size, seed, monkeypatch):
    import numpy as np

    random.seed(seed)
    numpy_seed = np.random.seed
    with monkeypatch.context() as scoped:
        scoped.setattr(np.random, 'seed', lambda: numpy_seed(seed))
        return getattr(mod, generator)(size, False)


def edge_multiset(graph):
    return collections.Counter(tuple(sorted((u, v))) for u, v in graph.edges())


def forbid_random(*args, **kwargs):
    pytest.fail("S8 attempted a random choice")


S8_SELECTIONS = ('SELECT-S8-F2', 'SELECT-S8-CONTINUE', 'SELECT-S8-CONTINUE-LAST', 'SELECT-S8-START',
                 'SELECT-S8-START-TOUCHING', 'SELECT-S8-FALLBACK')


def touching_ids(principal, face_index):
    return {id(principal)} | {id(face_index.first_face_with_edge((b, a), exclude_face=principal))
                              for a, b in principal}


def spy_reduction(mod, faces):
    """Run reduce_faces() with S8 and check the rule each selection applied."""
    observed = collections.Counter()

    def spy(g_faces, choices, i_global_counter, frontier, face_index):
        principal = mod.s8_principal_face
        alive = principal is not None and id(principal) in face_index.face_positions
        touching = touching_ids(principal, face_index) if alive else set()
        perimeter_vertices = {u for u, _ in principal} if alive else set()
        had_f2 = bool(face_index.faces_of_size(2))
        before = dict(mod.stats)
        edge, f1, f2, merged, event = mod.select_edge_to_remove_even_faces_restart_away(
            g_faces, choices, i_global_counter, frontier, face_index)
        (stat,) = [key for key in S8_SELECTIONS if mod.stats[key] != before[key]]
        observed[stat] += 1
        assert event is None
        assert 2 <= len(f1) <= len(f2)
        assert not mod.is_the_graph_one_edge_connected(merged)
        assert (stat == 'SELECT-S8-F2') == had_f2
        if stat in ('SELECT-S8-CONTINUE', 'SELECT-S8-START', 'SELECT-S8-START-TOUCHING'):
            assert len(merged) % 2 == 0
        if stat == 'SELECT-S8-CONTINUE':
            assert mod._even_neighbor_after_merge(f1, f2, edge, face_index)
        if stat in ('SELECT-S8-CONTINUE', 'SELECT-S8-CONTINUE-LAST'):
            assert principal is f1 or principal is f2
            assert len(f1) % 2 == 0 and len(f2) % 2 == 0
        if stat == 'SELECT-S8-CONTINUE-LAST':
            assert not mod._even_neighbor_after_merge(f1, f2, edge, face_index)
        if stat in ('SELECT-S8-START', 'SELECT-S8-START-TOUCHING', 'SELECT-S8-FALLBACK'):
            assert perimeter_vertices.isdisjoint(edge)
        if stat == 'SELECT-S8-START':
            # The new chain starts away from the old principal face
            assert id(f1) not in touching and id(f2) not in touching
        if stat == 'SELECT-S8-START-TOUCHING':
            # Only when no start away from the principal face was possible
            sizes = sorted({len(face) for face in g_faces if len(face) >= 3})
            away = [c for c in mod._face_reductions(face_index, sizes)
                    if perimeter_vertices.isdisjoint(c[0]) and id(c[1]) not in touching and id(c[2]) not in touching]
            assert mod._first_s6_reduction(away, face_index, True, allow_even_without_neighbor=True) is None
        return edge, f1, f2, merged, event

    mod.init_f_distribution(faces)
    thread = mod.reduce_faces(faces, 2345, spy)
    return thread, observed


def test_s8_near_restart_keeps_both_endpoints_off_the_previous_border(mod):
    cycles = [(7, 4, 6, 8), (3, 9, 10, 7, 8), (9, 2, 10), (1, 2, 9, 3, 5, 11),
              (5, 3, 8, 6, 12), (1, 11, 12, 6, 4), (11, 5, 12), (1, 4, 7, 10, 2)]
    faces = [list(zip(cycle, cycle[1:] + cycle[:1])) for cycle in cycles]
    principal = faces[3]
    mod.s8_principal_face = principal

    edge, _, _, merged, _ = mod.select_edge_to_remove_even_faces_restart_away(
        faces, 2345, 1, face_index=mod.FaceIndex(faces))

    # The first unprotected choice, 2–10, would suppress vertex 2 on the principal face.
    assert edge == (10, 7)
    assert len(merged) % 2 == 0
    assert mod.stats['SELECT-S8-START-TOUCHING'] == 1


def test_s8_stops_if_every_restart_would_cut_the_previous_border(mod, caplog):
    cycles = [(3, 4, 5), (5, 4, 6), (1, 8, 6, 4, 3, 2),
              (1, 7, 8), (7, 2, 3, 5, 6, 8), (1, 2, 7)]
    faces = [list(zip(cycle, cycle[1:] + cycle[:1])) for cycle in cycles]
    mod.s8_principal_face = faces[2]

    with pytest.raises(SystemExit):
        mod.select_edge_to_remove_even_faces_restart_away(faces, 2345, 1, face_index=mod.FaceIndex(faces))

    assert 'no bridge-free restart avoiding the previous perimeter' in caplog.text
    assert all(mod.stats[name] == 0 for name in S8_SELECTIONS)


def test_s8_accepts_a_continuation_with_a_shared_outside_neighbor(mod):
    cycles = [(3, 6, 2, 4), (1, 5, 6, 3), (5, 2, 6), (9, 8, 10),
              (7, 8, 9, 12), (1, 3, 4, 11, 12, 9, 10), (11, 7, 12), (1, 10, 8, 7, 11, 4, 2, 5)]
    faces = [list(zip(cycle, cycle[1:] + cycle[:1])) for cycle in cycles]
    mod.s8_principal_face = faces[1]

    edge, _, _, merged, _ = mod.select_edge_to_remove_even_faces_restart_away(
        faces, 2345, 1, face_index=mod.FaceIndex(faces))

    # The first choice, 1–5, gives two spokes to the same outside vertex.
    assert edge == (1, 5)
    assert mod.s8_principal_face is merged


def test_s8_starts_an_even_wave_on_a_cube(mod):
    faces = embedding(nx.cubical_graph())

    _, _, _, merged, _ = mod.select_edge_to_remove_even_faces_restart_away(faces, 2345, 0)

    # Every first merge of two square faces of the cube yields a square of a triangular prism.
    assert len(merged) == 4
    assert mod.stats['SELECT-S8-START'] == 1
    assert mod.s8_principal_face is merged


def test_s8_continues_with_a_merge_that_leaves_an_even_neighbor(mod):
    cycles = [(3, 2, 4), (1, 6, 5, 3, 4), (7, 8, 10, 9), (1, 2, 3, 5, 8, 7, 11, 6),
              (9, 10, 12), (5, 6, 11, 12, 10, 8), (11, 7, 9, 12), (1, 4, 2)]
    faces = [list(zip(cycle, cycle[1:] + cycle[:1])) for cycle in cycles]
    mod.s8_principal_face = faces[2]

    edge, _, _, merged, _ = mod.select_edge_to_remove_even_faces_restart_away(
        faces, 2345, 1, face_index=mod.FaceIndex(faces))

    assert edge == (8, 10)
    assert mod.stats['SELECT-S8-CONTINUE'] == 1
    assert mod.s8_principal_face is merged


def test_s8_takes_the_last_admissible_even_merge_before_restart(mod):
    cycles = [(3, 2, 4), (1, 6, 5, 3, 4), (7, 8, 10, 9), (1, 2, 3, 5, 8, 7, 11, 6),
              (9, 10, 12), (5, 6, 11, 12, 10, 8), (11, 7, 9, 12), (1, 4, 2)]
    faces = [list(zip(cycle, cycle[1:] + cycle[:1])) for cycle in cycles]
    mod.s8_principal_face = faces[3]

    edge, _, _, merged, _ = mod.select_edge_to_remove_even_faces_restart_away(
        faces, 2345, 1, face_index=mod.FaceIndex(faces))

    assert edge == (7, 8)
    assert mod.stats['SELECT-S8-CONTINUE-LAST'] == 1
    assert mod.s8_principal_face is merged


def test_s8_continues_by_merging_two_hexagons(mod):
    faces = embedding(nx.truncated_tetrahedron_graph())
    principal = next(face for face in faces if len(face) == 6)
    mod.s8_principal_face = principal

    _, f1, f2, merged, _ = mod.select_edge_to_remove_even_faces_restart_away(
        faces, 2345, 1, face_index=mod.FaceIndex(faces))

    assert principal is f1 or principal is f2
    assert (len(f1), len(f2), len(merged)) == (6, 6, 8)
    assert mod.stats['SELECT-S8-CONTINUE'] == 1


def test_s8_colors_links_between_two_disjoint_cycles_blue(mod):
    graph = nx.MultiGraph(nx.circular_ladder_graph(4))
    faces = embedding(graph)
    upper = next(face for face in faces if {u for u, _ in face} == {0, 1, 2, 3})
    lower = next(face for face in faces if {u for u, _ in face} == {4, 5, 6, 7})
    tracked = {}
    index = mod.FaceIndex(faces)

    assert mod._s8_cycle_cover(index, tracked, upper) is None
    cover = mod._s8_cycle_cover(index, tracked, lower)
    colored = mod._s8_color_from_cycle_cover(graph, cover)

    assert mod.is_well_colored(colored)
    assert edge_multiset(colored) == edge_multiset(graph)
    assert {frozenset((u, v)) for u, v, color in colored.edges(data='color') if color == 'blue'} == {
        frozenset((u, u + 4)) for u in range(4)}

    # The incoming coloring uses blue on the upper cycle instead of on the rungs.
    for _, _, data in colored.edges(data=True):
        data['color'] = {'red': 'blue', 'blue': 'red'}.get(data['color'], data['color'])
    u, v = upper[0]
    w, z = upper[2]
    mod.restore_ariadne_step_s8(colored, [4, 8, 9, u, z, v, w], 10000, cover)
    assert mod.stats['S8-CYCLE-RECOLORED'] == 1
    assert mod.is_well_colored(colored)
    assert mod.get_edge_color(colored, (8, 9)) == 'blue'


def test_s8_restores_a_triangle_from_two_parallel_edges(mod):
    graph = nx.MultiGraph()
    for u, v, color in [(0, 1, 'green'), (0, 1, 'blue'), (0, 2, 'red'), (1, 3, 'red'),
                        (2, 3, 'green'), (2, 3, 'blue')]:
        mod.graph_add_edge(graph, u, v, color)

    mod.restore_ariadne_step_s8(graph, [3, 4, 5, 0, 0, 1, 1], 10000, None)

    assert set(graph.neighbors(4)) == {0, 1, 5}
    assert set(graph.neighbors(5)) == {0, 1, 4}
    assert not graph.has_edge(0, 1)
    assert all(degree == 3 for _, degree in graph.degree())
    assert mod.is_well_colored(graph)


@pytest.mark.parametrize("generator,size,seed", [
    ("create_from_random1", 300, 1), ("create_from_random1", 300, 2),
    ("create_from_random2", 200, 3), ("create_from_random2", 200, 4),
])
def test_s8_restarts_away_from_the_principal_face(mod, generator, size, seed, monkeypatch):
    _, faces = seeded_map(mod, generator, size, seed, monkeypatch)
    thread, observed = spy_reduction(mod, faces)
    assert len(faces) == 3
    assert sum(observed.values()) == len(thread)
    assert observed['SELECT-S8-START'] > 0 and observed['SELECT-S8-CONTINUE'] > 0


@pytest.mark.parametrize("graph", [nx.tetrahedral_graph(), nx.cubical_graph(), nx.dodecahedral_graph(),
                                   nx.truncated_cube_graph()])
def test_s8_rebuild_preserves_topology_without_randomness(mod, monkeypatch, graph):
    monkeypatch.setattr(mod, "randint", forbid_random)
    monkeypatch.setattr(mod, "graph_random_edge", forbid_random)
    faces = embedding(graph)
    mod.init_f_distribution(faces)
    covers = []
    thread = mod.reduce_faces(faces, 2345, mod.select_edge_to_remove_even_faces_restart_away,
                              s8_cycle_covers=covers)
    rebuilt = mod.rebuild_faces(faces, thread, kempe_search_limit=10000, s8_cycle_covers=covers)
    assert not covers and not thread
    assert mod.is_well_colored(rebuilt)
    assert edge_multiset(rebuilt) == edge_multiset(graph)


def test_s8_rebuilds_random_maps(mod, monkeypatch):
    monkeypatch.setattr(mod, "randint", forbid_random)
    monkeypatch.setattr(mod, "graph_random_edge", forbid_random)
    for seed in (12, 13, 15):
        _, faces = seeded_map(mod, 'create_from_random1', 300, seed, monkeypatch)
        graph = mod.create_graph_from_planar_representation(faces)
        mod.initialize_statistics()
        mod.init_f_distribution(faces)
        covers = []
        thread = mod.reduce_faces(faces, 2345, mod.select_edge_to_remove_even_faces_restart_away,
                                  s8_cycle_covers=covers)
        rebuilt = mod.rebuild_faces(faces, thread, kempe_search_limit=10000, s8_cycle_covers=covers)
        assert mod.is_well_colored(rebuilt)
        assert edge_multiset(rebuilt) == edge_multiset(graph)


def test_s8_reduction_is_deterministic_and_read_only_per_step(mod):
    threads = []
    for _ in range(2):
        faces = embedding(nx.truncated_cube_graph())
        mod.initialize_statistics()
        mod.init_f_distribution(faces)
        threads.append(mod.reduce_faces(faces, 2345, mod.select_edge_to_remove_even_faces_restart_away))
    assert threads[0] == threads[1]
    faces = embedding(nx.cubical_graph())
    original = copy.deepcopy(faces)
    index = mod.FaceIndex(faces)
    mod.select_edge_to_remove_even_faces_restart_away(faces, 2345, 0, None, index)
    assert faces == original and index.validate()


def run_s8_cli(tmp_path, faces, *options):
    planar = tmp_path / "map.planar"
    planar.write_text(json.dumps(faces) + "\n")
    result = subprocess.run(
        [sys.executable, str(CT / "4ct.py"), "-s8", "-p", str(planar), *options],
        cwd=tmp_path, text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "BEGIN: Rebuild faces" not in result.stdout
    assert "Stats: SELECT-S8-FALLBACK = 0\n" in result.stdout
    return result.stdout


def dot_edges(path):
    lines = path.read_text().splitlines()
    assert lines[0] == "graph {" and lines[-1] == "}"
    return collections.Counter(tuple(sorted(map(int, line.strip().removesuffix(';').split(' -- '))))
                               for line in lines[1:-1])


def test_s8_cli_continues_after_a_near_restart(tmp_path):
    cycles = [(1, 8, 6, 4, 3, 2), (1, 7, 8), (3, 4, 11, 14, 12), (13, 12, 14),
              (7, 5, 16, 15, 10, 6, 8), (15, 16), (9, 17, 11, 4, 6, 10),
              (5, 2, 3, 12, 13, 18, 9, 10, 15, 16), (11, 17, 18, 13, 14), (17, 9, 18), (1, 2, 5, 7)]
    faces = [list(zip(cycle, cycle[1:] + cycle[:1])) for cycle in cycles]

    output = run_s8_cli(tmp_path, faces, '-o', 'partial')

    assert "Stats: SELECT-S8-START-TOUCHING = 1\n" in output
    assert dot_edges(tmp_path / 'partial.reduced.dot') == {(17, 18): 3}


def test_s8_cli_exports_before_an_available_structural_fallback(tmp_path):
    cycles = [(7, 8), (11, 12), (15, 16), (1, 2, 22, 21, 13, 3, 8, 7, 6, 5, 4), (23, 18, 24),
              (21, 22, 26, 25), (13, 21, 25, 26, 22, 2, 14), (25, 26), (19, 27, 20),
              (9, 29, 30, 19, 20), (29, 10, 30), (5, 6, 17, 32, 23, 24), (17, 15, 16, 31, 32),
              (31, 11, 12, 18, 23, 32), (3, 33, 4, 5, 24, 18, 12, 11, 31, 16, 15, 17, 6, 7, 8),
              (27, 19, 30, 10, 28, 34), (1, 4, 33, 34, 28), (33, 3, 13, 14, 9, 20, 27, 34),
              (1, 28, 10, 29, 9, 14, 2)]
    faces = [list(zip(cycle, cycle[1:] + cycle[:1])) for cycle in cycles]

    output = run_s8_cli(tmp_path, faces)

    assert "ending reduction before fallback" in output
    assert dot_edges(tmp_path / 'debug' / 's8.reduced.dot') == collections.Counter([
        (1, 2), (1, 4), (1, 28), (2, 13), (2, 14), (4, 5), (4, 28), (5, 6), (5, 23), (6, 13), (6, 17),
        (9, 14), (9, 29), (9, 30), (10, 28), (10, 29), (10, 30), (13, 14), (17, 31), (17, 32), (23, 31),
        (23, 32), (29, 30), (31, 32)])


def test_s8_cli_exports_theta_if_reduction_finishes_before_near_restart(tmp_path):
    run_s8_cli(tmp_path, embedding(nx.tetrahedral_graph()))

    edges = dot_edges(tmp_path / 'debug' / 's8.reduced.dot')
    assert list(edges.values()) == [3]


@pytest.mark.parametrize('options, prefix', [((), 'debug/s8'), (('-o', 'batch'), 'batch')])
def test_s8_cli_exports_every_map_in_random_batch(tmp_path, options, prefix):
    result = subprocess.run(
        [sys.executable, str(CT / '4ct.py'), '-s8', '-n', '3', '-r2', '18', *options],
        cwd=tmp_path, text=True, capture_output=True, timeout=30)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.count('S8 reduced graph saved') == 3
    assert 'BEGIN: Rebuild faces' not in result.stdout
    for run in range(1, 4):
        assert dot_edges(tmp_path / f'{prefix}.{run}.reduced.dot')
