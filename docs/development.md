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

Le strategie si selezionano con `-s1`, `-s2`, `-s3`, `-s4` o `-s5`. S1 è il default:

```bash
uv run --python ../.venv/bin/python python 4ct.py \
  -s4 -r2 100
```

Opzioni utili:

| Opzione | Effetto |
| --- | --- |
| `-o NAME` | Esporta `NAME.edgelist`, `NAME.orig.dot`, `NAME.dot` e `NAME.colored.planar`; con più esecuzioni aggiunge `.N` al prefisso, a partire da 1. |
| `-o2 FILE` | Aggiunge la rappresentazione planare colorata di ogni mappa riuscita come nuova riga JSON in `FILE`; il nome deve includere un'estensione. |
| `-c 2345` | Imposta la priorità delle facce per S1/S2/S3. |
| `-s` | Mescola inizialmente la lista delle facce. |
| `-n N` | Ripete N volte gli input casuali o edgelist. |
| `--skip N` / `-skip N` | Salta le prime N righe fisiche del file `.planar` (default 0). |
| `-s1` ... `-s5` | Sceglie la strategia di selezione. |
| `--kempe-search-limit N` | Limita a N colorazioni distinte ciascuna ricerca F5 di S5 (default 10000). |
| `--continue-on-error` | Nei file `.planar` con più mappe, passa alla successiva se la ricerca Kempe fallisce; gli errori inattesi restano fatali. |

Con `-o test` e una sola esecuzione vengono salvati `test.edgelist`,
`test.orig.dot`, `test.dot` e `test.colored.planar`. Con più mappe nel `.planar` o più ripetizioni
con `-n`, la prima esecuzione usa il prefisso `test.1`, la seconda `test.2`,
e così via. Le mappe saltate
con `--continue-on-error` non vengono esportate e lasciano un buco nella
numerazione. Un nuovo avvio con lo stesso prefisso e senza `--skip` riparte da 1 e può
sovrascrivere i file corrispondenti di un avvio precedente.

Il file `.colored.planar` contiene una sola riga JSON con le facce originali
e gli archi nella forma `[u, v, "red"]`, `[u, v, "green"]` o
`[u, v, "blue"]`. Con input `-p` conserva ordine delle facce, ordine e verso
degli archi e identificativi dei vertici del file sorgente, anche usando `-s`.
Per gli altri input conserva l'embedding iniziale prima della riduzione.
I colori sono quelli calcolati durante la ricostruzione, coerenti con gli
altri file esportati. Anche gli archi paralleli ricevono colori distinti.

`-o2` usa la stessa rappresentazione, ma non crea nomi derivati né sovrascrive
il file: apre il nome indicato in append e aggiunge una riga per ogni elaborazione
riuscita. Questo permette di raccogliere molte mappe in un solo file JSON Lines,
anche eseguendo il programma più volte. Le mappe che falliscono con
`--continue-on-error` non vengono scritte.

Il caricamento con `-p` accetta sia coppie `[u, v]` sia triple `[u, v, colore]`,
anche mescolate. Per ora ignora completamente il terzo valore: il grafo viene
ricolorato con l'algoritmo normale. È quindi possibile rileggere direttamente
un file `.colored.planar` senza attivare alcun uso dei colori come oracolo.

S5 usa i sette tipi a curvatura positiva di v17 e ricostruisce senza scambi
casuali. Per esempio:

```bash
uv run --python ../.venv/bin/python python 4ct.py \
  -s5 -p examples/planar/waterworld-1.planar
```

Le statistiche distinguono gli F5 risolti direttamente (`S5-F5-DIRECT`),
quelli che richiedono ricerca (`S5-F5-SEARCHED`), gli stati esaminati e gli
scambi deterministici. `TOTAL_RANDOM_KEMPE_SWITCHES` deve essere zero.
Una ricerca fallita termina con codice diverso da zero e distingue il
limite raggiunto dall'esaurimento della classe di Kempe. Aumentare il limite
non può risolvere una classe completamente esaurita. Per le garanzie e i
limiti matematici vedere [algorithm.md](algorithm.md).

Un file `.planar` può contenere più grafi, uno per riga. In questo caso il
programma esegue tutte le righe e il valore di `-n` viene ignorato.
Ogni riga elaborata deve contenere una mappa JSON valida; le righe vuote
non sono ammesse nella parte da elaborare.

Per riprendere dalla quarta riga, saltando le prime tre:

```bash
uv run --python ../.venv/bin/python python 4ct.py \
  -p examples/planar/maps_3000_maps_of_8000_faces.planar \
  -s -s5 --skip 3 --continue-on-error -o test
```

`--skip` accetta un intero non negativo e, se maggiore di zero, richiede `-p`.
Conta le righe fisiche, comprese quelle vuote: le righe saltate non vengono
interpretate. Log e output mantengono i numeri originali, quindi nell'esempio
gli output iniziano da `test.4.edgelist`, `test.4.orig.dot`, `test.4.dot`
e `test.4.colored.planar`.
Se resta una sola mappa da elaborare, gli output non hanno suffisso numerico.
Se `N` raggiunge o supera il numero di righe, il programma segnala che non
restano mappe e termina con successo, senza esportare file. Il riepilogo
conta solo le mappe elaborate, escludendo quelle saltate con `--skip`.

Per elaborare una raccolta anche quando alcune mappe non vengono colorate:

```bash
uv run --python ../.venv/bin/python python 4ct.py \
  -p examples/planar/maps_3000_maps_of_8000_faces.planar \
  -s -s5 --continue-on-error
```

Il parametro vale per tutte le strategie: intercetta il raggiungimento dei
2.000 tentativi casuali F5 di S1–S4 e l'esaurimento del budget o della classe
di Kempe in S5. Registra il numero della mappa (a partire da 1) e il motivo,
poi riparte con grafo e statistiche nuovi per la mappa successiva. Alla fine
stampa il numero di mappe riuscite e fallite e gli indici delle fallite;
il codice di uscita è 1 se almeno una mappa è fallita, 0 altrimenti.
Il fallimento della ricerca non dimostra che la mappa sia non colorabile.

Senza il parametro, il primo fallimento interrompe l'esecuzione. Il parametro
non ha effetto con una sola mappa o con input diversi da `-p`, anche usando
`-n`. Errori inattesi, violazioni degli invarianti, input non valido e Ctrl+C
interrompono comunque il programma. Anche dimensioni errate del grafo
ricostruito o una colorazione finale non valida sono errori fatali.

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

## Verifica S5 sulle mappe Waterworld

Da `ct/`:

```bash
uv run --python ../.venv/bin/python python tests/benchmark_selection5.py
```

Il benchmark trova tutti i file `examples/planar/waterworld-*.planar` ed
esegue ogni riga non vuota. Impedisce le chiamate casuali nella selezione e
nella ricostruzione e verifica la colorazione, la cubicità, l'esaurimento
della pila e l'uguaglianza esatta dei vertici e del multinsieme degli archi
etichettati con l'input. Stampa risultati JSON Lines, inclusi tempi e contatori.
Per un singolo file usare `--pattern 'waterworld-1.planar'`.

I risultati del campione verificato sono riportati in
[s5-waterworld.md](s5-waterworld.md). I test ordinari includono fixture piccole
per classificazione, selezione, ricerca, limiti, archi paralleli e CLI; il
benchmark completo rimane separato perché usa mappe con migliaia di vertici.

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
