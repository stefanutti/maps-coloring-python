# Split & Bridge Label Controls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aggiungere due controlli indipendenti per la dimensione delle etichette e spostare il pannello Trasformazione in alto a sinistra.

**Architecture:** La pagina resta un singolo HTML autosufficiente. I valori tipografici entrano nel sistema dichiarativo `DEFAULT_CONFIG` / `CONFIG_CONTROL_DEFS`; due funzioni applicano gli stili al renderer Cytoscape e vengono richiamate nei punti di inizializzazione e sincronizzazione già esistenti. Il layout cambia solo tramite l'ancoraggio CSS della `.command-card`.

**Tech Stack:** HTML5, CSS3, JavaScript ES2020, Cytoscape.js 3.27.0, pytest, Node.js.

## Global Constraints

- Modificare soltanto `ct/web_split_and_bridge/split_and_bridge_v2.html` e i relativi test in `ct/tests/test_split_and_bridge_v2.py`.
- Conservare colori, font, visibilità predefinita, dimensione di nodi e archi, fisica e logica Split & Bridge.
- Usare `11` px come dimensione predefinita delle etichette nodo e `9` px per le etichette arco.
- Imporre minimi di `8` px per i nodi e `7` px per gli archi.
- Conservare aggiornamento immediato e ripristino tramite il sistema di controlli esistente.
- Ancorare Trasformazione a `1rem` dall'alto e da sinistra; Parametri resta a destra.
- Non creare un worktree.

---

### Task 1: Spostare Trasformazione in alto a sinistra

**Files:**
- Modify: `ct/tests/test_split_and_bridge_v2.py:548-560`
- Modify: `ct/web_split_and_bridge/split_and_bridge_v2.html:117-126`

**Interfaces:**
- Consumes: la classe CSS `.command-card` già applicata a `#group-transform`.
- Produces: `.command-card { top: 1rem; left: 1rem; right: auto; }`.

- [ ] **Step 1: Aggiornare il test visuale con il nuovo contratto**

Nel test `test_v2_visual_contract_has_contrast_texture_and_responsive_dock`, sostituire le due asserzioni dell'ancoraggio con:

```python
assert command_card["top"] == "1rem"
assert command_card["left"] == "1rem"
assert command_card["right"] == "auto"
```

- [ ] **Step 2: Eseguire il test e verificare il fallimento corretto**

Run dalla directory `ct/`:

```bash
../.venv/bin/python -m pytest tests/test_split_and_bridge_v2.py::test_v2_visual_contract_has_contrast_texture_and_responsive_dock -q
```

Expected: FAIL perché `.command-card` ha ancora `left: auto` e `right: 1rem`.

- [ ] **Step 3: Applicare il minimo cambiamento CSS**

In `.command-card`, mantenere `top: 1rem` e sostituire l'ancoraggio orizzontale con:

```css
left: 1rem;
right: auto;
```

- [ ] **Step 4: Verificare il passaggio del test mirato**

Run lo stesso comando dello Step 2.

Expected: `1 passed`.

- [ ] **Step 5: Commit del layout**

```bash
git add ct/tests/test_split_and_bridge_v2.py ct/web_split_and_bridge/split_and_bridge_v2.html
git commit -m "fix: separate transform and settings panels"
```

---

### Task 2: Aggiungere i controlli indipendenti per le etichette

**Files:**
- Modify: `ct/tests/test_split_and_bridge_v2.py:10-18,199-250,399-425`
- Modify: `ct/web_split_and_bridge/split_and_bridge_v2.html:486-497,710-734,1635-1717,1969-2006`

**Interfaces:**
- Consumes: `DEFAULT_CONFIG`, `config`, `CONFIG_CONTROL_DEFS`, `applyConfigChange(def, rawValue)` e `resetConfigControl(def)`.
- Produces: `config.nodeLabelFontSize: number`, `config.edgeLabelFontSize: number`, `applyNodeLabelFontSize(size): void` e `applyEdgeLabelFontSize(size): void`.

- [ ] **Step 1: Estendere il contratto statico dei controlli**

Aggiungere `cfgNodeLabelFontSize` e `cfgEdgeLabelFontSize` a `REQUIRED_IDS` e ad `appearance_controls`. Nel test dei gruppi verificare inoltre gli attributi letterali:

```python
assert parser.attributes_by_id["cfgNodeLabelFontSize"]["value"] == "11"
assert parser.attributes_by_id["cfgNodeLabelFontSize"]["min"] == "8"
assert parser.attributes_by_id["cfgEdgeLabelFontSize"]["value"] == "9"
assert parser.attributes_by_id["cfgEdgeLabelFontSize"]["min"] == "7"
```

- [ ] **Step 2: Scrivere il test comportamentale per aggiornamento e reset**

