# Oracolo: protocollo di tre repliche del picco RSS

> Esecuzione futura: Superpowers `executing-plans`, inline. Questo documento
> conserva il disegno precedente all'esecuzione. **Serie autorizzata e conclusa**
> il 30 settembre 2026; si veda l'annotazione finale, senza altre corse implicite.

**Goal:** osservare quante volte ricompare la soglia storica di memoria in
tre repliche con la stessa strumentazione, senza attribuirne ancora la causa.
**Architecture:** tre processi sequenziali; ciascuno parte dall'input originale,
esegue al massimo 100 riduzioni e subito il replay interno nello stesso processo.
**Tech Stack:** Mac, Python della `.venv`, `uv`, osservatore con sonde leggere,
`ru_maxrss`, RSS Mach, `time`, `ps`, `vmmap`; nessuna dipendenza nuova.
**Spec:** [studio dell'oracolo](../specs/2026-09-28-oracle-reduction-study-design.md).

## Domanda e scelta del campione

Con il medesimo osservatore leggero, il massimo storico raggiunge nuovamente
**T = 390,921875 MiB**, e il primo superamento è osservabile nel replay?
La soglia è fissata prima delle repliche, dal valore originale; non verrà
abbassata dopo aver visto i risultati. Non richiedere uguaglianza esatta del picco.

Si scelgono **3 nuove repliche**, massimo **300 riduzioni TOTALI**, tutte sulla
riga 1 di `ct/maps_3000_maps_of_8000_faces.colored.planar`. Tre processi nuovi,
ciascuno con andata e replay interni; mai un replay isolato del prefisso caricato.
Due repliche offrirebbero meno possibilità di osservare variabilità; cinque
aumenterebbero il costo senza rendere questa prova una stima statistica robusta.
Tre è una scelta di budget esplorativa, non un campione statisticamente adeguato.
Le tre corse precedenti sono riferimenti storici, esclusi dal denominatore:
la loro strumentazione differisce. Anche l'ultima, simile, resta fuori dalla serie.

La singola misura più recente dura 271,91 s: tre corse richiederebbero circa
14 minuti di sola esecuzione se i tempi restassero simili, oltre a preparazione,
verifiche e analisi. È un ordine di grandezza, non un tempo garantito.

## Condizioni da congelare

- Checkout esistente; nessun commit, reset, stash, pulizia o altra checkout.
  Preservare modifiche locali, file non tracciati, cache e debug ignorati.
- Codice identico alle impronte dell'ultimo manifest; stessa riga sorgente,
  Python, NetworkX e configurazione. Non modificare motore, test o dataset.
- Usare **byte per byte** `observe.py` e `native.py` di
  `ct/debug/oracle-study/task5-minimal-peak-s6LAt3x4/` in tutte e tre le repliche.
  Congelarne gli hash prima della prima corsa. Nessuna strumentazione adattiva.
- Conservare checkpoint 20/50/100, contatori originali e sonde ai confini;
  invarianti e cache del motore attivi, GC naturale. Nessun GC forzato,
  wrapper interno dettagliato, malloc per evento, profiler o tracemalloc.
- Una nuova directory per replica, direttamente sotto `ct/debug/oracle-study/`:
  la profondità è necessaria al calcolo di `CT` nell'osservatore. Non annidare
  le repliche nella directory di coordinamento. Output esclusivi, mai riutilizzati.
- Da `ct/`, Python con `uv run --python ../.venv/bin/python`, bytecode disabilitato;
  nuova cache uv dedicata a ciascuna replica. Non cancellare o riscaldare cache,
  non riavviare il Mac, non cambiare allocatore, seed, GC o impostazioni energetiche.
- Esecuzioni sequenziali, senza altro lavoro dell'agente durante la misura.
  Registrare prima di ciascuna data/ora, versione OS/architettura, alimentazione,
  carico e memoria disponibili, variabili `PYTHONMALLOC`/`PYTHONHASHSEED` e versioni.
  Mantenere il Mac alimentato e le medesime condizioni pratiche; non terminare
  processi dell'utente. Una variazione osservata si annota, non si elimina il risultato.
  Caches del sistema, seed non fissato, heap, GC e carico restano fonti di variabilità.

## Sequenza futura, soltanto dopo autorizzazione

- [ ] Creare una directory di coordinamento sotto debug, con inventario iniziale,
  hash congelati, comandi, condizioni e registro dei tentativi. Nessun motore avviato.
- [ ] Prima di ogni replica creare la sua directory, copiare i due script congelati
  e `preflight.py` dalla stessa diagnosi leggera (eseguire la copia nuova),
  predisporre `baseline-check.json` verificando davvero codice/input/strumentazione
  e `preflight/result.json` mediante il preflight esistente su processo piccolo.
  Verificare time/ps/vmmap/RSS nativo con lo stesso accesso host della futura corsa.
  Non copiare come se fossero attuali gli esiti positivi dei preflight precedenti.
- [ ] Avviare una sola volta la replica; registrare il tentativo prima del lancio.
  Dopo la conclusione analizzare i file salvati e verificare esattezza/conservazione
  prima di procedere alla successiva. Nessun rilancio automatico.
- [ ] Completare esattamente le tre repliche valide previste, salvo i criteri di
  arresto sotto. Non fermarsi al primo picco favorevole e non aggiungere repliche
  perché il picco manca. Non sostituire un tentativo fallito con uno nuovo.
- [ ] Produrre una tabella aggregata e aggiornare il punto di ripresa dello studio,
  lasciando Task 5 e catena completa aperte. Fermarsi, senza ottimizzazioni.

Comando tipo, **da non eseguire durante la progettazione**. `RUN_DIR` deve
indicare una directory nuova già preparata nella posizione prescritta:

```bash
cd /Users/mario.stefanutti/mario/programming/github-stefanutti/maps-coloring-python/ct
: "${RUN_DIR:?directory della replica preparata e verificata}"
/usr/bin/time -l env PYTHONDONTWRITEBYTECODE=1 UV_CACHE_DIR="$RUN_DIR/uv-cache" \
  uv run --python ../.venv/bin/python python "$RUN_DIR/observe.py" \
  > "$RUN_DIR/observed.stdout.log" 2> "$RUN_DIR/observed.stderr-time.log"
```

L'argv interno congelato seleziona riga 1, max_steps 100 e budget Kempe 10000;
quest'ultimo riguarda solo l'ordinario, che resta `not_run_nonterminal` su step_limit.
Nessun ciclo shell che avvii automaticamente tutte le corse o ripeta un errore.

## Misure e classificazione fissate in anticipo

Per ogni replica conservare tutti gli eventi, campioni e output nativi su disco.
In chat mostrare una riga per replica e le sole discrepanze. Misurare separatamente
checkpoint e sonde come nell'osservatore congelato; dichiarare residuo non quantificato.

Definire H0 come `ru_maxrss` a `checkpoint:replay-before:before`, H1 come
`ru_maxrss` a `checkpoint:replay-after:after`. La finestra comprende anche
l'osservazione ai confini; non è attribuita esclusivamente al motore.

| Esito della soglia nel replay | Criterio |
| --- | --- |
| Superamento osservato | H0 < T e almeno un evento della finestra raggiunge T |
| Superamento non osservato | H0 < T e H1 < T |
| Non discriminabile dal massimo storico | H0 >= T, anche se H1 = H0 |

Riportare anche: massimo dell'intero processo da time, massimo storico del
processo Python, H0/H1, ogni incremento nel replay, massimo RSS **campionato**,
prima coppia di eventi che attraversa T, e fase dell'eventuale superamento iniziale.
Un picco complessivo >= T già nell'andata non è una riproduzione localizzata nel replay.
Picchi solo nell'avvio/coda finale sono registrati separatamente. Differenze fra
time e letture Python non vengono automaticamente attribuite a una fase non osservata.

Per checkpoint 50 riportare prima/dopo e ingresso inversione 51, per coprire la coda.
Riportare inoltre il primo incremento fra checkpoint 50-before e 100-before,
finestra comparabile a quella storica ma con letture leggermente anticipate
dalle nuove sonde. Essa include l'osservazione 50. Ogni segmento comprende anche
il lavoro della strumentazione fra letture; non identifica una specifica allocazione.
Nessun aumento di ru_maxrss esclude transitori sotto il massimo precedente.

Contare separatamente: repliche valide N; repliche con massimo complessivo >= T;
repliche valutabili nel replay R (H0 < T); attraversamenti osservati K; repliche
non discriminabili N-R. Presentare **K/R**, oppure «non valutabile» se R=0,
insieme a tutti i conteggi. Non chiamarlo probabilità generale del fenomeno.
Le repliche sequenziali sullo stesso Mac non sono garantite indipendenti.

## Verifiche e arresti

Ogni corsa valida deve produrre step_limit a 100 passi e 100 inversioni interne;
confrontare **tutti i certificati e terminale byte per byte** col riferimento
`task5-prefix100-izztpr64`, oltre a source/config/result/hash e replay esatto.
Caricare il nuovo terminale, forzare gli invarianti e verificare fingerprint
invariato, senza replay separato. Verificare contatori, 228 eventi ordinati,
copertura dei confini, vmmap e misure temporali. Nessuna suite/smoke se il codice
resta identico; 356 PASS/S1 sono soltanto risultati storici.

Fermare la serie in caso di baseline diversa, errore strumentale/software,
violazione degli invarianti, confronto esatto fallito o andamento diverso dal
prefisso100 atteso. Distinguere `no_certified_candidate`, eventuale terminale
anticipato e interruzione esterna; non rinominarli errore matematico. Salvare anche
gli artefatti incompleti. Un tentativo avviato conta nel limite di tre, anche se
fallisce; nessuna sostituzione o ripetizione automatica. Preflight fallito: stop
prima del motore. Massimo budget autorizzabile di questa proposta: 300 riduzioni.

Se K=0, registrare mancata riproduzione nelle repliche valutabili, senza escludere
il fenomeno. Se K>0, registrare segmenti e frequenza osservata; la causa resta
aperta e un esperimento mirato successivo richiede un nuovo progetto/autorizzazione.
Con qualunque esito: nessun A/B causale, nessuna impossibilità matematica dimostrata,
nessuna estensione a catena completa, altre mappe o ottimizzazioni.

## Verifica della sola progettazione

Protocollo confrontato con i vincoli e l'osservatore già letti: soglia e denominatori
predefiniti, budget chiuso, finestra50 inclusiva della coda, errori distinti,
profondità directory corretta e nessuna nuova esecuzione implicita.
Non viene implementato in questa fase un nuovo riepilogatore o launcher.
Conservazione e comandi della progettazione:
`ct/debug/oracle-study/task5-replication-protocol-KhSZYcmp/`.

## Esecuzione conclusa — 30 settembre 2026

Autorizzazione esplicita «vai», poi «procedi anche senza alimentazione collegata».
Tre repliche eseguite,300 riduzioni totali, nessun tentativo sostitutivo.
Soglia congelata:K/R=0/3; picchi386,406250 /308,125000 /313,062500 MiB.
Prima replica a batteria, successive su AC con intervallo notturno:condizioni
registrate e risultati conservati. Prima replica con discrepanza time/CLI
non localizzata; non inferire cause o tempi non strumentati.
Tutti i certificati/terminali identici, replay interni esatti e invarianti PASS.
[Resoconto e limiti](../../llm-vs-4ct/4ct-oracle-study-step-3.md#aggiornamento-tre-repliche-con-osservatore-congelato).
Artefatti: `ct/debug/oracle-study/task5-replicates-x8rrh9HI/`.
Task5/catena completa aperte; nessuna ulteriore esecuzione autorizzata.
