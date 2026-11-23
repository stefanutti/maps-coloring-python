"""Validation reuse must detect public mutations, including derived indexes."""
from copy import deepcopy
from collections import UserDict
import cProfile
from dataclasses import replace
import marshal
from pathlib import Path
import sys
from types import SimpleNamespace
import zlib

import networkx as nx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from experiments import oracle_reduction as oracle


@pytest.fixture
def state():
    return oracle.make_state((
        ((0, 1, "blue"), (1, 2, "green"), (2, 0, "red")),
        ((1, 0, "blue"), (0, 3, "green"), (3, 1, "red")),
        ((2, 1, "green"), (1, 3, "red"), (3, 2, "blue")),
        ((0, 2, "red"), (2, 3, "blue"), (3, 0, "green")),
    ))


def bridge_checks(operation, *args, **kwargs):
    # Observe real global traversal, without replacing the checker with a mock.
    profile = cProfile.Profile()
    profile.runcall(operation, *args, **kwargs)
    return sum(entry.callcount for entry in profile.getstats()
               if entry.code == oracle._has_bridge.__code__)


def test_unchanged_state_reuses_global_checks(state):
    assert bridge_checks(oracle.assert_state_invariants, state) == 1
    assert bridge_checks(oracle.assert_state_invariants, state) == 0
    assert bridge_checks(oracle.assert_state_invariants, state) == 0


def test_snapshot_avoids_a_whole_state_serialization_buffer(state, monkeypatch):
    serialized_sizes = []

    def observed_dumps(value, version):
        # Keep the real encoder; measure its temporary outputs, not RSS or time.
        encoded = marshal.dumps(value, version)
        serialized_sizes.append(len(encoded))
        return encoded

    monkeypatch.setattr(oracle, "marshal", SimpleNamespace(dumps=observed_dumps))
    assert bridge_checks(oracle.assert_state_invariants, state) == 1
    assert max(serialized_sizes) < sum(serialized_sizes) // 2
    evidence = state._validated_snapshot
    assert len(zlib.decompress(evidence)) == sum(serialized_sizes)
    assert bridge_checks(oracle.assert_state_invariants, state) == 0
    assert state._validated_snapshot == evidence


def test_validation_evidence_is_compact_and_lossless_for_parallel_edges():
    theta = oracle.make_state((
        ((0, 1, "blue"), (1, 0, "red")),
        ((0, 1, "red"), (1, 0, "green")),
        ((0, 1, "green"), (1, 0, "blue")),
    ))
    identities = tuple(id(face) for face in theta.g_faces)
    # Hand-derived full payload: equal boundaries must retain distinct IDs,
    # parallel keys, colors, primitive types and all derived index contents.
    expected = b"".join(marshal.dumps(component, 2) for component in (
        True, False, (0, 1),
        ((0, 1, 0, "blue"), (0, 1, 1, "red"), (0, 1, 2, "green")),
        [[(0, 1), (1, 0)], [(0, 1), (1, 0)], [(0, 1), (1, 0)]],
        [0, 1, 2], {0: [0, 1], 1: [1, 2], 2: [2, 0]},
        {0: (0, 1), 1: (0, 1), 2: (0, 1)}, 3, 3,
        identities, True, {identity: i for i, identity in enumerate(identities)},
        ({(0, 1): identities, (1, 0): identities},
         {2: identities}, {0: identities, 1: identities}),
    ))
    oracle.assert_state_invariants(theta)
    evidence = theta._validated_snapshot
    # Deterministic storage regression, not an RSS or timing threshold.
    assert len(evidence) < len(expected) // 2
    assert zlib.decompress(evidence) == expected
    assert bridge_checks(oracle.assert_state_invariants, theta) == 0


def test_forced_validation_runs_complete_checks_even_when_warm(state):
    oracle.assert_state_invariants(state)
    assert bridge_checks(oracle.assert_state_invariants, state, force=True) == 1
    assert bridge_checks(oracle.assert_state_invariants, state) == 0


def test_failure_invalidates_previous_evidence_before_repair(state):
    oracle.assert_state_invariants(state)
    state.next_face_id = float(state.next_face_id)
    with pytest.raises(AssertionError, match="allocator"):
        oracle.assert_state_invariants(state)
    state.next_face_id = int(state.next_face_id)
    assert bridge_checks(oracle.assert_state_invariants, state) == 1
    assert bridge_checks(oracle.assert_state_invariants, state) == 0


def test_valid_but_nonserializable_mapping_falls_back_to_full_checks(state):
    oracle.assert_state_invariants(state)
    state.face_edge_ids = UserDict(state.face_edge_ids)
    assert bridge_checks(oracle.assert_state_invariants, state) == 1
    assert bridge_checks(oracle.assert_state_invariants, state) == 1


