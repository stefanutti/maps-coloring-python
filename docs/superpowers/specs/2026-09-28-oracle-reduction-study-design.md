# Studio dell'oracolo: dalle riduzioni locali a un ramo certificato

Data: 28 settembre 2026. Specifica dello studio; include funzionalità future
e non costituisce una dimostrazione. Lo stato di avanzamento è nel piano
collegato, i contratti già implementati in [architettura](../../architecture.md#prototipo-sperimentale-delloracolo).

## Scopo e confini

L'obiettivo finale dell'autore è dimostrare l'esistenza di almeno un ramo di
riduzione fino a theta che sia completamente ricostruibile. La colorazione
nota serve a osservare e certificare trasformazioni, poi a cercare proprietà
riconoscibili senza colori. Non deve diventare un'ipotesi nascosta della
conclusione sul grafo non colorato.

Il prossimo traguardo è più piccolo: definire e provare sperimentalmente le
trasformazioni cromatiche F2/F3/F4/F5, concatenarle su una mappa e verificare
il ritorno esatto mediante un certificato. Un arresto deve produrre un caso
riproducibile, non l'affermazione che il ramo sia matematicamente impossibile.

Non rientrano in questo traguardo: una nuova strategia S6, il refactoring del
programma principale, l'albero completo delle riduzioni, l'addestramento di
modelli o una nuova verifica massiva del dataset originale.

## Fonti e risultati di partenza

- [Richiesta scientifica originale](../../llm-vs-4ct/4ct-reduction-of-already-colored-maps.md).
  La stima iniziale di 2.000 mappe da 7.000 facce è stata superata dalla scelta
  effettiva dell'autore: **151 mappe già verificate, di circa 8.000 facce**.
- [Passo 1 e suoi limiti](../../llm-vs-4ct/4ct-oracle-study-step-1.md), con
  [aggregati JSON](../../llm-vs-4ct/4ct-oracle-study-step-1-results.json).
- [Algoritmo](../../algorithm.md), [architettura](../../architecture.md),
  [sviluppo e comandi](../../development.md), oltre ad `AGENTS.md`.

Il passo 1 ha classificato 571.369 pentagoni iniziali e 2.856.845 candidate.
1.888.271 candidate soddisfano il criterio del ciclo bicolore complementare;
le altre 968.574 restano **non risolte da quel criterio**. Ogni F5 ha 1, 3 o 5
scelte compatibili. Nove trasformazioni campione hanno superato il ritorno
esatto. Questi risultati riguardano gli stati iniziali, non catene complete.

Il pentagono ha molteplicità cromatiche 2,2,1: il lato del colore unico
fornisce una trasformazione locale. I soli cinque gradi delle facce vicine
non determinano l'esito cromatico di tutte le candidate: nel primo pentagono
una stessa firma compare con due esiti diversi. Non è esclusa l'esistenza di
condizioni sufficienti o di firme strutturali più ricche.

`create_from_planar()` conserva già `graph.graph["oracle_faces"]`, ma solo
come fotografia iniziale. `reduce_faces()` non aggiorna quei colori e non
esegue backtracking fra rami. La ricerca Kempe di S5 esplora colorazioni,
non alberi di riduzione. Il prototipo `f5_oracle_probe.py` non gestisce ancora
in generale gli archi paralleli degli stati intermedi.

## Metodo scelto

Si prosegue con un esperimento separato in `ct/experiments/`. Prima si
documentano le regole locali e le ipotesi; poi si scrive un motore minimo
di passi reversibili, riusando le primitive esistenti quando hanno la
semantica necessaria. Non si estende alla cieca il prototipo F5 e non si
interpreta un gestore di ricostruzione come prova automatica del passo diretto.

Per F2 si studia l'eliminazione del digono e la fusione degli archi esterni:
non è la generica soppressione indipendente dei due estremi di un solo arco.
Per F3 si studia il cammino complementare sul triangolo. Per F4 si separano
i bordi a due colori dai bordi a tre colori e si identificano gli eventuali
scambi preliminari. Vanno esaminati anche vicini coincidenti, archi paralleli
e facce distinte aventi lo stesso elenco di coppie di vertici.

Se una famiglia non dispone ancora di una costruzione motivata e testata,
si registra `unsupported_case`, si salva un esempio piccolo e si aggiorna il
piano. Non si inventa una regola per poter avviare l'esperimento grande.

## Contratti del prossimo prototipo

Questi sono i contratti da realizzare nel piano collegato. La Task 2 introduce
stato, certificati e applicazione/inversione; ricerca automatica, catena e
salvataggio restano nelle Task 3–4. Le annotazioni devono funzionare con
Python 3.9 usando `typing` e dataclass.

### Stato e identificazione

`OracleState` contiene il grafo colorato, `g_faces` strutturale, `FaceIndex`,
identificatori stabili di facce e archi, e la corrispondenza fra ciascuna
occorrenza orientata nelle facce e l'arco del `MultiGraph`.

`g_faces` resta la fonte strutturale; gli identificatori sono metadati
sincronizzati, non un secondo embedding indipendente. Un arco parallelo non
è identificabile dalla sola coppia `(u, v)`. Un `edge_id` intero stabile deve
risolvere l'esatta chiave NetworkX; colori e chiavi assegnate automaticamente
non sono identificatori persistenti. La costruzione iniziale può abbinare
le due occorrenze tramite estremi e colore, data la colorazione propria
assunta. Gli ID restano invariati quando si scambiano i colori.

`Candidate(face_id: int, edge_id: int)` identifica una scelta nello stato
corrente. L'orientamento deriva dall'occorrenza nella faccia scelta.

### Passi e certificati

`plan_step(state: OracleState, candidate: Candidate) -> StepAttempt` non
muta lo stato. `StepAttempt` contiene `status`, `reason` e un `witness`
opzionale. Gli stati ammessi sono `certified`, `structurally_rejected`,
`no_witness`, `unsupported_case`; nessuno significa «ramo impossibile».

`StepWitness` conserva: candidata, tipo F2–F5, record Arianna compatibile,
patch strutturale prima/dopo con ID, archi eliminati e creati con colori,
sequenza ordinata di scambi con coppia di colori e ID degli archi percorsi,
contatori degli ID prima/dopo, e precondizioni per rilevare un certificato
applicato allo stato sbagliato.
Gli scambi preliminari completi e quello parziale non vanno confusi.

La prima implementazione F5 usa il solo criterio diretto del ciclo
complementare; se non vale restituisce `no_witness`, senza cercare altre
colorazioni. Eventuali scambi preliminari F4 appartengono alla costruzione
studiata nella Task 1, non a una ricerca generale e illimitata.

Aggiornamento Task 1 (28 settembre 2026): il
[resoconto F2/F3/F4](../../llm-vs-4ct/4ct-oracle-study-step-2.md) e le fixture
coprono F4 a tre colori e i due sottocasi esterni della F4 a due colori.
La costruzione può indicare un lato diverso da quello inizialmente provato:
`plan_step()` non dovrà cambiare di nascosto l'identità della candidata.
Se necessario dovrà lasciare al chiamante la prova dell'altro lato, senza
confondere `no_witness` per una candidata con assenza di scelte per la faccia.

`apply_step(state: OracleState, witness: StepWitness) -> None` e
`undo_step(state: OracleState, witness: StepWitness) -> None` aggiornano
insieme grafo, facce, metadati e indice. Un tentativo rifiutato o una
precondizione non soddisfatta non deve lasciare mutazioni parziali.

`assert_state_invariants(state: OracleState) -> None` controlla i risultati
prodotti: cubicità, tre colori incidenti distinti, assenza di loop e ponti,
corrispondenza delle occorrenze orientate con gli archi keyed, chiusura delle
facce, embedding planare coerente e `FaceIndex` aggiornato. Ogni riduzione
accettata perde due vertici, tre archi e una faccia. Un controllo di soli
conteggi non basta.

### Catena e riproducibilità

`run_chain(state: OracleState, max_steps: int) -> ChainResult` muta lo stato
e restituisce certificati ordinati, contatori e motivo di arresto:
`theta_reached`, `step_limit` oppure `no_certified_candidate`. Una violazione
di invariante è un errore fatale con diagnostica, non una candidata negativa.

Ordine di base deterministico: F2, F3, F4, F5; poi ID della faccia e dell'arco.
Nelle F5 provare prima il lato del colore unico, poi gli altri lati. Questa
preferenza è dichiaratamente **oracle**, non una strategia color-blind.
Provare le altre candidate disponibili dopo un esito non certificato; non
eseguire ancora scambi casuali o backtracking fra stati.

`replay_exact(terminal: OracleState, witnesses: Sequence[StepWitness]) -> OracleState`
lavora su una copia dello stato terminale e inverte i certificati. Conserva
i colori effettivi di theta, senza sostituirli con un'assegnazione arbitraria.
Il confronto finale comprende vertici, archi con molteplicità e colori,
occorrenze orientate e ID persistenti; non solo isomorfismo o dimensioni.

Le esecuzioni registrano versione dello schema, percorso del dataset, riga sorgente a base 1 e
SHA-256 di quella riga, configurazione, revisione Git e impronte dei file di
codice coinvolti, anche se non committati. Salvare certificati a differenze
e lo stato terminale; evitare una copia completa della mappa per ogni passo.
Per eventuali errori è sufficiente aggiungere uno snapshot diagnostico.

## Due risultati diversi da misurare

1. **Ritorno certificato esatto:** usa colori terminali e scambi registrati
   dall'oracolo e deve recuperare lo stato iniziale.
2. **Ricostruzione ordinaria:** usa una copia dello stack Arianna con
   `rebuild_faces()` e un budget Kempe esplicito. Deve essere misurata
   separatamente; può ottenere colori diversi, arrestarsi per budget oppure
   incontrare un caso non gestito. Non deve leggere i certificati cromatici.
   Si esegue soltanto se la catena ha raggiunto theta; altrimenti risulta
   `not_run_nonterminal`. Gli errori inattesi non diventano risultati negativi
   della ricerca matematica.

Il primo risultato non implica il secondo. Nessuno dei due, su un campione
di grafi già colorati, dimostra da solo l'esistenza universale richiesta.

## Vincoli globali

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

## Dopo il primo ramo

Solo dopo il ritorno esatto si amplia lo studio: poche altre mappe, poi il
campione completo; confronto fra alternative con budget e backtracking;
firme strutturali più ricche e regole interpretabili; infine enunciati e
tentativi di dimostrazione. Ogni fase avrà criteri di uscita ed esperimenti
propri. Una futura valutazione di predittori terrà fuori intere mappe prima
di scegliere le regole, senza contaminare il test con gli stati di training.

Piano operativo: [oracle-reduction-study](../plans/2026-09-28-oracle-reduction-study.md).
