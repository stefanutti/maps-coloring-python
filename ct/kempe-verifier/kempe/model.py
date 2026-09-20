"""Boundary connectivity in Q (§10); these partitions are NOT §9.8 matchings."""

from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Optional, Tuple

COLORS = (0, 1, 2, 3)
PAIRS = tuple(combinations(COLORS, 2))
Partition = Tuple[Tuple[int, ...], ...]


def canonical_partition(blocks) -> Partition:
    blocks = tuple(tuple(block) for block in blocks)
    flat = tuple(v for block in blocks for v in block)
    if any(not block for block in blocks):
        raise ValueError('Empty blocks are not components')
    if any(type(v) is not int or v not in range(5) for v in flat):
        raise ValueError('Terminal indices must be integers 0..4')
    if len(set(flat)) != len(flat):
        raise ValueError('A terminal must occur in exactly one block')
    return tuple(sorted(tuple(sorted(block)) for block in blocks))


def validate_boundary(boundary):
    if len(boundary) != 5 or any(type(c) is not int or c not in COLORS for c in boundary):
        raise ValueError('Boundary must have five colors in 0..3')
    if any(boundary[i] == boundary[(i + 1) % 5] for i in range(5)):
        raise ValueError('Boundary must properly color the five-cycle')


@dataclass(frozen=True, order=True)
class State:
    boundary: Tuple[int, ...]
    partitions: Tuple[Partition, ...]

    def __post_init__(self):
        boundary = tuple(self.boundary)
        validate_boundary(boundary)
        partitions = tuple(canonical_partition(p) for p in self.partitions)
        if len(partitions) != 6:
            raise ValueError('Exactly six color-pair partitions are required')
        for pair, partition in zip(PAIRS, partitions):
            actual = {v for block in partition for v in block}
            expected = {v for v, c in enumerate(boundary) if c in pair}
            if actual != expected:
                raise ValueError(f'Partition {pair} must cover precisely its active terminals')
        object.__setattr__(self, 'boundary', boundary)
        object.__setattr__(self, 'partitions', partitions)

    def partition(self, pair) -> Partition:
        return self.partitions[PAIRS.index(tuple(sorted(pair)))]

    def linked(self, pair, u, v) -> bool:
        return any(u in block and v in block for block in self.partition(pair))

    def relabel_colors(self, permutation):
        permutation = tuple(permutation)
        if (len(permutation) != 4 or set(permutation) != set(COLORS)
                or any(type(c) is not int for c in permutation)):
            raise ValueError('Expected a permutation of 0..3')
        renamed = {}
        for pair, part in zip(PAIRS, self.partitions):
            renamed[tuple(sorted(permutation[c] for c in pair))] = part
        return State(tuple(permutation[c] for c in self.boundary),
                     tuple(renamed[pair] for pair in PAIRS))

    def canonical_colors(self):
        order = list(dict.fromkeys(self.boundary))
        order.extend(c for c in COLORS if c not in order)
        permutation = tuple(order.index(c) for c in COLORS)
        return self.relabel_colors(permutation)

    def to_dict(self):
        return {'boundary': list(self.boundary),
                'partitions': {f'{a}{b}': [list(block) for block in part]
                               for (a, b), part in zip(PAIRS, self.partitions)}}

    @classmethod
    def from_dict(cls, data):
        if set(data) != {'boundary', 'partitions'}:
            raise ValueError('State requires boundary and partitions only')
        if set(data['partitions']) != {f'{a}{b}' for a, b in PAIRS}:
            raise ValueError('Expected exactly the six color-pair keys')
        return cls(tuple(data['boundary']),
                   tuple(data['partitions'][f'{a}{b}'] for a, b in PAIRS))


@dataclass(frozen=True)
class Classification:
    kind: str
    reason: str
    sector: Optional[str] = None
    fans: Tuple[int, ...] = ()

    def __post_init__(self):
        if self.kind not in ('good', 'bad', 'unknown'):
            raise ValueError('Classification must be good, bad or unknown')
        if not self.reason:
            raise ValueError('Classification requires a reason')


def r5(state_or_boundary) -> Classification:
    """Exact boundary criterion of v16 §10.5, without claims about reachability."""
    word = state_or_boundary.boundary if isinstance(state_or_boundary, State) else tuple(state_or_boundary)
    validate_boundary(word)
    counts = Counter(word)
    fans = tuple(i for i, c in enumerate(word) if counts[c] == 1)
    if len(counts) == 3:
        return Classification('good', 'v16 §10.5: missing fourth color extends to v',
                              f'E{fans[0]}', fans)
    i = next(i for i in range(5) if word[i] == word[(i + 2) % 5])
    return Classification('bad', 'v16 §10.5: all four colors occur on the boundary',
                          f'B{i}', fans)
