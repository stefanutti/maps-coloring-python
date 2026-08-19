# Split & Bridge V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Creare una nuova pagina `split_and_bridge_v2.html` con canvas immersivo Graphite, controlli flottanti e tutte le funzionalità della pagina originale preservate.

**Architecture:** La V2 resta un singolo documento HTML autosufficiente per seguire la struttura esistente. La logica Graphology/Cytoscape viene copiata senza alterarne gli algoritmi; il nuovo markup mantiene gli ID pubblici esistenti, mentre un piccolo livello UI separato gestisce drawer, statistiche e messaggi di stato.

**Tech Stack:** HTML5, CSS3, JavaScript ES2020, Graphology 0.25.4, Cytoscape.js 3.27.0, pytest con libreria standard Python, Node.js per il controllo sintattico JavaScript, browser locale per QA.

## Global Constraints

- Creare esclusivamente `ct/web_split_and_bridge/split_and_bridge_v2.html`; `split_and_bridge.html` deve restare invariato.
- Conservare Graphology 0.25.4 e Cytoscape.js 3.27.0 dagli stessi CDN.
- Conservare creazione del grafo, Split & Bridge, fisica, archi paralleli, trascinamento, curvatura, selezione, export DOT, etichette, debug, reset, diagnostica e `Shift+D`.
- Conservare tutti gli ID dei controlli esistenti.
- Il drawer è chiuso all'avvio e si chiude tramite pulsante, `Escape` e backdrop.
- Le animazioni devono rispettare `prefers-reduced-motion`.
- Non aggiungere dipendenze, backend, persistenza o nuovi algoritmi.

---

### Task 1: Contratto statico della pagina V2

**Files:**
- Create: `ct/tests/test_split_and_bridge_v2.py`
- Create: `ct/web_split_and_bridge/split_and_bridge_v2.html`
- Reference: `ct/web_split_and_bridge/split_and_bridge.html`

**Interfaces:**
- Consumes: gli ID e gli URL CDN della pagina originale.
- Produces: una baseline V2 caricabile con gli ID legacy `graph-container`, `edgeSplitInput`, `btnSplitEdges`, `btnExportDot`, `toggleNodeLabels`, `toggleEdgeLabels`, `toggleDebug` e tutti gli ID `cfg*`. Gli ID nuovi di drawer, statistiche e stato appartengono al Task 2.

- [ ] **Step 1: Scrivere il test di contratto che fallisce**

```python
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import subprocess

CT_ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = CT_ROOT / "web_split_and_bridge/split_and_bridge.html"
V2 = CT_ROOT / "web_split_and_bridge/split_and_bridge_v2.html"

REQUIRED_IDS = {
    "graph-container", "edgeSplitInput", "btnSplitEdges", "btnExportDot",
    "toggleNodeLabels", "toggleEdgeLabels", "toggleDebug", "cfgEdgeWidth",
    "cfgNodeWidth", "cfgPhysicsSpringLength", "cfgPhysicsRepulsion",
    "cfgPhysicsSpringStrength", "cfgPhysicsDamping",
    "cfgPhysicsMaxVelocity", "cfgNodeColor", "cfgEdgeColor",
}

class IdParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.script_sources = []
        self.attributes_by_id = {}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids.append(attributes["id"])
            self.attributes_by_id[attributes["id"]] = attributes
        if tag == "script" and "src" in attributes:
            self.script_sources.append(attributes["src"])

def test_v2_has_unique_required_control_ids():
    parser = IdParser()
    parser.feed(V2.read_text(encoding="utf-8"))
    assert REQUIRED_IDS <= set(parser.ids)
    assert len(parser.ids) == len(set(parser.ids))

def test_v2_preserves_runtime_dependencies():
    parser = IdParser()
    parser.feed(V2.read_text(encoding="utf-8"))
    assert parser.script_sources == [
        "https://unpkg.com/graphology@0.25.4/dist/graphology.umd.min.js",
        "https://unpkg.com/cytoscape@3.27.0/dist/cytoscape.min.js",
    ]

def test_original_page_remains_tracked_as_a_separate_file():
    assert ORIGINAL.exists()
    assert V2.resolve() != ORIGINAL.resolve()
```

