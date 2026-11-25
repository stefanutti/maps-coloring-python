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
│   ├── experiments/
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
reduce_faces() -- strategia S1...S6 --> ariadne_s_thread
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
| Ricostruzione | `ariadne_case_f2()` ... `ariadne_case_f5()`, `ariadne_case_any_face()` (S6); `restore_ariadne_step()` (S1–S5) e `restore_ariadne_step_s6()` scelgono il gestore per ogni record |
| Indici delle facce | `FaceIndex` e helper di aggiornamento |
| Selezione | le sei funzioni `select_edge_to_remove_*()`, `positive_corners()` e gli helper di parità S6 |
| Località S4 | `update_wave_frontier()` e helper F5-F5/F5-F6 |
| Input | `create_from_random1()`, `create_from_random2()`, `create_from_edge_list()`, `create_from_planar()` |
| Conversione embedding | `from_graph_to_planar()` |
| Pipeline | `reduce_faces()`, `rebuild_faces()`, `init_f_distribution()` |

S5 riutilizza il contratto di selezione e i record di Arianna. La CLI passa
`kempe_search_limit` a `rebuild_faces()` e al gestore F5: `None` mantiene il
comportamento storico; un intero positivo attiva la ricerca deterministica.
Le statistiche `SELECT-S5-*` distinguono le riduzioni e `S5-*` distinguono
estensioni dirette, ricerche, stati esaminati e scambi deterministici.

Con `-s6`, `main()` passa a `reduce_faces()` e a `rebuild_faces()` la stessa
lista `perimeters`: la riduzione vi aggiunge una copia di ogni faccia unita,
la ricostruzione la consuma in ordine LIFO e chiama `measure_s6_reinsertion()`.
Con `-s6` passa anche `restore_step=restore_ariadne_step_s6` e
`kempe_search_limit`. Con le altre strategie `perimeters` vale `None`,
`restore_step` è il gestore classico e il comportamento non cambia.

`KempeSearchExhausted` segnala solo l'esaurimento della ricerca di colorazione:
2.000 tentativi casuali F5 per S1–S4, budget o classe di Kempe esauriti per S5, budget esaurito per S6
(una classe esaurita in S6 attiva invece la ricolorazione esatta).
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

La costruzione completa (`rebuild()`, usata anche dal costruttore) visita
`g_faces` nell'ordine corrente e aggiunge direttamente ogni faccia ai bucket.
Il costo è lineare nel numero di facce e di occorrenze dei loro bordi, con
le normali ipotesi sulle tabelle hash. Archi e vertici ripetuti nella stessa
faccia contribuiscono una sola volta al rispettivo bucket; facce distinte
uguali per valore restano distinte. Se lo stesso oggetto compare più volte
nella lista sorgente, mantiene l'ultima posizione e compare una sola volta
per bucket, come nel comportamento precedente.

Gli inserimenti incrementali (`index_face()`) conservano la ricerca ordinata
per posizione e identità, necessaria quando una faccia viene reinserita fra
quelle esistenti. `validate()` conserva la ricostruzione incrementale di
riferimento come controllo indipendente, più costoso; gli invarianti
dell'oracolo costruiscono invece il confronto tramite un nuovo `FaceIndex`.

## `ct/ct_graph_utils.py`

`ct_graph_utils.py` raccoglie le primitive riutilizzate dall'algoritmo:

| Area | Responsabilità |
| --- | --- |
| Wrapper NetworkX | aggiunta, rimozione, ricerca e colorazione degli archi di un `MultiGraph` |
| Validazione | planarità, 3-regolarità, loop, controllo della colorazione |
| Embedding | estrazione delle facce, grafo duale, creazione del grafo da `g_faces` |
| Operazioni sulle facce | rotazione, rimozione di vertici, unione di due facce, ricerca di adiacenze |
| Kempe | individuazione di cicli/catene, scambio di colori, half-cycle switching |
| Ricerca S5/S6 | `find_kempe_repair()` esplora colorazioni complete senza mutare il grafo e restituisce una sequenza di cicli con chiavi; `KempeSearchExhausted` distingue i fallimenti dalla colorazione riuscita, e la sottoclasse `KempeClassExhausted` indica che l'intera classe è stata esaminata. |
| Colorazione esatta | `find_three_edge_coloring()` trova per ricerca esaustiva e deterministica una 3-colorazione degli archi, provando prima i colori correnti; pensata per grafi piccoli (S6, classe di Kempe esaurita). |
| I/O | esportazione `.edgelist` e `.dot`; con embedding originale fornito, `color_planar_representation()` associa i colori e `export_graph()` scrive anche `.colored.planar`; stampa diagnostica |

