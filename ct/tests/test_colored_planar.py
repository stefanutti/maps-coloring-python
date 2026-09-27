"""Colored planar I/O preserves the embedding, but input colors are ignored."""
from collections import Counter
import importlib.util
import json
from pathlib import Path
import sys

import networkx as nx
import pytest


CT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CT))
TETRAHEDRON = [
    [(0, 1), (1, 2), (2, 0)],
    [(1, 0), (0, 3), (3, 1)],
    [(2, 1), (1, 3), (3, 2)],
    [(0, 2), (2, 3), (3, 0)],
]
THETA = [[(0, 1), (1, 0)] for _ in range(3)]
DOUBLE_EDGES = [
    [(0, 1), (1, 0)],
    [(2, 3), (3, 2)],
    [(0, 1), (1, 3), (3, 2), (2, 0)],
    [(1, 0), (0, 2), (2, 3), (3, 1)],
]


@pytest.fixture
def mod():
    spec = importlib.util.spec_from_file_location("fourct_planar_io", CT / "4ct.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.stats = {}
    module.initialize_statistics()
    return module


@pytest.mark.parametrize("mode", ["pairs", "triples", "mixed"])
def test_loader_ignores_input_colors(mod, tmp_path, mode):
    faces = [[list(edge) for edge in face] for face in TETRAHEDRON]
    for face in faces:
        for i, edge in enumerate(face):
            if mode == "triples" or (mode == "mixed" and i % 2 == 0):
                edge.append("ignored-color")
    planar = tmp_path / "input.planar"
    planar.write_text(json.dumps(faces) + "\n")
    graph, loaded = mod.create_from_planar(planar, False)
    assert loaded == TETRAHEDRON
    assert graph.number_of_edges() == 6
    assert all("color" not in data for _, _, data in graph.edges(data=True))
    mod.init_f_distribution(loaded)
    thread = mod.reduce_faces(loaded, 2345, mod.select_edge_to_remove_positive_corner)
    assert mod.is_well_colored(mod.rebuild_faces(loaded, thread, kempe_search_limit=100))


@pytest.mark.parametrize("edge", [[0], [0, 1, "red", "extra"]])
def test_loader_rejects_edges_that_are_neither_pairs_nor_triples(mod, tmp_path, edge):
    faces = [[list(e) for e in face] for face in TETRAHEDRON]
    faces[0][0] = edge
    planar = tmp_path / "invalid.planar"
    planar.write_text(json.dumps(faces) + "\n")
    with pytest.raises(ValueError, match="pair or triple"):
        mod.create_from_planar(planar, False)


@pytest.mark.parametrize("faces", [TETRAHEDRON, THETA, DOUBLE_EDGES])
@pytest.mark.parametrize("colored_input", [False, True])
def test_cli_exports_original_embedding_and_new_colors(
        mod, tmp_path, monkeypatch, faces, colored_input):
    original = [[list(edge) for edge in face] for face in faces]
    source = [[edge + ["red"] if colored_input else edge for edge in face] for face in original]
    planar = tmp_path / "input.planar"
    planar.write_text(json.dumps(source) + "\n")
    # Force a different face order so preserving the shuffled order cannot pass.
    monkeypatch.setattr(mod, "shuffle", lambda items: items.reverse())
    monkeypatch.setattr(sys, "argv", ["4ct.py", "-p", str(planar), "-s", "-s5",
                                     "-o", str(tmp_path / "result")])
    mod.main()
    output = tmp_path / "result.colored.planar"
    assert len(output.read_text().splitlines()) == 1
    colored = json.loads(output.read_text())
    assert [[edge[:2] for edge in face] for face in colored] == original
    graph = nx.read_edgelist(tmp_path / "result.edgelist", nodetype=int,
                             create_using=nx.MultiGraph())
    expected = Counter()
    for u, v, data in graph.edges(data=True):
        expected[(u, v, data["color"])] += 1
        expected[(v, u, data["color"])] += 1
    assert Counter(tuple(edge) for face in colored for edge in face) == expected
    assert {edge[2] for face in colored for edge in face} == {"red", "green", "blue"}
    for face in colored:
        for i, edge in enumerate(face):
            assert edge[2] != face[(i + 1) % len(face)][2]
    reloaded_graph, reloaded_faces = mod.create_from_planar(output, False)
    assert reloaded_faces == faces
    assert reloaded_graph.number_of_edges() == graph.number_of_edges()
    assert all("color" not in data for _, _, data in reloaded_graph.edges(data=True))


def test_cli_o2_appends_one_colored_planar_map_per_processed_input(
        mod, tmp_path, monkeypatch):
    planar = tmp_path / "input.planar"
    planar.write_text("\n".join((json.dumps(TETRAHEDRON), json.dumps(TETRAHEDRON))) + "\n")
    output = tmp_path / "maps.colored.planar"
    output.write_text('{"existing": true}\n')
    monkeypatch.setattr(sys, "argv", ["4ct.py", "-p", str(planar), "-s5",
                                     "-o2", str(output)])

    mod.main()

    lines = output.read_text().splitlines()
    assert len(lines) == 3
    assert json.loads(lines[0]) == {"existing": True}
    for line in lines[1:]:
        colored = json.loads(line)
        assert [[edge[:2] for edge in face] for face in colored] == [
            [list(edge) for edge in face] for face in TETRAHEDRON]
        assert {edge[2] for face in colored for edge in face} == {"red", "green", "blue"}


@pytest.mark.parametrize("filename", ["output", "output."])
def test_cli_o2_requires_output_filename_extension(
        mod, tmp_path, monkeypatch, capsys, filename):
    monkeypatch.setattr(sys, "argv", ["4ct.py", "-r2", "10", "-o2",
                                     str(tmp_path / filename)])

    with pytest.raises(SystemExit) as error:
        mod.main()

    assert error.value.code == 2
    assert "-o2 requires a filename with an extension" in capsys.readouterr().err


def test_colored_export_rejects_mismatched_embedding(mod, tmp_path):
    graph = nx.MultiGraph()
    for color in ("red", "green", "blue"):
        graph.add_edge(0, 1, color=color)
    with pytest.raises(ValueError, match="embedding"):
        mod.export_graph(graph, str(tmp_path / "bad"), planar_faces=THETA[:2])
    assert not (tmp_path / "bad.colored.planar").exists()
