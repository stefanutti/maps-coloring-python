"""Keyed oracle state and certified local reductions, outside the main pipeline.

plan_step discovers a witness for a fixed candidate without changing its state.
apply/undo verify reversible patches; deterministic chains retain only deltas.
"""
from collections import Counter
from dataclasses import dataclass, field
import hashlib
import importlib.util
import json
import marshal
from pathlib import Path
import sys
from typing import Dict, List, Optional, Sequence, Tuple
import zlib

import networkx as nx

CT = Path(__file__).resolve().parents[1]
if str(CT) not in sys.path:
    sys.path.insert(0, str(CT))
from ct_graph_utils import VALID_COLORS, is_well_colored, join_faces, remove_vertex_from_face

_spec = importlib.util.spec_from_file_location("fourct_oracle_state", CT / "4ct.py")
_fourct = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fourct)

Dart = Tuple[int, int, int]  # source, target, stable edge ID


@dataclass(frozen=True)
class Candidate:
    face_id: int
    edge_id: int


@dataclass(frozen=True)
class EdgeRecord:
    edge_id: int
    u: int
    v: int
    color: str


@dataclass(frozen=True)
class FaceRecord:
    face_id: int
    position: int
    darts: Tuple[Dart, ...]


@dataclass(frozen=True)
class ColorSwap:
    colors: Tuple[str, str]
    darts: Tuple[Dart, ...]
    kind: str  # "cycle" (preliminary) or "path" (partial)


@dataclass(frozen=True)
class StepWitness:
    candidate: Candidate
    ariadne: Tuple[int, ...]
    before_edges: Tuple[EdgeRecord, ...]
    after_edges: Tuple[EdgeRecord, ...]
    before_faces: Tuple[FaceRecord, ...]
    after_faces: Tuple[FaceRecord, ...]
    before_next_ids: Tuple[int, int]
    after_next_ids: Tuple[int, int]
    before_fingerprint: str
    after_fingerprint: str
    swaps: Tuple[ColorSwap, ...] = ()


@dataclass(frozen=True)
class StepAttempt:
    status: str
    reason: str
    witness: Optional[StepWitness] = None

    def __post_init__(self):
        if self.status not in {"certified", "structurally_rejected", "no_witness", "unsupported_case"}:
            raise ValueError("Unknown step status")
        if (self.status == "certified") != (self.witness is not None):
            raise ValueError("Only a certified attempt must carry a witness")
        if self.status != "certified" and not self.reason:
            raise ValueError("An uncertified attempt needs a reason")


@dataclass
class OracleState:
    graph: nx.MultiGraph
    g_faces: List[List[Tuple[int, int]]]
    face_ids: List[int]
    face_edge_ids: Dict[int, List[int]]
    edge_endpoints: Dict[int, Tuple[int, int]]
    next_edge_id: int
    next_face_id: int
    face_index: object = field(init=False, repr=False)
    _validated_snapshot: Optional[bytes] = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self):
        self.face_index = _fourct.FaceIndex(self.g_faces)


@dataclass(frozen=True)
class RejectedCandidate:
    candidate: Candidate
    status: str
    reason: str


@dataclass
class ChainResult:
    status: str
    witnesses: List[StepWitness]
    rejections: List[RejectedCandidate]
    initial_fingerprint: str
    initial_counts: Tuple[int, int, int]

    @property
    def family_counts(self):
        counts = Counter(w.ariadne[0] for w in self.witnesses)
        return {"F" + str(size): counts[size] for size in (2, 3, 4, 5)}

    @property
    def swap_counts(self):
        return dict(Counter(s.kind for w in self.witnesses for s in w.swaps))


def make_state(colored_faces: Sequence[Sequence[Tuple[int, int, str]]]) -> OracleState:
    """Copy a complete colored embedding; IDs follow first occurrence order.

    Input coloring is a prerequisite. This is not a dataset validation pass;
    only record shape and ambiguous duplicate darts are rejected here.
    """
    graph = nx.MultiGraph()
    faces, face_edge_ids, edge_endpoints = [], {}, {}
    identified, seen_darts = {}, set()
    for fid, colored_face in enumerate(colored_faces):
        face, edge_ids = [], []
        for record in colored_face:
            if len(record) != 3:
                raise ValueError("Oracle state requires fully colored triples")
            u, v, color = record
            if type(u) is not int or type(v) is not int or color not in VALID_COLORS or u == v:
                raise ValueError("Invalid oracle edge record")
            if (u, v, color) in seen_darts:
                raise ValueError("Ambiguous duplicate colored dart")
            seen_darts.add((u, v, color))
            endpoints = (min(u, v), max(u, v))
            identity = (*endpoints, color)
            if identity not in identified:
                eid = len(identified)
                identified[identity] = eid
                edge_endpoints[eid] = endpoints
                # Explicit keys are essential: graph_add_edge uses local keys.
                graph.add_edge(*endpoints, key=eid, color=color)
            face.append((u, v))
            edge_ids.append(identified[identity])
        faces.append(face)
        face_edge_ids[fid] = edge_ids
    return OracleState(graph, faces, list(range(len(faces))), face_edge_ids,
                       edge_endpoints, len(identified), len(faces))


