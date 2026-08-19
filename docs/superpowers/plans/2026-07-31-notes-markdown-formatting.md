# Project Notes Markdown Formatting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rendere `docs/notes.md` leggibile e navigabile con Markdown coerente, correggendo i refusi senza tradurre o modificare il significato tecnico.

**Architecture:** L'intervento resta confinato a un unico documento. La struttura conserva l'ordine esistente, usa le date come sezioni principali e distingue testo, requisiti, pseudocodice, log e profili attraverso elementi Markdown appropriati.

**Tech Stack:** Markdown, Git, comandi Unix di sola verifica (`rg`, `wc`, `diff`).

## Global Constraints

- Conservare l'ordine attuale delle note.
- Conservare italiano e inglese così come sono distribuiti nel documento.
- Correggere soltanto errori ortografici, grammaticali e di battitura evidenti.
- Non cambiare il significato di requisiti, osservazioni, log o risultati sperimentali.
- Mantenere completi i dump e gli esempi tecnici.
- Non modificare codice Python o altri documenti, esclusi i documenti Superpowers prodotti dal flusso di lavoro.

---

### Task 1: Ristrutturare e verificare `docs/notes.md`

**Files:**

- Rename already present in the worktree: `docs/notes.txt` → `docs/notes.md`
- Modify: `docs/notes.md`

**Interfaces:**

- Consumes: il testo storico completo attualmente presente in `docs/notes.md`.
- Produces: un documento Markdown autonomo, navigabile e semanticamente equivalente all'originale.

- [ ] **Step 1: Registrare i riferimenti strutturali prima della modifica**

Run:

```bash
wc -l -w -c docs/notes.md
rg -n '^(25/Apr/2026|16/Apr/2026|14/Apr/2026|20/May/2017|06/Lug/2016|07/Lug/2016|Performance)$' docs/notes.md
rg -c '^edge: ' docs/notes.md
rg -c 'DEBUG --- Face:' docs/notes.md
rg -c '^2026-02-24 ' docs/notes.md
```

Expected baseline:

- 756 lines, 8172 words and 50228 bytes before formatting.
- All dated sections and the final `Performance` section are found.
- The three counts provide preservation references for the large technical blocks.

- [ ] **Step 2: Applicare la gerarchia editoriale approvata**

Modify `docs/notes.md` with `apply_patch` and apply this exact structural map:

```markdown
# Project Notes

## Contents

- [25 April 2026 — Static review](#25-april-2026--static-review)
- [16 April 2026 — Selection strategy 4 specification](#16-april-2026--selection-strategy-4-specification)
- [14 April 2026 — Selection strategy 4 implementation notes](#14-april-2026--selection-strategy-4-implementation-notes)
- [20 May 2017 — Edge diagnostics](#20-may-2017--edge-diagnostics)
- [6 July 2016 — Reconstruction checks](#6-july-2016--reconstruction-checks)
- [7 July 2016 — Kempe chain color switching](#7-july-2016--kempe-chain-color-switching)
- [Performance profile](#performance-profile)
```

Then:

- Convert each standalone date into the corresponding `##` heading.
- In the 25 April 2026 review, use `### Verification`, `### Performance`, `### Logical errors and risks`, and `### Proposed improvements`.
- Keep the existing English specification hierarchy under 16 April 2026, demoting its current headings by one level so only dated sections use `##`.
- In the 14 April 2026 notes, use `### Algoritmo da implementare`, `### Vincolo di località`, `### Implementazione dello stato`, `### Interfaccia CLI`, `### Identificazione di \`prev_face\` tra un'iterazione e l'altra`, and `### Cosa ti chiedo`.
- In the 20 May 2017 section, place every `edge: ...` line inside one fenced `text` block.
- Split the two 6 July 2016 entries into `### Grafo a fine riduzione` and `### Perfect at first shot?`; put their raw timestamped face listings inside fenced `text` blocks while leaving the question and answer as prose.
- In the 7 July 2016 section, put the pseudocode inside a fenced `text` block and remove the redundant leading comment markers when doing so.
- Convert the final standalone `Performance` label into `## Performance profile` and enclose both the application log and cProfile table in fenced `text` blocks.
- Format filenames, function names, CLI flags, identifiers, edge names and literal values with inline backticks where they occur in prose.
- Use `-` for unordered lists and preserve ordered-list numbering.

- [ ] **Step 3: Correggere i refusi senza tradurre**

Apply only unambiguous local corrections, including:

```text
othe F5                     → other F5
edge candidata             → edge candidate
il numero di edge massimo  → il numero massimo di edge
la fallback                → il fallback
faccia merged              → faccia risultante dal merge
E' infatti                 → È infatti
first shoot                → first shot
le planarity               → la planarità (only if this phrase occurs in the file)
```

Do not normalize deliberate technical terms such as `face`, `edge`, `fallback`, `wave`, `frontier`, `F5-F5`, or `F5-F6` merely because they mix languages.

- [ ] **Step 4: Verificare sintassi e completezza**

Run:

```bash
python3 -c "from pathlib import Path; s=Path('docs/notes.md').read_text(); assert s.count('```') % 2 == 0; assert s.startswith('# Project Notes\n'); print('Markdown fences and title: OK')"
rg -n '^(## |### |#### )' docs/notes.md
rg -c '^edge: ' docs/notes.md
rg -c 'DEBUG --- Face:' docs/notes.md
rg -c '^2026-02-24 ' docs/notes.md
git diff --check -- docs/notes.txt docs/notes.md
```

Expected:

- The Python assertion prints `Markdown fences and title: OK`.
- The heading hierarchy matches the structural map.
- Counts for `edge:`, `DEBUG --- Face:`, and `2026-02-24` lines equal the Step 1 baseline.
- `git diff --check` reports no whitespace errors.

- [ ] **Step 5: Riesaminare il diff e versionare la rinomina formattata**

Run:

```bash
git diff --stat -- docs/notes.txt docs/notes.md
git diff -- docs/notes.txt docs/notes.md
git status --short
```

Confirm that no technical block was shortened and no unrelated file is staged. Then commit only the renamed/formatted notes:

```bash
git add docs/notes.txt docs/notes.md
git commit -m "docs: format project notes as Markdown"
```
