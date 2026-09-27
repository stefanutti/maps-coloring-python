# Iteration report — 4ct-v17

## 1. Starting point and deliverables

- Date: 2026-09-22.
- Instructions: [prompt-en.md](prompt-en.md).
- Starting manuscript: [4ct-v16.md](4ct-v16.md).
- Complete updated manuscript: [4ct-v17.md](4ct-v17.md).
- Previous separate iteration record: absent from `docs/llm-vs-4ct/`.
- Supplied separate review report: absent.
- Available earlier manuscript: [4ct-v14.md](4ct-v14.md); its old endgame claims and failed-route discussion were compared with the corrections already present in v16.

The source versions and the algorithm implementation were not changed. The document remains in English. R₅ and R_existential keep their meanings; R2-escape is an identifier for the already existing uniform R2 target, not a new obligation replacing it.

## 2. Problem addressed

The essential target is R₅: for a map M in C and a chosen pentagon whose five excavations are colorable, at least one excavation has a coloring admitting reinsertion. By the existing bijection, this is equivalent to positivity of A = |Tait(M)| = Σ_i |Alt(G_i)|.

The smaller problem chosen for this iteration was to sharpen the comparison of good sectors E_i and bad sectors B_i of the common dual graph Q. Version 16 supplied a linked bad-to-bad bijection and two unlinked bad-to-good injections, proving inequalities only. The question was whether their unmatched good subsets also admit a controlled bijection.

Available assumptions: Q is a finite graph embedded in a disk whose boundary is the five-cycle a₀…a₄; colorings are proper with four fixed labels. In the application, Q = T−v where T is a simple 5-connected triangulation and v has degree five. The new sector theorem needs only the disk embedding and boundary cycle. Counting statements about Tait(M) and the excavations also use the already proved common-dual and pentagon bijections.

Progress would mean an exact relation reducing the independent sector data, with an explicit proof and a precise account of the positivity still missing. A numerical check or a reformulation of R₅ alone would not meet that criterion.

## 3. Result actually obtained

A one-vertex-Kempe-change bijection was proved:

$$
B_i\sqcup E_i\longleftrightarrow B_{i+2}\sqcup E_{i+4}.
$$

It preserves each vertex-Kempe class of Q. The new part pairs the linked good subsets by a complementary-color switch through a_{i+2}. A two-color path between a_{i+1},a_{i+3} separates the other two marked boundary positions; the swapped component consequently has exactly the required boundary intersection. The previously known injections are onto their unlinked good subsets. All four pairings have explicit inverses.

Hence, within every class and globally,

$$
b_i-b_{i+2}=g_{i+4}-g_i,
\qquad b_i+g_i+g_{i+2}=\lambda,
\qquad 5\lambda=b+2g.
$$

With fixed edge-color names, write A_i = |Alt(G_i)|, A = Σ_i A_i, N_i = |Tait(G_i)|. The free S₄-action on each sector gives λ = 24ℓ. The new consequences are

$$
N_i=18\ell-A+2A_i-A_{i-1}-A_{i+1},
\qquad 5A_i-A=2N_i-N_{i+2}-N_{i+3}.
$$

Thus all relative A_i are determined by the five N_i, Σ_i N_i is divisible by 30, and

$$
A\ge\max_i(N_{i+2}+N_{i+3}-2N_i).
$$

In the remaining case N_i = 18m for all i, the counts necessarily have the form

$$
A_i=18r,\quad A=90r,\quad g_i=72r,\quad
b_i=24(m-r),\quad \ell=m+5r,
\qquad 0\le r\le m.
$$

The new result determines relative counts and restricts the remaining scalar. It does **not** prove r > 0. These results are new to this manuscript; no claim of priority in the mathematical literature is made.

## 4. Statements changed and logical status

