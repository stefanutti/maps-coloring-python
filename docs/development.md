# Sviluppo

Questa guida raccoglie i comandi e le regole operative per lavorare con la
struttura attuale del repository. I comandi della pipeline principale assumono
`ct/` come working directory, perché `4ct.py` scrive file relativi in `debug/`.

## Requisiti

- Python 3;
- `uv` consigliato per creare l'ambiente ed eseguire Python;
- NetworkX per il core;
- pytest per i test;
- NumPy e SciPy per l'opzione `-r1`;
- pydot per i converter/visualizzatori DOT.

Il repository non contiene ancora un `pyproject.toml` o un lockfile. La
configurazione va quindi creata localmente.

## Preparazione con `uv`

Dalla root del repository:

```bash
uv venv .venv
uv pip install --python .venv/bin/python networkx numpy scipy pydot pytest
```

Per il visualizzatore DOT installare anche Matplotlib:

```bash
uv pip install --python .venv/bin/python matplotlib
```

Per l'applicazione web sulla formula di Eulero:

```bash
uv pip install --python .venv/bin/python flask flask-socketio
```

Non è necessario attivare l'ambiente se si indica esplicitamente
l'interprete. I comandi consigliati sono:

```bash
cd ct
uv run --python ../.venv/bin/python python 4ct.py --help
uv run --python ../.venv/bin/python python -m pytest tests -q
```

In alternativa:

```bash
source .venv/bin/activate
cd ct
uv run --active python 4ct.py --help
```

Con l'ambiente già attivo è possibile usare anche il normale `python`.

## Eseguire il programma

Da `ct/`:

```bash
# Duale di una triangolazione casuale di 100 punti
uv run --python ../.venv/bin/python python 4ct.py -r1 100

# Mappa casuale costruita direttamente con 100 facce
uv run --python ../.venv/bin/python python 4ct.py -r2 100

# Embedding planare
uv run --python ../.venv/bin/python python 4ct.py \
  -p path/to/map.planar

# File NetworkX edgelist
uv run --python ../.venv/bin/python python 4ct.py -e path/to/map.edgelist
```

Le strategie si selezionano con `-s1`, `-s2`, `-s3` o `-s4`. S1 è il default:

```bash
uv run --python ../.venv/bin/python python 4ct.py \
  -s4 -r2 100
```

Opzioni utili:

| Opzione | Effetto |
| --- | --- |
| `-o NAME` | Esporta `NAME.edgelist`, `NAME.orig.dot` e `NAME.dot`. |
| `-c 2345` | Imposta la priorità delle facce per S1/S2/S3. |
| `-s` | Mescola inizialmente la lista delle facce. |
| `-n N` | Ripete N volte gli input casuali o edgelist. |
| `-s1` ... `-s4` | Sceglie la strategia di selezione. |

Un file `.planar` può contenere più grafi, uno per riga. In questo caso il
programma esegue tutte le righe e il valore di `-n` viene ignorato dal
comportamento corrente. Evitare righe vuote intermedie: il conteggio iniziale
le ignora, ma la lettura successiva usa gli indici delle righe fisiche.

## Test

La suite completa si esegue da `ct/`:

```bash
uv run --python ../.venv/bin/python python -m pytest tests -q
```

Durante lo sviluppo è utile limitare il test:

```bash
uv run --python ../.venv/bin/python python -m pytest \
  tests/test_selection4.py -q

uv run --python ../.venv/bin/python python -m pytest \
  tests/test_wave_frontier.py -q

uv run --python ../.venv/bin/python python -m pytest \
  tests/test_selection4.py -k fallback -vv
```

Poiché `4ct.py` inizia con una cifra, i test lo caricano tramite `importlib`.
Non rinominare il file solo per poterlo importare: mantenere lo stesso approccio
nei nuovi test che devono accedere alle sue funzioni.

## Smoke test

Dopo cambiamenti alla pipeline, eseguire almeno un caso piccolo oltre a pytest:

```bash
uv run --python ../.venv/bin/python python 4ct.py -s1 -r2 10
uv run --python ../.venv/bin/python python 4ct.py -s4 -r2 20
```