def state_fingerprint(state: OracleState) -> str:
    """Digest semantic state, not Python identities or derived index internals."""
    payload = (
        sorted(state.graph.nodes()),
        sorted((min(u, v), max(u, v), key, data["color"])
               for u, v, key, data in state.graph.edges(keys=True, data=True)),
        [(fid, face, state.face_edge_ids[fid]) for fid, face in zip(state.face_ids, state.g_faces)],
        sorted(state.edge_endpoints.items()), state.next_edge_id, state.next_face_id,
    )
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _has_bridge(graph: nx.MultiGraph) -> bool:
    """Read-only iterative low-link search on an undirected multigraph."""
    discovery, low = {}, {}
    for root in graph:
        if root not in discovery:
            discovery[root] = low[root] = len(discovery)
            stack = [(root, None, iter(graph.adj[root].items()))]
            while stack:
                vertex, parent, neighbors = stack[-1]
                item = next(neighbors, None)
                if item is None:
                    stack.pop()
                    if parent is not None:
                        if low[vertex] > discovery[parent]:
                            return True
                        low[parent] = min(low[parent], low[vertex])
                else:
                    neighbor, keys = item
                    if neighbor not in discovery:
                        discovery[neighbor] = low[neighbor] = len(discovery)
                        stack.append((neighbor, vertex, iter(graph.adj[neighbor].items())))
                    elif neighbor != parent or len(keys) > 1:
                        # A second edge to the parent is a return edge too.
                        low[vertex] = min(low[vertex], discovery[neighbor])
    return False


def _invariant_snapshot(state):
    """Exact process-local evidence, including types and derived face identities.

    Marshal version 2 preserves primitive types without reference-sharing
    encodings. Each component is serialized into one lossless zlib stream,
    avoiding an uncompressed buffer for the whole state. The ordered marshal
    values are self-delimiting; equality compares full content, not a digest.
    These bytes are only compared, never loaded or persisted.
    Unsupported/malformed data falls back to the complete reference checker.
    """
    try:
        index = state.face_index
        payload = (
            state.graph.is_multigraph(), state.graph.is_directed(),
            tuple(state.graph), tuple(state.graph.edges(keys=True, data="color")),
            state.g_faces, state.face_ids, state.face_edge_ids, state.edge_endpoints,
            state.next_edge_id, state.next_face_id,
            tuple(id(face) for face in state.g_faces), index.g_faces is state.g_faces,
            index.face_positions,
            tuple({key: tuple(id(face) for face in faces) for key, faces in mapping.items()}
                  for mapping in (index.edge_to_faces, index.faces_by_len, index.vertex_to_faces)),
        )
        compressor = zlib.compressobj(1)
        compressed = [compressor.compress(marshal.dumps(component, 2))
                      for component in payload]
        compressed.append(compressor.flush())
        return b"".join(compressed)
    except (AttributeError, KeyError, TypeError, ValueError):
        return None


def assert_state_invariants(state: OracleState, *, force: bool = False) -> None:
    """Reuse a successful check only while every checked input is unchanged.

    Public graph/list/index mutations are detected by value and identity, not
    by a caller-maintained revision flag. force=True runs the full reference.
    """
    snapshot = None
    if not force and state._validated_snapshot is not None:
        snapshot = _invariant_snapshot(state)
        if snapshot is not None and snapshot == state._validated_snapshot:
            return
    state._validated_snapshot = None
    _assert_state_invariants_full(state)
    state._validated_snapshot = snapshot if snapshot is not None else _invariant_snapshot(state)


