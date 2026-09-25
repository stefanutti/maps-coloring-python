"""Run from ct/: python tests/benchmark_selection5.py [--pattern GLOB].

Verify every matching JSONL map, with random choices forbidden. Prints
machine-readable results; debug output stays under ct/debug/ as usual.
"""
import argparse
from collections import Counter
import importlib.util
import json
import logging
from pathlib import Path
import sys
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", default="waterworld-*.planar")
    parser.add_argument("--kempe-search-limit", type=int, default=10000)
    args = parser.parse_args()
    ct = Path(__file__).resolve().parents[1]
    if Path.cwd() != ct:
        parser.error("Run this benchmark with ct/ as the working directory")
    sys.path.insert(0, str(ct))
    spec = importlib.util.spec_from_file_location("fourct_benchmark", ct / "4ct.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    logging.disable(logging.CRITICAL)
    mod.stats = {}

    def forbidden(*args, **kwargs):
        raise AssertionError("S5 attempted a random choice")

    mod.randint = forbidden
    mod.graph_random_edge = forbidden
    search = mod.find_kempe_repair

    def report_search(graph, first, second, limit):
        print(json.dumps({"search_vertices": len(graph), "split_edges": [first, second]}), flush=True)
        result = search(graph, first, second, limit)
        print(json.dumps({"search_states": result[3], "switches": len(result[0])}), flush=True)
        return result

    mod.find_kempe_repair = report_search
    files = sorted((ct / "examples/planar").glob(args.pattern))
    if not files:
        parser.error("No maps matched")
    for path in files:
        for line, raw in enumerate(path.read_text().splitlines(), 1):
            if raw.strip():
                faces = [[tuple(edge) for edge in face] for face in json.loads(raw)]
                directed = Counter(edge for face in faces for edge in face)
                assert all(directed[u, v] == directed[v, u] for u, v in directed)
                expected = Counter({(u, v): count for (u, v), count in directed.items() if u < v})
                vertices = {v for edge in directed for v in edge}
                mod.initialize_statistics()
                mod.init_f_distribution(faces)
                print(json.dumps({"start": path.name, "line": line, "faces": len(faces),
                                  "vertices": len(vertices)}), flush=True)
                start = time.perf_counter()
                thread = mod.reduce_faces(faces, 2345, mod.select_edge_to_remove_positive_corner)
                reduction_seconds = time.perf_counter() - start
                print(json.dumps({"reduced": path.name, "seconds": round(reduction_seconds, 3)}), flush=True)
                graph = mod.rebuild_faces(faces, thread, kempe_search_limit=args.kempe_search_limit)
                actual = Counter(tuple(sorted((u, v))) for u, v in graph.edges())
                assert actual == expected and set(graph) == vertices
                assert mod.is_well_colored(graph) and mod.is_graph_regular(graph, 3)
                assert not thread and mod.stats['TOTAL_RANDOM_KEMPE_SWITCHES'] == 0
                result = {"map": path.name, "line": line, "vertices": len(vertices),
                          "edges": graph.number_of_edges(), "valid": True,
                          "reduction_seconds": round(reduction_seconds, 3),
                          "total_seconds": round(time.perf_counter() - start, 3)}
                result.update({key: value for key, value in mod.stats.items()
                               if key.startswith(('S5-', 'SELECT-S5-', 'TOTAL_RANDOM'))})
                print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
