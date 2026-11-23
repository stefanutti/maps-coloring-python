# Oracle Reduction Study Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ottenere su una mappa già colorata una catena F2/F3/F4/F5 fino a theta con ritorno esatto certificato, oppure isolare e spiegare il primo ostacolo riproducibile.

**Architecture:** Prototipo sperimentale separato dalla pipeline normale, con stato strutturale e oracolo cromatico sincronizzati e certificati reversibili. Prima si studiano i casi locali; poi si concatenano i passi e si confronta il ritorno esatto con la ricostruzione ordinaria. Le fasi successive sono una roadmap condizionata ai risultati, non funzionalità già approvate o implementate.

**Tech Stack:** Python 3.9, NetworkX MultiGraph, pytest, JSON/JSONL, `uv`; dipendenze già presenti.

**Spec:** [2026-09-28-oracle-reduction-study-design.md](../specs/2026-09-28-oracle-reduction-study-design.md).

## Global Constraints

- Compatibilità con Python 3.9; nessuna nuova dipendenza nel primo traguardo.
- Eseguire programma e test con `ct/` come working directory.
- Non modificare il dataset; assumere valide le 151 colorazioni originali.
- Verificare le trasformazioni nuove, senza ripetere una validazione massiva degli input.
- Conservare nomi, ruoli e contratti di `ct/4ct.py` e `ct/ct_graph_utils.py`.
- Conservare i formati Arianna e le firme delle strategie esistenti.
- Separare i dati `structure` dai dati `oracle`; non usare colori nelle feature strutturali.
- Conservare le modifiche locali dell'autore; non eseguire reset, stash o commit cumulativi.
- Tenere i risultati voluminosi sotto `ct/debug/`, fuori da Git; versionare solo piccoli casi e resoconti.
- Qualunque futura separazione train/test deve avvenire per mappa intera.

## Review Focus

1. Archi paralleli, theta e facce uguali per valore: identità e occorrenze non devono collassare — Task 2 e 3.
2. F2 non generica, F4 a due colori e vicini coincidenti: nessuna formula applicata senza verificarne le ipotesi — Task 1 e 3.
3. Tentativo rifiutato o certificato obsoleto: nessuna mutazione parziale e nessun `FaceIndex` desincronizzato — Task 2 e 3.
4. Colori di theta, ordine degli scambi e JSON: ritorno esatto dopo salvataggio/lettura, non soltanto una nuova colorazione valida — Task 4.
5. Budget esaurito o caso non implementato: risultato non conclusivo, distinto da errore software e da impossibilità matematica — Task 3, 4 e 5.

---

## Punto di ripresa

### R1 parte27 — seguito complementare row2 preparato staticamente, lanci NOT_RUN (2 ottobre2026)

Autorizzata solo preparazione statica, cap1800s inclusivo delle letture; nuova arena `ct/debug/oracle-study/r1-followup-part27-20261002-20261002-25658-v7xxky/`. Due ingressi manuali distinti: replay persistito, poi ordinario soltanto dopo PASS completo e nuova autorizzazione. Nessun main, retry, riga3/4 o151. Fonte parte25 congelata in loco: riga fisica2,8048 passi; main originale rimane STOP/exit1, con sentinel e lock conservati. Il seguito non riapre né produce PASS della serie R1 originale.

Proposta esplicita di contabilità/budget complementari in `accounting-policy.md` e `budgets-proposed.json`: diagnosi misurata≤1s/child e riserva2s sui due consumer; finestra conservativa di chiusura osservata≤15s/child/30s seguito, già dentro wall; cap motore replay10800s/ordinario14400s invariati. Costi storici incompleti riportati senza riclassificarli; nuovi cumulativi da approvare prima del lancio. [Comandi manuali](../../../ct/debug/oracle-study/r1-followup-part27-20261002-20261002-25658-v7xxky/manual-commands.md), [report](../../../ct/debug/oracle-study/r1-followup-part27-20261002-20261002-25658-v7xxky/report.md), [revisione inline distinta](../../../ct/debug/oracle-study/r1-followup-part27-20261002-20261002-25658-v7xxky/final-review.txt). Verifica esclusivamente statica AST3/82 controlli e sintassi; freeze, conservazione e tempo finale nell'arena. Superpowers inline, stesso autore, nessun subagent. Cap4GiB e recuperabilità non presunti. Tutti i lanci NOT_RUN/non autorizzati; prossimo possibile passo: approvazione del pacchetto e della proposta, poi consenso al solo replay persistito row2. Fermarsi qui.

### R1 parte23 — P1 statica consegnata, lanci NOT_RUN (1 ottobre2026)

Nuova preparazione autorizzata con cap60min dopo STOP parte22, senza aumenti retroattivi. Arena: `ct/debug/oracle-study/r1-launchers-part23-20261001-2078-19863la/`; base parte22 copiata selettivamente sul freeze, STOP1800s e artefatti precedenti preservati. Budget runtime parte21 invariati; unica variazione nuova P1 3600s, nominale203490s.

Pacchetto P1: righe fisiche2→3→4, nove ingressi manuali main/replay persistito/ordinario, timer e contatori scalari per fase, cap cumulativi, gate identità/save/esiti/conservazione e sentinel monouso. Autonomo dal Terminale e dalla sessione LLM; niente retry, prosecuzione automatica o151. Comandi in `manual-commands.md`, esito statico in `report.md`, freeze/baseline e inventari nell'arena. Nessun launcher Task5 modificato o adattato.

AST3/bash-n9/Ruby-c1 e audit43 controlli statici conformi; revisione finale inline separata dello stesso autore, senza subagent, Critical0/Important0/Minor0 residui nell'ambito P1. Corretto stato ausiliari irrisolti e ciclo TERM/KILL child unico; nessun helper motore o loader importato/eseguito. Limiti monitorati, query wake non preflightata, sufficienza4GiB e recuperabilità non presunte. Conservazione e tempo finale documentati in `preservation.json`, `preparation-timing.json` e `completion.json`.

**Tutti i nove lanci NOT_RUN. P2 non autorizzata: serve successiva autorizzazione esplicita dopo consegna/revisione dei comandi. Nessun motore, benchmark, prefisso, preflight, replay, loader terminali, suite/focused/smoke avviato.** Unico inserimento nel punto di ripresa; modifiche locali e arene precedenti conservate. Fermarsi qui.

**Ultima sessione: R1 parte22,1 ottobre2026: pacchetto candidato P1 congelato; STOP per superamento del budget di preparazione.**
Piano parte21 e budget approvati dall'utente; autorizzata SOLO preparazione
statica, nessun lancio. Superpowers executing-plans/verifica inline, review
finale inline separata stesso autore, nessun subagent. Nuova arena diretta
`ct/debug/oracle-study/r1-launchers-part22-20261001-24737-1mtqmv0/`:
[comandi e istruzioni](../../../ct/debug/oracle-study/r1-launchers-part22-20261001-24737-1mtqmv0/manual-commands.md),
[report](../../../ct/debug/oracle-study/r1-launchers-part22-20261001-24737-1mtqmv0/report.md),
[review](../../../ct/debug/oracle-study/r1-launchers-part22-20261001-24737-1mtqmv0/final-review.txt),
[freeze](../../../ct/debug/oracle-study/r1-launchers-part22-20261001-24737-1mtqmv0/freeze.json),
[audit statico](../../../ct/debug/oracle-study/r1-launchers-part22-20261001-24737-1mtqmv0/static-audit.json),
[conservazione](../../../ct/debug/oracle-study/r1-launchers-part22-20261001-24737-1mtqmv0/preservation.json).
Righe fisiche2→3→4, metadati/SHA confermati; nove ingressi manuali distinti
main/replay persistito/ordinario; helper nuovi con contatori di completamento,
timer e cumulativi/gate/sentinel. Launcher Task5 congelati non adattati.
Sintassi finale AST3/3/bash9/9/Ruby1/1, solo file/JSON/SHA; nessun helper o
motore importato/eseguito, nessun benchmark/prefisso/preflight/replay/loader
terminali/suite/focused/smoke. Python solo ct/uv offline/bytecode off/cache/tmp
nuovi nell'arena. Runtime non verificato; cap4GiB non garantisce sufficienza
né salvataggio recuperabile, main salva soltanto dopo replay interno.
**P1 NON CONFORME:** cap statico1800s superato; almeno
2076.389s dall'inventario, letture iniziali escluse; nessun aumento retroattivo.
SERIES_BLOCKED.json conserva STOP e impedisce tutti i9 child futuri. Dopo
rilevamento solo chiusura documentale/review/freeze/conservazione/resume.
Nuovo accordo necessario sullo STOP P1; P2 richiede successiva autorizzazione,
nessun reset sentinel/retry/prosecuzione automatica/151. R1 NOT_RUN.
Inventario iniziale7626; conservazione finale fuori arena ammette soltanto
questo singolo inserimento. Corretto un mkdir di7 directory nuove vuote
sotto ct/ct, senza file/preesistenti toccati; riscontro in path-correction.json.
Locali, produzione/test/FaceIndex/cache/snapshot/certificati/dataset/architecture
e arene precedenti preservati; Task5/T/N/R/K e receipt storici invariati.
**STOP dopo consegna del candidato statico bloccato, nessun lancio.**

**Ultima sessione: R1 parte21,1 ottobre2026: primo campione aggiuntivo progettato; STOP dopo sola analisi statica/evidenze/piano.**
Superpowers inline (brainstorming/writing-plans/verifica), review finale inline
separata stesso autore,nessun subagent. Nessun motore/Python/replay/loader di
terminali/preflight/benchmark/prefisso/suite/focused/smoke;nessun launcher R1.
Nuova arena diretta `ct/debug/oracle-study/r1-plan-part21-9afKX7PR/`:
[piano](../../../ct/debug/oracle-study/r1-plan-part21-9afKX7PR/r1-plan.md),
[budget proposti](../../../ct/debug/oracle-study/r1-plan-part21-9afKX7PR/budgets-proposed.json),
[report](../../../ct/debug/oracle-study/r1-plan-part21-9afKX7PR/report.md),
[evidenze](../../../ct/debug/oracle-study/r1-plan-part21-9afKX7PR/static-evidence.txt),
[audit](../../../ct/debug/oracle-study/r1-plan-part21-9afKX7PR/plan-audit.json),
[review](../../../ct/debug/oracle-study/r1-plan-part21-9afKX7PR/final-review.txt),
[conservazione](../../../ct/debug/oracle-study/r1-plan-part21-9afKX7PR/preservation.json).
Selezione proposta:righe fisiche2→3→4 del medesimo dataset,criterio posizionale
dichiarato prima degli esiti;solo metadati di quelle righe,nessuna validazione
massiva. V/E/F16098/24147/8051,16058/24087/8031,16072/24108/8038;
passi attesi condizionali8048/8028/8035 da −2/−3/−1,non codificati nel motore.
Budget proposti per mappa:max_steps10000,RSS/HWM4GiB child/controller128MiB,
storage2GiB,main11h15min (chain8h/internal replay3h/save10min/other5min),
persisted replay3h,ordinary4h/Kempe10000 per ricerca. Totale child54h45min;
envelope nominale con supervisione/terminazione/preparazione56h01min30s;
storage complessivo6GiB+64MiB. Nessuna garanzia di sufficienza o quota hard.
Quattro esiti distinti;gate budget/conservazione/status/exactness e contatori
per fase;futuri lanci manuali Terminale,una modalità/mappa per comando,
indipendenti dalla sessione LLM. Primo STOP/errore/non conclusivo blocca
restanti comandi/mappe,nessun retry/sostituzione/estensione automatica alle151.
CLI salva dopo replay interno;timeout/errori non garantiscono recuperabilità.
Launcher Task5 congelati su riga1/prefix100/candidato/fingerprint e gate
specifici,non riutilizzabili né adattati qui. Preparazione distinta richiesta.
Inventario iniziale7605;conservazione finale fuori arena ammette soltanto
questo inserimento. Locali/produzione/test/FaceIndex/cache/snapshot/certificati/
dataset/architecture/checker/invarianti/GC naturale e arene precedenti preservati.
Task5 resta conclusa sulla riga1;main parte17 STOP cap1GiB immutato;
T390,921875MiB,N3/R3/K0 invariati. Nessuna prova4CT o copertura generale.
**R1 NOT_RUN. Piano e budget NON APPROVATI: preparazione dei launcher ed
esecuzioni richiedono approvazione esplicita. Fermata dopo progettazione.**

**Ultima sessione: Task5 parte20,1 ottobre2026: prima catena completa sulla riga1 con replay persistito esatto e ordinario riuscito confermati.**
L'utente ha lanciato manualmente i due comandi parte19; consumer separato
`ct/debug/oracle-study/task5-followup-part19-kXpS8bAe/`,input readonly
`ct/debug/oracle-study/task5-long-run-part17-ui6vuER3/run`.
Catena persistita theta8031,max_steps10000,V/E/F16064/24096/8034→2/3/3;
F2/F3/F4/F5=1/22/3919/4089,path8030/cycle298. Main parte17 conserva
STOP/HWMcap1GiB/exit-15;nessun aumento retroattivo o riscrittura del receipt.
**PERSISTED_REPLAY_EXACTexit0:**8031 inversioni,source/fingerprint e archi
con ID/colori esatti. Child2471,145168s,replay2467,605063s,load2,970697s;
RSS campionato1378,71875MiB,HWM1410,625MiB. **ORDINARY_SUCCESSexit0:**
topologia originale,V/E16064/24096,well_colored e stack_consumed true;
child115,091632s,rebuild111,619264s,load2,995696s,RSS1627,015625MiB,
HWM1627,1875MiB. Kempe10000 per F5,replay_calls0;esito ordinario esterno,
manifest originale ordinary=not_requested immutato. Colorazione ordinaria
non richiede gli stessi ID/colori del replay. Entrambi sotto4GiB/3h/4h,
budget e conservazione runtime7543/7543 PASS;nessun retry/fase automatica.
Superpowers inline,review separata stesso autore,nessun subagent.
Audit evidenze/hash37/37 Rubyexit0;freeze14,source/codice/input/receipt,
fasi/progressi/esiti e budget verificati. Nessun nuovo engine/loader/replay/
test/preflight/benchmark da agent,nessuna suite fresca dichiarata PASS.
Nuova arena diretta `ct/debug/oracle-study/task5-results-part20-7pc7ahTq/`:
[report](../../../ct/debug/oracle-study/task5-results-part20-7pc7ahTq/report.md),
[audit](../../../ct/debug/oracle-study/task5-results-part20-7pc7ahTq/result-audit.json),
[review](../../../ct/debug/oracle-study/task5-results-part20-7pc7ahTq/final-review.txt),
[conservazione](../../../ct/debug/oracle-study/task5-results-part20-7pc7ahTq/preservation.json).
Inventario7580;unico inserimento resume fuori arena,conservazione finale
nel receipt. Produzione/checker/invarianti/FaceIndex/cache/GC naturale,
certificati/dataset/locali e arene precedenti preservati.
T390,921875MiB,N3/R3/K0 invariati. **Task5,prima catena sulla riga1 e
confronto ordinario conclusi:**evidenza su mappa colorata/ramo osservato,
non prova del4CT o garanzia su altre mappe. **STOP dopo verifica/report.**
Prossima fase applicabile R1:solo su richiesta,progettare piano dedicato
per3 mappe ulteriori con selezione/budget/arresti da approvare;nessun lancio.

