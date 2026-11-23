# Studio dell'oracolo — Task 5, prima mappa grande

Data: 28 settembre 2026. Esecuzione inline di Superpowers, limitata alla
Task 5 del [piano](../superpowers/plans/2026-09-28-oracle-reduction-study.md).
Task 1–4 già completate; nessuna nuova validazione delle 151 mappe.

## Stato dell'indagine

**Ultimo aggiornamento, 29 settembre 2026: istantanee serializzate per
componenti, implementate con TDD.** Il buffer non compresso dell'intero
stato è sostituito da buffer per componente dentro un unico flusso zlib.
Suite **356 PASS**, smoke S1 PASS, certificati e terminale identici ai cinque
prefissi precedenti, replay interno e in nuovo processo esatti.

Sulla CLI della riga 1, sempre con 20 riduzioni, picco RSS **397,66→311,75
MiB (−21,60%)**, tempo **50,15→54,49 s**; replay separato **214,25→219,38
MiB**, **12,92→13,80 s**. È un compromesso memoria/tempo da singole corse:
la memoria dell'andata aumenta e nessuna catena lunga è stata eseguita.
Task 5 e confronto ordinario restano aperti. Dettagli, diagnosi e comandi
nell'[aggiornamento sui buffer](#aggiornamento-istantanee-serializzate-per-componenti).

Le sezioni seguenti conservano in ordine la **diagnosi iniziale** e i vari
interventi successivi, ciascuno con hash del codice e misure di quel momento.
Il prefisso di 20 passi sulla sola riga 1 è stato salvato come `step_limit`,
con invarianti verificati e ritorno esatto anche in un processo nuovo.
È isolato un ostacolo prestazionale riproducibile nella costruzione di
`FaceIndex`. **La corsa completa con budget 10.000 non è stata avviata**:
restano aperti il ramo fino a theta e il confronto ordinario sulla mappa
grande. È completata la diagnosi del prefisso, non il traguardo completo.
Questo prefisso non certifica un ramo completo né un'impossibilità matematica.

## Configurazione e provenienza

- Input: `ct/maps_3000_maps_of_8000_faces.colored.planar`, sola riga fisica 1.
- SHA-256 della riga, inclusa newline:
  `41e6b1a2c7e4f84d0be13a036522797b68312ee200bb2f58c9e0c7e0208f31f2`.
- Conteggi iniziali effettivi V/E/F: **16.064 / 24.096 / 8.034**.
  Riduzioni necessarie fino a theta: `(16064 - 2) // 2 = 8031`.
- Python 3.9.6, NetworkX 3.2.1; branch `feature/machine-learning`;
  HEAD `08dd2e911d25a35f2c32320403f90020ba5a7e01`.
- Budget del prefisso: 20; confronto ordinario richiesto con budget Kempe
  10.000, ma eseguito solo se si raggiunge theta.
- Politica deterministica F2/F3/F4/F5, poi ID; priorità al lato del colore
  unico nelle F5. È una politica che consulta l'oracolo.

Impronte del codice locale registrate dal manifest:

| File | SHA-256 |
| --- | --- |
| `ct/4ct.py` | `58002e608591f071defa7b82c6998a330cf330d2e831ea1277216429255eae46` |
| `ct/ct_graph_utils.py` | `6775a1fbb5afeabd87061965569a78a6941770cc4abb1040c05b4b1df208dba0` |
| `ct/experiments/oracle_reduction.py` | `500377b0ae5416e934f36ba8270680da546ebbcd4722e150ed54d9f68d90e22a` |
| `ct/experiments/oracle_reduction_run.py` | `7ca1578eba9985bc7dfc5ce5ebb0a710687604ea814b0aeeb467d612430fe9df` |

## Prefisso di 20 passi

| Misura | Risultato |
| --- | --- |
| Stato | `step_limit`, arresto non conclusivo |
| Profondità | 20 su 8.031 riduzioni richieste fino a theta |
| V/E/F terminali | 16.024 / 24.036 / 8.014 |
| F2 / F3 / F4 / F5 | 0 / 0 / 10 / 10 |
| Scambi completi / parziali | 0 / 20 |
| Archi percorsi negli scambi parziali | 1.607 in totale; minimo 3, mediana 4, massimo 1.519, media 80,35 |
| Sola catena (`perf_counter`) | 199,826821541 s; media 9,991341077 s/passo |
| CLI completa, inclusi replay interno e salvataggio | 301,68 s reali; 298,30 s user; 2,72 s sys |
| Memoria residente campionata durante la CLI | 208.224–227.120 KiB (203,34–221,80 MiB); non è una misura del picco |
| Replay interno | Esatto |
| Replay in processo nuovo | Esatto, sorgente e multinsieme keyed/colorato coincidenti; exit 0 |
| Tempo del replay separato | 92,32 s reali; 91,01 s user; 0,94 s sys |
| Picco RSS del replay separato | 246.480.896 byte = 235,06 MiB; zero swap riportati |
| Ordinario | `not_run_nonterminal` |

Le lunghezze dei 20 cammini, nell'ordine, sono
`4,14,4,3,3,4,3,13,4,4,3,1519,4,4,3,4,4,4,3,3`.
Il cammino lungo è al passo 12. Un passo non è necessariamente una modifica
cromatica limitata al bordo della faccia scelta.

Il motore verifica cubicità, colori incidenti, assenza di loop/ponti,
occorrenze orientate keyed, rotazioni, Eulero e sincronizzazione di
`FaceIndex` durante pianificazione, applicazione e inversione. Ogni passo
accettato perde esattamente 2 vertici, 3 archi e 1 faccia. Questi controlli
riguardano il percorso selezionato, non una scansione delle altre mappe.

Prima candidata: `face_id=0, edge_id=2`. Ultima candidata certificata:
`face_id=48, edge_id=144`. Impronta del terminale:
`328f9e29cc9bb9e2785171e5e510b2245bfdae5e0f567fb737ce672d8aacc84c`.
Il certificato numero 20 è l'ultima riga di `steps.jsonl`; lo stato completo
è in `terminal.json`. Non c'è una candidata fallita: l'arresto è il limite
richiesto di 20 passi. `rejections=[]` non documenta il numero di tentativi
scartati lungo il percorso, perché il runner conserva i rifiuti soltanto
in caso di blocco finale per `no_certified_candidate`.

Dimensioni: `steps.jsonl` 243.460 byte; `terminal.json` 2.924.150 byte;
`manifest.json` 1.834 byte. SHA-256 dei primi due file:
`22e87b0a050ebbc30ce4203b8e85d650a0fc384783bb898027f441b0b4dcb98a`
e `57e699dd1cf7096c5697d36cf896b6f136b598b7564a1bd56630d4491e135ca2`.

## Comandi e artefatti

Tutti i programmi sono eseguiti da `ct/`. Radice nuova di questa sessione:
`ct/debug/oracle-study/task5-map-001-20260928-n_j6eb82/`.
I certificati restano ignorati da Git; conservarne le directory intere.

Comandi effettivamente eseguiti:

```bash
/usr/bin/time -l env UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --input maps_3000_maps_of_8000_faces.colored.planar --map-number 1 --max-steps 20 --output debug/oracle-study/task5-map-001-20260928-n_j6eb82/prefix-20 --ordinary-rebuild --kempe-search-limit 10000 > debug/oracle-study/task5-map-001-20260928-n_j6eb82/prefix.stdout.log 2> debug/oracle-study/task5-map-001-20260928-n_j6eb82/prefix.stderr-time.log
/usr/bin/time -l env UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --replay debug/oracle-study/task5-map-001-20260928-n_j6eb82/prefix-20 > debug/oracle-study/task5-map-001-20260928-n_j6eb82/replay.stdout.log 2> debug/oracle-study/task5-map-001-20260928-n_j6eb82/replay.stderr-time.log
python3 debug/oracle-study/task5-map-001-20260928-n_j6eb82/summarize_run.py debug/oracle-study/task5-map-001-20260928-n_j6eb82/prefix-20 > debug/oracle-study/task5-map-001-20260928-n_j6eb82/prefix-summary.json
```

Il primo `/usr/bin/time -l` ha stampato i tempi, ma il sandbox ha negato
`sysctl kern.clockrate`: il wrapper ha restituito 1 senza poter stampare
il picco RSS. La CLI ha prodotto manifest e riepilogo esatto; il codice 1
del wrapper non viene attribuito a un errore dell'oracolo. Per il replay
il medesimo strumento è stato autorizzato fuori dal sandbox. Le misure RSS
del prefisso provengono da `ps`, con valori espressi in KiB su macOS.

I file locali preesistenti sono copiati e improntati in `before/` e
`before-sha256.json`; i file top-level preesistenti di `ct/debug/` sono
conservati in `debug-before/` con impronte separate. Nessun commit creato.

## Ostacolo prestazionale e decisione sulla corsa completa

Per separare il costo degli scambi dai controlli globali è stata profilata
la stessa CLI su **un solo passo della stessa riga 1**. Nessuna nuova
mappa, modifica del motore, disattivazione di assert o ottimizzazione.
La corsa diagnostica riuscita ha ottenuto `step_limit`, una F5, un cammino
di quattro archi, replay interno esatto e `not_run_nonterminal`.

| Misura della CLI sotto cProfile | Risultato |
| --- | --- |
| Tempo reale / user / sys | 44,24 / 43,74 / 0,42 s |
| Picco RSS | 283.164.672 byte = 270,05 MiB |
| Tempo totale registrato da cProfile | 44,124 s |
| Costruzioni di `FaceIndex` | 15, per 35,906 s cumulativi, circa 81,4% del totale profilato |
| `FaceIndex._insert_ordered()` | 1.566.166 chiamate, 35,428 s cumulativi |
| `assert_state_invariants()` | 9 chiamate, 27,131 s cumulativi |
| Chiamate complessive registrate | 684.572.738 |

I tempi cumulativi si sovrappongono e non vanno sommati. cProfile aggiunge
overhead: il riferimento per il costo reale resta il prefisso **senza**
profilazione, non il tempo di questa prova a un passo.

La causa osservata è nel percorso
`OracleState/assert_state_invariants → FaceIndex → rebuild → index_face →
_insert_ordered`. `rebuild()` ripassa le facce in ordine e, per ciascuna,
`_insert_ordered()` scansiona il bucket delle facce della medesima taglia:
prima cerca duplicati per identità, poi cerca la posizione. Un bucket di
`k` facce richiede quindi un numero quadratico di visite durante la sua
costruzione. Il prototipo ricostruisce tali indici nelle copie temporanee e
anche per controllare la coerenza dell'indice esistente. La profilazione
conferma che questo costo domina già un passo F5 con un cammino molto corto.
Non è stata misurata una crescita patologica della memoria.

La proiezione a costo costante dei 20 passi è **22,29 ore per la sola
riduzione** (`199,826821541 / 20 × 8031 / 3600`). Un modello illustrativo
in cui il costo per passo cali quadraticamente con la dimensione darebbe
circa 7,43 ore; **nessuna delle due cifre è una previsione verificata o un
limite garantito**. Cambiano distribuzione delle facce, cammini e tentativi
scartati. Vanno inoltre aggiunti replay interno, replay in processo nuovo,
salvataggio e ricostruzione ordinaria. Le prestazioni e la memoria di una
catena completa restano non misurate.

**Decisione dell'autore dopo le misure:** «Isola e documenta prima
l'ostacolo prestazionale». Si usa quindi l'esito diagnostico consentito
dal criterio di uscita del piano, conservando il prefisso e lasciando la
checkbox della catena completa aperta. Il rinvio del comando a 10.000 passi
segue questa indicazione esplicita; non è un arresto automatico del motore
né un nuovo budget matematico. Il costo della decisione è che non è
disponibile alcuna evidenza su theta o sull'ordinario di questa mappa.
Non è stata avviata alcuna altra mappa.

### Errore del primo comando di profilazione

Il primo comando ha passato a `python -m cProfile` il percorso relativo
`experiments/oracle_reduction_run.py`. Dopo riduzione e replay interni,
la raccolta di provenienza ha sollevato `ValueError` a riga 262 del runner:
`Path(__file__)` era relativo, mentre `CT.parent` era assoluto. Non è stato
salvato un run utilizzabile; il file pstats e il traceback sono conservati.
È un **errore software nel percorso di provenienza sotto questo modo di
invocazione**, non `no_witness` e non impossibilità matematica.

Il medesimo esperimento con percorso assoluto del runner è terminato con
exit 0 e ha salvato tutti gli artefatti. Nessuna correzione al codice in
questa Task 5. Il caso relativo resta da proteggere con un test se si decide
di supportare stabilmente tale invocazione del profiler.

Ulteriori comandi effettivamente eseguiti da `ct/`:

```bash
/usr/bin/time -l env UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m cProfile -o debug/oracle-study/task5-map-001-20260928-n_j6eb82/profile-one-step.pstats experiments/oracle_reduction_run.py --input maps_3000_maps_of_8000_faces.colored.planar --map-number 1 --max-steps 1 --output debug/oracle-study/task5-map-001-20260928-n_j6eb82/profile-one-step --ordinary-rebuild --kempe-search-limit 10000 > debug/oracle-study/task5-map-001-20260928-n_j6eb82/profile.stdout.log 2> debug/oracle-study/task5-map-001-20260928-n_j6eb82/profile.stderr-time.log
/usr/bin/time -l env UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m cProfile -o debug/oracle-study/task5-map-001-20260928-n_j6eb82/profile-one-step-absolute.pstats /Users/mario.stefanutti/mario/programming/github-stefanutti/maps-coloring-python/ct/experiments/oracle_reduction_run.py --input maps_3000_maps_of_8000_faces.colored.planar --map-number 1 --max-steps 1 --output debug/oracle-study/task5-map-001-20260928-n_j6eb82/profile-one-step-absolute --ordinary-rebuild --kempe-search-limit 10000 > debug/oracle-study/task5-map-001-20260928-n_j6eb82/profile-absolute.stdout.log 2> debug/oracle-study/task5-map-001-20260928-n_j6eb82/profile-absolute.stderr-time.log
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests -q > debug/oracle-study/task5-map-001-20260928-n_j6eb82/tests.log 2>&1
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python 4ct.py -s1 -r2 10 > debug/oracle-study/task5-map-001-20260928-n_j6eb82/smoke-s1.log 2>&1
```

Per leggere il profilo senza rilanciare esperimenti:

```bash
../.venv/bin/python - <<'PY'
import pstats
pstats.Stats('debug/oracle-study/task5-map-001-20260928-n_j6eb82/profile-one-step-absolute.pstats').strip_dirs().sort_stats('cumtime').print_stats(25)
PY
```

Gli estratti realmente letti sono anche salvati nei file
`profile-one-step.txt` e `profile-one-step-absolute.txt` della sessione.
Per rigenerare, scegliere una radice nuova e sostituirla in ogni comando;
il runner rifiuta output già popolati. Il profilo fallito non ha creato
`profile-one-step/`; non usarlo come run da rigiocare.

## Verifiche, classificazione e prossimo passo

Verifica fresca: **299 test PASS in 1,19 s**, comprendenti i 201 test
dell'oracolo. Smoke S1 `-r2 10`: exit 0, sette riduzioni, theta e
ricostruzione valida con 16 vertici e 24 archi. I due file di debug a nome
fisso modificati dallo smoke sono stati copiati in
`verification-generated-debug/` e ripristinati ai byte precedenti;
`debug-preservation.json` registra l'operazione.

Revisione indipendente in sola lettura: nessun rilievo azionabile. Sono
stati confrontati resoconto, manifest, certificati, log, profilo e impronte
di conservazione; nessun test o esperimento rilanciato dal revisore.
Il certificato della prova profilata coincide con il primo del prefisso.
Codice, test e tutti i file locali precedenti restano invariati, salvo
gli aggiornamenti intenzionali al piano e al punto di ripresa del
resoconto step-2; il resoconto step-3 è nuovo. Non viene riaperta la revisione
delle Task 1–4, né attribuita copertura alla catena completa non eseguita.

