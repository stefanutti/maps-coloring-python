"""May graph SCCs and a separate forall-actions/exists-successor bad kernel."""

from collections import Counter
from dataclasses import dataclass, field

from .model import Classification, State, r5
from .moves import Move, kempe_moves


class IncompleteGraphError(ValueError):
    """A partial graph must never be used to assert closure or forced escape."""


@dataclass(frozen=True)
class TransitionGraph:
    states: tuple
    moves: tuple
    adjacency: tuple = field(init=False)
    quotient_colors: bool = False
    assumptions: tuple = ()

    def __post_init__(self):
        if len(self.states) != len(self.moves) or len(set(self.states)) != len(self.states):
            raise ValueError('Unique states and one action list per state are required')
        adjacency = []
        for moves in self.moves:
            if len({m.action for m in moves}) != len(moves):
                raise ValueError('Duplicate actions: alternative targets must be grouped')
            neighbors = set()
            for move in moves:
                if not move.targets and move.action.guaranteed:
                    raise IncompleteGraphError('A guaranteed action has no admissible successor')
                if any(type(v) is not int or not 0 <= v < len(self.states) for v in move.targets):
                    raise ValueError('Target index is outside the graph')
                neighbors.update(move.targets)
            adjacency.append(tuple(sorted(neighbors)))
        object.__setattr__(self, 'adjacency', tuple(adjacency))


def build_graph(states, quotient_colors=False, constraints=(), explain=None, max_edges=None):
    states = tuple(states)
    if max_edges is not None and max_edges < 1:
        raise ValueError('max_edges must be positive')
    index = {state: i for i, state in enumerate(states)}
    moves_by_state = []
    edge_count = 0
    for state in states:
        if quotient_colors and state.canonical_colors() != state:
            raise ValueError('Color quotient requires canonical input states')
        indexed_moves = []
        neighbors = set()
        for move in kempe_moves(state, quotient_colors, constraints, explain):
            targets = []
            for target in move.targets:
                if target not in index:
                    raise IncompleteGraphError('Successor missing from state space; no closure analysis performed')
                targets.append(index[target])
            indexed_moves.append(Move(move.action, tuple(targets)))
            neighbors.update(targets)
        edge_count += len(neighbors)
        if max_edges is not None and edge_count > max_edges:
            raise IncompleteGraphError('Edge limit exceeded; no partial graph returned')
        moves_by_state.append(tuple(indexed_moves))
    assumptions = tuple({'name': c.name, 'source': c.source} for c in constraints)
    return TransitionGraph(states, tuple(moves_by_state), quotient_colors=quotient_colors,
                           assumptions=assumptions)


def strongly_connected_components(adjacency):
    """Iterative Kosaraju: supports graphs larger than Python's recursion limit."""
    visited, finish = set(), []
    for root in range(len(adjacency)):
        if root in visited:
            continue
        visited.add(root)
        stack = [(root, iter(adjacency[root]))]
        while stack:
            node, children = stack[-1]
            child = next(children, None)
            if child is None:
                finish.append(node)
                stack.pop()
            elif child not in visited:
                visited.add(child)
                stack.append((child, iter(adjacency[child])))
    reverse = [[] for _ in adjacency]
    for u, neighbors in enumerate(adjacency):
        for v in neighbors:
            reverse[v].append(u)
    visited, components = set(), []
    for root in reversed(finish):
        if root in visited:
            continue
        visited.add(root)
        stack, component = [root], []
        while stack:
            node = stack.pop()
            component.append(node)
            for child in reverse[node]:
                if child not in visited:
                    visited.add(child)
                    stack.append(child)
        components.append(sorted(component))
    return sorted(components)


def survival_kernel(graph, candidates, explain=None, event_prefix='kernel'):
    """Greatest X where every guaranteed action has at least one target in X."""
    remaining = set(candidates)
    eliminations, round_number = [], 0
    while remaining:
        removed = []
        for node in sorted(remaining):
            for move in graph.moves[node]:
                if move.action.guaranteed and not remaining.intersection(move.targets):
                    removed.append((node, move))
                    break
        if not removed:
            break
        round_number += 1
        for node, move in removed:
            witness = {'state': node, 'round': round_number, 'action': move.action.to_dict(),
                       'targets': list(move.targets)}
            eliminations.append(witness)
            if explain is not None:
                explain.record(f'{event_prefix}.no_bad_successor',
                               'All possible successors of this guaranteed action are outside the current candidate set',
                               **witness)
        remaining.difference_update(node for node, _ in removed)
    return sorted(remaining), eliminations


def analyze(graph, classifier=r5, explain=None):
    if graph.quotient_colors and classifier is not r5:
        raise ValueError('Custom classifiers require fixed labels; S4 invariance is not assumed')
    verdicts = tuple(classifier(state) for state in graph.states)
    if any(not isinstance(v, Classification) for v in verdicts):
        raise TypeError('Classifier must return Classification')
    bad = {i for i, v in enumerate(verdicts) if v.kind == 'bad'}
    non_good = {i for i, v in enumerate(verdicts) if v.kind != 'good'}
    sccs = strongly_connected_components(graph.adjacency)
    bad_sccs = [scc for scc in sccs if set(scc) <= bad]
    closed_bad = [scc for scc in bad_sccs
                  if all(set(graph.adjacency[v]) <= set(scc) for v in scc)]
    kernel, eliminated = survival_kernel(graph, bad, explain)
    if non_good == bad:
        non_good_kernel, non_good_eliminated = kernel, eliminated
    else:
        non_good_kernel, non_good_eliminated = survival_kernel(graph, non_good, explain, 'non_good_kernel')
    return {
        'status': 'complete_abstract_analysis',
        'semantics': 'may transitions; alternative successors grouped by switch',
        'r5_proved': False,
        'interpretation': 'Abstract candidates are not realizability certificates or concrete coloring counts.',
        'quotient_colors': graph.quotient_colors,
        'additional_assumptions': list(graph.assumptions),
        'state_count': len(graph.states),
        'edge_count': sum(map(len, graph.adjacency)),
        'action_count': sum(map(len, graph.moves)),
        'classification_counts': dict(Counter(v.kind for v in verdicts)),
        'sector_counts_abstract': dict(Counter(v.sector for v in verdicts if v.sector is not None)),
        'classifications': [{'kind': v.kind, 'reason': v.reason, 'sector': v.sector,
                             'fans': list(v.fans)} for v in verdicts],
        'sccs': sccs, 'bad_sccs': bad_sccs, 'closed_bad_sccs': closed_bad,
        'bad_kernel': kernel, 'eliminations': eliminated,
        'non_good_kernel': non_good_kernel, 'non_good_eliminations': non_good_eliminated,
        'all_states_forced_good': bool(graph.states) and not non_good_kernel,
    }
