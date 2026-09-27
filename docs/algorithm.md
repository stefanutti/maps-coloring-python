# Algoritmo

Questo documento descrive l'algoritmo implementato oggi in `ct/4ct.py` e nelle
primitive di `ct/ct_graph_utils.py`. Non è una proposta di refactoring e non
descrive varianti storiche conservate nelle note di progetto.

## Obiettivo e modello matematico

Il programma lavora su un grafo planare cubico, cioè 3-regolare, privo di
loop. Sono ammessi archi multipli durante la riduzione e la ricostruzione.

L'idea usa l'equivalenza di Tait: per un grafo planare cubico, una colorazione
propria degli archi con tre colori corrisponde a una colorazione delle regioni
con quattro colori nel problema duale. Il programma costruisce quindi una
3-colorazione degli archi con i colori `red`, `green` e `blue`; al termine
controlla direttamente che i tre archi incidenti a ogni vertice abbiano colori
distinti.

Questa implementazione è un algoritmo sperimentale che riduce il grafo e poi
lo ricostruisce. La validità dell'output prodotto viene verificata dal codice;
questo documento non presenta il software come una dimostrazione formale del
teorema dei quattro colori.

## Rappresentazione planare: `g_faces`

La struttura centrale è `g_faces`, una lista di facce. Ogni faccia è una lista
ciclica di archi orientati, ordinati lungo il suo bordo:

```python
g_faces = [
    [(0, 1), (1, 2), (2, 0)],
    [(0, 2), (2, 4), (4, 3), (3, 0)],
]
```

Se `(u, v)` appartiene a una faccia, l'arco ruotato `(v, u)` appartiene alla
faccia adiacente. Questa coppia di orientamenti permette di trovare
l'adiacenza tra facce senza mantenere un grafo duale separato.

Le proprietà della rappresentazione sono:

- ogni faccia è un ciclo coerente di archi orientati;
- ogni arco compare due volte nell'embedding, una per verso.

Le precondizioni e gli invarianti obbligatori per le modifiche al codice sono
raccolti in [AGENTS.md](../AGENTS.md).

Nel codice una faccia di lunghezza `n` viene chiamata `Fn`: per esempio `F2`,
`F3`, `F4` e `F5`.

## Flusso generale

```text
input o generazione
        |
        v
grafo NetworkX + g_faces
        |
        v
riduzione fino a 3 facce  --->  pila di Arianna
        |                           |
        v                           |
multigrafo base a 2 vertici        |
        |                           |
        +<--- ricostruzione LIFO ---+
        |
        v
3-colorazione e controlli finali
```

Il processo ha cinque passaggi:

1. genera o carica un grafo;
2. valida planarità, 3-regolarità e assenza di loop;
3. riduce l'embedding fino al multigrafo minimo con due vertici e tre archi;
4. ricostruisce il grafo reinserendo le configurazioni in ordine inverso;
5. verifica dimensioni e colorazione del grafo ricostruito.

## Riduzione

`reduce_faces()` ripete una trasformazione locale finché rimangono tre facce.
Per ogni iterazione:

1. una strategia seleziona una faccia `f1`, un arco `(v1, v2)` e la faccia
   adiacente `f2`;
2. `join_faces()` calcola la faccia ottenuta eliminando il bordo comune;
3. la candidata viene normalmente accettata solo se non crea una connessione
   a un solo arco; S4 tratta invece gli archi di una F2 come sempre validi e
   non ripete questo controllo per quel caso;
4. `f1` e `f2` vengono sostituite dalla faccia unita;
5. `v1` e `v2` vengono rimossi dalle altre facce coinvolte, simulando la
   soppressione locale dei due vertici;
6. le informazioni necessarie a invertire l'operazione vengono aggiunte alla
   pila `ariadne_s_thread`.

Durante la riduzione `FaceIndex` accelera la ricerca di facce e adiacenze. La
sua struttura e il suo aggiornamento sono descritti in
[architecture.md](architecture.md).

### Contratto delle strategie

Tutte le strategie restituiscono la stessa tupla:

```python
(edge, f1, f2, f1_plus_f2, event)
```

`event` vale normalmente `None`. In S4/S5 può valere `"fallback"`, segnalando a
`reduce_faces()` che una ricerca globale ha interrotto la wave locale.

### Strategie di selezione