def _assert_state_invariants_full(state: OracleState) -> None:
    """Check a produced state; deliberately independent of candidate selection."""
    graph = state.graph
    assert graph.is_multigraph() and not graph.is_directed(), "Expected undirected MultiGraph"
    assert len(graph) >= 2 and nx.is_connected(graph), "Disconnected or empty graph"
    assert is_well_colored(graph), "Invalid cubic coloring"
    assert all(data["color"] in VALID_COLORS for _, _, data in graph.edges(data=True)), "Unknown color"
    assert nx.number_of_selfloops(graph) == 0, "Loop"
    assert not _has_bridge(graph), "Bridge"
    actual_edges = [(key, (min(u, v), max(u, v))) for u, v, key in graph.edges(keys=True)]
    actual_edge_lookup = dict(actual_edges)
    assert len(actual_edge_lookup) == len(actual_edges), "Duplicate edge ID"
    assert actual_edge_lookup == state.edge_endpoints, "Edge lookup out of sync"
    del actual_edges, actual_edge_lookup
    assert type(state.next_edge_id) is int and state.next_edge_id >= 0, "Edge allocator counter"
    assert all(type(eid) is int and 0 <= eid < state.next_edge_id for eid in state.edge_endpoints), "Edge allocator"
    assert len(state.face_ids) == len(state.g_faces) == len(state.face_edge_ids), "Face metadata sizes"
    assert len(set(state.face_ids)) == len(state.face_ids), "Duplicate face ID"
    assert set(state.face_ids) == set(state.face_edge_ids), "Face lookup out of sync"
    assert type(state.next_face_id) is int and state.next_face_id >= 0, "Face allocator counter"
    assert all(type(fid) is int and 0 <= fid < state.next_face_id for fid in state.face_ids), "Face allocator"
    assert len({id(face) for face in state.g_faces}) == len(state.g_faces), "Aliased faces"
    occurrences, rotation = Counter(), {}
    for fid, face in zip(state.face_ids, state.g_faces):
        edge_ids = state.face_edge_ids[fid]
        assert len(face) >= 2 and len(face) == len(edge_ids), "Face occurrence length"
        for i, ((u, v), eid) in enumerate(zip(face, edge_ids)):
            assert state.edge_endpoints.get(eid) == (min(u, v), max(u, v)), "Edge occurrence endpoints"
            occurrences[u, v, eid] += 1
            a, b = face[(i + 1) % len(face)]
            assert v == a, "Open face boundary"
            rotation[v, u, eid] = (a, b, edge_ids[(i + 1) % len(face)])
    expected_occurrences = Counter(dart for eid, (u, v) in state.edge_endpoints.items()
                                   for dart in ((u, v, eid), (v, u, eid)))
    assert occurrences == expected_occurrences, "Wrong directed edge occurrence multiplicity"
    for dart in occurrences:
        assert rotation[dart] != dart and rotation[rotation[rotation[dart]]] == dart, "Invalid vertex rotation"
    # Connected, oriented dart permutations with one 3-cycle per vertex and
    # Euler characteristic 2 certify the supplied spherical embedding itself.
    assert len(graph) - graph.number_of_edges() + len(state.g_faces) == 2, "Non-spherical embedding"
    assert state.face_index.g_faces is state.g_faces, "Index references another embedding"
    expected_index = _fourct.FaceIndex(state.g_faces)
    assert state.face_index.face_positions == expected_index.face_positions, "Stale face positions"
    for name in ("edge_to_faces", "faces_by_len", "vertex_to_faces"):
        actual = {key: [id(face) for face in values]
                  for key, values in getattr(state.face_index, name).items()}
        expected = {key: [id(face) for face in values]
                    for key, values in getattr(expected_index, name).items()}
        assert actual == expected, "Stale " + name


def _bicolored_walk(state, colors, pair, start, first_edge, stop):
    """Follow one direction of a keyed bicolored cycle up to stop, if present."""
    vertex, eid = start, first_edge
    darts = []
    for _ in range(len(state.graph)):
        a, b = state.edge_endpoints[eid]
        neighbor = b if a == vertex else a
        assert vertex in (a, b) and colors[eid] in pair, "Invalid bicolored start"
        darts.append((vertex, neighbor, eid))
        if neighbor == stop:
            return tuple(darts)
        if neighbor == start:
            return ()
        following = [key for _, _, key in state.graph.edges(neighbor, keys=True)
                     if key != eid and colors[key] in pair]
        assert len(following) == 1, "Bicolored component must be a cycle"
        vertex, eid = neighbor, following[0]
    raise AssertionError("Bicolored walk did not close")


def _suppress_face_darts(darts, vertices, replacements):
    """Use the face primitive while carrying fusion IDs through its exact slots.

Endpoint lookup alone cannot distinguish the parallel edges created in theta.
F2 also needs the temporary edge from the first suppression to carry the same
fusion ID through the second suppression.
"""
    face = [(u, v) for u, v, _ in darts]
    ids = [eid for _, _, eid in darts]
    for vertex in vertices:
        if any(u == vertex for u, _ in face):
            incoming = next(i for i, (_, v) in enumerate(face) if v == vertex)
            outgoing = next(i for i, (u, _) in enumerate(face) if u == vertex)
            fused = replacements[ids[incoming]]
            assert fused == replacements[ids[outgoing]], "Inconsistent face fusion"
            ids.pop(incoming)
            insert_at = outgoing - int(incoming < outgoing)
            ids[insert_at] = fused
            remove_vertex_from_face(face, vertex)
    return tuple((u, v, eid) for (u, v), eid in zip(face, ids))


