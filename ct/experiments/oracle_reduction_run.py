"""Persist and replay one oracle reduction branch (schema 1, no dataset sweep)."""
import argparse
from collections import Counter
from dataclasses import asdict
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Tuple

import networkx as nx

CT = Path(__file__).resolve().parents[1]
if str(CT) not in sys.path:
    sys.path.insert(0, str(CT))
from experiments.oracle_reduction import (
    Candidate, ChainResult, ColorSwap, EdgeRecord, FaceRecord, OracleState,
    RejectedCandidate, StepAttempt, StepWitness, _fourct, assert_state_invariants,
    make_state, replay_exact, run_chain, state_fingerprint,
)
from ct_graph_utils import KempeSearchExhausted, is_well_colored


def _state_data(state):
    return {
        "vertices": sorted(state.graph),
        "edges": [asdict(EdgeRecord(eid, u, v, state.graph[u][v][eid]["color"]))
                  for eid, (u, v) in sorted(state.edge_endpoints.items())],
        "faces": [asdict(FaceRecord(fid, i, tuple((u, v, eid) for (u, v), eid in
                  zip(face, state.face_edge_ids[fid]))))
                  for i, (fid, face) in enumerate(zip(state.face_ids, state.g_faces))],
        "next_ids": [state.next_edge_id, state.next_face_id],
    }


def _read_state(data):
    graph = nx.MultiGraph()
    graph.add_nodes_from(data["vertices"])
    endpoints = {}
    for edge in data["edges"]:
        eid, u, v = edge["edge_id"], edge["u"], edge["v"]
        if eid in endpoints or u >= v or u not in graph or v not in graph:
            raise ValueError("Invalid persisted edge identity")
        endpoints[eid] = (u, v)
        graph.add_edge(u, v, key=eid, color=edge["color"])
    records = data["faces"]
    if [r["position"] for r in records] != list(range(len(records))):
        raise ValueError("Invalid persisted face positions")
    state = OracleState(graph, [[(u, v) for u, v, _ in r["darts"]] for r in records],
                        [r["face_id"] for r in records],
                        {r["face_id"]: [eid for _, _, eid in r["darts"]] for r in records},
                        endpoints, *data["next_ids"])
    assert_state_invariants(state)
    return state


def _read_witness(data):
    faces = {name: tuple(FaceRecord(r["face_id"], r["position"], tuple(tuple(d) for d in r["darts"]))
                         for r in data[name]) for name in ("before_faces", "after_faces")}
    return StepWitness(
        Candidate(**data["candidate"]), tuple(data["ariadne"]),
        tuple(EdgeRecord(**r) for r in data["before_edges"]),
        tuple(EdgeRecord(**r) for r in data["after_edges"]),
        faces["before_faces"], faces["after_faces"],
        tuple(data["before_next_ids"]), tuple(data["after_next_ids"]),
        data["before_fingerprint"], data["after_fingerprint"],
        tuple(ColorSwap(tuple(r["colors"]), tuple(tuple(d) for d in r["darts"]), r["kind"])
              for r in data["swaps"]),
    )


def _check_chain(terminal, result):
    """Check completeness/boundaries; semantic certificate validation is replay's job."""
    assert_state_invariants(terminal)
    if result.status not in {"theta_reached", "step_limit", "no_certified_candidate"}:
        raise ValueError("Unknown chain status")
    n = len(result.witnesses)
    terminal_counts = (len(terminal.graph), terminal.graph.number_of_edges(), len(terminal.g_faces))
    if tuple(c - d * n for c, d in zip(result.initial_counts, (2, 3, 1))) != terminal_counts:
        raise ValueError("Chain counts do not match terminal state")
    if (result.status == "theta_reached") != (terminal_counts == (2, 3, 3)):
        raise ValueError("Chain status does not match terminal state")
    fingerprint = result.initial_fingerprint
    for witness in result.witnesses:
        if witness.before_fingerprint != fingerprint:
            raise ValueError("Incomplete or reordered certificate chain")
        fingerprint = witness.after_fingerprint
    if fingerprint != state_fingerprint(terminal):
        raise ValueError("Chain does not end at saved terminal state")
    if result.rejections and result.status != "no_certified_candidate":
        raise ValueError("Rejections must describe the final blocked state")
    for rejected in result.rejections:
        StepAttempt(rejected.status, rejected.reason)


