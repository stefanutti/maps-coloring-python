# Studio dell'oracolo — passo 2: F2, F3 e i due casi F4

Data: 28 settembre 2026. Studio della Task 1 e verifica automatica della Task 3 del
[piano](../superpowers/plans/2026-09-28-oracle-reduction-study.md).

Le costruzioni sotto sono confrontate con piccoli embedding colorati nei
[test riproducibili](../../ct/tests/test_oracle_reduction.py), non con le
151 mappe. Le sezioni iniziali conservano lo studio manuale della Task 1;
l'aggiornamento Task 3 in fondo documenta `plan_step()` e i limiti attuali.
Si riusano le primitive esistenti senza modificarle.

## Ipotesi e notazione

Si parte da un grafo connesso, cubico, planare, senza loop né ponti e già
propriamente colorato. I colori A, B, C sono tre nomi distinti fra rosso,
verde e blu. L'oracolo rimane un'ipotesi: non stiamo colorando un input
arbitrario non colorato.

Per il passo generico si elimina un lato uv, si scambiano due colori lungo
un cammino complementare da u a v e si sopprimono u e v. Ai vertici interni
del cammino vengono scambiati due archi; a ciascuno degli estremi cambia
solo uno dei due archi rimasti, che diventano dello stesso colore e possono
essere fusi. Se si usa questo schema, i due estremi e gli archi da fondere
devono essere identificati senza ambiguità, soprattutto con archi paralleli.

## F2: nessuno scambio

I due archi del digono fra u e v hanno colori A e B. Il terzo arco incidente
a ciascun estremo deve avere colore C. Eliminando il digono e i suoi due
vertici, i due archi esterni vengono sostituiti da un unico arco di colore C.
Per l'inverso si suddivide quell'arco, si reinseriscono u e v e i due archi
paralleli A e B. Occorre conservare quale occorrenza aveva ciascun colore
se si vuole recuperare anche l'embedding colorato esatto.

Theta è il caso terminale: il terzo arco unisce già u e v, non ci sono due
archi esterni da fondere. Non si applica un'altra riduzione F2 a theta.
Negli altri casi i due vicini esterni sono distinti: se coincidessero,
quel vertice vedrebbe due archi di colore C, contro l'ipotesi di colorazione
propria. La fusione non introduce quindi un loop.

## F3: uno scambio lungo due lati

Un triangolo usa tutti e tre i colori. Scegliendo il lato uv di colore C,
gli altri due lati sono un cammino A/B fra u e v. Eliminare uv, scambiare
A/B sui due lati, poi fondere le coppie concordi agli estremi.

Nel tetraedro i due vicini esterni coincidono. Il risultato è theta con tre
archi paralleli distinti: non è un errore e non va convertito in un grafo
semplice. L'inverso deve distinguere i due archi fusi dal terzo arco esistente.

## F4 con tre colori: uno scambio lungo tre lati

La parola sul bordo, a meno di rotazione e rinomina, è A,B,A,C. Scegliere
uno dei due colori singoli, per esempio C: gli altri tre lati sono A,B,A.
Dopo la cancellazione del lato C, scambiare A/B sul cammino di tre lati e
sopprimere gli estremi. La stessa costruzione vale scegliendo B.

Questo certifica le due scelte singole nella colorazione corrente; non
afferma che ogni scelta del colore ripetuto abbia lo stesso testimone locale.

## F4 con due colori: due sottocasi esterni

Scrivere il quadrato 0–1–2–3–0 con parola A,B,A,B; i quattro archi esterni
hanno colore C. Guardare i cicli A/C che contengono i lati opposti 0–1 e 2–3.

- **Cicli distinti:** scambiare A/C sul ciclo contenente 0–1. Il bordo diventa
  C,B,A,B, quindi 0–1 è ora un lato di colore singolo. Eliminarlo e applicare
  lo scambio locale A/B sui tre lati restanti. Per tornare ai colori iniziali,
  invertire prima la riduzione locale, poi lo scambio sul ciclo completo.
- **Stesso ciclo:** tutti e quattro i vertici del quadrato sono sullo stesso
  ciclo A/C. Un lato B, per esempio 1–2, soddisfa dunque il criterio diretto
  del ciclo complementare. Il cammino da scambiare può uscire dal quadrato.
  In questo sottocaso non è necessario uno scambio preliminare.

