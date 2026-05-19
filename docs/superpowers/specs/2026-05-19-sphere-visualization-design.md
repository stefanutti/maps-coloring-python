# Sphere Visualization — Design Spec

**Date:** 2026-05-19  
**Status:** Approved  
**Location:** `python_tests/sphere/`

---

## 1. Obiettivo

Strumento standalone di esplorazione visiva di una mappa planare cubica proiettata su sfera. L'utente parte da una configurazione minima (2 regioni + oceano) e la fa crescere iterativamente dividendo facce. Supporta sia interazione umana (click + conferma) sia split automatici programmastici senza UI.

Non è integrato con il flusso dell'algoritmo 4CT principale — usa la propria struttura dati interna.

---

## 2. File structure

```
python_tests/sphere/
    spherical_map.py    — SphericalMap: dati del grafo + operazione di split (zero rendering)
    renderer.py         — SphereRenderer: costruisce mesh PyVista, gestisce refresh incrementale
    interaction.py      — InteractionController: edge picking, snap preview, state machine
    main.py             — entry point: crea mappa iniziale, collega i tre moduli
```

La separazione **dati / rendering / interazione** garantisce che la modalità automatica chiami solo `spherical_map.py` senza toccare il renderer.

---

## 3. Struttura dati — SphericalMap

```python
@dataclass
class Edge:
    v_start   : int              # vid vertice di partenza
    v_end     : int              # vid vertice di arrivo
    waypoints : list[np.ndarray] # punti 3D interni sulla sfera (può essere [])
    # waypoints=[] → arco geodetico puro (slerp diretto v_start→v_end)

@dataclass
class SphericalMap:
    vertices  : dict[int, np.ndarray]  # vid → (x,y,z) su sfera unitaria
    edges     : dict[int, Edge]        # eid → Edge
    faces     : dict[int, list[int]]   # fid → lista ordinata di eid (boundary CW dall'esterno)
    colors    : dict[int, str]         # fid → colore hex
    next_vid  : int
    next_eid  : int
    next_fid  : int
```

**Invarianti da preservare ad ogni split:**
- Ogni edge appare esattamente in 2 facce (una per direzione) — identico al contratto `g_faces` del progetto 4CT
- Ogni vertice ha grado esattamente 3 (grafo cubico/3-regolare)
- Il grafo rimane planare e privo di bridge (la struttura dello split lo garantisce per costruzione)
- Tutti i vertici giacciono sulla sfera unitaria (coordinate normalizzate)

---

## 4. Stato iniziale

2 vertici (poli), 3 edge parallele (meridiani a 120°), 3 facce lune:

```python
v0 = np.array([0.0,  0.0,  1.0])   # polo nord
v1 = np.array([0.0,  0.0, -1.0])   # polo sud

# Tre meridiani: archi geodetici v0→v1 a longitudine 0°, 120°, 240°
# Ogni edge ha un waypoint equatoriale per forzare il percorso sul meridiano corretto
# (senza waypoint, slerp v0→v1 collasserebbe su un arco arbitrario tra i poli)
e0: v0→v1  waypoints=[ (1.0, 0.0, 0.0) ]           # equatore lon 0°
e1: v0→v1  waypoints=[ (-0.5, 0.866, 0.0) ]         # equatore lon 120°
e2: v0→v1  waypoints=[ (-0.5, -0.866, 0.0) ]        # equatore lon 240°

f0: [e0, rev(e1)]   # luna 0°–120°
f1: [e1, rev(e2)]   # luna 120°–240°
f2: [e2, rev(e0)]   # luna 240°–360° (designata come "oceano")
```

Formula di Eulero al momento dello start: V=2, E=3, F=3 → V−E+F = 2 ✓

Ogni split aggiunge: +2 vertici, +3 edge, +1 faccia → invariante Euleriano mantenuto.

---

## 5. Operazione di split

### Firma API

```python
def split_face(
    smap      : SphericalMap,
    fid       : int,
    eid1      : int,  t1: float,   # primo nuovo vertice: edge + parametro [0,1]
    eid2      : int,  t2: float,   # secondo nuovo vertice (eid2 == eid1 consentito)
    waypoints : list[np.ndarray] | None = None  # None → auto_waypoints()
) -> tuple[int, int]:              # (fid_new1, fid_new2)
```