| Opzione | Funzione | Comportamento corrente |
| --- | --- | --- |
| `-s1` | `select_edge_to_remove_first_fit` | Prima candidata valida nella prima classe di facce indicata da `--choices`. È il default. |
| `-s2` | `select_edge_to_remove_by_largest_neighbor` | Per ogni classe prioritaria preferisce la candidata la cui faccia adiacente è più grande. |
| `-s3` | `select_edge_to_remove_f5_shared_vertex` | Usa il first-fit per F2/F3/F4; sulle F5 preferisce configurazioni con una F5/F6 adiacente che condivide esattamente un vertice. |
| `-s4` | `select_edge_to_remove_unavoidable_set` | Gestisce prima F2/F3/F4, poi coppie F5-F5 e F5-F6, privilegiando una regione locale attiva. |
| `-s5` | `select_edge_to_remove_positive_corner` | Usa i sette tipi di vertice a curvatura positiva di v17, con località e scelte deterministiche; ricostruisce senza scambi casuali. |

Per S1, S2 e S3, `--choices` stabilisce la priorità tra F3, F4 e F5, con F2
sempre per prima. Sono accettate le permutazioni `2345`, `2354`, `2435`,
`2453`, `2534` e `2543`.

S4 usa invece la sequenza fissa `2345`; un valore diverso viene ignorato con
un warning. Il comportamento corrente di S4 è:

1. una F2 sceglie casualmente uno dei suoi archi;
2. una F3 o F4 sceglie una candidata valida con faccia adiacente più grande;
3. quando non esistono facce più piccole, cerca localmente una F5-F5;
4. se non la trova, cerca localmente una F5-F6;
5. se la regione locale è esaurita, ripete le due ricerche globalmente e
   restituisce l'evento `fallback` quando una wave era attiva.

La regione locale è rappresentata da un insieme di vertici modificati di
recente. `update_wave_frontier()` la avvia o la estende dopo una riduzione F5;
le riduzioni F2/F3/F4 la estendono solo se era già attiva. Dopo un fallback
globale, il comportamento corrente di `reduce_faces()` azzera la frontier.

### S5: configurazioni inevitabili e verifica della ricostruzione

Il punto di partenza è la sezione 6 di
[v17](llm-vs-4ct/4ct-v17.md). Se tutte le facce hanno almeno cinque lati,
la carica di un vertice incidente a facce di taglia `a,b,c` è
`6/a + 6/b + 6/c - 3`. La somma delle cariche è 12. Pertanto esiste almeno
un vertice positivo, con uno dei sette tipi:

```text
(5,5,5), (5,5,6), (5,5,7), (5,5,8), (5,5,9), (5,6,6), (5,6,7)
```

Questa è una garanzia di **inevitabilità**, non di riducibilità cromatica.
V17 lascia aperta l'estensione R₅ (§10.3) e non garantisce che una qualunque
colorazione dell'intermedio sia riparabile nella propria classe di Kempe.
S5 usa quindi questi tipi per guidare la scelta, senza interpretarli come
configurazioni la cui ricostruzione sia già dimostrata. Non implementa il
catalogo delle 633 configurazioni riducibili della dimostrazione RSST, né
il pilotaggio completo di tre facce di v17.

La selezione ha priorità fissa `2345`:

1. Per F2/F3/F4 ordina le candidate per taglia decrescente della faccia
   adiacente e accetta la prima che non crea ponti. Anche F2 è deterministica.
2. Per F5 privilegia le facce contenenti un vertice di uno dei sette tipi.
   Dentro questa classe privilegia la wave locale.
3. Ordina gli archi per numero di pentagoni laterali che diventano F4,
   poi per taglia decrescente della faccia adiacente, poi per carica
   decrescente del miglior vertice positivo della faccia. I pareggi seguono
   l'ordine delle facce e degli archi nell'input.
4. Se le candidate positive non ammettono una riduzione valida, prova le
   altre F5. Ogni candidata accettata passa il controllo dei ponti.

Le informazioni provengono dal `FaceIndex` corrente. S5 non modifica né
l'embedding né la frontier durante la selezione. Come S4, emette `fallback`
quando una scelta F5 globale interrompe una wave attiva; `reduce_faces()`
rimane responsabile dell'aggiornamento degli indici e della frontier.