### Sessione precedente: parte19, preparazione dei comandi sul salvataggio

**Ultima sessione: Task5 parte19, 1 ottobre 2026: nuovi comandi per il salvataggio parte17 preparati, nessun motore lanciato.**
Design parte18 approvato dalla richiesta «Modifica se necessario i file e dimmi
che comandi lanciare». Superpowers executing-plans inline, review finale
separata dello stesso autore, nessun subagent. Il candidato theta salvato
`task5-long-run-part17-ui6vuER3/run` viene riusato readonly; main parte17 e
vecchio receipt STOP/HWMcap1GiB immutati. Nuovo replay manuale3h/4GiB,
ordinario manuale4h/4GiB soltanto dopo nuovo replay esatto PASS. Main0,
tentativi nuovi replay1/ordinario1/retry0; nessuna fase successiva automatica.
Contatori caricamento/replay dopo completamento; ordinario log pre-passo
esplicitamente «in corso». Totale dal manifest/lista8031,non cap del motore
né percentuale del tempo.100% non è esito: PERSISTED_REPLAY_EXACT verifica
sorgente/ID/colori; ORDINARY_SUCCESS verifica topologia/conteggi/colori/stack.
Checker,invarianti,FaceIndex,cache,GC naturale,loader/save e certificati invariati.
Freeze14, audit statico Python3.9 AST/compile/hash33/33 uvexit0; zsh4/4exit0,
Ruby3/3SyntaxOK. Nessun engine,loader,replay,test,preflight o dummy-child;
runtime/overhead/risorse/segnali non collaudati.4GiB non garantisce completamento.
Nuova arena diretta `ct/debug/oracle-study/task5-resume-part19-8jGY8cZU/`:
[comandi da lanciare](../../../ct/debug/oracle-study/task5-resume-part19-8jGY8cZU/README.md),
[report](../../../ct/debug/oracle-study/task5-resume-part19-8jGY8cZU/report.md),
[budget](../../../ct/debug/oracle-study/task5-resume-part19-8jGY8cZU/budgets.json),
[freeze](../../../ct/debug/oracle-study/task5-resume-part19-8jGY8cZU/frozen.json),
[audit statico](../../../ct/debug/oracle-study/task5-resume-part19-8jGY8cZU/static-verification.json),
[review](../../../ct/debug/oracle-study/task5-resume-part19-8jGY8cZU/final-review.txt),
[conservazione](../../../ct/debug/oracle-study/task5-resume-part19-8jGY8cZU/preservation.json).
Inventario7479; conservazione finale registrata nel receipt. Unico inserimento
resume fuori arena. T390,921875MiB,N3/R3/K0 invariati. **STOP preparazione:
replay persistito/ordinario NOT_RUN,Task5 aperta; utente lancia ora solo replay.**

### Sessione precedente: parte18, diagnosi e progetto del seguito

**Ultima sessione: Task5 parte18, 1 ottobre 2026: diagnosi del run parte17 lanciato manualmente;salvataggio candidato integro a theta.**
Arena del run `task5-long-run-part17-ui6vuER3`:catena8031,V/E/F2/3/3,
F2/F3/F4/F5=1/22/3919/4089;replay interno e save exitdi faseok.
Child11440,855s;chain8154,227s,replay interno3274,927s,save11,179s.
STOP originale child_HWM_cap,exit-15,controllerexit1:HWM1329,828125MiB
>cap1024MiB,controRSScampionato963,359375MiB. Picco in save,+385,109375MiB.
Finished/child-summary assenti;vecchio budget/receipt/riserve non modificati.
Manifest scritto ultimo e presente;JSONL193288972B,8031righe,riga max1221502B.
Audit statico27/27exit0:SHAterminale/certificati,identità riga1/codice/freeze13,
conteggi/famiglie/scambi/continuità fingerprint e prefix100byte-identico.
**Salvataggio utilizzabile come input di futuro replay separato;nessuna nuova
catena necessaria per ottenere l'input. Replay persistito e ordinario NOT_RUN.**
Superpowers systematic-debugging/brainstorming inline,review finale separata
stesso autore,nessun subagent. Nessun engine/loader/replay/test/preflight nuovo.
Utente autorizza range3/4/5GB;proposto cap4GiB per nuovi child,senza applicarlo
retroattivamente. Progetto bounded in chat:nuovi script manuali sul run salvato,
replay3h/ordinario4h separati e contatori1234/8031 per fase,non percentualetempo.
**Approvazione del design pendente;nessun nuovo adattatore prodotto/lancio.**
Streaming JSONL/hash nel save/load è possibilità distinta,non implementata
né misurata;nessuna modifica a produzione/checker/cache/GC/FaceIndex/certificati.
Nuova arena diretta `ct/debug/oracle-study/task5-diagnosis-part18-WGPi5I7z/`:
[report](../../../ct/debug/oracle-study/task5-diagnosis-part18-WGPi5I7z/report.md),
[audit file salvati](../../../ct/debug/oracle-study/task5-diagnosis-part18-WGPi5I7z/saved-artifact-audit.json),
[budget proposti](../../../ct/debug/oracle-study/task5-diagnosis-part18-WGPi5I7z/budgets-proposed.json),
[review separata](../../../ct/debug/oracle-study/task5-diagnosis-part18-WGPi5I7z/final-review.txt),
[conservazione](../../../ct/debug/oracle-study/task5-diagnosis-part18-WGPi5I7z/preservation.json).
Inventario7457;conservazione nel receipt finale;solo questo inserimento
fuori arena. Checkout/locali/index/arene precedenti preservati.
T390,921875MiB,N3/R3/K0 invariati. **STOP:diagnosi conclusa;Task5 resta aperta
per replay persistito e ordinario. Nessun rilancio del main parte17.**

### Sessione precedente: parte17, preparazione del lancio autonomo

**Ultima sessione: Task5 parte17, 1 ottobre 2026: pacchetto per lancio autonomo dal Terminale preparato; motore0.**
Su richiesta successiva al piano parte16, preparati controller/adattatori,
launcher main/replay/ordinario distinti e comando stato di sola lettura.
Superpowers inline, review finale separata dello stesso autore, senza subagent.
Nessun motore/prefisso/benchmark/preflight/replay/load terminale/test/smoke.
Main manuale sulla riga1: max_steps10000,wall10h,catena6h,replay interno3h,
save30min,altro600s; childRSS1024MiB/controller128MiB campionati,
arena2GiB/diagnostica128MiB. Replay persistito3h e ordinario4h richiedono
comandi umani e receipt/hash/conservazione validi del predecessore.
Riserve1/1 permanenti per fase,0 retry,nessuna fase automatica.
Freeze13 file; SHA riga1 e4 sorgenti approvati parte15 coincidono.
Audit finale sintassi Python3.9/AST/hash27/27 uvexit0; zsh5/5exit0,
Ruby inventory/status SyntaxOK. Solo letture/compile,nessun import engine.
Review statica Critical0/Important0; runtime/segnali/overhead non collaudati.
Il Terminale indipendente dall'LLM prosegue senza crediti del turno; Mac
e Terminale devono restare attivi. Caffeinate solo sleep per inattività.
Save originale dopo replay interno: terminal/steps/manifest, nessun checkpoint,
nessuna promessa di recuperabilità in timeout/kill; stop non conclusivi.
8031 resta conteggio condizionale osservato,non guardia del motore.
Nuova arena diretta `ct/debug/oracle-study/task5-launch-part17-epqnaLt0/`:
[istruzioni e comando unico](../../../ct/debug/oracle-study/task5-launch-part17-epqnaLt0/README.md),
[report](../../../ct/debug/oracle-study/task5-launch-part17-epqnaLt0/report.md),
[decisioni/riuso/arresti](../../../ct/debug/oracle-study/task5-launch-part17-epqnaLt0/design-decisions.md),
[budget](../../../ct/debug/oracle-study/task5-launch-part17-epqnaLt0/budgets.json),
[freeze](../../../ct/debug/oracle-study/task5-launch-part17-epqnaLt0/frozen.json),
[audit statico](../../../ct/debug/oracle-study/task5-launch-part17-epqnaLt0/static-verification.json),
[review separata](../../../ct/debug/oracle-study/task5-launch-part17-epqnaLt0/final-review.txt),
[conservazione finale](../../../ct/debug/oracle-study/task5-launch-part17-epqnaLt0/preservation.json).
Inventario iniziale7360;conservazione nel receipt finale;solo questo inserimento
fuori arena. Produzione/test/FaceIndex/cache/GC/snapshot/certificati/dataset/
architettura e vecchie arene preservati; checkout/index/branch/locali invariati.
T390,921875MiB,N3/R3/K0 invariati. **STOP: preparazione conclusa; nessun
lancio automatico. Il lancio lungo resta azione esplicita dell'utente con
piano e budget documentati; Task5/catena completa/ordinario ancora aperti.**

### Sessione precedente: parte16, progettazione del tentativo lungo

**Ultima sessione: Task5 parte16, 1 ottobre 2026: sola analisi statica/evidenze salvate e progetto del tentativo lungo; STOP dopo progettazione.**
Superpowers inline con review finale separata dello stesso autore, non
indipendente; senza subagent, checkout esistente. Nessun Python/import motore,
benchmark/prefisso/preflight/replay/caricamento terminali/test/smoke.
Inventario iniziale7321 file/symlink; hash4 sorgenti e26 file freeze parte15,
SHA della sola riga1 riconfermati. Task2 parte15 resta completata e il suo
budget consumato; nessun rilancio. T390,921875MiB e N3/R3/K0 invariati.

Piano principale **max-steps10000 sulla riga1 originale**;8031 deriva da
V/E/F16064/24096/8034 e non garantisce completamento né va codificato.
Estrapolazioni illustrative soltanto:chain/replay interno4,025/1,797h a
costo costante oppure2,025/0,904h per dimensione grafo; RSS lungo ignoto,
certificati asimmetrici e serializzazioni complete in RAM.
Audit statico:save dopo chain/replay interno e,con ordinary flag,dopo
ordinario;manifest ultimo senza fsync/rename. Timeout/errori possono non
lasciare una catena recuperabile. Nessun checkpoint/resume presunto.

Proposta:main senza ordinario,poi replay persistito e ordinario separati,
condizionati a theta salvato/replay esatto e budget validi. Cap proposti:
main10h(chain6h,replay interno3h,save30min,altri10min),replay nuovo3h,
ordinario4h/Kempe10000 perF5;RSS campionato1024MiB perchild da approvare
specificamente,distinto daT. Totalechild massimo17h,non durata prevista;
diagnostica minima/cap propri/storage/grazia espliciti nel piano.
Helper100 non riutilizzabili invariati:cap/101−inverse/window60–95/buffer/
gate specifici;nessun adattamento automatico. Checker/invarianti/cache/GC
naturale/snapshot/certificati/FaceIndex/produzione/test/dataset/architettura,
modifiche locali e arene precedenti preservati;un solo inserimento qui.

Nuova arena diretta `ct/debug/oracle-study/task5-plan-part16-Z1uKjBkj/`:
[piano e arresti](../../../ct/debug/oracle-study/task5-plan-part16-Z1uKjBkj/experiment-plan.md),
[budget proposti](../../../ct/debug/oracle-study/task5-plan-part16-Z1uKjBkj/budgets-proposed.json),
[audit statico](../../../ct/debug/oracle-study/task5-plan-part16-Z1uKjBkj/static-audit.md),
[riuso helper](../../../ct/debug/oracle-study/task5-plan-part16-Z1uKjBkj/helper-reuse.md),
[report](../../../ct/debug/oracle-study/task5-plan-part16-Z1uKjBkj/report.md),
[review inline separata](../../../ct/debug/oracle-study/task5-plan-part16-Z1uKjBkj/final-review.txt),
[conservazione finale](../../../ct/debug/oracle-study/task5-plan-part16-Z1uKjBkj/preservation.json).
**STOP:progettazione conclusa;Task5,catena completa e confronto ordinario
restano aperti. Nessun run lungo autorizzato:richiede approvazione esplicita
del piano e dei budget,poi preparazione/review statica dei nuovi adattatori.**

### Sessione precedente: parte15, prefisso100 verificato


