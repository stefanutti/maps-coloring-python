import unittest

from kempe.analysis import analyze, build_graph, TransitionGraph, IncompleteGraphError
from kempe.moves import Action, Move
from kempe.enumeration import enumerate_states
from kempe.model import Classification
from kempe.explain import Explain


class AnalysisTests(unittest.TestCase):
    def graph(self, actions):
        return TransitionGraph(tuple(range(len(actions))), tuple(tuple(a) for a in actions))

    def verdict(self, node):
        return Classification('good' if node == 2 else 'bad', 'test fixture')

    def test_may_scc_absence_does_not_prove_escape(self):
        action = Action((0, 1), (0,))
        # At 0 the same action MAY stay at 0 or reach good 2. No forced escape.
        graph = self.graph([[Move(action, (0, 2))], [Move(action, (0,))], [Move(action, (2,))]])
        report = analyze(graph, self.verdict)
        self.assertEqual(report['closed_bad_sccs'], [])
        self.assertEqual(report['bad_kernel'], [0, 1])
        self.assertEqual(report['bad_sccs'], [[0], [1]])

    def test_forced_escape_has_layered_witness(self):
        action = Action((0, 1), (0,))
        graph = self.graph([[Move(action, (1,))], [Move(action, (2,))], [Move(action, (2,))]])
        trace = Explain()
        report = analyze(graph, self.verdict, explain=trace)
        self.assertEqual(report['bad_kernel'], [])
        self.assertEqual([(e['state'], e['round']) for e in report['eliminations']], [(1, 1), (0, 2)])
        self.assertEqual(trace.counts['kernel.no_bad_successor'], 2)

    def test_optional_remote_action_cannot_force_elimination(self):
        mandatory = Action((0, 1), (0,))
        optional = Action((2, 3), ())
        graph = self.graph([[Move(mandatory, (0,)), Move(optional, (2,))], [], []])
        report = analyze(graph, self.verdict)
        self.assertIn(0, report['bad_kernel'])
        self.assertNotIn([0], report['closed_bad_sccs'])

    def test_closure_is_checked_in_full_graph_not_bad_induced_graph(self):
        action = Action((0, 1), (0,))
        graph = self.graph([[Move(action, (1,))], [Move(action, (0, 2))], []])
        report = analyze(graph, self.verdict)
        self.assertEqual(report['bad_sccs'], [[0, 1]])
        self.assertEqual(report['closed_bad_sccs'], [])

    def test_unknown_never_becomes_a_proved_escape(self):
        action = Action((0, 1), (0,))
        graph = self.graph([[Move(action, (1,))], []])
        classify = lambda i: Classification('bad' if i == 0 else 'unknown', 'test')
        report = analyze(graph, classify)
        self.assertEqual(report['bad_kernel'], [])
        self.assertEqual(report['non_good_kernel'], [0, 1])
        self.assertFalse(report['all_states_forced_good'])

    def test_graph_limits_and_missing_successors_fail_closed(self):
        states = tuple(enumerate_states(quotient_colors=True))
        with self.assertRaises(IncompleteGraphError):
            build_graph(states[:1], quotient_colors=True)
        with self.assertRaises(IncompleteGraphError):
            build_graph(states, quotient_colors=True, max_edges=1)
        with self.assertRaises(ValueError):
            self.graph([[Move(Action((0, 1), (0,)), (99,))]])

    def test_quotient_graph_matches_projection_of_labeled_graph(self):
        raw = build_graph(tuple(enumerate_states()))
        small = build_graph(tuple(enumerate_states(quotient_colors=True)), quotient_colors=True)
        expected = {(raw.states[u].canonical_colors(), raw.states[v].canonical_colors())
                    for u, neighbors in enumerate(raw.adjacency) for v in neighbors}
        actual = {(small.states[u], small.states[v])
                  for u, neighbors in enumerate(small.adjacency) for v in neighbors}
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
