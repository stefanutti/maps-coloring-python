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
reduce_faces() -- strategia S1/S2/S3/S4/S5 --> ariadne_s_thread
   |
   v
rebuild_faces() --> MultiGraph con archi colorati
   |
   +-- controllo dimensioni
   +-- is_well_colored()
   +-- export opzionale .edgelist/.dot/.colored.planar
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
| Selezione | le cinque funzioni `select_edge_to_remove_*()` e `positive_corners()` |
| Località S4 | `update_wave_frontier()` e helper F5-F5/F5-F6 |
| Input | `create_from_random1()`, `create_from_random2()`, `create_from_edge_list()`, `create_from_planar()` |
| Conversione embedding | `from_graph_to_planar()` |
| Pipeline | `reduce_faces()`, `rebuild_faces()`, `init_f_distribution()` |

S5 riutilizza il contratto di selezione e i record di Arianna. La CLI passa
`kempe_search_limit` a `rebuild_faces()` e al gestore F5: `None` mantiene il
comportamento storico; un intero positivo attiva la ricerca deterministica.
Le statistiche `SELECT-S5-*` distinguono le riduzioni e `S5-*` distinguono
estensioni dirette, ricerche, stati esaminati e scambi deterministici.

`KempeSearchExhausted` segnala solo l'esaurimento della ricerca di colorazione:
2.000 tentativi casuali F5 per S1–S4, budget o classe di Kempe esauriti per S5.
`main()` intercetta questa eccezione nella ricostruzione. Con
`--continue-on-error` e un file `.planar` con più mappe, registra il fallimento
e passa alla mappa successiva; il riepilogo finale mantiene un codice di
uscita non nullo se ci sono fallimenti. Le altre eccezioni e gli arresti
espliciti non vengono intercettati. I controlli finali di dimensioni e
colorazione interrompono il programma se falliscono.

Il nome numerico del file non crea problemi quando è avviato come script, ma
non è importabile con un normale `import ct.4ct`. I test che devono chiamarne
le funzioni lo caricano esplicitamente tramite `importlib`.

Con `-o` o `-o2`, `main()` conserva una copia delle liste di archi iniziali prima
della riduzione e la passa a `export_graph(..., planar_faces=original_faces)`.
Per `-p`, lo shuffle avviene dopo questa copia, così l'export mantiene l'ordine
del file sorgente. La copia contiene soltanto coppie di vertici e non viene
mutata dalla riduzione.

`-o2 FILE` riusa la stessa conversione dell'embedding colorato e aggiunge ogni
mappa riuscita come record JSON Lines al file `FILE`, aperto in append. A
differenza di `-o`, non genera file `.edgelist` o `.dot` e non rinomina il file
nelle elaborazioni multiple; il nome deve avere un'estensione.

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
| Ricerca S5 | `find_kempe_repair()` esplora colorazioni complete senza mutare il grafo e restituisce una sequenza di cicli con chiavi; `KempeSearchExhausted` distingue i fallimenti dalla colorazione riuscita. |
| I/O | esportazione `.edgelist` e `.dot`; con embedding originale fornito, `color_planar_representation()` associa i colori e `export_graph()` scrive anche `.colored.planar`; stampa diagnostica |

Il confine corrente è quindi pratico: `4ct.py` decide il flusso e la strategia,
mentre `ct_graph_utils.py` esegue operazioni elementari su grafi, facce e
colori.

## Formati dati

### `.planar`

È un formato JSON Lines: ogni riga contiene una `g_faces` completa.
Ogni arco può essere una coppia `[u, v]` oppure una tripla `[u, v, colore]`.
`create_from_planar()` verifica che ogni arco abbia due o tre elementi, poi
conserva soltanto i primi due come tupla. Il colore in ingresso viene ignorato
e non viene assegnato al grafo: la riduzione e la ricostruzione operano come
per un input senza colori.

Esempio ridotto:

```json
[[[0, 1], [1, 2], [2, 0]], [[0, 2], [2, 1], [1, 0]]]
```

Quando `-p` punta a un file con più righe, `main()` esegue una volta per ogni
riga contata. Questo sostituisce il valore di `--num_executions`.
Il conteggio e il lettore usano entrambi le righe fisiche, comprese quelle
vuote. `--skip N` (alias `-skip N`) fa partire il ciclo dalla riga N+1,
senza interpretare le precedenti. Ogni riga da elaborare deve contenere una
mappa valida. I numeri nei log e nei nomi dei file esportati restano quelli
originali; se rimane una sola esecuzione, l'output non ha suffisso numerico.
Il riepilogo e l'attivazione di `--continue-on-error` considerano solo le
esecuzioni rimanenti.

### `.colored.planar`

L'output aggiunto da `-o` è una singola riga JSON con la stessa struttura di
facce e archi dell'input, ma con triple `[u, v, colore]`, dove il colore è
`"red"`, `"green"` o `"blue"`. L'ordine originale viene preservato anche con
`--shuffle`; per input generati o edgelist viene usato l'embedding iniziale.
Il file può essere riletto tramite `-p`, che per ora ne ignora i colori.

Il formato a coppie non identifica gli archi paralleli tramite chiavi.
L'esportazione assegna i loro colori alle occorrenze orientate in modo
coerente: ogni colore compare una volta in ciascun verso e gli archi
consecutivi di una faccia hanno colori diversi. Essendo il grafo cubico e
senza loop, ci sono al massimo tre archi paralleli e sei permutazioni da
verificare. Incoerenze tra grafo colorato ed embedding interrompono l'export.

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
