# Compact Transform Card Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ridurre al 60% il pannello Trasformazione nelle finestre strette, rimuovere il messaggio iniziale e separare meglio stato di selezione e pulsante.

**Architecture:** La modifica resta nel singolo HTML V2 e usa il breakpoint CSS già esistente. `#actionStatus` conserva la regione live e le funzioni JavaScript correnti, ma parte vuoto e viene nascosto tramite `:empty`; la spaziatura viene applicata al contenitore `.command-actions`.

**Tech Stack:** HTML5, CSS3, JavaScript ES2020, pytest.

## Global Constraints

- Modificare soltanto `ct/web_split_and_bridge/split_and_bridge_v2.html` e `ct/tests/test_split_and_bridge_v2.py`.
- La larghezza desktop resta `min(22rem, calc(100% - 2rem))`.
- Nel breakpoint `max-width: 760px`, `.command-card` usa `width: 60%` e conserva `top: 1rem`, `left: 1rem`, `right: auto`.
- `#actionStatus` resta nel DOM con `aria-live="polite"`, parte vuoto e non occupa spazio quando vuoto.
- I messaggi successivi di successo ed errore continuano a essere mostrati da `setActionStatus()`.
- Aggiungere spazio verticale esplicito tra `#selectionStatus` e `.command-actions`.
- Non modificare logica Split & Bridge, drawer Parametri, controlli tipografici, grafo, fisica, toolbar o file HTML originale.
- Non creare un worktree.

---

### Task 1: Rendere compatto il pannello Trasformazione

**Files:**
- Modify: `ct/tests/test_split_and_bridge_v2.py:168-180,712-735`
- Modify: `ct/web_split_and_bridge/split_and_bridge_v2.html:139-175,405-414,458-474`

**Interfaces:**
- Consumes: `css_declarations()`, `css_declarations_in_media()`, `IdParser.text()` e il comportamento esistente di `setActionStatus()`.
- Produces: `.action-status:empty`, `.command-card .command-actions`, larghezza mobile `60%` e `#actionStatus` inizialmente vuoto.

- [ ] **Step 1: Scrivere i test che definiscono il nuovo contratto**

Nel test accessibile aggiungere:

```python
assert parser.text("actionStatus") == ""
```

Nel test visuale aggiungere:

```python
assert command_card["width"] == "min(22rem, calc(100% - 2rem))"
assert responsive_command_card["width"] == "60%"
empty_status = css_declarations(source, ".action-status:empty")
assert empty_status["display"] == "none"
command_actions = css_declarations(source, ".command-card .command-actions")
assert command_actions["margin-top"] == ".7rem"
```

Il test `test_v2_ui_helpers_change_observable_dom_state` resta la prova che un messaggio successivo viene inserito e assume il tono richiesto.

- [ ] **Step 2: Eseguire i test mirati e verificare il RED**

Run dalla directory `ct/`:

```bash
../.venv/bin/python -m pytest tests/test_split_and_bridge_v2.py -k "accessible_shell_controls or visual_contract or ui_helpers" -q
```

Expected: FAIL perché lo stato iniziale contiene ancora “Pronto per una trasformazione.”, la larghezza mobile è `auto` e le due regole di spaziatura/visibilità non esistono.

- [ ] **Step 3: Implementare il CSS minimo**

Aggiungere accanto a `.action-status`:

```css
.action-status:empty {
  display: none;
}
```

Aggiungere la spaziatura dedicata:

```css
.command-card .command-actions {
  margin-top: .7rem;
}
```

Nel breakpoint `max-width: 760px`, cambiare soltanto:

```css
width: 60%;
```

- [ ] **Step 4: Rimuovere il testo iniziale senza eliminare la regione live**

Sostituire il contenuto del nodo con:

```html
<p id="actionStatus" class="action-status" aria-live="polite"></p>
```

- [ ] **Step 5: Verificare il GREEN mirato**

Run lo stesso comando dello Step 2.

Expected: i tre test selezionati passano.

- [ ] **Step 6: Eseguire la suite completa e il controllo diff**

Run dalla directory `ct/`:

```bash
../.venv/bin/python -m pytest tests/ -q
```

Expected: suite completa senza fallimenti.

Run dalla root:

```bash
git diff --check -- ct/web_split_and_bridge/split_and_bridge_v2.html ct/tests/test_split_and_bridge_v2.py
```

Expected: exit code `0` senza errori di whitespace.

- [ ] **Step 7: Commit**

```bash
git add ct/tests/test_split_and_bridge_v2.py ct/web_split_and_bridge/split_and_bridge_v2.html
git commit -m "refactor: compact transform panel"
```