CORRUPTIONS = (
    "color", "edge", "isolated_node", "directed", "simple",
    "face_boundary", "edge_list_in_face", "extra_face", "aliased_face",
    "equal_face_replacement", "extra_face_id", "fractional_face_id",
    "extra_face_lookup", "occurrence", "extra_occurrence", "endpoints",
    "fractional_edge_id", "edge_counter", "face_counter",
    "index_source", "index_positions", "index_edges", "index_sizes",
    "index_vertices",
)


@pytest.mark.parametrize("corruption", CORRUPTIONS)
def test_warm_cache_rejects_corruption_of_every_validation_input(state, corruption):
    oracle.assert_state_invariants(state)
    u, v, key = next(iter(state.graph.edges(keys=True)))
    if corruption == "color":
        state.graph[u][v][key]["color"] = "red"
    elif corruption == "edge":
        state.graph.remove_edge(u, v, key)
    elif corruption == "isolated_node":
        state.graph.add_node(99)
    elif corruption == "directed":
        state.graph = nx.MultiDiGraph(state.graph)
    elif corruption == "simple":
        state.graph = nx.Graph(state.graph)
    elif corruption == "face_boundary":
        state.g_faces[0][0] = (0, 2)
    elif corruption == "edge_list_in_face":
        # JSON/fingerprint alone would normalize this unhashable pair to [0, 1].
        state.g_faces[0][0] = list(state.g_faces[0][0])
    elif corruption == "extra_face":
        state.g_faces.append(state.g_faces[0][:])
    elif corruption == "aliased_face":
        state.g_faces[1] = state.g_faces[0]
    elif corruption == "equal_face_replacement":
        state.g_faces[0] = state.g_faces[0][:]
    elif corruption == "extra_face_id":
        state.face_ids.append(99)
    elif corruption == "fractional_face_id":
        state.face_ids[0] = float(state.face_ids[0])
    elif corruption == "extra_face_lookup":
        state.face_edge_ids[99] = []
    elif corruption == "occurrence":
        state.face_edge_ids[0][0] = 99
    elif corruption == "extra_occurrence":
        state.face_edge_ids[0].append(key)
    elif corruption == "endpoints":
        state.edge_endpoints[key] = (u, 99)
    elif corruption == "fractional_edge_id":
        endpoints = state.edge_endpoints.pop(key)
        state.edge_endpoints[float(key)] = endpoints
    elif corruption == "edge_counter":
        state.next_edge_id = float(state.next_edge_id)
    elif corruption == "face_counter":
        state.next_face_id = float(state.next_face_id)
    elif corruption == "index_source":
        state.face_index.g_faces = state.g_faces[:]
    elif corruption == "index_positions":
        state.face_index.face_positions.clear()
    elif corruption == "index_edges":
        state.face_index.edge_to_faces.clear()
    elif corruption == "index_sizes":
        state.face_index.faces_by_len[3].reverse()
    elif corruption == "index_vertices":
        state.face_index.vertex_to_faces[99] = [state.g_faces[0]]
    with pytest.raises((AssertionError, TypeError, KeyError)):
        oracle.assert_state_invariants(state)
    # A failed check must not become a cached success.
    with pytest.raises((AssertionError, TypeError, KeyError)):
        oracle.assert_state_invariants(state)


def test_valid_mutation_rechecks_then_reuses_and_rejects_old_witness(state):
    witness = oracle.plan_step(state, next(oracle.ordered_candidates(state))).witness
    for _, _, data in state.graph.edges(data=True):
        data["color"] = {"red": "green", "green": "blue", "blue": "red"}[data["color"]]
    assert bridge_checks(oracle.assert_state_invariants, state) == 1
    assert bridge_checks(oracle.assert_state_invariants, state) == 0
    fingerprint = oracle.state_fingerprint(state)
    references = state.graph, state.g_faces, state.face_index
    with pytest.raises(ValueError, match="precondition"):
        oracle.apply_step(state, witness)
    assert oracle.state_fingerprint(state) == fingerprint
    assert all(a is b for a, b in zip(references, (state.graph, state.g_faces, state.face_index)))


def test_apply_and_undo_transfer_only_verified_result(state):
    original = oracle.state_fingerprint(state)
    witness = oracle.plan_step(state, next(oracle.ordered_candidates(state))).witness
    oracle.apply_step(state, witness)
    assert bridge_checks(oracle.assert_state_invariants, state) == 0
    oracle.assert_state_invariants(state, force=True)
    oracle.undo_step(state, witness)
    assert bridge_checks(oracle.assert_state_invariants, state) == 0
    oracle.assert_state_invariants(state, force=True)
    assert oracle.state_fingerprint(state) == original