Il confine corrente è quindi pratico: `4ct.py` decide il flusso e la strategia,
mentre `ct_graph_utils.py` esegue operazioni elementari su grafi, facce e
colori.

## Prototipo sperimentale dell'oracolo

`ct/experiments/oracle_reduction.py` è separato dalla pipeline principale.
Implementa stato, scoperta del testimone per una candidata esplicita,
applicazione/inversione dei certificati e catene deterministiche con replay
esatto. `ct/experiments/oracle_reduction_run.py` offre persistenza e CLI
separate da `4ct.py`. Il [piano dello studio](superpowers/plans/2026-09-28-oracle-reduction-study.md)
distingue i controlli sulle piccole mappe dalle future esecuzioni grandi.

`make_state(colored_faces)` copia un embedding interamente colorato, assunto
valido. Controlla forma dei record e ambiguità delle occorrenze, senza lanciare
una nuova verifica del dataset. `OracleState` contiene:

- `graph`, un `MultiGraph` colorato, e `g_faces`, fonte strutturale;
- ID globali degli archi usati anche come chiavi NetworkX esplicite,
  con lookup `edge_endpoints`; lo scambio di colori non cambia questi ID;
- `face_ids` allineati a `g_faces` e `face_edge_ids`, che associa ogni slot
  orientato di ogni faccia al suo arco esatto, anche in presenza di paralleli;
- contatori `next_edge_id` / `next_face_id` e un `FaceIndex` sincronizzato.

Gli ID iniziali seguono il primo incontro nell'input. Estremi e colore
permettono l'abbinamento iniziale delle due occorrenze, ma il colore non è
più l'identità dell'arco nello stato. Le tre facce di theta rimangono distinte
anche quando le liste di coppie di vertici hanno lo stesso valore.

`StepWitness` conserva la candidata, il record Arianna, le sole patch prima/
dopo di archi e facce (con posizioni), gli scambi ordinati `ColorSwap`, i
contatori e due impronte SHA-256. Ogni scambio specifica colori, tipo
`cycle` o `path` e triple orientate `(u, v, edge_id)`. Le impronte riguardano
lo stato semantico completo, inclusi colori lontani dalla candidata, ordine
delle facce e ID; non includono gli indirizzi Python o gli indici derivati.

`apply_step()` e `undo_step()` rifiutano precondizioni obsolete e verificano
su uno stato temporaneo patch, record Arianna, cammini/cicli alternati,
fusioni, variazioni V/E/F e invarianti. Solo dopo installano il risultato:
un rifiuto non lascia mutazioni parziali. Un successo sostituisce gli oggetti
grafo/liste/indice; il chiamante deve recuperarli nuovamente dallo stato.
Il ritorno esatto conserva ID, colori, occorrenze, ordine e contatori, non
l'identità degli oggetti Python.

`assert_state_invariants()` controlla connessione, cubicità e colorazione,
assenza di loop/ponti, ID e lookup, due occorrenze orientate per arco,
chiusura delle facce, rotazioni cubiche ed Eulero per l'embedding sferico,
oltre alla corrispondenza di tutti gli indici di `FaceIndex`.
Nel checker completo la lista degli archi keyed genera un solo dict locale,
indipendente dal lookup dello stato e riutilizzato nei due assert, con ordine
e messaggi invariati. Lista e dict vengono rilasciati dopo l'ultimo uso;
non sono conservati tra chiamate. L'effetto su tempo e RSS non è misurato.
Il risultato positivo può essere riutilizzato su uno stato invariato.
`OracleState` conserva una sola istantanea privata `_validated_snapshot`,
esclusa dall'uguaglianza del dataclass, dal fingerprint e dai file salvati.
Prima di ogni riuso viene ricostruita e confrontata esattamente l'istantanea
dei dati controllati:

- tipo di grafo (diretto/multigrafo), vertici e archi keyed con colori;
- facce, ID, interi lookup delle occorrenze e degli estremi, contatori;
- identità delle facce, collegamento `face_index.g_faces is g_faces`,
  posizioni e contenuto ordinato di tutti i bucket dell'indice.

