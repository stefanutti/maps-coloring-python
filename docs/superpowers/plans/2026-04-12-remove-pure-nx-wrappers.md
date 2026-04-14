# Remove Pure NetworkX Wrappers — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminare le 5 funzioni wrapper in `ct_graph_utils.py` che sono semplici pass-through di NetworkX, sostituendone i call site con chiamate dirette a `nx` o ai metodi del grafo.

**Architecture:** I wrapper erano stati introdotti per agevolare la migrazione da SageMath a NetworkX. Ora che la migrazione è completa, le funzioni senza logica aggiuntiva sono rumore inutile. Le 5 da eliminare sono: `is_graph_planar`, `graph_degree`, `graph_order`, `graph_size`, `create_networkx_graph`. I call site si trovano solo in `ct/ct_graph_utils.py` e `ct/4ct.py`.

**Tech Stack:** Python 3, NetworkX (`nx`), nessuna dipendenza aggiuntiva.

---

## Specifiche

### Funzioni da eliminare e sostituzione

| Funzione rimossa | Sostituzione diretta |
|---|---|
| `is_graph_planar(graph)` | `nx.is_planar(graph)` |
| `graph_degree(graph, vertex)` | `graph.degree(vertex)` |
| `graph_order(graph)` | `graph.number_of_nodes()` |
| `graph_size(graph)` | `graph.number_of_edges()` |
| `create_networkx_graph()` | `nx.MultiGraph()` |

### Call site da aggiornare

**In `ct/ct_graph_utils.py`:**

| Riga (circa) | Chiamata attuale | Sostituzione |
|---|---|---|
| 256 | `is_graph_planar(graph) is False` | `nx.is_planar(graph) is False` |
| 263 | `graph_order(graph)` | `graph.number_of_nodes()` |
| 263 | `graph_size(graph)` | `graph.number_of_edges()` |
| 293 | `graph_degree(graph, current_edge[direction_fix]) != 3` | `graph.degree(current_edge[direction_fix]) != 3` |
| 314 | `graph_degree(graph, current_edge[direction_fix]) != 3` | `graph.degree(current_edge[direction_fix]) != 3` |
| 638 | `create_networkx_graph()` | `nx.MultiGraph()` |

**In `ct/4ct.py`:**

| Riga (circa) | Chiamata attuale | Sostituzione |
|---|---|---|
| 149 | `from ct_graph_utils import graph_order` | rimuovere |
| 150 | `from ct_graph_utils import graph_size` | rimuovere |
| 152 | `from ct_graph_utils import create_networkx_graph` | rimuovere |
| 1223 | `graph_order(the_graph)` | `the_graph.number_of_nodes()` |
| 1631 | `create_networkx_graph()` | `nx.MultiGraph()` |
| 1933 | `graph_order(the_graph)` | `the_graph.number_of_nodes()` |
| 1933 | `graph_size(the_graph)` | `the_graph.number_of_edges()` |
| 1933 | `graph_order(the_colored_graph)` | `the_colored_graph.number_of_nodes()` |
| 1933 | `graph_size(the_colored_graph)` | `the_colored_graph.number_of_edges()` |

### Precondizioni
- `import networkx as nx` è già presente in entrambi i file.
- Nessun altro file importa queste 5 funzioni (verificato con grep).

### Postcondizioni
- Le 5 funzioni non esistono più in `ct_graph_utils.py`.
- Nessun `import` di queste funzioni rimane in `4ct.py`.
- Il comportamento del programma è identico.
- I test passano.

### Invarianti
- Le funzioni wrapper con logica aggiuntiva (`graph_edges`, `graph_add_edge`, `graph_delete_edge`, ecc.) **non vengono toccate**.

---

## File coinvolti

- **Modificati:** `ct/ct_graph_utils.py`, `ct/4ct.py`
- **Creati:** `tests/test_no_pure_wrappers.py` (test di non-regressione)
- **Non toccati:** tutti gli altri file

---

## Task 1: Scrivere il test di non-regressione (RED)

**Files:**
- Create: `tests/test_no_pure_wrappers.py`

- [ ] **Step 1: Creare il file di test**

