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
| `-s6` | `select_edge_to_remove_even_faces` | Dopo le F2, fa crescere una faccia principale pari fondendola con facce adiacenti pari (faccia ridotta al massimo F5); ricostruzione dedicata, senza scambi casuali. |
| `-s7` | `select_edge_to_remove_even_ring` | Studio: come S6 ma senza limite di taglia, con una scelta che garantisce una faccia pari accanto alla faccia unita; usa la ricostruzione di S6. |
| `-s8` | `select_edge_to_remove_even_faces_restart_away` | Completa le fusioni pari ammissibili, senza limite di taglia, prima di ripartire lontano dal perimetro della faccia principale. Usa la ricostruzione di S6. |

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

### S6: faccia principale pari

S6 cerca di mantenere pari la faccia prodotta da ogni riduzione e di farla
crescere assorbendo facce adiacenti pari, fino al grafo theta (tre F2).
Le lunghezze dopo una riduzione si calcolano così: la faccia unita misura
`len(f1) + len(f2) - 4` (per una F2, `len(f2) - 2`); ogni altra faccia perde
un lato per ciascuno dei due vertici soppressi che contiene, e può quindi
cambiare parità.

La selezione, deterministica e a priorità fissa, prova in ordine:

1. **F2.** La prima riduzione F2 senza ponti. I gestori di ricostruzione e
   `remove_vertex_from_face()` presuppongono che nessun arco multiplo tocchi
   una F3/F4 ridotta, come in S1–S5. Rimuovere una F2 non cambia alcuna
   parità: `f2` e la terza faccia perdono due lati ciascuna.
2. **Continuazione.** Se la faccia principale, cioè la faccia prodotta dalla
   riduzione S6 precedente, esiste ancora ed è pari, la fonde con una faccia
   adiacente pari. La più piccola delle due facce deve avere al più cinque
   lati; le vicine più piccole hanno la precedenza. Due facce pari si
   fondono sempre in una faccia pari.
3. **Avvio.** Altrimenti, in ordine F3, F4, F5, la prima riduzione la cui
   faccia unita è pari.
4. **Ripiego.** Se nessuna candidata soddisfa le condizioni di parità, la
   prima riduzione F3/F4/F5 senza ponti.

`f1`, la faccia descritta dal record di Arianna, è sempre la più piccola
delle due e ha al più cinque lati (`S6_MAX_REDUCED_FACE`). Così una vicina F4
mantiene il suo gestore di ricostruzione dimostrato e un F5 usa la
ricostruzione deterministica descritta sotto.

**Perché il limite di cinque lati.** Una versione senza limite fondeva la
faccia principale con vicine pari di qualunque taglia. Completava le mappe
casuali, ma si fermava su 4 delle 10 mappe waterworld, su record da F6 a F12.
Il caso studiato in dettaglio, in `waterworld-3`, staccava una F8 da una
faccia di 402 lati: in 160 colorazioni diverse del grafo nessuna permetteva il
mezzo scambio, quindi nessuna ricerca di Kempe poteva riuscire. In termini di
colori delle facce, `f1` ed `f2` stanno nella stessa coppia di colori A; il
mezzo scambio richiede che le due facce agli estremi dell'arco reinserito
siano collegate senza attraversare la regione A che contiene `f1` ed `f2`.
Una faccia principale enorme, che avvolge parti della mappa, chiude quel
passaggio, e più lati ha `f1` più vicine possono bloccarlo.

Una protezione euristica "dalle sacche" (scartare un F5 se una sua vicina
tocca `f2` in più tratti separati) è stata provata e scartata: senza limite
di taglia non evitava i blocchi, e con il limite faceva fallire
`waterworld-2`, che senza protezione viene completata.

Nei passi 2 e 3 una candidata è accettata solo se non crea ponti
(`is_the_graph_one_edge_connected()` falso) e se la faccia unita, dopo la
riduzione, ha almeno una faccia adiacente pari. La faccia unita diventa la
nuova faccia principale; una riduzione F2 la sposta solo se la assorbe.
Il riferimento è conservato in `s6_principal_face` e azzerato all'inizio di
ogni esecuzione (`i_global_counter == 0`). S6 ignora `--choices` e la wave
frontier e restituisce sempre `event = None`. Le statistiche `SELECT-S6-*`
contano i quattro casi.