La costruzione individua **almeno una scelta cromatica**, non promette di
risolvere qualsiasi lato fissato in anticipo con lo stesso procedimento.
La topologia della candidata va verificata separatamente prima di accettare
il passo; il motore futuro manterrà la priorità F2/F3 prima delle F4.

### Che cosa stabilisce questo ragionamento

I due lati opposti A sono necessariamente su uno stesso ciclo A/C o su due
cicli distinti. I sottocasi esauriscono quindi questa alternativa cromatica:
nel primo si sceglie un lato B; nel secondo si cambia un solo ciclo e si
sceglie il lato A appena diventato C. Non serve ipotizzare una ricerca
casuale per trovare questa scelta, data la colorazione propria.

Il conteggio degli scambi preliminari completi è dunque al più uno per questa
costruzione F4; lo scambio parziale può però avere lunghezza non locale.
Non si sta affermando un limite uniforme alla lunghezza del cammino.

Questo argomento riguarda facce quadrangolari con quattro vertici distinti
e il passo di cancellazione/soppressione ammissibile. Nei casi ordinari
senza archi paralleli incidenti agli estremi, ciascun vertice soppresso ha
due vicini distinti: la fusione non produce un loop. Cancellazione e
soppressione preservano la planarità dell'embedding; la connessione si
conserva cancellando un arco non ponte. La colorazione propria ottenuta
è anche una verifica dell'assenza di ponti: ogni arco di un grafo cubico
propriamente 3-colorato appartiene a un ciclo bicolore. La gestione keyed
generale dei casi degeneri non è implementata né certificata da questi test.

Il risultato è **condizionato a una colorazione già nota**. Non risolve il
problema di costruirla a partire da un grafo non colorato.

## Esempi espliciti

I nomi dei colori nei test sono `red`, `green`, `blue`. Ciascuna delle cinque
trasformazioni qui sotto è ripetuta con tutte le sei permutazioni dei colori.

### F2: due digoni connessi, quattro vertici

Archi iniziali: 0–1 rosso e blu, 2–3 rosso e blu, 0–2 verde, 1–3 verde.
Rimuovere il digono 0–1 e i suoi vertici; i due archi verdi si fondono in
un terzo arco 2–3 verde. Risultato: theta su 2 e 3, con un arco per colore.
L'inverso manuale seleziona proprio il nuovo arco verde, non il primo arco
parallelo trovato. Nessuno scambio cromatico.

### F3: tetraedro, quattro vertici

Triangolo: 0–1 blu, 1–2 verde, 2–0 rosso. Archi esterni:
0–3 verde, 1–3 rosso, 2–3 blu.

Eliminare 0–1 blu; scambiare rosso/verde sul cammino 0–2–1. Si ottengono
due archi fusi 2–3, uno verde e uno rosso, oltre al blu già presente.
Il vicino esterno coincide nei due estremi (è 3), ma le due fusioni non
devono essere confuse. L'inverso tramite `apply_half_kempe_loop_color_switching()`
recupera il multinsieme degli archi colorati del tetraedro iniziale.

### F4 a tre colori: cubo già preparato, otto vertici

Le due basi del prisma sono 0–1–2–3–0 e 4–5–6–7–4; le verticali sono i–(i+4).
Entrambe le basi hanno parola blu, verde, rosso, verde; le verticali hanno
colori rosso, rosso, blu, blu, rispettivamente per i=0,1,2,3.

Eliminare 0–1 blu e scambiare verde/rosso sul cammino 0–3–2–1. Le fusioni
sono 3–4 rosso e 2–5 rosso; il lato 2–3 diventa verde. Rimangono sei
vertici, nove archi e cinque facce. L'inverso ripristina tutti i colori.

### F4 a due colori, cicli distinti: cubo standard

Le due basi hanno entrambe parola rosso, verde, rosso, verde; le quattro
verticali sono blu. I cicli rosso/blu contenenti i due lati rossi del
quadrato sono 0–1–5–4–0 e 2–3–7–6–2, quindi distinti.

Scambiare rosso/blu sul primo ciclo, di quattro archi: si ottiene esattamente
il cubo a tre colori appena descritto. Poi applicare la sua riduzione.
Per il ritorno esatto servono, in ordine, l'inverso locale e l'inverso dello
scambio completo. Omettere l'ultimo scambio non recupererebbe i colori
originali, pur lasciando una colorazione propria.

