"""Necessary disk constraints only; simultaneous realizability is not decided."""

from dataclasses import dataclass
from itertools import combinations, product
from typing import Callable, Optional

from .model import COLORS, PAIRS, State, validate_boundary


@dataclass(frozen=True)
class Constraint:
    name: str
    source: str
    reject: Callable[[State], Optional[str]]

    def __post_init__(self):
        if not self.name or not self.source:
            raise ValueError('An additional constraint requires a name and mathematical source')


def set_partitions(items):
    """Each set partition exactly once, with stable block ordering."""
    items = tuple(items)
    if not items:
        yield ()
        return
    first, rest = items[0], items[1:]
    for partition in set_partitions(rest):
        yield ((first,),) + partition
        for i in range(len(partition)):
            blocks = list(partition)
            blocks[i] = (first,) + blocks[i]
            yield tuple(sorted(blocks))


def boundary_words(quotient_colors=False, explain=None):
    for word in product(COLORS, repeat=5):
        if any(word[i] == word[(i + 1) % 5] for i in range(5)):
            if explain is not None:
                explain.record('boundary.not_proper', 'Adjacent boundary vertices have equal colors', boundary=word)
            continue
        order = list(dict.fromkeys(word))
        if quotient_colors and word != tuple(order.index(c) for c in word):
            if explain is not None:
                explain.record('symmetry.color_representative', 'Another S4 representative is retained', boundary=word)
            continue
        yield word


def blocks_cross(left, right):
    """Distinct connected disjoint sets cannot have alternating disk contacts."""
    for a, b in combinations(left, 2):
        for c, d in combinations(right, 2):
            if a < c < b < d or c < a < d < b:
                return True
    return False


def partition_reasons(word, pair, partition):
    block_of = {v: i for i, block in enumerate(partition) for v in block}
    reasons = []
    for u in range(5):
        v = (u + 1) % 5
        if word[u] in pair and word[v] in pair and block_of[u] != block_of[v]:
            reasons.append(('partition.boundary_edge', f'Boundary edge {u}-{v} forces connectivity in {pair}'))
    if any(blocks_cross(a, b) for a, b in combinations(partition, 2)):
        reasons.append(('planarity.same_pair_cross', f'Disjoint components of {pair} have alternating contacts'))
    return tuple(reasons)


def rejection_reasons(state, constraints=()):
    reasons = []
    for pair, part in zip(PAIRS, state.partitions):
        reasons.extend(partition_reasons(state.boundary, pair, part))
    for pair in PAIRS[:3]:  # exactly one representative of each complementary pair
        other = tuple(c for c in COLORS if c not in pair)
        if any(blocks_cross(a, b) for a in state.partition(pair) for b in state.partition(other)):
            reasons.append(('planarity.disjoint_colors_cross',
                            f'Components with disjoint colors {pair}/{other} have alternating contacts (§10.6)'))
    for constraint in constraints:
        reason = constraint.reject(state)
        if reason is not None:
            reasons.append((f'custom.{constraint.name}', f'{reason} [source: {constraint.source}]'))
    return tuple(reasons)


def enumerate_states(boundaries=None, quotient_colors=False, constraints=(), explain=None):
    if quotient_colors and constraints:
        raise ValueError('Custom constraints require fixed color labels; symmetry is not assumed')
    words = boundary_words(quotient_colors, explain) if boundaries is None else boundaries
    seen = set()
    for raw_word in words:
        word = tuple(raw_word)
        validate_boundary(word)
        options = []
        for pair in PAIRS:
            active = tuple(i for i, color in enumerate(word) if color in pair)
            choices = []
            for partition in set_partitions(active):
                reasons = partition_reasons(word, pair, partition)
                if reasons and explain is not None:
                    for code, reason in reasons:
                        explain.record(code, reason, boundary=word, pair=pair, partition=partition)
                if not reasons:
                    choices.append(partition)
            options.append(choices)
        for partitions in product(*options):
            state = State(word, partitions)
            reasons = rejection_reasons(state, constraints)
            if reasons:
                if explain is not None:
                    for code, reason in reasons:
                        explain.record(code, reason, state=state.to_dict())
                continue
            result = state.canonical_colors() if quotient_colors else state
            if result not in seen:
                seen.add(result)
                yield result