def _reduced_face_records(state, first, second, edge_id, vertices, replacements):
    """Splice by exact occurrence, check against join_faces, then suppress IDs."""
    before = tuple(FaceRecord(fid, position, tuple((u, v, eid) for (u, v), eid in
                        zip(face, state.face_edge_ids[fid])))
                   for position, (fid, face) in enumerate(zip(state.face_ids, state.g_faces)))
    f1, f2 = before[first], before[second]
    i = next(i for i, dart in enumerate(f1.darts) if dart[2] == edge_id)
    j = next(i for i, dart in enumerate(f2.darts) if dart[2] == edge_id)
    spliced = f1.darts[:i] + f2.darts[j + 1:] + f2.darts[:j] + f1.darts[i + 1:]
    merged = _suppress_face_darts(spliced, vertices, replacements)
    expected = join_faces(state.g_faces[first], state.g_faces[second], vertices)
    assert [(u, v) for u, v, _ in merged] == expected, "Keyed join disagrees with join_faces"
    after = []
    for record in before:
        if record.face_id not in (f1.face_id, f2.face_id):
            darts = _suppress_face_darts(record.darts, vertices, replacements)
            after.append(FaceRecord(record.face_id, len(after), darts))
    after.append(FaceRecord(state.next_face_id, len(after), merged))
    return before, tuple(after)


