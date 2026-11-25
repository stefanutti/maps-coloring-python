"""S7: S6 without face-size limits, with a parity lookahead that keeps the chain alive."""
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
    spec = importlib.util.spec_from_file_location("fourct_s7", CT / "4ct.py")
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
    pytest.fail("S7 attempted a random choice")


S7_SELECTIONS = ('SELECT-S7-F2', 'SELECT-S7-CONTINUE', 'SELECT-S7-START', 'SELECT-S7-FALLBACK')
S7_BREAKS = ('S7-BREAK-PRINCIPAL-GONE', 'S7-BREAK-ODD-PRINCIPAL', 'S7-BREAK-NO-EVEN-NEIGHBOR',
             'S7-BREAK-BRIDGE', 'S7-BREAK-NO-DURABLE-EVEN')


def spy_reduction(mod, faces):
    """Run reduce_faces() with S7 and check the rule each selection applied."""
    observed = collections.Counter()

    def spy(g_faces, choices, i_global_counter, frontier, face_index):
        had_f2 = bool(face_index.faces_of_size(2))
        principal = mod.s7_state['principal']
        before = dict(mod.stats)
        edge, f1, f2, merged, event = mod.select_edge_to_remove_even_ring(
            g_faces, choices, i_global_counter, frontier, face_index)
        (stat,) = [key for key in S7_SELECTIONS if mod.stats[key] != before[key]]
        observed[stat] += 1
        assert event is None
        assert edge in f1 and tuple(reversed(edge)) in f2
        assert 2 <= len(f1) <= len(f2)  # no size limit, but f1 is the smaller face
        assert not mod.is_the_graph_one_edge_connected(merged)
        assert (stat == 'SELECT-S7-F2') == had_f2
        if stat in ('SELECT-S7-CONTINUE', 'SELECT-S7-START'):
            assert len(merged) % 2 == 0 and len(merged) >= mod.S7_DURABLE_EVEN
            assert mod._even_neighbor_after_merge(f1, f2, edge, face_index, mod.S7_DURABLE_EVEN)
        if stat == 'SELECT-S7-CONTINUE':
            assert principal is f1 or principal is f2
            assert len(f1) % 2 == 0 and len(f2) % 2 == 0
        return edge, f1, f2, merged, event

    mod.init_f_distribution(faces)
    thread = mod.reduce_faces(faces, 2345, spy)
    return thread, observed


def random_faces(mod, number_of_faces, seed):
    random.seed(seed)
    _, faces = mod.create_from_random2(number_of_faces, False)
    return faces


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_s7_rules_hold_on_random_maps(mod, seed):
    faces = random_faces(mod, 150, seed)
    thread, observed = spy_reduction(mod, faces)
    assert len(faces) == 3
    assert sum(observed.values()) == len(thread)
    assert observed['SELECT-S7-CONTINUE'] > 0
    # A break is recorded only when a chain existed and could not continue
    assert sum(mod.stats[key] for key in S7_BREAKS) <= observed['SELECT-S7-START'] + observed['SELECT-S7-FALLBACK']
    assert mod.stats['S7-MAX-CHAIN'] > 0


def test_s7_keeps_long_chains_on_the_dodecahedron(mod):
    faces = embedding(nx.dodecahedral_graph())
    _, observed = spy_reduction(mod, faces)
    assert observed['SELECT-S7-CONTINUE'] >= observed['SELECT-S7-START']


@pytest.mark.parametrize("graph", [nx.tetrahedral_graph(), nx.cubical_graph(), nx.dodecahedral_graph(),
                                   nx.truncated_cube_graph(), nx.truncated_tetrahedron_graph()])
def test_s7_rebuild_preserves_topology_without_randomness(mod, monkeypatch, graph):
    monkeypatch.setattr(mod, "randint", forbid_random)
    monkeypatch.setattr(mod, "graph_random_edge", forbid_random)
    faces = embedding(graph)
    thread, _ = spy_reduction(mod, faces)
    rebuilt = mod.rebuild_faces(faces, thread, kempe_search_limit=10000, restore_step=mod.restore_ariadne_step_s6)
    assert mod.is_well_colored(rebuilt)
    assert edge_multiset(rebuilt) == edge_multiset(graph)


def test_s7_rebuilds_random_maps(mod, monkeypatch):
    monkeypatch.setattr(mod, "randint", forbid_random)
    monkeypatch.setattr(mod, "graph_random_edge", forbid_random)
    for seed in (11, 12, 13):
        random.seed(seed)
        _, faces = mod.create_from_random2(200, False)
        graph = mod.create_graph_from_planar_representation(faces)
        mod.initialize_statistics()
        mod.init_f_distribution(faces)
        thread = mod.reduce_faces(faces, 2345, mod.select_edge_to_remove_even_ring)
        rebuilt = mod.rebuild_faces(faces, thread, kempe_search_limit=10000, restore_step=mod.restore_ariadne_step_s6)
        assert mod.is_well_colored(rebuilt)
        assert edge_multiset(rebuilt) == edge_multiset(graph)


def test_s7_reduction_is_deterministic_and_read_only_per_step(mod):
    threads = []
    for _ in range(2):
        faces = embedding(nx.truncated_cube_graph())
        mod.initialize_statistics()
        mod.init_f_distribution(faces)
        threads.append(mod.reduce_faces(faces, 2345, mod.select_edge_to_remove_even_ring))
    assert threads[0] == threads[1]
    faces = embedding(nx.cubical_graph())
    original = copy.deepcopy(faces)
    index = mod.FaceIndex(faces)
    mod.select_edge_to_remove_even_ring(faces, 2345, 0, None, index)
    assert faces == original and index.validate()


def test_s7_cli_rebuilds_map(tmp_path, isolated_workdir):
    planar = tmp_path / "dodecahedron.planar"
    planar.write_text(json.dumps(embedding(nx.dodecahedral_graph())) + "\n")
    result = subprocess.run(
        [sys.executable, str(CT / "4ct.py"), "-s7", "-p", str(planar)],
        cwd=isolated_workdir, text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "Stats: SELECT-S7-CONTINUE" in result.stdout
    assert "Stats: TOTAL_RANDOM_KEMPE_SWITCHES = 0" in result.stdout
    assert "ERROR" not in result.stdout