Controllare nel log che:

- la riduzione arrivi a tre facce;
- la ricostruzione consumi tutto `ariadne_s_thread`;
- il numero di nodi e archi ricostruiti coincida con l'input;
- `is_well_colored()` non segnali errori.

I generatori e il caso F5 usano casualità. Un singolo smoke test positivo non
sostituisce i test mirati sui casi limite.

## Converter

### Generare un `.planar`

Da `ct/`:

```bash
uv run --python ../.venv/bin/python python \
  converters/ct_create_random_maps_from_2v.py \
  --faces 100 --output new_map_100.planar
```

Le opzioni `--fast` e `--show_graph` sono esposte dal parser ma, nel codice
corrente, non vengono lette da `main()` e quindi non cambiano il risultato.
Senza `--output`, l'embedding completo non viene scritto su file; il programma
stampa invece log e statistiche.

### Convertire `.planar` in `.dot` e `.edgelist`

Da `ct/`:

```bash
uv run --python ../.venv/bin/python python \
  converters/ct_convert_planar_to_other.py \
  --planar new_map_100.planar --output new_map_100
```

### Convertire GML in `.planar`

Questo converter importa il package `ct`, quindi il comando più affidabile va
eseguito dalla root del repository:

```bash
uv run --python .venv/bin/python python \
  -m ct.converters.ct_convert_gml_to_planar \
  --gml path/to/map.gml --output map.planar
```

Il parser GML legge nodi e archi, poi il converter verifica planarità,
3-regolarità e assenza di loop prima di scrivere il risultato.

## Esempi e file di prova

Gli embedding mantenuti nel repository sono in `ct/examples/planar/`. Sono
casi diagnostici e alcuni sono molto grandi o contengono centinaia di grafi:
non assumerli come smoke test rapidi senza prima controllare dimensione e
numero di righe. Per aggiungere un caso riproducibile:

1. salvare un embedding JSON completo su una singola riga, senza inserire
   righe vuote tra grafi diversi;
2. usare estensione `.planar` e un nome che descriva il comportamento;
3. verificare il file con almeno una strategia dalla CLI;
4. se il caso protegge una regressione, aggiungere anche un test pytest mirato.

Non modificare manualmente i file `debug.previous_run.*` per trasformarli in
fixture: copiarne esplicitamente il contenuto in `examples/planar/` e assegnare
un nome stabile.

## Debug, logging e output

`ct/logging.conf` configura il logger usato da `4ct.py`. Se il file non è nel
working directory, lo script prova a caricarlo dalla propria directory.

La pipeline usa `ct/debug/` per artefatti temporanei:

- `debug.previous_run.planar`: ultimo embedding convertito;
- `debug.previous_run.edgelist`: ultimo grafo generato o caricato;
- `debug.f_distribution.json.dump`: distribuzione delle facce a ogni passo;
- `error.txt` e grafi diagnostici per alcuni fallimenti.

Quasi tutti questi file sono ignorati da Git. Al termine di ogni esecuzione
diretta, `cProfile` stampa le 30 funzioni con maggiore tempo cumulativo; questo
output è normale.

Per visualizzare un file DOT:

```bash
uv run --python ../.venv/bin/python python \
  visualizers/visualize_dot.py path/to/graph.dot
```

## Workflow per modifiche algoritmiche

Gli invarianti e lo stile obbligatori sono definiti in
[AGENTS.md](../AGENTS.md); il comportamento delle strategie è definito in
[algorithm.md](algorithm.md).
Questa guida mantiene soltanto il workflow operativo:

1. aggiungere o aggiornare un test mirato al comportamento modificato;
2. eseguire il test specifico durante l'iterazione;
3. eseguire l'intera suite pytest;
4. eseguire almeno uno smoke test piccolo;
5. controllare `git diff --check` e `git status --short`;
6. non includere gli artefatti prodotti in `ct/debug/`.

Per il comportamento algoritmico si veda [algorithm.md](algorithm.md); per la
mappa dei moduli si veda [architecture.md](architecture.md).
