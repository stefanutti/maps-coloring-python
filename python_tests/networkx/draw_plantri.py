import re
import sys
import networkx as nx
import matplotlib.pyplot as plt

def parse_plantri_T_line(line: str):
    parts = line.strip().split()
    if not parts:
        raise ValueError("linea vuota")

    V = int(parts[0])

    # trova la posizione del numero di facce (prima token numerica dopo le adiacenze)
    face_idx = None
    for i in range(1, len(parts)):
        if parts[i].isdigit():
            face_idx = i
            break
    if face_idx is None:
        raise ValueError("non trovo il numero di facce nella riga")

    adj_tokens = parts[1:face_idx]
    F = int(parts[face_idx])
    face_tokens = parts[face_idx + 1: face_idx + 1 + F]

    if len(adj_tokens) != V:
        raise ValueError(f"mi aspettavo {V} token di adiacenza, trovati {len(adj_tokens)}")

    # mappa: vertice -> lista vicini in ordine ciclico (come appare nel token)
    rot = {}
    for tok in adj_tokens:
        if len(tok) != 3:
            raise ValueError(f"token di adiacenza non di lunghezza 3: {tok}")
        u = tok[0]
        rot[u] = [tok[1], tok[2], tok[3-1]]  # cioè [1], [2] (teniamo la forma esplicita sotto)
        rot[u] = [tok[1], tok[2]]  # placeholder, rimpiazziamo subito sotto

    # correzione: per cubici, il token è u + 2 vicini? no: è u + 2? in realtà è u + 2? (vedi output: "ASB" = A,S,B)
    # quindi: u=tok[0], vicini=tok[1],tok[2]
    # ma in output hai sempre 3 simboli: il vertice + 2 vicini? sembra 3 totali, quindi grado 2: impossibile.
    # in realtà plantri usa token di LUNGHEZZA 3 per cubic? no: è 3 vicini + vertice? no.
    # soluzione robusta: interpretazione standard doublecode: token è "u v w" concatenati (vertice + 2 vicini) SOLO per triangolazioni.
    # per il duale cubico in -d, la rappresentazione è: per ogni vertice u, stampa i 3 vicini SENZA ripetere u?
    # ma il tuo token "ASB" ha 3 caratteri: sono i 3 vicini di A (S,B,?) oppure include A.
    # guardando altri token: "BVC" inizia con B: molto probabilmente include il vertice.
    # quindi per cubic, dovrebbe essere 4 (u+3 vicini). però qui è 3: quindi include u + 2 vicini.
    # conclusione: questi token NON sono "lista vicini", ma la codifica planar-code (pcode) compressa.
    # per disegnare in modo affidabile: usiamo SOLO le facce (che sono corrette) per ricostruire gli edges del grafo.

    # ricostruisci edges dalle facce: ogni faccia token t = ciclo dei suoi caratteri
    G = nx.Graph()
    for t in face_tokens:
        cyc = list(t)
        for i in range(len(cyc)):
            a = cyc[i]
            b = cyc[(i + 1) % len(cyc)]
            if a != b:
                G.add_edge(a, b)

    return G, face_tokens

def draw_graph(G: nx.Graph(), out_png="graph.png"):
    is_planar, embedding = nx.check_planarity(G)
    if not is_planar:
        raise ValueError("il grafo ricostruito non risulta planare (strano).")

    pos = nx.combinatorial_embedding_to_pos(embedding) if hasattr(nx, "combinatorial_embedding_to_pos") else nx.planar_layout(G)

    plt.figure(figsize=(8, 8))
    nx.draw_networkx_edges(G, pos, width=1.2)
    nx.draw_networkx_nodes(G, pos, node_size=450)
    nx.draw_networkx_labels(G, pos, font_size=10)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    print(f"salvato: {out_png}")

if __name__ == "__main__":
    # leggi da file passato come argomento, altrimenti da stdin
    if len(sys.argv) > 1:
        line = open(sys.argv[1], "r", encoding="utf-8").read().strip()
    else:
        line = sys.stdin.read().strip()

    G, faces = parse_plantri_T_line(line)
    draw_graph(G, "graph.png")
