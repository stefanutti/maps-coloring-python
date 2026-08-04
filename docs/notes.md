# Project Notes

## Contents

- [25 April 2026 — Static review](#25-april-2026--static-review)
- [16 April 2026 — Selection strategy 4 specification](#16-april-2026--selection-strategy-4-specification)
- [14 April 2026 — Selection strategy 4 implementation notes](#14-april-2026--selection-strategy-4-implementation-notes)
- [20 May 2017 — Edge diagnostics](#20-may-2017--edge-diagnostics)
- [6 July 2016 — Reconstruction checks](#6-july-2016--reconstruction-checks)
- [7 July 2016 — Kempe chain color switching](#7-july-2016--kempe-chain-color-switching)
- [Performance profile](#performance-profile)

## 25 April 2026 — Static review

Ho fatto review statica e verifiche locali. Nessuna modifica al codice.

### Verification

`pytest tests -q` passa con 26 passed; smoke `python 4ct.py -s4 -r1 10` da `ct/` passa, ma non esercita davvero la fase F5.

### Performance

- La selezione è circa `O(F^2)` per iterazione e può diventare `O(F^3)` sull’intera riduzione: ogni edge candidate cerca la faccia adiacente con scan lineare su `g_faces`, ad esempio in `ct/4ct.py:1163`, `ct/4ct.py:949`, `ct/4ct.py:1005`.
- `join_faces()` viene calcolata per molti candidati solo per scartarli dopo `is_the_graph_one_edge_connected`; corretto, ma costoso perché copia liste e fa altre scansioni.
- La locality riduce solo la fase `F5`; `F2`/`F3`/`F4` restano sempre globali anche durante una wave.
- `reduce_faces()` scrive JSON a ogni iterazione su `debug.f_distribution` in `ct/4ct.py:1768`, quindi su mappe grandi l’I/O diventa rumore prestazionale.
- Il `cProfile` è sempre attivo nel `main` in `ct/4ct.py:2186`, utile per debug ma penalizzante come default.

### Logical errors and risks

- Probabile bug nella wave: dopo un fallback globale attivo, `reduce_faces()` prima aggiorna la frontier e poi la azzera in `ct/4ct.py:1598`. Questo interrompe la propagazione invece di ripartire dal punto trovato globalmente. È in tensione con la strategia “fallback globale, poi restart local expansion”.
- Il fallback `F5` non è un vero fallback generico: prova solo `F5-F5` e `F5-F6`, poi termina con `exit(-1)` in `ct/4ct.py:1212`. Esiste `_select_max_neighbor_from_candidates()` in `ct/4ct.py:1033`, ma non viene usata. Se non vuoi dipendere strettamente dal teorema “esiste sempre una coppia `F5-F5`/`F5-F6` valida”, questo è fragile.
- La fase `F2` con wave attiva termina il processo con `exit(-1)` in `ct/4ct.py:1148`. Anche se l’evento è considerato impossibile, sarebbe più sicuro gestirlo come normale `F2` o fallire con eccezione testabile.
- La fase `F2` sceglie casualmente e non verifica `is_the_graph_one_edge_connected()` in `ct/4ct.py:1137`. Se l’invariante “le `F2` sono sempre valide” è essenziale, va documentato e coperto da test.
- `g_faces.remove(f1)` e `g_faces.remove(f2)` rimuovono per uguaglianza, non per identità, in `ct/4ct.py:1625` e `ct/4ct.py:1684`. Con facce duplicate per valore può essere rimossa la faccia sbagliata.
- Le specifiche locali sono incoerenti: alcune note dicono `F5-F6` prima di `F5-F5`, altre il contrario; alcune dicono `F2` max-neighbor, il codice fa random. Questo non è necessariamente un bug, ma rende difficile validare l’algoritmo.

### Proposed improvements

1. Introdurre indici incrementali: `edge_to_face`, `faces_by_len`, e opzionalmente `vertex_to_faces`. Questo elimina quasi tutti gli scan lineari per trovare adiacenze.
2. Decidere formalmente la semantica del fallback `S4`: secondo me dovrebbe avviare una nuova frontier dal `f1_plus_f2_temp` scelto globalmente, non azzerarla.
3. Aggiungere un fallback finale su tutte le `F5` con `_select_max_neighbor_from_candidates()` prima di `exit(-1)`, oppure aggiungere un assert/test che dimostri che `F5-F5`/`F5-F6` è sempre sufficiente.
4. Sostituire `exit(-1)` con eccezioni specifiche, così i casi impossibili diventano testabili.
5. Rimuovere facce per identità o per indice, non con `list.remove()`.
6. Aggiungere test su `reduce_faces()`, soprattutto: fallback con wave attiva, `F2` con wave attiva, facce duplicate, e caso in cui non ci siano coppie `F5-F5`/`F5-F6` valide.

## 16 April 2026 — Selection strategy 4 specification

You are an expert algorithm designer and graph theorist.

### Task

Read the `ct/4ct.py` and the `ct/ct_graph_utils.py` files to understand what is implemented.

Modify the `--selection4` algorithm that performs **iterative edge-removal reduction** on a **planar 3-regular graph (cubic planar graph)** based on face configurations.

---

### Definitions

- The graph is planar and embedded (faces are explicitly available).
- Each face has a size equal to the number of edges (`F2`, `F3`, `F4`, `F5`, `F6`, etc.).
- Two faces are *adjacent* if they share an edge.
- Configurations:
  - **`F2`**: face with 2 edges
  - **`F3`**: face with 3 edges
  - **`F4`**: face with 4 edges
  - **`F5-F5`**: two adjacent faces both of size 5
  - **`F5-F6`**: two adjacent faces of size 5 and 6

---

### High-Level Strategy

The algorithm proceeds in **two phases**:

#### Phase 1 — Eliminate small faces (`F2`, `F3`, `F4`)

Repeat until no `F2`, `F3`, or `F4` faces remain:

1. Select **any face randomly** among all faces of type `F2`, `F3`, or `F4`, in the order specified by the parameter `--choices`.

2. Apply the following rules:

   - **`F2`**:

     - Remove **one of its two edges randomly**.
     - No additional constraints.

   - **`F3` or `F4`**:

     - Select an edge of the face such that the adjacent face sharing that edge has the **largest size** among candidates.
     - Remove that edge.

3. After each removal:

   - Update the planar embedding and face structure.
   - Continue until no `F2`, `F3`, `F4` remain anywhere in the graph.

---

#### Phase 2 — Handle unavoidable configurations (`F5-F6`, `F5-F5`)

At this point, the graph contains only configurations involving `F5` and `F6`.

##### Priority Order:

1. **`F5-F6` (highest priority)**
2. **`F5-F5`**

---

### Local expansion strategy ("wave-like propagation")

The reduction should proceed **locally** whenever possible:

- Maintain a set of **recently modified faces**. Optimize saving the vertices if necessary.
- Prefer selecting configurations **adjacent to already processed areas**.
- This creates a wave-like propagation over the graph.

---

### Selection Rules

#### Step 1 — Try local selection

From the neighborhood of recently modified faces:

0. After the Phase 1, the **recently modified faces** is not set
1. If there exists an **`F5-F5` configuration**, select it.
2. Else if there exists an **`F5-F6` configuration**, select it.
3. Else fallback (see below).

---

#### Step 2 — Edge removal rules

- **`F5-F5`**:

  - Apply the corresponding rule already defined in the program.
  - This should transform the other `F5` into an `F4`.

- **`F5-F6`**:

  - Select one of the two edges belonging to the **`F5` face** that shares a **vertex with the `F6` face**.
  - Remove that edge.
  - This should transform the `F6` into an `F5`.

---

#### Step 3 — Dynamic reappearance of small faces

After any edge removal:

- If a new **`F4`** face appears:

  - **Immediately process it** using the `F4` rule (from Phase 1).
  - This has priority over continuing with F5-based reductions.
  - Consider this removal as part of the local selection and add this face to the **recently modified faces**

---

#### Step 4 — Fallback Strategy

If no valid configuration (`F5-F6` or `F5-F5`) exists in the local neighborhood:

- Select **globally at random**:
  - Any available `F5-F5`, otherwise `F5-F6`.
- Restart local expansion from that point.

---

### Important Constraints

- Always update:

  - Face structure
  - Adjacency relations
  - Planar embedding consistency

- The algorithm must be:

  - Deterministic except where randomness is explicitly required
  - Modular (clear functions for face detection, adjacency, edge removal)

---

### Suggested Implementation Structure

- `find_faces_by_size(graph)`
- `find_adjacent_faces(face)`
- `select_edge_F3_F4(face)`
- `select_edge_F5-F6(face_pair)`
- `remove_edge(graph, edge)`
- `update_faces(graph)`
- `get_local_candidates(graph, region)`
- `fallback_selection(graph)`

---

### Output

- Return the sequence of edge removals.
- Optionally store intermediate graph states for reconstruction.

---

### Notes

- Do NOT implement coloring.
- Focus only on the reduction process.
- Ensure correctness of face updates after each modification.
- The algorithm must terminate.

---

Implement clean, well-documented, and testable code.

## 14 April 2026 — Selection strategy 4 implementation notes

### Algoritmo da implementare

- Regola base per le facce `F2`, `F3`, `F4`: tra tutte le facce di quella specifica dimensione (esempio `F2`), scegli l'edge la cui faccia dall'altra parte (non quella scelta) ha il numero massimo di edge. Prima esaurisci tutte le `F2`, poi le `F3`, poi le `F4`.
- Regola per `F5` (solo quando non ci sono più `F2`, `F3`, `F4`):
  - Coppia `F5-F5`: per ogni coppia di `F5` adiacenti, considera le 4 edge incidenti ai due vertici dell'edge condivisa, escludendo quindi l'edge condivisa stessa. Scegli quella in cui la faccia adiacente alle 2 `F5` ha il numero massimo di edge.
  - Coppia `F5-F6`: stessa identica logica ma con una `F5` adiacente a una `F6`.
  - Fallback: se né `F5-F5` né `F5-F6` producono candidati validi, applica la regola "max neighbor" sulle `F5`.

### Vincolo di località
- Dopo la prima selezione, le selezioni successive devono essere ristrette alle facce adiacenti alla faccia risultante dal merge prodotta dall'iterazione precedente (cioè al `f1_plus_f2_temp` restituito). Se in quel vicinato non si trova nessun candidato valido, rilascia il vincolo e cerca globalmente.

### Implementazione dello stato
- Lo stato `prev_face` deve vivere nel chiamante come variabile locale del ciclo `for i_execution`, e deve essere passato come parametro alla strategia e riaggiornato col valore di ritorno. Non usare classi, non usare attributi di funzione, non usare variabili globali. Il programma non contiene classi e voglio mantenere lo stile a funzioni. Cambia la firma delle 3 strategie esistenti e passa `prev_face = None`. La strategia nuova invece accetta e restituisce davvero `prev_face`.

### Interfaccia CLI
- Aggiungi un nuovo argomento `-s4` / `--selection4` al `group_selection` (mutuamente esclusivo con gli altri, come `-s1`/`-s2`/`-s3`) e aggiungi il relativo ramo nel dispatch della `selection_strategy`.

### Identificazione di `prev_face` tra un'iterazione e l'altra
- Il `f1_plus_f2_temp` restituito viene inserito in `g_faces` dal chiamante come stesso oggetto-lista (identity preserved). Alla chiamata successiva, per ritrovarlo in `g_faces`, usa il confronto per identità `face is prev_face`, non per uguaglianza. Se non lo trovi (perché è stato assorbito da un ulteriore merge in qualche caso limite), considera `prev_face = None` e cerca globalmente.

### Cosa ti chiedo
- Leggi `4ct.py` e `ct_graph_utils.py` per verificare strutture dati, nomi e righe esatte, poi applica queste modifiche:
  - Aggiungi la funzione `select_edge_to_remove_unavoidable_set(g_faces, choices, i_global_counter, prev_face=None)` che implementa l'algoritmo descritto e ritorna `(edge, f1, f2, f1_plus_f2_temp, new_prev_face)`.
  - Aggiungi l'argomento CLI `-s4` / `--selection4`.
  - Nel ciclo `for i_execution`, inizializza `prev_face = None` subito dopo `initialize_statistics()`.
  - Modifica la chiamata `selection_strategy(g_faces, choices, i_global_counter)` per passare `prev_face` e riassegnarlo col valore di ritorno: `edge_to_remove, f1, f2, f1_plus_f2_temp, prev_face = selection_strategy(g_faces, choices, i_global_counter, prev_face)`.

## 20 May 2017 — Edge diagnostics

```text

edge: (179, 168), down: 4, up: 10, left: 7, right: 8, (L==R) = False
edge: (286, 321), down: 4, up: 5, left: 15, right: 3, (L==R) = False
edge: (210, 214), down: 4, up: 10, left: 6, right: 5, (L==R) = False
edge: (80, 78),   down: 4, up: 4, left: 6, right: 7, (L==R) = False
edge: (214, 221), down: 4, up: 5, left: 10, right: 4, (L==R) = False
edge: (222, 332), down: 4, up: 6, left: 7, right: 17, (L==R) = False
edge: (7, 12),    down: 3, up: 7, left: 9, right: 9, (L==R) = False
edge: (144, 356), down: 4, up: 15, left: 5, right: 11, (L==R) = False
edge: (75, 85),   down: 4, up: 10, left: 10, right: 5, (L==R) = False
edge: (121, 70),  down: 4, up: 4, left: 7, right: 14, (L==R) = False
edge: (94, 95),   down: 4, up: 8, left: 7, right: 3, (L==R) = False
edge: (79, 191),  down: 4, up: 5, left: 16, right: 5, (L==R) = False
edge: (40, 41),   down: 4, up: 11, left: 7, right: 4, (L==R) = False
edge: (122, 71),  down: 4, up: 4, left: 7, right: 14, (L==R) = False
edge: (275, 322), down: 4, up: 6, left: 13, right: 11, (L==R) = False
edge: (103, 104), down: 4, up: 13, left: 6, right: 4, (L==R) = False
edge: (392, 125), down: 3, up: 7, left: 9, right: 6, (L==R) = False
edge: (23, 26),   down: 4, up: 7, left: 6, right: 7, (L==R) = False
edge: (312, 268), down: 4, up: 17, left: 7, right: 6, (L==R) = False
edge: (55, 44),   down: 3, up: 19, left: 14, right: 10, (L==R) = False
edge: (152, 150), down: 3, up: 11, left: 4, right: 11, (L==R) = False
edge: (383, 384), down: 4, up: 15, left: 11, right: 6, (L==R) = False
edge: (218, 217), down: 3, up: 8, left: 6, right: 8, (L==R) = False
edge: (295, 292), down: 4, up: 5, left: 5, right: 6, (L==R) = False
edge: (372, 364), down: 4, up: 10, left: 5, right: 10, (L==R) = False
edge: (236, 244), down: 4, up: 3, left: 11, right: 8, (L==R) = False
edge: (112, 223), down: 4, up: 10, left: 16, right: 4, (L==R) = False
edge: (98, 96),   down: 4, up: 5, left: 3, right: 7, (L==R) = False
edge: (266, 263), down: 3, up: 8, left: 6, right: 8, (L==R) = False
edge: (85, 82),   down: 4, up: 5, left: 10, right: 7, (L==R) = False
edge: (276, 270), down: 3, up: 13, left: 6, right: 15, (L==R) = False
edge: (15, 11),   down: 4, up: 9, left: 6, right: 7, (L==R) = False
edge: (62, 32),   down: 4, up: 3, left: 8, right: 7, (L==R) = False
edge: (285, 318), down: 4, up: 9, left: 15, right: 11, (L==R) = False
edge: (122, 121), down: 4, up: 7, left: 4, right: 4, (L==R) = False
edge: (0, 223),   down: 4, up: 4, left: 4, right: 10, (L==R) = False
edge: (332, 333), down: 4, up: 17, left: 6, right: 3, (L==R) = False
edge: (321, 317), down: 3, up: 5, left: 4, right: 9, (L==R) = False
edge: (137, 136), down: 4, up: 15, left: 5, right: 5, (L==R) = False
edge: (298, 297), down: 3, up: 9, left: 6, right: 6, (L==R) = False
edge: (117, 115), down: 3, up: 5, left: 8, right: 7, (L==R) = False
edge: (317, 316), down: 3, up: 9, left: 5, right: 4, (L==R) = False
edge: (223, 330), down: 4, up: 10, left: 4, right: 6, (L==R) = False
edge: (211, 221), down: 4, up: 4, left: 6, right: 5, (L==R) = False
edge: (293, 294), down: 4, up: 9, left: 6, right: 5, (L==R) = False
edge: (231, 179), down: 4, up: 7, left: 7, right: 10, (L==R) = False
edge: (1, 112),   down: 4, up: 16, left: 4, right: 10, (L==R) = False
edge: (38, 118),  down: 3, up: 4, left: 11, right: 7, (L==R) = False
edge: (176, 162), down: 3, up: 5, left: 7, right: 9, (L==R) = False
edge: (45, 91),   down: 4, up: 10, left: 19, right: 3, (L==R) = False
edge: (87, 84),   down: 3, up: 13, left: 5, right: 7, (L==R) = False
edge: (172, 178), down: 4, up: 7, left: 7, right: 7, (L==R) = False
edge: (263, 261), down: 3, up: 8, left: 8, right: 6, (L==R) = False
edge: (306, 305), down: 4, up: 4, left: 7, right: 6, (L==R) = False
edge: (95, 98),   down: 4, up: 3, left: 8, right: 5, (L==R) = False
edge: (0, 341),   down: 4, up: 4, left: 4, right: 6, (L==R) = False
edge: (208, 211), down: 4, up: 6, left: 8, right: 4, (L==R) = False
edge: (131, 337), down: 3, up: 5, left: 13, right: 12, (L==R) = False
edge: (371, 372), down: 4, up: 5, left: 15, right: 10, (L==R) = False
edge: (262, 269), down: 3, up: 8, left: 8, right: 4, (L==R) = False
edge: (0, 1),     down: 4, up: 4, left: 4, right: 16, (L==R) = False
edge: (72, 73),   down: 4, up: 10, left: 6, right: 7, (L==R) = False
edge: (47, 77),   down: 3, up: 8, left: 19, right: 10, (L==R) = False
edge: (349, 347), down: 4, up: 11, left: 13, right: 5, (L==R) = False
edge: (341, 352), down: 4, up: 6, left: 4, right: 16, (L==R) = False
edge: (187, 174), down: 4, up: 4, left: 7, right: 7, (L==R) = False
edge: (56, 118),  down: 4, up: 7, left: 19, right: 3, (L==R) = False
edge: (125, 393), down: 3, up: 6, left: 7, right: 9, (L==R) = False
edge: (161, 176), down: 3, up: 7, left: 9, right: 5, (L==R) = False
edge: (80, 72),   down: 4, up: 6, left: 4, right: 10, (L==R) = False
edge: (352, 1),   down: 4, up: 16, left: 6, right: 4, (L==R) = False
edge: (70, 121),  down: 4, up: 4, left: 14, right: 7, (L==R) = False
edge: (347, 358), down: 4, up: 5, left: 11, right: 10, (L==R) = False
edge: (174, 187), down: 4, up: 4, left: 7, right: 7, (L==R) = False
edge: (267, 264), down: 4, up: 13, left: 8, right: 8, (L==R) = False
edge: (105, 80),  down: 4, up: 6, left: 13, right: 4, (L==R) = False
edge: (118, 39),  down: 3, up: 7, left: 4, right: 11, (L==R) = False
edge: (48, 47),   down: 3, up: 19, left: 10, right: 8, (L==R) = False
edge: (96, 94),   down: 4, up: 7, left: 5, right: 8, (L==R) = False
edge: (269, 267), down: 4, up: 8, left: 3, right: 13, (L==R) = False
edge: (168, 228), down: 4, up: 8, left: 10, right: 7, (L==R) = False
edge: (6, 16),    down: 3, up: 9, left: 9, right: 7, (L==R) = False
edge: (227, 219), down: 4, up: 8, left: 7, right: 8, (L==R) = False
edge: (12, 8),    down: 3, up: 9, left: 7, right: 9, (L==R) = False
edge: (220, 229), down: 4, up: 9, left: 8, right: 7, (L==R) = False
edge: (44, 66),   down: 3, up: 10, left: 19, right: 14, (L==R) = False
edge: (355, 354), down: 4, up: 11, left: 4, right: 11, (L==R) = False
edge: (83, 105),  down: 4, up: 13, left: 7, right: 6, (L==R) = False
edge: (110, 109), down: 3, up: 5, left: 6, right: 8, (L==R) = False
edge: (32, 31),   down: 4, up: 7, left: 3, right: 14, (L==R) = False
edge: (221, 211), down: 4, up: 4, left: 5, right: 6, (L==R) = False
edge: (69, 70),   down: 4, up: 14, left: 8, right: 4, (L==R) = False
edge: (97, 91),   down: 3, up: 4, left: 7, right: 10, (L==R) = False
edge: (251, 250), down: 3, up: 10, left: 8, right: 5, (L==R) = False
edge: (77, 48),   down: 3, up: 10, left: 8, right: 19, (L==R) = False
edge: (92, 53),   down: 3, up: 10, left: 13, right: 19, (L==R) = False
edge: (370, 349), down: 4, up: 13, left: 10, right: 11, (L==R) = False
edge: (289, 291), down: 4, up: 15, left: 6, right: 4, (L==R) = False
edge: (362, 235), down: 4, up: 8, left: 6, right: 17, (L==R) = False
edge: (185, 181), down: 3, up: 7, left: 7, right: 8, (L==R) = False
edge: (156, 173), down: 4, up: 7, left: 6, right: 7, (L==R) = False
edge: (381, 122), down: 4, up: 7, left: 15, right: 4, (L==R) = False
edge: (279, 207), down: 3, up: 8, left: 17, right: 4, (L==R) = False
edge: (84, 81),   down: 3, up: 7, left: 13, right: 5, (L==R) = False
edge: (175, 174), down: 4, up: 7, left: 7, right: 4, (L==R) = False
edge: (337, 335), down: 3, up: 12, left: 5, right: 13, (L==R) = False
edge: (310, 308), down: 4, up: 3, left: 8, right: 7, (L==R) = False
edge: (53, 52),   down: 3, up: 19, left: 10, right: 13, (L==R) = False
edge: (35, 369),  down: 4, up: 13, left: 16, right: 10, (L==R) = False
edge: (99, 108),  down: 4, up: 8, left: 13, right: 5, (L==R) = False
edge: (16, 10),   down: 3, up: 7, left: 9, right: 9, (L==R) = False
edge: (244, 245), down: 4, up: 8, left: 3, right: 6, (L==R) = False
edge: (281, 310), down: 4, up: 8, left: 15, right: 3, (L==R) = False
edge: (126, 41),  down: 4, up: 4, left: 6, right: 11, (L==R) = False
edge: (91, 89),   down: 3, up: 10, left: 4, right: 7, (L==R) = False
edge: (234, 236), down: 4, up: 11, left: 6, right: 3, (L==R) = False
edge: (235, 246), down: 4, up: 17, left: 8, right: 5, (L==R) = False
edge: (292, 293), down: 4, up: 6, left: 5, right: 9, (L==R) = False
edge: (255, 251), down: 3, up: 8, left: 5, right: 10, (L==R) = False
edge: (136, 147), down: 4, up: 5, left: 15, right: 11, (L==R) = False
edge: (316, 321), down: 3, up: 4, left: 9, right: 5, (L==R) = False
edge: (57, 374),  down: 3, up: 16, left: 5, right: 12, (L==R) = False
edge: (291, 325), down: 4, up: 4, left: 15, right: 11, (L==R) = False
edge: (351, 134), down: 4, up: 15, left: 11, right: 3, (L==R) = False
edge: (305, 306), down: 4, up: 4, left: 6, right: 7, (L==R) = False
edge: (133, 132), down: 3, up: 6, left: 15, right: 4, (L==R) = False
edge: (95, 93),   down: 3, up: 8, left: 4, right: 5, (L==R) = False
edge: (308, 310), down: 3, up: 4, left: 7, right: 8, (L==R) = False
edge: (19, 18),   down: 3, up: 4, left: 6, right: 7, (L==R) = False
edge: (114, 111), down: 4, up: 5, left: 4, right: 6, (L==R) = False
edge: (132, 353), down: 4, up: 6, left: 3, right: 11, (L==R) = False
edge: (236, 242), down: 3, up: 11, left: 4, right: 8, (L==R) = False
edge: (52, 92),   down: 3, up: 13, left: 19, right: 10, (L==R) = False
edge: (390, 23),  down: 4, up: 6, left: 9, right: 7, (L==R) = False
edge: (321, 316), down: 4, up: 3, left: 5, right: 9, (L==R) = False
edge: (307, 304), down: 4, up: 8, left: 7, right: 6, (L==R) = False
edge: (209, 208), down: 4, up: 8, left: 5, right: 6, (L==R) = False
edge: (147, 148), down: 4, up: 11, left: 5, right: 5, (L==R) = False
edge: (14, 157),  down: 4, up: 6, left: 9, right: 10, (L==R) = False
edge: (369, 367), down: 4, up: 10, left: 13, right: 7, (L==R) = False
edge: (126, 123), down: 4, up: 6, left: 4, right: 7, (L==R) = False
edge: (265, 269), down: 4, up: 3, left: 8, right: 8, (L==R) = False
edge: (153, 355), down: 4, up: 4, left: 5, right: 11, (L==R) = False
edge: (261, 266), down: 3, up: 6, left: 8, right: 8, (L==R) = False
edge: (78, 80),   down: 4, up: 4, left: 7, right: 6, (L==R) = False
edge: (108, 114), down: 4, up: 5, left: 8, right: 4, (L==R) = False
edge: (268, 205), down: 4, up: 6, left: 17, right: 10, (L==R) = False
edge: (225, 333), down: 3, up: 4, left: 7, right: 17, (L==R) = False
edge: (39, 38),   down: 3, up: 11, left: 7, right: 4, (L==R) = False
edge: (288, 276), down: 3, up: 6, left: 15, right: 13, (L==R) = False
edge: (178, 187), down: 4, up: 7, left: 7, right: 4, (L==R) = False
edge: (24, 35),   down: 4, up: 16, left: 7, right: 13, (L==R) = False
edge: (242, 244), down: 3, up: 8, left: 11, right: 4, (L==R) = False
edge: (343, 350), down: 4, up: 11, left: 7, right: 6, (L==R) = False
edge: (150, 164), down: 3, up: 11, left: 11, right: 4, (L==R) = False
edge: (97, 51),   down: 4, up: 7, left: 3, right: 19, (L==R) = False
edge: (245, 234), down: 4, up: 6, left: 8, right: 11, (L==R) = False
edge: (328, 326), down: 3, up: 8, left: 6, right: 9, (L==R) = False
edge: (322, 258), down: 4, up: 11, left: 6, right: 8, (L==R) = False
edge: (123, 40),  down: 4, up: 7, left: 6, right: 11, (L==R) = False
edge: (115, 119), down: 3, up: 7, left: 5, right: 8, (L==R) = False
edge: (121, 120), down: 4, up: 7, left: 4, right: 8, (L==R) = False
edge: (223, 0),   down: 4, up: 4, left: 10, right: 4, (L==R) = False
edge: (391, 390), down: 4, up: 9, left: 7, right: 6, (L==R) = False
edge: (353, 351), down: 4, up: 11, left: 6, right: 15, (L==R) = False
edge: (333, 225), down: 4, up: 3, left: 17, right: 7, (L==R) = False
edge: (395, 362), down: 4, up: 6, left: 5, right: 8, (L==R) = False
edge: (358, 370), down: 4, up: 10, left: 5, right: 13, (L==R) = False
edge: (74, 75),   down: 4, up: 10, left: 7, right: 10, (L==R) = False
edge: (341, 0),   down: 4, up: 4, left: 6, right: 4, (L==R) = False
edge: (61, 62),   down: 4, up: 8, left: 14, right: 3, (L==R) = False
edge: (335, 131), down: 3, up: 13, left: 12, right: 5, (L==R) = False
edge: (393, 392), down: 3, up: 9, left: 6, right: 7, (L==R) = False
edge: (51, 45),   down: 4, up: 19, left: 7, right: 10, (L==R) = False
edge: (139, 156), down: 4, up: 6, left: 15, right: 7, (L==R) = False
edge: (153, 144), down: 4, up: 5, left: 4, right: 15, (L==R) = False
edge: (2, 385),   down: 4, up: 16, left: 10, right: 9, (L==R) = False
edge: (330, 341), down: 4, up: 6, left: 10, right: 4, (L==R) = False
edge: (21, 127),  down: 3, up: 5, left: 10, right: 5, (L==R) = False
edge: (111, 103), down: 4, up: 6, left: 5, right: 13, (L==R) = False
edge: (318, 325), down: 4, up: 11, left: 9, right: 4, (L==R) = False
edge: (114, 104), down: 4, up: 4, left: 5, right: 13, (L==R) = False
edge: (299, 300), down: 4, up: 9, left: 6, right: 7, (L==R) = False
edge: (32, 62),   down: 3, up: 4, left: 7, right: 8, (L==R) = False
edge: (287, 286), down: 4, up: 15, left: 9, right: 5, (L==R) = False
edge: (173, 143), down: 4, up: 7, left: 7, right: 15, (L==R) = False
edge: (1, 0),     down: 4, up: 4, left: 16, right: 4, (L==R) = False
edge: (282, 281), down: 4, up: 15, left: 7, right: 8, (L==R) = False
edge: (207, 204), down: 4, up: 8, left: 3, right: 6, (L==R) = False
edge: (142, 188), down: 4, up: 7, left: 15, right: 7, (L==R) = False
edge: (244, 236), down: 3, up: 4, left: 8, right: 11, (L==R) = False
edge: (128, 346), down: 4, up: 13, left: 6, right: 7, (L==R) = False
edge: (297, 303), down: 3, up: 6, left: 9, right: 6, (L==R) = False
edge: (104, 99),  down: 4, up: 13, left: 4, right: 8, (L==R) = False
edge: (151, 152), down: 4, up: 11, left: 9, right: 3, (L==R) = False
edge: (195, 202), down: 3, up: 10, left: 8, right: 6, (L==R) = False
edge: (301, 207), down: 4, up: 3, left: 17, right: 8, (L==R) = False
edge: (270, 288), down: 3, up: 15, left: 13, right: 6, (L==R) = False
edge: (143, 139), down: 4, up: 15, left: 7, right: 6, (L==R) = False
edge: (119, 117), down: 3, up: 8, left: 7, right: 5, (L==R) = False
edge: (41, 126),  down: 4, up: 4, left: 11, right: 6, (L==R) = False
edge: (118, 38),  down: 4, up: 3, left: 7, right: 11, (L==R) = False
edge: (26, 391),  down: 4, up: 7, left: 7, right: 9, (L==R) = False
edge: (148, 137), down: 4, up: 5, left: 11, right: 15, (L==R) = False
edge: (215, 312), down: 4, up: 7, left: 10, right: 17, (L==R) = False
edge: (310, 309), down: 3, up: 8, left: 4, right: 7, (L==R) = False
edge: (291, 285), down: 4, up: 15, left: 4, right: 9, (L==R) = False
edge: (382, 381), down: 4, up: 15, left: 14, right: 7, (L==R) = False
edge: (73, 78),   down: 4, up: 7, left: 10, right: 4, (L==R) = False
edge: (202, 196), down: 3, up: 6, left: 10, right: 8, (L==R) = False
edge: (71, 122),  down: 4, up: 4, left: 14, right: 7, (L==R) = False
edge: (211, 210), down: 4, up: 6, left: 4, right: 10, (L==R) = False
edge: (189, 169), down: 3, up: 4, left: 5, right: 11, (L==R) = False
edge: (323, 225), down: 3, up: 7, left: 17, right: 4, (L==R) = False
edge: (120, 69),  down: 4, up: 8, left: 7, right: 14, (L==R) = False
edge: (374, 336), down: 3, up: 12, left: 16, right: 5, (L==R) = False
edge: (18, 17),   down: 3, up: 7, left: 4, right: 6, (L==R) = False
edge: (145, 153), down: 4, up: 5, left: 11, right: 4, (L==R) = False
edge: (66, 55),   down: 3, up: 14, left: 10, right: 19, (L==R) = False
edge: (41, 383),  down: 4, up: 11, left: 4, right: 15, (L==R) = False
edge: (59, 43),   down: 3, up: 19, left: 8, right: 14, (L==R) = False
edge: (8, 7),     down: 3, up: 9, left: 9, right: 7, (L==R) = False
edge: (164, 152), down: 3, up: 4, left: 11, right: 11, (L==R) = False
edge: (217, 226), down: 3, up: 8, left: 8, right: 6, (L==R) = False
edge: (294, 295), down: 4, up: 5, left: 9, right: 5, (L==R) = False
edge: (265, 262), down: 3, up: 8, left: 4, right: 8, (L==R) = False
edge: (67, 59),   down: 3, up: 8, left: 14, right: 19, (L==R) = False
edge: (134, 133), down: 3, up: 15, left: 4, right: 6, (L==R) = False
edge: (82, 74),   down: 4, up: 7, left: 5, right: 10, (L==R) = False
edge: (186, 175), down: 4, up: 7, left: 7, right: 7, (L==R) = False
edge: (264, 265), down: 4, up: 8, left: 13, right: 3, (L==R) = False
edge: (316, 287), down: 4, up: 9, left: 3, right: 15, (L==R) = False
edge: (205, 215), down: 4, up: 10, left: 6, right: 7, (L==R) = False
edge: (166, 189), down: 3, up: 5, left: 11, right: 4, (L==R) = False
edge: (169, 189), down: 4, up: 3, left: 11, right: 5, (L==R) = False
edge: (306, 307), down: 4, up: 7, left: 4, right: 8, (L==R) = False
edge: (256, 275), down: 4, up: 13, left: 8, right: 6, (L==R) = False
edge: (305, 299), down: 4, up: 6, left: 4, right: 9, (L==R) = False
edge: (188, 170), down: 4, up: 7, left: 7, right: 11, (L==R) = False
edge: (78, 83),   down: 4, up: 7, left: 4, right: 13, (L==R) = False
edge: (152, 164), down: 4, up: 3, left: 11, right: 11, (L==R) = False
edge: (141, 142), down: 4, up: 15, left: 11, right: 7, (L==R) = False
edge: (308, 282), down: 4, up: 7, left: 3, right: 15, (L==R) = False
edge: (170, 141), down: 4, up: 11, left: 7, right: 15, (L==R) = False
edge: (196, 195), down: 3, up: 8, left: 6, right: 10, (L==R) = False
edge: (191, 339), down: 4, up: 5, left: 5, right: 12, (L==R) = False
edge: (355, 153), down: 4, up: 4, left: 11, right: 5, (L==R) = False
edge: (109, 107), down: 3, up: 8, left: 5, right: 6, (L==R) = False
edge: (327, 328), down: 3, up: 6, left: 9, right: 8, (L==R) = False
edge: (34, 56),   down: 4, up: 19, left: 11, right: 7, (L==R) = False
edge: (62, 33),   down: 3, up: 8, left: 4, right: 7, (L==R) = False
edge: (301, 279), down: 3, up: 17, left: 4, right: 8, (L==R) = False
edge: (180, 185), down: 3, up: 7, left: 8, right: 7, (L==R) = False
edge: (346, 343), down: 4, up: 7, left: 13, right: 11, (L==R) = False
edge: (10, 6),    down: 3, up: 9, left: 7, right: 9, (L==R) = False
edge: (228, 231), down: 4, up: 7, left: 8, right: 7, (L==R) = False
edge: (303, 298), down: 3, up: 6, left: 6, right: 9, (L==R) = False
edge: (350, 128), down: 4, up: 6, left: 11, right: 13, (L==R) = False
edge: (204, 290), down: 4, up: 6, left: 8, right: 17, (L==R) = False
edge: (19, 15),   down: 4, up: 6, left: 3, right: 9, (L==R) = False
edge: (127, 22),  down: 3, up: 5, left: 5, right: 10, (L==R) = False
edge: (107, 110), down: 3, up: 6, left: 8, right: 5, (L==R) = False
edge: (104, 114), down: 4, up: 4, left: 13, right: 5, (L==R) = False
edge: (157, 2),   down: 4, up: 10, left: 6, right: 16, (L==R) = False
edge: (33, 32),   down: 3, up: 7, left: 8, right: 4, (L==R) = False
edge: (225, 222), down: 4, up: 7, left: 3, right: 6, (L==R) = False
edge: (183, 167), down: 4, up: 8, left: 5, right: 11, (L==R) = False
edge: (18, 19),   down: 4, up: 3, left: 7, right: 6, (L==R) = False
edge: (229, 227), down: 4, up: 7, left: 9, right: 8, (L==R) = False
edge: (181, 180), down: 3, up: 8, left: 7, right: 7, (L==R) = False
edge: (207, 301), down: 3, up: 4, left: 8, right: 17, (L==R) = False
edge: (326, 327), down: 3, up: 9, left: 8, right: 6, (L==R) = False
edge: (38, 34),   down: 4, up: 11, left: 3, right: 19, (L==R) = False
edge: (333, 323), down: 3, up: 17, left: 4, right: 7, (L==R) = False
edge: (364, 365), down: 4, up: 10, left: 10, right: 15, (L==R) = False
edge: (385, 14),  down: 4, up: 9, left: 16, right: 6, (L==R) = False
edge: (339, 68),  down: 4, up: 12, left: 5, right: 16, (L==R) = False
edge: (250, 255), down: 3, up: 5, left: 10, right: 8, (L==R) = False
edge: (174, 172), down: 4, up: 7, left: 4, right: 7, (L==R) = False
edge: (93, 98),   down: 3, up: 5, left: 8, right: 4, (L==R) = False
edge: (356, 355), down: 4, up: 11, left: 15, right: 4, (L==R) = False
edge: (81, 87),   down: 3, up: 5, left: 7, right: 13, (L==R) = False
edge: (246, 395), down: 4, up: 5, left: 17, right: 6, (L==R) = False
edge: (11, 18),   down: 4, up: 7, left: 9, right: 3, (L==R) = False
edge: (167, 169), down: 4, up: 11, left: 8, right: 3, (L==R) = False
edge: (22, 21),   down: 3, up: 10, left: 5, right: 5, (L==R) = False
edge: (226, 218), down: 3, up: 6, left: 8, right: 8, (L==R) = False
edge: (219, 220), down: 4, up: 8, left: 8, right: 9, (L==R) = False
edge: (221, 209), down: 4, up: 5, left: 4, right: 8, (L==R) = False
edge: (325, 324), down: 4, up: 11, left: 4, right: 6, (L==R) = False
edge: (17, 19),   down: 3, up: 6, left: 7, right: 4, (L==R) = False
edge: (367, 24),  down: 4, up: 7, left: 10, right: 16, (L==R) = False
edge: (309, 308), down: 3, up: 7, left: 8, right: 4, (L==R) = False
edge: (43, 67),   down: 3, up: 14, left: 19, right: 8, (L==R) = False
edge: (91, 97),   down: 4, up: 3, left: 10, right: 7, (L==R) = False
edge: (71, 382),  down: 4, up: 14, left: 4, right: 15, (L==R) = False
edge: (31, 61),   down: 4, up: 14, left: 7, right: 8, (L==R) = False
edge: (162, 161), down: 3, up: 9, left: 5, right: 7, (L==R) = False
edge: (269, 265), down: 3, up: 4, left: 8, right: 8, (L==R) = False
edge: (336, 57),  down: 3, up: 5, left: 12, right: 16, (L==R) = False
edge: (70, 71),   down: 4, up: 14, left: 4, right: 4, (L==R) = False
edge: (169, 166), down: 3, up: 11, left: 4, right: 5, (L==R) = False
edge: (164, 160), down: 4, up: 11, left: 3, right: 9, (L==R) = False
edge: (304, 305), down: 4, up: 6, left: 8, right: 4, (L==R) = False
edge: (365, 371), down: 4, up: 15, left: 10, right: 5, (L==R) = False
edge: (132, 134), down: 3, up: 4, left: 6, right: 15, (L==R) = False
edge: (300, 306), down: 4, up: 7, left: 9, right: 4, (L==R) = False
edge: (98, 95),   down: 3, up: 4, left: 5, right: 8, (L==R) = False
edge: (68, 79),   down: 4, up: 16, left: 12, right: 5, (L==R) = False
edge: (187, 186), down: 4, up: 7, left: 4, right: 7, (L==R) = False
edge: (258, 256), down: 4, up: 8, left: 11, right: 13, (L==R) = False
edge: (290, 301), down: 4, up: 17, left: 6, right: 3, (L==R) = False
edge: (189, 183), down: 4, up: 5, left: 3, right: 8, (L==R) = False
edge: (89, 97),   down: 3, up: 7, left: 10, right: 4, (L==R) = False
edge: (134, 132), down: 4, up: 3, left: 15, right: 6, (L==R) = False
edge: (324, 289), down: 4, up: 6, left: 11, right: 15, (L==R) = False
edge: (384, 126), down: 4, up: 6, left: 15, right: 4, (L==R) = False
edge: (354, 145), down: 4, up: 11, left: 11, right: 5, (L==R) = False
edge: (160, 151), down: 4, up: 9, left: 11, right: 11, (L==R) = False
edge: (325, 291), down: 4, up: 4, left: 11, right: 15, (L==R) = False
```

## 6 July 2016 — Reconstruction checks

### Grafo a fine riduzione

```text
        2016-07-06 07:25:42,872 - DEBUG --- Face: [(35, 20), (20, 24), (24, 35)]
        2016-07-06 07:25:42,872 - DEBUG --- Face: [(8, 24), (24, 20), (20, 8)]
        2016-07-06 07:25:42,872 - DEBUG --- Face: [(35, 8), (8, 20), (20, 35)]
        2016-07-06 07:25:42,872 - DEBUG --- Face: [(8, 35), (35, 24), (24, 8)]
    Grafo appena ricreato - Step 0 della ricostruzione:
        2016-07-06 07:25:42,895 - DEBUG --- Face: [(35, 24), (24, 20), (20, 35)]
        2016-07-06 07:25:42,895 - DEBUG --- Face: [(8, 35), (35, 20), (20, 8)]
        2016-07-06 07:25:42,896 - DEBUG --- Face: [(35, 8), (8, 24), (24, 35)]
        2016-07-06 07:25:42,896 - DEBUG --- Face: [(20, 24), (24, 8), (8, 20)]

```

Domanda: Lo ricostruisco con la stessa rappresentazione di `faces()`?

Risposta: Per ora lascio tutto così. È infatti lo stesso grafo

### Perfect at first shot?

Original graph:

```text
        2016-07-06 09:34:07,717 - DEBUG --- Face: [(30, 28), (28, 29), (29, 30)]
        2016-07-06 09:34:07,718 - DEBUG --- Face: [(44, 43), (43, 47), (47, 44)]
        2016-07-06 09:34:07,718 - DEBUG --- Face: [(2, 8), (8, 4), (4, 2)]
        2016-07-06 09:34:07,718 - DEBUG --- Face: [(14, 13), (13, 31), (31, 14)]
        2016-07-06 09:34:07,718 - DEBUG --- Face: [(18, 16), (16, 46), (46, 18)]
        2016-07-06 09:34:07,718 - DEBUG --- Face: [(0, 6), (6, 1), (1, 0)]
        2016-07-06 09:34:07,718 - DEBUG --- Face: [(35, 22), (22, 21), (21, 34), (34, 35)]
        2016-07-06 09:34:07,718 - DEBUG --- Face: [(52, 51), (51, 48), (48, 49), (49, 52)]
        2016-07-06 09:34:07,719 - DEBUG --- Face: [(34, 21), (21, 20), (20, 32), (32, 34)]
        2016-07-06 09:34:07,719 - DEBUG --- Face: [(24, 37), (37, 38), (38, 23), (23, 24)]
        2016-07-06 09:34:07,719 - DEBUG --- Face: [(27, 33), (33, 32), (32, 20), (20, 27)]
        2016-07-06 09:34:07,719 - DEBUG --- Face: [(42, 48), (48, 51), (51, 45), (45, 42)]
        2016-07-06 09:34:07,719 - DEBUG --- Face: [(33, 36), (36, 35), (35, 34), (34, 32), (32, 33)]
        2016-07-06 09:34:07,719 - DEBUG --- Face: [(43, 17), (17, 18), (18, 46), (46, 47), (47, 43)]
        2016-07-06 09:34:07,719 - DEBUG --- Face: [(1, 3), (3, 2), (2, 4), (4, 0), (0, 1)]
        2016-07-06 09:34:07,719 - DEBUG --- Face: [(31, 13), (13, 12), (12, 28), (28, 30), (30, 31)]
        2016-07-06 09:34:07,720 - DEBUG --- Face: [(52, 40), (40, 39), (39, 45), (45, 51), (51, 52)]
        2016-07-06 09:34:07,720 - DEBUG --- Face: [(29, 28), (28, 12), (12, 11), (11, 26), (26, 29)]
        2016-07-06 09:34:07,720 - DEBUG --- Face: [(37, 41), (41, 53), (53, 55), (55, 38), (38, 37)]
        2016-07-06 09:34:07,720 - DEBUG --- Face: [(40, 41), (41, 37), (37, 24), (24, 25), (25, 39), (39, 40)]
        2016-07-06 09:34:07,720 - DEBUG --- Face: [(55, 36), (36, 33), (33, 27), (27, 23), (23, 38), (38, 55)]
        2016-07-06 09:34:07,721 - DEBUG --- Face: [(4, 8), (8, 5), (5, 7), (7, 6), (6, 0), (0, 4)]
        2016-07-06 09:34:07,721 - DEBUG --- Face: [(5, 9), (9, 19), (19, 54), (54, 50), (50, 7), (7, 5)]
        2016-07-06 09:34:07,721 - DEBUG --- Face: [(9, 5), (5, 8), (8, 2), (2, 3), (3, 10), (10, 9)]
        2016-07-06 09:34:07,721 - DEBUG --- Face: [(41, 40), (40, 52), (52, 49), (49, 50), (50, 54), (54, 53), (53, 41)]
        2016-07-06 09:34:07,721 - DEBUG --- Face: [(17, 43), (43, 44), (44, 42), (42, 45), (45, 39), (39, 25), (25, 15), (15, 17)]
        2016-07-06 09:34:07,721 - DEBUG --- Face: [(26, 11), (11, 15), (15, 25), (25, 24), (24, 23), (23, 27), (27, 20), (20, 21), (21, 22), (22, 26)]
        2016-07-06 09:34:07,722 - DEBUG --- Face: [(14, 19), (19, 9), (9, 10), (10, 16), (16, 18), (18, 17), (17, 15), (15, 11), (11, 12), (12, 13), (13, 14)]
        2016-07-06 09:34:07,722 - DEBUG --- Face: [(31, 30), (30, 29), (29, 26), (26, 22), (22, 35), (35, 36), (36, 55), (55, 53), (53, 54), (54, 19), (19, 14), (14, 31)]
        2016-07-06 09:34:07,722 - DEBUG --- Face: [(50, 49), (49, 48), (48, 42), (42, 44), (44, 47), (47, 46), (46, 16), (16, 10), (10, 3), (3, 1), (1, 6), (6, 7), (7, 50)]

```

Recreated graph:

```text
        2016-07-06 09:34:08,359 - DEBUG --- Face: [(30, 28), (28, 29), (29, 30)]
        2016-07-06 09:34:08,359 - DEBUG --- Face: [(44, 43), (43, 47), (47, 44)]
        2016-07-06 09:34:08,359 - DEBUG --- Face: [(2, 8), (8, 4), (4, 2)]
        2016-07-06 09:34:08,360 - DEBUG --- Face: [(14, 13), (13, 31), (31, 14)]
        2016-07-06 09:34:08,360 - DEBUG --- Face: [(18, 16), (16, 46), (46, 18)]
        2016-07-06 09:34:08,360 - DEBUG --- Face: [(0, 6), (6, 1), (1, 0)]
        2016-07-06 09:34:08,361 - DEBUG --- Face: [(35, 22), (22, 21), (21, 34), (34, 35)]
        2016-07-06 09:34:08,361 - DEBUG --- Face: [(52, 51), (51, 48), (48, 49), (49, 52)]
        2016-07-06 09:34:08,361 - DEBUG --- Face: [(34, 21), (21, 20), (20, 32), (32, 34)]
        2016-07-06 09:34:08,361 - DEBUG --- Face: [(24, 37), (37, 38), (38, 23), (23, 24)]
        2016-07-06 09:34:08,361 - DEBUG --- Face: [(27, 33), (33, 32), (32, 20), (20, 27)]
        2016-07-06 09:34:08,362 - DEBUG --- Face: [(42, 48), (48, 51), (51, 45), (45, 42)]
        2016-07-06 09:34:08,362 - DEBUG --- Face: [(33, 36), (36, 35), (35, 34), (34, 32), (32, 33)]
        2016-07-06 09:34:08,362 - DEBUG --- Face: [(43, 17), (17, 18), (18, 46), (46, 47), (47, 43)]
        2016-07-06 09:34:08,363 - DEBUG --- Face: [(1, 3), (3, 2), (2, 4), (4, 0), (0, 1)]
        2016-07-06 09:34:08,363 - DEBUG --- Face: [(31, 13), (13, 12), (12, 28), (28, 30), (30, 31)]
        2016-07-06 09:34:08,363 - DEBUG --- Face: [(52, 40), (40, 39), (39, 45), (45, 51), (51, 52)]
        2016-07-06 09:34:08,363 - DEBUG --- Face: [(29, 28), (28, 12), (12, 11), (11, 26), (26, 29)]
        2016-07-06 09:34:08,363 - DEBUG --- Face: [(37, 41), (41, 53), (53, 55), (55, 38), (38, 37)]
        2016-07-06 09:34:08,363 - DEBUG --- Face: [(40, 41), (41, 37), (37, 24), (24, 25), (25, 39), (39, 40)]
        2016-07-06 09:34:08,364 - DEBUG --- Face: [(55, 36), (36, 33), (33, 27), (27, 23), (23, 38), (38, 55)]
        2016-07-06 09:34:08,364 - DEBUG --- Face: [(4, 8), (8, 5), (5, 7), (7, 6), (6, 0), (0, 4)]
        2016-07-06 09:34:08,364 - DEBUG --- Face: [(5, 9), (9, 19), (19, 54), (54, 50), (50, 7), (7, 5)]
        2016-07-06 09:34:08,364 - DEBUG --- Face: [(9, 5), (5, 8), (8, 2), (2, 3), (3, 10), (10, 9)]
        2016-07-06 09:34:08,364 - DEBUG --- Face: [(41, 40), (40, 52), (52, 49), (49, 50), (50, 54), (54, 53), (53, 41)]
        2016-07-06 09:34:08,364 - DEBUG --- Face: [(17, 43), (43, 44), (44, 42), (42, 45), (45, 39), (39, 25), (25, 15), (15, 17)]
        2016-07-06 09:34:08,364 - DEBUG --- Face: [(26, 11), (11, 15), (15, 25), (25, 24), (24, 23), (23, 27), (27, 20), (20, 21), (21, 22), (22, 26)]
        2016-07-06 09:34:08,365 - DEBUG --- Face: [(14, 19), (19, 9), (9, 10), (10, 16), (16, 18), (18, 17), (17, 15), (15, 11), (11, 12), (12, 13), (13, 14)]
        2016-07-06 09:34:08,365 - DEBUG --- Face: [(31, 30), (30, 29), (29, 26), (26, 22), (22, 35), (35, 36), (36, 55), (55, 53), (53, 54), (54, 19), (19, 14), (14, 31)]
        2016-07-06 09:34:08,365 - DEBUG --- Face: [(50, 49), (49, 48), (48, 42), (42, 44), (44, 47), (47, 46), (46, 16), (16, 10), (10, 3), (3, 1), (1, 6), (6, 7), (7, 50)]
```

## 7 July 2016 — Kempe chain color switching

```text
PSEUDOCODE:
Handle the different cases

if previous_edge_color_at_v1 == previous_edge_color_at_v2:

    CASE-001: Since edges at v1 and v2 are on the same Kempe cycle, apply half Kempe cycle color swapping

    delete edge at v1 + edge at v2
    insert edge (vertex_to_join_near_v1_on_the_face, v1, previous_edge_color_at_v1)
    insert edge (vertex_to_join_near_v2_on_the_face, v2, previous_edge_color_at_v2)
    kempe_chain_color_swapping(edge (vertex_to_join_near_v1_on_the_face, v1), swap previous_edge_color_at_v1 with edge_color_of_top_edge)
    insert edge (v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
    insert edge (v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
    insert edge (v1, v2, get_the_other_colors([previous_edge_color_at_v1, edge_color_of_top_edge])[0])

else:

    In this case I have to check if the edges at v1 and v2 are on the same Kempe cycle

    if are_edges_to_join_on_the_same_cycle(previous_edge_color_at_v1, previous_edge_color_at_v2) is True:

        CASE-002: Since edges at v1 and v2 are on the same Kempe cycle, apply half Kempe cycle color swapping

        delete edge at v1 + edge at v2
        insert edge (vertex_to_join_near_v1_on_the_face, v1, previous_edge_color_at_v1)
        insert edge (vertex_to_join_near_v2_on_the_face, v2, previous_edge_color_at_v2)
        kempe_chain_color_swapping(edge (vertex_to_join_near_v1_on_the_face, v1), swap previous_edge_color_at_v1 with previous_edge_color_at_v2)
        insert edge (v1, vertex_to_join_near_v1_not_on_the_face, previous_edge_color_at_v1)
        insert edge (v2, vertex_to_join_near_v2_not_on_the_face, previous_edge_color_at_v2)
        insert edge (v1, v2, get_the_other_colors([previous_edge_color_at_v1, previous_edge_color_at_v2])[0])
    else:

        CASE-003: Worst case: the two edges at v1 and v2 are on different Kempe cycles

        kempe_chain_color_swapping(edge at v1, swap previous_edge_color_at_v1 with get_the_other_colors([previous_edge_color_at_v1, edge_color_of_top_edge])[0])
        At this point ... Since previous_edge_color_at_v1 == previous_edge_color_at_v2, apply CASE-001
```

## Performance profile

```text

2026-02-24 09:31:32,970 - root - INFO - ------------------------------------------
2026-02-24 09:31:32,970 - root - INFO - BEGIN: Show the restored and 4 colored map
2026-02-24 09:31:32,971 - root - INFO - ------------------------------------------
2026-02-24 09:31:32,971 - root - INFO - BEGIN: Check if isomorphic
2026-02-24 09:31:33,014 - root - INFO - Recreated graph is equal to the original
2026-02-24 09:31:33,014 - root - INFO - END: Check if isomorphic
2026-02-24 09:31:33,117 - root - INFO - 
2026-02-24 09:31:33,117 - ct.ct_graph_utils - INFO - -----------------------------
2026-02-24 09:31:33,117 - ct.ct_graph_utils - INFO - BEGIN: Save the 4 colored map
2026-02-24 09:31:33,117 - ct.ct_graph_utils - INFO - -----------------------------
2026-02-24 09:31:33,186 - ct.ct_graph_utils - INFO - File saved: C6000
2026-02-24 09:31:33,193 - ct.ct_graph_utils - INFO - ---------------------------
2026-02-24 09:31:33,193 - ct.ct_graph_utils - INFO - END: Save the 4 colored map
2026-02-24 09:31:33,193 - ct.ct_graph_utils - INFO - ---------------------------
2026-02-24 09:31:33,193 - root - INFO - ------------------
2026-02-24 09:31:33,193 - root - INFO - BEGIN: Print stats
2026-02-24 09:31:33,193 - root - INFO - ------------------
2026-02-24 09:31:33,193 - root - INFO - Stat: CASE-F2-01 = 9
2026-02-24 09:31:33,193 - root - INFO - Stat: CASE-F3-01 = 791
2026-02-24 09:31:33,193 - root - INFO - Stat: CASE-F4-01 = 11
2026-02-24 09:31:33,193 - root - INFO - Stat: CASE-F4-02 = 1
2026-02-24 09:31:33,193 - root - INFO - Stat: CASE-F4-03 = 0
2026-02-24 09:31:33,193 - root - INFO - Stat: CASE-F5-C1!=C2-SameKempeLoop-C1-C2 = 1700
2026-02-24 09:31:33,194 - root - INFO - Stat: CASE-F5-C1==C2-SameKempeLoop-C1-C3 = 301
2026-02-24 09:31:33,194 - root - INFO - Stat: CASE-F5-C1==C2-SameKempeLoop-C1-C4 = 186
2026-02-24 09:31:33,194 - root - INFO - Stat: F# = {5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 4: 0, 13: 0, 3: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0, 29: 0, 30: 0, 31: 0, 32: 0, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0, 40: 0, 41: 0, 42: 0, 43: 0, 44: 0, 45: 0, 46: 0, 47: 0, 48: 0, 49: 0, 50: 0, 51: 0, 52: 0, 53: 0, 54: 0, 55: 0, 56: 0, 2: 3}
2026-02-24 09:31:33,194 - root - INFO - Stat: MAX_RANDOM_KEMPE_SWITCHES = 454
2026-02-24 09:31:33,194 - root - INFO - Stat: TOTAL_RANDOM_KEMPE_SWITCHES = 11327
2026-02-24 09:31:33,194 - root - INFO - Stat: time_ELABORATION = 476
2026-02-24 09:31:33,194 - root - INFO - Stat: time_ELABORATION_BEGIN = Tue Feb 24 09:23:36 2026
2026-02-24 09:31:33,194 - root - INFO - Stat: time_ELABORATION_END = Tue Feb 24 09:31:32 2026
2026-02-24 09:31:33,194 - root - INFO - Stat: time_GRAPH_CREATION_BEGIN = Tue Feb 24 09:23:33 2026
2026-02-24 09:31:33,194 - root - INFO - Stat: time_GRAPH_CREATION_END = Tue Feb 24 09:23:36 2026
2026-02-24 09:31:33,194 - root - INFO - ----------------
2026-02-24 09:31:33,194 - root - INFO - END: Print stats
2026-02-24 09:31:33,194 - root - INFO - ----------------
```

```text
         1236211882 function calls (1224943724 primitive calls) in 478.448 seconds

   Ordered by: cumulative time
   List reduced from 467 to 30 due to restriction <30>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000  479.644  479.644 /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct/4ct.py:1630(main)
        1    0.012    0.012  467.749  467.749 /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct/4ct.py:1475(rebuild_faces)
     2187    1.496    0.001  467.401    0.214 /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct/4ct.py:613(ariadne_case_f5)
    11327    7.030    0.001  186.534    0.016 /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct/../ct/ct_graph_utils.py:168(graph_random_edge)
 11605199   49.700    0.000  172.021    0.000 /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct/../ct/ct_graph_utils.py:69(graph_edges_incident)
    13515   15.341    0.001  164.196    0.012 /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct/../ct/ct_graph_utils.py:268(kempe_chain_color_swap)
115982256  115.989    0.000  158.667    0.000 /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/networkx/classes/reportviews.py:988(__iter__)
    17401   18.212    0.001  114.153    0.007 /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct/../ct/ct_graph_utils.py:718(are_edges_on_the_same_kempe_cycle)
5624608/5606608   12.419    0.000  109.196    0.000 {built-in method builtins.sum}
    15701    0.019    0.000   96.947    0.006 /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/networkx/classes/reportviews.py:954(__len__)
 57982127   13.186    0.000   89.309    0.000 /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/networkx/classes/reportviews.py:955(<genexpr>)
116098858   37.518    0.000   80.590    0.000 <frozen _collections_abc>:892(__iter__)
193283336   29.649    0.000   29.649    0.000 {method 'items' of 'dict' objects}
 46103181   20.587    0.000   26.229    0.000 /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/networkx/classes/coreviews.py:81(__getitem__)
  5584902    2.936    0.000   23.907    0.000 /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct/../ct/ct_graph_utils.py:89(graph_degree)
 46440418   18.877    0.000   23.636    0.000 <frozen _collections_abc>:823(items)
 22885161    7.096    0.000   22.002    0.000 /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/networkx/classes/graph.py:498(__getitem__)
  5584907    2.455    0.000   20.971    0.000 /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/networkx/classes/reportviews.py:428(__call__)
 52102813   13.184    0.000   20.044    0.000 /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/networkx/classes/coreviews.py:50(__iter__)
  5605578    5.859    0.000   19.536    0.000 /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct/../ct/ct_graph_utils.py:544(is_multiedge)
  5571398    6.236    0.000   19.514    0.000 /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct/../ct/ct_graph_utils.py:142(graph_set_edge_label)
  5584902    5.178    0.000   18.516    0.000 /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/networkx/classes/reportviews.py:595(__getitem__)
 22867161   11.387    0.000   14.895    0.000 /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/networkx/classes/coreviews.py:103(__getitem__)
115915608   13.022    0.000   13.022    0.000 /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/networkx/classes/reportviews.py:934(<lambda>)
57745602/52107196    8.588    0.000    9.964    0.000 {built-in method builtins.iter}
     2188    0.010    0.000    9.865    0.005 /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct/../ct/ct_graph_utils.py:803(apply_half_kempe_loop_color_switching)
        1    0.111    0.111    9.158    9.158 /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct/4ct.py:1221(reduce_faces)
 68970346    9.150    0.000    9.150    0.000 /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/networkx/classes/coreviews.py:44(__init__)
42482524/36870945    6.261    0.000    7.641    0.000 {built-in method builtins.len}
22335232    5.434    0.000    7.411    0.000 /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages/networkx/classes/reportviews.py:599(<genexpr>)
```
