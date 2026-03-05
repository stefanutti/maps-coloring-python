# random_triangulation_demo.py
# pip install networkx matplotlib

import math
import random
from collections import Counter
import networkx as nx
import matplotlib.pyplot as plt


def random_triangulation(n, k=3, seed=None):
    """
    genera una triangolazione interna casuale di un k-gono con n vertici totali.
    costruzione apolloniana: triangola il k-gono, poi inserisci vertici
    all'interno di facce triangolari scelte a caso.
    """
    if k < 3:
        raise ValueError("k deve essere almeno 3.")
    if n < k:
        raise ValueError("n deve essere >= k.")

    rng = random.Random(seed) if not isinstance(seed, random.Random) else seed
    G = nx.Graph()

    # outer k-gon su nodi 0..k-1
    outer = list(range(k))
    G.add_nodes_from(outer)
    G.add_edges_from((outer[i], outer[(i + 1) % k]) for i in range(k))

    # triangola il poligono con una “ventaglio” da 0
    triangles = []
    for i in range(1, k - 1):
        if not G.has_edge(0, i + 1):
            G.add_edge(0, i + 1)
        triangles.append((0, i, i + 1))

    # inserisci vertici interni
    next_label = k
    while next_label < n:
        a, b, c = rng.choice(triangles)
        v = next_label
        next_label += 1
        G.add_node(v)
        G.add_edges_from([(v, a), (v, b), (v, c)])
        triangles.remove((a, b, c))
        triangles.extend([(v, a, b), (v, b, c), (v, c, a)])

    # embedding planare
    is_planar, embedding = nx.check_planarity(G, counterexample=False)
    if not is_planar:
        raise RuntimeError("il grafo generato non è planare (inaspettato).")
    G.graph['embedding'] = embedding

    # rinomina 0->-2 e 1->-1 come in sage (root edge)
    mapping = {0: -2, 1: -1}
    G = nx.relabel_nodes(G, mapping, copy=True)

    # check conteggi
    if G.number_of_edges() != 3 * n - 3 - k:
        raise AssertionError(
            f"mismatch edges: attesi {3*n - 3 - k}, ottenuti {G.number_of_edges()}"
        )
    if G.number_of_nodes() != n:
        raise AssertionError("mismatch nodi.")

    return G


# --- utilities per le facce (compatibili con più versioni di networkx) ---

def embedding_faces(embedding):
    # usa .faces() se presente, altrimenti ricostruisci con traverse_face
    if hasattr(embedding, "faces") and callable(getattr(embedding, "faces")):
        return [tuple(f) for f in embedding.faces()]
    faces = []
    seen = set()  # darts (u, v) già percorsi
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


# --- disegno ---

def draw_graph(G, title=None, layout="planar", spring_iterations=80):
    """
    layout: "planar" (default), "spring", "hybrid" (planar -> poche iterazioni spring)
    """
    if layout == "planar":
        pos = nx.planar_layout(G)
    elif layout == "spring":
        pos = nx.spring_layout(G, seed=42)
    elif layout == "hybrid":
        pos0 = nx.planar_layout(G)
        pos = nx.spring_layout(G, seed=42, pos=pos0, fixed=None, iterations=spring_iterations)
    else:
        pos = nx.planar_layout(G)

    plt.figure(figsize=(7, 7))
    nx.draw(G, pos=pos, with_labels=True, node_size=420, font_size=9)
    if title:
        plt.title(title)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # parametri
    n = 45
    k = 10
    seed = 123

    G = random_triangulation(n=n, k=k, seed=seed)

    is_planar, embedding = nx.check_planarity(G, counterexample=False)
    print("planar:", is_planar)
    print("|V|, |E|:", G.number_of_nodes(), G.number_of_edges())
    print("expected |E|:", 3 * n - 3 - k)

    faces, counts = analyze_faces(embedding)
    print("face size histogram:", dict(counts))
    print(f"outer k-face presente (k={k}):", counts.get(k, 0) >= 1)
    print("numero di facce triangolari:", counts.get(3, 0))

    # prova i layout: "planar", "spring", oppure "hybrid"
    draw_graph(G, title=f"triangolazione (n={n}, k={k}) - planar", layout="planar")
    draw_graph(G, title=f"triangolazione (n={n}, k={k}) - hybrid", layout="hybrid")
