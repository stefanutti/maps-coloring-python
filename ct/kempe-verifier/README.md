# Verificatore combinatorio Kempe sul pentagono

Prototipo Python eseguibile, senza dipendenze esterne, fondato sulla **v16** di
*Building the Map from the Beach*. Studia le colorazioni del bordo di
`Q = T − v` (§10.4), enumera gli stati compatibili con vincoli necessari e
genera una **sovra-approssimazione** delle transizioni Kempe: tutti gli esiti
concreti devono essere inclusi, ma alcuni esiti astratti possono essere impossibili.

**Esito dell'esecuzione completa:** 2.160 stati con etichette fisse, oppure 90
modulo rinominazione dei quattro colori. Restano 120/5 candidati bad nel nucleo
conservativo. **R5 rimane irrisolto.** Questi candidati non sono controesempi.

## Posizione nel repository e avvio da `ct/`

Il pacchetto risiede in **`ct/kempe-verifier/`** ed è autonomo: non viene
importato dal programma principale e non richiede le sue dipendenze.
La fonte matematica è [4ct-v16.md](../../docs/llm-vs-4ct/4ct-v16.md).

Dalla root di `maps-coloring-python`, eseguire:

```sh
cd ct
PYTHONPATH="$PWD/kempe-verifier" python3 -m unittest discover -s kempe-verifier/tests -v
mkdir -p kempe-verifier/results
PYTHONPATH="$PWD/kempe-verifier" python3 -m kempe analyze --quotient-colors \
  --include-graph --output kempe-verifier/results/quotient.json \
  --explain kempe-verifier/results/explain.jsonl \
  --dot kempe-verifier/results/quotient.dot
```

Il comando con `PYTHONPATH` vale solo per quella esecuzione: non serve
installare il pacchetto né modificare l'ambiente della pipeline principale.
È possibile sostituire `python3` con `../.venv/bin/python` per usare
l'interprete già presente nel repository.

Altri comandi, sempre da `ct/`:

```sh
# Analisi con i nomi dei colori distinti.
PYTHONPATH="$PWD/kempe-verifier" python3 -m kempe analyze \
  --output kempe-verifier/results/labeled.json

# Mosse del candidato B0 fornito come esempio.
PYTHONPATH="$PWD/kempe-verifier" python3 -m kempe moves \
  --state kempe-verifier/examples/locked-b0.json \
  --output kempe-verifier/results/moves-b0.json

# Controesempio del §9.15 della v16.
PYTHONPATH="$PWD/kempe-verifier" python3 -m kempe pairing-example

# Classificatore sperimentale: non modifica il criterio R5 predefinito.
PYTHONPATH="$PWD/kempe-verifier" python3 -m kempe analyze \
  --classifier examples.custom_classifier:classify \
  --output kempe-verifier/results/experimental.json
```

Codice di uscita `0`: comando completato; `2`: input errato o analisi
interrotta. Leggere `r5_proved`, `bad_kernel` e `all_states_forced_good` nel
rapporto: un comando completato non è una dimostrazione matematica.

`results/` contiene le esecuzioni di riferimento ed è ignorata da Git;
chi ottiene il pacchetto tramite Git deve rigenerarla con i comandi sopra.
I risultati attesi sono nella tabella più avanti. Anche cache Python,
ambienti locali e file di build sono ignorati. I test vivono nella cartella
isolata `kempe-verifier/tests/`, separata dalla suite principale `ct/tests/`.

Il resto di questa guida mostra anche l'uso autonomo dalla sottocartella.
Non richiede cambiamenti a `4ct.py`, `ct_graph_utils.py` o alla loro configurazione.

## Esecuzione rapida

Richiede Python **3.9 o successivo**. Dalla cartella `kempe-verifier`:

```sh
python3 -m unittest discover -s tests -v
python3 -m kempe analyze --quotient-colors --output report.json
```

Non occorre installare il pacchetto. L'installazione con `pip install .` è
facoltativa e aggiunge il comando `kempe-verifier`.

### Rapporto completo, grafo e spiegazioni

```sh
python3 -m kempe analyze --quotient-colors --include-graph \
  --output report.json --explain explain.jsonl --dot graph.dot

python3 -m kempe analyze --output labeled.json
python3 -m kempe enumerate --quotient-colors --output states.json
python3 -m kempe pairing-example --output pairing-example.json
```

