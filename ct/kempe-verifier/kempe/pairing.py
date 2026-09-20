"""Actual edge-cycle transition pairing of v16 §9.8, separate from dual State."""

from dataclasses import dataclass


def _matching(edges):
    edges = tuple(tuple(edge) for edge in edges)
    flat = tuple(v for edge in edges for v in edge)
    if (not edges or any(len(e) != 2 for e in edges)
            or any(type(v) is not int for v in flat)
            or len(set(flat)) != len(flat) or set(flat) != set(range(len(flat)))):
        raise ValueError('Expected a perfect matching on consecutive vertices 0..2n-1')
    return tuple(sorted(tuple(sorted(edge)) for edge in edges))


@dataclass(frozen=True)
class TransitionPairing:
    matching: tuple

    def __post_init__(self):
        object.__setattr__(self, 'matching', _matching(self.matching))

    def two_page_assignment(self):
        """A 2-coloring of the chord crossing graph, or None if impossible."""
        adjacency = [[] for _ in self.matching]
        for i, (a, b) in enumerate(self.matching):
            for j, (c, d) in enumerate(self.matching[:i]):
                if a < c < b < d or c < a < d < b:
                    adjacency[i].append(j)
                    adjacency[j].append(i)
        pages = {}
        for root in range(len(adjacency)):
            if root in pages:
                continue
            pages[root] = 0
            stack = [root]
            while stack:
                node = stack.pop()
                for child in adjacency[node]:
                    if child not in pages:
                        pages[child] = 1 - pages[node]
                        stack.append(child)
                    elif pages[child] == pages[node]:
                        return None
        return tuple(pages[i] for i in range(len(adjacency)))

    def closure_partition(self, alternating_matching):
        """Components of Q union P, marked by the canonical Q-edge indices.

        Parallel Q/P edges remain distinct conceptually. Connectivity is enough
        for this partition, so duplicate adjacency does not affect the result.
        P must be one of the two alternating matchings of the specified cycle.
        """
        p = _matching(alternating_matching)
        n = 2 * len(self.matching)
        p0 = tuple((i, i + 1) for i in range(0, n, 2))
        p1 = _matching(tuple((i, (i + 1) % n) for i in range(1, n, 2)))
        if len(p) != len(self.matching) or p not in (p0, p1):
            raise ValueError('Closure must be an alternating matching of the same cycle')
        adjacent = [set() for _ in range(n)]
        for u, v in self.matching + p:
            adjacent[u].add(v)
            adjacent[v].add(u)
        remaining = set(range(n))
        partition = []
        while remaining:
            root = min(remaining)
            remaining.remove(root)
            reached, stack = {root}, [root]
            while stack:
                for child in adjacent[stack.pop()] & remaining:
                    remaining.remove(child)
                    reached.add(child)
                    stack.append(child)
            partition.append(tuple(i for i, (u, _) in enumerate(self.matching) if u in reached))
        return tuple(sorted(partition))