```python
# tests/test_no_pure_wrappers.py
"""
Test di non-regressione: verifica che le funzioni wrapper pure
NON esistano più in ct_graph_utils e che le API nx dirette
producano i risultati attesi.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ct'))

import pytest
import networkx as nx
import ct_graph_utils


def test_is_graph_planar_wrapper_removed():
    """is_graph_planar non deve esistere in ct_graph_utils."""
    assert not hasattr(ct_graph_utils, 'is_graph_planar'), \
        "is_graph_planar è ancora presente — rimuoverla"


def test_graph_degree_wrapper_removed():
    """graph_degree non deve esistere in ct_graph_utils."""
    assert not hasattr(ct_graph_utils, 'graph_degree'), \
        "graph_degree è ancora presente — rimuoverla"


def test_graph_order_wrapper_removed():
    """graph_order non deve esistere in ct_graph_utils."""
    assert not hasattr(ct_graph_utils, 'graph_order'), \
        "graph_order è ancora presente — rimuoverla"


def test_graph_size_wrapper_removed():
    """graph_size non deve esistere in ct_graph_utils."""
    assert not hasattr(ct_graph_utils, 'graph_size'), \
        "graph_size è ancora presente — rimuoverla"


def test_create_networkx_graph_wrapper_removed():
    """create_networkx_graph non deve esistere in ct_graph_utils."""
    assert not hasattr(ct_graph_utils, 'create_networkx_graph'), \
        "create_networkx_graph è ancora presente — rimuoverla"


# --- Test che le API nx dirette funzionano correttamente ---

def test_nx_is_planar_works():
    g = nx.MultiGraph()
    g.add_edges_from([(0, 1), (1, 2), (2, 0)])
    assert nx.is_planar(g) is True


def test_nx_degree_works():
    g = nx.MultiGraph()
    g.add_edges_from([(0, 1), (0, 2), (0, 3)])
    assert g.degree(0) == 3


def test_nx_number_of_nodes_works():
    g = nx.MultiGraph()
    g.add_nodes_from([0, 1, 2])
    assert g.number_of_nodes() == 3


def test_nx_number_of_edges_works():
    g = nx.MultiGraph()
    g.add_edges_from([(0, 1), (1, 2)])
    assert g.number_of_edges() == 2


def test_nx_multigraph_creation():
    g = nx.MultiGraph()
    assert isinstance(g, nx.MultiGraph)
```

- [ ] **Step 2: Eseguire il test per verificare che fallisce (RED)**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python
python -m pytest tests/test_no_pure_wrappers.py -v
```

Output atteso: i 5 test `test_*_wrapper_removed` falliscono con `AssertionError` perché le funzioni esistono ancora. I test sulle API nx dirette passano.

- [ ] **Step 3: Commit del test rosso**

```bash
git add tests/test_no_pure_wrappers.py
git commit -m "test: add non-regression tests for pure nx wrapper removal"
```

---

## Task 2: Aggiornare i call site in `ct_graph_utils.py` (GREEN)

**Files:**
- Modify: `ct/ct_graph_utils.py`

- [ ] **Step 1: Rimuovere la funzione `is_graph_planar` e aggiornare il call site**

Rimuovere le righe:
```python
def is_graph_planar(graph):
    """
    Check if graph is planar.
    Sage API: graph.is_planar()
    """
    return nx.is_planar(graph)
```

Alla riga ~256, sostituire:
```python
    if is_graph_planar(graph) is False:
```
con:
```python
    if nx.is_planar(graph) is False:
```

- [ ] **Step 2: Rimuovere la funzione `graph_degree` e aggiornare i call site**

Rimuovere le righe:
```python
def graph_degree(graph, vertex):
    """
    Return degree of a vertex.
    Sage API: graph.degree(vertex)
    """
    return graph.degree(vertex)
```

Alle righe ~293 e ~314, sostituire:
```python
    if graph_degree(graph, current_edge[direction_fix]) != 3:
```
con:
```python
    if graph.degree(current_edge[direction_fix]) != 3:
```
(entrambe le occorrenze)

- [ ] **Step 3: Rimuovere la funzione `graph_order` e aggiornare il call site**

Rimuovere le righe:
```python
def graph_order(graph):
    """
    Return number of vertices.
    Sage API: graph.order()
    """
    return graph.number_of_nodes()
```

Alla riga ~263, sostituire:
```python
    logger.info("The graph has %s vertices and %s edges", graph_order(graph), graph_size(graph))
```
con:
```python
    logger.info("The graph has %s vertices and %s edges", graph.number_of_nodes(), graph.number_of_edges())