La codifica privata `marshal` versione 2 conserva i tipi primitivi usati
dal modello (`int`, `float`, stringhe, tuple e liste), senza riferimenti condivisi nella
codifica. I 14 componenti del payload vengono serializzati uno alla volta
e inviati, nello stesso ordine, a un unico `zlib.compressobj(1)`, con un solo
`flush()` finale. Il flusso decompresso contiene 14 valori `marshal`
autodelimitanti, senza il precedente involucro di tupla; conserva tutti i
dati e i tipi. Le porzioni compresse vengono unite prima del confronto:
l'evidenza completa non è sostituita da un digest.
La compressione deterministica nello stesso processo permette il confronto
esatto dei byte compressi; il motore non li decomprime, deserializza o persiste.
L'identità da sola e il fingerprint semantico dei certificati non bastano:
lo stato è modificabile dal chiamante e il fingerprint non copre gli indici.
Le rappresentazioni non serializzabili ricadono nel controllo completo.
Il confronto costa O(V+E) e conserva O(V+E) byte per stato vivo; non accumula
una cronologia delle verifiche. Un diverso ordine dei dizionari può causare
una verifica aggiuntiva, mai un successo per dati diversi.
Resta temporaneamente un buffer `marshal` per componente, senza quello
dell'intero stato. Il payload Python e le porzioni compresse esistono ancora
durante la codifica; non è una strategia a memoria costante. La costruzione
per componenti riduce il picco complessivo nelle misure locali del prefisso,
con un costo di memoria maggiore nella sola andata rispetto alla compressione
monolitica. Non introduce raccolte forzate né una garanzia sul comportamento
dell'allocatore per catene lunghe.

Una differenza invalida l'evidenza prima di eseguire il checker completo;
un errore non viene memorizzato come successo. Gli stati nuovi partono senza
evidenza. `_install()` trasferisce l'evidenza del risultato temporaneo già
verificato insieme ai suoi stessi oggetti; ogni successiva mutazione viene
comunque ricontrollata. Copie e caricamenti non possono riutilizzare le
identità delle facce dello stato originale. Per una verifica di riferimento
senza riuso, chiamare `assert_state_invariants(state, force=True)`; il corpo
di `_assert_state_invariants_full()` è il checker completo preesistente.
Il contratto resta sincrono: lo stato non deve essere modificato da un altro
thread durante una verifica o una trasformazione.

Il controllo dei ponti, condiviso con il filtro strutturale di `plan_step()`,
usa `_has_bridge()`: visita DFS iterativa con valori low-link direttamente
sul `MultiGraph`, senza copiarlo né modificarlo. Un secondo arco verso il
padre conta come arco di ritorno, quindi una coppia di archi paralleli non
viene scambiata per un ponte. Il costo è O(V+E), la memoria ausiliaria O(V);
il controllo termina al primo ponte trovato. Restano attivi tutti gli
altri controlli globali (o il loro riuso verificato) e le copie temporanee
richieste dall'atomicità.

`plan_step(state, Candidate(face_id, edge_id))` è read-only e mantiene la
candidata indicata. Verifica prima lo stato sorgente e l'ammissibilità della
soppressione strutturale (loop, connessione, ponti); poi cerca lo scambio:

- F2: elimina il digono e fonde i due archi esterni, senza scambi; theta è
  terminale e restituisce `unsupported_case`.
- F3–F5: segue il ciclo dei due colori complementari, partendo dal lato
  precedente della faccia verso l'altro estremo della candidata. Gli archi
  percorsi sono identificati dalle chiavi, anche quando sono paralleli.
- F4 a due colori: se il testimone diretto manca, può scambiare il ciclo
  del colore selezionato e del colore assente dal bordo, soltanto se non
  contiene il lato opposto. Registra questo ciclo prima del cammino parziale.
  Non cambia lato di nascosto e non cerca altre colorazioni.
- F5: usa soltanto il criterio diretto; se manca, restituisce `no_witness`.

La chirurgia delle facce usa `join_faces()` e `remove_vertex_from_face()`;
i metadati seguono gli slot orientati delle fusioni, senza ricostruire gli ID
dai soli estremi. Le facce sopravvissute mantengono ID e ordine relativo;
la faccia unita riceve un nuovo ID ed è aggiunta in fondo. Il certificato
contiene solo gli archi cambiati e le facce con occorrenze cambiate, oltre
agli scambi. Il risultato temporaneo passa i controlli di invarianti e
descrizione del passo prima della restituzione di `certified`.

`StepAttempt` distingue `certified`, `structurally_rejected`, `no_witness` e
`unsupported_case`; nessuno degli ultimi tre significa impossibilità
matematica. Una violazione degli invarianti solleva un errore, senza essere
convertita in un esito negativo della ricerca. I test comprendono sia i
certificati manuali precedenti, sia le trasformazioni scoperte automaticamente,
con risultati attesi indipendenti e ritorno completo di ID/colori/occorrenze.
La copertura dei casi piccoli non garantisce ogni stato intermedio possibile.

