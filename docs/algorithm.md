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

`event` vale normalmente `None`. In S4 può valere `"fallback"`, segnalando a
`reduce_faces()` che una ricerca globale ha interrotto la wave locale.

### Strategie di selezione

| Opzione | Funzione | Comportamento corrente |
| --- | --- | --- |
| `-s1` | `select_edge_to_remove_first_fit` | Prima candidata valida nella prima classe di facce indicata da `--choices`. È il default. |
| `-s2` | `select_edge_to_remove_by_largest_neighbor` | Per ogni classe prioritaria preferisce la candidata la cui faccia adiacente è più grande. |
| `-s3` | `select_edge_to_remove_f5_shared_vertex` | Usa il first-fit per F2/F3/F4; sulle F5 preferisce configurazioni con una F5/F6 adiacente che condivide esattamente un vertice. |
| `-s4` | `select_edge_to_remove_unavoidable_set` | Gestisce prima F2/F3/F4, poi coppie F5-F5 e F5-F6, privilegiando una regione locale attiva. |

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

Il caso F5 contiene scelte casuali tra tentativi equivalenti. Di conseguenza,
esecuzioni ripetute sullo stesso input non sono necessariamente identiche.

## Controlli finali

Al termine il programma controlla:

- che il grafo ricostruito abbia lo stesso numero di vertici e archi
  dell'originale;
- che `is_well_colored()` confermi una 3-colorazione propria degli archi.

Il controllo topologico completo con `nx.is_isomorphic()` è presente nel
codice ma attualmente commentato per ragioni prestazionali. L'uguaglianza di
numero di vertici e archi è quindi un controllo meno forte dell'isomorfismo.

Questo documento descrive il comportamento corrente di S4. Specifiche e note
storiche possono riportare priorità differenti e non sono la fonte canonica
per l'algoritmo in uso.

Per la collocazione delle funzioni e dei moduli si veda
[architecture.md](architecture.md); per esecuzione e test si veda
[development.md](development.md).