### F4 a due colori, stesso ciclo: cambiare solo la base inferiore

La base superiore è ancora rosso, verde, rosso, verde; quella inferiore è
verde, rosso, verde, rosso. Le verticali sono ancora blu. I lati rossi
superiori stanno ora sullo stesso ciclo rosso/blu:
0–1–5–6–2–3–7–4–0.

Eliminare il lato verde 1–2 e scambiare rosso/blu sul cammino
1–0–4–7–3–2, lungo cinque archi. Le fusioni sono 0–5 blu e 3–6 blu.
Nessuno scambio preliminare; anche questo inverso recupera tutti i colori.

I due cubi hanno **la stessa struttura e gli stessi colori sul quadrato
superiore**, ma diversa connessione bicolore nel resto della mappa. Per
decidere questo sottocaso non basta guardare soltanto il bordo colorato.

## Copertura e risultati riproducibili della Task 1

La tabella seguente conserva i limiti alla chiusura della Task 1; gli
avanzamenti delle Task 2–3 sono riportati nell’aggiornamento successivo.

| Famiglia | Costruzione studiata | Test / esempio | Limite ancora aperto |
| --- | --- | --- | --- |
| F2 | Fusione degli archi esterni dello stesso colore; nessuno scambio | Due digoni → theta; 6 permutazioni | Certificato con identità persistenti delle occorrenze |
| F3 | Scambio sul cammino dei due lati complementari | Tetraedro → theta; 6 permutazioni | Applicazione automatica a stati arbitrari |
| F4, tre colori | Scegliere un lato di colore singolo; cammino di 3 lati | Cubo preparato; 6 permutazioni | Non copre automaticamente qualunque lato ripetuto |
| F4, due colori / cicli distinti | Uno scambio completo, poi il caso precedente | Cubo standard; 6 permutazioni | Registrazione persistente dei due scambi nell'ordine corretto |
| F4, due colori / stesso ciclo | Scegliere un lato dell'altro colore; cammino complementare | Cubo con base inferiore ricolorata; 6 permutazioni | Lunghezza del cammino potenzialmente non locale |

Sono disponibili otto fixture valide: theta, F2, F3, tre casi F4 e due
scelte sulla stessa piccola mappa a prisma pentagonale. Il prisma pentagonale
ha dieci vertici: le due basi hanno parola blu, verde, rosso, blu, verde,
con verticali rosso, rosso, blu, verde, rosso. La scelta 2–3 supera il criterio
complementare, la scelta 0–1 no. Sono fixture di confine per le prossime
Task, non nuove prove di trasformazioni F5 in questo passo.

Comandi da `ct/`:

```bash
uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_reduction.py -k fixtures -q
uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_reduction.py -q
uv run --python ../.venv/bin/python python -m pytest tests -q
```

Esecuzioni del 28 settembre 2026: **8 test delle fixture superati**, **45 test
del nuovo file superati**, **143 test complessivi superati**. La suite di
partenza conteneva 98 test, anch'essi verificati prima delle modifiche.

I test controllano:

- correttezza dei piccoli input, versi/colore degli archi, chiusura delle
  facce, rotazione a tre archi a ogni vertice e relazione di Eulero;
- connessione complementare dei due sottocasi F4 e delle due scelte F5;
- 30 andate/ritorni manualmente specificati: 5 trasformazioni × 6 rinomine;
- conteggi V−2/E−3/F−1, colorazione propria, connessione, assenza di loop e
  ponti, confronto delle occorrenze strutturali con `join_faces()` e
  `remove_vertex_from_face()`, validità del nuovo `FaceIndex`;
- uguaglianza del multinsieme degli archi colorati e dei vertici dopo il
  ritorno, e arresto del riduttore esistente quando l'input è già theta.

Non sono test di un motore di scoperta automatica del passo: cammini e
fusioni sono scritti esplicitamente, con risultati attesi indipendenti.
Non si dichiara ancora un replay di ID NetworkX, patch di facce colorate o
certificati serializzati. Non sono state eseguite catene sulle mappe grandi,
ricerche tra rami o verifiche massive dei loro colori originali.

## Aggiornamento Task 3: passi scoperti e certificati automaticamente