def test_failed_apply_preserves_source_and_its_validity(state):
    witness = oracle.plan_step(state, next(oracle.ordered_candidates(state))).witness
    broken = replace(witness, after_fingerprint="invalid result")
    original = oracle.state_fingerprint(state)
    references = state.graph, state.g_faces, state.face_index
    with pytest.raises(ValueError, match="fingerprint"):
        oracle.apply_step(state, broken)
    assert oracle.state_fingerprint(state) == original
    assert all(a is b for a, b in zip(references, (state.graph, state.g_faces, state.face_index)))
    assert bridge_checks(oracle.assert_state_invariants, state) == 0


def test_copy_does_not_inherit_evidence_for_original_face_identities(state):
    oracle.assert_state_invariants(state)
    copied = deepcopy(state)
    copied.face_index = oracle._fourct.FaceIndex(copied.g_faces)
    assert bridge_checks(oracle.assert_state_invariants, copied) == 1
    assert bridge_checks(oracle.assert_state_invariants, copied) == 0
    copied.face_index.edge_to_faces.clear()
    with pytest.raises(AssertionError):
        oracle.assert_state_invariants(copied)
    assert bridge_checks(oracle.assert_state_invariants, state) == 0


def test_persisted_state_starts_with_fresh_validation(tmp_path, state):
    from experiments.oracle_reduction_run import load_run, save_run

    result = oracle.run_chain(state, 1)
    original = oracle.state_fingerprint(state)
    save_run(tmp_path / "run", state, result, {})
    terminal, loaded, _ = load_run(tmp_path / "run")
    assert oracle.state_fingerprint(terminal) == original
    assert loaded.witnesses == result.witnesses
    assert bridge_checks(oracle.assert_state_invariants, terminal) == 0
    terminal.face_edge_ids[99] = []
    with pytest.raises(AssertionError):
        oracle.assert_state_invariants(terminal)


def full_checker_observation(state, *, include_evidence=True):
    """Independent, lossless contents plus live references for read-only checks."""
    index = state.face_index
    mappings = (index.edge_to_faces, index.faces_by_len, index.vertex_to_faces)
    contents = marshal.dumps((
        state.graph.is_multigraph(), state.graph.is_directed(), state.graph.graph,
        tuple(state.graph.nodes(data=True)), tuple(state.graph.edges(keys=True, data=True)),
        state.g_faces, state.face_ids, state.face_edge_ids, state.edge_endpoints,
        state.next_edge_id, state.next_face_id, index.face_positions,
        tuple({key: tuple(id(face) for face in bucket) for key, bucket in mapping.items()}
              for mapping in mappings),
        state._validated_snapshot if include_evidence else None,
    ), 2)
    references = (
        state.graph, state.graph.graph, state.g_faces, *state.g_faces,
        state.face_ids, state.face_edge_ids, *state.face_edge_ids.values(),
        state.edge_endpoints, index, index.g_faces, index.face_positions,
        *mappings, *(bucket for mapping in mappings for bucket in mapping.values()),
        *(data for _, data in state.graph.nodes(data=True)),
        *(data for _, _, _, data in state.graph.edges(keys=True, data=True)),
    )
    if include_evidence:
        references += (state._validated_snapshot,)
    return contents, references


def assert_full_checker_preserved(state, before, *, include_evidence=True):
    contents, references = full_checker_observation(state, include_evidence=include_evidence)
    assert contents == before[0]
    assert len(references) == len(before[1])
    assert all(current is previous for current, previous in zip(references, before[1]))


def observe_edge_lookup_constructions(monkeypatch):
    # The raw checker alone resolves this module-level constructor. Keep the
    # native dict and all validation real; retain only a scalar call count.
    native_dict = dict
    counter = SimpleNamespace(calls=0)

    def observed_dict(*args, **kwargs):
        counter.calls += 1
        return native_dict(*args, **kwargs)

    monkeypatch.setattr(oracle, "dict", observed_dict, raising=False)
    return counter


def test_full_checker_builds_one_independent_edge_lookup_per_call(state, monkeypatch):
    # Catches a second materialization or reuse of an inventory across calls.
    before = full_checker_observation(state)
    counter = observe_edge_lookup_constructions(monkeypatch)
    oracle._assert_state_invariants_full(state)
    assert_full_checker_preserved(state, before)
    assert counter.calls == 1
    oracle._assert_state_invariants_full(state)
    assert_full_checker_preserved(state, before)
    assert counter.calls == 2


def test_full_checker_duplicate_global_key_precedes_stale_lookup(state):
    # A key may be unique per endpoint pair yet collide globally. Keep V/E,
    # coloring and bridges intact so the global-ID assertion must reject it.
    edges = list(state.graph.edges(keys=True, data=True))
    u, v, key, data = edges[0]
    other_key = edges[1][2]
    state.graph.remove_edge(u, v, key)
    state.graph.add_edge(u, v, key=other_key, **data)
    before = full_checker_observation(state)
    with pytest.raises(AssertionError, match="^Duplicate edge ID$"):
        oracle._assert_state_invariants_full(state)
    assert_full_checker_preserved(state, before)