**Ultima sessione: Task5 parte15, sola fase B / Task2 del piano parte9, 1 ottobre 2026: prefisso100 verificato e STOP finale.**
Superpowers inline con revisione finale inline separata dello stesso autore,
senza subagent;checkout esistente,nessun commit/reset/stash/pulizia.
**Task2 completata nel perimetro autorizzato.** Snapshot produzione sotto
approved-code/,fuori dal glob *.py,senza restringere gate.Logging registra
e propaga gli exit reali anche di chiusura.Audit producer→consumer25/25;
baseline unica70/70uv0 con tutti i30 gate originali;review statica22/22;
preflight unico33/33exit0,0,786s≤60s,RSS753664B≤1MiB,buffer524288B.
Sette copie diagnostiche parte8 byte-identiche;vecchia/nuova freeze distinte,
diff dict parte12 byte-esatto;conservazione prelaunch7111/7111 e freezePASS.
**Unico childexit0,265,511s≤1800s,100 riduzioni e100 undo LIFO interni**;
replay esatto CLI;certificati100 e terminale byte-identici al riferimento.
Ordinary not_run_nonterminal per step_limit100.Solo nuovo terminale
load/force/fingerprint0,940s≤60s,exit0,replay0,V/E/F15864/23796/7934.
Analisi45/45,228 eventi/1228 record,profili/nesting/guardie/ruoli/cap/
accounting validi.RSSmax campionato267,734375MiB≤512;HWM290,515625MiB;
direct0,279237366s≤3,sonde già incluse0,271532251s.
Confronto parte8:checker36 chiamate inclusivo/esclusivo13,313406126s contro
14,36437325s,RSScampionato−0,8125MiB ma HWM+9,5MiB.Segnale misto,
nessuna causalità/beneficio generale;finestra censurata dal massimo precedente,
deltaHWM0,RSS+1,515625MiB.Sonde/bookkeeping deltaRSS/HWMzero ai bordi.
Batteria84→81%,parte8AC;carico/heap/GC/scheduling non controllati,GC naturale.
Errore sintattico Ruby offline rilevato prima dell'esecuzione e corretto
sul solo helper,confronto unicoexit0;nessun gate scientifico o motore ripetuto.
Patch documentale aggregata rifiutata prima delle scritture,ripreparata;
tutti gli exit reali conservati,incluso syntax1 e chiusura0.
Nuova radice diretta `ct/debug/oracle-study/task5-checker-part15-HxVOcFCI/`:
[report e log](../../../ct/debug/oracle-study/task5-checker-part15-HxVOcFCI/report.md),
[freeze operativa](../../../ct/debug/oracle-study/task5-checker-part15-HxVOcFCI/frozen.json),
[gate correnti](../../../ct/debug/oracle-study/task5-checker-part15-HxVOcFCI/gate-results.json),
[analisi](../../../ct/debug/oracle-study/task5-checker-part15-HxVOcFCI/run-analysis.json),
[confronto parte8](../../../ct/debug/oracle-study/task5-checker-part15-HxVOcFCI/part8-comparison.json),
[review finale separata](../../../ct/debug/oracle-study/task5-checker-part15-HxVOcFCI/final-review.txt),
[conservazione finale](../../../ct/debug/oracle-study/task5-checker-part15-HxVOcFCI/preservation.json).
Inventario7111;pre-resume7111/7111 e Git invariati;un solo inserimento.
Produzione/test/FaceIndex/cache/snapshot/certificati/dataset/architettura e
vecchie arene preservati.Python ct/uv offline,bytecode disabilitato,
cache/temp nuove soloarena.Focused/suite/smoke0;RED/GREEN57/focused280/
suite380 parte12 solo storici.T390,921875MiB,N3/R3/K0 invariati,
discrepanza time replica1 separata.Tentativo1/1consumato.
**STOP:nessun retry,altra misura,ottimizzazione o catena completa.
Task5 e catena completa restano aperte.**

### Sessione precedente: parte14, stop alla review statica

**Ultima sessione: Task5 parte14, sola fase B / Task2 del piano parte9, 30 settembre 2026: STOP alla review statica.**
Superpowers inline con revisione finale inline separata dello stesso autore,
senza subagent; checkout esistente, nessun commit/reset/stash/pulizia.
**Task2 non completata.** Corretti nella nuova arena lo schema changed
list[str] e il logging dei gate uv. Audit statico17/17 prima dell'unica
baseline: **baseline70/70 PASS, exit uv0/controller0**,30 gate originali
conservati, vecchi hash e diff esatto dict parte12 attestati separatamente.
Review statica **21/22, exit1**, cache_read_only FALSE: baseline_check.py
salva approved-oracle_reduction.py nella root dell'arena; il glob *.py
del consumer include lo snapshot con i normali Store alla cache. Mai
importato/eseguito. Errore della preparazione non intercettato dall'audit
degli output futuri; nessun esito del motore. Applicato stop al gate fallito:
**preflight0/1, motore0/1, terminale0/1, focused/suite/smoke0**, nessuna
correzione/rilancio/riduzione/inversione/replay/misura. Ambiente e freeze
operativa NOT RUN; nuova freeze solo conservazione, NON valida per lancio.
Sette copie diagnostiche parte8 byte-identiche; codice approvato preservato.
Nessuna modifica produzione/test/FaceIndex/cache/snapshot/certificati/dataset/
architettura; nessun terminale storico caricato. Exit Ruby della chiusura
metadati non registrato separatamente, senza inventare il dato mancante;
gli exit gate uv e conservazione pre-resume sono reali e separati.
Nuova radice diretta `ct/debug/oracle-study/task5-checker-part14-ZJHeLIXF/`:
[report e log](../../../ct/debug/oracle-study/task5-checker-part14-ZJHeLIXF/report.md),
[baseline corrente](../../../ct/debug/oracle-study/task5-checker-part14-ZJHeLIXF/baseline-check.json),
[freeze sola conservazione](../../../ct/debug/oracle-study/task5-checker-part14-ZJHeLIXF/approved-code-freeze.json),
[stato gate](../../../ct/debug/oracle-study/task5-checker-part14-ZJHeLIXF/gate-results.json),
[review separata non indipendente](../../../ct/debug/oracle-study/task5-checker-part14-ZJHeLIXF/review.txt),
[conservazione finale](../../../ct/debug/oracle-study/task5-checker-part14-ZJHeLIXF/preservation.json).
Inventario7041; conservazione pre-inserimento7041/7041 e Git invariati;
un solo inserimento autorizzato nel punto di ripresa. Python da ct via uv
offline, bytecode disabilitato, cache/temp solo nell'arena. RED/GREEN57/
focused280/suite380 parte12 e preflight33/prefisso100 parte8 solo storici.
Nessun beneficio tempo/RSS dimostrato; T390,921875MiB e N3/R3/K0 invariati.
**Stop; fase B incompleta, Task5 e catena completa restano aperte.**

### Sessione precedente: parte13, stop alla baseline

**Ultima sessione: Task5 parte13, sola fase B / Task2 del piano parte9, 30 settembre 2026: STOP alla baseline.**
Superpowers inline con revisione finale inline separata dello stesso autore,
senza subagent; checkout esistente, nessun commit/reset/stash/pulizia.
**Task2 non completata.** Nuovo helper di baseline arrestato con
`TypeError: string indices must be integers` alla riga45: il campo `changed`
della conservazione parte12 contiene percorsi stringa, trattati erroneamente
come record. Errore dell'autore nella preparazione; nessun esito del motore.
La shell ha restituito0 dopo `cat`, non un PASS uv; exit uv non catturato
separatamente. Traceback conservato. Applicato stop: **nessun retry/correzione
baseline; preflight0/1, motore0/1, terminale0, focused/suite/smoke0.**
Nessuna riduzione/inversione/replay o misura tempo/RSS; nessun terminale
storico caricato. Gate baseline incompleto, static/preflight/freeze operativa/
condizioni AC-carico-OS NOT RUN. Snapshot del codice approvato conservato,
**freeze NON valida per lancio**; hash nuovi/storici distinti e sette copie
strumentazione parte8 byte-identiche. Dict parte12 preservato, nessuna
modifica produzione/test/FaceIndex/cache/snapshot/certificati/dataset/architettura.
Nuova radice diretta `ct/debug/oracle-study/task5-checker-part13-bBohgK3J/`:
[report](../../../ct/debug/oracle-study/task5-checker-part13-bBohgK3J/report.md),
[freeze sola conservazione](../../../ct/debug/oracle-study/task5-checker-part13-bBohgK3J/approved-code-freeze.json),
[baseline/log](../../../ct/debug/oracle-study/task5-checker-part13-bBohgK3J/baseline.log),
[gate e NOT RUN](../../../ct/debug/oracle-study/task5-checker-part13-bBohgK3J/gate-results.json),
[review separata non indipendente](../../../ct/debug/oracle-study/task5-checker-part13-bBohgK3J/review.txt),
[conservazione](../../../ct/debug/oracle-study/task5-checker-part13-bBohgK3J/preservation.json).
Inventario6492; conservazione pre-inserimento6492/6492 e stato Git invariati;
conservazione finale verifica soltanto questo inserimento. Cache/temp nuove
solo nell'arena, Python nuovo via uv offline da `ct/`, bytecode disabilitato;
un'iniziale lettura read-only dello schema via python3 da root è scostamento
registrato. RED/GREEN57/focused280/suite380 parte12 e preflight33/prefisso100
parte8 rimangono solo storici. Nessun beneficio tempo/RSS, T390,921875MiB e
N3/R3/K0 invariati, discrepanza time replica1 separata.
**Stop; fase B incompleta, Task5 e catena completa restano aperte.**

### Sessione precedente: parte12, sola fase A / Task1

**Ultima sessione: Task5 parte12, sola fase A / Task1 del piano parte9, 30 settembre 2026.**
Superpowers inline con revisione finale inline separata dello stesso autore,
senza subagent; checkout esistente, nessun commit/reset/stash/pulizia.
Checker iniziale byte-identico al riferimento parte9. Implementata soltanto
la trasformazione autorizzata del blocco `actual_edges`: lista invariata,
un dict locale indipendente nei due assert, stessi messaggi/ordine, rilascio
dei due locali prima dell'allocator. Resto della produzione, FaceIndex,
cache/snapshot/certificati e harness parte11 byte-identici all'inizio.
Cinque nuove funzioni TDD/equivalenza (22 casi), breve nota in architettura.
**Risultati correnti parte12:** RED reale `2 == 1` (1 fallimento atteso),
GREEN57 pass; focused avversi/cache/FaceIndex/ponti280 pass;
**unica suite completa380 pass**, exit0. Nessun test escluso.
358 pass di parte11 rimane soltanto storico, non un nuovo gate parte12.
Audit statico degli output PASS prima dei gate; subprocess/cwd isolati,
sentinelle/export reali, nessuna soppressione o mock di validità.
Budget consumato **3/4 focused≤180s,1/1 suite≤600s,ZERO smoke autonomi**;
nessun timeout o run aggiuntivo implicito. Python/pytest da `ct/` via uv offline,
bytecode/cacheprovider/autoload esterni disabilitati, nessun PYTEST_ADDOPTS;
cache uv/TMPDIR e basetemp nuovi nella sola radice diretta
`ct/debug/oracle-study/task5-checker-part12-wQMSIJST/`:
[report e log](../../../ct/debug/oracle-study/task5-checker-part12-wQMSIJST/report.md),
[patch minima](../../../ct/debug/oracle-study/task5-checker-part12-wQMSIJST/part12.patch),
[audit statico](../../../ct/debug/oracle-study/task5-checker-part12-wQMSIJST/static-isolation.txt),
[review inline non indipendente](../../../ct/debug/oracle-study/task5-checker-part12-wQMSIJST/review.txt),
[conservazione](../../../ct/debug/oracle-study/task5-checker-part12-wQMSIJST/preservation.json).
Inventario6224 preesistenti; conservazione finale nella radice verifica le sole
4 modifiche autorizzate, gli altri file/cache/vecchi artefatti e lo stato Git.
Nessun beneficio tempo/RSS misurato o dichiarato. **Fase A / Task1 conclusa;
fase B non autorizzata, nessun prefisso/catena autonoma/benchmark o diagnosi.
Stop qui; Task5 e catena completa restano aperte, nessuna estensione automatica.**

### Sessione precedente: parte11, isolamento degli output dei test

**Ultima sessione: Task5 parte11, isolamento degli output dei test, 30 settembre 2026.**
Superpowers inline con revisione finale inline separata dello stesso autore,
senza subagent; checkout esistente, nessun commit/reset/stash/pulizia.
Intervento limitato a `ct/tests/`: fixture autouse con cwd in `tmp_path` e
`debug/` reale, subprocess con cwd isolata e script assoluti, sentinella
`error.txt` verificata con export reale. Il test della directory già popolata
usa un proprio sottopercorso, conservando la verifica completa dei contenuti.
Breve nota in `docs/development.md`; nessuna modifica a produzione, checker,
FaceIndex, cache di validazione, dataset o diagnostica precedente.
**Risultati correnti:** RED sicuro su sentinelle sintetiche (due invocazioni,
2 fallimenti attesi ciascuna); GREEN72 pass; focused oracolo257 pass/1 fail
per interferenza `tmp_path/debug`, corretta e verificata nell'unica suite:
**358 pass**. Tutte le119 funzioni di test originali mantenute; due nuovi
casi parametrizzati. Audit statico degli output PASS prima dei gate e,
aggiornato dopo la correzione, prima della suite. Nessun test escluso.
Budget consumato **4/4 focused≤180s,1/1 suite≤600s,0 smoke autonomi**.
Python/pytest avviati da `ct/` via uv offline, bytecode/cacheprovider disabilitati;
cache uv, temporanei e basetemp nuovi soltanto nella nuova radice diretta
`ct/debug/oracle-study/task5-test-isolation-iXrsJJqw/`:
[report](../../../ct/debug/oracle-study/task5-test-isolation-iXrsJJqw/report.md),
[TDD e gate](../../../ct/debug/oracle-study/task5-test-isolation-iXrsJJqw/gate-results.json),
[audit statico](../../../ct/debug/oracle-study/task5-test-isolation-iXrsJJqw/static-isolation.txt),
[review inline non indipendente](../../../ct/debug/oracle-study/task5-test-isolation-iXrsJJqw/review.txt),
[conservazione](../../../ct/debug/oracle-study/task5-test-isolation-iXrsJJqw/preservation.json).
Inventario5778 preesistenti; conservazione finale verificata nella radice.
Proposta dict parte9 non implementata; ottimizzazioni/diagnosi di memoria sospese,
nessun nuovo prefisso/catena/benchmark o misura autonoma.356 PASS/S1 precedenti
restano soltanto storici. **Stop dopo l'isolamento; Task5 e catena completa aperte.**

### Sessione precedente: parte10, sola fase A arrestata al controllo statico

