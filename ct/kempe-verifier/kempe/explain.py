"""Bounded in-memory samples, exact event counts, optional complete JSONL stream."""

import json
from collections import Counter


class Explain:
    def __init__(self, stream=None, sample_limit=20):
        if sample_limit < 0:
            raise ValueError('sample_limit must be nonnegative')
        self.stream = stream
        self.sample_limit = sample_limit
        self.counts = Counter()
        self.samples = []

    def record(self, code, reason, **context):
        event = {'code': code, 'reason': reason, **context}
        self.counts[code] += 1
        if len(self.samples) < self.sample_limit:
            self.samples.append(event)
        if self.stream is not None:
            self.stream.write(json.dumps(event, sort_keys=True) + '\n')

    def summary(self):
        return {'counts': dict(sorted(self.counts.items())), 'samples': self.samples,
                'samples_truncated': sum(self.counts.values()) > len(self.samples)}