def save_run(directory: Path, terminal: OracleState, result: ChainResult, provenance: dict) -> None:
    """Write deltas and terminal once; manifest last marks a completed save.

    Existing populated destinations are never overwritten. A failed write may
    leave a partial directory, which load_run rejects; retry in a new directory.
    """
    directory = Path(directory)
    if directory.exists() and any(directory.iterdir()):
        raise FileExistsError("Run directory is already populated: " + str(directory))
    _check_chain(terminal, result)
    terminal_bytes = (json.dumps(_state_data(terminal), sort_keys=True) + "\n").encode("utf-8")
    steps_bytes = "".join(json.dumps(asdict(w), sort_keys=True) + "\n" for w in result.witnesses).encode("utf-8")
    files = {"terminal.json": terminal_bytes, "steps.jsonl": steps_bytes}
    manifest = {
        "schema_version": 1,
        "files_sha256": {name: hashlib.sha256(raw).hexdigest() for name, raw in files.items()},
        "result": {
            "status": result.status, "step_count": len(result.witnesses),
            "initial_fingerprint": result.initial_fingerprint, "initial_counts": result.initial_counts,
            "family_counts": result.family_counts, "swap_counts": result.swap_counts,
            "rejections": [asdict(r) for r in result.rejections],
        },
        "provenance": provenance,
    }
    files["manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    directory.mkdir(parents=True, exist_ok=True)
    for name, raw in files.items():
        with (directory / name).open("xb") as stream:
            stream.write(raw)


def load_run(directory: Path) -> Tuple[OracleState, ChainResult, dict]:
    """Load schema 1, verify file integrity and recreate all derived indexes."""
    directory = Path(directory)
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    if type(manifest.get("schema_version")) is not int or manifest["schema_version"] != 1:
        raise ValueError("Unsupported oracle run schema")
    try:
        files = {}
        for name in ("terminal.json", "steps.jsonl"):
            raw = (directory / name).read_bytes()
            if hashlib.sha256(raw).hexdigest() != manifest["files_sha256"][name]:
                raise ValueError("SHA-256 mismatch: " + name)
            files[name] = raw
        terminal = _read_state(json.loads(files["terminal.json"]))
        witnesses = [_read_witness(json.loads(line)) for line in files["steps.jsonl"].splitlines()]
        data = manifest["result"]
        result = ChainResult(data["status"], witnesses,
                             [RejectedCandidate(Candidate(**r["candidate"]), r["status"], r["reason"])
                              for r in data["rejections"]],
                             data["initial_fingerprint"], tuple(data["initial_counts"]))
        if (len(witnesses) != data["step_count"] or result.family_counts != data["family_counts"]
                or result.swap_counts != data["swap_counts"]):
            raise ValueError("Saved certificate counts disagree with manifest")
        _check_chain(terminal, result)
        return terminal, result, manifest["provenance"]
    except (KeyError, TypeError, IndexError, AssertionError) as error:
        raise ValueError("Malformed oracle run: " + str(error)) from error


def ordinary_rebuild(terminal, result, original, kempe_search_limit):
    """Measure ordinary reconstruction using only structural faces and Ariadne.

    original is used only to compare the returned graph, never by rebuild_faces.
    Unexpected errors propagate; only KempeSearchExhausted is inconclusive.
    """
    if type(kempe_search_limit) is not int or kempe_search_limit < 1:
        raise ValueError("Kempe search limit must be positive")
    outcome = {"kempe_search_limit": kempe_search_limit}
    if result.status != "theta_reached":
        outcome["status"] = "not_run_nonterminal"
        return outcome
    _check_chain(terminal, result)
    faces = [face[:] for face in terminal.g_faces]
    stack = [list(w.ariadne) for w in result.witnesses]
    _fourct.stats = {}
    _fourct.initialize_statistics()
    _fourct.stats["time_ELABORATION"] = datetime.datetime.now()
    try:
        graph = _fourct.rebuild_faces(faces, stack, kempe_search_limit=kempe_search_limit)
    except KempeSearchExhausted as error:
        outcome.update(status="search_exhausted", reason=str(error))
        return outcome
    topology = (set(graph) == set(original.graph) and
                Counter(tuple(sorted((u, v))) for u, v in graph.edges()) ==
                Counter(tuple(sorted((u, v))) for u, v in original.graph.edges()))
    colored = is_well_colored(graph)
    outcome.update(status="success" if topology and colored and not stack else "verification_failed",
                   topology_matches=topology, well_colored=colored, stack_consumed=not stack,
                   vertices=len(graph), edges=graph.number_of_edges())
    if outcome["status"] != "success":
        raise AssertionError("Ordinary reconstruction verification failed: " + str(outcome))
    return outcome


def _source_line(path, map_number):
    """Select a physical 1-based line without parsing/validating other maps."""
    with Path(path).open("rb") as stream:
        for number, raw in enumerate(stream, 1):
            if number == map_number:
                return raw
    raise ValueError("Input has no physical line " + str(map_number))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--input", type=Path)
    mode.add_argument("--replay", type=Path)
    parser.add_argument("--map-number", type=int)
    parser.add_argument("--max-steps", type=int)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--ordinary-rebuild", action="store_true")
    parser.add_argument("--kempe-search-limit", type=int)
    args = parser.parse_args(argv)
    run_options = (args.map_number, args.max_steps, args.output, args.kempe_search_limit)
    if args.replay is not None:
        if any(value is not None for value in run_options) or args.ordinary_rebuild:
            parser.error("--replay is a separate mode; no run options are accepted")
        terminal, result, provenance = load_run(args.replay)
        restored = replay_exact(terminal, result.witnesses)
        source = provenance["source"]
        raw = _source_line(source["path"], source["map_number"])
        if hashlib.sha256(raw).hexdigest() != source["line_sha256"]:
            raise ValueError("Source line SHA-256 changed")
        original = make_state(json.loads(raw))
        exact = state_fingerprint(restored) == state_fingerprint(original) == result.initial_fingerprint
        edges_match = Counter((min(u, v), max(u, v), k, d["color"])
                              for u, v, k, d in restored.graph.edges(keys=True, data=True)) == Counter(
                              (min(u, v), max(u, v), k, d["color"])
                              for u, v, k, d in original.graph.edges(keys=True, data=True))
        if not exact or not edges_match:
            raise AssertionError("Exact replay differs from the source map")
        print(json.dumps({"status": result.status, "steps": len(result.witnesses),
                          "exact_replay": exact, "source_matches": exact,
                          "edge_multiset_matches": edges_match}, sort_keys=True))
        return
    if args.output is None or args.max_steps is None:
        parser.error("--input requires --output and --max-steps")
    map_number = 1 if args.map_number is None else args.map_number
    kempe_limit = 10000 if args.kempe_search_limit is None else args.kempe_search_limit
    if args.max_steps < 0 or map_number < 1 or kempe_limit < 1:
        parser.error("max-steps must be nonnegative; map-number and kempe-search-limit must be positive")
    if args.output.exists() and any(args.output.iterdir()):
        raise FileExistsError("Run directory is already populated: " + str(args.output))
    raw = _source_line(args.input, map_number)
    original = make_state(json.loads(raw))
    terminal = make_state(json.loads(raw))
    start = time.perf_counter()
    result = run_chain(terminal, args.max_steps)
    chain_seconds = time.perf_counter() - start
    restored = replay_exact(terminal, result.witnesses)
    if state_fingerprint(restored) != state_fingerprint(original):
        raise AssertionError("Exact replay differs from source")
    code_files = [CT / "4ct.py", CT / "ct_graph_utils.py", Path(__file__),
                  CT / "experiments/oracle_reduction.py"]
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=CT, capture_output=True, text=True, check=True)
    provenance = {
        "source": {"path": str(args.input.resolve()), "map_number": map_number,
                   "line_sha256": hashlib.sha256(raw).hexdigest()},
        "configuration": {"max_steps": args.max_steps, "ordinary_rebuild": args.ordinary_rebuild,
                          "kempe_search_limit": kempe_limit},
        "git_revision": revision.stdout.strip(),
        "code_sha256": {str(p.relative_to(CT.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in code_files},
        "python_version": sys.version, "networkx_version": nx.__version__,
        "chain_seconds": chain_seconds, "exact_replay": True,
        "ordinary": {"status": "not_requested"},
    }
    if args.ordinary_rebuild:
        try:
            provenance["ordinary"] = ordinary_rebuild(terminal, result, original, kempe_limit)
        except (Exception, SystemExit) as error:
            # Preserve the certified run, but never disguise a software error as
            # a negative mathematical result. The original error remains fatal.
            provenance["ordinary"] = {"status": "software_error", "reason": repr(error),
                                      "kempe_search_limit": kempe_limit}
            save_run(args.output, terminal, result, provenance)
            raise
    save_run(args.output, terminal, result, provenance)
    print(json.dumps({"status": result.status, "steps": len(result.witnesses),
                      "family_counts": result.family_counts, "swap_counts": result.swap_counts,
                      "exact_replay": True, "ordinary": provenance["ordinary"],
                      "output": str(args.output.resolve())}, sort_keys=True))


if __name__ == "__main__":
    main()