def plan_step(state: OracleState, candidate: Candidate) -> StepAttempt:
    """Certify one fixed F2–F5 candidate, or explain why this method cannot.

Input must satisfy OracleState invariants; corruption is a fatal assertion,
not a negative mathematical result. All work uses temporary data. F5 uses
only the direct complementary cycle; F4 may swap one complete cycle first.
"""
    assert_state_invariants(state)
    if candidate.face_id not in state.face_edge_ids:
        return StepAttempt("structurally_rejected", "Candidate face ID is absent")
    edge_ids = state.face_edge_ids[candidate.face_id]
    if candidate.edge_id not in edge_ids:
        return StepAttempt("structurally_rejected", "Candidate edge ID is not on the selected face")
    first = state.face_ids.index(candidate.face_id)
    face = state.g_faces[first]
    size = len(face)
    if len(state.graph) == 2:
        return StepAttempt("unsupported_case", "Theta is terminal; no further F2 reduction")
    if size not in (2, 3, 4, 5):
        return StepAttempt("unsupported_case", "Only F2–F5 constructions are implemented")
    position = edge_ids.index(candidate.edge_id)
    u, v = face[position]
    second = next(i for i, (fid, other) in enumerate(zip(state.face_ids, state.g_faces))
                  if ((v, u), candidate.edge_id) in zip(other, state.face_edge_ids[fid]))
    if first == second:
        return StepAttempt("structurally_rejected", "The selected edge borders the same face twice")
    incident = {vertex: [(b if a == vertex else a, eid)
                         for a, b, eid in state.graph.edges(vertex, keys=True)]
                for vertex in (u, v)}
    # Each fusion is (two surviving endpoints, source edge IDs). F2 consumes
    # both parallel digon edges and fuses only the two external edges.
    if size == 2:
        outside = [(b, eid) for vertex in (u, v) for b, eid in incident[vertex] if b not in (u, v)]
        assert len(outside) == 2, "Nonterminal F2 requires two external edges"
        ariadne = (2, u, v, outside[0][0], outside[1][0])
        fusions = [(outside[0][0], outside[1][0], tuple(eid for _, eid in outside))]
    else:
        remaining = [[(b, eid) for b, eid in incident[vertex] if eid != candidate.edge_id]
                     for vertex in (u, v)]
        fusions = [(items[0][0], items[1][0], tuple(eid for _, eid in items)) for items in remaining]
        if any(a in (u, v) or b in (u, v) or a == b for a, b, _ in fusions):
            return StepAttempt("structurally_rejected", "Suppression would retain a removed endpoint or create a loop; try F2")
        on_u, on_v = face[(position - 1) % size][0], face[(position + 1) % size][1]
        off_u = next(b for b, eid in remaining[0] if eid != edge_ids[(position - 1) % size])
        off_v = next(b for b, eid in remaining[1] if eid != edge_ids[(position + 1) % size])
        ariadne = (size, u, v, on_u, on_v, off_u, off_v)

    graph = state.graph.copy()
    graph.remove_nodes_from((u, v))
    for offset, (a, b, _) in enumerate(fusions):
        graph.add_edge(a, b, key=state.next_edge_id + offset)
    if nx.number_of_selfloops(graph) or not nx.is_connected(graph) or _has_bridge(graph):
        return StepAttempt("structurally_rejected", "Reduction would create a loop, disconnection or bridge")

    colors = {eid: state.graph[a][b][eid]["color"] for eid, (a, b) in state.edge_endpoints.items()}
    swaps = []
    if size != 2:
        start_edge = edge_ids[(position - 1) % size]
        pair = tuple(c for c in VALID_COLORS if c != colors[candidate.edge_id])
        path = _bicolored_walk(state, colors, pair, u, start_edge, v)
        if not path and size == 4 and len({colors[eid] for eid in edge_ids}) == 2:
            missing = next(c for c in VALID_COLORS if c not in {colors[eid] for eid in edge_ids})
            preliminary_pair = (colors[candidate.edge_id], missing)
            cycle = _bicolored_walk(state, colors, preliminary_pair, u, candidate.edge_id, u)
            opposite = edge_ids[(position + 2) % size]
            if opposite not in {eid for _, _, eid in cycle}:
                swaps.append(ColorSwap(preliminary_pair, cycle, "cycle"))
                for _, _, eid in cycle:
                    colors[eid] = preliminary_pair[1] if colors[eid] == preliminary_pair[0] else preliminary_pair[0]
                pair = tuple(c for c in VALID_COLORS if c != colors[candidate.edge_id])
                path = _bicolored_walk(state, colors, pair, u, start_edge, v)
        if not path:
            return StepAttempt("no_witness", "No complementary path for this candidate under the implemented construction")
        swaps.append(ColorSwap(pair, path, "path"))
        for _, _, eid in path:
            colors[eid] = pair[1] if colors[eid] == pair[0] else pair[0]

    replacements = {}
    for offset, (a, b, source_ids) in enumerate(fusions):
        eid = state.next_edge_id + offset
        assert len({colors[key] for key in source_ids}) == 1, "Swap does not permit fusion"
        graph[a][b][eid]["color"] = colors[source_ids[0]]
        replacements.update((key, eid) for key in source_ids)
        replacements[eid] = eid  # F2's temporary edge is suppressed a second time.
    if size == 2:
        replacements.update((eid, state.next_edge_id) for eid in edge_ids)
    for a, b, eid in graph.edges(keys=True):
        if eid in colors:
            graph[a][b][eid]["color"] = colors[eid]
    old_faces, new_faces = _reduced_face_records(state, first, second, candidate.edge_id, (u, v), replacements)
    result = OracleState(
        graph, [[(u, v) for u, v, _ in record.darts] for record in new_faces],
        [record.face_id for record in new_faces],
        {record.face_id: [eid for _, _, eid in record.darts] for record in new_faces},
        {eid: (min(a, b), max(a, b)) for a, b, eid in graph.edges(keys=True)},
        state.next_edge_id + len(fusions), state.next_face_id + 1,
    )
    old_edges = {eid: EdgeRecord(eid, a, b, state.graph[a][b][eid]["color"])
                 for eid, (a, b) in state.edge_endpoints.items()}
    new_edges = {eid: EdgeRecord(eid, a, b, graph[a][b][eid]["color"])
                 for eid, (a, b) in result.edge_endpoints.items()}
    old_by_id = {record.face_id: record.darts for record in old_faces}
    new_by_id = {record.face_id: record.darts for record in new_faces}
    witness = StepWitness(
        candidate, ariadne,
        tuple(old_edges[eid] for eid in sorted(old_edges) if old_edges[eid] != new_edges.get(eid)),
        tuple(new_edges[eid] for eid in sorted(new_edges) if new_edges[eid] != old_edges.get(eid)),
        tuple(record for record in old_faces if record.darts != new_by_id.get(record.face_id)),
        tuple(record for record in new_faces if record.darts != old_by_id.get(record.face_id)),
        (state.next_edge_id, state.next_face_id), (result.next_edge_id, result.next_face_id),
        state_fingerprint(state), state_fingerprint(result), tuple(swaps),
    )
    _check_witness(witness)
    _check_result(state, result, witness.after_fingerprint, -1)
    _check_reduction_description(state, result, witness)
    return StepAttempt("certified", "Keyed reduction and ordered color swaps verified", witness)