@pytest.mark.parametrize("invalid_allocator", [False, True])
def test_full_checker_stale_endpoint_lookup_preserves_first_failure(state, invalid_allocator):
    first, second = list(state.edge_endpoints)[:2]
    state.edge_endpoints[first], state.edge_endpoints[second] = (
        state.edge_endpoints[second], state.edge_endpoints[first])
    if invalid_allocator:
        state.next_edge_id = -1
    before = full_checker_observation(state)
    with pytest.raises(AssertionError, match="^Edge lookup out of sync$"):
        oracle._assert_state_invariants_full(state)
    assert_full_checker_preserved(state, before)


@pytest.mark.parametrize("case", [
    "valid", "aliased_faces", "duplicate_dart",
    *(name + ":" + change for name in ("edge_to_faces", "faces_by_len", "vertex_to_faces")
      for change in ("reverse", "duplicate", "clone")),
])
def test_full_checker_theta_keeps_identity_order_and_multiplicity(case):
    # All theta boundaries have equal values, but their identities and keyed
    # darts differ. Collapsing identities/order/multiplicity must be rejected.
    theta = oracle.make_state((
        ((0, 1, "blue"), (1, 0, "red")),
        ((0, 1, "red"), (1, 0, "green")),
        ((0, 1, "green"), (1, 0, "blue")),
    ))
    message = None
    if case == "aliased_faces":
        theta.g_faces[1] = theta.g_faces[0]
        message = "Aliased faces"
    elif case == "duplicate_dart":
        theta.face_edge_ids[0][0] = theta.face_edge_ids[0][1]
        message = "Wrong directed edge occurrence multiplicity"
    elif case != "valid":
        name, change = case.split(":")
        bucket = next(iter(getattr(theta.face_index, name).values()))
        if change == "reverse":
            bucket.reverse()
        elif change == "duplicate":
            bucket.append(bucket[0])
        else:
            bucket[0] = bucket[0][:]
        message = "Stale " + name
    before = full_checker_observation(theta)
    if message is None:
        oracle._assert_state_invariants_full(theta)
    else:
        with pytest.raises(AssertionError, match="^" + message + "$"):
            oracle._assert_state_invariants_full(theta)
    assert_full_checker_preserved(theta, before)


@pytest.mark.parametrize("corruption,message", [
    ("duplicate", "Duplicate edge ID"), ("stale", "Edge lookup out of sync"),
])
@pytest.mark.parametrize("mode", ["cold", "warm", "force"])
def test_full_checker_failure_and_force_keep_validation_contract(
        state, monkeypatch, corruption, message, mode):
    # A failed full check must invalidate warm evidence; repair needs a new
    # real check. force=True must also materialize the lookup when warm.
    if mode != "cold":
        oracle.assert_state_invariants(state)
    counter = observe_edge_lookup_constructions(monkeypatch)
    if mode != "cold":
        before = full_checker_observation(state)
        oracle.assert_state_invariants(state)
        assert_full_checker_preserved(state, before)
        assert counter.calls == 0
    if mode == "force":
        before = full_checker_observation(state, include_evidence=False)
        oracle.assert_state_invariants(state, force=True)
        assert_full_checker_preserved(state, before, include_evidence=False)
        assert state._validated_snapshot is not None
        assert counter.calls == 1

    edges = list(state.graph.edges(keys=True, data=True))
    u, v, key, data = edges[0]
    other_key = edges[1][2]
    endpoints = state.edge_endpoints[key], state.edge_endpoints[other_key]
    if corruption == "duplicate":
        state.graph.remove_edge(u, v, key)
        state.graph.add_edge(u, v, key=other_key, **data)
    else:
        state.edge_endpoints[key], state.edge_endpoints[other_key] = reversed(endpoints)
    before = full_checker_observation(state, include_evidence=False)
    calls = counter.calls
    with pytest.raises(AssertionError, match="^" + message + "$"):
        oracle.assert_state_invariants(state, force=(mode == "force"))
    assert counter.calls == calls + 1
    assert state._validated_snapshot is None
    assert_full_checker_preserved(state, before, include_evidence=False)

    if corruption == "duplicate":
        state.graph.remove_edge(u, v, other_key)
        state.graph.add_edge(u, v, key=key, **data)
    else:
        state.edge_endpoints[key], state.edge_endpoints[other_key] = endpoints
    before = full_checker_observation(state, include_evidence=False)
    oracle.assert_state_invariants(state)
    assert counter.calls == calls + 2
    assert state._validated_snapshot is not None
    assert_full_checker_preserved(state, before, include_evidence=False)
    before = full_checker_observation(state)
    oracle.assert_state_invariants(state)
    assert counter.calls == calls + 2
    assert_full_checker_preserved(state, before)