`--output -` (default) scrive JSON sullo standard output. Gli indici delle SCC,
dei nuclei e dei testimoni riferiscono l'array `states` del medesimo rapporto.
`--include-graph` aggiunge `actions[i]`: ogni azione ha **un insieme di esiti
alternativi**, non una lista di switch tutti garantiti. Il DOT rappresenta il
grafo delle possibilità; per ragionare sulle scelte usare le azioni nel JSON.

Per ispezionare un singolo stato, salvare un elemento di `states` come
`state.json`, poi:

```sh
python3 -m kempe moves --state state.json --output moves.json
```

Limiti: `--max-states` (default 100.000), `--max-edges` (default 1.000.000,
archi orientati distinti, cappi inclusi). Superare un limite produce codice
di uscita **2**, `status: incomplete` su stderr e nessuna nuova analisi.
Non viene restituito un grafo troncato da cui dedurre erroneamente la chiusura.
Un eventuale vecchio rapporto presente sul disco resta il rapporto della
precedente esecuzione. Il registro explain può essere parziale in caso di errore.

## Fonte matematica e scelte di rappresentazione

Documento letto: `docs/llm-vs-4ct/4ct-v16.md` del repository
`maps-coloring-python`; la fonte non è stata modificata.

SHA-256 della versione usata:

```text
68a06cdd35bafeba9607331ca8a6aeb31101d856500b1fbadba74a08d1e12b4c
```

| Parte della v16 | Uso nel prototipo |
|---|---|
| §10.4 | Q in un disco con bordo pentagonale indotto |
| §10.5 | criterio good/bad, settori E_i/B_i, cinque fan |
| §10.6 | switch su componenti di vertici; separazione per coppie di colori disgiunte |
| §§10.8–10.9 | significato delle classi interamente bad e del bersaglio esistenziale R5 |
| §9.8 | struttura separata `TransitionPairing`, chiusure e test delle due pagine |
| §§9.14–9.15 | limite della compressione e controesempio alla determinazione del nuovo stato |

### `State`: partizioni, non perfect matching

```python
from kempe.model import State, r5

state = State.from_dict({
    "boundary": [0, 1, 0, 2, 3],
    "partitions": {
        "01": [[0, 1, 2]], "02": [[0], [2, 3]],
        "03": [[0, 4], [2]], "12": [[1, 3]],
        "13": [[1, 4]], "23": [[3, 4]]
    }
})
assert r5(state).sector == "B0"
```

I terminali `0,...,4` rappresentano `a₀,...,a₄`, in ordine ciclico. I quattro
colori sono `0,...,3`. Per una coppia `ij`, la partizione registra quali
terminali di colore i o j appartengono alla stessa componente indotta.
Sono ammessi blocchi di qualsiasi dimensione, inclusi singleton; una coppia
senza terminali avrebbe la partizione vuota. Ogni terminale attivo compare
esattamente una volta. Lo stato è immutabile, confrontabile e utilizzabile
come chiave; membri e blocchi vengono ordinati canonicamente.

**Correzione della descrizione informale nella conversazione:** i sei oggetti
che servono qui sono partizioni di connettività di **vertici di Q**, non i
transition pairing del §9.8. La v16 non fornisce una corrispondenza che permetta
di identificarli. Il programma evita di inventarla.

`TransitionPairing` in `kempe/pairing.py` rappresenta invece il vero matching
`Q_AC(K)` su **tutti i vertici di uno specifico ciclo K**. Calcola le due
chiusure e una ripartizione in due pagine non incrociate, se esiste. Il comando
`pairing-example` riproduce esattamente i due matching del §9.15:

```text
Q1: prima {a}|{b,c}, dopo {a,b,c}
Q2: prima {a}|{b,c}, dopo {a,b}|{c}
```

Le etichette a,b,c sono rappresentate dagli indici 0,1,2 degli archi di Q
in ordine canonico. Questo calcolatore di una singola transizione primal
non viene impiegato come automa degli switch successivi in Q.

### Simmetrie