`ordered_candidates()` ordina F2, F3, F4, F5, poi ID della faccia e dell'arco;
all'interno di ciascuna F5 anticipa il lato del colore unico. Questa preferenza
usa esplicitamente l'oracolo. `run_chain(state, max_steps)` prova le altre
candidate dopo un rifiuto, senza backtracking, e muta lo stato solo tramite
`apply_step()`. `ChainResult` contiene certificati ordinati, impronta e conteggi
iniziali, contatori F2–F5 e scambi `cycle`/`path`, oltre ai motivi delle
candidate rifiutate nello stato finale se nessuna è certificabile.
Gli esiti sono `theta_reached`, `step_limit`, `no_certified_candidate`;
theta viene riconosciuto anche quando coincide con l'ultimo passo disponibile.
Gli ultimi due esiti sono non conclusivi. Gli errori software restano fatali.

`replay_exact()` ricrea uno stato indipendente e inverte i certificati in
ordine LIFO, conservando i colori terminali effettivi. Non usare `deepcopy`
per copiare `OracleState`: le chiavi derivate di `FaceIndex` contengono indirizzi
Python e vanno ricostruite sulle nuove liste.

Il runner salva lo schema 1 in `terminal.json`, `steps.jsonl` e
`manifest.json`, scritto per ultimo. Il manifest conserva stato d'arresto,
conteggi, rifiuti, SHA-256 dei due file, provenienza della riga selezionata
(percorso assoluto, numero fisico a base 1, SHA-256 dei byte inclusa l'eventuale
newline), configurazione, revisione Git e impronte dei quattro file di codice
coinvolti anche se non committati. Salva inoltre versioni Python/NetworkX,
tempo della catena ed esiti del replay e del confronto ordinario.
Una directory già popolata è rifiutata. `load_run()` verifica schema,
integrità, conteggi e continuità delle impronte e ricostruisce gli indici;
`replay_exact()` verifica semanticamente i singoli certificati. Un salvataggio
incompleto non equivale a una catena completa. Gli hash controllano integrità,
non autenticità contro la riscrittura intenzionale di file e manifest.

`--ordinary-rebuild` chiama `rebuild_faces()` soltanto dopo theta, con copie
delle facce strutturali e dei soli record Arianna e budget Kempe positivo.
Confronta vertici e multinsieme degli archi etichettati, verifica colorazione
e stack consumato; non richiede uguaglianza dei colori. Registra `success`,
`search_exhausted` con motivo, oppure `not_run_nonterminal`. Un errore inatteso
resta fatale e la CLI salva prima il ramo certificato con diagnostica
`software_error`. Il ricostruttore non riceve colori o scambi dell'oracolo.

Le copie temporanee e i controlli globali per passo sono una scelta iniziale
di atomicità: occorre misurarne il costo prima delle esecuzioni lunghe.
I certificati non trattengono snapshot completi per livello; i file JSON
sono costruiti in memoria e il costo sulle mappe grandi resta da misurare.

## Formati dati

### `.planar`

È un formato JSON Lines: ogni riga contiene una `g_faces` completa.
Ogni arco può essere una coppia `[u, v]` oppure una tripla `[u, v, colore]`.
`create_from_planar()` verifica che ogni arco abbia due o tre elementi.
Restituisce sempre `(the_graph, g_faces)`: gli archi del grafo restano senza
colore e `g_faces` conserva soltanto le coppie di vertici come tuple.

Se almeno un arco contiene un terzo elemento, `the_graph.graph["oracle_faces"]`
conserva tutti i record originali come tuple annidate (facce, archi, valori),
prima di qualunque shuffle. Per input senza colori vale `None`. Questa copia
mantiene ordine, orientamento e occorrenze degli archi paralleli, senza
condividerne le liste con `g_faces`. Negli input misti conserva le coppie prive
di colore senza completarle: la presenza del dato non certifica una
colorazione completa o valida. I colori vengono conservati senza aggiungere
controlli di correttezza cromatica.

L'oracolo fotografa solo la mappa iniziale: non viene aggiornato durante la
riduzione né consultato dalle strategie o dalla ricostruzione. Non viene
copiato sul grafo ricostruito. Ogni riga caricata ha la propria copia; non è
stato aggiunto alcuno stato globale.

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
Il file può essere riletto tramite `-p`, che conserva i colori nell'oracolo
di input; l'algoritmo continua a calcolare autonomamente la nuova colorazione.

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
