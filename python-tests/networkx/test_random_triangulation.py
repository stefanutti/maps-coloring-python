# random_triangulation_demo.py
# pip install networkx matplotlib

import math
import random

import networkx as nx
import matplotlib.pyplot as plt

# add this near your imports
from collections import Counter


def embedding_faces(embedding):
    # prefer .faces() if present
    if hasattr(embedding, "faces") and callable(getattr(embedding, "faces")):
        return [tuple(f) for f in embedding.faces()]

    # fallback: enumerate faces by walking each directed edge once
    faces = []
    seen = set()  # directed edges (u, v)
    for u in embedding:
        for v in embedding[u]:
            if (u, v) in seen:
                continue
            cycle = list(embedding.traverse_face(u, v))
            faces.append(tuple(cycle))
            for a, b in zip(cycle, cycle[1:] + cycle[:1]):
                seen.add((a, b))
    return faces


def analyze_faces(embedding):
    faces = embedding_faces(embedding)
    counts = Counter(len(f) for f in faces)
    return faces, counts


def random_triangulation(n, k=3, set_position=False, seed=None):
    """
    return a random inner triangulation of an outer face of size k with n vertices total.
    construction: start with a triangulated k-gon (fan from vertex 0), then
    repeatedly pick a random triangular face and insert a new vertex connected
    to the face's three vertices (apollonian-style growth).

    parameters
    ----------
    n : int
        total number of vertices (must be >= k)
    k : int
        size of the outer face (>= 3)
    set_position : bool
        if True, includes a straight-line drawing in G.graph['pos']
    seed : int or random.Random
        rng seed or rng instance

    returns
    -------
    G : networkx.Graph
        planar graph whose outer face is a k-cycle, all inner faces are triangles.
        - G.graph['embedding'] is a networkx PlanarEmbedding
        - optional drawing coords in G.graph['pos']
        - nodes -2 and -1 are the ends of a designated root edge on the outer face
    """
    if k < 3:
        raise ValueError("k must be at least 3.")
    if n < k:
        raise ValueError("n must be at least k.")

    rng = random.Random(seed) if not isinstance(seed, random.Random) else seed

    G = nx.Graph()

    # create outer k-gon on nodes 0..k-1
    outer = list(range(k))
    G.add_nodes_from(outer)
    G.add_edges_from((outer[i], outer[(i + 1) % k]) for i in range(k))

    # helper to add a diagonal if missing
    def add_diagonal(u, v):
        if not G.has_edge(u, v):
            G.add_edge(u, v)

    # triangulate the outer polygon via a fan from vertex 0
    # track current triangular faces
    triangles = []
    for i in range(1, k - 1):
        add_diagonal(0, i + 1)
        triangles.append((0, i, i + 1))

    # optional positions for a tidy drawing
    pos = {}
    if set_position:
        R = 1.0
        for i in range(k):
            theta = 2 * math.pi * i / k
            pos[i] = (R * math.cos(theta), R * math.sin(theta))

    # insert interior vertices until we reach n
    next_label = k
    while next_label < n:
        a, b, c = rng.choice(triangles)
        v = next_label
        next_label += 1
        G.add_node(v)
        G.add_edges_from([(v, a), (v, b), (v, c)])

        # replace chosen face with three faces around the new vertex
        idx = triangles.index((a, b, c))
        triangles.pop(idx)
        triangles.extend([(v, a, b), (v, b, c), (v, c, a)])

        if set_position:
            ax, ay = pos[a]
            bx, by = pos[b]
            cx, cy = pos[c]
            cxtr = (ax + bx + cx) / 3.0
            cytr = (ay + by + cy) / 3.0
            pos[v] = (cxtr + rng.uniform(-1e-3, 1e-3),
                      cytr + rng.uniform(-1e-3, 1e-3))

    # verify planarity and keep the embedding
    is_planar, embedding = nx.check_planarity(G, counterexample=False)
    if not is_planar:
        raise RuntimeError("constructed graph is not planar (unexpected).")
    G.graph['embedding'] = embedding

    # relabel 0->-2 and 1->-1 to mimic the sage root-edge convention
    mapping = {0: -2, 1: -1}
    G = nx.relabel_nodes(G, mapping, copy=True)

    if set_position:
        pos2 = {mapping.get(u, u): p for u, p in pos.items()}
        G.graph['pos'] = pos2

    # sanity checks
    if G.number_of_edges() != 3 * n - 3 - k:
        raise AssertionError(
            f"edge count mismatch: expected {3*n - 3 - k}, got {G.number_of_edges()}"
        )
    if G.number_of_nodes() != n:
        raise AssertionError("node count mismatch.")

    return G


def draw_graph(G, title=None):
    """
    draw the graph using stored positions if present, otherwise a planar layout.
    """
    pos = G.graph.get('pos')
    if pos is None:
        # compute a planar layout from the embedding if available
        embedding = G.graph.get('embedding')
        try:
            pos = nx.planar_layout(G, embed=embedding) if embedding else nx.planar_layout(G)
        except Exception:
            pos = nx.spring_layout(G, seed=0)

    plt.figure(figsize=(6, 6))
    nx.draw(G, pos=pos, with_labels=True, node_size=300, font_size=9)
    if title:
        plt.title(title)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # parameters
    n = 50
    k = 10
    seed = 123
    set_position = True

    # build the triangulation
    G = random_triangulation(n=n, k=k, set_position=set_position, seed=seed)

    # check planarity and report
    is_planar, embedding = nx.check_planarity(G, counterexample=False)
    print("planar:", is_planar)
    print("|V|, |E|:", G.number_of_nodes(), G.number_of_edges())
    print("expected |E|:", 3 * n - 3 - k)

    # faces and their sizes
    faces, counts = analyze_faces(embedding)
    print("face size histogram:", dict(counts))

    # verify "inner triangulation" property: all inner faces are triangles, one outer face of length k
    # networkx includes the outer face in embedding.faces(); we look for exactly one face of length k
    num_k_faces = counts.get(k, 0)
    num_triangles = counts.get(3, 0)

    print(f"outer k-face present (k={k}):", num_k_faces >= 1)
    print(f"number of triangular faces:", num_triangles)

    # show a few faces (first 5) for inspection
    print("sample faces:", faces[:5])

    # draw
    draw_graph(G, title=f"random inner triangulation (n={n}, k={k})")