Per default **tutte le etichette dei colori restano distinte**, coerentemente
con §10.4. `--quotient-colors` sceglie la rinominazione canonica per ordine
di prima apparizione e rinomina insieme le sei coppie. Non identifica
rotazioni o riflessioni del pentagono: i cinque settori restano distinti.
Le azioni del rapporto usano i nomi dei colori dello stato sorgente; il
successore può essere rinominato al rappresentante canonico.

Le classificazioni e i filtri personalizzati richiedono le etichette fisse:
la loro invarianza rispetto a S4 non è assunta automaticamente.

## Vincoli di ammissibilità implementati

1. Colorazione propria del ciclo, inclusa l'adiacenza `a₄–a₀`.
2. Appartenenza esatta dei terminali alle sei partizioni.
3. Gli estremi di ogni arco bicolore del bordo appartengono allo stesso blocco.
4. Blocchi distinti di una stessa coppia non possono avere contatti alternati
   sul bordo del disco: `a,c,b,d` con a,b in un blocco e c,d nell'altro.
5. Lo stesso divieto vale fra componenti di coppie di colori **disgiunte**,
   come nell'argomento di separazione del §10.6.

Non si vietano incroci fra coppie che condividono un colore: le componenti
possono incontrarsi in vertici di quel colore. Vietarli riprodurrebbe un
passaggio ingiustificato nell'argomento di Kempe.

Questi vincoli sono necessari, **non un criterio di realizzabilità simultanea**.
Il modello non conserva triangolazione interna, 5-connessione di T,
dimensioni e molteplicità delle componenti, né compatibilità di intere
sequenze nello stesso grafo. Non impone parità o cardinalità pari ai blocchi:
una componente di vertici non è un cammino che debba accoppiare terminali.
Non applica ai conteggi astratti le divisibilità per 24, 120 o 18 del §10.8.

## `kempe_moves`: cosa è determinato e cosa resta possibile

Uno switch di colori i,j su una componente K determina:

- lo scambio dei colori nei terminali del blocco `K ∩ bordo`;
- l'invarianza della partizione `P_ij`, perché il sottografo indotto da i,j
  rimane identico come grafo non colorato;
- l'invarianza della partizione della coppia complementare, i cui colori
  non cambiano.

Per ciascuna delle altre quattro partizioni, il generatore considera **tutti**
i valori compatibili con i vincoli sopra e con le due partizioni invarianti.
Non sceglie un esito arbitrario. Non assume che ogni candidato abbia una
realizzazione sullo stesso Q della sorgente, o una realizzazione qualunque.

Ogni blocco non vuoto definisce un'azione **garantita** in ogni realizzazione
dello stato. Per ogni coppia si aggiunge anche l'azione `block=[]`: un
eventuale componente tutto interno, che può cambiare altre connettività pur
lasciando il bordo immutato. È **opzionale**, perché lo stato non ne certifica
l'esistenza. Componenti interni diversi sono aggregati nella stessa azione
possibile. Gli esiti remoti sono ulteriormente sovra-approssimati.

**Argomento di conservatività.** La proiezione di ogni colorazione concreta
di Q soddisfa i vincoli. Dopo uno switch concreto, le due partizioni citate
sono identiche, il nuovo bordo è quello calcolato e il risultato resta una
colorazione di un grafo nel disco. La sua proiezione è quindi fra i candidati
enumerati. Questo argomento vale anche per gli switch remoti. La verifica su
grafi piccoli controlla il codice; non sostituisce l'argomento generale.

## R5, SCC e nucleo bad: leggere correttamente il risultato

### Classificazione esatta della parola di bordo

- **good**, molteplicità `(2,2,1)`: si può colorare v con il quarto colore;
  il singleton identifica `E_i` e l'unico fan compatibile.
- **bad**, molteplicità `(2,1,1,1)`: il bordo fissato non si estende;
  la coppia ripetuta `(a_i,a_{i+2})` identifica `B_i`; sono compatibili tre fan.

Essere bad non esclude una successiva colorazione good. Una classe interamente
bad non confuterebbe da sola R5, che è esistenziale anche sulle altre classi.

### Grafo may

Il grafo ha un arco `s → t` quando t è uno degli esiti **possibili** di uno
switch astratto. Il rapporto elenca:

- `sccs`: componenti fortemente connesse del grafo intero;
- `bad_sccs`: SCC del grafo intero i cui stati sono tutti bad;
- `closed_bad_sccs`: fra queste, quelle senza archi verso l'esterno.

Una SCC del sottografo indotto dai soli bad non viene spacciata per una SCC
chiusa nel grafo intero. In un grafo finito ogni insieme non vuoto, chiuso
rispetto a tutti gli archi, contiene una SCC terminale: cercare queste SCC
individua dunque i componenti minimi degli insiemi bad universalmente chiusi.

**Attenzione ai quantificatori:** aggiungere archi possibili può cancellare
le SCC chiuse bad. Se un'azione da s può andare a s oppure a un good, l'arco
verso good non prova che una realizzazione concreta possa prenderlo.
Perciò `closed_bad_sccs=[]` **non implica** l'assenza di classi concrete bad.

### Nucleo conservativo e testimoni di eliminazione

Si parte da tutti gli stati bad e si itera:

```text
X(0) = Bad
X(n+1) = {s in X(n): per ogni azione garantita A in s,
                     esiste t in Successori(s,A) intersezione X(n)}
```

Gli esiti di un'azione sono alternative che un grafo concreto potrebbe imporre.
Uno stato si elimina solo quando **esiste una scelta di switch garantita
che porta fuori dall'insieme per tutti i suoi esiti possibili**. Gli switch
remoti opzionali non possono imporre eliminazioni. Per ciascuna eliminazione
il JSON conserva stato, livello, azione e intero insieme dei successori.

La proiezione di una classe concreta interamente bad deve sopravvivere in
`bad_kernel`: per ogni componente che tocca il bordo, il suo switch concreto
ha un esito bad nella stessa classe. Per induzione la proiezione sopravvive
a ogni livello. Un nucleo non vuoto è solo un insieme di candidati; non
certifica che tutti gli esiti scelti possano coesistere sullo stesso Q.

Le callback possono restituire `unknown`. In tal caso viene calcolato anche
`non_good_kernel`, inizializzato con bad **e** unknown. Solo questo secondo
calcolo può certificare `all_states_forced_good`; eliminare verso un unknown
non è una prova di raggiungibilità di good. In assenza di unknown i due
calcoli coincidono. Uno spazio vuoto non dà una certificazione vacua.

Il rapporto riporta sempre `r5_proved: false`: il prototipo non è un
certificatore formale della v16 e non verifica le premesse di filtri aggiunti.

## Esito riproducibile del modello predefinito

Esecuzione completa del 16 settembre 2026, con tutti gli switch remoti inclusi:

| Misura | Colori etichettati | Quoziente S4 |
|---|---:|---:|
| Stati | 2.160 | 90 |
| Good / bad | 1.080 / 1.080 | 45 / 45 |
| Azioni, incluse remote | 31.680 | 1.320 |
| Archi may distinti, inclusi cappi | 101.520 | 1.530 |
| SCC del grafo completo | 1 | 1 |
| SCC interamente bad / chiuse bad | 0 / 0 | 0 / 0 |
| Stati nel nucleo bad | 120 | 5 |
| Stati bad eliminati | 960 | 40 |

Il nucleo contiene un candidato per ciascun settore B_i modulo i colori.
Il JSON dello stato nell'esempio iniziale è il rappresentante del settore B₀:
entrambi i collegamenti `a₁–a₃` e `a₁–a₄` sono presenti. Il dato è compatibile
con l'ostacolo “locked” discusso nella conversazione; la sua realizzabilità
resta indeterminata. I 120 stati etichettati **non** sono 120 colorazioni di Q:
più colorazioni e grafi diversi possono proiettarsi sul medesimo stato.

## Personalizzazione e API Python

### Classificatore

```python
from kempe.model import Classification

def classify(state):
    # Una regola deve restituire anche il motivo della decisione.
    return Classification("unknown", "Criterio sperimentale non ancora definito")
```

```sh
python3 -m kempe analyze --classifier examples.custom_classifier:classify \
  --output experimental.json
```

L'esempio distribuito richiede specificamente il settore E₀ e considera gli
altri good come unknown: serve a mostrare l'interfaccia, **non è R5**.
Una callback è normale codice Python locale e viene eseguita come tale.