La Task 2 ha introdotto ID persistenti, occorrenze keyed e applicazione/
inversione atomiche. La Task 3 aggiunge `plan_step(state, candidate)` in
`ct/experiments/oracle_reduction.py`: produce un certificato per il lato
richiesto senza modificare lo stato. I contratti e il trattamento degli
indici sono descritti nella [documentazione canonica](../architecture.md#prototipo-sperimentale-delloracolo).

Le costruzioni sono ora verificate con **36 riduzioni automatiche**: sei
casi (F2, F3, tre casi F4 e F5) per tutte le sei permutazioni dei colori.
I test confrontano il risultato con multinsiemi colorati derivati a mano,
verificano V−2/E−3/F−1, embedding, indice e ritorno esatto dello snapshot,
inclusi ID delle facce/archi, occorrenze, ordine e contatori. La pianificazione
ripetuta restituisce lo stesso certificato e conserva anche gli oggetti
grafo/liste/indice del chiamante.

| Caso | Scambi scoperti nella fixture | Esito automatico |
| --- | --- | --- |
| F2, due digoni | Nessuno | Theta, un nuovo arco verde e due archi originali distinti |
| F3, tetraedro | Cammino di 2 archi | Theta; vicini esterni coincidenti e tre ID distinti |
| F4 a tre colori | Cammino di 3 archi | Risultato del cubo preparato descritto sopra |
| F4 a due colori, cicli distinti | Ciclo di 4 archi, poi cammino di 3 | Stesso cubo ridotto; ricolorazione remota registrata |
| F4 a due colori, stesso ciclo | Cammino di 5 archi | Testimone esterno al quadrato, nessuno scambio preliminare |
| F5, lato 2–3 del prisma | Cammino 2–1–0–4–3 di 4 archi | Fusioni 1–7 blu e 4–8 verde; ritorno esatto |
| F5, lato 0–1 dello stesso prisma | Nessuno disponibile col criterio diretto | `no_witness`, nessuna sostituzione della candidata |

Un'ulteriore fixture espande il lato rosso 4–7 del cubo `f4_same_cycle` in
4–8 rosso, due archi 8–9 blu/verde, 9–7 rosso. Il cammino complementare
rosso/blu attraversa soltanto l'ID blu fra 8 e 9: diventa rosso mentre l'ID
verde resta verde. Questo verifica un cammino con paralleli già nell'input,
oltre ai paralleli prodotti dalle riduzioni F2/F3. Anche questa fixture
supera gli invarianti iniziali e il ritorno completo.

Sono verificati anche theta terminale, ID mancanti o non incidenti, faccia
fuori da F2–F5 e candidata che produrrebbe loop. F2 aggiorna la stessa terza
faccia alle due soppressioni; F3 gestisce i vicini esterni coincidenti.
Le facce risultanti uguali per valore restano distinte e `FaceIndex.validate()`
riesce sia dopo l'applicazione sia dopo l'inverso.

Diagnostica aggiuntiva sui sette stati distinti delle fixture: **132 candidate
orientate provate singolarmente**, di cui 86 certificate con apply/undo,
32 `no_witness`, 8 `structurally_rejected` e 6 `unsupported_case` su theta.
Ogni prova riparte dallo stato identico: questo controllo non è una catena.

### Evidenza di esecuzione

RED iniziale: **46 nuovi fallimenti** dovuti a `plan_step()` assente, mentre
i 72 test precedenti passavano. Dopo l'implementazione: **118 test dell'oracolo
e 216 test complessivi superati**, usando Python 3.9. Lo smoke S1 da 10 facce
ha completato sette riduzioni fino a theta e ricostruito 16 vertici e 24 archi,
superando il controllo finale di colorazione del programma.

La revisione indipendente non ha rilevato problemi azionabili e ha ripetuto
la suite completa (216 PASS). Ha inoltre controllato tutte le candidate delle
fixture con inversione dell'embedding e rotazioni cicliche delle facce:
832 passi certificati con ritorno esatto, 448 `no_witness`, 64 rifiuti
strutturali e 24 risposte terminali `unsupported_case`. Questi controlli
restano su piccoli stati singoli; non ampliano la conclusione alle catene.

Comandi eseguiti da `ct/` (la cache temporanea evita il divieto di scrittura
nella cache utente imposto dal sandbox):

```bash
UV_CACHE_DIR=/private/tmp/4ct-oracle-uv-cache uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_reduction.py -q
UV_CACHE_DIR=/private/tmp/4ct-oracle-uv-cache uv run --python ../.venv/bin/python python -m pytest tests -q
UV_CACHE_DIR=/private/tmp/4ct-oracle-uv-cache uv run --python ../.venv/bin/python python 4ct.py -s1 -r2 10
```

I log della sessione sono nella directory ignorata
`.superpowers/sdd/2026-09-28-oracle-reduction-study/` (`task-3-red.log`,
`task-3-green.log`, `task-3-tests.log`, `task-3-smoke.log`). Non sono necessari
per rieseguire i test: tutte le fixture piccole sono nel file dei test.

### Precondizioni e limiti residui

- Lo stato sorgente deve essere un embedding sferico connesso, cubico,
  senza loop/ponti e propriamente colorato. La corruzione degli invarianti
  resta un errore software; non viene riclassificata come candidata negativa.
- Per F3–F5 la soppressione deve avere vicini sopravvissuti distinti a ogni
  estremo. Le scelte che produrrebbero loop, disconnessione o ponti sono
  rifiutate prima degli scambi. Gli archi paralleli richiedono la scelta
  corretta: un lato esterno al digono non equivale al passo F2 dedicato.
- La ricerca è limitata alle costruzioni studiate: F5 non prova altri cicli
  preliminari; F4 ne prova al massimo uno. `no_witness` riguarda questa
  candidata e questa costruzione, non tutte le scelte della faccia o del ramo.
- Cammini e cicli possono uscire dal vicinato locale. Il costo include copie,
  controlli globali e nuove impronte; non è stato misurato su mappe grandi.
- Nessuna catena, persistenza JSON o ricostruzione ordinaria guidata dallo
  stack dell'oracolo è stata eseguita. Nessuna lettura o validazione delle
  151 mappe. I risultati sui casi piccoli non dimostrano la copertura
  universale degli stati intermedi né il teorema dei quattro colori.

## Aggiornamento Task 4: catene, persistenza e replay su piccole mappe

Data: 28 settembre 2026. Ambito della nuova sessione: **soltanto Task 4**.
La baseline dei Task 1–3 è stata verificata nuovamente: **216 test PASS**.
Nessuna riga della raccolta da 151 mappe è stata letta o rivalidata.

### Comportamento implementato

`run_chain()` concatena i passi certificati in ordine F2/F3/F4/F5, poi ID
della faccia e dell'arco. In ogni F5 anticipa il lato del colore unico:
questa scelta dipende esplicitamente dall'oracolo. Dopo un rifiuto prova le
altre candidate; non esplora altri rami e non aggiunge scambi casuali.
Theta viene controllato prima del limite di passi, incluso il caso iniziale
con zero passi. `step_limit` e `no_certified_candidate` sono arresti non
conclusivi; nell'ultimo caso conserva candidate, stati e motivazioni.

`replay_exact()` opera su una copia ricostruita dello stato e inverte i
certificati in ordine LIFO. I test confrontano snapshot completi: vertici,
archi keyed/colori/molteplicità, facce/occorrenze/ID/ordine e contatori.
I colori effettivi di theta sono conservati, anche dopo permutazione dei
tre colori. Un errore di replay non modifica il terminale del chiamante.

Il runner separato `experiments/oracle_reduction_run.py` salva schema 1:
`manifest.json`, `terminal.json`, `steps.jsonl`. Contiene un solo stato
terminale e certificati a differenze, con scambi ordinati. Il loader
ricostruisce `FaceIndex` e gli ID, controlla hash/conteggi/continuità e
rifiuta file incompleti o corrotti. Non serializza indirizzi Python.
La destinazione popolata non viene sovrascritta; il manifest è scritto
per ultimo. Provenienza e CLI sono documentati in
[architettura](../architecture.md#prototipo-sperimentale-delloracolo) e
[sviluppo](../development.md#catene-sperimentali-delloracolo).

La ricostruzione ordinaria riceve solo copie dell'embedding strutturale e
dei record Arianna, con budget Kempe esplicito, dopo `theta_reached`.
I confronti comprendono vertici e multinsieme degli archi, colorazione
propria e stack consumato; i colori possono differire dall'oracolo.
Su un prefisso l'esito è `not_run_nonterminal`. `KempeSearchExhausted` resta
non conclusivo; un errore inatteso viene registrato e rilanciato, preservando
i certificati già prodotti. Nessuna modifica alla pipeline principale.

### Evidenza su piccoli casi

- 48 prove parametrizzate di catena completa: otto casi (sette embedding
  distinti, perché le due candidate F5 condividono l'input) per le sei
  permutazioni cromatiche, incluso theta a zero passi.
- Test dei limiti 0/1/2, ordine deterministico, prosecuzione dopo un rifiuto,
  corruzione fatale degli invarianti e replay errato senza mutazioni.
- Salvataggio/lettura JSON di theta, F2, catena F4 con scambio preliminare
  completo e prefisso non terminale. Controllati schema ignoto, file
  mancante/troncato, colori alterati e falso stato `theta_reached`.
- La CLI seleziona una sola riga da un file di test con altre righe non JSON;
  un processo nuovo verifica replay, SHA-256 della sorgente e multinsieme
  keyed/colorato. Una sorgente cambiata viene rifiutata.
- Ricostruzione ordinaria reale su theta, F2, F3, due colorazioni del cubo,
  prisma pentagonale e dodecaedro, separata da terminale e certificati.
- L'arresto `no_certified_candidate` è testato iniettando esiti negativi
  del pianificatore: **non è stato trovato un controesempio reale** su cui
  tutte le candidate siano prive di testimone.

È aggiunto il piccolo input riproducibile
`ct/examples/planar/oracle-study-dodecahedron.colored.planar`: 20 vertici,
30 archi, 12 F5; colori alternati sul ciclo 0–1–…–19–0 e blu sui rimanenti
archi. Non appartiene alla raccolta da 151 mappe.

| Esecuzione sul dodecaedro | Completa | Prefisso |
| --- | --- | --- |
| Budget riduzioni | 9 | 2 |
| Stato finale | `theta_reached` | `step_limit` |
| V/E/F terminali | 2/3/3 | 16/24/10 |
| Riduzioni F2/F3/F4/F5 | 0/2/6/1 | 0/0/1/1 |
| Scambi completi/parziali | 0/9 | 0/2 |
| Replay in processo nuovo | Esatto | Esatto |
| Ordinario | Successo, 20 vertici/30 archi e topologia originale | `not_run_nonterminal` |
| Budget Kempe per F5 | 10000 | 100 (non usato) |

La corsa completa ha impiegato circa **0,016 s nella sola catena** su questa
macchina; non è un benchmark delle mappe grandi. Il manifest contiene
Python 3.9.6, NetworkX 3.2.1, HEAD `08dd2e9` e hash del codice non committato.
SHA-256 della riga piccola (inclusa newline):
`80fbcc94111b125570e0d50187b196aabab5ea06c4f1bca48666af6c67b7d4c7`.

### Comandi, artefatti e revisione

Comandi realmente eseguiti da `ct/`, con cache temporanea nel sandbox:

```bash
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_reduction.py -q
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests -q
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python 4ct.py -s1 -r2 10
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --input examples/planar/oracle-study-dodecahedron.colored.planar --map-number 1 --max-steps 9 --output debug/oracle-study/task4-dodecahedron-001 --ordinary-rebuild --kempe-search-limit 10000
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --replay debug/oracle-study/task4-dodecahedron-001
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --input examples/planar/oracle-study-dodecahedron.colored.planar --map-number 1 --max-steps 2 --output debug/oracle-study/task4-dodecahedron-prefix-001 --ordinary-rebuild --kempe-search-limit 100
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --replay debug/oracle-study/task4-dodecahedron-prefix-001
```

RED iniziale: 57 test delle nuove API fallenti, 17 errori per runner assente
più 7 errori del confronto ordinario, eseguito separatamente. Il primo GREEN
ha evidenziato una fixture non valida: `deepcopy(OracleState)` conserva gli
indirizzi nelle chiavi di `FaceIndex`; il test ora crea un secondo stato
tramite `make_state()`. Non è stato cambiato il contratto del motore.
Dopo la correzione: 199 test dedicati e 297 complessivi PASS. Aggiunti poi
due controlli sul dodecaedro e sul replay fallito, entrambi PASS; risultato
finale: **201 test dedicati, 299 complessivi PASS**. Smoke S1 da 10 facce
completato con sette riduzioni e ricostruzione valida (16 vertici/24 archi).

Revisione indipendente: nessun problema azionabile; suite da 297 test
rieseguita e altre **96 catene piccole**, con embedding invertiti e bordi
ruotati, arrivate a theta con salvataggio/lettura JSON e ritorno esatto.
Gli ultimi due test di copertura e la documentazione sono verificati
dall'esecutore; nessuna modifica al codice dopo la revisione.

Conservare per il replay le intere directory ignorate:

- `ct/debug/oracle-study/task4-dodecahedron-001/`;
- `ct/debug/oracle-study/task4-dodecahedron-prefix-001/`.

Si rigenerano con i comandi sopra scegliendo nomi di output nuovi. La piccola
sorgente è nel repository; i log RED/GREEN, lo smoke e le copie prima delle
modifiche sono in `.superpowers/sdd/2026-09-28-oracle-reduction-study/`.
Nessun commit creato; conservare anche i file non tracciati nelle riprese.

### Limiti e decisioni della Task 4

Si continua nel checkout feature esistente per preservare il lavoro locale:
nessuna nuova worktree o integrazione del branch. I salvataggi interrotti
possono lasciare una directory parziale, rifiutata dal loader, da conservare
o gestire esplicitamente prima di una nuova corsa. Gli hash verificano
integrità e consistenza, non autenticità contro la riscrittura intenzionale
del manifest. Il replay riguarda lo stato semantico definito, non eventuali
attributi NetworkX arbitrari aggiunti dal chiamante.

Restano esclusi validità del dataset, costo sulle mappe grandi e completezza
matematica universale. Le copie temporanee e i controlli globali possono
costare molto; prima della corsa grande serve misurare il prefisso previsto
nella Task 5. Le catene qui osservate non dimostrano il teorema né l'esistenza
di un ramo per tutti gli stati intermedi.

## Prossimo passo

**Task 4 completata. Aggiornamento Task 5, 28 settembre 2026:** eseguiti
20 passi sulla sola riga 1 (10 F4, 10 F5), con invarianti e replay esatto
anche in processo nuovo. La catena ha richiesto 199,83 s; il replay
separato 92,32 s e un picco RSS di 235,06 MiB. La profilazione individua
la costruzione ripetuta di `FaceIndex` come costo dominante.

Su indicazione dell'autore, è documentato prima l'ostacolo prestazionale:
**catena completa e confronto ordinario sulla mappa grande restano aperti**.
299 test e smoke S1 nuovamente superati; nessun codice modificato, nessuna
altra mappa avviata o validazione massiva ripetuta. Risultati, comandi,
artefatti e prossimo passo nel [resoconto step-3](4ct-oracle-study-step-3.md).
Il successivo intervento approvato sulla costruzione lineare di `FaceIndex`
è ora verificato: 308 test e smoke PASS, stesso prefisso da 199,83 a 59,15 s,
replay da 92,32 a 21,16 s; certificati e terminale identici byte per byte.
La successiva profilazione ha individuato il controllo dei ponti come
bersaglio circoscritto: sostituito con visita iterativa sul multigrafo,
senza togliere invarianti. Il prefisso scende ancora a **51,81 s**, il
replay a **17,41 s**, con certificati/terminale identici. **321 test**, smoke
e revisione indipendente di entrambe le ottimizzazioni superati.
Su ulteriore richiesta, implementato anche il riuso delle verifiche con
istantanea esatta e invalidazione delle mutazioni pubbliche: **354 test**,
smoke e revisione superati. Prefisso **36,13 s**, replay **13,01 s**;
certificati/terminale identici, ma picchi RSS saliti a **470,08/363,34 MiB**.
La diagnosi successiva localizza il maggiore RSS soprattutto in regioni
native vuote ma residenti (`MALLOC_LARGE (empty)`), con snapshot vivi e
numero di stati stabili. La compressione lossless, provata solo nel
diagnostico, riduce il picco del replay strumentato **368,33→213,75 MiB**
con esito esatto. Il prossimo passo è implementare e verificare questa
rappresentazione, inclusi nuovo prefisso forward e replay. La catena completa
resta aperta; nessuna corsa lunga o altra mappa avviata. Dettagli e comandi
nell'ultimo aggiornamento di step-3.
