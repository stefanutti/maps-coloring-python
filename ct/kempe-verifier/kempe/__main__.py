"""Run with python3 -m kempe; no third-party dependencies required."""

import argparse
from contextlib import ExitStack
import importlib
from itertools import combinations
import json
from pathlib import Path
import sys

from .analysis import IncompleteGraphError, analyze, build_graph
from .enumeration import enumerate_states
from .explain import Explain
from .model import State, r5
from .moves import kempe_moves
from .pairing import TransitionPairing

SOURCE = {'document': '4ct-v16.md', 'sections': ['9.8', '9.14', '9.15', '10.3–10.9'],
          'sha256': '68a06cdd35bafeba9607331ca8a6aeb31101d856500b1fbadba74a08d1e12b4c'}


def parser():
    root = argparse.ArgumentParser(description='Verificatore conservativo degli stati Kempe di bordo (v16).')
    commands = root.add_subparsers(dest='command', required=True)
    for command in ('analyze', 'enumerate', 'moves', 'pairing-example'):
        sub = commands.add_parser(command)
        sub.add_argument('--output', default='-', help='Rapporto JSON; default stdout')
        if command != 'pairing-example':
            sub.add_argument('--quotient-colors', action='store_true', help='Quoziente per S4, terminali fissi')
            sub.add_argument('--explain', type=Path, help='Registro completo delle eliminazioni in JSONL')
        if command in ('analyze', 'enumerate'):
            sub.add_argument('--max-states', type=int, default=100000)
        if command == 'analyze':
            sub.add_argument('--max-edges', type=int, default=1000000)
            sub.add_argument('--classifier', default='r5', help='r5 oppure modulo:funzione Python')
            sub.add_argument('--include-graph', action='store_true', help='Esporta tutti i successori per azione')
            sub.add_argument('--dot', type=Path, help='Esporta il grafo may in formato Graphviz DOT')
        if command == 'moves':
            sub.add_argument('--state', required=True, type=Path, help='Singolo State JSON')
    return root


def load_classifier(spec):
    if spec == 'r5':
        return r5
    if ':' not in spec:
        raise ValueError('Classifier syntax: module:function')
    module, name = spec.split(':', 1)
    classifier = getattr(importlib.import_module(module), name)
    if not callable(classifier):
        raise ValueError('Classifier is not callable')
    return classifier


def validate_paths(args):
    paths = [Path(args.output)] if args.output != '-' else []
    for name in ('explain', 'dot', 'state'):
        path = getattr(args, name, None)
        if path is not None:
            paths.append(path)
    if len({path.resolve() for path in paths}) != len(paths):
        raise ValueError('Input, output, explain and DOT paths must be distinct')
    for left, right in combinations(paths, 2):
        if left.exists() and right.exists() and left.samefile(right):
            raise ValueError('Input and output paths must not be hard links to the same file')


def write_dot(graph, verdicts, path):
    colors = {'good': 'palegreen', 'bad': 'mistyrose', 'unknown': 'lightgray'}
    with path.open('w', encoding='utf-8') as output:
        output.write('digraph Kempe {\n  // MAY edges: no concrete realizability claim\n')
        for i, state in enumerate(graph.states):
            label = f'{i}: ' + ''.join(map(str, state.boundary)) + ' ' + str(verdicts[i]['sector'])
            output.write(f'  n{i} [label={json.dumps(label)}, style=filled, fillcolor={colors[verdicts[i]["kind"]]}];\n')
        for u, neighbors in enumerate(graph.adjacency):
            for v in neighbors:
                output.write(f'  n{u} -> n{v};\n')
        output.write('}\n')


def run(args, trace):
    if args.command == 'pairing-example':
        examples = []
        for matching in (((0, 1), (2, 4), (3, 5)), ((0, 1), (2, 5), (3, 4))):
            pairing = TransitionPairing(matching)
            examples.append({'matching': pairing.matching, 'pages': pairing.two_page_assignment(),
                             'before': pairing.closure_partition(((0, 1), (2, 3), (4, 5))),
                             'after': pairing.closure_partition(((1, 2), (3, 4), (5, 0)))})
        return {'status': 'exact_pairing_example', 'source': SOURCE, 'examples': examples}
    if args.command == 'moves':
        state = State.from_dict(json.loads(args.state.read_text(encoding='utf-8')))
        if args.quotient_colors:
            state = state.canonical_colors()
        return {'status': 'conservative_moves', 'source': SOURCE, 'state': state.to_dict(),
                'moves': [{'action': m.action.to_dict(), 'targets': [t.to_dict() for t in m.targets]}
                          for m in kempe_moves(state, args.quotient_colors, explain=trace)]}
    if args.max_states < 1:
        raise ValueError('max-states must be positive')
    classifier = load_classifier(args.classifier) if args.command == 'analyze' else r5
    if args.quotient_colors and classifier is not r5:
        raise ValueError('Custom classifier requires fixed labels; omit --quotient-colors')
    states = []
    for state in enumerate_states(quotient_colors=args.quotient_colors, explain=trace):
        states.append(state)
        if len(states) > args.max_states:
            raise IncompleteGraphError('State limit exceeded; no partial analysis performed')
    if args.command == 'enumerate':
        report = {'status': 'complete_necessary_state_enumeration', 'state_count': len(states),
                  'quotient_colors': args.quotient_colors,
                  'realizability_certified': False}
    else:
        graph = build_graph(states, quotient_colors=args.quotient_colors, explain=trace,
                            max_edges=args.max_edges)
        report = analyze(graph, classifier, trace)
        report['classifier'] = args.classifier
        if args.include_graph:
            report['actions'] = [[{'action': m.action.to_dict(), 'targets': list(m.targets)}
                                  for m in moves] for moves in graph.moves]
        if args.dot is not None:
            write_dot(graph, report['classifications'], args.dot)
    report['source'] = SOURCE
    report['states'] = [s.to_dict() for s in states]
    return report


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        validate_paths(args)
        with ExitStack() as stack:
            trace_path = getattr(args, 'explain', None)
            stream = stack.enter_context(trace_path.open('w', encoding='utf-8')) if trace_path else None
            trace = Explain(stream) if stream is not None else None
            report = run(args, trace)
            if trace is not None:
                report['explain'] = trace.summary()
            if args.output == '-':
                json.dump(report, sys.stdout, indent=2)
                sys.stdout.write('\n')
            else:
                Path(args.output).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        return 0
    except (ValueError, TypeError, KeyError, AttributeError, ImportError, OSError) as error:
        status = 'incomplete' if isinstance(error, IncompleteGraphError) else 'error'
        print(json.dumps({'status': status, 'message': str(error), 'r5_proved': False}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
