# triangolazione_k_gono.py
# pip install networkx matplotlib

import math
import random
from collections import Counter
import networkx as nx
import matplotlib.pyplot as plt


def triangolazione_interna(n, k=3, seed=None, root_edge=True):
    """
    genera una triangolazione interna di un k-gono con n vertici totali.
    - bordo esterno: k-ciclo (non modificato durante la crescita)
    - tutte le facce interne: triangoli
    ritorna: (G, faces) con faces[0] = bordo esterno.
    Parametri:
      seed: per RNG
      root_edge (bool, default True): se True rilabella i due primi vertici
        0 -> -2 e 1 -> -1 per imitare la convenzione di una 'root edge' (-2,-1)
        usata in alcune rappresentazioni / enumerazioni (es. Sage) di mappe planari.
        Se False mantiene le etichette naturali 0,1,2,...
    """
    if k < 3:
        raise ValueError("k deve essere almeno 3.")
    if n < k:
        raise ValueError("n deve essere >= k.")

    rng = random.Random(seed) if not isinstance(seed, random.Random) else seed

    # grafo e ciclo esterno 0..k-1
    G = nx.Graph()
    outer = list(range(k))
    G.add_nodes_from(outer)
    G.add_edges_from((outer[i], outer[(i + 1) % k]) for i in range(k))

    # facce: manteniamo noi l'elenco
    # la prima faccia è l'esterno (k nodi, in ordine)
    faces = [tuple(outer)]

    # triangola il k-gono con un ventaglio da 0: crea solo facce triangolari interne
    triangles = []  # lista di facce triangolari interne
    for i in range(1, k - 1):
        u, v = 0, i + 1
        if not G.has_edge(u, v):
            G.add_edge(u, v)
        tri = (0, i, i + 1)
        triangles.append(tri)

    # nella struttura 'faces' mettiamo prima l'outer, poi tutte le inner triangles
    faces.extend(triangles)

    # crescita apolloniana: inserisci vertici solo dentro facce triangolari
    next_label = k
    while next_label < n:
        a, b, c = rng.choice(triangles)
        v = next_label
        next_label += 1

        G.add_node(v)
        G.add_edges_from([(v, a), (v, b), (v, c)])

        # rimpiazza la faccia (a,b,c) con tre triangoli (v,a,b), (v,b,c), (v,c,a)
        triangles.remove((a, b, c))
        new_tris = [(v, a, b), (v, b, c), (v, c, a)]
        triangles.extend(new_tris)

        # aggiorna anche 'faces': togli la vecchia e aggiungi le tre nuove
        # (faces[0] è l'outer; le interne stanno da faces[1:] )
        idx = faces.index((a, b, c))
        faces.pop(idx)
        faces.extend(new_tris)

    # verifica formula |E| = 3n - 3 - k
    if G.number_of_edges() != 3 * n - 3 - k:
        raise AssertionError(
            f"edge count mismatch: attesi {3*n - 3 - k}, trovati {G.number_of_edges()}"
        )

    # opzionale: ottieni embedding da networkx (solo per layout/verifica planaritá)
    is_planar, embedding = nx.check_planarity(G, counterexample=False)
    if not is_planar:
        raise RuntimeError("il grafo generato non è planare (inaspettato).")
    G.graph["embedding"] = embedding

    if root_edge:
        # per imitare sage: root edge (-2,-1)
        mapping = {0: -2, 1: -1}
        G = nx.relabel_nodes(G, mapping, copy=True)

        # aggiorna le facce con la rilabel
        faces = [tuple(mapping.get(u, u) for u in face) for face in faces]

    return G, faces


def analizza_facce(faces):
    """
    prende l'elenco 'faces' e restituisce:
    - Counter delle lunghezze
    - numero di facce triangolari interne
    - lunghezza del bordo esterno (faces[0])
    """
    counts = Counter(len(f) for f in faces)
    outer_len = len(faces[0]) if faces else 0
    num_tri_inner = sum(1 for f in faces[1:] if len(f) == 3)
    return counts, num_tri_inner, outer_len


def disegna(
    G,
    faces,
    layout="planar",
    spring_iterations=80,
    title=None,
    outer_width=1.4,
    inner_width=0.4,
    outer_color="#222",
    inner_color="#666",
    alpha=0.9,
):
    """
    layout: "planar" (default), "spring", "hybrid"
    edge widths ridotti per evitare spessori eccessivi.
    """
    if layout == "planar":
        pos = nx.planar_layout(G)
    elif layout == "spring":
        pos = nx.spring_layout(G, seed=42)
    elif layout == "hybrid":
        pos0 = nx.planar_layout(G)
        pos = nx.spring_layout(G, seed=42, pos=pos0, iterations=spring_iterations)
    else:
        pos = nx.planar_layout(G)

    plt.figure(figsize=(7, 7))

    outer = faces[0]
    outer_cycle = list(zip(outer, outer[1:] + outer[:1]))
    outer_edge_set = {frozenset(e) for e in outer_cycle}
    inner_edges = [e for e in G.edges() if frozenset(e) not in outer_edge_set]

    nx.draw_networkx_edges(
        G, pos=pos, edgelist=inner_edges, width=inner_width, edge_color=inner_color, alpha=alpha
    )
    nx.draw_networkx_nodes(G, pos=pos, node_size=420, linewidths=0.8)
    nx.draw_networkx_labels(G, pos=pos, font_size=9)
    nx.draw_networkx_edges(
        G, pos=pos, edgelist=outer_cycle, width=outer_width, edge_color=outer_color, alpha=alpha
    )

    if title:
        plt.title(title)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # esempio
    n = 4
    k = 3
    seed = 123

    # puoi disattivare la rilabel passando root_edge=False
    G, faces = triangolazione_interna(n=n, k=k, seed=seed, root_edge=False)

    print("planar:", nx.check_planarity(G)[0])
    print("|V|, |E|:", G.number_of_nodes(), G.number_of_edges())
    print("expected |E|:", 3 * n - 3 - k)

    counts, num_tri_inner, outer_len = analizza_facce(faces)
    print("face size histogram:", dict(counts))
    print(f"outer face length (atteso k={k}):", outer_len)
    print("numero di facce triangolari interne:", num_tri_inner)  # atteso = 2n - 3 - k

    # sostituisce la chiamata errata a G.is_planar()
    is_planar, _ = nx.check_planarity(G)
    print("planar? ", is_planar)

    # disegni (una sola volta per ciascun layout)
    disegna(G, faces, layout="planar", title=f"triangolazione (n={n}, k={k}) - planar")
    disegna(G, faces, layout="hybrid", title=f"triangolazione (n={n}, k={k}) - hybrid")
