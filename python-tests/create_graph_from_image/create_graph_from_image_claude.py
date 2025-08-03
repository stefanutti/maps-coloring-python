#!/usr/bin/env python3

import sys
import os
import cv2
import numpy as np
from collections import deque

def get_8neighbors(x, y, w, h):
    """Restituisce la lista dei vicini 8-connected di (x, y) entro immagine w x h."""
    offsets = [(-1, -1), (-1,  0), (-1,  1),
               ( 0, -1),           ( 0,  1),
               ( 1, -1), ( 1,  0), ( 1,  1)]
    neighbors = []
    for dx, dy in offsets:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h:
            neighbors.append((nx, ny))
    return neighbors

def distanza(p1, p2):
    """Distanza euclidea tra p1=(x1,y1) e p2=(x2,y2)."""
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def raggruppa_punti(punti, soglia):
    """
    Raggruppa i punti troppo vicini (entro 'soglia') in un solo centro
    calcolando il baricentro.
    """
    cluster = []
    usati = set()
    for i, p in enumerate(punti):
        if i in usati:
            continue
        vicini = [p]
        usati.add(i)
        for j, q in enumerate(punti[i+1:], start=i+1):
            if j not in usati and distanza(p, q) < soglia:
                vicini.append(q)
                usati.add(j)
        cx = int(np.mean([v[0] for v in vicini]))
        cy = int(np.mean([v[1] for v in vicini]))
        cluster.append((cx, cy))
    return cluster

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 script.py <immagine_di_input>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    img = cv2.imread(image_path)
    if img is None:
        print("Impossibile caricare l'immagine:", image_path)
        sys.exit(1)

    # 1) Binarizzazione
    # Esempio: linee verdi
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([90, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Morfologia per ripulire
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 2) Trova componenti connesse (se ce ne sono più di una)
    # Le label vanno da 0...nLabels-1 (0 è lo sfondo)
    num_labels, labels = cv2.connectedComponents(mask)

    # Supponiamo di avere una singola grande componente di interesse.
    # In caso di più componenti, potresti iterare su ciascuna.
    # Qui, per semplicità, assumeremo di cercare i "pix bianchi" generici della maschera
    # e poi filtrare su base "pixels in labels > 0".
    # Se la tua immagine ha esattamente 1 componente connessa (oltre lo sfondo), ok.
    # Altrimenti, potresti dover gestire più componenti.

    h, w = mask.shape
    potential_vertices = []

    # 3) Individua pixel di incrocio
    for y in range(h):
        for x in range(w):
            if labels[y, x] > 0:  # pixel bianco della componente
                neighbors = get_8neighbors(x, y, w, h)
                count_white = 0
                for (nx, ny) in neighbors:
                    if labels[ny, nx] > 0:
                        count_white += 1
                # Se questo pixel ha >= 3 vicini bianchi, è un potenziale incrocio
                if count_white >= 3:
                    potential_vertices.append((x, y))

    # 4) Raggruppa i pixel di incrocio in veri e propri "vertici"
    vertices = raggruppa_punti(potential_vertices, soglia=10)

    # 5) Per costruire gli archi, facciamo BFS da ogni vertice e ci fermiamo quando
    # raggiungiamo un altro vertice o un "capolinea".
    # Creiamo una mappa (x,y) -> id vertice
    vert_map = {}
    for i, v in enumerate(vertices):
        vert_map[v] = i

    edges = set()

    def bfs_find_next_vertex(start_id):
        """Parte da un vertice e cammina lungo la maschera finché
        non trova un altro vertice o un estremo.
        Se lo trova, registra un arco."""
        start_coord = vertices[start_id]
        visited_pix = set([start_coord])
        queue = deque([start_coord])

        while queue:
            cx, cy = queue.popleft()
            # Se (cx, cy) è un altro vertice (diverso da start_coord):
            if (cx, cy) != start_coord and (cx, cy) in vert_map:
                other_id = vert_map[(cx, cy)]
                if other_id != start_id:  # per sicurezza
                    e = tuple(sorted((start_id, other_id)))
                    edges.add(e)
                return
            
            # Trova vicini bianchi e continua
            nbrs = get_8neighbors(cx, cy, w, h)
            white_nbrs = [(nx, ny) for (nx, ny) in nbrs if labels[ny, nx] > 0]
            # Se ci troviamo su un estremo (white_nbrs <= 1 e non è un vertice), fermiamoci
            if len(white_nbrs) <= 1 and (cx, cy) not in vert_map:
                # Non abbiamo trovato un altro vertice, niente edge.
                return
            
            # Altrimenti proseguiamo
            for (nx, ny) in white_nbrs:
                if (nx, ny) not in visited_pix:
                    visited_pix.add((nx, ny))
                    queue.append((nx, ny))

    # Lanciamo BFS da ogni vertice
    for v_id in range(len(vertices)):
        bfs_find_next_vertex(v_id)

    # 6) Creazione del file .dot
    basename, _ = os.path.splitext(image_path)
    output_dot = basename + ".dot"

    indexed_vertices = list(enumerate(vertices))  # [(id, (x,y)), ...]
    with open(output_dot, "w") as f:
        f.write("graph output {\n")
        # Vertici con label
        for vid, (vx, vy) in indexed_vertices:
            f.write(f'  {vid} [label="{vid}"];\n')
        # Archi
        for (v1, v2) in edges:
            f.write(f"  {v1} -- {v2};\n")
        f.write("}\n")

    print(f"Numero di vertici trovati: {len(vertices)}")
    print(f"Numero di archi trovati: {len(edges)}")
    print(f"Grafo salvato in: {output_dot}")

if __name__ == "__main__":
    main()