### Algoritmo

1. Calcola `p = slerp(v_start(e1), v_end(e1), t1)` — normalizzato sulla sfera
2. Calcola `q = slerp(v_start(e2), v_end(e2), t2)` — normalizzato sulla sfera
3. Suddividi `e1` in `e1a` (v_start→p) e `e1b` (p→v_end), con waypoints proporzionali ereditati
4. Suddividi `e2` in `e2a` e `e2b` analogamente (se `eid1 == eid2`: split in 3 segmenti u→p, p→q, q→v)
5. Se `waypoints is None`: calcola con `auto_waypoints(p, q, face_vertices)`
6. Crea `new_arc = Edge(p, q, waypoints)`
7. Taglia il boundary di F in due percorsi: F1 = p→…→q + new_arc, F2 = q→…→p + rev(new_arc)
8. Assegna colori: F1 eredita il colore di F, F2 riceve `assign_color(smap, fid_new2)`
9. Rimuovi F, aggiungi F1 e F2

### Caso speciale eid1 == eid2

Entrambi i nuovi vertici sulla stessa edge (u,v). L'edge si divide in 3 segmenti: u→p, p→q, q→v. Il nuovo arco p→q è parallelo al segmento centrale, creando una faccia bigon (2 edge) — valida nel grafo planare cubico (coerente con la struttura iniziale del progetto 4CT che parte già da multi-edge).

---

## 6. Generazione automatica dei waypoints

```python
def auto_waypoints(
    p              : np.ndarray,
    q              : np.ndarray,
    face_vertices  : list[np.ndarray],
    strength       : float = 0.35
) -> list[np.ndarray]:
    c = normalize(np.mean(face_vertices, axis=0))   # centroide della faccia
    m = normalize(p + q)                            # midpoint geodetico p→q
    w = normalize(m + strength * (c - m))           # spostato verso il centroide

    if not point_in_face(w, face_vertices):         # fallback se concavità
        return []
    return [w]
```

Un singolo waypoint `w` spostato dal midpoint geodetico verso il centroide della faccia di `strength=0.35`. Produce un arco che curva verso l'interno della faccia dividendola in modo bilanciato — simile a un confine geografico naturale. Quando il punto di controllo cade fuori dalla faccia (possibile con facce molto concave), il fallback è una geodesica diretta.

---

## 7. API modalità automatica

```python
def split_face_auto(
    smap     : SphericalMap,
    fid      : int | None = None,  # None → faccia più grande
    strategy : str = "balanced"    # "balanced" | "random"
) -> tuple[int, int]:

def grow_map(
    smap     : SphericalMap,
    renderer,                      # SphereRenderer | None
    n_splits : int = 10,
    strategy : str = "balanced",
    show     : bool = True         # se True, aggiorna il renderer tra uno split e l'altro
) -> None:
```

**Strategia `"balanced"`:** seleziona la faccia più grande, sceglie due edge non adiacenti del boundary, piazza i punti a t=0.5, usa `auto_waypoints()`.  
**Strategia `"random"`:** faccia e parametri casuali con t ∈ [0.2, 0.8] (evita vertici degeneri vicino agli angoli).

---

## 8. Renderer PyVista

### Costruzione mesh

**Facce (regioni colorate):**
- Per ogni edge del boundary: campiona K=30 punti lungo la polilinea geodetica (slerp tra waypoints consecutivi)
- Centroide `c = normalize(mean di tutti i punti del boundary))`
- Fan-triangolazione: triangoli `(c, pts[i], pts[i+1])`
- Un `pv.PolyData` per faccia, aggiunto come attore separato

**Edge (confini):**
- Campiona 30 punti lungo la polilinea (include waypoints)
- `pv.Spline(points).tube(radius=0.004)` — tubo sottile
- Colore bianco/grigio scuro; giallo durante hover/selezione

**Vertici:**
- `pv.Sphere(radius=0.012, center=v)` — attore separato per aggiornamento individuale

### Refresh incrementale O(1)

Dopo ogni split vengono sostituiti solo gli attori coinvolti (~7 attori max), indipendentemente dal numero totale di facce:

```python
plotter.remove_actor(actors[fid])           # vecchia faccia F
plotter.remove_actor(actors[eid1])          # edge spezzata 1
plotter.remove_actor(actors[eid2])          # edge spezzata 2 (se diversa da eid1)
# Aggiunge: F1, F2, e1a, e1b, e2a, e2b (o 3 se same-edge), new_arc, vertex_p, vertex_q
plotter.render()
```

### Navigazione

- **Rotazione**: drag tasto destro (liberato dal left-click usato per picking)
- **Zoom**: scroll rotella — attivo in tutti gli stati
- **Pan**: drag tasto medio
- In stato `FIRST_SELECTED` o `WAYPOINT_MODE`: rotazione bloccata per evitare spostamenti accidentali durante la selezione

---

## 9. Edge picking — screen-space

```python
def find_edge_at_cursor(mx, my, max_px=14) -> tuple[int | None, float]:
    # Cache: proiezione screen di tutti i sample-point delle edge
    # Ricalcolata solo quando la camera si muove (dirty flag)
    best_eid, best_t, best_dist = None, 0.0, math.inf

    for eid, screen_pts in screen_cache.items():
        for i in range(len(screen_pts) - 1):
            d, t_local = dist_point_segment_2d(
                (mx, my), screen_pts[i], screen_pts[i+1]
            )
            if d < best_dist:
                best_dist = d
                best_eid  = eid
                best_t    = (i + t_local) / (len(screen_pts) - 1)

    return (best_eid, best_t) if best_dist < max_px else (None, None)
```

La cache si invalida (dirty) ogni volta che la camera si muove, e viene ricalcolata lazily al prossimo mouse-move event.

---

## 10. Macchina a stati — InteractionController

| Stato | Azione utente | Transizione |
|-------|--------------|-------------|
| `IDLE` | hover su edge | snap preview — rimane `IDLE` |
| `IDLE` | click su edge | → `FIRST_SELECTED` (p fissato, edge evidenziata) |
| `FIRST_SELECTED` | click su edge della **stessa faccia** | → `WAYPOINT_MODE` (q fissato) |
| `FIRST_SELECTED` | click su edge di **faccia diversa** | nessuna azione (feedback visivo) |
| `WAYPOINT_MODE` | click su punto **interno** alla faccia | aggiunge waypoint, rimane `WAYPOINT_MODE` |
| `WAYPOINT_MODE` | Backspace | rimuove ultimo waypoint |
| `WAYPOINT_MODE` | Enter / Spazio | esegue split → `IDLE` |
| qualsiasi | Escape | → `IDLE` (annulla selezione corrente) |

---

## 11. HUD overlay

- **Top-left:** stato corrente (`MODE: IDLE / FIRST_SELECTED / WAYPOINT_MODE`), coordinate di p e q, numero di waypoints
- **Top-right:** statistiche `V: N  E: N  F: N  splits: N`
- **Bottom:** key hints contestuali (cambiano in base allo stato attivo)

Implementato con `plotter.add_text(..., name='hud_*')` — aggiornato dopo ogni evento rilevante.

---

## 12. Colorazione facce

```python
PALETTE = [
    "#e53935","#1e88e5","#43a047","#fb8c00",
    "#8e24aa","#00acc1","#f4511e","#6d4c41","#546e7a","#c0ca33"
]

def assign_color(smap: SphericalMap, fid: int) -> str:
    used = {smap.colors[n] for n in neighbors(smap, fid)}
    for c in PALETTE:
        if c not in used:
            return c
    return min(PALETTE, key=lambda c: list(PALETTE).count(c))  # fallback
```

Al momento dello split: F1 eredita il colore di F, F2 riceve `assign_color()`. Il 4CT garantisce che con 4 colori esiste sempre una colorazione valida; con 10 colori il greedy locale non fallisce mai in pratica.

---

## 13. Dipendenze

Tutte già presenti nel progetto o nell'ambiente standard:

```
pyvista    # rendering 3D
numpy      # operazioni vettoriali su sfera
```

Nessuna dipendenza nuova richiesta.

---

## 14. Struttura dei test

```
python_tests/sphere/tests/
    test_spherical_map.py   — split_face: invarianti V-E-F, grado 3, Eulero
    test_auto_waypoints.py  — waypoint dentro la faccia, fallback geodesica
    test_grow_map.py        — N split automatici consecutivi senza violazioni
```

Il renderer non viene testato automaticamente (richiede display); i test coprono solo `spherical_map.py`.