Durante la ricostruzione, F2/F3/F4 e gli F5 che soddisfano subito il criterio
di mezzo ciclo seguono le operazioni esistenti. Quando un F5 si blocca,
`find_kempe_repair()` cerca deterministicamente una colorazione in cui i due
archi da suddividere appartengano allo stesso ciclo di una coppia ammissibile
(CONDITION-1, v17 §8.2). Alterna gruppi di al massimo otto espansioni sui
cicli che toccano gli archi da suddividere con espansioni sui cicli remoti,
ordinati per distanza topologica dagli archi da suddividere e poi per
lunghezza decrescente. Le nuove colorazioni prodotte dai cicli remoti hanno
priorità, per evitare che un'orbita locale molto grande le escluda dal
budget. Queste priorità sono euristiche; non minimizzano il numero di scambi.
Il risultato contiene i cicli completi da scambiare, i colori
degli archi da suddividere e la coppia per il mezzo scambio finale.

Lo stato visitato contiene la colorazione **completa**, con chiavi distinte
per gli archi paralleli. Conservare soltanto la parola sul bordo non sarebbe
corretto: uno scambio remoto può cambiare le connessioni senza cambiarla
(v17 §§9.14–9.18). La ricerca non modifica il grafo; applica gli scambi solo
dopo aver trovato una sequenza valida.

`--kempe-search-limit` limita il numero di colorazioni distinte memorizzate
per ciascun F5 (default 10000). Una classe esaurita o un limite raggiunto
producono un errore esplicito e nessun ripiego casuale. La ricerca può essere
esponenziale; un fallimento non dimostra che il grafo non sia colorabile.
Questa politica assicura l'assenza di scambi casuali nelle esecuzioni S5,
non il successo universale della selezione o della ricerca limitata.

## Il filo di Arianna

Ogni riduzione memorizza soltanto il contesto locale necessario per tornare
indietro. I record hanno due forme:

```text
F2:       [2, v1, v2, near_v1, near_v2]
F3/F4/F5: [n, v1, v2, on_v1, on_v2, off_v1, off_v2]
```

La prima posizione identifica il caso di ricostruzione. I record sono
consumati in ordine LIFO: l'ultima configurazione rimossa è la prima a essere
reinserita.

## Ricostruzione e colorazione

`rebuild_faces()` parte dal caso base: due vertici collegati da tre archi
paralleli, colorati rispettivamente `red`, `green` e `blue`.

Per ogni record della pila chiama uno dei quattro gestori:

- `ariadne_case_f2()` reinserisce il caso dell'arco multiplo;
- `ariadne_case_f3()` ricostruisce la configurazione triangolare;
- `ariadne_case_f4()` ricostruisce il quadrilatero e applica gli scambi di
  colore necessari;
- `ariadne_case_f5()` prova le configurazioni di colore disponibili e, quando
  necessario, usa catene di Kempe e half-cycle switching.

Una catena di Kempe considera una componente alternata formata da due colori.
Scambiare quei due colori lungo la catena conserva la colorazione propria e
può liberare la combinazione richiesta per reinserire un arco. Le primitive
principali sono `kempe_chain_color_swap()`, `is_a_kempe_cycle()` e
`apply_half_kempe_loop_color_switching()` in `ct_graph_utils.py`.

Il caso F5 delle strategie S1–S4 contiene scelte casuali tra tentativi
equivalenti. Di conseguenza, esecuzioni ripetute sullo stesso input non sono
necessariamente identiche. S5 usa invece la ricerca deterministica descritta
sopra. I generatori casuali e l'opzione esplicita `--shuffle` rimangono casuali.

## Controlli finali

Al termine il programma controlla:

- che il grafo ricostruito abbia lo stesso numero di vertici e archi
  dell'originale;
- che `is_well_colored()` confermi una 3-colorazione propria degli archi.

Il controllo topologico completo con `nx.is_isomorphic()` è presente nel
codice ma attualmente commentato per ragioni prestazionali. L'uguaglianza di
numero di vertici e archi è quindi un controllo meno forte dell'isomorfismo.

Questo documento descrive il comportamento corrente di S4 e S5. Specifiche e note
storiche possono riportare priorità differenti e non sono la fonte canonica
per l'algoritmo in uso.

Per la collocazione delle funzioni e dei moduli si veda
[architecture.md](architecture.md); per esecuzione e test si veda
[development.md](development.md).