def _check_source(state, fingerprint, counters):
    if (state.next_edge_id, state.next_face_id) != counters or state_fingerprint(state) != fingerprint:
        raise ValueError("Certificate precondition does not match current state")
    assert_state_invariants(state)


def _patched_state(state, old_edges, new_edges, old_faces, new_faces,
                   removed_vertices, added_vertices, counters):
    """Build a private prospective state. Never mutate the caller on rejection."""
    for records, field_name in ((old_edges, "edge_id"), (new_edges, "edge_id"),
                                (old_faces, "face_id"), (new_faces, "face_id")):
        ids = [getattr(record, field_name) for record in records]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate patch ID")
    graph = state.graph.copy()
    endpoints = state.edge_endpoints.copy()
    for record in old_edges:
        if endpoints.get(record.edge_id) != (record.u, record.v):
            raise ValueError("Edge patch precondition mismatch")
        if graph[record.u][record.v][record.edge_id]["color"] != record.color:
            raise ValueError("Edge color precondition mismatch")
        graph.remove_edge(record.u, record.v, key=record.edge_id)
        del endpoints[record.edge_id]
    for vertex in removed_vertices:
        if vertex not in graph or graph.degree(vertex) != 0:
            raise ValueError("Vertex patch has missing incident edges")
        graph.remove_node(vertex)
    for vertex in added_vertices:
        if vertex in graph:
            raise ValueError("Vertex patch would overwrite a vertex")
        graph.add_node(vertex)
    for record in new_edges:
        if record.edge_id in endpoints or record.u not in graph or record.v not in graph or record.u >= record.v:
            raise ValueError("Invalid new edge patch")
        graph.add_edge(record.u, record.v, key=record.edge_id, color=record.color)
        endpoints[record.edge_id] = (record.u, record.v)

    removed_ids = {record.face_id for record in old_faces}
    for record in old_faces:
        pos = record.position
        if not 0 <= pos < len(state.g_faces) or state.face_ids[pos] != record.face_id:
            raise ValueError("Face patch precondition mismatch")
        actual = tuple((u, v, eid) for (u, v), eid in
                       zip(state.g_faces[pos], state.face_edge_ids[record.face_id]))
        if actual != record.darts:
            raise ValueError("Face dart precondition mismatch")
    remaining = [(fid, face[:], state.face_edge_ids[fid][:])
                 for fid, face in zip(state.face_ids, state.g_faces) if fid not in removed_ids]
    present_ids = {fid for fid, _, _ in remaining}
    positions = [record.position for record in new_faces]
    if len(set(positions)) != len(positions):
        raise ValueError("Duplicate face insertion position")
    for record in sorted(new_faces, key=lambda item: item.position):
        if record.face_id in present_ids or not 0 <= record.position <= len(remaining):
            raise ValueError("Invalid new face patch")
        remaining.insert(record.position, (record.face_id,
                                          [(u, v) for u, v, _ in record.darts],
                                          [eid for _, _, eid in record.darts]))
        present_ids.add(record.face_id)
    return OracleState(graph, [face for _, face, _ in remaining],
                       [fid for fid, _, _ in remaining],
                       {fid: ids for fid, _, ids in remaining}, endpoints, *counters)


def _check_witness(witness):
    step = witness.ariadne
    if not step or step[0] not in (2, 3, 4, 5) or len(step) != (5 if step[0] == 2 else 7):
        raise ValueError("Invalid Ariadne record")
    if step[1] == step[2]:
        raise ValueError("Reduction requires two distinct vertices")
    face = next((record for record in witness.before_faces
                 if record.face_id == witness.candidate.face_id), None)
    if face is None or len(face.darts) != step[0] or (step[1], step[2], witness.candidate.edge_id) not in face.darts:
        raise ValueError("Candidate and Ariadne record disagree")
    if step[0] != 2:
        position = face.darts.index((step[1], step[2], witness.candidate.edge_id))
        on_u = face.darts[(position - 1) % len(face.darts)][0]
        on_v = face.darts[(position + 1) % len(face.darts)][1]
        if (on_u, on_v) != step[3:5]:
            raise ValueError("Ariadne on-face neighbors disagree with the selected face")
    if any(after < before for before, after in zip(witness.before_next_ids, witness.after_next_ids)):
        raise ValueError("Allocation counters cannot go backwards in a reduction")