```

- [ ] **Step 4: Rimuovere la funzione `graph_size`**

Rimuovere le righe (il call site è già stato aggiornato nello step 3):
```python
def graph_size(graph):
    """
    Return number of edges.
    Sage API: graph.size()
    """
    return graph.number_of_edges()
```

- [ ] **Step 5: Rimuovere la funzione `create_networkx_graph` e aggiornare il call site**

Rimuovere le righe:
```python
def create_networkx_graph():
    """
    Create a new MultiGraph (equivalent to Sage Graph with multiple edges allowed).
    Sage API: Graph(sparse=True) with allow_multiple_edges(True)
    """
    return nx.MultiGraph()
```

Alla riga ~638, sostituire:
```python
    new_graph = create_networkx_graph()  # Creates nx.MultiGraph
```
con:
```python
    new_graph = nx.MultiGraph()
```

- [ ] **Step 6: Eseguire i test per verificare GREEN**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python
python -m pytest tests/test_no_pure_wrappers.py -v
```

Output atteso: tutti i 10 test passano.

- [ ] **Step 7: Commit**

```bash
git add ct/ct_graph_utils.py
git commit -m "refactor: replace pure nx wrappers with direct nx calls in ct_graph_utils"
```

---

## Task 3: Aggiornare i call site e gli import in `ct/4ct.py` (GREEN)

**Files:**
- Modify: `ct/4ct.py`

- [ ] **Step 1: Rimuovere le 3 righe di import obsolete**

Rimuovere da `ct/4ct.py`:
```python
from ct_graph_utils import graph_order
from ct_graph_utils import graph_size
from ct_graph_utils import create_networkx_graph
```

- [ ] **Step 2: Aggiornare i call site di `graph_order` alla riga ~1223**

Trovare:
```python
    logger.info("END: Create a random planar graph of %s vertices, from the dual of a random triangulation of %s vertices", graph_order(the_graph), number_of_vertices_for_the_random_triangulation)
```
Sostituire con:
```python
    logger.info("END: Create a random planar graph of %s vertices, from the dual of a random triangulation of %s vertices", the_graph.number_of_nodes(), number_of_vertices_for_the_random_triangulation)
```

- [ ] **Step 3: Aggiornare il call site di `create_networkx_graph` alla riga ~1631**

Trovare:
```python
    the_colored_graph = create_networkx_graph()  # Creates nx.MultiGraph
```
Sostituire con:
```python
    the_colored_graph = nx.MultiGraph()
```

- [ ] **Step 4: Aggiornare i call site alla riga ~1933**

Trovare (la riga con tutti e 4 i riferimenti):
```python
        if graph_order(the_graph) == graph_order(the_colored_graph) and graph_size(the_graph) == graph_size(the_colored_graph):
```
Sostituire con:
```python
        if the_graph.number_of_nodes() == the_colored_graph.number_of_nodes() and the_graph.number_of_edges() == the_colored_graph.number_of_edges():
```

- [ ] **Step 5: Eseguire i test**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python
python -m pytest tests/test_no_pure_wrappers.py -v
```

Output atteso: tutti i test passano.

- [ ] **Step 6: Verifica che non rimangano riferimenti alle funzioni rimosse**

```bash
grep -rn "graph_order\|graph_size\|create_networkx_graph\|is_graph_planar\|graph_degree" ct/4ct.py ct/ct_graph_utils.py
```

Output atteso: nessun risultato.

- [ ] **Step 7: Commit**

```bash
git add ct/4ct.py
git commit -m "refactor: replace pure nx wrapper calls with direct nx API in 4ct.py"
```

---

## Task 4: Verifica finale

- [ ] **Step 1: Eseguire tutti i test disponibili**

```bash
cd /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python
python -m pytest -v
```

- [ ] **Step 2: Verifica sintattica di entrambi i file**

```bash
python -m py_compile ct/ct_graph_utils.py && echo "OK ct_graph_utils"
python -m py_compile ct/4ct.py && echo "OK 4ct.py"
```

Output atteso: `OK ct_graph_utils` e `OK 4ct.py`.

- [ ] **Step 3: Grep finale di sicurezza su tutto il progetto**

```bash
grep -rn "graph_order\|graph_size\|create_networkx_graph\|is_graph_planar\|graph_degree" \
  --include="*.py" \
  /Users/mario.stefanutti/mario/programming/4ct/maps-coloring-python/ct/
```

Output atteso: nessun risultato.
