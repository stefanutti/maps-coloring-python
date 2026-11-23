# Studio dell'oracolo — passo 1: una riduzione F5

Data: 27 settembre 2026.

Questo esperimento studia i pentagoni degli **stati iniziali** delle 151 mappe
già colorate. Assume la correttezza degli input verificata dall'autore; non
riesegue una verifica generale delle colorazioni originali. Classifica le
scelte con un criterio cromatico esplicito ed esegue nove riduzioni campione,
controllando i grafi trasformati e la loro ricostruzione.

Non esplora ancora una sequenza fino a theta, né l'albero delle riduzioni.
Il codice sperimentale è in
[`ct/experiments/f5_oracle_probe.py`](../../ct/experiments/f5_oracle_probe.py).
Gli aggregati e i tre esempi sono conservati nel
[risultato JSON](4ct-oracle-study-step-1-results.json).

## 1. La scelta fornita dalla colorazione nota

Su un pentagono propriamente colorato nessun colore può comparire più di due
volte: archi consecutivi devono avere colori distinti. Due colori non bastano
a colorare un ciclo dispari. Le molteplicità sono quindi necessariamente
**2, 2, 1**.

Questo argomento e la trasformazione seguente sono già descritti nella
[sezione 10.2 di v17](4ct-v17.md#102-a-canonical-bijection).

Sia `pq` l'unico lato di colore W. Gli altri quattro lati formano un cammino
da p a q, alternato nei colori U e V. L'operazione è:

1. eliminare `pq`;
2. scambiare U e V lungo quei quattro lati;
3. sopprimere p e q, fondendo le coppie di archi che vi rimangono incidenti.

Dopo lo scambio ciascuna coppia da fondere ha lo stesso colore. I vertici
interni del cammino continuano a vedere tre colori distinti. Si ottiene
quindi una colorazione propria del grafo ridotto. L'operazione inversa
reinserisce p e q, ripete lo scambio sul cammino e ripristina `pq` con W.

Questa è una costruzione basata sulla colorazione già nota. Non è ancora
una regola che selezioni l'arco usando soltanto la struttura.

## 2. Criterio esteso alle cinque scelte

Per un lato `uv` di colore C, consideriamo il sottografo formato dagli altri
due colori. Essendo la colorazione di Tait completa, questo sottografo è
un'unione di cicli bicolori.

Il criterio usato nell'esperimento è:

> u e v appartengono allo stesso ciclo dei due colori diversi da C.

Quando è vero, un arco di quel ciclo congiunge u a v. Eliminando `uv`,
scambiando i due colori lungo quell'arco e sopprimendo u e v, le coppie fuse
ricevono colori coerenti. Per gli esempi planari si percorre l'arco che parte
sul lato del pentagono e si verifica che raggiunga v dallo stesso lato.

Il lato del colore unico soddisfa sempre il criterio: il cammino è già
visibile sui quattro lati rimanenti del pentagono. Altre scelte possono
soddisfarlo mediante cammini che attraversano il resto della mappa.

Se il criterio è falso, questa particolare operazione non è disponibile
nella colorazione corrente. **Non significa che la riduzione sia impossibile:**
non abbiamo cercato altri scambi preliminari o altre colorazioni.

Il controllo strutturale viene eseguito separatamente, tramite `join_faces()`
e `is_the_graph_one_edge_connected()`, come nel programma principale.

## 3. Il primo pentagono concreto

Prima mappa, faccia di indice 0. Il bordo è:

```text
0 --blu-- 1 --verde-- 2 --rosso-- 3 --blu-- 4 --verde-- 0
```

I gradi delle facce adiacenti, nello stesso ordine, sono `6, 6, 5, 5, 5`.

| Arco da eliminare | Colore | Grado della faccia vicina | Controllo strutturale | Stesso ciclo complementare |
| --- | --- | ---: | --- | --- |
| 0–1 | blu | 6 | superato | no |
| 1–2 | verde | 6 | superato | no |
| 2–3 | rosso | 5 | superato | sì |
| 3–4 | blu | 5 | superato | no |
| 4–0 | verde | 5 | superato | no |

La riduzione dell'arco rosso è stata eseguita. Sono stati controllati la
colorazione del risultato, l'assenza di loop e ponti, la perdita di due
vertici e tre archi e la coincidenza con l'embedding ottenuto usando le
primitive di riduzione del programma.

La ricostruzione con `apply_half_kempe_loop_color_switching()` restituisce
esattamente i vertici e il multinsieme degli archi colorati originali.
Anche `ariadne_case_f5()` ricostruisce questo caso direttamente, recuperando
gli stessi colori, senza ricerca preliminare di altri scambi.

## 4. Risultati sulle 151 mappe

Input: `ct/maps_3000_maps_of_8000_faces.colored.planar`, prime 151 righe.
Per ogni mappa vengono calcolate le componenti dei tre sottografi bicolori.
Il conteggio valuta il criterio per ogni scelta; non esegue materialmente
milioni di riduzioni.

| Misura | Risultato |
| --- | ---: |
| Mappe analizzate | 151 |
| Pentagoni iniziali | 571.369 |
| Scelte candidate, cinque per pentagono | 2.856.845 |
| Candidate che superano il controllo strutturale del programma | 2.856.845 |
| Candidate sullo stesso ciclo complementare | 1.888.271 (66,10%) |
| Di cui: lato del colore unico | 571.369 |
| Di cui: altre scelte | 1.316.902 |
| Candidate non risolte da questo criterio | 968.574 |

Ogni pentagono ha 1, 3 oppure 5 scelte che soddisfano il criterio:

| Scelte per pentagono | Pentagoni | Percentuale |
| ---: | ---: | ---: |
| 1 | 107.159 | 18,75% |
| 3 | 269.969 | 47,25% |
| 5 | 194.241 | 34,00% |

Le percentuali descrivono questo campione di pentagoni e le colorazioni
fornite. Non sono una stima di generalizzazione a nuove mappe. Non sono
stati eseguiti addestramento o suddivisioni train/test.

### Perché compaiono 1, 3 e 5

Il fenomeno ha una spiegazione combinatoria. Scriviamo il bordo, scegliendo
orientamento e nomi dei colori, come A, B, C, A, B, con C unico.

Nel sottografo B/C i vertici 1 e 3 sono già collegati dal cammino 1–2–3,
mentre 4 e 0 sono collegati dall'arco 4–0. Quindi 0 e 1 stanno nello stesso
ciclo se e solo se vi stanno 3 e 4: i due lati A hanno lo stesso esito.
Lo stesso ragionamento vale per i due lati B. Il lato C ha sempre esito
positivo. Il numero di esiti positivi è pertanto

```text
1 + 2 × indicatore(A) + 2 × indicatore(B).
```

Questa deduzione riguarda il criterio cromatico prima di eventuali filtri
strutturali. Nel campione tutte le candidate superano anche quel filtro.

## 5. Nove trasformazioni eseguite

Nella prima mappa sono stati scelti i primi pentagoni con rispettivamente
1, 3 e 5 scelte compatibili: facce di indice 0, 2 e 7. Sono state eseguite
tutte le rispettive scelte compatibili, nove in totale.

Tutte producono un grafo ridotto ben colorato, senza loop né ponti e con
embedding coerente con le primitive esistenti. Tutte ammettono il ritorno
esatto alla colorazione originale usando l'inverso dello scambio scelto.
Il gestore F5 esistente ricostruisce tutti e nove i casi senza ricerca S5.

I cammini scambiati hanno lunghezze `4`, `37, 4, 18` e `7, 108, 4, 48, 69`,
nei tre pentagoni rispettivamente. Il criterio può quindi usare connessioni
che escono dal pentagono, anche in questa prima prova.

Per la faccia 2 e l'arco 4–9, il gestore F5 normale restituisce una
colorazione valida diversa da quella iniziale. L'inverso dello scambio
registrato recupera invece i colori originali anche in questo caso.
Per un futuro certificato di ricostruzione dell'oracolo occorrerà conservare
la coppia di colori e il cammino scelto, oltre al record topologico di Arianna.

## 6. Un limite della firma basata sui cinque gradi

La firma di una candidata inizia dal grado della faccia oltre l'arco scelto
e prosegue lungo il pentagono. Per eliminarne la dipendenza dall'orientamento
si prende la sequenza minore tra lettura nei due versi.

Nel primo pentagono gli archi 2–3 e 4–0 hanno entrambi firma
`(5, 5, 5, 6, 6)`, ma soltanto 2–3 soddisfa il criterio cromatico.

Questo è un controesempio alla possibilità di **determinare esattamente
questo esito, nella colorazione fornita, dai soli cinque gradi**. Non esclude
condizioni sufficienti per altre firme, regole che usino più struttura o
la ricostruibilità dopo ulteriori scambi.

## 7. Riproducibilità e confini dell'esperimento

Da `ct/`, per ripetere il primo esempio e il conteggio della prima mappa:

```bash
uv run --python ../.venv/bin/python python experiments/f5_oracle_probe.py --limit 1
```

Per ripetere il conteggio completo:

```bash
uv run --python ../.venv/bin/python python experiments/f5_oracle_probe.py --limit 151
```

`--input FILE` permette di indicare un'altra raccolta nello stesso formato.
Il prototipo assume mappe iniziali completamente colorate; il tracciamento
dei nove cammini campione richiede archi iniziali semplici. Non è ancora
un motore per stati intermedi con archi paralleli. Gli assert controllano
le trasformazioni studiate e non vanno disabilitati con `python -O`.

Le caratteristiche degli esempi sono separate in `structure` e `oracle`.
`structure` deriva dall'embedding senza colori; `oracle` contiene colori,
appartenenza ai cicli e risultati delle trasformazioni. Il JSON conserva
gli aggregati e tre esempi, non un dataset completo di milioni di righe.

L'esperimento non modifica il dataset o l'algoritmo principale. La prova
locale garantita dal colore unico assume già una colorazione disponibile:
non dimostra il risultato per un grafo non ancora colorato e non completa
la dimostrazione di esistenza del ramo fino a theta.

Il prossimo studio è concatenare le riduzioni su **una sola mappa**,
definendo anche la gestione cromatica di F2/F3/F4, aggiornando l'oracolo
dello stato corrente e conservando i certificati per il ritorno esatto.

Il [piano di continuazione Superpowers](../superpowers/plans/2026-09-28-oracle-reduction-study.md)
conserva lo stato dello studio, le attività verificabili, le fasi successive
e un prompt per riprendere in un'altra chat. Lo studio locale delle
trasformazioni F2/F3/F4 è ora documentato nel [passo 2](4ct-oracle-study-step-2.md);
il checkpoint aggiornato si trova nel piano.
