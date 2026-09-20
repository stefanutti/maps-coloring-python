import itertools
import unittest

from kempe.model import COLORS, PAIRS, State, r5
from kempe.enumeration import enumerate_states, rejection_reasons
from kempe.moves import kempe_moves
from kempe.explain import Explain


def components(n, edges, colors, pair):
    """Independent concrete-graph oracle, not the abstract transition code."""
    remaining = {v for v in range(n) if colors[v] in pair}
    adjacency = {v: set() for v in range(n)}
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    result = []
    while remaining:
        root = min(remaining)
        reached, stack = {root}, [root]
        remaining.remove(root)
        while stack:
            for v in adjacency[stack.pop()] & remaining:
                remaining.remove(v)
                reached.add(v)
                stack.append(v)
        result.append(reached)
    return result


def project(n, edges, colors):
    return State(tuple(colors[:5]), tuple(
        tuple(tuple(sorted(block & set(range(5)))) for block in components(n, edges, colors, pair)
              if block & set(range(5))) for pair in PAIRS))


def colorings(n, edges):
    adjacent = [{u for u, v in edges if v == i} | {v for u, v in edges if u == i}
                for i in range(n)]
    word = [-1] * n
    def visit(i):
        if i == n:
            yield tuple(word)
        else:
            for c in COLORS:
                if all(word[j] != c for j in adjacent[i]):
                    word[i] = c
                    yield from visit(i + 1)
            word[i] = -1
    yield from visit(0)


class MoveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.states = tuple(enumerate_states(quotient_colors=True))

    def test_all_and_only_invariant_compatible_successors(self):
        by_word = {}
        for state in enumerate_states():
            by_word.setdefault(state.boundary, set()).add(state)
        for state in self.states:
            for move in kempe_moves(state):
                pair, block = move.action.pair, move.action.block
                other = tuple(c for c in COLORS if c not in pair)
                # Explicit form avoids coupling expected boundary to implementation helpers.
                boundary = list(state.boundary)
                for i in block:
                    boundary[i] = pair[1] if boundary[i] == pair[0] else pair[0]
                expected = {t for t in by_word[tuple(boundary)]
                            if t.partition(pair) == state.partition(pair)
                            and t.partition(other) == state.partition(other)}
                self.assertEqual(set(move.targets), expected)
                self.assertTrue(expected)

    def test_each_boundary_component_is_mandatory_remote_is_optional(self):
        for state in self.states:
            moves = tuple(kempe_moves(state))
            self.assertEqual({(m.action.pair, m.action.block) for m in moves if m.action.guaranteed},
                             {(p, block) for p in PAIRS for block in state.partition(p)})
            self.assertEqual(len([m for m in moves if not m.action.guaranteed]), 6)

    def test_move_explanations_include_candidate_enumeration_exclusions(self):
        state = next(enumerate_states(boundaries=((0, 1, 0, 1, 2),)))
        trace = Explain()
        list(kempe_moves(state, explain=trace))
        self.assertGreater(trace.counts['partition.boundary_edge'], 0)
        self.assertGreater(trace.counts['planarity.same_pair_cross'], 0)
        self.assertGreater(trace.counts['planarity.disjoint_colors_cross'], 0)

    def test_exchange_lemma_all_admissible_bad_states(self):
        for state in self.states:
            verdict = r5(state)
            if verdict.kind != 'bad':
                continue
            sector = int(verdict.sector[1:])
            for i in (sector, (sector - 2) % 5):
                u, v = (i + 1) % 5, (i + 3) % 5
                pair = tuple(sorted((state.boundary[u], state.boundary[v])))
                if not state.linked(pair, u, v):
                    move = next(m for m in kempe_moves(state) if m.action.pair == pair and u in m.action.block)
                    self.assertTrue(all(r5(t).kind == 'good' for t in move.targets))

    def test_remote_switch_can_change_boundary_connectivity(self):
        edges = [(i, (i + 1) % 5) for i in range(5)] + [(0, 5), (2, 5)]
        before = project(6, edges, (0, 1, 0, 2, 3, 1))
        after = project(6, edges, (0, 1, 0, 2, 3, 2))
        # Vertex 5 is an internal 1/2 component; changing it joins a0/a2 in 0/2.
        self.assertFalse(before.linked((0, 2), 0, 2))
        self.assertTrue(after.linked((0, 2), 0, 2))
        self.assertEqual(before.boundary, after.boundary)
        self.assertNotEqual(before, after)
        move = next(m for m in kempe_moves(before) if m.action.pair == (1, 2) and not m.action.block)
        self.assertFalse(move.action.guaranteed)
        self.assertIn(after, move.targets)

    def test_every_concrete_switch_is_covered_on_small_planar_disks(self):
        cycle = [(i, (i + 1) % 5) for i in range(5)]
        # Q = icosahedron minus one degree-five vertex: induced outer pentagon,
        # inner ring and one centre. Also simpler disks outside the R5 family.
        annulus = cycle + [(5 + i, 5 + (i + 1) % 5) for i in range(5)]
        annulus += [(i, 5 + i) for i in range(5)]
        annulus += [(i, 5 + (i - 1) % 5) for i in range(5)]
        annulus += [(5 + i, 10) for i in range(5)]
        checked = 0
        for n, edges in [(5, cycle), (6, cycle + [(1, 5), (3, 5)]), (11, annulus)]:
            for colors in colorings(n, edges):
                # One orbit per global color permutation suffices for graph fixtures.
                if tuple(dict.fromkeys(colors)) != tuple(range(len(set(colors)))):
                    continue
                state = project(n, edges, colors)
                self.assertEqual(rejection_reasons(state), ())
                moves = {(m.action.pair, m.action.block): m for m in kempe_moves(state)}
                for pair in PAIRS:
                    for component in components(n, edges, colors, pair):
                        swapped = list(colors)
                        for v in component:
                            swapped[v] = pair[1] if colors[v] == pair[0] else pair[0]
                        target = project(n, edges, swapped)
                        key = pair, tuple(sorted(component & set(range(5))))
                        self.assertIn(target, moves[key].targets)
                        checked += 1
        self.assertGreater(checked, 500)


if __name__ == '__main__':
    unittest.main()