#### Ricostruzione S6

Con `-s6`, `-s7` e `-s8`, `rebuild_faces()` riceve il gestore
`restore_step=restore_ariadne_step_s6`:

- F2, F3 e F4 usano i gestori esistenti, il cui successo è garantito;
- F5 e le facce più grandi usano `ariadne_case_any_face()`.

`ariadne_case_any_face()` non dipende dalla taglia della faccia. I due archi da
suddividere, `(on_v1, off_v1)` e `(on_v2, off_v2)`, stanno sul bordo della
faccia unita. Se stanno già su un ciclo di Kempe comune, basta un mezzo
scambio: si scambiano i due colori sull'arco del ciclo che parte dal lato
`on_v1`, e la planarità garantisce che quell'arco arrivi dal lato `on_v2`. Il
nuovo arco prende il terzo colore. Il controllo usa le chiavi del multigrafo,
quindi distingue gli archi paralleli. Se il ciclo comune non esiste,
`find_kempe_repair()` cerca in modo deterministico gli scambi di cicli interi
che lo creano, entro `--kempe-search-limit`. Se si esaurisce il budget, la
ricostruzione si ferma con `KempeSearchExhausted`, come in S5. S6 non usa mai
scambi casuali.

**Classe di Kempe esaurita: ricolorazione esatta.** Le colorazioni di un
grafo possono formare più classi di Kempe, e gli scambi di Kempe non passano
mai da una classe all'altra. Può succedere che i reinserimenti precedenti
portino la colorazione in una classe in cui nessuna colorazione permette il
mezzo scambio, anche se un'altra classe dello stesso grafo lo permette. Nella
mappa 3 di `maps_3000_maps_of_8000_faces.planar`, al 14° reinserimento F5,
il grafo di 28 vertici ha 210 colorazioni in due classi: quella raggiunta ne
ha 36, nessuna utile; l'altra 174, di cui 96 utili. In questo caso
`find_kempe_repair()` solleva `KempeClassExhausted` (sottoclasse di
`KempeSearchExhausted`) e `_recolor_with_edge_restored()` reinserisce l'arco
e colora l'intero grafo con `find_three_edge_coloring()`, una ricerca
esaustiva e deterministica che conserva i colori correnti dove possibile. Una
classe si esaurisce solo se è piccola, quindi solo su grafi piccoli, verso la
fine della ricostruzione, dove la ricerca esaustiva è istantanea. È l'unico
passo di S6 che esce dal metodo di Kempe.

Le statistiche distinguono i reinserimenti diretti (`REBUILD-DIRECT`) da
quelli con ricerca (`REBUILD-SEARCHED`), gli stati esaminati, gli scambi
deterministici, la faccia più grande ricostruita (`REBUILD-MAX-FACE`), le
ricolorazioni esatte (`EXACT-RECOLORINGS`) e il grafo più grande
ricolorato (`EXACT-MAX-VERTICES`). S7 e S8 usano la stessa ricostruzione e la stessa misura dei perimetri, quindi
aggiornano gli stessi contatori `REBUILD-*`, `EXACT-*` e `MEASURE-*`.

Il gestore classico ora rifiuta con un errore esplicito un record senza
gestore (per esempio F6+), invece di saltarlo in silenzio; S1–S5 non
producono mai record del genere.

#### Misura dei perimetri (studio)

Con `-s6`, `-s7` e `-s8`, `reduce_faces()` conserva una copia del bordo di ogni faccia
unita e `rebuild_faces()` lo misura con `measure_s6_reinsertion()` prima di
ogni reinserimento diverso da F2, senza modificare colori né scelte. In quel
momento il grafo è nello stesso stato di quando la faccia è stata creata.
Le statistiche `MEASURE-*` contano:

- la parità del perimetro (`M-EVEN`, `M-ODD`);
- i perimetri bicolori, cioè un unico ciclo di Kempe (`M-EVEN-BICHROMATIC`);
- i casi in cui i due archi da suddividere stanno già su un ciclo di Kempe
  comune per almeno una coppia di colori (`M-*-SAME-KEMPE`), anche per
  taglia della faccia ridotta (`F3/F4/F5/F6+-M-EVEN*`);