**Ultima sessione: Task5 parte10, sola fase A; stop al controllo statico degli output, 30 settembre 2026.**
Superpowers inline con revisione finale inline separata nello stesso autore,
senza subagent. Checker corrente byte-identico al riferimento parte9: proposta
minima ancora applicabile, **nessuna ottimizzazione implementata**.
**Blocco prima del RED:** `test_theta_is_terminal_in_existing_pipeline`
(`ct/tests/test_oracle_reduction.py:301`, incluso nel focused avversi e nella
suite) chiama `init_f_distribution()`; `ct/4ct.py:2178` apre con `w` il
preesistente `ct/debug/debug.f_distribution.json.dump` (291 byte).
`reduce_faces()` apre inoltre lo stesso nome fisso con `a`; basetemp/tmp_path
non isolano quelle aperture. Altri test della suite hanno lo stesso percorso;
sentinella `debug/error.txt` non reindirizzata nel test del limite Kempe.
Mandato parte10 impone stop prima dell'esecuzione: nessun test eliminato dal
gate, nessuna patch di isolamento fuori perimetro. **RED/GREEN/avversi/suite
NOT RUN; budget0/4 focused,0/1 suite,0 smoke.** Nessun import motore/NetworkX,
tentativo/prefisso/preflight/benchmark/replay separato o terminale caricato.
Per riprendere A occorre risolvere progetto/autorizzazione dell'isolamento
mantenendo tutti i test; TDD e gate restano da eseguire. Fase B non autorizzata.
Nuova radice diretta `ct/debug/oracle-study/task5-checker-phase-a-51fLrHan/`:
[report](../../../ct/debug/oracle-study/task5-checker-phase-a-51fLrHan/report.md),
[evidenza statica](../../../ct/debug/oracle-study/task5-checker-phase-a-51fLrHan/static-isolation.txt),
[comandi](../../../ct/debug/oracle-study/task5-checker-phase-a-51fLrHan/commands.md),
[gate NOT RUN](../../../ct/debug/oracle-study/task5-checker-phase-a-51fLrHan/gate-results.json),
[review inline non indipendente](../../../ct/debug/oracle-study/task5-checker-phase-a-51fLrHan/review.txt),
[conservazione](../../../ct/debug/oracle-study/task5-checker-phase-a-51fLrHan/preservation.json).
5819 file preesistenti inventariati; solo inserimento qui. Esito e conteggi
del controllo di conservazione finale registrati alla chiusura nella radice.
Produzione/test/architettura non modificati. Scostamento procedurale registrato:
piccolo preservation.json parte9 stampato completo; successive letture selettive.
Nessun beneficio RSS/tempo misurato; discrepanza temporale replica1 separata,
356 PASS/S1 soltanto storici. **Stop; Task5 e catena completa restano aperte.**

### Sessione precedente: parte9, analisi offline e progetto minimo
**Ultima sessione: Task5 parte9, analisi offline e progetto minimo, 30 settembre 2026.**
Superpowers inline; ZERO nuovi tentativi/riduzioni/inversioni/replay/preflight/
benchmark/suite/smoke, nessun import motore/NetworkX o caricamento di stati/dataset.
Dati parte8 soltanto:21/21 riconciliazioni offline,10/10 controlli documentali
AST/hash. Finestra inverse60–95:sei esclusivi29,950831165s; checker14,364373250s
(47,95985%); residuo undo0,369940667s; sonde0,306623162s; bookkeeping0,010562584s;
gap0,000594088s. Totale disgiunto30,638551666s; inclusivi annidati non sommati.
Direct processuale0,315377826s distinto dai corpi preesistenti dell'osservatore.
Lettura statica:inventario archi convertito due volte in dict; temporanei dart,
indice atteso e proiezioni coesistono. **Proposta, non implementazione:** un solo
dict indipendente dalla lista originale, due assert invariati per significato/
ordine/messaggi, rilascio locale dopo l'ultimo uso. Risparmia una costruzioneO(E);
beneficio RSS/tempo ignoto, nessuna attribuzione del picco storico al checker.
FaceIndex indipendente, molteplicità/identità/ordine/cache/controlli tutti preservati
nel progetto; T/N/R/K e discrepanza timeR1 separati. Piano futuro con TDD reale,
avversi/force/cache, gate e budget A/B da autorizzare esplicitamente; zero smoke
nel budget proposto, deroga futura dichiarata per preservare output preesistenti.
Nuova radice sorella `ct/debug/oracle-study/task5-checker-design-Y88Wc0ir/`:
[report](../../../ct/debug/oracle-study/task5-checker-design-Y88Wc0ir/report.md),
[piano futuro](../../../ct/debug/oracle-study/task5-checker-design-Y88Wc0ir/plan.md),
[costi](../../../ct/debug/oracle-study/task5-checker-design-Y88Wc0ir/cost-analysis.json),
[review inline non indipendente](../../../ct/debug/oracle-study/task5-checker-design-Y88Wc0ir/review.txt),
[conservazione](../../../ct/debug/oracle-study/task5-checker-design-Y88Wc0ir/preservation.json).
5733 file preesistenti inventariati; unico inserimento qui, resto preservato.
Scostamento procedurale registrato nella review:piccolo preservation.json parte8
stampato completo nella lettura iniziale; successive letture selettive.
356 PASS/S1 soltanto storici. **Stop; nessuna autorizzazione del motore implicita.
Task5 e catena completa restano aperte.**

### Sessione precedente: parte8, unico tentativo verificato

**Ultima sessione: Task5 parte8, strumentazione entro budget e unico tentativo verificato, 30 settembre 2026.**
Superpowers inline; diagnosi piccola unica: residual loader/compilazione901120B,
buffer524288B, altri delta non visibili alla risoluzione16KiB; nessuna causalità
oltre i dati. Revisione esterna in tre unità, tutti gli import dentro identica
baseline; gate1MiB invariato, GC naturale. Baseline30 e static22 valide;
preflight finale unico33/33, RSS aggiunto0,75MiB, time/ps/vmmap exit0 fuori
sandbox. Freeze/ambiente AC/conservazione prelaunch5623 validi.
**UN solo child, exit0:100 riduzioni/100 inversioni interne,275,934456s**.
Certificati/terminale byte-identici al prefisso100; replay interno esatto;
terminale solo load/force/fingerprint, nessun replay separato.45 gate offline
validi,228 eventi,1228/2048 record, direct0,315378s; memoria probe child
0,71875MiB, RSS campionato268,546875MiB, HWM281,015625MiB, cap rispettati.
Cinque piccoli incrementi HWM nella famiglia checker globale (inverse66/69/
83/86/91,+0,78125MiB); due sonde +16KiB RSS sotto HWM, nessun nuovo massimo
nell'osservatore. Censura/ambiguità causale e perturbazione indiretta restano;
pattern storico+85,53125MiB non riprodotto. T/N/R/K invariati, timeR1 separato.
Nuova radice sorella `ct/debug/oracle-study/task5-memory-components-mkFjTAca/`:
[report e limiti](../../../ct/debug/oracle-study/task5-memory-components-mkFjTAca/report.md),
[analisi](../../../ct/debug/oracle-study/task5-memory-components-mkFjTAca/run-analysis.json),
[conservazione](../../../ct/debug/oracle-study/task5-memory-components-mkFjTAca/preservation.json);
baseline/preflight/freeze/ambiente/review/CSV/comandi nella stessa radice.
Motore/test/dataset/cache/modifiche locali e artefatti precedenti preservati;
solo inserimento qui. Nessuna suite/smoke/altre mappe;356/S1 solo storici.
**Budget autorizzato esaurito; stop. Task5 e catena completa restano aperte.**

### Sessione precedente: parte7, stop al budget

**Ultima sessione: parte7, ripresa autorizzata; stop al budget del preflight, 30 settembre 2026.**
Permessi risolti con eccezione mirata alla sandbox:time/ps/vmmap exit0.
Nuova baseline30 e revisione statica inline19 valide. Preflight piccolo
senza motore:24/25 validi, unico falso `added_memory_budget`; RSS aggiunto
**1,203125MiB >1MiB**, buffer512KiB, strutture possedute524728B. Componenti
non misurati separatamente:nessuna causa attribuita. **Zero tentativi motore,
riduzioni/inversioni**, nessun rilancio, freeze valido o modifica di soglie.
Artefatti nuovi: `ct/debug/oracle-study/task5-targeted-authorized-BSUDO9vJ/`:
[esito e limiti](../../../ct/debug/oracle-study/task5-targeted-authorized-BSUDO9vJ/report.md),
[preflight](../../../ct/debug/oracle-study/task5-targeted-authorized-BSUDO9vJ/preflight.log),
script/hash, comandi, revisione e conservazione nella stessa radice.
Solo inserimento qui; motore/test/dataset/cache e artefatti precedenti
preservati. Nessuna evidenza RSS del motore:localizzazione/riproduzione/
censura non valutabili. Limiti parte6 e timeR1 separati;356/S1 solo storici.
**Task5 e catena completa aperte.** Ripresa chiusa al gate fallito.

### Sessione precedente: parte7, stop permessi

**Ultima sessione: parte7, strumentazione preparata; stop al preflight, 30 settembre 2026.**
Protocollo parte6 approvato. Baseline30 controlli e revisione statica inline19
validi; preflight della sola strumentazione exit1: sandbox, `/bin/ps`,
`PermissionError: Operation not permitted`. **Zero tentativi del motore,
zero riduzioni/inversioni**; nessun retry, escalation, freeze valido o lancio.
Observer/launcher/buffer esterni salvati, verifica dinamica incompleta.
Artefatti: `ct/debug/oracle-study/task5-targeted-8mswgLn4/`:
[esito e limiti](../../../ct/debug/oracle-study/task5-targeted-8mswgLn4/report.md),
[preflight fallito](../../../ct/debug/oracle-study/task5-targeted-8mswgLn4/preflight.log),
revisione, hash, comandi e conservazione finale nella stessa radice.
Nessuna nuova evidenza RSS o ottimizzazione; categorie di riproduzione/censura
non valutabili. Limiti parte6 e discrepanza temporale R1 restano separati.
Solo inserimento in questo punto; file/cache/artefatti preesistenti preservati.
356 PASS/S1 soltanto storici. **Task5 e catena completa aperte.** Parte7 chiusa
al gate fallito; nessuna ripresa o ulteriore corsa automatica.

### Sessione precedente: parte6

**Ultima sessione: parte6, analisi offline e progettazione, 30 settembre 2026.**
Nessuna nuova andata/replay/test/smoke, import del motore o ottimizzazione.
Dagli eventi salvati: tutti i23 incrementi storici (+85,531250 MiB) della
replica1 sono nelle coppie undo-before/after62–79 e89–93; zero nei segmenti
checkpoint/gap. Le coppie includono code delle sonde, non identificano
allocazioni. RSS cresce già51–61 e cala in80/93. Native vuote residenti
50→100:≈43,6→129,1 MiB, piccoli blocchi Python/oggetti vivi quasi stabili;
ipotesi di temporanei/ritenzione nativa sostenuta, causa non dimostrata.
Discrepanza time1202,79s vs CLI/CPU≈273s separata e non localizzata.

Artefatti nuovi: `ct/debug/oracle-study/task5-inverse62-93-9iDqoEOU/`:
[analisi e limiti](../../../ct/debug/oracle-study/task5-inverse62-93-9iDqoEOU/report.md),
[protocollo proposto](../../../ct/debug/oracle-study/task5-inverse62-93-9iDqoEOU/protocol.md),
CSV/intervalli, comandi, revisione inline e conservazione finale nella stessa
radice. Proposta motivata: **un solo tentativo≤100**, andata e replay interno
nello stesso processo, sonde interne60–95, invarianti/cache attivi e GC naturale.
**Non implementata né autorizzata/eseguita**; nessuna replica automatica per
cercare la soglia. Limiti ambientali, storico ru_maxrss e campionamento
restano validi. **Task5 e catena completa aperte.** Motore/test/cache/artefatti
precedenti preservati;356 PASS/S1 soltanto storici.

### Sessione precedente: tre repliche con osservatore congelato

**Ultima sessione: tre repliche, concluse il 30 settembre 2026.**
Tre andate100 della sola riga1 originale, ognuna seguita dal replay interno
nello stesso processo: **300 riduzioni totali**, nessun tentativo aggiuntivo.
Soglia prefissata390,921875 MiB non raggiunta: **K/R=0/3**, N=3, nessun
caso non discriminabile. Massimi386,406250 /308,125000 /313,062500 MiB.
Replica1:23 incrementi storici nel replay, ai confini delle inversioni62–93;
repliche2/3:nessuno. Tutti i300 certificati e i tre terminali identici al
riferimento, replay interni esatti e invarianti forzati dei terminali PASS.

Osservatore/native byte-identici alla diagnosi leggera. Condizioni diverse:
replica1 avviata a batteria (esplicitamente autorizzata), repliche2/3 su AC,
con intervallo notturno e carico diverso. Replica1:time1202,79s contro circa273s
interni/CPU; scarto non localizzato. **Conteggio descrittivo, non stima di
probabilità né confronto causale.** Nessuna causa del vecchio picco attribuita.

**Task5 e catena completa aperte.** Serie autorizzata esaurita, nessun'altra
corsa o ottimizzazione. Prossimo passo proposto: formulare una diagnosi mirata
dei temporanei nelle inversioni62–93, partendo dagli eventi già salvati;
qualunque nuova esecuzione richiede autorizzazione separata. Non ripetere
automaticamente una serie per cercare il superamento della soglia.