| Evento | Classificazione |
| --- | --- |
| Prefisso fermato dopo 20 passi | `step_limit`: non conclusivo, budget esplicito esaurito |
| Confronto ordinario sul prefisso | `not_run_nonterminal`: non eseguito, non fallito |
| Mancata corsa completa | Decisione operativa per costo misurato; non un risultato del motore |
| `sysctl` negato a `/usr/bin/time` | Limitazione dello strumento nel sandbox |
| `ValueError` con cProfile/percorso relativo | Errore software di provenienza, aggirato con percorso assoluto |
| Violazioni di invarianti o replay sul prefisso | Nessuna osservata |
| Impossibilità matematica | Non stabilita; nessun controesempio trovato |

Il prossimo passo concreto è progettare un intervento prestazionale
mirato alla costruzione degli indici prima di riprendere la catena completa
della **stessa Task 5**. L'intervento non è implementato in questa sessione. Un'eventuale ottimizzazione deve mantenere identità delle
facce, ordine dei bucket, atomicità, controlli globali e replay esatto,
con regressioni specifiche e nuova misura dello stesso prefisso.
Il comando completo nel piano resta **da eseguire**, seguito da replay in
processo nuovo e confronto ordinario separato. Nessuna fase R1–R5 è avviata.


## Aggiornamento: costruzione lineare di FaceIndex