def _check_reduction_description(before, after, witness):
    """Check keyed color traces and local graph surgery, in forward direction.

    Faces are checked as a valid resulting embedding. Discovery of their
    local patch via join_faces/remove_vertex_from_face belongs to plan_step.
    """
    step = witness.ariadne
    u, v = step[1:3]
    incident = {vertex: [(b if a == vertex else a, eid)
                         for a, b, eid in before.graph.edges(vertex, keys=True)]
                for vertex in (u, v)}
    neighbors = ([v, v, step[3]], [u, u, step[4]]) if step[0] == 2 else (
        [v, step[3], step[5]], [u, step[4], step[6]])
    for vertex, expected in zip((u, v), neighbors):
        if Counter(b for b, _ in incident[vertex]) != Counter(expected):
            raise ValueError("Ariadne neighbors do not describe the source graph")
    removed = {eid for eid, ends in before.edge_endpoints.items() if u in ends or v in ends}
    if set(before.edge_endpoints) - set(after.edge_endpoints) != removed:
        raise ValueError("Patch removes edges outside the selected vertices")
    for old, new, start, stop in (
            (set(before.edge_endpoints), set(after.edge_endpoints), witness.before_next_ids[0], witness.after_next_ids[0]),
            (set(before.face_ids), set(after.face_ids), witness.before_next_ids[1], witness.after_next_ids[1])):
        if any(not start <= item < stop for item in new - old):
            raise ValueError("Patch reuses an already allocated ID")

    colors = {eid: before.graph[a][b][eid]["color"] for eid, (a, b) in before.edge_endpoints.items()}
    if step[0] == 2:
        if witness.swaps:
            raise ValueError("F2 does not need a swap trace")
    elif not witness.swaps or witness.swaps[-1].kind != "path":
        raise ValueError("Missing final partial swap")
    for number, swap in enumerate(witness.swaps):
        pair, darts = swap.colors, swap.darts
        if len(pair) != 2 or len(set(pair)) != 2 or any(c not in VALID_COLORS for c in pair) or not darts:
            raise ValueError("Invalid swap colors or empty trace")
        if swap.kind not in ("cycle", "path") or (swap.kind == "path" and number != len(witness.swaps) - 1):
            raise ValueError("Invalid swap order or kind")
        vertices = [dart[0] for dart in darts] + [darts[-1][1]]
        if any(darts[i][1] != darts[i + 1][0] for i in range(len(darts) - 1)):
            raise ValueError("Disconnected swap trace")
        if len({eid for _, _, eid in darts}) != len(darts):
            raise ValueError("Repeated swap edge")
        if swap.kind == "cycle":
            if vertices[0] != vertices[-1] or len(set(vertices[:-1])) != len(darts):
                raise ValueError("Invalid swap cycle")
        elif (vertices[0], vertices[-1]) != (u, v) or len(set(vertices)) != len(vertices):
            raise ValueError("Invalid partial swap endpoints")
        if swap.kind == "path" and colors[witness.candidate.edge_id] in pair:
            raise ValueError("Partial swap must use complementary colors")
        sequence = []
        for a, b, eid in darts:
            if before.edge_endpoints.get(eid) != (min(a, b), max(a, b)) or colors.get(eid) not in pair:
                raise ValueError("Invalid swap edge identity or color")
            sequence.append(colors[eid])
        adjacent = list(zip(sequence, sequence[1:]))
        if swap.kind == "cycle":
            adjacent.append((sequence[-1], sequence[0]))
        if any(a == b for a, b in adjacent):
            raise ValueError("Non-alternating swap trace")
        for _, _, eid in darts:
            colors[eid] = pair[1] if colors[eid] == pair[0] else pair[0]
    for eid in set(before.edge_endpoints) & set(after.edge_endpoints):
        a, b = after.edge_endpoints[eid]
        if (a, b) != before.edge_endpoints[eid] or after.graph[a][b][eid]["color"] != colors[eid]:
            raise ValueError("Retained edge disagrees with the swap trace")

    fused = []
    if step[0] == 2:
        outside = [(b, colors[eid]) for vertex in (u, v)
                   for b, eid in incident[vertex] if b not in (u, v)]
        if len(outside) != 2 or outside[0][1] != outside[1][1]:
            raise ValueError("F2 external colors do not agree")
        fused.append((*sorted((outside[0][0], outside[1][0])), outside[0][1]))
    else:
        for vertex in (u, v):
            remaining = [(b, colors[eid]) for b, eid in incident[vertex] if eid != witness.candidate.edge_id]
            if len(remaining) != 2 or remaining[0][1] != remaining[1][1]:
                raise ValueError("Partial swap does not permit fusion")
            fused.append((*sorted((remaining[0][0], remaining[1][0])), remaining[0][1]))
    created = Counter((a, b, after.graph[a][b][eid]["color"])
                      for eid, (a, b) in after.edge_endpoints.items() if eid not in before.edge_endpoints)
    if created != Counter(fused):
        raise ValueError("New edges do not match the certified fusions")