Artefatti canonici:`ct/debug/oracle-study/task5-replicates-x8rrh9HI/`; directory delle repliche in `series.json`.
[Resoconto delle repliche](../../llm-vs-4ct/4ct-oracle-study-step-3.md#aggiornamento-tre-repliche-con-osservatore-congelato).

### Sessione precedente: singola ripetizione con sonde leggere

**Ultima sessione: ripetizione con sonde leggere, 29 settembre 2026.**
Una sola andata100 della riga1 originale e replay interno nello stesso
processo. Picco storico di riferimento 390,921875 MiB **non riprodotto**:
nuovo massimo **298.125000 MiB**, già raggiunto prima del replay;
0 incrementi storici nel replay.
Tutti i 100 certificati e il terminale byte-identici; replay esatto e
invarianti forzati del terminale PASS. Arresto `step_limit`, non candidata
esaurita, errore o impossibilità matematica.

Osservatore derivato direttamente dal riferimento: checkpoint e contatori
originari, sole nuove sonde RSS/picco ai confini di inversioni/checkpoint;
nessun wrapper interno dettagliato o GC forzato. Overhead diretto
5.756796 s; perturbazione residua non quantificata. Motore/test invariati,
356 PASS/S1 soltanto storici; cache e artefatti precedenti preservati.

**Task 5 e catena completa restano aperte.** Corsa autorizzata esaurita:
nessuna ulteriore esecuzione o ottimizzazione. Prossimo passo: definire un
protocollo di riproducibilità con repliche e condizioni registrate, prima
di attribuire cause o aumentare il budget; eventuali corse richiedono nuova
autorizzazione. Questa singola misura non è un A/B conclusivo.

Artefatti: `ct/debug/oracle-study/task5-minimal-peak-s6LAt3x4/`.
Risultati e limiti nel [nuovo aggiornamento](../../llm-vs-4ct/4ct-oracle-study-step-3.md#aggiornamento-ripetizione-con-sonde-leggere).

### Sessione precedente: diagnosi con wrapper interni

**Ultima sessione: localizzazione del picco, 29 settembre 2026.**
Una sola nuova andata di 100 riduzioni TOTALI della riga 1 dall'originale,
con replay interno nello stesso processo; motore, test, cache e artefatti
precedenti preservati. **Il picco precedente di 390,92 MiB non riprodotto**:
massimo nuovo 321,078125 MiB, già raggiunto nell'andata, nessun incremento
storico nel replay. Questo non attribuisce la causa del vecchio transitorio.

- [x] Baseline: 5027 confronti riusciti; inventario 5087 file preesistenti.
- [x] Accesso time/ps/vmmap verificato prima della corsa, exit 0.
- [x] Osservatore esterno: 2310 eventi, confini di inversioni/funzioni e
  sottoperazioni checkpoint. Nessun GC forzato; invarianti/cache attivi.
- [x] Checkpoint replay 50: RSS 263,250→263,266 MiB (+16 KiB), picco
  321,078125 MiB invariato; durata 0,501631 s. Finestra storica include
  sempre il lavoro dell'osservatore 50, non solo le inversioni 51–100.
- [x] Massimo RSS campionato nel replay 267,046875 MiB dopo checker
  completo all'inversione 87: **massimo dei campioni, non picco effettivo**.
  Native vuote residenti 36,003 MiB ai checkpoint 50 e 100; snapshot circa
  2,24–2,27 MiB. Il transitorio storico non è attribuibile con questa corsa.
- [x] Tutti i 100 certificati e terminale byte-identici; replay interno
  esatto, terminale con invarianti forzati PASS; esito `step_limit`.
- [x] Tempi meno osservazione misurata: andata 181,509 s, replay 79,434 s,
  salvataggio 0,455 s. Checkpoint CLI 5,862 s + probe 0,217 s;
  perturbazione residua non quantificata. Processo 268,50 s / 321,078 MiB.
- [x] Piano/resoconto, comandi, conservazione e revisione delle evidenze
  nella nuova radice; nessuna suite/smoke rieseguita, 356 PASS/S1 storici.

**Task 5 e catena completa restano aperte.** Nessun replay separato aggiuntivo,
altra andata, altra mappa, validazione delle 151 mappe o ottimizzazione.
Prossimo esperimento soltanto proposto: nuova andata≤100 autorizzata, con
osservatore precedente e sole letture picco/RSS ai confini delle inversioni
e del checkpoint 50, senza wrapper interni, per cercare la riproducibilità
con minore strumentazione. Non sarebbe ancora un A/B causale conclusivo.

Artefatti: `ct/debug/oracle-study/task5-replay-peak-in1wh35K/`.
Dettagli nel [resoconto della localizzazione](../../llm-vs-4ct/4ct-oracle-study-step-3.md#aggiornamento-ricerca-del-picco-transitorio-nel-replay-interno).

### Sessione precedente: primo prefisso di 100 riduzioni

**Prefisso di 100 riduzioni TOTALI, 29 settembre 2026.**
Task 1–4 complete; Task 5 e catena completa ancora aperte. Autorizzazione
esplicita 20→100 sulla sola riga 1 dall'input originale; una sola andata,
nessuna modifica a motore/test/cache. Baseline salvata verificata esatta.

- [x] Prefisso 100: `step_limit`, F3=1/F4=51/F5=48, 100 scambi parziali e
  due cicli; V/E/F 16064/24096/8034→15864/23796/7934.
- [x] Checkpoint 20/50/100 di andata e replay interno; fasi separate.
  Andata 184.833 s, replay 80.032 s,
  salvataggio 0.453 s, sottratti soltanto i checkpoint;
  residuo overhead non quantificato. Processo 272.57 s / 390.92 MiB.
- [x] Primi 20 certificati byte-identici alla baseline; replay interno e
  separato esatti; terminale con invarianti completi forzati PASS.
- [x] Replay separato misurato 65.18 s / 349.750 MiB.
  Primo tentativo esatto ma RSS assente per `time/sysctl` nel sandbox;
  conservato, poi ripetuto solo il replay con accesso verificato, exit 0.
- [x] Piano/resoconto e comandi aggiornati; sorgenti/test/debug/cache
  preservati. 356 PASS e smoke S1 sono baseline, non rieseguiti.

Picco nel replay strumentato 326,92→390,92 MiB fra le letture 50 e 100,
incluso il lavoro dell'osservatore al checkpoint 50: attribuzione al motore
o all'osservatore non risolta. RSS ai checkpoint circa 299 MiB, snapshot
circa 2,25 MiB. Nessuna conclusione di
memoria costante/leak o impossibilità matematica; singole misure con limiti
di strumentazione espliciti. Prossimo passo proposto: localizzare questo
picco transitorio entro lo stesso budget 100, prima di aumentarlo ancora.
Non avviati catena completa, altre mappe, validazione delle 151 mappe.

Artefatti: `ct/debug/oracle-study/task5-prefix100-izztpr64/`. Dettagli nel
[resoconto del prefisso 100](../../llm-vs-4ct/4ct-oracle-study-step-3.md#aggiornamento-prefisso-autorizzato-di-100-riduzioni-totali).

### Baseline precedente: istantanee per componenti

**Aggiornato:** 29 settembre 2026. **Stato:** Task 1–4 completate;
**Task 5: serializzazione delle istantanee per componenti integrata; catena completa aperta**.
Con TDD, la costruzione di un unico buffer `marshal` viene sostituita dalla
serializzazione dei 14 componenti in un solo flusso zlib. Tutti gli invarianti
e il riuso della cache restano attivi. GREEN **249 test mirati**, suite
**356 PASS**, smoke S1 PASS. Due diagnosi e una CLI di produzione, sempre
sola riga 1 con 20 riduzioni, più replay di produzione in un nuovo processo.

Diagnosi per stadio: liberando il buffer completo dello snapshot 40, le
regioni native vuote residenti crescono di circa 4,6 MiB. La variante elimina
quel buffer, conservando buffer per componente: il massimo osservato passa
da 4,65 a 2,17 MiB. Picco diagnostico **400,19→311,92 MiB**; regioni vuote
nel replay 1→20: **22,3→162,0 MiB** prima, **69,7→69,7 MiB** dopo. Peggiora
la memoria dell'andata: picco **250,23→296,91 MiB**. La policy di libmalloc
e tutte le altre allocazioni non sono ricostruite.

CLI ordinaria: catena **34,574952→37,668683 s**, tempo completo
**50,15→54,49 s**, RSS **397,66→311,75 MiB (−21,60%)**. Replay separato
**12,92→13,80 s**, **214,25→219,38 MiB (+2,39%)**. Singole corse: nessuna
garanzia statistica, nessuna pretesa di memoria costante o di miglioramento
della sola andata. Certificati e terminale byte per byte identici ai cinque
prefissi precedenti; replay interno/separato esatti, controllo completo
forzato del terminale PASS e payload tipizzato precedente recuperato esattamente.

Artefatti: `ct/debug/oracle-study/task5-snapshot-buffers-hk5diq7u/`.
Modificati soltanto motore, test cache e documentazione pertinente; ogni
altro file locale e i 14 artefatti fissi preservati. Nessun commit, reset,
pulizia o nuova checkout. Revisione indipendente finale conclusa senza
rilievi; verbale `review.txt` nella nuova radice.
`step_limit` resta non conclusivo, ordinario non eseguito; nessun errore
software del motore osservato né impossibilità matematica. La catena lunga,
altre mappe e validazione delle 151 mappe rimangono escluse.

Intervento circoscritto implementato; Task 5 resta aperta. Ogni ulteriore
strategia sui buffer o estensione del prefisso sarà un passo distinto.
Evidenze e comandi nel [resoconto sui buffer](../../llm-vs-4ct/4ct-oracle-study-step-3.md#aggiornamento-istantanee-serializzate-per-componenti).

Repository: `maps-coloring-python`. Branch osservato: `feature/machine-learning`.
HEAD di riferimento: `08dd2e9` (`feat: add S5 coloring workflow and planar exports (#21)`).
Non fare checkout di questo SHA: le modifiche non committate fanno parte del
lavoro corrente. Al momento della stesura risultano modificati `ct/4ct.py`,
`ct/tests/test_colored_planar.py`, `docs/architecture.md`, `docs/development.md`;
esperimenti, test dell'oracolo, resoconti e piano sono ancora non tracciati.
Non sono stati creati commit nelle Task 1–4. La Task 4 aggiunge anche
`ct/experiments/oracle_reduction_run.py` e la piccola fixture
`ct/examples/planar/oracle-study-dodecahedron.colored.planar`; estende motore,
test, architettura, sviluppo e resoconto step-2. Ricontrollare lo stato nella
nuova sessione e preservare tutto, inclusi i file non tracciati.

### Già fatto: non ripartire da zero

- [x] Ricognizione di rappresentazioni, riduzione, ricostruzione e ricerca Kempe.
- [x] Conservazione separata dell'oracolo iniziale in `graph.graph["oracle_faces"]`.
- [x] Conteggio del criterio F5 sulle 151 mappe: 571.369 F5, 2.856.845 candidate, 1.888.271 compatibili.
- [x] Nove riduzioni F5 campione con ritorno esatto verificato.
- [x] Controesempio alla sufficienza dei soli cinque gradi per determinare l'esito cromatico corrente.
- [x] [Resoconto e comandi del passo 1](../../llm-vs-4ct/4ct-oracle-study-step-1.md).
- [x] [Task 1: studio F2/F3/F4](../../llm-vs-4ct/4ct-oracle-study-step-2.md): otto fixture, 30 andate/ritorni manualmente specificati, entrambi i sottocasi F4 a due colori.
- [x] Task 2: `OracleState`, ID persistenti, certificati a differenze e `apply_step()` / `undo_step()` atomici; [contratti implementati](../../architecture.md#prototipo-sperimentale-delloracolo).
- [x] Task 3: `plan_step()` read-only su candidata fissa; F2 dedicata, cammini keyed F3–F5 e preparazione F4. 36 riduzioni automatiche con risultati attesi indipendenti, paralleli già presenti nel cammino, rifiuti senza mutazioni e ritorno esatto.
- [x] Task 4: catene deterministiche, replay su copia, persistenza schema 1, CLI e confronto ordinario separato. Dodecaedro: nove passi fino a theta, replay in processo nuovo e ordinario riusciti; prefisso a due passi salvato come non conclusivo.

Verifiche Task 1: baseline di 98 test superata; poi 8 test fixture,
45 test del nuovo file e 143 test complessivi superati. Verifiche fresche
Task 2: **72 test dell'oracolo e 170 test complessivi superati**; revisione
indipendente eseguita, correzione dei contatori ID verificata RED→GREEN.
Nella Task 3 sono stati aggiunti 46 test: RED per `plan_step()` assente,
poi **118 test dell'oracolo e 216 complessivi PASS**. Smoke S1 da 10 facce
completato (16 vertici, 24 archi, sette riduzioni e colorazione finale valida).
La ripresa Task 4 ha riconfermato la baseline di 216 test. Risultati finali:
**201 test dell'oracolo e 299 complessivi PASS**, smoke S1 PASS. Revisione
indipendente senza rilievi; 96 ulteriori catene piccole con embedding
invertiti/bordi ruotati e JSON esatti. Catena, replay e salvataggio sono
implementati; la Task 5 ne ha misurato il costo su un prefisso della riga 1,
mentre la catena grande completa resta aperta. Dettagli e comandi nel
[resoconto step-2 aggiornato](../../llm-vs-4ct/4ct-oracle-study-step-2.md#aggiornamento-task-4-catene-persistenza-e-replay-su-piccole-mappe).

Il dataset è `ct/maps_3000_maps_of_8000_faces.colored.planar`: il nome storico
non indica il numero attuale di mappe. Le 151 righe contengono le colorazioni
già controllate dall'autore. Il primo studio non ha eseguito catene complete.

## Mappa dei file

| File | Responsabilità / intervento previsto |
| --- | --- |
| `docs/llm-vs-4ct/4ct-oracle-study-step-2.md` | Nuovo: regole F2/F3/F4, ipotesi, esempi e casi aperti. |
| `ct/tests/test_oracle_reduction.py` | Nuovo: piccoli embedding colorati, test dei passi e della catena. |
| `ct/experiments/oracle_reduction.py` | Nuovo: stato, certificati, trasformazioni, catena e inverso esatto. |
| `ct/experiments/oracle_reduction_run.py` | Nuovo: CLI, serializzazione, provenienza e confronto ordinario. |
| `docs/llm-vs-4ct/4ct-oracle-study-step-3.md` | Nuovo: esito della prima catena, costi e riproducibilità. |
| `docs/development.md` | Aggiungere i comandi solo quando saranno implementati e verificati. |
| `ct/experiments/f5_oracle_probe.py` | Conservare come esperimento di riferimento del passo 1. |
| `ct/4ct.py`, `ct/ct_graph_utils.py` | Leggere e riusare le primitive; nessuna modifica algoritmica prevista in questa fase. |

Caricare `4ct.py` con `importlib`, come nei test esistenti. Reinizializzare
`stats` quando si chiamano i gestori. Non importare il prototipo del passo 1
come libreria: contiene configurazione globale del logging e ipotesi sugli
archi semplici. Non aggiungere wrapper di pura delegazione.

## Task 1: risolvere sulla carta e su piccoli casi F2/F3/F4

**Files:** creare il resoconto step-2 e `ct/tests/test_oracle_reduction.py`.
Leggere `ariadne_case_f2/f3/f4`, `reduce_faces()` e le primitive di Kempe e
di modifica delle facce, dopo `docs/algorithm.md`.

**Interfaces:** consuma embedding con triple `(u, v, color)`; produce fixture
`colored_cases` indicizzate da `theta`, `f2`, `f3`, `f4_two_colors`,
`f4_three_colors`, `f5`, `f5_no_direct_witness`, ciascuna con embedding e
scelta locale esplicita (nessun passo da applicare per theta). L'ultimo caso
è una piccola mappa colorata con gli estremi della candidata su cicli
complementari distinti. Le fixture e i confronti restano nel file di test.

- [x] Nel resoconto disegnare/descrivere una trasformazione per ciascuna famiglia: colori prima/dopo, archi fusi, eventuale cammino o ciclo scambiato, ipotesi e inverso. Distinguere F4 con molteplicità 2,2 da F4 con 2,1,1. Non equiparare una spiegazione locale a una prova universale.
- [x] Scrivere `test_colored_case_fixtures_are_valid`: su ogni piccolo caso controllare cubicità, colori distinti, assenza di loop/ponti e due occorrenze orientate per arco; controllare che la faccia selezionata abbia il pattern dichiarato. Partire dalle fixture tetraedro/theta in `test_colored_planar.py` e dal prisma colorato in `test_selection5.py`, senza importare test da altri test.
- [x] Eseguire `uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_reduction.py -k fixtures -q`. Risultato richiesto: PASS delle fixture, non ancora delle trasformazioni. Questo controllo riguarda nuovi piccoli casi di studio, non le 151 mappe.
- [x] Per F4 a due colori stabilire quando serve uno scambio preliminare e quale connessione esterna lo rende possibile; annotare esplicitamente i casi non risolti. Per F2 escludere theta dall'ulteriore riduzione; per F3 includere la produzione di archi paralleli.
- [x] Chiudere la Task con tabella «famiglia / costruzione / ipotesi / fixture / caso aperto» e spiegare il risultato all'autore. Se una famiglia resta aperta, dedicare il passo successivo a quel caso: non lanciare la mappa grande e non marcare la copertura completa.

**Criterio di uscita:** regole candidate esplicite e casi piccoli corretti;
la verifica automatica delle trasformazioni avviene nella Task 3.

**Esito Task 1:** criterio raggiunto. Sono aggiunti anche controlli di
trasformazioni con cammini e fusioni scritti a mano, non un'API generale.
La futura Task 3 deve ancora scoprire automaticamente i passi e verificarli
su stati arbitrari. Le identità persistenti e il replay delle occorrenze
colorate sono stati aggiunti nella Task 2; restano aperte serializzazione
e gestione generale dei casi degeneri.

## Task 2: stato con identità degli archi e certificato reversibile

**Files:** creare `ct/experiments/oracle_reduction.py`; estendere i test.

**Interfaces:** definire `OracleState`, `Candidate`, `StepWitness`,
`StepAttempt` secondo la specifica, più:

```python
def make_state(colored_faces: Sequence[Sequence[Tuple[int, int, str]]]) -> OracleState: ...
def assert_state_invariants(state: OracleState) -> None: ...
def apply_step(state: OracleState, witness: StepWitness) -> None: ...
def undo_step(state: OracleState, witness: StepWitness) -> None: ...
```

I tipi `Sequence`, `Tuple`, `Optional` vengono da `typing`. I metadati delle
facce devono preservare identità distinte anche quando le liste sono uguali;
gli ID degli archi devono distinguere i tre archi di theta.

- [x] Scrivere i test fallenti `test_theta_keeps_three_edge_ids_and_three_face_ids`, `test_make_state_does_not_alias_input`, `test_witness_roundtrip_restores_full_state`, `test_stale_witness_does_not_mutate_state`. Il certificato di prova è costruito a mano da una trasformazione della Task 1, senza dipendere da `plan_step()` non ancora implementata.

```python
# Schema delle asserzioni del round-trip; snapshot_state è un helper dei test
# che include vertici, archi con ID/colori, facce/occorrenze/ID e contatori ID.
before = snapshot_state(state)
apply_step(state, witness)
assert_state_invariants(state)
undo_step(state, witness)
assert snapshot_state(state) == before
assert_state_invariants(state)
```

- [x] Eseguire `uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_reduction.py -k 'edge_ids or alias or witness' -q`; confermare fallimento per API mancante, non per fixture invalida.
- [x] Implementare lo stato e le patch reversibili. Conservare il record Arianna separato dal certificato cromatico; aggiornare/ripristinare anche ID e `FaceIndex`. Usare wrapper esistenti solo quando identificano l'arco giusto: un helper che prende la prima chiave parallela non è adatto a un certificato keyed.
- [x] Scrivere `test_corrupted_occurrence_is_detected_with_unchanged_counts`: alterare l'ID di una sola occorrenza in theta; `assert_state_invariants()` deve sollevare `AssertionError` pur con V/E/F invariati. Confermare il fallimento prima di completare il controllo di coerenza.
- [x] Eseguire `uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_reduction.py -q`: tutti i test della Task 1 e 2 devono essere PASS, compreso il controllo della corruzione.
- [x] Aggiornare questo piano con evidenze e file cambiati. Nessun commit richiesto né creato; il lavoro preesistente è preservato.

**Esito Task 2:** aggiunto `ct/experiments/oracle_reduction.py`; estesi
`ct/tests/test_oracle_reduction.py`, `docs/architecture.md`, specifica e
presente piano. Baseline: 143 test. RED iniziale: cinque errori per modulo
assente; poi test negativi sulle occorrenze, sui record Arianna e sugli scambi.
GREEN finale: 72 test dell'oracolo (45 precedenti + 27 nuovi), 170 complessivi.
La revisione ha individuato contatori frazionari accettati: due regressioni
prima fallenti, poi superate dopo il controllo di tipo intero non negativo.

I certificati F2/F3/F4 ripristinano lo snapshot completo; F4 verifica anche
uno scambio preliminare lontano dalla faccia scelta. Sono controllati
certificati obsoleti, patch cromatiche errate, occorrenze/rotazioni/indici
incoerenti, vicini Arianna interni/esterni e tracce di scambio non valide.
`StepAttempt` separa un certificato da un esito non conclusivo.

**Limiti da portare alla Task 3:** gli ID sono chiavi NetworkX globali, non
chiavi locali automatiche; dopo un passo riuscito recuperare i riferimenti
grafo/liste/indice da `OracleState`. Il controllo attuale verifica la
correttezza dell'embedding fornito dal certificato, non ne deriva
indipendentemente la chirurgia locale. `plan_step()` dovrà costruirla usando
le primitive delle facce e verificarla nei test, inclusi i vicini coincidenti.
Ogni passo usa copie temporanee e controlli globali: misurarne il costo prima
delle catene grandi. Nessuna lettura o modifica del dataset nella Task 2.

## Task 3: produrre e verificare i passi F2–F5

**Files:** estendere il motore, i test e il resoconto step-2.

**Interfaces:** consuma stato, candidate e certificati della Task 2; produce
`plan_step(state: OracleState, candidate: Candidate) -> StepAttempt`.
`status == "certified"` implica `witness is not None`; gli altri stati hanno
`witness is None` e una motivazione. Tutti i tentativi sono read-only.

- [x] Scrivere `test_each_supported_family_reduces_and_replays`, parametrizzato sui casi della Task 1. Per ogni candidato supportato verificare le seguenti asserzioni, poi il ritorno esatto mediante `undo_step()`.

```python
before = snapshot_state(state)
n, m, f = len(state.graph), state.graph.number_of_edges(), len(state.g_faces)
attempt = plan_step(state, candidate)
assert snapshot_state(state) == before
assert attempt.status == "certified"
apply_step(state, attempt.witness)
assert (len(state.graph), state.graph.number_of_edges(), len(state.g_faces)) == (n - 2, m - 3, f - 1)
assert_state_invariants(state)
```

- [x] Scrivere i test `test_rejected_attempt_is_read_only`, `test_unavailable_witness_is_not_impossibility`, `test_parallel_path_uses_edge_ids`, `test_coincident_neighbors_keep_face_index_consistent`. Per `f5_no_direct_witness` richiedere `status == "no_witness"`, `witness is None` e snapshot invariato; sul cammino parallelo deve cambiare solo il colore dell'ID indicato. I casi di facce coincidenti devono superare `FaceIndex.validate()` e il ritorno esatto. Nessun test unitario deve dipendere dal file da 151 mappe.
- [x] Eseguire `uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_reduction.py -q`; confermare i nuovi fallimenti per comportamento mancante.
- [x] Implementare solo le costruzioni motivate dalla Task 1. F2 ha trattamento dedicato. Per F3–F5 registrare gli scambi reali e riusare `join_faces()` / `remove_vertex_from_face()` rispettando occorrenze e identità. Controllare ammissibilità strutturale e invarianti del risultato; non generalizzare a tutti gli stati il conteggio positivo delle sole F5 iniziali.
- [x] Rieseguire i test: PASS. Eseguire anche `uv run --python ../.venv/bin/python python -m pytest tests -q` per controllare la compatibilità con il programma esistente.
- [x] Completare il resoconto step-2 con prove sperimentali, precondizioni e limiti residui, aggiornare le checkbox e comunicare il risultato prima di avviare catene lunghe. Se emerge un caso non coperto, conservarlo come fixture e riaprire la Task 1 su quella famiglia.

**Esito Task 3:** implementato `plan_step()` in
`ct/experiments/oracle_reduction.py`; estesi test, resoconto step-2,
architettura e presente piano. Il tentativo non cambia la candidata né lo
stato: prima controlla l'ammissibilità strutturale, poi produce scambi e
patch e verifica il risultato temporaneo. Le primitive delle facce sono
riusate insieme a metadati keyed, così gli archi paralleli e le facce uguali
per valore non collassano. F2 tratta il digono senza scambi e rifiuta theta
terminale; F4 registra correttamente ciclo preliminare e cammino parziale.

Evidenza: 46 fallimenti attesi per API assente e 72 test precedenti PASS;
poi 118 test dell'oracolo e 216 complessivi PASS, con Python 3.9. I sei casi
supportati sono verificati con tutte le permutazioni dei colori. La fixture
F5 senza criterio diretto restituisce `no_witness`, mentre un altro lato
della stessa faccia viene certificato. Una fixture aggiuntiva controlla che
il cammino cambi solo l'ID blu fra due archi paralleli blu/verde. Le fixture
F2/F3 verificano coincidenze e indice, oltre al ritorno dello snapshot completo.

Diagnostica sui sette stati distinti delle fixture: 132 candidate orientate
provate singolarmente, 86 certificate con ritorno esatto, 32 `no_witness`,
8 `structurally_rejected`, 6 `unsupported_case` su theta. Nessuna catena o
lettura del dataset. Revisione indipendente del delta Task 3 rispetto alle
copie precedenti, necessaria perché il codice è ancora non tracciato e
BASE/HEAD coincidono; esito e ulteriori controlli registrati sotto.

Revisione conclusa senza problemi azionabili: 216 test complessivi superati
indipendentemente; sulle fixture, candidate provate anche con embedding
invertito e facce ruotate (832 passi certificati con ritorno esatto,
448 `no_witness`, 64 rifiuti strutturali, 24 risposte terminali).
Restano deliberatamente esclusi catene/JSON/budget/confronto ordinario,
dataset e prestazioni su mappe grandi, attributi NetworkX estranei al
contratto e ogni pretesa di completezza matematica universale.

Comandi realmente eseguiti da `ct/`:

```bash
UV_CACHE_DIR=/private/tmp/4ct-oracle-uv-cache uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_reduction.py -q
UV_CACHE_DIR=/private/tmp/4ct-oracle-uv-cache uv run --python ../.venv/bin/python python -m pytest tests -q
UV_CACHE_DIR=/private/tmp/4ct-oracle-uv-cache uv run --python ../.venv/bin/python python 4ct.py -s1 -r2 10
```

La cache è stata spostata solo per questi comandi: il sandbox impediva di
scrivere nella cache utente predefinita di `uv`. I log sono nella directory
ignorata `.superpowers/sdd/2026-09-28-oracle-reduction-study/`, insieme alle
copie e impronte dei dodici file locali preesistenti in `task-3-before/`.
Questi artefatti di sessione non viaggiano con Git; per riprodurre le prove
bastano il motore e le fixture nel repository. Lo smoke produce gli usuali
artefatti ignorati sotto `ct/debug/`.

**Limiti e punto di ripresa:** nessuna garanzia universale sugli stati
intermedi. F5 cerca solo il cammino complementare; F4 prova al massimo un
ciclo preliminare della costruzione studiata. `no_witness` non significa
impossibilità del ramo; gli errori di invarianti non vengono intercettati
come esiti della ricerca. Le facce mantenute conservano ID e ordine relativo;
la faccia unita riceve un nuovo ID in fondo alla lista. Le copie e verifiche
globali per passo richiederanno misurazione prima delle mappe grandi.
La prima attività futura è il test `test_small_chain_reaches_theta_and_replays`
della Task 4, seguito da budget e serializzazione; non eseguire la Task 5
né ripetere la validazione delle 151 mappe prima di quel completamento.

## Task 4: concatenazione, salvataggio e ritorno esatto su piccole mappe

**Files:** estendere il motore; creare `ct/experiments/oracle_reduction_run.py`;
estendere i test. Nessuna nuova opzione in `4ct.py`.

**Interfaces:** nel motore definire:

```python
def run_chain(state: OracleState, max_steps: int) -> ChainResult: ...
def replay_exact(terminal: OracleState, witnesses: Sequence[StepWitness]) -> OracleState: ...
```

`ChainResult` contiene `status`, `witnesses`, contatori per F2–F5 e scambi,
e motivi delle candidate rifiutate quando non si può continuare. Nel runner:

```python
def save_run(directory: Path, terminal: OracleState, result: ChainResult, provenance: dict) -> None: ...
def load_run(directory: Path) -> Tuple[OracleState, ChainResult, dict]: ...
```

Schema versione 1: `manifest.json`, `terminal.json`, `steps.jsonl`. La
directory di output deve essere nuova: rifiutare una destinazione già
popolata. Il loader riconosce lo schema e ricostruisce gli indici, non gli
indirizzi degli oggetti Python. Una serie incompleta non è una catena completa.

- [x] Scrivere `test_small_chain_reaches_theta_and_replays`: theta deve avere V=2, E=3, F=3; il numero di passi deve essere `(initial_v - 2) // 2`, e il ritorno deve coincidere con lo snapshot iniziale. Includere theta già terminale con zero passi.
- [x] Scrivere `test_step_limit_is_inconclusive`, `test_no_certified_candidate_is_inconclusive`, `test_json_roundtrip_preserves_ids_and_colors`, `test_existing_run_directory_is_not_overwritten`. Richiedere rispettivamente `step_limit`, `no_certified_candidate`, uguaglianza del replay prima/dopo JSON, e rifiuto senza alterare i file esistenti. Permutare `red`, `green`, `blue` in una fixture per evitare un replay che funzioni solo con un theta hardcoded; non introdurre nomi di colori diversi.
- [x] Eseguire `uv run --python ../.venv/bin/python python -m pytest tests/test_oracle_reduction.py -k 'chain or limit or candidate or json or directory' -q`; confermare i nuovi fallimenti.
- [x] Implementare la politica deterministica della specifica e il replay inverso su copia. Al raggiungimento del budget salvare lo stato parziale senza dichiarare successo; verificare theta prima di fermarsi per budget, se l'ultimo passo l'ha raggiunto. Non memorizzare una copia completa per ogni livello.
- [x] Implementare serializzazione e CLI: `--input PATH`, `--map-number N` a base 1, `--max-steps N` non negativo, `--output DIR`, `--ordinary-rebuild`, `--kempe-search-limit N` positivo, e modalità separata `--replay DIR`. Per la prima prova usare solo una riga. Salvare provenienza e conteggi, senza scrivere nel dataset.
- [x] Con `--ordinary-rebuild`, chiamare `rebuild_faces()` soltanto dopo `theta_reached`, altrimenti registrare `not_run_nonterminal`. Passare copie delle facce terminali e dei record Arianna: lo stack viene consumato. Registrare budget, successo/topologia/colorazione oppure motivo d'arresto; non fornire al ricostruttore i colori dell'oracolo. In `test_ordinary_rebuild_is_separate`, verificare che l'opzione non alteri certificati o replay esatto e non invochi il ricostruttore su un prefisso non terminale.
- [x] Rieseguire l'intero file di test: PASS. Controllare il replay in un processo nuovo e confrontare anche il multinsieme degli archi, non solo V/E. Documentare la CLI effettiva in `docs/development.md` e aggiornare il piano.

**Esito Task 4:** criterio raggiunto sulle piccole mappe. API di catena,
replay e persistenza implementate; theta a zero passi, limiti e rifiuti
espliciti. Il runner legge solo la riga scelta e registra SHA-256 della
sorgente, revisione Git, hash del codice locale e configurazione. Directory
popolate, salvataggi incompleti e mismatch della sorgente sono rifiutati.
La ricostruzione ordinaria riceve soltanto copie strutturali e Arianna e
non viene eseguita su prefissi non terminali.

Baseline verificata 216 PASS; RED per le API mancanti; GREEN finale
201 test dedicati e 299 complessivi, smoke S1 PASS. Su dodecaedro piccolo:
20→2 vertici, 30→3 archi, 12→3 facce in nove passi (F5=1, F4=6, F3=2),
nove scambi parziali, ritorno esatto e ordinario con topologia/colorazione
validi. Prefisso di due passi: `step_limit`, replay esatto e
`not_run_nonterminal`. Entrambi riletti in processi nuovi.

Artefatti da conservare sotto `ct/debug/oracle-study/`:
`task4-dodecahedron-001/` e `task4-dodecahedron-prefix-001/`; rigenerazione
dai comandi nel resoconto, con nuove directory. Piccolo input versionabile
in `ct/examples/planar/oracle-study-dodecahedron.colored.planar`.
Nessuna riga della raccolta grande letta. Revisione indipendente: nessun
rilievo, più 96 catene con variazioni dell'embedding esatte dopo JSON.
Il test dell'arresto per nessuna candidata è sintetico: non costituisce
un controesempio reale. Prestazioni sulle mappe grandi e completezza
universale restano aperte. Nessun commit né integrazione del branch.

## Task 5: prima catena sulla mappa da circa 8.000 facce

**Files:** creare il resoconto step-3; aggiornare il presente piano. Salvare
gli artefatti grandi in una nuova sottodirectory di `ct/debug/oracle-study/`.

**Interfaces:** usa esclusivamente la CLI implementata e verificata nella
Task 4. Prefisso e replay eseguiti; i comandi completi qui sotto restano
**non eseguiti**, rinviati su indicazione dell'autore dopo le misure.
La profilazione usa la medesima CLI con percorso assoluto del runner.

- [x] Eseguire prima una prova di 20 passi sulla riga 1, con output nuovo. Atteso: `step_limit` oppure un arresto motivato, non `theta_reached`. Controllare invarianti, tipi incontrati, memoria, tempo per passo e replay del prefisso. Un test del prefisso non certifica il ramo completo.
- [ ] Dopo la prova breve, eseguire la catena completa con budget 10.000. Per la prima mappa osservata nel passo 1, V=16.064 e F=8.034, quindi si attendono 8.031 riduzioni se il percorso raggiunge theta. Derivare comunque il valore dai conteggi effettivi, non codificarlo nel motore.

```bash
# Da ct/, dopo Task 4; scegliere output non ancora esistente.
uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py \
  --input maps_3000_maps_of_8000_faces.colored.planar \
  --map-number 1 --max-steps 10000 \
  --output debug/oracle-study/map-001-run-001 \
  --ordinary-rebuild --kempe-search-limit 10000
uv run --python ../.venv/bin/python python experiments/oracle_reduction_run.py \
  --replay debug/oracle-study/map-001-run-001
```

- [x] Se si raggiunge theta, verificare il ritorno esatto in un nuovo processo usando la riga sorgente identificata dal manifest. Registrare separatamente il risultato ordinario, senza richiedere uguaglianza dei suoi colori. Se ci si arresta, salvare stato, candidata/motivo, ultimo certificato valido e istruzioni di riproduzione; non passare automaticamente ad altre 150 mappe.
- [x] Eseguire `uv run --python ../.venv/bin/python python -m pytest tests -q` e `uv run --python ../.venv/bin/python python 4ct.py -s1 -r2 10`. Atteso: test PASS e smoke completato con grafo ben colorato. Riportare i risultati realmente ottenuti, non quelli della sessione precedente.
- [x] Scrivere step-3: configurazione e impronte, riduzioni per tipo, numero di scambi completi/parziali, lunghezze dei cammini, profondità, esito esatto e ordinario, tempo/memoria, casi aperti. Aggiornare questo piano con il prossimo passo concreto e spiegare all'autore cosa è stato stabilito e cosa no.

**Esito diagnostico Task 5 (28 settembre 2026):** prefisso a 20 passi
`step_limit`, V/E/F 16.064/24.096/8.034 → 16.024/24.036/8.014; 10 F4 e 10 F5,
20 scambi parziali, zero completi. Cammini: totale 1.607 archi, mediana 4,
massimo 1.519. Tutti gli invarianti applicati dal motore passano; replay
interno e in processo nuovo esatti, inclusi sorgente e archi keyed/colorati.
Ordinario `not_run_nonterminal`, correttamente non eseguito.

Sola catena 199,8268 s (9,9913 s/passo), CLI con replay/salvataggio 301,68 s;
replay separato 92,32 s, picco RSS 235,06 MiB. Nel profilo di un solo passo
sulla medesima riga, 15 costruzioni di `FaceIndex` occupano 35,906 dei
44,124 s profilati (81,4%); `_insert_ordered` introduce visite quadratiche
nei bucket per taglia durante ogni ricostruzione. Il profilo non va usato
come tempo reale senza overhead. La proiezione a costo costante della sola
riduzione è 22,29 ore, non una previsione garantita del ramo completo.

L'autore ha chiesto di isolare e documentare prima questo ostacolo:
**catena completa a budget 10.000 e confronto ordinario restano aperti**.
La checkbox sui salvataggi/replay è soddisfatta dal caso diagnostico: stato
alla profondità 20, ultimo certificato e motivo `step_limit` conservati;
nessuna candidata matematica bloccante è stata trovata. Nessun automatismo
sulle altre mappe. Il traguardo sperimentale non è dichiarato completato.

Artefatti: `ct/debug/oracle-study/task5-map-001-20260928-n_j6eb82/`, con
`prefix-20/`, log del replay, `profile-one-step-absolute/`, pstats e copie
prima delle modifiche. Comandi realmente eseguiti, impronte e distinzione
fra `sysctl` negato, errore software di provenienza con cProfile relativo,
arresto per budget e impossibilità matematica nel
[resoconto step-3](../../llm-vs-4ct/4ct-oracle-study-step-3.md).

Verifiche fresche: 299 test PASS (inclusi i 201 dell'oracolo), smoke S1 PASS
con 16 vertici/24 archi e sette riduzioni. Nessun codice o test modificato;
file di debug fissi preservati. Piano e resoconti aggiornati, nessun commit.
Prossimo passo: piano mirato alle prestazioni dell'indice mantenendo
identità, ordine, atomicità e invarianti; nuova misura del medesimo prefisso
prima di riprendere la corsa completa. Non avviare R1–R5.

**Aggiornamento successivo, approvato dall'autore:** costruzione lineare
implementata in `FaceIndex.rebuild()`, senza cambiare il resto del motore.
Due regressioni di costo prima FAIL, poi nove test dell'indice PASS e 308
complessivi PASS; smoke S1 PASS. Lo stesso prefisso e il replay separato
sono stati rieseguiti: catena 59,1538 s (3,38×), CLI 86,06 s (3,51×), replay
21,16 s (4,36×). Picchi RSS CLI/replay: 275,73/228,06 MiB. `steps.jsonl` e
`terminal.json` identici byte per byte alla prova precedente. Nessun assert
rimosso; F4=10, F5=10, esatto e `not_run_nonterminal` invariati.
Artefatti nuovi in `ct/debug/oracle-study/task5-linear-index-wt4mbk55/`.

Il precedente prossimo passo sulla costruzione dell'indice è concluso.
La catena completa resta aperta: il costo iniziale residuo è circa 3 s/passo;
la proiezione a costo costante di 6,60 ore è ancora non verificata. Non
avviare automaticamente la catena lunga né altre mappe. Prima di estendere
l'ottimizzazione, profilare brevemente il codice aggiornato e progettare
l'eventuale intervento su copie/controlli con verifiche dedicate.

**Ulteriore aggiornamento, continuazione autorizzata:** il profilo di un
passo attribuisce 3,260/9,390 s (34,7%) a dieci controlli ponti NetworkX.
Nuovo predicato iterativo low-link in `oracle_reduction.py`, impiegato nei
due punti già esistenti senza togliere controlli: 0,943 s nel nuovo profilo,
7,131 s totali. Tredici test nuovi RED→GREEN, inclusa enumerazione di 729
piccoli multigrafi contro cancellazione effettiva degli archi; 214 dedicati,
321 complessivi e smoke S1 PASS. Revisione indipendente di indice e ponti
conclusa senza rilievi; risolta la precedente pendenza del revisore.

Nuovo prefisso sulla sola riga 1: **51,8083 s** di catena (−12,42% rispetto
all'indice lineare, 3,86× rispetto all'inizio), CLI 76,36 s, replay separato
17,41 s; picchi RSS CLI/replay 254,53/209,88 MiB. Replay esatto e file di
certificati/terminale identici a entrambe le prove precedenti. `step_limit`
e `not_run_nonterminal` restano arresto non conclusivo e confronto non
eseguito, senza errore software né conclusione di impossibilità matematica.
Artefatti: `ct/debug/oracle-study/task5-residual-2pk826jb/`.

Prossimo passo aggiornato: progettare il riuso delle verifiche e degli indici
di stati immutati, con invalidazione esplicita e stessa atomicità, prima di
modificare copie o controlli. Gli invarianti globali occupano ancora circa
il 60% del profilo breve. La proiezione a costo costante scende a 5,78 ore
per la riduzione, resta non verificata. Catena completa, ordinario e altre
mappe non avviati. Il precedente prossimo passo di profilazione e intervento
circoscritto è concluso; non avviare R1–R5.

**Aggiornamento: riuso delle verifiche richiesto dall'autore.** Aggiunta una
sola istantanea privata per stato, confrontata prima di ogni riuso su tutti
gli input del checker, inclusi gli indici derivati e i tipi dei contatori.
Una differenza invalida l'evidenza; nuovi stati partono senza cache,
`_install()` trasferisce soltanto l'evidenza degli stessi oggetti verificati.
Il checker completo è preservato (AST identico salvo nome) e forzabile con
`assert_state_invariants(state, force=True)`. Nessun fingerprint/schema,
controllo dei certificati o copia atomica modificato.

33 nuovi test: mutazioni dirette, riuso, invalidazione, precondizioni
obsolete, atomicità, apply/undo/copy/load e fallback. RED 7 FAIL/24 PASS;
suite finale **354 PASS**, smoke S1 PASS, revisione indipendente approvata.
Profilo di un passo: nove richieste, cinque verifiche complete e quattro
riusi; istantanee 0,534 s, totale profilato **7,131→5,612 s**. Prefisso:
catena **36,1301 s**, CLI **52,15 s**, replay separato **13,01 s**; esatto
e byte-identico a tutte le prove precedenti, invarianti forzati sul terminale
ricaricato PASS. Artefatti nuovi:
`ct/debug/oracle-study/task5-validation-reuse-cxeaekbk/`.

Regressione misurata della memoria: picco CLI **470,08 MiB**, replay
**363,34 MiB** (prima 254,53/209,88). Istantanea terminale 4,64 MiB;
replay diagnostico separato: al massimo tre stati vivi e 13,94 MiB di
istantanee ai punti osservati, nessuno stato/cache vivo alla fine. Il
maggiore picco RSS resta da attribuire completamente, non va descritto
come solo costo dell'istantanea. Nessuna raccolta forzata in produzione.

Il riuso è completato. Prossimo approfondimento: allocazioni temporanee e
picco RSS, mantenendo stessa riga e riferimento completo. Proiezione a
costo costante **4,03 ore**, non durata verificata. Il traguardo della
catena completa e l'ordinario restano aperti; `step_limit` è non conclusivo,
non un errore o un'impossibilità matematica. Nessun avvio di altre mappe.

**Aggiornamento: diagnosi del maggiore RSS.** Solo replay dei 20 passi
salvati, senza codice di produzione modificato. Confronto checker completo
vs cache: picchi 203,17/361,97 MiB; byte piccoli Python in uso circa 98,6 MiB
e tre grafi vivi ai checkpoint in entrambi. Gli snapshot unici vivi della
cache sono circa 9,29 MiB costanti, non una cronologia crescente.

Con diagnostica nativa, al passo 20 `vmmap` localizza 170,4 MiB residenti in
`MALLOC_LARGE (empty)`. La variante solo sperimentale che comprime senza
perdita il risultato di `_invariant_snapshot()` porta tale categoria a
20,0 MiB, il picco RSS **368,33→213,75 MiB**, gli snapshot vivi **9,29→2,24 MiB**.
Replays esatti; tempi strumentati 13,058/13,078 s. La differenza di circa
150,4 MiB nelle regioni vuote spiega gran parte dei circa 154,36 MiB di
differenza nel RSS corrente al passo 20. Revisione indipendente delle
evidenze senza rilievi bloccanti o errori materiali.

Quaranta snapshot sullo stato fisso e serializzazioni con dimensione fissa
o leggermente crescente non riproducono da soli l'aumento: l'effetto è
associato al ciclo dei grandi buffer nel flusso del replay e alle altre
allocazioni. GC finale elimina i grafi osservati, ma non il RSS residuo;
la richiesta nativa di rilascio memoria libera zero byte in queste prove.
Nessuna policy GC/native API aggiunta al motore. Nessuna conclusione sul
dettaglio interno di libmalloc o oltre i 20 passi.

Artefatti e script versionati nella nuova directory ignorata
`ct/debug/oracle-study/task5-memory-diagnosis-55sjo0d_/`.
Diagnosi completata; **compressione ancora solo nel diagnostico**. Il
prossimo passo è implementarla con test di riuso/invalidazione e riferimento
completo, poi suite/smoke, prefisso forward di 20 passi e replay separato.
Catena completa e confronto ordinario rimangono aperti e non avviati.

**Aggiornamento 29 settembre 2026: compressione integrata, scope limitato dall'autore.**

- [x] TDD sulla rappresentazione compressa completa: theta con archi paralleli, tre identità di faccia distinte, payload atteso indipendente e limite deterministico dei byte conservati. RED 1 FAIL/33 PASS; GREEN 248 mirati PASS.
- [x] Comprimere con `zlib.compress(marshal.dumps(payload, 2), 1)`; nessun altro cambiamento al motore. AST di tutte le altre funzioni, incluso checker completo e ciclo di vita della cache, invariato rispetto alle copie precedenti.
- [x] Suite **355 PASS in 1,17 s** e smoke S1 exit 0, sette riduzioni, ricostruzione valida di 16 vertici/24 archi; debug preesistente ripristinato e verificato tramite hash.
- [x] Solo prefisso forward di 20 passi della riga 1 e replay in processo nuovo: esatti; certificati/terminale identici alle quattro prove precedenti, stessi conteggi/scambi, terminale ricaricato verificato con `force=True`.
- [x] Confronto tempi/RSS e documentazione di comandi effettivi, limiti e conservazione in `ct/debug/oracle-study/task5-compressed-snapshot-31zqnha5/`.

Catena **36,130→34,575 s**, CLI **52,15→50,15 s**, replay **13,01→12,92 s**;
picchi RSS CLI **470,08→397,66 MiB**, replay **363,34→214,25 MiB**.
Il buffer terminale scende da 4.863.570 a 1.167.447 byte (circa −76%).
La riduzione del picco del replay è forte; quella della CLI è parziale e
non riporta il picco al valore precedente al riuso (254,53 MiB). Non
attribuire automaticamente la differenza residua alle stesse regioni native:
questa esecuzione non le ha rimisurate. Nessun allentamento degli invarianti.

Intervento e revisione indipendente finale conclusi senza rilievi.
Il revisore ha letto delta ed evidenze senza ripetere test o esperimenti.
La Task 5 resta aperta: `step_limit` non certifica theta né impossibilità;
ordinario `not_run_nonterminal`. Il prossimo approfondimento riguarda il
picco residuo della CLI sullo stesso prefisso; nessuna estensione automatica
alla catena lunga o alle altre mappe. Dettagli nell'
[aggiornamento del resoconto](../../llm-vs-4ct/4ct-oracle-study-step-3.md#aggiornamento-compressione-lossless-integrata).

**Aggiornamento 29 settembre 2026: diagnosi delle fasi della CLI.**

- [x] Osservare riduzione/replay interno/salvataggio sulla sola riga 1, 20 passi, senza modificare produzione o test. Picchi rispettivamente 247,31/398,30/398,30 MiB.
- [x] Correlare RSS con byte vivi e statistiche native: nel replay le regioni vuote residenti salgono a 162,0 MiB; gli snapshot restano circa 2,23 MiB, senza accumulo di stati/grafi.
- [x] Confronto diagnostico con checker completo nel solo replay: picco 257,78 MiB, regioni vuote al passo 20 19,7 MiB, stessi certificati e terminale. Tutti gli invarianti restano verificati.
- [x] Registrare comandi, versioni degli script, hash e limiti in `ct/debug/oracle-study/task5-cli-memory-phases-ww6kj7bo/` e aggiornare il resoconto. Nessuna nuova suite eseguita, codice invariato.

Il prossimo intervento riguarda la validazione nel replay interno, non il
salvataggio. Non è ancora adottata una politica diversa di cache, GC o
allocazione; il checker completo è soltanto il controllo diagnostico.
L'origine precisa di ogni allocazione e la generalizzazione oltre 20 passi
restano fuori dalle conclusioni. Revisione indipendente conclusa senza
rilievi, in sola lettura e senza ripetere test o esperimenti.

**Aggiornamento 29 settembre 2026: buffer delle istantanee.**

- [x] Isolare payload/marshal/zlib/liberazione con due diagnosi circoscritte alla riga 1, 20 passi; controllo per componenti esatto. Documentare aumento della memoria dell'andata e riduzione del picco complessivo.
- [x] TDD: regressione sull'encoder reale e flusso tipizzato atteso indipendente; RED 1 FAIL/34 PASS, poi 2 FAIL/33 PASS. Modifica minima di `_invariant_snapshot`, GREEN 249 mirati PASS.
- [x] Suite 356 PASS, smoke S1 PASS con ripristino artefatti; nessun cambiamento al checker/cache lifecycle.
- [x] CLI di produzione: 20 passi, RSS 311,75 MiB, 54,49 s; replay in nuovo processo: 219,38 MiB, 13,80 s. Certificati/terminale identici ai cinque prefissi precedenti, payload precedente ricostruito esattamente e invarianti forzati PASS.
- [x] Aggiornare architettura, sviluppo, resoconto, comandi e ledger nella nuova directory `task5-snapshot-buffers-hk5diq7u`; revisione indipendente conclusa senza rilievi; Task 5/catena completa rimangono aperte.

**Criterio di uscita del traguardo:** catena completa con replay esatto
documentato, oppure ostacolo riproducibile isolato. Nel secondo caso il
traguardo di catena completa resta **aperto**; è completata soltanto
l'indagine diagnostica. Nessuno dei due esiti è una prova del 4CT.

## Roadmap dopo questo traguardo

Queste fasi non vanno eseguite in blocco né considerate già progettate nel
dettaglio. Al termine della Task 5, scegliere la prima applicabile e scrivere
un piano esecutivo dedicato usando i risultati effettivi.

| Fase | Domanda | Esperimento e criterio di uscita |
| --- | --- | --- |
| R1 — Estendere il campione | Il motore copre altri stati intermedi? | Dopo la prima riuscita, 3 mappe ulteriori, poi le 151; tutti gli esiti espliciti, fixture per ogni nuovo caso, nessuna ri-validazione massiva degli input. |
| R2 — Alternative e rami | Quanto dipende il risultato dalla scelta? | Enumerare candidate in stati selezionati, confrontare continuazioni con budget fissati e poi introdurre backtracking limitato. Distinguere passo certificato, ramo completato, ricerca non conclusiva. |
| R3 — Dataset strutturale | Quali dati senza colori distinguono le scelte? | Registrare `map_id`, `state_id`, `candidate_id`, profondità; in `structure` vicinati, gradi, distanze e cicli; in `oracle` colori, testimoni, esiti e costi. Testare l'invarianza delle feature rispetto a permutazioni dei colori. |
| R4 — Regole interpretabili | Esistono condizioni sufficienti semplici? | Fissare uno split per mappa prima della selezione delle regole; contare firme, cercare controesempi e solo se utile piccoli alberi decisionali. Separare previsione empirica da garanzia. |
| R5 — Lemma | Si può eliminare l'ipotesi della colorazione nota? | Enunciato preciso, ipotesi puramente strutturali, casi coperti, argomento di esistenza di una continuazione e base theta; cercare controesempi. Se la prova resta dipendente dall'oracolo, il problema originario resta aperto. |

## Protocollo fra sessioni

1. Leggere questo piano, la specifica, l'ultimo resoconto e `AGENTS.md`;
   leggere i documenti canonici pertinenti prima delle modifiche.
2. Controllare branch e diff senza eliminare modifiche; non ricreare il branch
   e non ripetere automaticamente il conteggio del passo 1.
3. Riprendere la prima checkbox aperta tenendo conto delle dipendenze e dei
   casi di ricerca ancora irrisolti. La modalità suggerita è esecuzione
   inline con `superpowers:executing-plans`, usata per la Task 1 su richiesta
   dell'autore. Rispettare sempre l'eventuale ambito più ristretto della
   nuova richiesta: non avviare automaticamente tutte le fasi.
4. Prima di ciascuna Task spiegare cosa si vuole verificare; dopo, comunicare
   esito, evidenza e conseguenza per il passo successivo. Usare TDD per le
   modifiche e verifiche fresche prima di dichiararle riuscite.
5. Prima di terminare aggiornare data, checkbox, risultati, comandi realmente
   eseguiti, percorsi degli artefatti e prima azione successiva. Un fallimento
   motivato è un risultato utile, ma non rende completa una funzionalità.
6. Prima di riprendere in un altro checkout o dispositivo, conservare anche
   i file non tracciati. I certificati in `ct/debug/` non viaggiano con Git:
   il resoconto deve indicare quali mantenere e come rigenerarli.

### Prompt da usare in una nuova chat

> Continuiamo lo studio dell'oracolo 4CT. Leggi
> `docs/superpowers/plans/2026-09-28-oracle-reduction-study.md` e la specifica
> collegata, poi riprendi la prima attività non completata. Usa Superpowers
> con esecuzione inline e spiegami i risultati fra un passo e il successivo.
> Conserva le modifiche locali. Le 151 mappe originali sono già validate:
> verifica le nuove trasformazioni, senza rifare quella validazione.
> Aggiorna il piano e il resoconto prima di terminare la sessione.

### Registro di continuità

| Data | Completato / evidenza | Primo passo successivo |
| --- | --- | --- |
| 2026-09-27 | Passo 1: conteggio F5 e nove trasformazioni, resoconto e JSON collegati sopra. | Studiare F2/F3/F4. |
| 2026-09-28 | Specifica e piano persistenti; nessuna nuova trasformazione implementata in questa fase di pianificazione. | Revisione del piano, poi Task 1. |
| 2026-09-28 | Task 1 completata: resoconto step-2, otto fixture e 30 andate/ritorni; 45 test dedicati e 143 complessivi PASS. Nessuna modifica al motore o al dataset. | Task 2: stato keyed e certificati reversibili. |
| 2026-09-28 | Task 2 completata: stato keyed, certificati reversibili, controlli atomici e revisione; 72 test dedicati e 170 complessivi PASS. | Task 3: scoperta automatica dei passi. |
| 2026-09-28 | Task 3 completata: `plan_step()` F2–F5, 36 riduzioni automatiche, regressioni keyed e rifiuti read-only; 118 test dedicati, 216 complessivi e smoke S1 PASS. | Task 4: catena su piccole mappe e replay, poi JSON. |
| 2026-09-28 | Task 4 completata: catena/replay/JSON/CLI, dodecaedro in nove passi e prefisso non conclusivo; 201 test dedicati, 299 complessivi, smoke e revisione PASS. | Task 5: 20 passi sulla sola riga 1, misurazione e replay prima della corsa completa. |
| 2026-09-28 | Task 5, diagnosi: prefisso riga 1 di 20 passi e replay esatto; 199,83 s di catena, replay 92,32 s / 235,06 MiB; costo FaceIndex isolato, 299 test e smoke PASS. Autore richiede diagnosi prima della corsa lunga. | Progettare ottimizzazione mirata dell’indice; catena completa e ordinario ancora aperti sulla stessa riga. |
| 2026-09-28 | Follow-up Task 5: costruzione lineare approvata e implementata; 9 test nuovi, 308 totali e smoke PASS. Prefisso 199,83→59,15 s, replay 92,32→21,16 s; certificati/terminale identici. | Profilare brevemente i costi residui prima di ulteriori ottimizzazioni o della corsa completa. |
| 2026-09-28 | Follow-up Task 5: profilato e ottimizzato il controllo ponti; 13 test nuovi, 321 totali, smoke e revisione delle due ottimizzazioni PASS. Prefisso 59,15→51,81 s, replay 21,16→17,41 s; certificati/terminale identici. | Progettare riuso di verifiche/indici con invalidazione esplicita; catena completa e ordinario ancora aperti, nessun avvio automatico. |
| 2026-09-28 | Follow-up Task 5: riuso verifiche implementato su richiesta, 33 test nuovi, 354 totali, smoke e revisione PASS. Prefisso 51,81→36,13 s, replay 17,41→13,01 s; file identici. Picchi RSS saliti a 470,08/363,34 MiB. | Isolare allocazioni temporanee e maggiore picco RSS sulla stessa riga; catena completa e ordinario ancora aperti. |
| 2026-09-28 | Follow-up Task 5: RSS diagnosticato in regioni native vuote ma residenti; variante lossless solo diagnostica porta replay strumentato da 368,33 a 213,75 MiB, esatto. Nessun codice di produzione modificato. | Implementazione lossless separata con TDD e nuovo prefisso forward/replay; nessuna corsa lunga automatica. |
| 2026-09-29 | Follow-up Task 5: compressione lossless integrata con TDD, 355 test e smoke PASS; 20 passi e replay esatti, certificati/terminale identici. Catena 34,575 s; picchi RSS CLI/replay 397,66/214,25 MiB. | Attribuire il picco residuo della CLI sul medesimo prefisso prima di estendere la corsa; catena completa ancora aperta. |
| 2026-09-29 | Follow-up Task 5: picco CLI localizzato nel replay interno, 398,30 MiB con 162,0 MiB nativi vuoti; controllo senza cache nel solo replay 257,78 MiB / 19,7 MiB, certificati esatti. Produzione/test invariati. | Progettare intervento mirato alla validazione del replay, con TDD e trade-off tempo/memoria; catena completa ancora aperta. |
| 2026-09-29 | Follow-up Task 5: serializzazione per componenti integrata con TDD; 356 test e smoke PASS, certificati/replay esatti. RSS CLI 397,66→311,75 MiB; tempo 50,15→54,49 s; replay separato 214,25→219,38 MiB. | Intervento circoscritto verificato; ulteriori limiti ai buffer o estensione del prefisso richiedono un passo distinto. Catena completa ancora aperta. |

| 2026-09-29 | Diagnosi picco: unica nuova andata100 e replay interno esatto, tutti100 certificati/terminale identici; vecchio 390,92 MiB non riprodotto, nuovo massimo321,078 MiB già nell’andata. Checkpoint50 +16KiB RSS, nessun nuovo picco; produzione/test invariati. | Cercare riproducibilità con osservatore precedente e soli confini inversione/checkpoint, previa nuova autorizzazione≤100; nessuna ottimizzazione o estensione automatica. |
