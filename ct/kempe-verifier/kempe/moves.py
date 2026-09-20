"""May successors grouped by actual switch choice, not independent actions."""

from dataclasses import dataclass
from functools import lru_cache
import io
import json
from typing import Tuple

from .enumeration import enumerate_states, rejection_reasons
from .explain import Explain
from .model import COLORS, PAIRS, canonical_partition


@dataclass(frozen=True, order=True)
class Action:
    pair: Tuple[int, int]
    block: Tuple[int, ...]

    def __post_init__(self):
        pair = tuple(sorted(self.pair))
        if pair not in PAIRS or any(type(c) is not int for c in pair):
            raise ValueError('Action requires two distinct colors in 0..3')
        block = canonical_partition((self.block,))[0] if self.block else ()
        object.__setattr__(self, 'pair', pair)
        object.__setattr__(self, 'block', block)

    @property
    def guaranteed(self):
        return bool(self.block)

    def to_dict(self):
        return {'pair': self.pair, 'block': self.block, 'guaranteed': self.guaranteed,
                'kind': 'boundary_component' if self.block else 'possible_internal_component'}


@dataclass(frozen=True)
class Move:
    action: Action
    targets: tuple


@lru_cache(maxsize=4096)
def _candidates(boundary, with_explanations=False):
    if not with_explanations:
        return tuple(enumerate_states(boundaries=(boundary,))), ()
    stream = io.StringIO()
    trace = Explain(stream=stream, sample_limit=0)
    candidates = tuple(enumerate_states(boundaries=(boundary,), explain=trace))
    # Keep the rejection evidence with the cached accepted candidates. Replaying
    # it for each action makes standalone `moves --explain` auditable too.
    events = tuple(json.loads(line) for line in stream.getvalue().splitlines())
    return candidates, events


def kempe_moves(state, quotient_colors=False, constraints=(), explain=None):
    """All guaranteed boundary actions plus six optional remote actions.

    The switched pair and its complement are invariant as uncolored induced
    subgraphs. Nothing stronger is assumed about the other four partitions.
    Constraints are user-supplied necessary state conditions, never guards
    silently removing actions. Empty target sets remain visible to callers.
    """
    if quotient_colors and constraints:
        raise ValueError('Custom constraints require fixed color labels')
    reasons = rejection_reasons(state, constraints)
    if reasons:
        raise ValueError(f'Source is not admissible: {reasons}')
    for pair in PAIRS:
        other = tuple(c for c in COLORS if c not in pair)
        for block in state.partition(pair) + ((),):
            action = Action(pair, block)
            boundary = list(state.boundary)
            for v in block:
                boundary[v] = pair[1] if boundary[v] == pair[0] else pair[0]
            targets = set()
            candidates, events = _candidates(tuple(boundary), explain is not None)
            if explain is not None:
                for event in events:
                    explain.record(**event, source=state.to_dict(), action=action.to_dict(),
                                   stage='target_enumeration')
            for candidate in candidates:
                violations = []
                if candidate.partition(pair) != state.partition(pair):
                    violations.append(('move.switched_pair_changed', 'The switched two-color induced subgraph is unchanged'))
                if candidate.partition(other) != state.partition(other):
                    violations.append(('move.complement_changed', 'Neither complementary color is switched'))
                violations.extend(rejection_reasons(candidate, constraints))
                if violations:
                    if explain is not None:
                        for code, reason in violations:
                            explain.record(code, reason, source=state.to_dict(), action=action.to_dict(),
                                           candidate=candidate.to_dict())
                else:
                    targets.add(candidate.canonical_colors() if quotient_colors else candidate)
            yield Move(action, tuple(sorted(targets)))