def _check_result(source, result, fingerprint, delta):
    assert (len(result.graph), result.graph.number_of_edges(), len(result.g_faces)) == (
        len(source.graph) + 2 * delta, source.graph.number_of_edges() + 3 * delta,
        len(source.g_faces) + delta), "Wrong reduction sizes"
    assert_state_invariants(result)
    if state_fingerprint(result) != fingerprint:
        raise ValueError("Certificate result fingerprint mismatch")


def _install(state, result):
    # All rejection points precede installation. Persistent IDs survive; the
    # caller must reacquire graph/list/index references after a successful step.
    state.graph = result.graph
    state.g_faces = result.g_faces
    state.face_ids = result.face_ids
    state.face_edge_ids = result.face_edge_ids
    state.edge_endpoints = result.edge_endpoints
    state.next_edge_id = result.next_edge_id
    state.next_face_id = result.next_face_id
    state.face_index = result.face_index
    state._validated_snapshot = result._validated_snapshot


def apply_step(state: OracleState, witness: StepWitness) -> None:
    _check_source(state, witness.before_fingerprint, witness.before_next_ids)
    _check_witness(witness)
    result = _patched_state(state, witness.before_edges, witness.after_edges,
                            witness.before_faces, witness.after_faces,
                            witness.ariadne[1:3], (), witness.after_next_ids)
    _check_result(state, result, witness.after_fingerprint, -1)
    _check_reduction_description(state, result, witness)
    _install(state, result)


def undo_step(state: OracleState, witness: StepWitness) -> None:
    _check_source(state, witness.after_fingerprint, witness.after_next_ids)
    _check_witness(witness)
    result = _patched_state(state, witness.after_edges, witness.before_edges,
                            witness.after_faces, witness.before_faces,
                            (), witness.ariadne[1:3], witness.before_next_ids)
    _check_result(state, result, witness.before_fingerprint, 1)
    _check_reduction_description(result, state, witness)
    _install(state, result)


def ordered_candidates(state: OracleState):
    """F2–F5, stable face ID, then edge ID; F5's unique color goes first.

    The F5 preference explicitly uses the oracle, not structural features.
    """
    faces = sorted((len(face), fid) for fid, face in zip(state.face_ids, state.g_faces)
                   if 2 <= len(face) <= 5)
    for size, fid in faces:
        ids = state.face_edge_ids[fid]
        colors = {eid: state.graph[u][v][eid]["color"]
                  for eid in ids for u, v in [state.edge_endpoints[eid]]}
        counts = Counter(colors.values())
        for eid in sorted(ids, key=lambda key: (size == 5 and counts[colors[key]] != 1, key)):
            yield Candidate(fid, eid)


def run_chain(state: OracleState, max_steps: int) -> ChainResult:
    """Mutate state along one deterministic branch; never claim impossibility."""
    if type(max_steps) is not int or max_steps < 0:
        raise ValueError("max_steps must be a nonnegative integer")
    assert_state_invariants(state)
    result = ChainResult("step_limit", [], [], state_fingerprint(state),
                         (len(state.graph), state.graph.number_of_edges(), len(state.g_faces)))
    while True:
        # Invariants already hold initially and after every atomic apply_step.
        if (len(state.graph), state.graph.number_of_edges(), len(state.g_faces)) == (2, 3, 3):
            result.status = "theta_reached"
            return result
        if len(result.witnesses) == max_steps:
            return result
        rejected = []
        witness = None
        candidates = iter(ordered_candidates(state))
        candidate = next(candidates, None)
        while candidate is not None and witness is None:
            attempt = plan_step(state, candidate)
            if attempt.status == "certified":
                witness = attempt.witness
            else:
                rejected.append(RejectedCandidate(candidate, attempt.status, attempt.reason))
                candidate = next(candidates, None)
        if witness is None:
            result.status = "no_certified_candidate"
            result.rejections = rejected
            return result
        apply_step(state, witness)
        result.witnesses.append(witness)


def replay_exact(terminal: OracleState, witnesses: Sequence[StepWitness]) -> OracleState:
    """Invert ordered certificates on an independent state, retaining its colors."""
    assert_state_invariants(terminal)
    restored = OracleState(
        terminal.graph.copy(), [face[:] for face in terminal.g_faces], terminal.face_ids[:],
        {fid: ids[:] for fid, ids in terminal.face_edge_ids.items()},
        terminal.edge_endpoints.copy(), terminal.next_edge_id, terminal.next_face_id,
    )
    for witness in reversed(witnesses):
        undo_step(restored, witness)
    return restored
