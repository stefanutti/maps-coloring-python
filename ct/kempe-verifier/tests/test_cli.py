import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'kempe', *map(str, args)],
                              cwd=ROOT, capture_output=True, text=True)

    def test_analyze_produces_report_dot_and_complete_explanation(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            report, trace, dot = [folder / name for name in ('report.json', 'explain.jsonl', 'graph.dot')]
            result = self.run_cli('analyze', '--quotient-colors', '--include-graph',
                                  '--output', report, '--explain', trace, '--dot', dot)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(report.read_text())
            self.assertEqual(data['status'], 'complete_abstract_analysis')
            self.assertFalse(data['r5_proved'])
            self.assertEqual(len(data['states']), data['state_count'])
            self.assertEqual(len(data['actions']), data['state_count'])
            events = [json.loads(line) for line in trace.read_text().splitlines()]
            self.assertEqual(len(events), sum(data['explain']['counts'].values()))
            self.assertTrue(any(e['code'].startswith('move.') for e in events))
            self.assertTrue(any(e['code'].startswith('kernel.') for e in events))
            self.assertIn('digraph Kempe', dot.read_text())

    def test_limit_never_emits_success_report(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'report.json'
            result = self.run_cli('analyze', '--max-states', 1, '--output', output)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(output.exists())
            self.assertEqual(json.loads(result.stderr)['status'], 'incomplete')

    def test_enumeration_and_state_moves_round_trip(self):
        result = self.run_cli('enumerate', '--quotient-colors')
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(result.stdout)['states'][0]
        with tempfile.TemporaryDirectory() as folder:
            input_path = Path(folder) / 'state.json'
            input_path.write_text(json.dumps(state))
            result = self.run_cli('moves', '--state', input_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            moves = json.loads(result.stdout)['moves']
            self.assertTrue(any(not m['action']['guaranteed'] for m in moves))
            self.assertTrue(all(m['targets'] for m in moves))

    def test_custom_classifier_and_symmetry_guard(self):
        result = self.run_cli('analyze', '--classifier', 'examples.custom_classifier:classify', '--quotient-colors')
        self.assertEqual(result.returncode, 2)
        result = self.run_cli('analyze', '--classifier', 'examples.custom_classifier:classify')
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertGreater(data['classification_counts']['unknown'], 0)
        self.assertFalse(data['all_states_forced_good'])

    def test_outputs_cannot_overwrite_state_input(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'state.json'
            path.write_text('original')
            result = self.run_cli('moves', '--state', path, '--output', path)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(path.read_text(), 'original')

    def test_hardlinked_output_cannot_truncate_input(self):
        with tempfile.TemporaryDirectory() as folder:
            path, alias = Path(folder) / 'state.json', Path(folder) / 'alias.jsonl'
            path.write_text('original')
            os.link(path, alias)
            result = self.run_cli('moves', '--state', path, '--explain', alias)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(path.read_text(), 'original')

    def test_pairing_example_executes_v16_counterexample(self):
        result = self.run_cli('pairing-example')
        self.assertEqual(result.returncode, 0, result.stderr)
        q1, q2 = json.loads(result.stdout)['examples']
        self.assertEqual(q1['before'], q2['before'])
        self.assertNotEqual(q1['after'], q2['after'])


if __name__ == '__main__':
    unittest.main()
