import itertools
import unittest
from collections import Counter

from kempe.model import PAIRS, State, r5, canonical_partition
from kempe.enumeration import enumerate_states, boundary_words, rejection_reasons
from kempe.explain import Explain


class ModelTests(unittest.TestCase):
    def test_proper_words_and_r5_counts(self):
        words = list(boundary_words())
        self.assertEqual(len(words), 240)
        verdicts = [r5(w) for w in words]
        self.assertEqual(Counter(v.kind for v in verdicts), {'good': 120, 'bad': 120})
        self.assertEqual(Counter(v.sector for v in verdicts),
                         {f'{k}{i}': 24 for k in 'EB' for i in range(5)})
        for word, verdict in zip(words, verdicts):
            fans = tuple(i for i in range(5)
                         if word[i] != word[(i + 2) % 5]
                         and word[i] != word[(i + 3) % 5])
            self.assertEqual(verdict.fans, fans)
            self.assertEqual(len(fans), 1 if verdict.kind == 'good' else 3)

    def test_canonical_partitions_are_not_matchings(self):
        self.assertEqual(canonical_partition(((3,), (2, 0, 1))), ((0, 1, 2), (3,)))
        for invalid in (((0, 0),), ((0,), (0,)), ((),), ((5,),), ((True,),)):
            with self.assertRaises(ValueError):
                canonical_partition(invalid)

    def test_state_validates_membership_and_boundary(self):
        state = next(enumerate_states())
        self.assertEqual(State.from_dict(state.to_dict()), state)
        with self.assertRaises(ValueError):
            State((0, 0, 1, 2, 3), state.partitions)
        parts = list(state.partitions)
        parts[0] = ()
        with self.assertRaises(ValueError):
            State(state.boundary, tuple(parts))

    def test_color_quotient_relabels_all_six_pairs(self):
        state = next(s for s in enumerate_states() if r5(s).kind == 'bad')
        expected = state.canonical_colors()
        for perm in itertools.permutations(range(4)):
            renamed = state.relabel_colors(perm)
            self.assertEqual(renamed.canonical_colors(), expected)
            for pair in PAIRS:
                self.assertEqual(state.partition(pair),
                                 renamed.partition(tuple(sorted(perm[c] for c in pair))))
        self.assertEqual(len(list(boundary_words(quotient_colors=True))), 10)

    def test_enumerated_states_have_only_necessary_constraints(self):
        states = list(enumerate_states())
        self.assertTrue(states)
        self.assertEqual(len(states), len(set(states)))
        for state in states:
            self.assertEqual(rejection_reasons(state), ())
        self.assertEqual({s.canonical_colors() for s in states},
                         set(enumerate_states(quotient_colors=True)))

    def test_explain_records_eliminations(self):
        trace = Explain()
        list(enumerate_states(explain=trace))
        self.assertGreater(trace.counts['boundary.not_proper'], 0)
        self.assertGreater(trace.counts['partition.boundary_edge'], 0)
        self.assertGreater(trace.counts['planarity.disjoint_colors_cross'], 0)


if __name__ == '__main__':
    unittest.main()