Estrarre ed eseguire nel harness Node le funzioni di configurazione e le due nuove funzioni di applicazione. Usare un finto oggetto stile che registra le chiamate reali a `selector(...).style(...).update()`; applicare `"14"` al controllo nodi, `"12"` al controllo archi, quindi resettare entrambi. Verificare il risultato osservabile:

```python
assert result == {
    "updated": {
        "nodeConfig": 14,
        "edgeConfig": 12,
        "nodeStyle": 14,
        "edgeStyle": 12,
    },
    "reset": {
        "nodeConfig": 11,
        "edgeConfig": 9,
        "nodeInput": "11",
        "edgeInput": "9",
        "nodeStyle": 11,
        "edgeStyle": 9,
    },
}
```

Il test deve usare le vere `applyConfigChange` e `resetConfigControl`; il doppio sostituisce solo Cytoscape, dipendenza grafica esterna.

- [ ] **Step 3: Eseguire i nuovi test e verificare il RED**

Run dalla directory `ct/`:

```bash
../.venv/bin/python -m pytest tests/test_split_and_bridge_v2.py -k "groups_parameters or label_font_size" -q
```

Expected: FAIL perché gli ID, i valori di configurazione e le funzioni di applicazione non esistono.

- [ ] **Step 4: Aggiungere i due campi alla sezione Aspetto**

Inserire nella `.config-grid`:

```html
<div class="field"><label class="field-label" for="cfgNodeLabelFontSize">Dimensione caratteri nodi</label><div class="control-row"><input id="cfgNodeLabelFontSize" type="number" min="8" step="1" value="11" /><button type="button" class="reset-btn" data-reset-target="cfgNodeLabelFontSize" aria-label="Ripristina valore predefinito" title="Ripristina valore predefinito">↺</button></div></div>
<div class="field"><label class="field-label" for="cfgEdgeLabelFontSize">Dimensione caratteri archi</label><div class="control-row"><input id="cfgEdgeLabelFontSize" type="number" min="7" step="1" value="9" /><button type="button" class="reset-btn" data-reset-target="cfgEdgeLabelFontSize" aria-label="Ripristina valore predefinito" title="Ripristina valore predefinito">↺</button></div></div>
```

- [ ] **Step 5: Integrare i valori nello stato di configurazione**

Aggiungere a `DEFAULT_CONFIG`:

```javascript
nodeLabelFontSize: 11,
edgeLabelFontSize: 9,
```

e inizializzare le stesse proprietà in `config` dai rispettivi valori predefiniti.

- [ ] **Step 6: Applicare le dimensioni al renderer Cytoscape**

Definire accanto alle funzioni di dimensionamento esistenti:

```javascript
function applyNodeLabelFontSize(size) {
  const resolved = Number.isFinite(size) ? size : config.nodeLabelFontSize;
  const fontSize = Math.max(8, resolved);
  if (!state.cy) return;
  state.cy.style().selector('node').style('font-size', fontSize).update();
}

function applyEdgeLabelFontSize(size) {
  const resolved = Number.isFinite(size) ? size : config.edgeLabelFontSize;
  const fontSize = Math.max(7, resolved);
  if (!state.cy) return;
  state.cy.style().selector('edge').style('font-size', fontSize).update();
}
```

Usare `config.nodeLabelFontSize` e `config.edgeLabelFontSize` anche nello stile iniziale di Cytoscape. Richiamare entrambe le funzioni dopo `applyNodeBaseSize` / `applyEdgeBaseWidth` in `initializeCytoscapeRenderer()` e `syncGraphToCytoscape()`.

- [ ] **Step 7: Registrare i controlli dichiarativi**

Aggiungere a `CONFIG_CONTROL_DEFS`:

```javascript
{
  id: 'cfgNodeLabelFontSize', path: ['nodeLabelFontSize'], type: 'number', min: 8, step: 1,
  onUpdate: value => { applyNodeLabelFontSize(value); }
},
{
  id: 'cfgEdgeLabelFontSize', path: ['edgeLabelFontSize'], type: 'number', min: 7, step: 1,
  onUpdate: value => { applyEdgeLabelFontSize(value); }
},
```

- [ ] **Step 8: Verificare il GREEN mirato**

Run lo stesso comando dello Step 3.

Expected: tutti i test selezionati passano.

- [ ] **Step 9: Eseguire la verifica completa**

Run dalla directory `ct/`:

```bash
../.venv/bin/python -m pytest tests/ -q
```

Expected: suite completa senza fallimenti.

Controllare inoltre il diff:

```bash
git diff --check -- ct/web_split_and_bridge/split_and_bridge_v2.html ct/tests/test_split_and_bridge_v2.py
```

Expected: exit code `0` e nessun errore di whitespace.

- [ ] **Step 10: Commit della funzionalità**

```bash
git add ct/tests/test_split_and_bridge_v2.py ct/web_split_and_bridge/split_and_bridge_v2.html
git commit -m "feat: add graph label size controls"
```