- [ ] **Step 2: Eseguire il test e verificare il fallimento**

Run: `pytest tests/test_split_and_bridge_v2.py -v` dalla directory `ct/`.

Expected: FAIL perché `split_and_bridge_v2.html` non esiste.

- [ ] **Step 3: Creare la baseline V2 tramite `apply_patch`**

Usare `apply_patch` per creare `split_and_bridge_v2.html` come copia integrale dell'originale, poi cambiare il `<title>` in:

```html
<title>4CT · Split &amp; Bridge</title>
```

Non modificare ancora funzioni, ID o valori predefiniti.

- [ ] **Step 4: Eseguire il test e verificare il passaggio**

Run: `pytest tests/test_split_and_bridge_v2.py -v` dalla directory `ct/`.

Expected: PASS; la baseline preserva il contratto pubblico e le dipendenze della pagina originale.

- [ ] **Step 5: Commit della baseline e del contratto**

```bash
git add ct/tests/test_split_and_bridge_v2.py ct/web_split_and_bridge/split_and_bridge_v2.html
git commit -m "test: define split and bridge v2 interface"
```

---

### Task 2: Shell visuale Graphite e layout responsive

**Files:**
- Modify: `ct/web_split_and_bridge/split_and_bridge_v2.html` (blocco `<style>` e markup tra `<body>` e `<script>`)
- Test: `ct/tests/test_split_and_bridge_v2.py`

**Interfaces:**
- Consumes: gli ID dei controlli definiti nel Task 1 e la variabile globale `container` letta dalla logica esistente.
- Produces: header `graphStats`, pannello azione `actionStatus`, dock, drawer `settingsDrawer` e backdrop `settingsBackdrop`, senza duplicare alcun ID.

- [ ] **Step 1: Estendere il test con i requisiti visuali e accessibili**

```python
def test_v2_exposes_accessible_shell_controls():
    source = V2.read_text(encoding="utf-8")
    parser = IdParser()
    parser.feed(source)
    v2_ids = {
        "btnOpenSettings", "btnCloseSettings", "settingsDrawer",
        "settingsBackdrop", "graphStats", "actionStatus",
    }
    assert v2_ids <= set(parser.ids)
    assert parser.attributes_by_id["btnOpenSettings"]["aria-controls"] == "settingsDrawer"
    assert parser.attributes_by_id["actionStatus"]["aria-live"] == "polite"
```

- [ ] **Step 2: Eseguire il test e verificare il fallimento**

Run: `pytest tests/test_split_and_bridge_v2.py::test_v2_exposes_accessible_shell_controls -v` dalla directory `ct/`.

Expected: FAIL perché shell e token CSS non esistono.

- [ ] **Step 3: Sostituire il CSS della pagina con il design Graphite**

Definire i token nel `:root` e applicarli a header, canvas, pannello, dock e drawer:

```css
:root {
  --graphite-950: #11161b;
  --graphite-900: #171d23;
  --graphite-850: #1d252d;
  --graphite-700: #34414c;
  --ink: #f3f1eb;
  --muted: #99a49f;
  --orange: #ff8b4c;
  --green: #58d69b;
  --danger: #ff6b6b;
}
```

Il `body` usa una griglia con header di 52 px e workspace flessibile. `#graph-container` riempie il workspace. Pannello e dock usano superfici `rgba(...)` con `backdrop-filter`, ma dispongono sempre di un colore di fallback opaco. Aggiungere breakpoint a 760 px e regole `prefers-reduced-motion: reduce`.

- [ ] **Step 4: Sostituire soltanto il markup dei controlli**

Creare questa gerarchia semantica mantenendo gli ID originali dei controlli:

```html
<header class="app-header">...</header>
<main class="workspace">
  <div id="graph-container" aria-label="Grafo planare interattivo"></div>
  <section class="command-card" aria-labelledby="commandTitle">...</section>
  <nav class="tool-dock" aria-label="Strumenti del grafo">...</nav>
  <div id="settingsBackdrop" class="settings-backdrop" hidden></div>
  <aside id="settingsDrawer" class="settings-drawer" aria-hidden="true">...</aside>
</main>
```