- i perimetri con un arco multiplo (`UNKNOWN`), per i quali la ricerca del
  colore per coppia di vertici sarebbe ambigua.

Un perimetro bicolore garantisce il reinserimento con un solo mezzo scambio,
per qualunque taglia di `f1`; per il reinserimento basta però la condizione
più debole `SAME-KEMPE`.

### S8: catene pari e riavvii lontani dalla faccia principale

S8 fa avanzare la catena finché la faccia principale può fondersi con una
vicina pari senza creare ponti. Le fusioni considerano facce di qualunque
taglia, dando precedenza alle candidate con `f1` più piccola. A ogni nuovo
avvio, entrambi gli estremi dell'arco scelto devono stare fuori dal perimetro
dell'ultima faccia principale ancora presente.

La selezione prova in ordine:

1. **F2**, come in S6.
2. **Continuazione** (`SELECT-S8-CONTINUE`). Seleziona la prima
   fusione pari senza ponti che lascia almeno una vicina pari dopo la riduzione.
3. **Ultima fusione** (`SELECT-S8-CONTINUE-LAST`). Se nessuna candidata lascia
   una vicina pari, seleziona comunque la prima fusione senza ponti con una
   vicina pari della faccia principale corrente. La faccia unita diventa la
   nuova principale e al passo seguente il selettore rivaluta il suo perimetro.
4. **Avvio lontano** (`SELECT-S8-START`). Cerca una fusione senza ponti con
   faccia unita pari. Esclude la principale e le facce che condividono un
   arco con lei. Fra le candidate lontane dà precedenza a quelle che lasciano
   una vicina pari e, in assenza di queste, accetta la prima fusione pari.
5. **Avvio vicino** (`SELECT-S8-START-TOUCHING`). Se un avvio lontano non
   esiste, cerca una fusione pari anche fra le facce vicine, mantenendo il
   vincolo sugli estremi dell'arco.
6. **Ripiego** (`SELECT-S8-FALLBACK`). Sceglie la prima fusione senza ponti,
   in ordine crescente di taglia di `f1`, fra gli archi con entrambi gli
   estremi fuori dal perimetro precedente. È un passo strutturale di
   qualunque parità. La faccia unita resta fuori dall'onda e la principale
   precedente continua a essere protetta. Se manca anche questa fusione,
   S8 si ferma e segnala il vincolo che impedisce la ripartenza.

Da CLI, `-s8` prosegue dopo ogni avvio vicino riuscito. Esporta il grafo
corrente in DOT quando tutte le mosse fino all'avvio vicino sono esaurite,
prima del ripiego strutturale. Se raggiunge theta, esporta theta. La chiamata
Python a `reduce_faces()` può proseguire con il ripiego strutturale e fornire
il filo di Arianna alla ricostruzione.

Come in S7, una riduzione F2 sposta la faccia principale solo se questa
assorbe la F2; se la faccia principale si è ridotta essa stessa a una F2,
scompare con lei. `S8-MAX-PRINCIPAL` registra il numero massimo di lati
raggiunto dalla faccia principale durante la riduzione. Il primo numero di
un record di Arianna è la lunghezza di `f1`, quindi può superare 5. La
ricostruzione condivide i contatori `REBUILD-*`, `EXACT-*` e `MEASURE-*`.

Durante la riduzione S8 conserva i bordi pari delle onde ancora presenti,
preferendo il bordo più recente quando due bordi condividono un vertice.
Quando i cicli sono disgiunti e coprono tutti i vertici, salva la copertura
accanto al record di Arianna (`S8-CYCLE-COVER`). Alternare rosso e verde lungo
i cicli lascia esattamente un arco blu a ogni vertice.

Durante la ricostruzione, se i due archi da suddividere appartengono allo
stesso ciclo rosso–verde, S8 applica il mezzo scambio (`S8-CYCLE-DIRECT`).
Se serve, prova prima la colorazione della copertura salvata per quel passo
(`S8-CYCLE-RECOLORED`). Le F2, i triangoli da ripristinare su due archi
paralleli e i casi privi di un ciclo rosso–verde comune usano i gestori di
S6 (`S8-CYCLE-SPECIAL`), compresa la ricerca di Kempe quando necessaria.