| Location in v17 | Change | Status |
|---|---|---|
| Opening table | Stable identifiers and all existing essential/alternative obligations retained. | Organizational clarification. |
| §5.3 | Dictionary restricted to target maps with every face of size at least 5; proof and cube counterexample added. | Correction of a missing hypothesis. |
| §10.7 | Exact sector-exchange theorem and common-count parameter replace an inequality-only treatment; old inequalities retained as corollaries. | Proved in the text by explicit planar bijections. |
| §10.8 | Divisibility by 24 extended to good sectors and all vertex-Kempe classes. | Proved by a free color-permutation action. |
| §10.10 | Fan-count identity, recovery formula, quantitative lower bound, and balanced-case parameterization added. | Proved algebraic consequences. |
| §§12–15 | Directions, logical status, dependencies and glossary updated to reflect the exact identities. | R₅, R2-escape and R_existential remain open. |
| §§2.3 and 16 | Existing minimal-counterexample reference retained, with a precise location in §2.3. | Classical external dependency, checked in the primary source. |

The §5.3 correction does not invalidate §5.2: excavation to theta is still valid for general current maps. What failed was the unqualified assertion that reversal obeys the size-five sealing and closing rules. A cube provides a direct counterexample because its opposite square ends sealed with size four and its chosen ocean also has size four. All subsequent uses with targets in C satisfy the corrected hypothesis.

The essential chain—valid smaller excavations, pentagon bijection, common dual and conditional assembly—was reviewed and no new error was found. This is a scoped review, not a claim that every statement in the long manuscript has received a new independent proof audit.

## 5. Discarded attempts and reasons

- **A stronger complementary-crossing theorem for triangulated disks:** initially considered as a route from injections to equality. It is unnecessary. The linked good subsets are matched using the same one-way Jordan separation already sufficient for the bad subsets. No triangulation duality is invoked.
- **An unsupported nonnegative offset:** rewriting b_i = q + g − g_i − g_{i+2} does not imply q ≥ 0. On a five-wheel disk, g_i = 24 and b_i = 0, giving q = −72. The valid nonnegative parameter is λ = b_i+g_i+g_{i+2}.
- **Uniform excavation counts as evidence of no extension:** refuted even as a general disk-graph heuristic. A five-wheel with a pendant vertex at its center has |Ω_i|/4 = 18 for every i and g_i = 72. It realizes the positive numerical choice m = r = 1. These counts can also be checked without a search: the center forces a three-color boundary, with 24 choices per singleton position, and the pendant then has three color choices. This graph is outside the special triangulated Q family, so it is not a counterexample to any connectivity-specific assertion about C.
- **A positivity proof from the new identities alone:** the formal values g_i = 0, b_i = 24m satisfy all identities, nonnegativity and divisibility. Algebraic manipulation of those same constraints cannot exclude them. Their formal consistency does not assert realization by a planar graph.
- **Descent by repeatedly applying the reversible sector transfers or R2 toggle:** no new monotone quantity was found. The prior failure of that approach remains recorded; no termination claim is restored.

## 6. Checks performed and limits

### Proof review

Two independent mathematical reviews checked the four subset bijections, the meaning of the missing boundary color, the preservation of the two-color induced subgraphs, the inverse maps, the classwise quantifiers and all factors 4, 6 and 24. The sector proof and its algebra were also checked directly during integration. Agreement among reviews is not used as a proof: the manuscript contains the actual arguments.

A separate review checked the coastal and pentagon dependencies and found the §5.3 scope correction. The v14 claims already weakened or corrected by v16—gap-3 termination, intermediate-map connectivity, and reversible-switch descent—were not restored.

### Primary sources

