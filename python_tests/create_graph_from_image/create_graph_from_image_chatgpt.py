#!/usr/bin/env python3

import sys
import os
import cv2
import numpy as np
from collections import deque

def distanza(p1, p2):
    """Distanza euclidea tra due punti (x1,y1) e (x2,y2)."""
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def raggruppa_punti(punti, soglia=10):
    """
    Raggruppa i punti che sono entro 'soglia' pixel di distanza in un unico centro.
    Restituisce una lista di punti "aggregati".
    """
    cluster = []
    usati = set()
    for i, p in enumerate(punti):
        if i in usati:
            continue
        vicini = [p]
        usati.add(i)
        for j, q in enumerate(punti[i+1:], start=i+1):
            if j not in usati:
                if distanza(p, q) < soglia:
                    vicini.append(q)
                    usati.add(j)
        # calcola il baricentro
        cx = np.mean([v[0] for v in vicini])
        cy = np.mean([v[1] for v in vicini])
        cluster.append((int(cx), int(cy)))
    return cluster

def get_8neighbors(x, y, w, h):
    """Restituisce le coordinate dei vicini 8-connected del pixel (x, y)."""
    offsets = [(-1, -1), (-1,  0), (-1,  1),
               ( 0, -1),           ( 0,  1),
               ( 1, -1), ( 1,  0), ( 1,  1)]
    for dx, dy in offsets:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h:
            yield nx, ny

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 script.py <immagine_di_input>")
        sys.exit(1)

    input_path = sys.argv[1]
    img = cv2.imread(input_path)
    if img is None:
        print(f"Impossibile caricare l'immagine: {input_path}")
        sys.exit(1)

    # -------------------------
    # 1) Segmentazione / Binarizzazione
    # -------------------------
    # Esempio: se le linee sono verdi
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([90, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Se invece hai linee scure su sfondo chiaro, potresti fare:
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # _, mask = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY_INV)
    # ecc.

    # Morfologia per pulire
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # -------------------------
    # 2) Rilevazione corner
    # -------------------------
    # Convertiamo in float32 per Harris/Shi-Tomasi
    mask_for_corners = mask.copy()
    # Per Harris, ci serve un'immagine in scala di grigi e normalizzata
    gray_for_corners = np.float32(mask_for_corners)

    # cornerHarris vuole un'immagine in scala di grigi con intensità
    # N.B. Qui mask_for_corners è 0 o 255. Meglio normalizzare
    # per avere un range di valori 'morbido'.
    # Oppure possiamo usare Shi-Tomasi (goodFeaturesToTrack) che spesso funziona meglio con binario.

    # Convertiamo a un'immagine di intensità 0..1
    gray_norm = gray_for_corners / 255.0

    # Harris corner detection
    blockSize = 2
    ksize = 3
    k = 0.04
    dst = cv2.cornerHarris(gray_norm, blockSize, ksize, k)

    # Risultato di cornerHarris è una mappa di risposte
    # Applichiamo una soglia per rilevare i corner
    soglia_harris = 0.01 * dst.max()  # da regolare
    corners = np.argwhere(dst > soglia_harris)  # array di (y, x) per i corner
    # Convertiamo in (x, y)
    corners = [(int(x), int(y)) for (y, x) in corners]

    # In alternativa, potremmo usare Shi-Tomasi:
    # corners_shi = cv2.goodFeaturesToTrack(np.uint8(mask), maxCorners=50, qualityLevel=0.01, minDistance=10)
    # if corners_shi is not None:
    #     corners = [(int(p[0][0]), int(p[0][1])) for p in corners_shi]

    # Raggruppiamo i corner troppo vicini
    corners = raggruppa_punti(corners, soglia=10)

    # -------------------------
    # 3) Trova archi con BFS/DFS
    # -------------------------
    # Creiamo una mappa di vertici per accedere rapidamente al loro id
    indexed_vertices = list(enumerate(corners))  # [(id, (x, y)), ...]
    vert_map = { (v[0], v[1]): i for i, v in indexed_vertices }

    # Per scoprire se due vertici sono connessi, cerchiamo un percorso di pixel bianchi tra loro.
    # Strategia simile al BFS pixel-per-pixel:
    #   - Partiamo da un corner
    #   - Espandiamo finché non troviamo un altro corner
    #   - Registriamo un arco (edge)

    visited_edges = set()

    def bfs_connect(start_id):
        queue = deque()
        start_coord = indexed_vertices[start_id][1]  # (x, y)
        queue.append(start_coord)
        visited_pixels = set([start_coord])
        
        while queue:
            cx, cy = queue.popleft()
            # Controlliamo se (cx, cy) è un *altro* corner
            if (cx, cy) != start_coord and (cx, cy) in vert_map:
                other_id = vert_map[(cx, cy)]
                edge = tuple(sorted((start_id, other_id)))
                visited_edges.add(edge)
                return  # fermiamoci al primo corner raggiunto
            
            # Altrimenti continua a camminare nei vicini bianchi
            for nx, ny in get_8neighbors(cx, cy, mask.shape[1], mask.shape[0]):
                if (nx, ny) not in visited_pixels:
                    # se è parte della linea (pixel bianco)
                    if mask[ny, nx] > 0:
                        visited_pixels.add((nx, ny))
                        queue.append((nx, ny))

    # Avviamo la BFS da ogni corner
    for vid, coord in indexed_vertices:
        bfs_connect(vid)

    edges = list(visited_edges)

    # -------------------------
    # 4) Salva in formato .dot
    # -------------------------
    basename, _ = os.path.splitext(input_path)
    output_dot = basename + ".dot"

    with open(output_dot, "w") as f:
        f.write("graph output {\n")
        # Vertici
        for (vid, (vx, vy)) in indexed_vertices:
            f.write(f'  {vid} [label="{vid}"];\n')
        # Archi
        for (v1, v2) in edges:
            f.write(f"  {v1} -- {v2};\n")
        f.write("}\n")

    print(f"Numero di vertici trovati: {len(indexed_vertices)}")
    print(f"Numero di archi trovati:   {len(edges)}")
    print(f"Grafo salvato in: {output_dot}")

if __name__ == "__main__":
    main()