Usare checkbox native per i tre toggle, pulsanti con testo o SVG inline accompagnati da `aria-label`, e gli stessi input `cfg*` con gli stessi `min`, `max`, `step` e valori.

- [ ] **Step 5: Eseguire tutti i test statici**

Run: `pytest tests/test_split_and_bridge_v2.py -v` dalla directory `ct/`.

Expected: PASS per struttura, dipendenze, funzioni, responsive e accessibilità.

- [ ] **Step 6: Controllare la sintassi dello script inline**

Estrarre il contenuto dell'ultimo `<script>` in un file temporaneo e avvolgerlo in una funzione per permettere a Node di analizzarlo senza eseguire il DOM:

```bash
python3 -c 'from pathlib import Path; import re; s=Path("ct/web_split_and_bridge/split_and_bridge_v2.html").read_text(); blocks=re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>", s, re.S); Path("/tmp/split-and-bridge-v2.js").write_text("function syntaxCheck(){\n"+blocks[-1]+"\n}")'
node --check /tmp/split-and-bridge-v2.js
```

Expected: exit code 0 senza output.

- [ ] **Step 7: Commit della shell visuale**

```bash
git add ct/tests/test_split_and_bridge_v2.py ct/web_split_and_bridge/split_and_bridge_v2.html
git commit -m "feat: add immersive graphite graph workspace"
```

---

### Task 3: Integrazione UI, feedback e verifica browser

**Files:**
- Modify: `ct/web_split_and_bridge/split_and_bridge_v2.html` (helper UI e punti di sincronizzazione)
- Modify: `ct/tests/test_split_and_bridge_v2.py`

**Interfaces:**
- Consumes: `state.graph`, `state.selectedSplitEdges`, `initializeUI()` e `syncGraphToCytoscape()`.
- Produces: `setSettingsOpen(open: boolean): void`, `updateGraphStats(): void`, `setActionStatus(message: string, tone?: 'neutral'|'success'|'error'): void` e `splitAndBridgeEdges(tokA: string, tokB: string): {ok: boolean, message: string}`.

- [ ] **Step 1: Aggiungere test per helper e trigger UI**

```python
def test_v2_ui_helpers_change_observable_dom_state(tmp_path):
    source = V2.read_text(encoding="utf-8")
    match = re.search(r'<script id="ui-layer">(.*?)</script>', source, re.S)
    assert match, "ui-layer script must be executable in isolation"
    harness = """
const elements = new Map();
function element() {
  return { hidden: true, textContent: '', dataset: {}, attrs: {},
    classList: { values: new Set(), toggle(name, on) { on ? this.values.add(name) : this.values.delete(name); } },
    setAttribute(name, value) { this.attrs[name] = value; } };
}
['settingsDrawer','settingsBackdrop','btnOpenSettings','graphStats','actionStatus'].forEach(id => elements.set(id, element()));
global.document = { getElementById: id => elements.get(id) || null };
global.state = { graph: { order: 4, size: 6 } };
""" + match.group(1) + """
setSettingsOpen(true);
updateGraphStats();
setActionStatus('Completata', 'success');
console.log(JSON.stringify({
  open: elements.get('settingsDrawer').classList.values.has('is-open'),
  expanded: elements.get('btnOpenSettings').attrs['aria-expanded'],
  backdropHidden: elements.get('settingsBackdrop').hidden,
  stats: elements.get('graphStats').textContent,
  status: elements.get('actionStatus').textContent,
  tone: elements.get('actionStatus').dataset.tone
}));
"""
    script = tmp_path / "ui-layer-test.js"
    script.write_text(harness, encoding="utf-8")
    completed = subprocess.run(["node", script], text=True, capture_output=True, check=True)
    assert json.loads(completed.stdout) == {
        "open": True, "expanded": "true", "backdropHidden": False,
        "stats": "4 nodi · 6 archi", "status": "Completata", "tone": "success",
    }
```

- [ ] **Step 2: Eseguire il test e verificare il fallimento**

Run: `pytest tests/test_split_and_bridge_v2.py::test_v2_ui_helpers_change_observable_dom_state -v` dalla directory `ct/`.

Expected: FAIL perché gli helper UI non sono definiti.

- [ ] **Step 3: Implementare gli helper UI minimi**

