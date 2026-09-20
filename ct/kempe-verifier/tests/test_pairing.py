import unittest

from kempe.pairing import TransitionPairing


class PairingTests(unittest.TestCase):
    def test_v16_section_9_15_nonclosure_counterexample(self):
        q1 = TransitionPairing(((0, 1), (2, 4), (3, 5)))
        q2 = TransitionPairing(((0, 1), (2, 5), (3, 4)))
        p0 = ((0, 1), (2, 3), (4, 5))
        p1 = ((1, 2), (3, 4), (5, 0))
        for q in (q1, q2):
            self.assertIsNotNone(q.two_page_assignment())
            self.assertEqual(q.closure_partition(p0), ((0,), (1, 2)))
        self.assertEqual(q1.closure_partition(p1), ((0, 1, 2),))
        self.assertEqual(q2.closure_partition(p1), ((0, 1), (2,)))

    def test_three_pairwise_crossing_chords_cannot_fit_on_two_pages(self):
        q = TransitionPairing(((0, 3), (1, 4), (2, 5)))
        self.assertIsNone(q.two_page_assignment())

    def test_invalid_matching_and_closure_rejected(self):
        with self.assertRaises(ValueError):
            TransitionPairing(((0, 1), (1, 2)))
        q = TransitionPairing(((0, 1), (2, 3)))
        with self.assertRaises(ValueError):
            q.closure_partition(((0, 1),))


if __name__ == '__main__':
    unittest.main()
