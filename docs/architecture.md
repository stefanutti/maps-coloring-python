# Architettura corrente

Questo documento fotografa l'organizzazione attuale del programma. I due file
principali, `ct/4ct.py` e `ct/ct_graph_utils.py`, restano intenzionalmente il
centro dell'implementazione: qui non viene proposto di dividerli o rinominarli.

## Struttura del repository

```text
maps-coloring-python/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── ct/
│   ├── 4ct.py
│   ├── ct_graph_utils.py
│   ├── logging.conf
│   ├── converters/
│   ├── debug/
│   ├── examples/planar/
│   ├── plantri/plantri55_modified/
│   ├── tests/
│   ├── visualizers/
│   └── web_euler_s_formula_at_work/
└── docs/
    ├── algorithm.md
    ├── architecture.md
    ├── development.md
    ├── notes.md
    └── superpowers/
```

`docs/notes.md` e `docs/superpowers/` conservano review, specifiche e piani
storici. I tre documenti principali descrivono invece il codice in uso.

## Flusso di esecuzione

L'entry point è `main()` in `ct/4ct.py`:

```text
argparse
   |
   +-- -r1 --> create_from_random1()
   +-- -r2 --> create_from_random2()
   +-- -e  --> create_from_edge_list()
   +-- -p  --> create_from_planar()
   |
   v
NetworkX MultiGraph + g_faces
   |
   v
init_f_distribution()
   |
   v
reduce_faces() -- strategia S1/S2/S3/S4 --> ariadne_s_thread
   |
   v
rebuild_faces() --> MultiGraph con archi colorati
   |
   +-- controllo dimensioni
   +-- is_well_colored()
   +-- export opzionale .edgelist/.dot
   +-- statistiche e profilo
```

Il programma mantiene due rappresentazioni con ruoli diversi:

- il `nx.MultiGraph` rappresenta il grafo di input e, nella fase finale, il
  grafo ricostruito e colorato;
- `g_faces` rappresenta l'embedding planare ed è la struttura mutata durante
  la riduzione.

La ricostruzione non inverte direttamente tutte le mutazioni di `g_faces`.
Parte da un nuovo multigrafo minimo e usa `ariadne_s_thread` per ricreare il
grafo originale.

## `ct/4ct.py`

`4ct.py` contiene l'orchestrazione e le scelte algoritmiche. Le responsabilità
attuali sono:

| Area | Elementi principali |
| --- | --- |
| CLI e ciclo di esecuzione | `main()` |
| Statistiche | `initialize_statistics()`, `print_stats()`, dizionario globale `stats` |
| Ricostruzione | `ariadne_case_f2()`, `ariadne_case_f3()`, `ariadne_case_f4()`, `ariadne_case_f5()` |
| Indici delle facce | `FaceIndex` e helper di aggiornamento |
| Selezione | le quattro funzioni `select_edge_to_remove_*()` |
| Località S4 | `update_wave_frontier()` e helper F5-F5/F5-F6 |
| Input | `create_from_random1()`, `create_from_random2()`, `create_from_edge_list()`, `create_from_planar()` |
| Conversione embedding | `from_graph_to_planar()` |
| Pipeline | `reduce_faces()`, `rebuild_faces()`, `init_f_distribution()` |

Il nome numerico del file non crea problemi quando è avviato come script, ma
non è importabile con un normale `import ct.4ct`. I test che devono chiamarne
le funzioni lo caricano esplicitamente tramite `importlib`.

### Stato condiviso

Il modulo usa due oggetti globali inizializzati nel blocco `__main__`:

- `logger`, configurato da `ct/logging.conf`;
- `stats`, ricreato per ogni esecuzione della pipeline.

Le funzioni algoritmiche aggiornano `stats` direttamente. La configurazione di
logging viene cercata prima nel working directory e poi accanto a `4ct.py`.

### `FaceIndex`

`FaceIndex` è un indice incrementale costruito all'inizio della riduzione.
Mantiene collegamenti per:

- identità della faccia;
- lunghezza della faccia;
- arco orientato;
- vertice contenuto nella faccia.

Quando le facce vengono unite o modificate, `reduce_faces()` rimuove e
reinserisce nell'indice gli oggetti interessati. La semantica per identità è
importante perché due facce diverse possono avere lo stesso valore come lista.

## `ct/ct_graph_utils.py`

`ct_graph_utils.py` raccoglie le primitive riutilizzate dall'algoritmo:

| Area | Responsabilità |
| --- | --- |
| Wrapper NetworkX | aggiunta, rimozione, ricerca e colorazione degli archi di un `MultiGraph` |
| Validazione | planarità, 3-regolarità, loop, controllo della colorazione |
| Embedding | estrazione delle facce, grafo duale, creazione del grafo da `g_faces` |
| Operazioni sulle facce | rotazione, rimozione di vertici, unione di due facce, ricerca di adiacenze |
| Kempe | individuazione di cicli/catene, scambio di colori, half-cycle switching |
| I/O | esportazione `.edgelist` e `.dot`, stampa diagnostica |

Il confine corrente è quindi pratico: `4ct.py` decide il flusso e la strategia,
mentre `ct_graph_utils.py` esegue operazioni elementari su grafi, facce e
colori.

## Formati dati

### `.planar`

È un formato JSON Lines: ogni riga contiene una `g_faces` completa.
JSON trasforma le tuple in liste; `create_from_planar()` le riconverte in tuple
dopo il caricamento.

Esempio ridotto:

```json
[[[0, 1], [1, 2], [2, 0]], [[0, 2], [2, 1], [1, 0]]]
```

Quando `-p` punta a un file con più righe, `main()` esegue una volta per ogni
riga contata. Nel comportamento corrente questo sostituisce il valore di
`--num_executions`. Il conteggio ignora le righe vuote, ma il lettore avanza
per numero di riga fisico: i file `.planar` devono quindi evitare righe vuote
intermedie.

### `.edgelist`

Viene letto e scritto tramite NetworkX come `MultiGraph`, con identificatori
dei vertici convertiti a interi in ingresso.

### `.dot`

L'export include l'attributo di colore degli archi. È destinato alla
visualizzazione e all'ispezione dei risultati.

## Moduli di supporto

| Percorso | Ruolo |
| --- | --- |
| `ct/converters/` | Generazione e conversione tra `.planar`, GML, `.edgelist` e `.dot`. |
| `ct/examples/planar/` | Embedding diagnostici e raccolte di grafi riproducibili. |
| `ct/tests/` | Test delle strategie, della wave frontier e dei wrapper. |
| `ct/visualizers/` | Visualizzazione separata dei file DOT. |
| `ct/web_euler_s_formula_at_work/` | Applicazione Flask-SocketIO indipendente dalla pipeline principale. |
| `ct/plantri/plantri55_modified/` | Sorgenti modificati di plantri, con documentazione e licenza proprie. |

I converter espongono CLI separate e non formano un'unica API. Dipendenze,
comandi e uso degli esempi sono documentati in
[development.md](development.md).

## Vincoli tecnici attuali

Questi punti descrivono il comportamento presente, senza implicare una
richiesta di rimodellare i file principali:

- `4ct.py` concentra CLI, stato, riduzione e ricostruzione;
- `logger` e `stats` sono stato globale del modulo;
- il working directory fa parte implicitamente della configurazione dei file
  di debug;
- alcuni errori algoritmici usano `exit(-1)`, quindi sono meno semplici da
  testare di eccezioni dedicate.

La descrizione del metodo è in [algorithm.md](algorithm.md). Le procedure per
eseguire, testare e modificare il progetto sono in
[development.md](development.md).