Inserire gli helper in un blocco isolabile `<script id="ui-layer">`:

```javascript
function setSettingsOpen(open) {
  const drawer = document.getElementById('settingsDrawer');
  const backdrop = document.getElementById('settingsBackdrop');
  const trigger = document.getElementById('btnOpenSettings');
  if (!drawer || !backdrop || !trigger) return;
  drawer.classList.toggle('is-open', open);
  drawer.setAttribute('aria-hidden', String(!open));
  trigger.setAttribute('aria-expanded', String(open));
  backdrop.hidden = !open;
}

function updateGraphStats() {
  const element = document.getElementById('graphStats');
  if (!element || !state.graph) return;
  element.textContent = `${state.graph.order} nodi · ${state.graph.size} archi`;
}

function setActionStatus(message, tone = 'neutral') {
  const element = document.getElementById('actionStatus');
  if (!element) return;
  element.textContent = message;
  element.dataset.tone = tone;
}
```

- [ ] **Step 4: Rendere esplicito l'esito di Split & Bridge**

Senza cambiare i rami dell'algoritmo, sostituire i `return` anticipati di `splitAndBridgeEdges()` con risultati descrittivi e aggiungere il risultato positivo finale:

```javascript
if (!keyA) return { ok: false, message: `Arco "${tokA}" non trovato.` };
if (!keyB) return { ok: false, message: `Arco "${tokB}" non trovato.` };
// Nei tre punti di fallimento split:
return { ok: false, message: 'Impossibile dividere l’arco selezionato.' };
// Dopo sync, fisica e debug finali:
return { ok: true, message: 'Trasformazione completata.' };
```

- [ ] **Step 5: Collegare drawer, statistiche e feedback**

In `initializeUI()` collegare apertura, chiusura e backdrop. Aggiungere un listener `keydown` separato che chiama `setSettingsOpen(false)` quando `event.key === 'Escape'`. Chiamare `updateGraphStats()` al termine di `syncGraphToCytoscape()` e dopo l'inizializzazione.

Nel click di `btnSplitEdges`, sostituire il solo feedback di input non valido con:

```javascript
setActionStatus('Inserisci esattamente due ID separati da una virgola.', 'error');
```

Dopo la validazione, usare il risultato esplicito della funzione:

```javascript
const result = splitAndBridgeEdges(parts[0], parts[1]);
setActionStatus(result.message, result.ok ? 'success' : 'error');
```

- [ ] **Step 6: Eseguire test e controllo sintattico**

Run: `pytest tests/test_split_and_bridge_v2.py -v` dalla directory `ct/`.

Expected: tutti PASS.

Run: `node --check /tmp/split-and-bridge-v2.js` dopo aver rigenerato il file temporaneo con il comando del Task 2.

Expected: exit code 0.

- [ ] **Step 7: Verificare la pagina nel browser desktop**

Aprire `ct/web_split_and_bridge/split_and_bridge_v2.html` a circa 1440×900 e verificare:

- nessun errore in console;
- grafo visibile e canvas dominante;
- pannello e dock non si sovrappongono ai nodi iniziali in modo bloccante;
- selezione di due archi con tasto destro aggiorna `edgeSplitInput`;
- `Split & Bridge` aumenta nodi e archi e aggiorna `graphStats`;
- drawer si apre e si chiude nei tre modi previsti;
- modifica e reset di almeno un parametro funzionano;
- toggle etichette/debug ed export DOT restano disponibili.

- [ ] **Step 8: Verificare il layout mobile**

Ridimensionare a circa 390×844 e verificare che header, pannello, dock e drawer siano leggibili, raggiungibili e privi di overflow orizzontale.

- [ ] **Step 9: Controllare scope e file originale**

Run: `git diff --check && git status --short && git diff -- ct/web_split_and_bridge/split_and_bridge.html`

Expected: nessun errore whitespace; solo V2 e test risultano modificati per questa implementazione; nessuna diff per `split_and_bridge.html`.

- [ ] **Step 10: Commit finale**

```bash
git add ct/tests/test_split_and_bridge_v2.py ct/web_split_and_bridge/split_and_bridge_v2.html
git commit -m "feat: complete split and bridge v2 controls"
```