### Filtri di ammissibilità aggiuntivi

Disponibili nell'API; la CLI predefinita non aggiunge regole alla v16:

```python
from kempe.enumeration import Constraint, enumerate_states
from kempe.analysis import build_graph, analyze

def reject(state):
    return None  # Nessuna eliminazione senza una condizione matematica giustificata.

constraints = (Constraint("my_condition", "Riferimento esatto alla premessa", reject),)
states = tuple(enumerate_states(constraints=constraints))
graph = build_graph(states, constraints=constraints)
report = analyze(graph)
```

Usare gli stessi filtri nell'enumerazione e nelle mosse. Ogni filtro restituisce
`None` per accettare oppure un motivo testuale per eliminare. Nome e fonte sono
obbligatori e vengono conservati nel rapporto. Il codice non dimostra la fonte.
Un filtro deve valere per **ogni colorazione raggiungibile** della famiglia
concreta studiata, non solo per gli stati iniziali, affinché l'astrazione resti
conservativa. Non rimuovere i good per studiare il caso bad: la ricerca del
nucleo lo fa preservando tutti gli archi del grafo completo.

`build_graph` controlla che ogni successore sia presente nello spazio passato;
passare un ritaglio non chiuso produce un errore. Un'azione garantita con
nessun successore ammissibile produce un errore invece di un falso successo.

### `explain`

`Explain(stream=...)` registra eventi JSONL con codice, motivo e contesto:
parola, coppia, partizione, oppure sorgente/azione/candidato. Registra anche
le eliminazioni iterative dal nucleo con il loro testimone. Codici principali:

```text
boundary.not_proper
partition.boundary_edge
planarity.same_pair_cross
planarity.disjoint_colors_cross
symmetry.color_representative
move.switched_pair_changed
move.complement_changed
custom.<nome>
kernel.no_bad_successor
```

Il rapporto contiene conteggi esatti degli **eventi** e i primi 20 esempi;
il file JSONL conserva tutti gli eventi. Un candidato può violare più regole;
un ramo di enumerazione può essere scartato prima di costruire stati completi.
Quindi il numero di eventi non è il numero di stati distinti eliminati.
La rinominazione per simmetria è segnalata come tale, non come impossibilità.
Gli esiti che sopravvivono sono nel rapporto delle mosse; `explain` non
inventa motivi per eliminarli. File grandi sono possibili con etichette fisse.

## Test e struttura del codice

I test controllano proprietà indipendenti dal motore di transizione:

- le 240 parole proprie e i dieci settori della v16;
- validazione e canonicalizzazione di colori, blocchi e serializzazione;
- generazione di tutte le alternative compatibili con gli invarianti;
- Exchange Lemma nei casi unlinked;
- uno switch remoto concreto che modifica la connettività;
- tutti gli switch di colorazioni di piccoli dischi, incluso l'icosaedro
  senza un vertice, mediante un oracolo di connettività separato;
- uguaglianza fra grafo quoziente e proiezione del grafo etichettato;
- SCC, chiusura, quantificatori, livelli di eliminazione e unknown;
- il controesempio §9.15 e matching che non ammettono due pagine;
- CLI, rapporti JSON/DOT, registro explain e arresto per limiti.

| File | Responsabilità |
|---|---|
| `kempe/model.py` | Stato canonico, etichette, classificazione R5 |
| `kempe/enumeration.py` | Partizioni e vincoli necessari nel disco |
| `kempe/moves.py` | Switch e insiemi di esiti conservativi |
| `kempe/analysis.py` | Grafo may, SCC e nuclei conservativi |
| `kempe/pairing.py` | Matching primal e chiusure esatte di un ciclo |
| `kempe/explain.py` | Eventi, conteggi e registro JSONL |
| `kempe/__main__.py` | Interfaccia da terminale |
| `tests/` | Test automatici e oracoli su grafi concreti |
| `docs/design.md` | Specifica e limiti dell'astrazione |

La ricerca delle SCC è iterativa, senza limite di ricorsione legato alla
dimensione del grafo. L'enumerazione resta pensata per un bordo di **cinque**
vertici. Generalizzare il numero di terminali o collegare i veri pairing
primal agli stati duali richiede una nuova specifica matematica.