- Thomas, *An Update on the Four-Color Theorem*, [Theorem 10 and its preceding definition, manuscript p. 13](https://thomas.math.gatech.edu/PAP/update.pdf#page=14): checked the minimal-counterexample connectivity statement used by §§2.3 and 11.1.
- Dvořák and Lidický, *Coloring count cones of planar graphs*, [Lemma 7 and Conjecture 9](https://arxiv.org/html/1907.04066#S3): checked the existing comparison to the exceptional degree-five ray and the status of the stronger inequality. Neither the conjecture nor the cone enumeration is a premise of the new proof.

The new sector theorem has a self-contained proof and needs no new external mathematical result beyond planar Jordan separation.

### Reproducible diagnostic examples

The script below was executed with the repository's virtualenv, with `ct/` as working directory. It enumerates only five explicitly specified small graphs, quotients by global color permutations, constructs their vertex-Kempe classes, and checks the identities in each class and globally. All five graphs have one such class. Every normalized coloring has exactly 24 labeled representatives because its boundary uses at least three colors.

| Graph | Vertices | S₄ orbits | g_i | b_i | |Ω_i|/4 |
|---|---:|---:|---|---|---|
| Boundary C₅ only | 5 | 10 | (24,24,24,24,24) | (24,24,24,24,24) | (24,24,24,24,24) |
| Fan at a₀ | 5 | 4 | (24,0,0,0,0) | (0,24,24,0,24) | (24,6,12,12,6) |
| Five-wheel disk | 6 | 5 | (24,24,24,24,24) | (0,0,0,0,0) | (6,6,6,6,6) |
| Five-wheel plus pendant at center | 7 | 15 | (72,72,72,72,72) | (0,0,0,0,0) | (18,18,18,18,18) |
| Icosahedral triangulation minus one vertex | 11 | 20 | (48,48,48,48,48) | (48,48,48,48,48) | (48,48,48,48,48) |

Only the last example has the particular Q = T−v with T simple and 5-connected required by the main application. The other examples test the broader disk-graph hypotheses of the sector theorem. All assertions in this bounded diagnostic passed. These 54 orbits, and their single-class behavior, establish no universal coloring or Kempe-connectivity claim. The manuscript's proofs do not depend on these computations. No randomized search or exhaustive map enumeration is used as a proof.

To reproduce, run the following from the repository root. It needs only Python and the already used NetworkX dependency.

```bash
cd ct
../.venv/bin/python - <<'PY'
from collections import Counter, defaultdict
from itertools import combinations
import networkx as nx


def normalize(colors):
    names = {}
    return tuple(names.setdefault(c, len(names)) for c in colors)


def inspect(name, graph, boundary):
    order = boundary + sorted(set(graph) - set(boundary))
    pos = {v: i for i, v in enumerate(order)}
    edges = [(pos[u], pos[v]) for u, v in graph.edges()]
    adj = [set() for _ in order]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    colors, states = [], []

    def extend():
        v = len(colors)
        if v == len(order):
            states.append(tuple(colors))
        else:
            forbidden = {colors[u] for u in adj[v] if u < v}
            for c in range(min(4, max(colors, default=-1) + 2)):
                if c not in forbidden:
                    colors.append(c)
                    extend()
                    colors.pop()

    extend()
    index = {c: i for i, c in enumerate(states)}
    parent = list(range(len(states)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for n, coloring in enumerate(states):
        for x, y in combinations(range(4), 2):
            unseen = {v for v, c in enumerate(coloring) if c in (x, y)}
            while unseen:
                first = min(unseen)
                component, todo = {first}, [first]
                unseen.remove(first)
                while todo:
                    v = todo.pop()
                    for u in adj[v] & unseen:
                        unseen.remove(u)
                        component.add(u)
                        todo.append(u)
                switched = normalize([
                    x + y - c if v in component else c
                    for v, c in enumerate(coloring)
                ])
                parent[root(n)] = root(index[switched])

    groups = defaultdict(list)
    for n, coloring in enumerate(states):
        groups[root(n)].append(coloring)

    def counts(selected):
        good, bad = [0] * 5, [0] * 5
        for coloring in selected:
            w = coloring[:5]
            multiplicity = Counter(w)
            if len(multiplicity) == 3:
                i = next(i for i in range(5) if multiplicity[w[i]] == 1)
                good[i] += 24
            else:
                assert len(multiplicity) == 4
                i = next(i for i in range(5) if w[i] == w[(i + 2) % 5])
                bad[i] += 24
        fans = [sum(24 for c in selected if c[i] not in
                    (c[(i + 2) % 5], c[(i + 3) % 5])) for i in range(5)]
        lam = bad[0] + good[0] + good[2]
        total = sum(good)
        for i in range(5):
            assert bad[i] - bad[(i + 2) % 5] == good[(i + 4) % 5] - good[i]
            assert bad[i] + good[i] + good[(i + 2) % 5] == lam
            assert fans[i] == 3 * lam - total + 2 * good[i] - good[(i - 1) % 5] - good[(i + 1) % 5]
            assert 5 * good[i] - total == 2 * fans[i] - fans[(i + 2) % 5] - fans[(i + 3) % 5]
        assert lam % 24 == 0
        assert sum(fans) % 120 == 0
        return good, bad, [s // 4 for s in fans]

    for group in groups.values():
        counts(group)
    good, bad, normalized_fans = counts(states)
    print(name, 'orbits=', len(states), 'classes=', len(groups),
          'g=', good, 'b=', bad, 'fan_counts/4=', normalized_fans)


cycle = nx.cycle_graph(5)
fan = cycle.copy()
fan.add_edges_from([(0, 2), (0, 3)])
wheel = cycle.copy()
wheel.add_edges_from((5, i) for i in range(5))
pendant = wheel.copy()
pendant.add_edge(5, 6)
ico = nx.icosahedral_graph()
_, embedding = nx.check_planarity(ico)
boundary = list(embedding.neighbors_cw_order(0))
ico.remove_node(0)
for name, graph, rim in [
    ('C5', cycle, list(range(5))),
    ('fan', fan, list(range(5))),
    ('wheel', wheel, list(range(5))),
    ('wheel+leaf', pendant, list(range(5))),
    ('icosahedron-minus-vertex', ico, boundary),
]:
    inspect(name, graph, rim)
PY
```

### Artifact checks

The final checks compare v17 with v16, verify that the earlier manuscripts are unchanged, confirm all sixteen main sections remain, check internal section references and balanced display-math delimiters, and check the two new files for trailing whitespace. No application code changed, so runtime algorithm tests are not evidence for the mathematical claims in this iteration.

## 7. Dependencies still open

- **R₅:** rule out r = 0 for every actual Q in the balanced case, or otherwise construct a good coloring. This remains equivalent to the intended single-pentagon extension target.
- **R2-escape:** exclude hostile edge-Kempe classes in the specified intermediates. The marked separator and remote-chain alternatives are unresolved.
- **R_existential:** obtain compatible sequential pilot repairs, including terminating gap-3 control and the larger gaps. Independent successful colorings for the separate moves remain insufficient.
- The new identities concern vertex Kempe changes on Q. They do not convert an arbitrary fixed coloring into an edge-Kempe repair within one chosen G_i.

## 8. One concrete next attempt

Investigate the smallest entirely bad class permitted by §10.8: a class L with |L ∩ B_i| = 24 for every i, or one S₄-orbit in each bad sector. Its five linked-sector bijections then act on only one color-permutation orbit per sector. Follow the five transfers at the level of their actual bichromatic components and examine whether this action is compatible with the internal triangles of Q = T−v and 5-connectivity of T.

Success criterion: a self-contained proof excluding this smallest class in that precise family, yielding m_L ≥ 2 for every entirely bad class, or an explicit correctly embedded example proving that the exclusion is false. Even successful exclusion would be only partial progress; larger entirely bad classes would remain.

Abandonment criterion for a proposed argument: it produces only the already proved sector equalities, a reversible return of the boundary word, or an unsupported assertion that changing a bichromatic component preserves the other color-pair connections. In that case record no progress rather than interpreting the transfer cycle as descent.

Outcome: **PROGRESS**.
