"""Exploratory probe of initial colored maps; not part of the 4ct pipeline."""
import argparse
from collections import Counter
import importlib.util
import json
import logging
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'ct'))
import networkx as nx
from ct_graph_utils import (
    apply_half_kempe_loop_color_switching, get_edge_color, graph_add_edge,
    graph_delete_edge, is_the_graph_one_edge_connected, is_well_colored,
    join_faces, remove_vertex_from_face,
)

spec = importlib.util.spec_from_file_location('fourct_oracle_probe', ROOT / 'ct/4ct.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
logging.disable(logging.CRITICAL)


def colored_edges(graph):
    return Counter((min(u, v), max(u, v), data['color'])
                   for u, v, data in graph.edges(data=True))


def check_one_step(graph, faces, face_index, face_number, edge_number):
    face = faces[face_number]
    u, v = face[edge_number]
    neighbor = face_index.first_face_with_edge((v, u), exclude_face=face)
    on_u = face[(edge_number - 1) % 5][0]
    on_v = face[(edge_number + 1) % 5][1]
    off_u = next(b for a, b in neighbor if a == u)
    off_v = next(a for a, b in neighbor if b == v)
    deleted_color = get_edge_color(graph, (u, v))
    pair = tuple(c for c in ('red', 'green', 'blue') if c != deleted_color)

    # Trace one arc of the complementary bicolored cycle, starting on the F5.
    current, following = u, on_u
    path = []
    while True:
        keys = list(graph[current][following])
        assert len(keys) == 1, 'Prototype path tracing requires simple initial edges'
        key = keys[0]
        path.append((current, following, key))
        if following == v:
            assert current == on_v, 'The chosen arc does not end on the F5 side'
            break
        assert following != u, 'Endpoints are in different complementary cycles'
        next_edges = [(following, other, k) for other, edges in graph[following].items()
                      for k, data in edges.items()
                      if data['color'] in pair and (other, k) != (current, key)]
        assert len(next_edges) == 1
        current, following, _ = next_edges[0]

    reduced = graph.copy()
    graph_delete_edge(reduced, u, v, deleted_color)
    for a, b, key in path:
        old = reduced[a][b][key]['color']
        reduced[a][b][key]['color'] = pair[1] if old == pair[0] else pair[0]
    fused_colors = []
    for vertex, on_face, off_face in ((u, on_u, off_u), (v, on_v, off_v)):
        color = get_edge_color(reduced, (vertex, on_face))
        assert color == get_edge_color(reduced, (vertex, off_face))
        fused_colors.append(color)
        reduced.remove_node(vertex)
        graph_add_edge(reduced, on_face, off_face, color)

    assert reduced.number_of_nodes() == graph.number_of_nodes() - 2
    assert reduced.number_of_edges() == graph.number_of_edges() - 3
    assert is_well_colored(reduced)
    assert nx.number_of_selfloops(reduced) == 0
    assert not list(nx.bridges(reduced))

    # Independently compare against the program's face surgery primitives.
    reduced_faces = [join_faces(face, neighbor, (u, v))]
    for other in faces:
        if other is not face and other is not neighbor:
            copied = other[:]
            for vertex in (u, v):
                if any(a == vertex for a, _ in copied):
                    remove_vertex_from_face(copied, vertex)
            reduced_faces.append(copied)
    actual = Counter(edge for other in reduced_faces for edge in other)
    expected = Counter()
    for a, b in reduced.edges():
        expected[a, b] += 1
        expected[b, a] += 1
    assert actual == expected

    step = [5, u, v, on_u, on_v, off_u, off_v]
    restored = reduced.copy()
    first = fused_colors[0]
    second = next(c for c in pair if c != first)
    apply_half_kempe_loop_color_switching(restored, step, *fused_colors, first, second)
    assert set(restored) == set(graph)
    assert colored_edges(restored) == colored_edges(graph)

    # Also exercise the unmodified F5 reconstruction handler.
    rebuilt = reduced.copy()
    mod.stats = {}
    mod.initialize_statistics()
    mod.ariadne_case_f5(rebuilt, step, kempe_search_limit=100)
    assert is_well_colored(rebuilt)
    assert Counter(tuple(sorted(e)) for e in rebuilt.edges()) == Counter(
        tuple(sorted(e)) for e in graph.edges())
    assert mod.stats['S5-F5-DIRECT'] == 1
    return {'path_edges': len(path), 'reduced_coloring_valid': True,
            'face_surgery_matches': True, 'exact_inverse_colors': True,
            'existing_f5_handler_direct': True,
            'handler_matches_original_colors': colored_edges(rebuilt) == colored_edges(graph)}


def analyze(raw, map_number, include_example):
    faces = [[(edge[0], edge[1]) for edge in face] for face in raw]
    face_index = mod.FaceIndex(faces)
    graph = nx.MultiGraph()
    for face in raw:
        for u, v, color in face:
            if u < v:
                graph_add_edge(graph, u, v, color)
    components = {}
    for omitted in ('red', 'green', 'blue'):
        bicolored = nx.Graph()
        bicolored.add_nodes_from(graph)
        bicolored.add_edges_from((u, v) for u, v, data in graph.edges(data=True)
                                if data['color'] != omitted)
        components[omitted] = {vertex: index
                               for index, group in enumerate(nx.connected_components(bicolored))
                               for vertex in group}

    counts = Counter()
    per_face_direct = Counter()
    examples = {}
    for face_number, colored_face in enumerate(raw):
        if len(colored_face) != 5:
            continue
        face = faces[face_number]
        counts['pentagons'] += 1
        multiplicities = Counter(edge[2] for edge in colored_face)
        singleton = next(color for color, number in multiplicities.items() if number == 1)
        assert sorted(multiplicities.values()) == [1, 2, 2]
        candidates = []
        direct_count = 0
        degrees = [len(face_index.first_face_with_edge((v, u), exclude_face=face))
                   for u, v in face]
        for edge_number, (u, v, color) in enumerate(colored_face):
            neighbor = face_index.first_face_with_edge((v, u), exclude_face=face)
            structural = not is_the_graph_one_edge_connected(join_faces(face, neighbor, (u, v)))
            same_cycle = components[color][u] == components[color][v]
            local = color == singleton
            counts['candidates'] += 1
            counts['structurally_admissible'] += structural
            counts['same_complementary_cycle'] += same_cycle
            counts['admissible_same_cycle'] += structural and same_cycle
            counts['singleton_witnesses'] += local
            counts['singleton_admissible'] += local and structural
            counts['other_same_cycle'] += same_cycle and not local
            counts['unresolved_without_extra_switches'] += structural and not same_cycle
            direct_count += structural and same_cycle
            if include_example:
                forward = tuple(degrees[(edge_number + offset) % 5] for offset in range(5))
                backward = tuple(degrees[(edge_number - offset) % 5] for offset in range(5))
                record = {
                    'edge_number': edge_number, 'edge': [u, v],
                    'structure': {'neighbor_degree': degrees[edge_number],
                                  'admissible': structural,
                                  'rooted_neighbor_signature': min(forward, backward)},
                    'oracle': {'input_color': color, 'singleton': local,
                               'same_complementary_cycle': same_cycle},
                }
                candidates.append(record)
        per_face_direct[direct_count] += 1
        if include_example and direct_count not in examples:
            for record in candidates:
                if record['structure']['admissible'] and record['oracle']['same_complementary_cycle']:
                    record['oracle']['experiment'] = check_one_step(
                        graph, faces, face_index, face_number, record['edge_number'])
            examples[direct_count] = {
                'map_number': map_number, 'face_index': face_number,
                'structure': {'face': face, 'neighbor_degrees': degrees},
                'oracle': {'face': colored_face}, 'candidates': candidates}
    summary = {'map_number': map_number, 'faces': len(faces), **dict(counts),
               'direct_choices_per_f5': dict(sorted(per_face_direct.items()))}
    return summary, examples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=1)
    parser.add_argument('--input', type=Path,
                        default=ROOT / 'ct/maps_3000_maps_of_8000_faces.colored.planar')
    args = parser.parse_args()
    if args.limit < 1:
        parser.error('--limit must be positive')
    all_maps = []
    totals = Counter()
    distributions = Counter()
    examples = None
    source = args.input
    with source.open() as stream:
        for number, line in enumerate(stream, 1):
            if number > args.limit:
                break
            summary, first_example = analyze(json.loads(line), number, number == 1)
            all_maps.append(summary)
            if first_example:
                examples = first_example
            totals.update({k: v for k, v in summary.items()
                           if k not in ('map_number', 'faces', 'direct_choices_per_f5')})
            distributions.update(summary['direct_choices_per_f5'])
            if number % 10 == 0:
                print(json.dumps({'progress_maps': number,
                                  'pentagons': totals['pentagons']}), flush=True)
    print(json.dumps({'maps': len(all_maps), 'totals': dict(totals),
                      'direct_choices_per_f5': dict(sorted(distributions.items())),
                      'examples': examples,
                      'per_map_ranges': {
                          key: [min(m[key] for m in all_maps), max(m[key] for m in all_maps)]
                          for key in ('faces', 'pentagons', 'admissible_same_cycle')},
                      'all_maps_have_only_1_3_5_direct_choices': all(
                          set(m['direct_choices_per_f5']) <= {1, 3, 5} for m in all_maps)}))


if __name__ == '__main__':
    main()