Dopo la diagnosi, l'autore ha approvato l'intervento circoscritto:
«proviamo con la costruzione lineare». Modifica di produzione limitata a
`FaceIndex.rebuild()` in `ct/4ct.py`. Le facce vengono inserite direttamente
nei bucket seguendo l'ordine di `g_faces`, evitando di riesaminare i membri
precedenti. Semantica, complessità e gestione delle identità sono descritte
nella sezione [FaceIndex dell'architettura](../architecture.md#faceindex).

Nessun cambiamento a scelta delle riduzioni, oracolo, copie transazionali,
invarianti, certificati, inserimento incrementale o validatore indipendente.
L'errore di provenienza con cProfile relativo resta separato e non corretto.
La costruzione lineare migliora il costo dell'indice; non rende lineare
l'intera catena di migliaia di riduzioni.

### Test prima e dopo la modifica

Nuovo `ct/tests/test_face_index.py`, nove test: facce distinte uguali per
valore, archi/vertici ripetuti nella stessa faccia, oggetti faccia ripetuti,
ricostruzione dopo modifiche e lista vuota, reinserimenti incrementali fuori
ordine, rilevamento di bucket corrotti e costo della costruzione.

Prima della modifica: sette test semantici PASS, due regressioni di costo
FAIL. Raddoppiando 128→256 facce, le chiamate registrate dal profiler
crescevano da 37.640 a 140.808 su facce con archi distinti e da 167.688 a
663.048 con archi condivisi. Dopo: **1.288→2.568** in entrambi i casi
(rapporto 1,994). È una regressione deterministica sul lavoro eseguito,
senza soglie temporali dipendenti dalla macchina; usa solo dati sintetici.

GREEN: nove test nuovi PASS in 0,07 s; **308 test complessivi PASS in
1,61 s**, inclusi i 201 dell'oracolo. Smoke S1 `-r2 10`: exit 0, sette
riduzioni e ricostruzione valida con 16 vertici/24 archi.

### Nuova misura sulla stessa riga 1

| Misura | Prima | Costruzione lineare |
| --- | --- | --- |
| Sola catena, 20 passi | 199,826821541 s | 59,153774167 s |
| Media per riduzione | 9,9913 s | 2,9577 s |
| CLI con replay interno e salvataggio | 301,68 s | 86,06 s |
| Replay in processo nuovo | 92,32 s | 21,16 s |
| Picco RSS del replay | 235,06 MiB | 228,06 MiB |
| Picco RSS della CLI | Non disponibile | 275,73 MiB |
| Stato / ordinario | `step_limit` / `not_run_nonterminal` | Uguali |

Accelerazione osservata: **3,38×** sulla riduzione, **3,51×** sulla CLI
completa e **4,36×** sul replay separato. Sono confronti fra singole corse
sulla stessa macchina, non medie statistiche o garanzie per altri stati.
Il picco RSS precedente della CLI non era misurabile nel sandbox; non si
confronta il nuovo picco con i vecchi campioni istantanei di RSS.

Il nuovo replay restituisce `exact_replay=true`, `source_matches=true` e
`edge_multiset_matches=true`. Sono stati confrontati anche i byte dei file:
**`steps.jsonl` e `terminal.json` coincidono esattamente con quelli della
prima prova**. Stessi 20 passi (10 F4/10 F5), scambi, ID, colori e ordine.
Le rispettive impronte rimangono quelle riportate sopra, così come lo
SHA-256 della riga sorgente. Gli invarianti sono rimasti attivi.

Nuovo SHA-256 di `ct/4ct.py`:
`7ff955f781a6592010c695e88d04ab3b429e59ce56209c17cf2a4a849be0af31`.
Gli altri tre file di codice nel manifest hanno le stesse impronte della
prima prova. I conteggi V/E/F e il risultato sono identici; cambia solo
l'implementazione della costruzione dell'indice, oltre ai nuovi test e ai
documenti. Le modifiche locali preesistenti sono preservate.

### Artefatti e comandi effettivi

Nuova radice: `ct/debug/oracle-study/task5-linear-index-wt4mbk55/`.
Conservare `prefix-20/` insieme ai log, `comparison.json`,
`work-scaling.json`, `red.log`, `green-focused.log`, `green-suite.log`,
`smoke-s1.log` e copie precedenti in `before/`. I file di debug a nome fisso
scritti dallo smoke sono conservati in `verification-generated-debug/`;
i precedenti sono ripristinati e verificati tramite hash.

Comandi effettivi da `ct/` (il test mirato è stato eseguito prima in RED,
poi in GREEN):

```bash
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests/test_face_index.py -q
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests -q
/usr/bin/time -l env UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --input maps_3000_maps_of_8000_faces.colored.planar --map-number 1 --max-steps 20 --output debug/oracle-study/task5-linear-index-wt4mbk55/prefix-20 --ordinary-rebuild --kempe-search-limit 10000 > debug/oracle-study/task5-linear-index-wt4mbk55/prefix.stdout.log 2> debug/oracle-study/task5-linear-index-wt4mbk55/prefix.stderr-time.log
/usr/bin/time -l env UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --replay debug/oracle-study/task5-linear-index-wt4mbk55/prefix-20 > debug/oracle-study/task5-linear-index-wt4mbk55/replay.stdout.log 2> debug/oracle-study/task5-linear-index-wt4mbk55/replay.stderr-time.log
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python 4ct.py -s1 -r2 10 > debug/oracle-study/task5-linear-index-wt4mbk55/smoke-s1.log 2>&1
```

`/usr/bin/time -l` eseguito con accesso autorizzato alle metriche di sistema:
entrambi i comandi terminano con exit 0. Gli output pytest sono salvati nei
log RED/GREEN sopra. Un primo tentativo dello script ausiliario di conteggio
con `python3` di sistema è fallito per NetworkX assente, prima della misura;
lo script è stato eseguito correttamente da `ct/` con `../.venv/bin/python`.
Non è un errore del motore e non ha comportato installazioni.

### Revisione della modifica

La revisione indipendente finale è stata tentata, ma il revisore si è
fermato per il limite d'uso del servizio prima di restituire rilievi.
**A quel punto la revisione indipendente restava da completare**;
la precedente revisione della diagnosi iniziale non copre il nuovo codice.
È stata poi completata insieme al controllo dei ponti, come documentato
nell'ultimo aggiornamento sotto.
Restano eseguite le verifiche dell'esecutore: delta di produzione limitato
a `rebuild()`, test RED/GREEN, suite, smoke, replay, confronto esatto dei file,
conservazione delle modifiche precedenti e controllo del diff.

### Limite residuo

Il costo iniziale è ancora circa tre secondi per riduzione. La semplice
estrapolazione a costo costante scende da 22,29 a **6,60 ore per la sola
riduzione**, ma resta una proiezione non verificata, non una durata attesa
affidabile: il grafo si riduce e cambia la distribuzione del lavoro.
La prova non misura le prestazioni dell'intera catena né dell'ordinario.

L'intervento lineare e la sua prova sono completati; **la catena completa
resta aperta**. Nessuna altra mappa o validazione delle 151 mappe è stata
avviata. Prima di impegnare una corsa lunga, il prossimo approfondimento è
una nuova profilazione breve dei costi residui sul codice aggiornato;
eventuali modifiche alle copie o ai controlli richiedono un disegno e
verifiche specifici. Nessun controllo è stato disabilitato per ottenere
questi tempi e nessun risultato è una prova matematica generale.

## Aggiornamento: controllo iterativo dei ponti

### Diagnosi e intervento circoscritto

Dopo il via libera a continuare, profilato **un solo passo sulla riga 1**
con la costruzione lineare già presente. Nei 9,390 s profilati,
`nx.bridges()` occupava 3,260 s in dieci chiamate (34,7%). Il codice locale
di NetworkX 3.2.1 converte il multigrafo in grafo semplice ed esegue una
decomposizione in catene, creando anche copie temporanee. `FaceIndex` era
sceso a 0,992 s per 15 costruzioni: non era più il costo dominante.

Intervento limitato a `ct/experiments/oracle_reduction.py`: nuovo predicato
privato `_has_bridge()`, usato nei soli due controlli già presenti negli
invarianti e nel filtro strutturale di `plan_step()`. Visita iterativa
low-link direttamente sul multigrafo, con trattamento degli archi paralleli,
senza copie aggiuntive né mutazioni; dettagli in
[architettura](../architecture.md). Tutti gli altri controlli, copie atomiche,
fingerprint, candidati e formati dei certificati rimangono invariati.

| Profilo di un passo, inclusi replay e salvataggio | Indice lineare | Indice lineare + ponti |
| --- | --- | --- |
| Totale profilato | 9,390 s | 7,131 s |
| Controllo ponti, dieci chiamate | 3,260 s | 0,943 s |
| Quota cumulativa dei ponti | 34,7% | 13,2% |
| Invarianti globali, nove chiamate | 6,314 s | 4,286 s |
| Tempo reale CLI profilata | 9,51 s | 7,35 s |
| Picco RSS CLI profilata | 261,61 MiB | 248,66 MiB |

Entrambe le corse profilate: exit 0, un F5, `step_limit`, replay interno
esatto; `steps.jsonl` e `terminal.json` identici. I tempi cumulativi si
sovrappongono: gli invarianti comprendono il controllo ponti. Il profiler
aggiunge overhead; la misura ordinaria del prefisso è riportata sotto.

### Test e revisione

Nuovo `ct/tests/test_oracle_bridges.py`: 13 test. In RED falliscono tutti
per assenza del nuovo predicato; dopo l'implementazione, **214 test dedicati
PASS in 0,79 s**, inclusi i 201 dell'oracolo preesistente. **321 test
complessivi PASS in 1,24 s**; smoke S1 `-r2 10` exit 0, sette riduzioni,
ricostruzione valida con 16 vertici/24 archi.

I test coprono casi con risposta derivata a mano, attributi preservati,
loop, componenti disconnesse, archi paralleli e chiavi locali ripetute fra
coppie diverse; confrontano tutti i 729 multigrafi senza loop su quattro
vertici con molteplicità 0/1/2 contro la cancellazione effettiva di ciascun
arco; verificano inoltre un ciclo e un cammino di 3.000 vertici senza
ricorsione. Sono dati sintetici, non una nuova validazione del dataset.

La revisione indipendente ha esaminato **sia `FaceIndex.rebuild()` sia il
predicato dei ponti e i rispettivi test**, senza rilievi Critical, Important
o Minor. Il precedente tentativo fermato dal limite d'uso è quindi superato.
Il revisore ha controllato i log ma non ha ripetuto test o misure. Restano
fuori dal suo verdetto l'intero oracolo preesistente, i grafi semplici/diretti
(fuori contratto), la catena completa e il confronto ordinario rinviati.
L'ordine contrattuale delle facce nei bucket è preservato; l'ordine delle
chiavi dei dizionari con facce alias non è un requisito dei chiamanti.

### Misura dei 20 passi e replay in processo nuovo

| Misura | Indice lineare | Indice lineare + ponti |
| --- | --- | --- |
| Sola catena, 20 passi | 59,153774167 s | 51,808270333 s |
| Media per riduzione | 2,9577 s | 2,5904 s |
| CLI con replay interno e salvataggio | 86,06 s | 76,36 s |
| Replay in processo nuovo | 21,16 s | 17,41 s |
| Picco RSS CLI | 275,73 MiB | 254,53 MiB |
| Picco RSS replay | 228,06 MiB | 209,88 MiB |

Ulteriore riduzione del tempo della catena: **12,42% (1,14×)**; rispetto
alla prima implementazione, **3,86×**. Sono singole corse sulla stessa
macchina, non stime statistiche con carico controllato; il profilo di un
passo non rappresenta tutta la distribuzione del lavoro nei venti passi.

Il risultato resta `step_limit`, 10 F4/10 F5, 20 scambi parziali e zero
completi. V/E/F iniziali e terminali e lunghezze dei cammini sono quelli
già documentati. Il replay separato conferma `exact_replay=true`,
`source_matches=true`, `edge_multiset_matches=true`. **Tutti i byte di
`steps.jsonl` e `terminal.json` coincidono con entrambe le prove precedenti**;
coincidono anche risultato, sorgente e configurazione dei manifest.

Nuovo SHA-256 di `ct/experiments/oracle_reduction.py`:
`46b2a9f21c59ba5dae777e6d8a3ebd826510f359a275014d133458c2210ef4d4`.
Gli altri tre hash del codice sono quelli della prova con indice lineare;
gli hash di sorgente, certificati e terminale restano invariati.

### Artefatti e comandi effettivi

Nuova directory: `ct/debug/oracle-study/task5-residual-2pk826jb/`.
Contiene `profile-before/`, `profile-after/`, `before.pstats`, `after.pstats`,
riepiloghi testuali, `prefix-20/`, log di tempo/RSS, `comparison.json`,
`tests-red.log`, `tests-focused.log`, `tests-suite.log`, `smoke-s1.log`,
diff isolato, revisione e copie precedenti. I file di debug a nome fisso
precedenti sono ripristinati e verificati tramite hash; le versioni prodotte
dallo smoke restano in `verification-generated-debug/`.

Comandi realmente eseguiti da `ct/`, nell'ordine delle fasi. Il primo profilo
precede la modifica; le copie in `before/` ne conservano il codice. Come
nella diagnosi iniziale, cProfile usa il percorso **assoluto** del runner.

```bash
/usr/bin/time -l env UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m cProfile -o debug/oracle-study/task5-residual-2pk826jb/before.pstats /Users/mario.stefanutti/mario/programming/github-stefanutti/maps-coloring-python/ct/experiments/oracle_reduction_run.py --input maps_3000_maps_of_8000_faces.colored.planar --map-number 1 --max-steps 1 --output debug/oracle-study/task5-residual-2pk826jb/profile-before --ordinary-rebuild --kempe-search-limit 10000 > debug/oracle-study/task5-residual-2pk826jb/profile-before.stdout.log 2> debug/oracle-study/task5-residual-2pk826jb/profile-before.stderr-time.log
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_bridges.py -q > debug/oracle-study/task5-residual-2pk826jb/tests-red.log 2>&1
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_bridges.py tests/test_oracle_reduction.py -q > debug/oracle-study/task5-residual-2pk826jb/tests-focused.log 2>&1
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests -q > debug/oracle-study/task5-residual-2pk826jb/tests-suite.log 2>&1
/usr/bin/time -l env UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m cProfile -o debug/oracle-study/task5-residual-2pk826jb/after.pstats /Users/mario.stefanutti/mario/programming/github-stefanutti/maps-coloring-python/ct/experiments/oracle_reduction_run.py --input maps_3000_maps_of_8000_faces.colored.planar --map-number 1 --max-steps 1 --output debug/oracle-study/task5-residual-2pk826jb/profile-after --ordinary-rebuild --kempe-search-limit 10000 > debug/oracle-study/task5-residual-2pk826jb/profile-after.stdout.log 2> debug/oracle-study/task5-residual-2pk826jb/profile-after.stderr-time.log
/usr/bin/time -l env UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --input maps_3000_maps_of_8000_faces.colored.planar --map-number 1 --max-steps 20 --output debug/oracle-study/task5-residual-2pk826jb/prefix-20 --ordinary-rebuild --kempe-search-limit 10000 > debug/oracle-study/task5-residual-2pk826jb/prefix.stdout.log 2> debug/oracle-study/task5-residual-2pk826jb/prefix.stderr-time.log
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python 4ct.py -s1 -r2 10 > debug/oracle-study/task5-residual-2pk826jb/smoke-s1.log 2>&1
/usr/bin/time -l env UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --replay debug/oracle-study/task5-residual-2pk826jb/prefix-20 > debug/oracle-study/task5-residual-2pk826jb/replay.stdout.log 2> debug/oracle-study/task5-residual-2pk826jb/replay.stderr-time.log
```

Tutti i comandi terminano con exit 0, salvo il RED atteso dei test prima
dell'implementazione (exit 1). `/usr/bin/time -l` ha accesso autorizzato
alle metriche di sistema. Nessun nuovo errore software osservato in queste
corse; nessuna installazione, commit o modifica alle altre mappe.

### Decisione e prossimo passo

Il costo residuo resta circa **2,59 s/passo** nel prefisso. La proiezione
a costo costante di 8.031 riduzioni è **5,78 ore per la sola riduzione**,
non una previsione verificata della catena completa. Il grafo si riduce e
il lavoro può cambiare; replay e ordinario aggiungono altro costo.

L'ottimizzazione circoscritta è conclusa. La catena completa e il confronto
ordinario restano **aperti e non avviati**. `step_limit` è un arresto
non conclusivo imposto dal budget; `not_run_nonterminal` segnala che
l'ordinario non è stato eseguito. Nessuno dei due è un errore software o
un'impossibilità matematica.

Il profilo residuo attribuisce circa il 60% del tempo agli invarianti
globali, incluso il nuovo controllo dei ponti. Il prossimo passo concreto
è progettare il riuso delle verifiche e degli indici per stati immutati,
identificando tutte le mutazioni e la loro invalidazione prima di introdurre
cache o aggiornamenti incrementali. Il disegno deve conservare controlli
di riferimento, atomicità e rifiuto dei certificati obsoleti. Nessun altro
intervento, catena lunga, altra riga o validazione delle 151 mappe è stato
avviato automaticamente.

## Aggiornamento: riuso delle verifiche globali

### Implementazione e invalidazione

L'autore ha richiesto esplicitamente di implementare il riuso delle verifiche
sugli stati immutati. Intervento circoscritto al flusso esistente in
`ct/experiments/oracle_reduction.py`: una sola istantanea privata per stato,
memorizzata soltanto dopo il successo del checker completo. Il confronto
copre grafo/colori, facce, ID e relativi tipi, lookup completi, contatori,
identità delle facce, collegamento all'embedding e tutti i bucket `FaceIndex`.
Il dettaglio del contratto e della codifica è in [architettura](../architecture.md).

Un cambiamento invalida l'evidenza prima del controllo completo; un errore
non diventa un successo memorizzato. `_install()` trasferisce l'evidenza
insieme agli stessi oggetti del risultato temporaneo già verificato. I
nuovi stati iniziano senza cache. Nessun flag affidato al chiamante,
nessuna cache globale o cronologia; nessuna modifica ai certificati, ai
fingerprint, alla politica dei candidati o alle copie atomiche.

Il corpo precedente di `assert_state_invariants()` è conservato in
`_assert_state_invariants_full()`; il confronto AST è identico salvo il nome.
`assert_state_invariants(state, force=True)` esegue sempre questo riferimento.
Le istantanee richiedono ancora O(V+E) tempo e memoria; evitano le visite e
ricostruzioni più costose, senza trasformare ogni verifica in un'operazione
costante. Le rappresentazioni non serializzabili ricadono nel checker completo.

### Test e revisione

Nuovo `ct/tests/test_oracle_validation_cache.py`: **33 test**. Primo RED:
sette test sul riuso e sul ciclo di vita falliscono, 24 regressioni sulle
corruzioni passano già col checker originario. Dopo l'implementazione:
245 test mirati PASS in 0,89 s; aggiunte due verifiche su invalidazione dopo
errore/riparazione e fallback di un mapping non serializzabile. Suite finale:
**354 test PASS in 1,17 s**, inclusi tutti i 201 test originari dell'oracolo.
Smoke S1 exit 0: sette riduzioni e ricostruzione valida di 16 vertici/24 archi.

I test riscaldano la cache e poi alterano topologia, colori, facce, ID,
lookup, contatori e indici, anche a conteggi invariati. Verificano distinzione
fra interi e float, tuple e liste, rifiuto di certificati obsoleti dopo una
permutazione valida dei colori, atomicità su rifiuto, trasferimento apply/undo,
copie e caricamento. Le chiamate ai controlli globali vengono osservate con
cProfile sul codice reale, senza mock del validatore né soglie temporali.

Revisione indipendente read-only conclusa: approvato nello scope, nessun
rilievo bloccante o importante. Il revisore ha controllato separatamente
la copertura dello snapshot, il ciclo di vita e l'identità AST del checker.
Contratto invariato: uso sincrono e normali mutazioni pubbliche nelle
rappresentazioni del modello. Manomissione della cache privata, internals
NetworkX, iteratori consumabili al posto dei bucket e tipi estranei al modello
non diventano nuove API supportate. In particolare la codifica privata non
è un serializzatore generale: l'equivalenza marshal di bytes/bytearray non
riguarda le rappresentazioni del modello (vertici/ID interi, colori stringa,
bordi come tuple). La revisione non è una verifica generale del teorema o
dell'intero motore preesistente, né copre la catena completa rinviata.

### Profilo e prefisso della stessa riga 1

| Profilo di un passo, incluso replay/salvataggio | Prima | Con riuso |
| --- | --- | --- |
| Tempo totale profilato | 7,131 s | 5,612 s |
| Richieste di verifica | 9 | 9 |
| Verifiche globali complete | 9 | 5 |
| Tempo del flusso di verifica, incluso riuso | 4,286 s | 2,842 s |
| Costo delle nove istantanee | — | 0,534 s |
| Controlli ponti totali | 10 | 6 |
| Tempo reale CLI profilata | 7,35 s | 5,80 s |
| Picco RSS CLI profilata | 248,66 MiB | 255,73 MiB |

Quattro verifiche globali su nove vengono riutilizzate; restano cinque
verifiche complete sui nuovi stati. I tempi cumulativi si sovrappongono e
non vanno sommati; il profiler introduce overhead. Certificato e terminale
del passo profilato identici alla prova precedente.

| Misura ordinaria del prefisso di 20 passi | Prima | Con riuso |
| --- | --- | --- |
| Sola catena | 51,808270333 s | 36,130134083 s |
| Media per riduzione | 2,5904 s | 1,8065 s |
| CLI con replay interno e salvataggio | 76,36 s | 52,15 s |
| Replay in processo nuovo | 17,41 s | 13,01 s |
| Picco RSS CLI | 254,53 MiB | 470,08 MiB |
| Picco RSS replay | 209,88 MiB | 363,34 MiB |

La catena è **1,43× più veloce (−30,26%)** rispetto alla prova precedente,
**5,53×** rispetto all'implementazione iniziale. Sono singole corse, non medie
statistiche o previsioni della catena completa. Il guadagno temporale è
accompagnato da una regressione del picco RSS, esplicitamente registrata.

Invariati `step_limit`, 10 F4/10 F5, 20 scambi parziali, zero completi,
conteggi e lunghezze già documentati. Replay interno e separato esatti;
`source_matches=true`, `edge_multiset_matches=true`. **`steps.jsonl` e
`terminal.json` coincidono byte per byte con tutte e tre le prove precedenti**;
coincidono risultato, sorgente e configurazione. Il terminale ricaricato
supera anche `force=True`, con fingerprint invariato.

Nuovo SHA-256 di `ct/experiments/oracle_reduction.py`:
`06fb0ef1608da064de4b6483f56588377fb85cc944aeb5a1392fbf91514cfc7f`.
Gli altri tre hash del codice sono invariati, così come gli hash della
riga sorgente, dei certificati e del terminale.

### Memoria: evidenza e limite

L'istantanea conservata sul terminale occupa **4.863.570 byte (4,64 MiB)**.
Un ulteriore replay diagnostico, separato dalle misure della tabella,
ha osservato con riferimenti deboli i 23 stati/grafi creati. Ai punti di
installazione risultano al massimo tre stati e tre grafi vivi, con al
massimo **14.614.970 byte (13,94 MiB)** di istantanee conservate. Alla fine
del runner: zero stati e zero byte di cache, tre grafi ancora vivi; una
raccolta esplicita finale elimina anche questi tre grafi, senza oggetti
non raccoglibili. Il replay diagnostico è anch'esso esatto.

Questa osservazione non mostra accumulo di stati in una cronologia di cache,
ma **non attribuisce interamente l'aumento RSS**: il picco comprende tutte
le allocazioni del processo, incluse quelle temporanee e la gestione della
memoria Python. `ru_maxrss` è un massimo storico e non misura la memoria
corrente liberata. Nessun `gc.collect()` è stato aggiunto al codice di
produzione; nel diagnostico è chiamato soltanto dopo la conclusione del
runner. Le prestazioni e la memoria del ramo completo restano non misurate.

### Artefatti e comandi effettivi

Nuova radice: `ct/debug/oracle-study/task5-validation-reuse-cxeaekbk/`.
Contiene `before/` con hash, diff isolato, `full-checker-preserved.json`,
test RED/GREEN, smoke, `profile-one-step/`, `profile.pstats`, `profile.txt`,
`prefix-20/`, log di tempo/RSS, `comparison.json`, verifica forzata del
terminale, revisione e diagnostico memoria. File fissi di debug preesistenti
ripristinati e controllati tramite hash; output prodotti conservati in
`verification-generated-debug/`.

Comandi realmente eseguiti da `ct/`:

```bash
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_validation_cache.py -q > debug/oracle-study/task5-validation-reuse-cxeaekbk/tests-red.log 2>&1
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_validation_cache.py tests/test_oracle_reduction.py tests/test_oracle_bridges.py -q > debug/oracle-study/task5-validation-reuse-cxeaekbk/tests-focused.log 2>&1
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests -q > debug/oracle-study/task5-validation-reuse-cxeaekbk/tests-suite.log 2>&1
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python 4ct.py -s1 -r2 10 > debug/oracle-study/task5-validation-reuse-cxeaekbk/smoke-s1.log 2>&1
/usr/bin/time -l env UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m cProfile -o debug/oracle-study/task5-validation-reuse-cxeaekbk/profile.pstats /Users/mario.stefanutti/mario/programming/github-stefanutti/maps-coloring-python/ct/experiments/oracle_reduction_run.py --input maps_3000_maps_of_8000_faces.colored.planar --map-number 1 --max-steps 1 --output debug/oracle-study/task5-validation-reuse-cxeaekbk/profile-one-step --ordinary-rebuild --kempe-search-limit 10000 > debug/oracle-study/task5-validation-reuse-cxeaekbk/profile.stdout.log 2> debug/oracle-study/task5-validation-reuse-cxeaekbk/profile.stderr-time.log
/usr/bin/time -l env UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --input maps_3000_maps_of_8000_faces.colored.planar --map-number 1 --max-steps 20 --output debug/oracle-study/task5-validation-reuse-cxeaekbk/prefix-20 --ordinary-rebuild --kempe-search-limit 10000 > debug/oracle-study/task5-validation-reuse-cxeaekbk/prefix.stdout.log 2> debug/oracle-study/task5-validation-reuse-cxeaekbk/prefix.stderr-time.log
/usr/bin/time -l env UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --replay debug/oracle-study/task5-validation-reuse-cxeaekbk/prefix-20 > debug/oracle-study/task5-validation-reuse-cxeaekbk/replay.stdout.log 2> debug/oracle-study/task5-validation-reuse-cxeaekbk/replay.stderr-time.log
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-validation-reuse-cxeaekbk/inspect-memory.py > debug/oracle-study/task5-validation-reuse-cxeaekbk/memory-inspection.stdout.log 2> debug/oracle-study/task5-validation-reuse-cxeaekbk/memory-inspection.stderr.log
```

Tutti exit 0 salvo il RED atteso (exit 1). Metriche `/usr/bin/time -l`
autorizzate; nessun nuovo errore software osservato. Il controllo forzato
supplementare ha ricaricato `prefix-20/`, chiamato
`assert_state_invariants(terminal, force=True)` e confrontato il fingerprint
prima/dopo; esito e dimensione dell'istantanea sono salvati in
`forced-terminal-verification.json`.

### Decisione e prossimo passo

Riuso implementato e verificato; modifiche precedenti preservate. Il costo
iniziale è circa **1,81 s/passo**: proiezione a costo costante **4,03 ore**
per la sola riduzione di 8.031 passi, non una durata verificata. La catena
completa e il confronto ordinario restano aperti e non avviati.
`step_limit` è non conclusivo; `not_run_nonterminal` indica che l'ordinario
non è stato eseguito. Nessuna impossibilità matematica è stata dimostrata.

Prima di estendere la corsa, il prossimo approfondimento è isolare le
allocazioni temporanee responsabili del maggiore picco RSS, usando lo
stesso prefisso e il riferimento completo. Non sono state avviate altre
mappe, ripetuta la validazione delle 151 mappe o cambiate automaticamente
politiche di garbage collection o controlli.

## Aggiornamento: diagnosi della memoria

### Domanda e metodo

Su richiesta dell'autore, isolare l'aumento RSS prima della corsa lunga.
**Codice di produzione e test lasciati invariati.** Usato esclusivamente
il replay dei 20 passi già salvati della riga 1; nessuna nuova riduzione
della mappa grande, altra riga o validazione delle 151 mappe.

Nel primo confronto si varia soltanto il percorso di validazione nel
processo diagnostico: checker completo preesistente oppure riuso corrente.
Misurati RSS corrente con `ps` sul PID del diagnostico, massimo storico con
`resource.getrusage`, byte delle istantanee uniche, grafi/stati tramite
riferimenti deboli, statistiche `sys._debugmallocstats()` e GC. Ai checkpoint
di installazione, lo stato e il suo risultato possono condividere gli stessi
byte: questa diagnosi conta una volta sola ogni oggetto snapshot.

Secondo confronto: stesso replay con statistiche native `malloc` e riepiloghi
`vmmap`, prima con cache corrente e poi con la sola rappresentazione
dell'istantanea compressa tramite `zlib.compress(data, 1)`. È una prova
controllata in memoria nel processo, **non una patch al repository**. La
compressione conserva l'intero contenuto, senza sostituirlo con un hash;
checker, rilevamento delle mutazioni e certificati seguono il flusso esistente.

### Risultati comparabili

| Replay diagnostico, 20 passi salvati | Checker completo | Cache corrente | Cache + diagnostica nativa | Variante compressa + diagnostica nativa |
| --- | --- | --- | --- | --- |
| Tempo strumentato | 15,585 s | 12,110 s | 13,058 s | 13,078 s |
| Picco RSS, `ru_maxrss` | 203,17 MiB | 361,97 MiB | 368,33 MiB | 213,75 MiB |
| RSS corrente al passo 20 | 170,38 MiB | 343,14 MiB | 347,53 MiB | 193,17 MiB |
| Istantanee uniche vive al passo 20 | 0 | 9,29 MiB | 9,29 MiB | 2,24 MiB |
| Massimo grafi vivi ai checkpoint | 3 | 3 | 3 | 3 |
| RSS dopo raccolta finale diagnostica | 96,80 MiB | 257,28 MiB | 264,67 MiB | 106,78 MiB |
| Replay/sorgente/archi keyed | Esatti | Esatti | Esatti | Esatti |

Le due colonne con diagnostica nativa sono il confronto della variante
compressa; le altre due isolano il passaggio dal checker completo al riuso.
I tempi includono strumentazione e sono singole osservazioni. Non sono
nuove misure della CLI ordinaria o del prefisso di riduzione in avanti.
Il `physical footprint` di `vmmap` è una metrica diversa dal picco RSS;
non è stato usato al suo posto nella tabella.

Il checker completo mantiene il RSS corrente circa 166–172 MiB durante
il replay. Con la cache cresce da circa 177 a 348 MiB, mentre i byte delle
istantanee restano circa 9,29 MiB e i grafi vivi ai checkpoint restano tre.
I piccoli blocchi Python allocati sono circa 98,6 MiB in entrambe le prove;
la differenza nelle arene al passo 20 è circa 13,75 MiB, insufficiente a
spiegare l'aumento complessivo.

### Dove resta la memoria

Nel replay con diagnostica nativa, `malloc_zone_statistics` mostra circa
**30,62 MiB di allocazioni native in uso**, sostanzialmente costanti durante
i passi. Al passo 20, `vmmap` mostra invece **170,4 MiB residenti** nella
categoria **`MALLOC_LARGE (empty)`**, su 106 regioni. Sono regioni vuote per
l'allocatore, ancora residenti nel processo: non byte trattenuti da una
cronologia di stati dell'oracolo.

Con la variante compressa, mantenendo lo stesso flusso e lo stesso replay
esatto, tale categoria scende a **20,0 MiB su otto regioni**. Il picco RSS
scende di circa **154,58 MiB**; la riduzione delle sole istantanee vive è
circa 7,05 MiB. Il beneficio riguarda quindi soprattutto le allocazioni
native libere rimaste residenti, oltre allo spazio della cache viva.

A fine runner, in tutte le prove, nessuno stato né snapshot resta vivo;
dopo il GC finale diagnostico non rimane neppure alcuno dei grafi osservati.
Nel processo con cache corrente il RSS resta però 264,67 MiB.
`malloc_zone_pressure_relief(NULL, 0)` restituisce zero byte rilasciati e
non riduce questo valore nella prova. Non sono state aggiunte raccolte
forzate, chiamate native o politiche di memoria al codice di produzione.
ABI e significato delle metriche native sono stati letti nell'header
`malloc/malloc.h` dell'SDK installato.

### Ipotesi escluse e limiti della diagnosi

- Quaranta istantanee dello stesso stato immutato mantengono il RSS circa
  125,03 MiB: non riproducono una perdita sistematica a ogni chiamata.
- Quaranta serializzazioni dello stesso payload mantengono il RSS circa
  124,17 MiB. Aumentare il payload di 735 byte a iterazione, da solo,
  mantiene il RSS circa 122,48 MiB nella prova separata: **la variazione di
  dimensione da sola non basta** a spiegare il replay.
- Buffer sintetici di circa 4,6 MiB, senza grafo, mostrano un aumento
  limitato del RSS quando crescono leggermente; non riproducono da soli
  l'intero aumento osservato nel motore.

La causa dominante è dunque localizzata nel **ciclo di vita dei grandi
buffer dell'istantanea, combinato con le altre allocazioni del replay, e
nella loro permanenza in regioni native libere ma residenti su questo host**.
La sostituzione controllata con una rappresentazione lossless più piccola
riduce fortemente l'effetto. Non è stata ricostruita ogni decisione interna
di `libmalloc`, né dimostrato un andamento oltre i 20 passi: evitare di
chiamarlo un bug di `marshal`, una perdita illimitata o un comportamento
universale di Python su qualsiasi sistema.

### Artefatti e comandi effettivi

Nuova radice: `ct/debug/oracle-study/task5-memory-diagnosis-55sjo0d_/`.
Conservati script diagnostici, versioni precedenti degli script, JSON delle
misure, log, statistiche dell'allocatore, riepiloghi `vmmap`, `comparison.json`
e copie/hash dei file locali prima della diagnosi. `probe_replay-v1.py`
corrisponde ai primi due confronti; `probe_replay-v2.py` aggiunge le metriche
native; la versione corrente aggiunge la variante compressa. Per ripetere
una prova scegliere un `--label` nuovo: le directory esistenti sono rifiutate.

Comandi eseguiti da `ct/`, ciascuno nel proprio processo; stdout/stderr
salvati nei log con il nome della prova nella nuova radice:

```bash
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-memory-diagnosis-55sjo0d_/probe_replay.py --mode full --label full-default
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-memory-diagnosis-55sjo0d_/probe_replay.py --mode cached --label cached-default
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-memory-diagnosis-55sjo0d_/probe_snapshot.py --kind snapshot
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-memory-diagnosis-55sjo0d_/probe_snapshot.py --kind marshal
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-memory-diagnosis-55sjo0d_/probe_buffers.py --growth 0
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-memory-diagnosis-55sjo0d_/probe_buffers.py --growth 735
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-memory-diagnosis-55sjo0d_/probe_snapshot.py --kind marshal --growth 147
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-memory-diagnosis-55sjo0d_/probe_replay.py --mode cached --label cached-native --native
UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-memory-diagnosis-55sjo0d_/probe_replay.py --mode compressed --label compressed-native --native
```

Tutte queste prove terminano con exit 0. Un tentativo ausiliario precedente
ha usato un percorso con `ct/` duplicato mentre era già in `ct/`: fallita
la modifica dello script, il successivo lancio ha rifiutato l'opzione
`--growth` ancora assente (exit 2). Corretto il percorso e usati nuovi log;
nessuna esecuzione dell'oracolo in quel tentativo. La pagina man locale di
malloc non era disponibile; le API sono state verificate nell'SDK.
Questi incidenti diagnostici non sono errori software del motore o esiti
matematici. Non sono stati installati pacchetti.

### Decisione e prossimo passo

Revisione indipendente degli artefatti completata in sola lettura: nessun
finding bloccante o errore materiale. Confermati il confronto delle metriche
e i limiti della diagnosi; non ripetuti test o esperimenti dal revisore.
Il riepilogo della revisione e le decisioni sono conservati in `review.txt`
nella nuova radice diagnostica.

Diagnosi completata sul prefisso salvato: la crescita RSS principale è
attribuita alle regioni native vuote lasciate dai grandi buffer nel flusso
del replay; il cambio lossless della rappresentazione è una mitigazione
concreta già provata nel diagnostico.

**Prossimo passo:** implementare la rappresentazione compressa come modifica
circoscritta, con test di riuso/invalidazione e confronto esatto della
semantica; eseguire suite/smoke e misurare nuovamente riduzione in avanti
di 20 passi e replay sulla sola riga 1. La prova attuale non sostituisce
quelle verifiche e non è presentata come fix già integrato.
La catena completa e il confronto ordinario restano aperti e non avviati;
nessuna altra mappa o validazione massiva. I replay restano `step_limit`,
quindi non conclusivi rispetto al ramo completo e all'impossibilità matematica.

## Aggiornamento: compressione lossless integrata

### Intervento e TDD

Il 29 settembre 2026, su richiesta dell'autore, implementata inline la
rappresentazione provata nel diagnostico: `_invariant_snapshot()` comprime
l'intero buffer `marshal` versione 2 con `zlib` livello 1. Il confronto è
sui byte compressi completi, senza digest sostitutivi. La codifica è
privata e locale al processo; non entra in fingerprint, certificati o JSON.
Non richiede una nuova dipendenza. Il buffer non compresso continua a
esistere temporaneamente durante la codifica; il motore non decomprime
l'evidenza e non introduce raccolte forzate o chiamate native all'allocatore.
Il contratto è descritto in [architettura](../architecture.md).

Nuovo test `test_validation_evidence_is_compact_and_lossless_for_parallel_edges`
in `ct/tests/test_oracle_validation_cache.py`: theta con tre archi paralleli
colorati e tre facce uguali per valore ma distinte per identità. Il payload
atteso è derivato a mano, include i tipi, gli ID, le identità e tutti gli
indici; il test richiede dimensione inferiore alla metà del buffer originale
e recupero byte per byte del contenuto tramite decompressione. È una soglia
sui byte di questa piccola fixture, non una soglia di tempo o RSS.

**RED:** una regressione attesa, 713 byte conservati invece di meno di 356;
33 test esistenti PASS. **GREEN:** 248 test mirati PASS in 0,93 s;
**suite completa 355 PASS in 1,17 s**. Restano coperti riuso/invalidazione,
mutazioni pubbliche anche a conteggi invariati, differenze di tipo,
certificati obsoleti, atomicità, apply/undo, copie, caricamento e fallback
non serializzabile. Smoke S1 `-r2 10`: exit 0, sette riduzioni, ricostruzione
valida con 16 vertici e 24 archi, isomorfismo confermato.

Il confronto AST con la copia precedente conferma che tutte le altre
funzioni del motore, inclusi `_assert_state_invariants_full()`, il riuso,
la scelta dei candidati e apply/undo, sono identiche. Nessun controllo è
stato rimosso e la rappresentazione del payload è conservata integralmente.

### Nuovo prefisso e replay separato

Eseguiti soltanto i **20 passi della riga 1**, poi il replay dei nuovi file
in un processo separato. Stessa configurazione della prova precedente,
Python 3.9.6 e NetworkX 3.2.1. Il benchmark usa la CLI ordinaria senza
profiler o strumentazione dell'allocatore; `/usr/bin/time -l` misura tempi
e massimo RSS con accesso autorizzato alle metriche di sistema.

| Misura | Ponti, prima del riuso | Riuso senza compressione | Riuso con compressione |
| --- | --- | --- | --- |
| Sola catena, 20 passi | 51,808270333 s | 36,130134083 s | 34,574952417 s |
| Media per riduzione | 2,5904 s | 1,8065 s | 1,7287 s |
| CLI con replay interno e salvataggio | 76,36 s | 52,15 s | 50,15 s |
| Replay in processo nuovo | 17,41 s | 13,01 s | 12,92 s |
| Picco RSS CLI | 254,53 MiB | 470,08 MiB | 397,66 MiB |
| Picco RSS replay | 209,88 MiB | 363,34 MiB | 214,25 MiB |

Rispetto al riuso senza compressione: picco CLI **−15,41%**, replay
**−41,03%**; tempo della catena **−4,30%**. Sono singole corse, non medie
statistiche: le piccole differenze temporali non stabiliscono un guadagno
stabile. Il picco del replay è vicino ai 213,75 MiB della variante
compressa diagnostica, ma quella misura aveva strumentazione diversa e
non va usata per calcolare un confronto temporale equivalente.

Il beneficio sulla CLI completa è più limitato: **397,66 MiB restano sopra
254,53 MiB** della versione prima del riuso. La compressione mitiga la
regressione ma non la elimina nell'andata con replay interno e salvataggio.
Questa prova non campiona le fasi della CLI né `MALLOC_LARGE (empty)`;
non attribuisce quindi il picco residuo a uno specifico punto o alla
medesima categoria nativa. Nessuna conclusione su un leak illimitato,
sul dettaglio di libmalloc o sul comportamento oltre il prefisso osservato.

`steps.jsonl` e `terminal.json` coincidono **byte per byte con tutte e
quattro le precedenti prove** (iniziale, indice lineare, ponti, riuso).
Risultato, sorgente e configurazione dei manifest sono uguali. Invariati:

- `step_limit`, 20 riduzioni, V/E/F 16.064/24.096/8.034 → 16.024/24.036/8.014;
- 10 F4 e 10 F5; 20 scambi parziali e zero completi;
- cammini: 1.607 archi totali, mediana 4, massimo 1.519; stessa sequenza;
- replay interno e separato esatti; `source_matches=true` e `edge_multiset_matches=true`;
- ordinario `not_run_nonterminal`, correttamente non eseguito.

Il terminale ricaricato supera anche `assert_state_invariants(..., force=True)`
con fingerprint invariato. Sui medesimi oggetti faccia, la decompressione
nel solo script di controllo coincide esattamente con il vecchio snapshot
non compresso, eseguito dalla copia precedente della funzione. L'istantanea
terminale passa da **4.863.570 a 1.167.447 byte** (4,64→1,11 MiB, circa −76%).
Questa dimensione riguarda un'istanza nel processo di controllo; gli indirizzi
Python presenti nell'evidenza possono cambiare i byte compressi fra processi.

SHA-256 del nuovo `ct/experiments/oracle_reduction.py`:
`cc90c92ef482cdfa7433d7c05d1d776606768440b94696873da43cd857ad00ba`.
Gli altri tre hash del codice nel manifest sono invariati. Restano identiche
le impronte di riga sorgente, certificati, terminale e fingerprint riportate
nelle sezioni precedenti.

### Artefatti, conservazione e comandi effettivi

Nuova radice: `ct/debug/oracle-study/task5-compressed-snapshot-31zqnha5/`.
Contiene copie/hash precedenti, ledger `progress.md`, log RED/GREEN/suite,
smoke, `prefix-20/`, log di tempo/RSS, `comparison.json`,
`forced-terminal-verification.json`, script di verifica e diff isolati.
Tutti questi artefatti sono ignorati da Git: conservarli insieme al dataset
sorgente per rileggere il prefisso. Revisione indipendente finale conclusa
in sola lettura, senza rilievi Critical/Important/Minor e senza ripetere
test o esperimenti; verbale in `review.txt`. Confermati semantica lossless,
test, conservazione dei contratti e confronto delle evidenze.

La revisione non estende il verdetto alla catena completa, all'ordinario
grande, ad altre mappe o alla prova generale delle regole F2–F5; questi
obiettivi restano fuori scope e non verificati. Non attribuisce il residuo
RSS a una causa nativa precisa né considera stabili le variazioni temporali
da singole corse. Il difetto preesistente di provenienza sotto cProfile
resta separato. Nessuna correzione richiesta o rilievo minore rinviato.

Mantenuta la checkout esistente su `feature/machine-learning`; nessun commit,
nuova checkout, reset, stash o pulizia. I due file di debug fissi prodotti
dallo smoke sono archiviati in `verification-generated-debug/`; tutti i
14 file top-level di debug preesistenti risultano identici alle copie
iniziali dopo il ripristino. `PYTHONDONTWRITEBYTECODE=1`, cache pytest
disabilitata e directory temporanee nuove preservano le cache ignorate.
I file locali non pertinenti sono controllati contro le impronte iniziali.

Comandi realmente eseguiti da `ct/`:

```bash
PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_validation_cache.py -q -p no:cacheprovider --basetemp=debug/oracle-study/task5-compressed-snapshot-31zqnha5/pytest-red > debug/oracle-study/task5-compressed-snapshot-31zqnha5/tests-red.log 2>&1
PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_validation_cache.py tests/test_oracle_reduction.py tests/test_oracle_bridges.py -q -p no:cacheprovider --basetemp=debug/oracle-study/task5-compressed-snapshot-31zqnha5/pytest-focused > debug/oracle-study/task5-compressed-snapshot-31zqnha5/tests-focused.log 2>&1
../.venv/bin/python -B debug/oracle-study/task5-compressed-snapshot-31zqnha5/run-checks.py
/usr/bin/time -l env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --input maps_3000_maps_of_8000_faces.colored.planar --map-number 1 --max-steps 20 --output debug/oracle-study/task5-compressed-snapshot-31zqnha5/prefix-20 --ordinary-rebuild --kempe-search-limit 10000 > debug/oracle-study/task5-compressed-snapshot-31zqnha5/prefix.stdout.log 2> debug/oracle-study/task5-compressed-snapshot-31zqnha5/prefix.stderr-time.log
/usr/bin/time -l env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --replay debug/oracle-study/task5-compressed-snapshot-31zqnha5/prefix-20 > debug/oracle-study/task5-compressed-snapshot-31zqnha5/replay.stdout.log 2> debug/oracle-study/task5-compressed-snapshot-31zqnha5/replay.stderr-time.log
PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-compressed-snapshot-31zqnha5/compare-results.py > debug/oracle-study/task5-compressed-snapshot-31zqnha5/comparison.stdout.log 2> debug/oracle-study/task5-compressed-snapshot-31zqnha5/comparison.stderr.log
```

`run-checks.py` esegue, con gli stessi due valori di ambiente:

```bash
uv run --python ../.venv/bin/python python -m pytest tests -q -p no:cacheprovider --basetemp=/Users/mario.stefanutti/mario/programming/github-stefanutti/maps-coloring-python/ct/debug/oracle-study/task5-compressed-snapshot-31zqnha5/pytest-suite
uv run --python ../.venv/bin/python python 4ct.py -s1 -r2 10
```

I due log sono `tests-suite.log` e `smoke-s1.log`; argv ed exit code sono
in `verification-commands.json`. Il wrapper preserva i debug fissi in un
blocco `finally` e ne verifica gli hash in `debug-preservation.json`.
Tutti i comandi GREEN, smoke, prefisso, replay e confronto terminano con
exit 0. Il RED atteso è un fallimento di requisito prima del fix; la
successiva stampa del log aveva reso 0 l'exit del comando shell composto.
La conferma del RED viene dal risultato pytest (1 failed/33 passed).

### Classificazione e prossimo passo

`step_limit` è un **arresto non conclusivo** dopo il budget richiesto.
`not_run_nonterminal` significa **ordinario non eseguito**, non fallito.
Non sono osservati nuovi errori software o violazioni degli invarianti.
Il precedente difetto della provenienza con cProfile relativo resta
separato e non corretto da questa modifica. Nessuna impossibilità matematica
è dimostrata dal prefisso o dal replay esatto.

La compressione è integrata e verificata nello scope richiesto. **Task 5,
catena completa e confronto ordinario restano aperti**; non sono stati
avviati altri prefissi, altre mappe o la validazione delle 151 mappe.
Il prossimo approfondimento proposto è attribuire il picco RSS residuo
della CLI sul medesimo prefisso, separando riduzione, replay interno e
salvataggio prima di valutare l'estensione della corsa. Non è stato eseguito
in questa sessione e non è un'autorizzazione alla catena lunga.

## Aggiornamento: picco della CLI localizzato nel replay interno

### Domanda e metodo

Il 29 settembre 2026 l'autore ha autorizzato il prossimo approfondimento
nella stessa sessione: separare riduzione in avanti, replay interno e
salvataggio per localizzare il picco residuo di circa 398 MiB. **Produzione
e test sono rimasti invariati**; i 355 test e lo smoke documentati sopra
sono la verifica dell'implementazione precedente, non una nuova suite
eseguita durante questa diagnosi.

Due processi diagnostici hanno eseguito la CLI reale sulla **sola riga 1,
con budget 20**. Il primo osserva il flusso corrente; il secondo ripete lo
stesso prefisso usando il checker completo esistente durante il solo replay
interno. Nessun controllo di correttezza viene eliminato. La sostituzione
è limitata al processo diagnostico e ripristinata prima del salvataggio;
non è una patch al motore né una nuova opzione della CLI di produzione.

Gli script avvolgono le funzioni reali senza conservarne gli stati passati.
Riferimenti deboli contano stati e grafi; i byte condivisi di un'istantanea
vengono contati una volta sola. Ai confini delle fasi e ai passi 1/5/10/15/20
sono registrati RSS corrente (`ps`), massimo storico (`resource`), byte delle
istantanee, statistiche GC e native `malloc_zone_statistics`. Ai confini
e ai passi 1/20 si aggiungono `vmmap -summary` e `_debugmallocstats()`.
Il processo osservato è il diagnostico stesso; il `physical footprint`
di vmmap non viene confuso con RSS. ABI nativa verificata nell'header
`malloc/malloc.h` dell'SDK locale.

Una raccolta esplicita viene eseguita **solo dopo il ritorno della CLI**,
per distinguere gli oggetti raccoglibili dalla memoria residente; nessun GC
forzato durante riduzione/replay. L'osservazione introduce overhead e cambia
piccole allocazioni. La seconda versione aggiunge anche un wrapper di
misura del checker completo: il confronto non è una prova con carico o
layout dell'allocatore controllati. Sono due osservazioni diagnostiche,
non medie statistiche né nuovi benchmark di velocità della CLI ordinaria.

### Dove si forma il picco

| Checkpoint, flusso corrente | RSS corrente | Picco storico | Istantanee vive uniche | `MALLOC_LARGE (empty)` residente |
| --- | --- | --- | --- | --- |
| Prima della riduzione | 139,08 MiB | 139,08 MiB | 0 | 0 |
| Dopo 20 riduzioni | 217,23 MiB | 247,31 MiB | 1,12 MiB | 19,7 MiB |
| Replay interno, passo 1 | 225,66 MiB | 253,03 MiB | 2,23 MiB | 22,3 MiB |
| Replay interno, passo 20 | 387,34 MiB | 398,30 MiB | 2,23 MiB | 162,0 MiB |
| Dopo il salvataggio | 390,08 MiB | 398,30 MiB | 2,23 MiB | 166,9 MiB |
| Dopo CLI e GC diagnostico finale | 311,58 MiB | 398,30 MiB | 0 | 174,4 MiB |

Il picco riproduce i **397,66 MiB** della precedente CLI non strumentata.
Si forma nel **replay interno dopo la riduzione**, non nel salvataggio.
Il salvataggio aggiunge circa 4,97 MiB di RSS corrente fra i suoi confini,
ma non supera il massimo già raggiunto. La riduzione da sola aveva massimo
247,31 MiB; non è corretto attribuirle tutto il residuo della CLI completa.

Fra i checkpoint 1 e 20 del replay il RSS corrente cresce di **161,69 MiB**;
le regioni native vuote residenti crescono di circa **139,7 MiB**, da 10 a
100 regioni. Le allocazioni native in uso restano circa **30,9 MiB**;
i piccoli blocchi Python in uso circa **131,1–131,4 MiB**. Le istantanee
restano circa 2,23 MiB e i grafi osservati sono quattro a entrambi i
checkpoint. L'aumento non è una cronologia di stati trattenuti.

Le osservazioni dei massimi per funzione collocano gli aumenti nelle chiamate
`assert_state_invariants()` dei nuovi risultati di `undo_step()`. Questo
localizza il flusso di validazione, **non la singola istruzione responsabile
dell'allocazione**: un buffer può alterare il riuso successivo dell'heap anche
senza produrre da solo un nuovo massimo. I tempi inclusivi delle funzioni
annidate non vanno sommati.

### Confronto con il checker completo nel solo replay

| Misura diagnostica | Replay con cache compressa | Checker completo nel replay |
| --- | --- | --- |
| Picco dopo riduzione | 247,31 MiB | 248,80 MiB |
| Picco della CLI | 398,30 MiB | 257,78 MiB |
| RSS al passo 20 del replay | 387,34 MiB | 235,22 MiB |
| `MALLOC_LARGE (empty)` al passo 20 | 162,0 MiB | 19,7 MiB |
| Istantanee vive al passo 20 | 2,23 MiB | 1,12 MiB |
| Piccoli blocchi Python in uso al passo 20 | 131,36 MiB | 131,25 MiB |
| Massimo stati/grafi ai checkpoint | 4 / 4 | 4 / 4 |
| RSS dopo CLI e GC finale | 311,58 MiB | 155,38 MiB |
| Tempo complessivo strumentato | 56,398 s | 62,525 s |
| Intervallo strumentato del replay | 16,140 s | 22,228 s |

Il controllo conserva l'istantanea del terminale, costruita in avanti;
gli stati nuovi del replay non costruiscono né riutilizzano istantanee.
Le sue **41 richieste di validazione** eseguono il checker completo; nel
flusso corrente sono osservate 41 richieste e 41 costruzioni/confronti di
istantanee. Il caso di controllo non disabilita gli invarianti.

La riduzione in avanti ha comportamento simile nelle due prove. Il grande
aumento delle regioni vuote nel replay sparisce usando il percorso senza
istantanee: questo rafforza l'attribuzione al **ciclo delle allocazioni della
cache nel contesto del replay interno**, dove il processo conserva anche
la mappa originale e la storia delle allocazioni dell'andata. Il replay
separato della prova precedente aveva picco 214,25 MiB. Non è stato isolato
il contributo della sola mappa originale rispetto alla storia dell'heap;
non è ricostruita la policy interna di libmalloc e non è provato quale
specifico buffer inneschi ogni regione residente.

Il checker completo è qui un controllo diagnostico con un costo temporale
osservato maggiore, **non una modifica già adottata o una raccomandazione
a rimuovere la cache globalmente**. Dopo la CLI nessuno stato né snapshot
resta vivo; il GC finale elimina tutti i grafi osservati in entrambe le
prove, ma non tutta la memoria residente. Non è dimostrato un leak illimitato.

### Esattezza, conservazione e comandi

Entrambe le corse terminano con **exit 0**, 20 passi in avanti e 20 inversi,
`step_limit`, 10 F4/10 F5, 20 scambi parziali e `not_run_nonterminal`.
Il replay interno recupera il fingerprint completo della riga sorgente.
`steps.jsonl` e `terminal.json` coincidono byte per byte fra le due prove e
con il prefisso già certificato dell'implementazione compressa. Coincidono
risultato, sorgente, configurazione e tutti e quattro gli hash di produzione.
Non è stato eseguito un ulteriore replay separato in questa diagnosi.

Nuova radice: `ct/debug/oracle-study/task5-cli-memory-phases-ww6kj7bo/`.
Contiene `phase-observation/` e `full-replay-control/`, ciascuna con
`prefix-20/`, `measurement.json`, checkpoint JSONL, allocator/vmmap e
`exact-comparison.json`; inoltre `summary.json`, `summary.txt`, script,
ledger, copie/hash dei file locali e log. Prima versione conservata in
`probe_cli-v1.py`; `probe_cli.py` aggiunge l'opzione diagnostica per il
checker completo e la sua misura. Il primo comando seguente è stato
eseguito quando `probe_cli.py` corrispondeva a `probe_cli-v1.py`; per
riprodurre esattamente la prima strumentazione usare quella versione.
Scegliere sempre nuove etichette: le directory esistenti vengono rifiutate.

Comandi effettivi da `ct/`:

```bash
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-cli-memory-phases-ww6kj7bo/probe_cli.py --label phase-observation > debug/oracle-study/task5-cli-memory-phases-ww6kj7bo/phase-observation.stdout.log 2> debug/oracle-study/task5-cli-memory-phases-ww6kj7bo/phase-observation.stderr.log
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-cli-memory-phases-ww6kj7bo/probe_cli.py --label full-replay-control --replay-validation full > debug/oracle-study/task5-cli-memory-phases-ww6kj7bo/full-replay-control.stdout.log 2> debug/oracle-study/task5-cli-memory-phases-ww6kj7bo/full-replay-control.stderr.log
../.venv/bin/python -B debug/oracle-study/task5-cli-memory-phases-ww6kj7bo/summarize_phases.py > debug/oracle-study/task5-cli-memory-phases-ww6kj7bo/summary.txt
```

Gli script registrano in `measurement.json` gli argomenti effettivi della
CLI: input assoluto della raccolta, `--map-number 1 --max-steps 20`, output
nuovo, `--ordinary-rebuild --kempe-search-limit 10000`. `ps`, `vmmap` e
statistiche native hanno accesso autorizzato; tutte le chiamate vmmap
risultano exit 0. Nessuna installazione, modifica della checkout o pulizia;
bytecode disabilitato. Hash di sorgenti e debug preesistenti verificati
prima di concludere. Revisione indipendente conclusa in sola lettura,
senza rilievi Critical/Important/Minor. Il revisore ha controllato metriche,
log nativi, scope del checker completo e conservazione, e confrontato
indipendentemente i byte dei file; non ha ripetuto test o esperimenti.
Verbale in `review.txt`. Il verdetto lascia esplicitamente aperti causalità
della singola allocazione, policy dell'allocatore, stabilità dei tempi,
crescita illimitata, ramo completo e conclusioni matematiche.

### Classificazione e prossimo passo

La diagnosi del picco residuo è completata nello scope richiesto: **fase
localizzata e componente dominante della memoria attribuita**, con limiti
espliciti sulla causalità delle singole allocazioni. Nessuna modifica di
produzione o dei test, nessuna nuova suite/smoke necessaria per questo
intervento diagnostico. Nessun nuovo errore software osservato.
`step_limit` è non conclusivo, ordinario non eseguito; **Task 5 resta aperta**
e nessuna impossibilità matematica è dimostrata.

Il prossimo intervento va progettato sul percorso di validazione del replay
interno, conservando gli invarianti e verificando il compromesso tempo/memoria.
Il controllo senza cache fornisce un riferimento concreto; una nuova
strategia di allocazione delle istantanee resta un'ipotesi da provare, non
un fix implicito. Qualunque modifica richiederà TDD e confronto esatto sullo
stesso prefisso. Catena lunga, altre mappe e validazione delle 151 mappe
restano non avviate; non serve ottimizzare il salvataggio per questo picco.

## Aggiornamento: istantanee serializzate per componenti

### Diagnosi mirata e decisione

Dopo l'autorizzazione a procedere, due nuovi processi diagnostici osservano
sempre e soltanto **riga 1, prefisso di 20 riduzioni**. Il primo separa nella
funzione reale costruzione del payload, `marshal.dumps`, `zlib.compress` e
liberazione dei temporanei. Il secondo conserva lo stesso payload e invia
le sue parti a un unico compressore incrementale, prima di qualsiasi modifica
al motore. Entrambi eseguono il replay interno con tutti gli invarianti e
confrontano i file con il prefisso precedente: exit 0, confronto esatto.

Nel primo processo, snapshot 40 del replay: `marshal` produce un buffer di
circa 4,65 MiB; dopo la compressione le sue pagine sono residenti. Liberando
quel buffer, `MALLOC_LARGE (empty)` residente passa **150,2→154,8 MiB**;
liberando il payload passa a 157,3 MiB. Fra l'inizio e la fine dello snapshot
le regioni vuote crescono da 152,7 a 157,3 MiB. Questo localizza un contributo
nel ciclo del buffer serializzato completo; non ricostruisce la policy di
libmalloc o la causalità di ogni regione. Il `physical footprint` non è RSS.

Il codice di riferimento di [CPython 3.9.6, marshal.c](https://github.com/python/cpython/blob/v3.9.6/Python/marshal.c)
mostra che `marshal.dump()` costruisce anch'esso una stringa completa prima
di chiamare `write`: cambiare soltanto API di scrittura non risolve quel
buffer. [zlibmodule.c](https://github.com/python/cpython/blob/v3.9.6/Modules/zlibmodule.c)
conferma il ridimensionamento dei buffer compressi. La variante scelta evita
il singolo input completo, senza un serializzatore personalizzato o una
politica di GC/allocatore. Ambiente locale: Python 3.9.6, zlib 1.2.12.

| Misura diagnostica | Buffer completo | Per componenti |
| --- | --- | --- |
| Picco dopo l'andata | 250,23 MiB | 296,91 MiB |
| Picco complessivo | 400,19 MiB | 311,92 MiB |
| RSS al passo 20 del replay | 389,55 MiB | 296,30 MiB |
| Regioni native vuote residenti, replay passo 1→20 | 22,3→162,0 MiB | 69,7→69,7 MiB |
| RSS dopo CLI e GC diagnostico finale | 338,78 MiB | 251,70 MiB |
| Tempo complessivo strumentato | 64,761 s | 64,972 s |

Nel controllo, all'ultimo snapshot del replay, il maggiore buffer serializzato
è **2.273.189 byte**, contro **4.875.700 byte** complessivi del riferimento;
restano lo stesso payload e lo stesso numero di componenti. La memoria
migliora nel replay interno ma peggiora nell'andata. I checkpoint interni
sono diversi per riflettere i due flussi: più chiamate ps/vmmap nel primo,
e riferimenti locali diagnostici che possono prolungare la vita dei dati
fino all'uscita della funzione. Questi tempi non sono benchmark comparabili
alla CLI ordinaria. Nessuna raccolta forzata durante l'algoritmo; GC solo
alla fine del diagnostico. La successiva CLI senza osservatori verifica
che il miglioramento complessivo non dipenda soltanto dalla strumentazione.

### Implementazione e TDD

Modificata soltanto `_invariant_snapshot()` nel motore. I **14 valori** del
payload vengono codificati separatamente con `marshal` versione 2, nello
stesso ordine, e compressi con **un unico `zlib.compressobj(1)`**. Un solo
`flush()` finale; le porzioni compresse vengono unite in un `bytes` immutabile.
Il flusso decompresso contiene i valori autodelimitanti consecutivi, senza
la precedente intestazione della tupla esterna. È una rappresentazione
privata, mai salvata nei certificati o caricata dal motore: non richiede
migrazioni dei file. Il confronto continua a coprire esattamente tutti i
valori, tipi primitivi e identità, senza sostituirli con hash.

Restano buffer proporzionali al componente più grande, il payload Python
e i pezzi compressi; **non è memoria costante** e non elimina tutte le
allocazioni native residenti. Nessuna nuova opzione CLI, dipendenza o wrapper
di delegazione. AST di tutte le altre funzioni, incluso checker completo,
invalidazione, trasferimento e riuso della cache, invariato.

- RED del nuovo test di costo: **1 FAIL / 34 PASS**, exit 1; il vero encoder
  produceva un solo buffer di 1.400 byte. Il test osserva le dimensioni degli
  output reali, senza simulare l'encoder né usare soglie RSS/tempo.
- Adeguamento del payload atteso indipendente su theta alla sequenza di
  valori: secondo RED **2 FAIL / 33 PASS**, exit 1, prima della modifica.
- GREEN mirato: **249 PASS in 0,92 s**. Suite completa: **356 PASS in 1,20 s**.
- Smoke S1 `-r2 10`: exit 0, ricostruzione corretta/isomorfa, 16 vertici e
  24 archi; gli artefatti fissi precedenti sono ripristinati e verificati.

### Misure di produzione ed esattezza

Una sola nuova CLI di produzione del prefisso e un solo replay in **processo
nuovo**, misurati con `/usr/bin/time -l`, senza osservatori interni:

| Misura | Compressione monolitica precedente | Per componenti |
| --- | --- | --- |
| Catena, tempo registrato nel manifest | 34,574952 s | 37,668683 s |
| CLI completa, tempo reale | 50,15 s | 54,49 s |
| CLI completa, massimo RSS | 397,65625 MiB | 311,75000 MiB |
| Replay separato, tempo reale | 12,92 s | 13,80 s |
| Replay separato, massimo RSS | 214,25000 MiB | 219,37500 MiB |

Il picco CLI cala del **21,60%**; la catena impiega circa **8,95%** in più.
Il replay separato usa **2,39%** di RSS in più. Sono singole osservazioni:
non dimostrano stabilità delle differenze temporali né prestazioni su catene
più lunghe. Il controllo storico con checker completo soltanto nel replay
resta un riferimento diagnostico (257,78 MiB), non una modifica adottata.

Risultato identico: `step_limit`, 20 passi, **10 F4 + 10 F5**, 20 scambi
parziali, nessuno completo; V/E/F **16064/24096/8034→16024/24036/8014**.
Cammini: totale 1607 archi, mediana 4, massimo 1519; lista identica alle
precedenti. Ordinario `not_run_nonterminal`, budget Kempe 10000: non eseguito.
Replay interno esatto; nel processo separato `exact_replay`, `source_matches`
e `edge_multiset_matches` sono tutti veri.

`steps.jsonl` e `terminal.json` sono identici byte per byte a tutti e cinque
i prefissi storici confrontati. SHA-256 rispettivamente
`22e87b0a050ebbc30ce4203b8e85d650a0fc384783bb898027f441b0b4dcb98a` e
`57e699dd1cf7096c5697d36cf896b6f136b598b7564a1bd56630d4491e135ca2`.
Restano identici sorgente, configurazione e risultato del manifest.
L'hash del motore diventa
`f0ecf23afcf2916d4f343b83f6a1ff09c8a11b0e180788439640906b2e601a37`;
gli altri tre hash del codice sono invariati.

Sul terminale caricato, `force=True` supera nuovamente tutti gli invarianti
e non modifica il fingerprint. La vecchia funzione salvata viene eseguita
sugli stessi oggetti: ricostruendo la tupla dai 14 valori del nuovo flusso,
la codifica `marshal` coincide **esattamente** con il vecchio payload.
4.863.570 byte vecchi complessivi; componente massimo 2.267.539 byte;
evidenza compressa 1.167.296 byte nel processo di confronto. Le identità
Python possono variare quei byte fra processi; non variano i certificati.

### Conservazione, comandi e classificazione

Radice nuova: `ct/debug/oracle-study/task5-snapshot-buffers-hk5diq7u/`.
Contiene copie/hash iniziali, script distinti `probe_buffers.py` e
`probe_components.py`, `buffer-stages/`, `component-control/`, log RED/GREEN,
suite e smoke, `prefix-20/`, tempi/RSS, `comparison.json`,
`forced-terminal-verification.json`, `commands.md`, ledger e diff isolato.
Entrambe le diagnosi hanno eseguito lo stesso prefisso autorizzato; nessuna
altra mappa. La modalità opzionale `chunked-zlib` del primo script non è
stata eseguita. I comandi effettivi sono riportati sotto.

Preservati checkout, modifiche locali e artefatti ignorati. Nessun commit,
reset, stash, pulizia o nuova checkout. Bytecode disabilitato, cache pytest
disabilitata e directory temporanee nuove. Il wrapper dello smoke conserva
in `verification-generated-debug/` i nuovi file e ripristina quelli fissi;
i 14 file precedenti corrispondono agli hash iniziali. Rispetto alle copie
iniziali cambiano soltanto motore, test della cache, architettura, sviluppo,
piano e questo resoconto; gli altri 12 file locali restano identici.
Revisione indipendente finale conclusa in sola lettura, senza rilievi
Critical/Important/Minor; verbale in `review.txt`. Il revisore ha controllato
codice, test, log e conservazione senza ripetere gli esperimenti. Il limite
di utilizzo che l'aveva interrotto è stato superato riprendendo lo stesso
revisore. Il giudizio conserva i limiti dichiarati su regole matematiche
preesistenti, catena completa, ordinario grande, altre mappe, stabilità
statistica e causalità completa dell'allocatore.

`step_limit` è un **arresto non conclusivo** per budget, non un errore software;
`not_run_nonterminal` è ordinario non eseguito. I RED sono fallimenti di
requisito attesi prima del fix, non insuccessi matematici. Nessun nuovo errore
software osservato nel motore e nessuna impossibilità matematica dimostrata.
**Task 5, catena completa e confronto ordinario restano aperti.** Nessuna
catena lunga, altra mappa o validazione delle 151 mappe è stata avviata.

L'intervento circoscritto è verificato con il compromesso dichiarato. Un
ulteriore limite ai buffer per componente o un'estensione del numero di
passi richiedono un prossimo intervento esplicito; non sono avviati né
impliciti in questo risultato.

```bash
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-snapshot-buffers-hk5diq7u/probe_buffers.py --label buffer-stages > debug/oracle-study/task5-snapshot-buffers-hk5diq7u/buffer-stages.stdout.log 2> debug/oracle-study/task5-snapshot-buffers-hk5diq7u/buffer-stages.stderr.log
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-snapshot-buffers-hk5diq7u/probe_components.py --label component-control > debug/oracle-study/task5-snapshot-buffers-hk5diq7u/component-control.stdout.log 2> debug/oracle-study/task5-snapshot-buffers-hk5diq7u/component-control.stderr.log
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_validation_cache.py -q -p no:cacheprovider --basetemp=debug/oracle-study/task5-snapshot-buffers-hk5diq7u/pytest-red > debug/oracle-study/task5-snapshot-buffers-hk5diq7u/tests-red.log 2>&1
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_validation_cache.py -q -p no:cacheprovider --basetemp=debug/oracle-study/task5-snapshot-buffers-hk5diq7u/pytest-red-stream > debug/oracle-study/task5-snapshot-buffers-hk5diq7u/tests-red-stream.log 2>&1
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_validation_cache.py tests/test_oracle_reduction.py tests/test_oracle_bridges.py -q -p no:cacheprovider --basetemp=debug/oracle-study/task5-snapshot-buffers-hk5diq7u/pytest-focused > debug/oracle-study/task5-snapshot-buffers-hk5diq7u/tests-focused.log 2>&1
../.venv/bin/python -B debug/oracle-study/task5-snapshot-buffers-hk5diq7u/run-checks.py
/usr/bin/time -l env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --input maps_3000_maps_of_8000_faces.colored.planar --map-number 1 --max-steps 20 --output debug/oracle-study/task5-snapshot-buffers-hk5diq7u/prefix-20 --ordinary-rebuild --kempe-search-limit 10000 > debug/oracle-study/task5-snapshot-buffers-hk5diq7u/prefix.stdout.log 2> debug/oracle-study/task5-snapshot-buffers-hk5diq7u/prefix.stderr-time.log
/usr/bin/time -l env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py --replay debug/oracle-study/task5-snapshot-buffers-hk5diq7u/prefix-20 > debug/oracle-study/task5-snapshot-buffers-hk5diq7u/replay.stdout.log 2> debug/oracle-study/task5-snapshot-buffers-hk5diq7u/replay.stderr-time.log
env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache uv run --python ../.venv/bin/python python debug/oracle-study/task5-snapshot-buffers-hk5diq7u/compare-results.py > debug/oracle-study/task5-snapshot-buffers-hk5diq7u/comparison.stdout.log 2> debug/oracle-study/task5-snapshot-buffers-hk5diq7u/comparison.stderr.log
```

`run-checks.py` invoca con PYTHONDONTWRITEBYTECODE=1 e UV_CACHE_DIR=/private/tmp/maps-coloring-uv-cache:

```bash
uv run --python ../.venv/bin/python python -m pytest tests -q -p no:cacheprovider --basetemp=/Users/mario.stefanutti/mario/programming/github-stefanutti/maps-coloring-python/ct/debug/oracle-study/task5-snapshot-buffers-hk5diq7u/pytest-suite
uv run --python ../.venv/bin/python python 4ct.py -s1 -r2 10
```

Exit 1 soltanto nei due RED attesi (1 failed/34 passed e 2 failed/33 passed). GREEN 249 passed; suite 356 passed; smoke, due diagnosi, CLI, replay e confronto exit 0. Il wrapper conserva e ripristina i debug fissi in finally; argv/exit in verification-commands.json. ps/vmmap e time -l autorizzati tramite escalation per osservare i propri processi. Nessun auto-review rejection.


## Aggiornamento: prefisso autorizzato di 100 riduzioni totali

29 settembre 2026. Esecuzione Superpowers inline nella checkout esistente,
branch `feature/machine-learning`, HEAD `08dd2e911d25a35f2c32320403f90020ba5a7e01`.
Autorizzazione limitata a **100 riduzioni TOTALI della sola riga 1**, partendo
nuovamente dall'input originale. Una sola andata: nessuna ripartenza dal
terminale a 20 e nessuna somma di corse 20+50+100. Motore, test e cache
invariati. Catena completa, altre mappe e validazione delle 151 mappe escluse.

### Baseline e provenienza

I quattro hash di produzione coincidono con il manifest del riferimento
`ct/debug/oracle-study/task5-snapshot-buffers-hk5diq7u/prefix-20/`.
In particolare, motore `f0ecf23afcf2916d4f343b83f6a1ff09c8a11b0e180788439640906b2e601a37`.
Ricostruiti in memoria i file finali dal suo `before/` e `isolated.diff`:
tutti coincidono con la checkout, inclusi test e documenti; anche i file
rimasti invariati, HEAD e i due hash degli artefatti di riferimento coincidono.
Il SHA-256 della riga sorgente è
`41e6b1a2c7e4f84d0be13a036522797b68312ee200bb2f58c9e0c7e0208f31f2`.
Percorso assoluto, riga 1, Python 3.9.6, NetworkX 3.2.1, configurazione e
quattro hash sono nel nuovo manifest. Mac ARM64, macOS 26.5 (25F71),
come registrato dai log vmmap. Nessuna nuova dipendenza o impostazione malloc.

**356 test PASS, smoke S1 PASS e revisione senza rilievi appartengono alla
baseline precedente. Non sono nuove esecuzioni di questa sessione.**
Non sono state ripetute suite e smoke perché produzione e test non cambiano.
Le verifiche nuove sono prefisso, checkpoint, confronti dei certificati,
replay separati, checker completo forzato del terminale e conservazione.

### Risultato certificato

Esito **`step_limit`**, 100 passi, V/E/F **16064/24096/8034 →
15864/23796/7934**.
**F2=0, F3=1, F4=51, F5=48**; 100 scambi parziali e due cicli completi
(ai passi 69 e 96, lunghezze 20 e 14). Cammini parziali: totale
13811 archi, mediana 4.0, massimo 6773.
La lista completa è in `comparison.json`; il massimo compare al passo 66.
L'ordinario è `not_run_nonterminal` (opzione richiesta alla CLI, budget Kempe
10000), quindi non è stato eseguito.

I primi 20 certificati JSONL coincidono **byte per byte** con il riferimento:
SHA-256 `22e87b0a050ebbc30ce4203b8e85d650a0fc384783bb898027f441b0b4dcb98a`.
La continuità dei fingerprint e i conteggi del prefisso salvato sono verificati
da `load_run()`. Hash dei nuovi file:

- `steps.jsonl`: `8a49a4c6f490d7781d7de136ac7f49878a15d80f2a4d82f49dafbde3299af909`.
- `terminal.json`: `2650683d968cc0c35fdef57ad57b44ad34728c0ba17d29a93d9ce0a8275da592`.

Replay interno esatto; entrambi i replay in processi nuovi restituiscono
`exact_replay`, `source_matches` ed `edge_multiset_matches` veri, 100 inversi.
Sul terminale salvato, nuovo `assert_state_invariants(..., force=True)` PASS
e fingerprint invariato. Tutti gli invarianti ordinari restano attivi nella
corsa: cubicità, colori, loop/ponti, occorrenze keyed, embedding e FaceIndex.
L'osservatore conta nell'andata 117 `plan_step`, 418 richieste di validazione,
418 snapshot e 201 checker completi; nel replay interno 201 richieste/snapshot
e 101 checker completi. Il riuso delle verifiche è operativo, non disattivato.
La richiesta di validazione del salvataggio usa l'alias del runner non
strumentato: è contato lo snapshot (uno), non l'entrata nell'alias.

### Tempi separati e overhead

L'osservatore sotto debug chiama le funzioni originali e la vera `runner.main()`;
non sostituisce snapshot, controlli, ordinamento, scelta delle candidate o
salvataggio. Avvolge fasi/apply/undo e conta chiamate; mantiene soltanto weakref
agli stati/grafi/testimoni. Campiona **dopo** il ritorno di apply/undo ai passi
20, 50 e 100, oltre ai confini delle fasi. Questi punti differiscono dai vecchi
checkpoint dentro `_install`: non sono confronti identici delle vite temporanee.

| Fase | Tempo osservato s | Checkpoint inclusi s | Tempo meno checkpoint s |
| --- | ---: | ---: | ---: |
| Andata 100 | 186.192 | 1.359 | 184.833 |
| Replay interno 100 | 81.394 | 1.362 | 80.032 |
| Salvataggio | 0.453 | 0 | 0.453 |

L'intervallo della CLI osservata è **271.521 s**,
di cui **5.847 s (2.15%)**
misurati nei checkpoint; sottraendoli: 265.674 s.
Questo costo comprende ps/vmmap, lettura dei contatori, statistiche Python e
scritture del checkpoint; la durata totale dei checkpoint, inclusi quelli
successivi alla CLI, è 6.681 s.
**Non è tutto l'overhead**: restano wrapper/contatori/weakref e alterazioni
dell'heap, del GC e dello scheduling non quantificate. Sottrarre i tempi
non ricostruisce una corsa senza strumentazione. Non sono usati tracemalloc,
profiler, raccolte forzate o sostituzioni dell'allocatore durante la CLI.
Il solo GC forzato avviene dopo il suo ritorno, come diagnosi finale.

`time -l` sull'intero processo osservato: **272.57 s,
390.92 MiB di massimo RSS**. Include import, osservatore,
GC diagnostico finale e scritture successive; non coincide con l'intervallo
CLI. Il tempo catena nel manifest (187.069658 s)
include anche i checkpoint ai confini del wrapper: per separare le fasi
usare `measurement.json`, non interpretarlo come benchmark non strumentato.

Confronto con le singole misure storiche senza osservatore, a 20 passi:
andata **37,668683 s**, CLI **54,49 s / 311,75 MiB**, replay separato
**13,80 s / 219,375 MiB**. Qui l'andata meno checkpoint è
4.91 volte il tempo storico,
con cinque volte i passi; il massimo RSS dell'intero processo osservato è
25.40% più alto.
Sono percorsi e strumentazioni diversi: nessun rapporto è una garanzia.
Nel medesimo run, gli intervalli 1–20, 21–50 e 51–100 costano rispettivamente
1,768, 1,794 e 1,913 s/passo, al netto dei checkpoint: crescita del costo
cumulativo approssimativamente proporzionale nel tratto osservato, con costo
medio maggiore nell'ultimo intervallo. Non si estrapola fino alle 8031 riduzioni.

### Memoria ai checkpoint

Tempi cumulativi nella rispettiva fase al netto dei checkpoint; tutte le
memorie in MiB. «Vuote residenti» somma le colonne RESIDENT di tutte le righe
`MALLOC_* (empty)` di vmmap (valori nativi arrotondati).

| Checkpoint | Tempo s | RSS corrente | Picco storico | Snapshot vivi | Blocchi piccoli Python in uso | Native vuote residenti |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| chain-step-20 | 35.366 | 260.62 | 290.28 | 1.119 | 104.81 | 73.90 |
| chain-step-50 | 89.174 | 246.25 | 295.23 | 1.121 | 105.34 | 50.80 |
| chain-step-100 | 184.826 | 286.80 | 308.03 | 1.122 | 109.35 | 83.10 |
| replay-step-20 | 17.160 | 309.17 | 325.05 | 2.244 | 135.53 | 83.60 |
| replay-step-50 | 40.921 | 298.84 | 326.92 | 2.255 | 136.15 | 68.80 |
| replay-step-100 | 80.032 | 298.62 | 390.92 | 2.258 | 136.49 | 67.60 |

RSS corrente proviene da `ps`; il picco storico da `getrusage`, in byte su
questo Mac, e non si azzera fra fasi. Le letture non sono simultanee e non
misurano esattamente la stessa finestra. Il «physical footprint» riportato
da vmmap **non è RSS**. Le regioni native vuote residenti sono memoria
libera per l'allocatore ma ancora residente: non sono snapshot né oggetti
Python vivi. I byte di blocchi piccoli Python in uso escludono allocazioni
grandi e includono oggetti non ancora raccolti; non sono un censimento di
tutti i dati logicamente raggiungibili. Queste colonne si sovrappongono e
**non vanno sommate** per ricostruire RSS. Le statistiche native grezze e i
log allocator sono conservati, senza attribuire il residuo a una causa unica.

Ai checkpoint: due stati nell'andata, tre nel replay; snapshot deduplicati
circa 1,12 MiB e 2,25 MiB, senza storia di uno snapshot per passo. I testimoni
trattenuti crescono 20→50→100 e restano 100 durante il replay. I grafi non
ancora raccolti sono 3 nell'andata e 4 nel replay: le weakref contano oggetti
esistenti, inclusi eventuali cicli già irraggiungibili, non soltanto dati vivi
raggiungibili. Il nuovo `steps.jsonl` occupa 2028673 byte:
la storia dei certificati cresce, anche se non contiene mappe intere per passo.

Il picco sale **326,92→390,92 MiB fra i checkpoint 50 e 100 del replay**,
mentre l'RSS ai due estremi resta circa 299 MiB e le regioni native vuote
residenti non crescono. La finestra è fra le letture e include il lavoro
dell'osservatore al checkpoint 50, svolto dopo la lettura del picco.
Questo localizza un massimo transitorio nel replay strumentato, senza
attribuirlo al motore anziché all'osservatore: non identifica passo,
allocazione o causa del picco. Nessun
checkpoint campiona il suo istante esatto. A fine CLI: zero stati, zero
snapshot, zero testimoni, quattro grafi non ancora raccolti; RSS 297,20 MiB.
Dopo il solo GC diagnostico finale: zero grafi, RSS 208,20 MiB, picco storico
invariato. Non è provata né memoria costante né una perdita illimitata.

### Replay separato e inconveniente di misura

Primo nuovo processo: output esatto, **66,64 s real / 65,66 user / 0,76 sys**;
`time -l` termina poi con exit 1 perché il sandbox nega
`sysctl kern.clockrate`. La misura RSS manca. È un errore della
strumentazione/ambiente, distinto da errore del motore o violazione di
invariante; non è un auto-review rejection. Artefatti mantenuti in
`separate-replay/`.

Verificato l'accesso con `time -l /usr/bin/true`, quindi ripetuto **soltanto
il replay**, in un altro processo e nella nuova `separate-replay-timed/`.
Exit 0, esattezza completa; misura senza osservatori interni:
**65.18 s real / 64.29 user / 0.79 sys,
349.750 MiB massimo RSS**. Rispetto alla baseline a 20 inversi:
4.72 volte il tempo e
59.43% di picco RSS in più.
Non si combinano tempo del primo tentativo e memoria del secondo. Le due
corse non costituiscono un benchmark statistico né replicano l'heap del
replay interno dopo l'andata.

### Artefatti, conservazione e prossimo passo

Nuova radice **`ct/debug/oracle-study/task5-prefix100-izztpr64/`**. `observed-run/prefix-100/` contiene il prefisso;
`observed-run/measurement.json`, `samples.jsonl`, log vmmap/allocator e log
esterni conservano le misure; `comparison.json` e
`verification/forced-terminal-verification.json` i confronti. Script
`observe.py`, `analyze.py`, `update_docs.py`, `preserve.py`; provenienza,
comandi effettivi ed esiti in `commands.md` e `progress.md`.

Inventario SHA-256 di 5023 file preesistenti, inclusi artefatti ignorati,
cache e ambiente virtuale, esclusa `.git`; hash dell'intero dataset solo
per conservazione, senza parsare/validare altre righe. Controllo finale in
`preservation.json`: soltanto piano e questo resoconto cambiano. Nessun
commit, reset, stash, pulizia, nuova checkout, installazione o scrittura
sugli artefatti storici. Bytecode disabilitato; cache uv preesistente
conservata. Git fsmonitor segnala inizialmente un errore IPC nel sandbox:
le letture successive usano `git -c core.fsmonitor=false`, senza cambiare
configurazione. Il dettaglio della revisione finale è in `review.txt`.

**Arresto non conclusivo per budget**, nessun arresto per candidata non
certificata e nessuna violazione degli invarianti osservata. L'inconveniente
`time/sysctl` è ambientale e non diventa un esito matematico. Nessuna
impossibilità matematica dimostrata. **Task 5 e catena completa restano aperte**.

Prossimo passo proposto, non avviato: diagnosi mirata del picco transitorio
nel replay interno fra le letture 50 e 100, includendo il checkpoint 50 e
separando l'osservatore dalle inversioni, restando su riga 1 e budget
massimo 100 in una nuova sessione autorizzata, con osservazione leggera del
picco per passo. La memoria ai checkpoint e gli snapshot non spiegano da
soli il massimo di 390,92 MiB. Prima di un ulteriore aumento del budget è
utile localizzarlo; nessuna modifica del motore è implicita nella proposta.


## Aggiornamento: ricerca del picco transitorio nel replay interno

29 settembre 2026, Superpowers `executing-plans` inline, stessa checkout Mac,
branch `feature/machine-learning`, HEAD `08dd2e911d25a35f2c32320403f90020ba5a7e01`.
**Una sola nuova andata di 100 riduzioni TOTALI della sola riga 1 dall'input
originale, seguita dal replay interno nello stesso processo.** Nessun replay
separato aggiuntivo: era consentito, ma non ricostruisce la storia dell'heap
e non serve a ripetere l'esattezza già controllata internamente e sui file.

**Il transitorio precedente di 390,92 MiB non si è riprodotto.** Questa
corsa non può attribuire retroattivamente quel picco al motore o
all'osservatore. Il massimo dell'intero nuovo processo è **321,078125 MiB**,
già raggiunto prima del replay. Nessun incremento del massimo storico
durante le 100 inversioni, i loro checkpoint o i probe. Non si avvia
automaticamente un'altra andata per cercare il fenomeno.

### Baseline, accesso e strumentazione

Radice nuova: `ct/debug/oracle-study/task5-replay-peak-in1wh35K/`.
`prepare.py` confronta **5027** impronte/condizioni con la sessione precedente,
inclusi documenti finali ricostruiti dal suo `session-docs.diff`: tutte
coincidono. Inventario iniziale di **5087 file** preesistenti, inclusi cache,
file non tracciati e debug ignorati, esclusa `.git` e la nuova radice.
La lettura completa del dataset serve solo all'hash di conservazione;
nessuna nuova validazione delle 151 mappe.

Prima dell'unica corsa, `preflight.py` verifica con lo stesso accesso host
`time -l /usr/bin/true`, `ps` e `vmmap -summary` sul proprio processo:
**exit 0 per tutti**, RSS disponibile. Nessun fallimento della strumentazione
di misura o auto-review rejection. La prima lettura `git status` segnala
il già noto errore IPC di fsmonitor nel sandbox; le successive usano
`git -c core.fsmonitor=false`, senza cambiare configurazione o ripetere corse.
L'ABI di `MACH_TASK_BASIC_INFO`
è ricavata dall'header SDK locale `mach/task_info.h`: struttura di 48 byte,
12 parole, flavour 20. RSS nativo e `ps` coincidono nel preflight.
Le 10000 letture native preliminari costano **0,2154885 s** in un processo
piccolo: calibrazione, non stima sostitutiva dell'overhead della corsa.

`observe.py`, esterno al motore, chiama le implementazioni originali.
Mantiene il lavoro dei checkpoint precedenti: `ps`, weakref agli oggetti,
byte delle cache deduplicati, `vmmap` e statistiche dell'allocatore Python.
Aggiunge letture prima/dopo ogni sottoperazione del checkpoint, ogni
inversione e, nel replay, snapshot, checker completo, fingerprint,
costruzione dello stato temporaneo, controllo della riduzione e installazione.
Ogni probe legge prima e dopo il proprio piccolo record JSONL; **2310 eventi**
sono scritti progressivamente su disco, senza trattenerne la storia in memoria.
Al massimo due checkpoint aggiuntivi sarebbero stati ammessi dopo un'inversione
successiva alla 50 con almeno 16 MiB di nuovo picco: **nessuno è scattato**.

`getrusage().ru_maxrss` e il massimo Mach sono storici; il `resident_size`
Mach è RSS corrente. `malloc_zone_statistics` descrive byte allocati/in uso,
**non byte residenti** e non tutti gli oggetti Python. `vmmap` fornisce
le categorie native residenti ai checkpoint; il suo physical footprint
non è RSS. Le letture sono sequenziali, non simultanee. Nessun tracemalloc,
profiler, cambiamento dell'allocatore o GC forzato, neppure dopo la CLI.
Gli invarianti e la cache rimangono attivi.

### Checkpoint 50 e localizzazione possibile

| Lettura nel checkpoint 50 del replay | RSS MiB | Massimo storico MiB |
| --- | ---: | ---: |
| Prima dell'osservazione (evento 1166) | 263,250000 | 321,078125 |
| Dopo `ps` (1168) | 263,250000 | 321,078125 |
| Dopo conteggio oggetti/cache (1169) | 263,250000 | 321,078125 |
| Dopo `vmmap` e scrittura del suo output (1170) | 263,265625 | 321,078125 |
| Dopo statistiche Python e osservazione (1172) | 263,265625 | 321,078125 |

Checkpoint: **0,501631 s**, variazione RSS **+16 KiB**, byte malloc in uso
**+6528**, nessun nuovo picco. Il piccolo incremento RSS è osservato
nell'intervallo che contiene `vmmap` e la scrittura del suo output: non
si attribuisce a una specifica allocazione o alla sola chiamata vmmap.
Anche la lettura all'ingresso dell'inversione 51 mantiene lo stesso massimo,
coprendo la coda di scrittura/contabilizzazione del checkpoint 50.
La finestra della vecchia misura resta correttamente **fra letture 50 e 100,
inclusa osservazione 50**: il nuovo risultato non restringe retroattivamente
quella finestra alle sole inversioni 51–100.

Il maggiore RSS **campionato ai confini delle funzioni del replay** è
**267,046875 MiB**, dopo il checker completo dell'inversione **87**
(evento 1976). È un massimo dei campioni, non il massimo transitorio
effettivo del replay: un transitorio interno non campionato potrebbe aver
raggiunto un valore superiore, fino al massimo storico di 321,078125 MiB,
senza aggiornarlo. Nessun nuovo incremento storico implica quindi assenza
di superamento della soglia precedente, non assenza di transitori.

I tre incrementi storici registrati sono prima del replay. L'ultimo porta
293,359375→321,078125 MiB fra la lettura finale del checkpoint 20
dell'andata e quella iniziale del 50; include la coda del checkpoint 20.
L'andata non ha la risoluzione per funzione del replay: **non si attribuisce
quel massimo a un passo o a una funzione specifici**.

### Dati presenti e memoria libera ma residente

| Checkpoint replay | RSS corrente MiB | Snapshot unici MiB | Blocchi piccoli Python in uso MiB | Native vuote residenti MiB |
| --- | ---: | ---: | ---: | ---: |
| 20 | 260,000 | 2,249 | 135,571 | 34,003 |
| 50 | 263,250 prima / 263,266 dopo | 2,236 | 136,190 | 36,003 |
| 100 | 265,063 | 2,269 | 136,535 | 36,003 |

Tre stati osservati, quattro grafi non ancora raccolti e 100 testimoni
ai tre checkpoint. Le weakref contano oggetti ancora esistenti, inclusi
grafi ciclici eventualmente irraggiungibili: non sono una prova di
raggiungibilità logica. Gli snapshot non conservano una mappa per passo;
i certificati restano la storia di 100 passi (2028673 byte nel JSONL).
Non è una contabilità completa di tutti i dati vivi o dei temporanei.

Al checkpoint 50 precedente: RSS 298,84 MiB, blocchi piccoli Python
136,15 MiB, regioni vuote residenti 68,80 MiB. Qui i blocchi piccoli hanno
dimensione simile, mentre le regioni vuote residenti sono circa **32,80 MiB
in meno**, rispetto a circa **35,59 MiB** di RSS in meno prima dell'osservazione.
Questo distingue una componente importante della differenza **ai checkpoint**;
non spiega il vecchio transitorio di 390,92 MiB, mai campionato con vmmap.
Snapshot, blocchi Python, heap nativo e RSS si sovrappongono: non sommarli.

A fine CLI: zero stati, snapshot e testimoni osservati; quattro grafi
non ancora raccolti, RSS 264,766 MiB e regioni vuote residenti 55,20 MiB.
Nessun GC finale eseguito. Non si conclude memoria costante, leak illimitato,
assenza di dati ciclici o una particolare policy interna di libmalloc.

### Tempi e limiti dell'overhead

| Fase | Tempo osservato s | Checkpoint s | Probe fuori checkpoint s | Tempo meno costi misurati s |
| --- | ---: | ---: | ---: | ---: |
| Andata | 182,867705 | 1,358522 | 0,000173 | 181,509010 |
| Replay interno | 81,074329 | 1,423436 | 0,217003 | 79,433890 |
| Salvataggio | 0,454996 | 0 | 0,000190 | 0,454806 |

Intervallo CLI osservato **267,832504 s**. Checkpoint diretti **5,861574 s**,
probe fuori checkpoint **0,217366 s**: totale misurato **6,078941 s
(2,270%)**, senza sommare due volte i probe interni ai checkpoint.
Sottraendoli si ottengono **261,753563 s**, non un tempo non strumentato.
`time -l` dell'intero processo: **268,50 s real, 262,33 user, 5,40 sys**,
massimo RSS **336674816 byte = 321,078125 MiB**. Include avvio, import,
checkpoint successivo alla CLI e scritture finali.

Restano non quantificati wrapper/contatori/weakref, piccoli tratti fra probe,
ritenzione dei valori di ritorno durante l'osservazione, cambiamenti della
storia dell'heap, GC naturale, scheduling e carico del Mac. Anche il costo
di memoria degli osservatori può influenzare le allocazioni successive.
Gli osservatori sono più dettagliati di quelli precedenti: questa singola
corsa non è un confronto controllato né un miglioramento del motore.
Le differenze rispetto ai precedenti 184,83/80,03 s e 390,92 MiB non
giustificano un'ottimizzazione o l'attribuzione del picco alla strumentazione.

### Esattezza, conservazione e classificazione

CLI exit 0: **`step_limit`, 100 passi**, F3=1/F4=51/F5=48, 100 cammini e
due cicli; V/E/F 16064/24096/8034→15864/23796/7934. Risultato, sorgente,
configurazione e quattro hash di produzione identici al riferimento.
**Tutti i 100 certificati e terminal.json coincidono byte per byte**:
SHA-256 `8a49a4c6f490d7781d7de136ac7f49878a15d80f2a4d82f49dafbde3299af909`
e `2650683d968cc0c35fdef57ad57b44ad34728c0ba17d29a93d9ce0a8275da592`.
Replay interno esatto; caricamento del nuovo prefisso e checker completo
del terminale con `force=True` PASS, fingerprint invariato. Questa verifica
separata non esegue andate o replay. Nel replay: 201 richieste/snapshot,
101 checker completi, come nella baseline; il riuso resta operativo.

Produzione e test invariati. Suite **356 PASS e smoke S1 sono storici**,
non rieseguiti. Modificati soltanto questo resoconto e il piano; tutti i
file preesistenti verificati tramite `preservation.json`. Nuovi script,
misure e una cache uv dedicata sotto la nuova radice, bytecode disabilitato.
Nessun commit, reset, stash, pulizia, nuova checkout o modifica del dataset.
Log, provenienza e comandi effettivi: `commands.md`, `progress.md`,
`effective-argv.json`, `observed-run/measurement.json`, `samples.jsonl`,
`events.jsonl`, `peak-increments.json`, `event-summary.json`,
`comparison.json`, `verification/terminal.json` e `review.txt`.

L'arresto è **non conclusivo per budget**, non per candidata; nessun errore
del motore/della misura o violazione degli invarianti osservato. La mancata
riproduzione del picco è un **limite diagnostico**, non un fallimento
matematico. Ordinario `not_run_nonterminal`; **Task 5 e catena completa aperte**.
Nessuna impossibilità matematica dimostrata.

### Prossimo esperimento proposto, non eseguito

Prima di ottimizzare o aumentare il budget, cercare la riproducibilità
del picco con una nuova autorizzazione circoscritta: **una sola andata
di massimo 100 riduzioni della riga 1 dall'originale e replay interno**,
ripartendo dall'osservatore precedente e aggiungendo soltanto letture
`ru_maxrss`/RSS ai confini di ogni inversione e prima/dopo il checkpoint 50.
Evitare in quella prova i wrapper sulle funzioni interne e le letture
malloc per evento, mantenendo cache/invarianti e GC naturale.
Registrare overhead, tutti i certificati e gli stessi limiti: sarebbe una
prova di riproducibilità con minore strumentazione, non un A/B conclusivo.
Se il picco ritorna, localizzare prima il segmento e progettare poi una
misura mirata dei temporanei; se non ritorna, resta incerta la causalità.
Nessuna esecuzione ulteriore o modifica del motore è implicita nella proposta.

## Aggiornamento: ripetizione con sonde leggere

29 settembre 2026. Superpowers `executing-plans` inline, stessa checkout
Mac e HEAD `08dd2e911d25a35f2c32320403f90020ba5a7e01`.
**Una sola andata di 100 riduzioni TOTALI della riga1 dall'originale e
replay interno nello stesso processo. Picco 390,921875 MiB non riprodotto:**
nuovo massimo **298.125000 MiB**; incrementi storici osservati nel replay:
**0**. Il massimo è già raggiunto prima del replay, fra la lettura
finale del checkpoint 20 e quella iniziale del checkpoint50 dell'andata
(inclusa la coda 20, senza risoluzione per singolo passo). Non si avviano
altre corse.

Artefatti canonici della sessione: `ct/debug/oracle-study/task5-minimal-peak-s6LAt3x4/`.
`comparison.json`, `event-summary.json` e `peak-increments.json` contengono
numeri e segmenti completi; `commands.md` i comandi effettivi,
`artifact-provenance.json` le impronte, `preservation.json` la conservazione,
`review.txt` la revisione. Si evitano duplicazioni dei JSON nel piano.

### Strumentazione e confini osservati

Baseline 5091/5091; inventario 5163 file, inclusi non tracciati, cache e debug
ignorati, esclusi `.git` e la nuova directory. Verificati anche 17 controlli
sulla provenienza e sui confronti delle diagnosi precedenti. Preflight
senza riduzioni: time/ps/vmmap exit0, RSS Mach coerente con ps; dettagli
in `preflight/`. Python 3.9.6 da `ct/`, bytecode disabilitato e cache uv nuova.

`observe.py` deriva da `task5-prefix100-izztpr64/observe.py`; tutte le
differenze sono in `observer.diff`. Mantiene checkpoint, ps/vmmap,
statistiche malloc/Python e contatori originali delle quattro funzioni.
Aggiunge soltanto letture `ru_maxrss`/RSS corrente Mach prima/dopo ogni
inversione e ogni checkpoint, scritte progressivamente: **228 eventi**.
Nessun nuovo wrapper delle funzioni interne, malloc per evento, checkpoint
extra, profiler o tracemalloc. Cache/invarianti attivi; rimosso anche il GC
forzato finale del riferimento. I piccoli buffer Mach sono riutilizzati.
Guardie preliminari e contabilizzazione separata sono le altre differenze.

Le sonde checkpoint-after seguono anche scrittura e contabilizzazione
originali; la successiva undo-before copre la coda restante. Le letture
sequenziali delimitano intervalli, non allocazioni: fra due letture resta
anche lavoro della sonda stessa. Il vecchio intervallo fra letture 50 e 100
continua a includere l'osservazione 50; questa corsa non lo restringe
retroattivamente alle sole inversioni 51–100.

| Checkpoint50 replay | RSS corrente MiB | Massimo storico MiB |
| --- | ---: | ---: |
| Prima | 271.437500 | 298.125000 |
| Dopo osservazione e bookkeeping originali | 271.437500 | 298.125000 |
| Ingresso inversione 51 | 271.437500 | 298.125000 |

Variazione nell'osservazione 50: RSS **0 byte**,
picco **0 byte**; coda fino all'inversione 51:
picco **0 byte**. Massimo RSS campionato
nel replay **271.937500 MiB**, evento 120,
`undo:after`, inversione 51: **non è una misura del
massimo transitorio effettivo**. Assenza di incremento storico non esclude
transitori sotto il massimo già raggiunto. `vmmap` physical footprint,
heap allocato e RSS sono metriche diverse; non si sommano. Nessuna causa
del vecchio picco è dimostrata da questa singola ripetizione.

### Tempi ed esattezza

| Fase | Osservato s | Checkpoint s | Sonde s | Meno costi misurati s |
| --- | ---: | ---: | ---: | ---: |
| chain | 186.611180 | 1.321305 | 0.000369 | 185.289506 |
| replay | 80.797368 | 1.356739 | 0.009463 | 79.431166 |
| save | 0.466510 | 0.000000 | 0.000000 | 0.466510 |

CLI osservata **271.293584 s**; checkpoint completi
**5.746393 s**, nuove sonde **0.010404 s**,
totale diretto **5.756796 s (2.122%)**.
Timer disgiunti: le sonde sono fuori dal timer dei checkpoint originari.
La durata `checkpoint_seconds` del singolo sample resta il campo storico,
che esclude la coda di scrittura; i totali di fase/CLI includono quella coda.
`time -l` del processo: **271.91 s real** e
**298.125000 MiB**. Restano non quantificati contatori/weakref, code delle
sonde, storia dell'heap, GC naturale, scheduling e carico del Mac.
Sottrarre i costi diretti non ricostruisce un tempo senza strumentazione.

**100/100 certificati e terminale byte-identici** al riferimento;
configurazione, riga sorgente, risultato e hash del codice identici.
Replay interno esatto verificato dalla CLI. Solo caricamento e checker
completo `force=True` sul terminale salvato, fingerprint invariato: PASS;
nessun replay separato. Contatori delle chiamate uguali al riferimento.
Esito **`step_limit`**, F3=1/F4=51/F5=48; ordinario `not_run_nonterminal`.
Nessun errore software/strumentale o violazione degli invarianti osservato.
L'arresto è per budget, non per candidata né impossibilità matematica.

Solo piano e resoconto aggiornati; motore/test e file preesistenti fuori
scope invariati. Suite 356 PASS e smoke S1 sono risultati storici, non
rieseguiti. Nessun commit, reset, stash, pulizia, nuova checkout, altra
mappa, catena completa o validazione delle 151 mappe.
**Task 5 e catena completa aperte.** Prossimo passo proposto: definire un
protocollo di repliche limitate, con condizioni registrate, per misurare
quanto spesso ricompare il fenomeno; prima di qualsiasi esecuzione serve
nuova autorizzazione. Non implementare ottimizzazioni sulla base di questa
misura e non attribuire causalità all'osservatore o al motore.

## Aggiornamento: tre repliche con osservatore congelato

Serie avviata il 29 settembre e conclusa il 30 settembre 2026, protocollo
[predefinito](../superpowers/plans/2026-09-29-oracle-peak-replication-protocol.md),
Superpowers `executing-plans` inline. **Tre andate100, totale 300 riduzioni**,
sola riga 1 originale; ogni replay segue l'andata nello stesso processo.
Nessun quarto tentativo o replay separato. Articoli e web non necessari:
questa analisi usa soltanto i file salvati.

**Soglia 390,921875 MiB non raggiunta: N=3, R=3, K=0, K/R=0/3**;
nessun caso non discriminabile e nessun massimo complessivo sopra soglia.
La soglia non è stata abbassata dopo il risultato vicino della replica 1.
I precedenti esperimenti sono esclusi dal denominatore.

| Replica | Picco processo MiB | H0→H1 MiB | Incrementi replay | Esito soglia replay |
| --- | ---: | --- | ---: | --- |
| 1 | 386.406250 | 300.875000→386.406250 | 23 | not_observed |
| 2 | 308.125000 | 308.125000→308.125000 | 0 | not_observed |
| 3 | 313.062500 | 313.062500→313.062500 | 0 | not_observed |

H0/H1 sono le letture prima del checkpoint d'ingresso e dopo quello
all'uscita del replay, inclusa osservazione. Tre repliche sullo stesso Mac
non sono garantite indipendenti; il conteggio è descrittivo, non una stima
attendibile della probabilità e non esclude il fenomeno storico.

### Segmenti osservati e limiti

Replica 1:primo incremento300,875→303,906250 MiB tra le sonde prima/dopo
inversione62; ultimo384,515625→386,406250 MiB nella93;23 incrementi complessivi.
Incremento maggiore7,796875 MiB nella64 (308,265625→316,062500).
Tutti i 23 incrementi sono nella finestra50-before→100-before; sono intervalli
che comprendono anche il lavoro delle sonde, non prove su allocazioni specifiche.
Il checkpoint50 e la coda fino all'ingresso51 hanno delta RSS e picco zero
in tutte e tre le repliche. Non si attribuisce retroattivamente il vecchio
picco390,921875 a questi segmenti o a una funzione interna.

| Replica | RSS50 prima→dopo→ingresso51 MiB | Massimo RSS campionato replay MiB | Campione |
| --- | --- | ---: | --- |
| 1 | 273.593750→273.593750→273.593750 | 372.375000 | undo:after / 90 |
| 2 | 268.500000→268.500000→268.500000 | 269.015625 | undo:after / 85 |
| 3 | 263.359375→263.359375→263.359375 | 265.359375 | undo:after / 75 |

I massimi RSS campionati non sono i massimi transitori effettivi.
L'assenza di incrementi storici nelle repliche 2/3 non esclude transitori
sotto il massimo raggiunto nell'andata. La finestra storica fra letture50 e100
include sempre l'osservazione50. Dati completi in `details.json`,
`aggregate.json` e nei `replication-summary.json` delle singole repliche.

### Condizioni e discrepanza temporale

Osservatore/native/preflight/analyzer copiati identici dalla diagnosi leggera,
hash congelati prima della prima corsa; stessi hash del motore, versione
Python/NetworkX, input e configurazione. Time/ps/vmmap e RSS nativo verificati
prima di ogni replica. Invarianti/cache attivi, nessun GC forzato o profiling.
Nessun altro lavoro dell'agente durante le misure, salvo attesa e letture
compatte di progresso. Nuove cache uv separate, bytecode disabilitato.

La prima replica parte il 29/09 alle22:38:33+02:00 con batteria83%, su esplicita
autorizzazione; la seconda il 30/09 alle08:06:07+02:00 e la terza alle08:12:09+02:00,
AC collegata e batteria80%. Carico medio a1 minuto:2,257 /2,050 /4,400.
Versioni, variabili, memoria e alimentazione grezze sono in `conditions.json`
e `conditions/`; il sistema non è stato riconfigurato dall'agente.
Il divario notturno e l'alimentazione diversa sono conservati, non esclusi
a posteriori. **Non è una serie con tutte le condizioni ambientali uguali.**

Replica 1:time riporta1202,79s real,266,98 user e5,57 sys, mentre il timer CLI
riporta272.850051s e le fasi andata/replay circa189,151/79,715s.
Gli eventi non mostrano un corrispondente lungo intervallo interno al replay:
il maggiore intervallo fra sonde è94,837s nell'andata fra checkpoint50 e100.
Non si deduce una specifica sospensione, causa di scheduling o fase esterna:
le letture disponibili non localizzano lo scarto fra i timer. Non si usa
il tempo real1202,79 come costo CPU o regressione del motore. La sessione
PTY originale non era più recuperabile alla ripresa: il suo exit code non
è attestato; output CLI, measurement e time sono completi, e le verifiche
successive sono fresche. Repliche 2/3:exit0 direttamente osservato.
Nessun errore del motore, traceback o fallimento degli invarianti osservato;
la discrepanza dei tempi rimane un limite della misura, non un errore matematico.

| Replica | time real s | CLI interna s | Checkpoint s | Sonde s | Diretto/CLI |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 1202.79 | 272.850051 | 5.925072 | 0.014678 | 2.177% |
| 2 | 284.93 | 284.298538 | 5.790943 | 0.013100 | 2.042% |
| 3 | 279.97 | 279.357859 | 5.825177 | 0.011469 | 2.089% |

Timer checkpoint e sonde disgiunti; i totali includono la coda originale del
checkpoint. Tempi per fase nei measurement/details, senza duplicarli qui.
Overhead residuo non quantificato:contatori/weakref, code delle sonde, heap,
GC naturale, carico e scheduling. Nessuna sottrazione ricostruisce una corsa
senza strumentazione; nessun confronto causale AC/batteria è consentito dai dati.

### Esattezza, conservazione e conclusione

**300/300 certificati e 3/3 terminali byte-identici** al riferimento prefisso100;
replay interni esatti e checker completo forzato dei tre terminali PASS,
fingerprint invariato. Configurazione/riga/hash/call counters corrispondono;
228 eventi ordinati per replica. Ogni esito è `step_limit`,100 passi,
F3=1/F4=51/F5=48, ordinario `not_run_nonterminal`. Nessuna candidata esaurita,
violazione o impossibilità matematica dimostrata.

Baseline iniziale 5167 confronti riusciti; conservazione 5258 file, solo piano,
resoconto e annotazione d'esecuzione del protocollo autorizzati a cambiare.
Motore/test/dataset/cache/artefatti precedenti preservati. Suite 356 PASS e
smoke S1 restano storici, non rieseguiti. Nessun commit/reset/stash/pulizia,
nuova checkout, altra mappa o catena completa.

Radice canonica:`ct/debug/oracle-study/task5-replicates-x8rrh9HI/`: `commands.md`, `progress.md`, `series.json`,
`summary.md`, `aggregate.json`, `details.json`, `preservation.json`,
`artifact-provenance.json`, `review.txt`; tre directory sorelle elencate
in `series.json` conservano misure e verifiche integrali.
**Serie conclusa; Task 5 e catena completa aperte.** Il segnale utile è la
crescita osservata nelle inversioni62–93 della replica 1, pur sotto soglia.
Prossimo passo proposto: progettare una misura mirata dei temporanei in quel
segmento, tenendo separata la discrepanza temporale; nessuna nuova esecuzione
o ottimizzazione è implicita. Non reiterare automaticamente altre repliche.