Nelle prove precedenti all'introduzione di `SELECT-S8-CONTINUE-LAST` si è
osservato un avvio vicino su 3697 con 20 mappe `-r1 300` e 42 su 803 con 20
mappe `-r2 200`. Il numero di continuazioni era simile a S6.

### S7: catene pari senza limite di taglia (studio)

S7 riprende S6 senza alcun limite sulla taglia delle facce e cerca di
garantire che la catena non si interrompa: dopo ogni fusione, la faccia unita
deve avere una vicina pari con cui continuare.

**Argomento dell'anello.** Siano N1, …, Nk le facce attorno alla faccia
principale P, pari, nell'ordine del bordo. Fondere P con una vicina pari Ni dà
una faccia pari M; le due facce accanto a Ni nell'anello, N(i−1) e N(i+1),
sono le laterali: perdono un lato e cambiano parità, le altre no.

- Se l'anello contiene entrambe le parità, c'è una Ni pari accanto a una
  faccia dispari: fondendo Ni, quella dispari diventa pari, quindi M ha una
  vicina pari.
- Se l'anello è tutto pari e ha almeno quattro facce, quelle lontane da Ni
  restano pari.

Le eccezioni sono i casi degeneri: ponti (una vicina che tocca P in più
tratti), laterali coincidenti, anelli corti, e le vicine F2, che sono pari ma
vengono ridotte subito. Una fusione che produce una faccia pari esiste sempre
senza limiti di taglia: in ogni vertice due delle tre facce hanno la stessa
parità.

La selezione prova in ordine:

1. **F2**, come in S6.
2. **Continuazione:** una vicina pari di P, di qualunque taglia, tale che M
   abbia almeno `S7_DURABLE_EVEN` = 4 lati e tocchi, dopo la riduzione, una
   faccia pari di almeno quattro lati. Le `f1` più piccole hanno la
   precedenza.
3. **Avvio:** la prima coppia adiacente, per taglia crescente di `f1`, con le
   stesse condizioni.
4. **Ripiego:** la prima riduzione senza ponti, per taglia crescente.

Quando una catena si interrompe, `S7-BREAK-*` ne registra il motivo:
`ODD-PRINCIPAL` (la faccia principale è dispari, conseguenza di un ripiego),
`PRINCIPAL-GONE` (la faccia principale non esiste più: ogni F2 adiacente
eliminata le toglie due lati, e quando si riduce a una F2 viene eliminata a
sua volta; la faccia che la assorbe può avere qualunque parità, quindi non
eredita il ruolo), `NO-EVEN-NEIGHBOR`, `BRIDGE` (tutte le continuazioni creano
un ponte) e `NO-DURABLE-EVEN`. `S7-MAX-CHAIN` e `S7-MAX-PRINCIPAL` danno
la catena più lunga e la faccia principale più grande. La ricostruzione è
quella di S6 (`restore_ariadne_step_s6()`), deterministica.

**Risultati.** La garanzia di parità regge: con 20 mappe `-r1 300` le
continuazioni passano da circa il 38% delle riduzioni (S6) all'84%, e la catena
più lunga da 18 a 253 passi; il motivo principale di interruzione è un ponte.
Su `waterworld-3` la riduzione è quasi un'unica catena (2235 continuazioni
consecutive su 2787 riduzioni) e la faccia principale arriva a 408 lati. Proprio
per questo la ricostruzione si ferma sullo stesso reinserimento F8 di S6 senza
limite: una catena che non si interrompe produce una faccia principale enorme,
e con essa i reinserimenti che nessuna colorazione permette. Le mappe
casuali, `bad-c-2345-infinite_loops` e i poliedri di prova vengono completati.

## Il filo di Arianna

Ogni riduzione memorizza soltanto il contesto locale necessario per tornare
indietro. I record hanno due forme:

```text
F2:       [2, v1, v2, near_v1, near_v2]
F3+:      [n, v1, v2, on_v1, on_v2, off_v1, off_v2]
```

La prima posizione identifica il caso di ricostruzione. S1–S5 producono
soltanto `n <= 5`; S6 può produrre anche `n > 5`. I record sono
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
necessariamente identiche. S5 e S6 usano invece la ricerca deterministica
descritta sopra. I generatori casuali e l'opzione esplicita `--shuffle` rimangono casuali.

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
