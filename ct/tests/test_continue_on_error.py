"""Batch recovery skips search exhaustion, never unexpected failures."""
import importlib.util
import json
import logging
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


@pytest.fixture
def mod():
    spec = importlib.util.spec_from_file_location("fourct_batch", CT / "4ct.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.stats = {}
    module.initialize_statistics()
    return module


def configure_batch(tmp_path, monkeypatch, *, count=2, strategy="-s5", flag=True):
    planar = tmp_path / "batch.planar"
    maps = [
        [[(u + 10 * i, v + 10 * i) for u, v in face] for face in TETRAHEDRON]
        for i in range(count)
    ]
    planar.write_text("".join(json.dumps(faces) + "\n" for faces in maps))
    argv = ["4ct.py", "-p", str(planar), strategy]
    if flag:
        argv.append("--continue-on-error")
    monkeypatch.setattr(sys, "argv", argv)


def fail_first_reconstruction(mod, monkeypatch, error):
    rebuild = mod.rebuild_faces

    def rebuild_with_failure(faces, thread, **kwargs):
        # Only the first input fails; subsequent maps use the real pipeline.
        if min(u for face in faces for u, _ in face) < 10:
            raise error
        return rebuild(faces, thread, **kwargs)

    monkeypatch.setattr(mod, "rebuild_faces", rebuild_with_failure)


@pytest.mark.parametrize("strategy", ["-s1", "-s2", "-s3", "-s4", "-s5"])
def test_search_exhaustion_continues_and_reports_partial_failure(
        mod, tmp_path, monkeypatch, caplog, strategy):
    configure_batch(tmp_path, monkeypatch, strategy=strategy)
    fail_first_reconstruction(mod, monkeypatch, mod.KempeSearchExhausted("search exhausted"))
    with caplog.at_level(logging.INFO), pytest.raises(SystemExit) as stopped:
        mod.main()
    assert stopped.value.code == 1
    assert "Map 1/2" in caplog.text and "search exhausted" in caplog.text
    assert "Recreated graph is equal to the original" in caplog.text
    assert "1 succeeded, 1 failed" in caplog.text


@pytest.mark.parametrize("count,flag", [(2, False), (1, True), (1, False)])
def test_default_and_single_map_stop_on_search_exhaustion(
        mod, tmp_path, monkeypatch, caplog, count, flag):
    configure_batch(tmp_path, monkeypatch, count=count, flag=flag)
    fail_first_reconstruction(mod, monkeypatch, mod.KempeSearchExhausted("search exhausted"))
    with caplog.at_level(logging.INFO), pytest.raises(SystemExit) as stopped:
        mod.main()
    assert stopped.value.code == 1
    assert "execution 2" not in caplog.text
    assert "Batch summary" not in caplog.text


@pytest.mark.parametrize("error", [RuntimeError("bug"), ValueError("bad state"),
                                  AssertionError("invariant"), SystemExit(-1), KeyboardInterrupt()])
def test_unexpected_errors_are_never_swallowed(mod, tmp_path, monkeypatch, caplog, error):
    configure_batch(tmp_path, monkeypatch)
    fail_first_reconstruction(mod, monkeypatch, error)
    with caplog.at_level(logging.INFO), pytest.raises(type(error)) as stopped:
        mod.main()
    assert stopped.value is error
    assert "execution 2" not in caplog.text


def test_successful_batch_returns_normally(mod, tmp_path, monkeypatch, caplog):
    configure_batch(tmp_path, monkeypatch)
    with caplog.at_level(logging.INFO):
        mod.main()
    assert caplog.text.count("Recreated graph is equal to the original") == 2
    assert "2 succeeded, 0 failed" in caplog.text


@pytest.mark.parametrize("count,skip_first", [(1, False), (2, False), (2, True)])
def test_output_files_use_execution_number(mod, tmp_path, monkeypatch, count, skip_first):
    configure_batch(tmp_path, monkeypatch, count=count, flag=skip_first)
    monkeypatch.setattr(sys, "argv", sys.argv + ["-o", str(tmp_path / "test")])
    if skip_first:
        fail_first_reconstruction(mod, monkeypatch, mod.KempeSearchExhausted("search exhausted"))
        with pytest.raises(SystemExit) as stopped:
            mod.main()
        assert stopped.value.code == 1
    else:
        mod.main()

    executions = [2] if skip_first else list(range(1, count + 1))
    prefixes = ["test"] if count == 1 else [f"test.{i}" for i in executions]
    assert {path.name for path in tmp_path.glob("test.*")} == {
        f"{prefix}.{extension}"
        for prefix in prefixes for extension in ("edgelist", "orig.dot", "dot", "colored.planar")
    }
    for i, prefix in zip(executions, prefixes):
        graph = nx.read_edgelist(tmp_path / f"{prefix}.edgelist", nodetype=int,
                                 create_using=nx.MultiGraph())
        assert set(graph) == set(range(10 * (i - 1), 10 * (i - 1) + 4))
        assert graph.number_of_edges() == 6
        assert mod.is_well_colored(graph)
        assert 'label="' in (tmp_path / f"{prefix}.orig.dot").read_text()
        assert 'color="' in (tmp_path / f"{prefix}.dot").read_text()


@pytest.mark.parametrize("invalid", ["topology", "coloring"])
def test_final_invariant_failure_is_fatal(mod, tmp_path, monkeypatch, caplog, invalid):
    configure_batch(tmp_path, monkeypatch)
    rebuild = mod.rebuild_faces

    def corrupt_reconstruction(*args, **kwargs):
        graph = rebuild(*args, **kwargs)
        if invalid == "topology":
            graph.add_node(100)
        else:
            nx.set_edge_attributes(graph, "red", "color")
        return graph

    monkeypatch.setattr(mod, "rebuild_faces", corrupt_reconstruction)
    with caplog.at_level(logging.INFO), pytest.raises(SystemExit) as stopped:
        mod.main()
    assert stopped.value.code != 0
    assert "execution 2" not in caplog.text


@pytest.mark.parametrize("skip,expected_prefixes", [
    (0, ["test.1", "test.2", "test.3"]),
    (1, ["test.2", "test.3"]),
    (2, ["test"]),
    (3, []),
    (10, []),
])
def test_skip_reads_only_remaining_lines(mod, tmp_path, monkeypatch, caplog, skip, expected_prefixes):
    configure_batch(tmp_path, monkeypatch, count=3)
    planar = tmp_path / "batch.planar"
    lines = planar.read_text().splitlines(keepends=True)
    # Skipped rows are not parsed, and blank rows still count as physical lines.
    if skip:
        lines[0] = "\n"
    if skip > 1:
        lines[1] = "not JSON\n"
    planar.write_text("".join(lines))
    monkeypatch.setattr(sys, "argv", sys.argv + ["--skip", str(skip), "-o", str(tmp_path / "test")])
    with caplog.at_level(logging.INFO):
        mod.main()
    assert {p.name for p in tmp_path.glob("test.*")} == {
        f"{prefix}.{extension}" for prefix in expected_prefixes
        for extension in ("edgelist", "orig.dot", "dot", "colored.planar")
    }
    for i, prefix in enumerate(expected_prefixes, start=skip):
        graph = nx.read_edgelist(tmp_path / f"{prefix}.edgelist", nodetype=int,
                                 create_using=nx.MultiGraph())
        assert set(graph) == set(range(10 * i, 10 * i + 4))
        assert mod.is_well_colored(graph)
    if skip == 1:
        assert "2 succeeded, 0 failed (total: 2)" in caplog.text
    if skip >= 3:
        assert "No maps to process" in caplog.text


def test_skip_and_recovery_report_original_map_numbers(mod, tmp_path, monkeypatch, caplog):
    configure_batch(tmp_path, monkeypatch, count=3)
    monkeypatch.setattr(sys, "argv", sys.argv + ["-skip", "1"])
    rebuild = mod.rebuild_faces

    def fail_second_map(faces, thread, **kwargs):
        if min(u for face in faces for u, _ in face) < 20:
            raise mod.KempeSearchExhausted("search exhausted")
        return rebuild(faces, thread, **kwargs)

    monkeypatch.setattr(mod, "rebuild_faces", fail_second_map)
    with caplog.at_level(logging.INFO), pytest.raises(SystemExit) as stopped:
        mod.main()
    assert stopped.value.code == 1
    assert "Map 2/3" in caplog.text
    assert "1 succeeded, 1 failed (total: 2)" in caplog.text
    assert "Failed map numbers: [2]" in caplog.text
    assert "Recreated graph is equal to the original" in caplog.text


@pytest.mark.parametrize("options,message", [
    (["-p", "unused.planar", "--skip", "-1"], "--skip must be non-negative"),
    (["-r2", "10", "--skip", "1"], "--skip requires --planar"),
    (["-p", "unused.planar", "--skip", "1.5"], "invalid int value"),
])
def test_skip_rejects_invalid_arguments(mod, monkeypatch, capsys, options, message):
    monkeypatch.setattr(sys, "argv", ["4ct.py"] + options)
    with pytest.raises(SystemExit) as stopped:
        mod.main()
    assert stopped.value.code == 2
    assert message in capsys.readouterr().err


def test_random_kempe_limit_is_a_recoverable_failure(mod, tmp_path, monkeypatch):
    # Force an impasse to exercise the real 2,000-attempt termination path.
    graph = nx.MultiGraph()
    for offset in (0, 4):
        for i in range(4):
            graph.add_edge(offset + i, offset + (i + 1) % 4,
                           color="red" if i % 2 == 0 else "green")
    for i in range(4):
        graph.add_edge(i, i + 4, color="blue")
    monkeypatch.setattr(mod, "are_edges_on_the_same_kempe_cycle", lambda *args: False)
    monkeypatch.setattr(mod, "kempe_chain_color_swap", lambda *args: None)
    # Redirect the diagnostic files; keep the real export and sentinel writes.
    export = mod.export_graph
    monkeypatch.setattr(mod, "export_graph", lambda graph, name: export(graph, str(tmp_path / "failed")))
    with pytest.raises(mod.KempeSearchExhausted, match="2000"):
        mod.ariadne_case_f5(graph, [5, 8, 9, 0, 2, 4, 6])
    assert (tmp_path / "failed.edgelist").exists()
    assert mod.stats["TOTAL_RANDOM_KEMPE_SWITCHES"] == 2000
