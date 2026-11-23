# Più wave successive e raccordi cromatici — piano di studio futuro

2 ottobre 2026, Europe/Rome. **Stato: DIFFERITO / NON ESEGUITO.** È preparazione di uno studio, non un piano già autorizzato di implementazione.

## Idea generale: colorare durante la riduzione e avanzare per wave

L'idea da approfondire è affiancare alla riduzione del grafo originale una costruzione progressiva della sua colorazione. Mentre il grafo viene semplificato verso theta, si vorrebbe iniziare a colorare la regione coinvolta nelle scelte di riduzione e ampliarla a ogni passo, usando ciò che è già stato costruito per orientare le scelte successive. È una proposta di ricerca: non è il comportamento implementato nell'esperimento R1 in corso.

Quando si sceglie un arco uv, la regione da considerare comprende le facce incidenti ai suoi due vertici, insieme alle porzioni di mappa coinvolte nei passi precedenti. L'unione dei loro bordi individua il grafo parziale sul quale studiare la colorazione. Il grafo ridotto corrente, che perde vertici e archi, va distinto da questa regione cumulativa, che può crescere sul grafo originale. Le riduzioni fondono facce e sopprimono vertici: occorre quindi definire come mettere in corrispondenza archi, facce e colori fra i due oggetti. Questa corrispondenza resta un compito di F0, non un'assunzione già risolta.

La **wave** è il fronte attivo di questa crescita. Si cerca un arco su una faccia vicina alla regione già raggiunta, così che il nuovo passo estenda una costruzione cromatica coerente. La località suggerisce dove cercare; da sola non certifica che la riduzione sia ammissibile o che la colorazione parziale possa essere completata. Nell'idea proposta, wave di selezione e regione colorata devono essere collegate da una regola esplicita. La frontier già presente in S4 è un riferimento per la località, ma non realizza automaticamente questa nuova costruzione.

La scelta dell'arco potrebbe dipendere soprattutto dalle **connessioni bicolori** che si formano, più che dal nome di un colore su una F5. In un grafo cubico completamente colorato secondo Tait, ogni coppia rosso-verde, rosso-blu o verde-blu forma cicli alternati. Nella regione parziale, una connessione può invece presentarsi come un cammino con estremi sulla frontiera, dove mancano ancora archi della regione da costruire. Lo studio dovrà stabilire quali collegamenti degli estremi e quali trasformazioni permettano di proseguire mantenendo compatibilità con una colorazione completa.

«Non rompere i loop» non significa imporre che tutti i cicli rimangano identici. Riduzioni e scambi possono separarli o ricongiungerli mantenendo una colorazione di Tait valida. L'obiettivo da precisare è conservare i vincoli cromatici necessari alla prosecuzione, dichiarando quali trasformazioni sono ammesse. Una regione localmente ben colorata non è, per questo solo fatto, garantita estendibile all'intera mappa.

Una wave può esaurire le candidate locali: vicino alla frontiera potrebbero rimanere soltanto facce F6 o maggiori, mentre altre facce piccole si trovano lontano. La direzione preferita è allora ammettere **più wave successive**: conservare la regione già colorata, iniziare una nuova crescita altrove e definire il raccordo quando le regioni si incontrano. Resta da distinguere se conservare significhi mantenere immutati tutti i colori assegnati oppure permettere scambi certificati che mantengano valida la regione; il piano confronta esplicitamente queste due politiche.

Il percorso da verificare è quindi: scegliere una candidata ammissibile vicino alla wave, ampliare e colorare la regione coinvolta, aggiornare le connessioni bicolori della frontiera e, in caso di stallo locale, avviare una nuova wave con regole di raccordo dichiarate. Il punto decisivo è capire se questi dati possano guidare una scelta senza consultare una colorazione completa già nota, e se le scelte mantengano la possibilità di arrivare fino a theta. Al momento non sono dimostrate né la sufficienza dei dati di frontiera né l'esistenza di una prosecuzione per ogni caso.

Le fasi F0–F4 che seguono organizzano questo studio futuro; non autorizzano esperimenti o modifiche al lavoro attualmente in corso.

> Per chi riprenderà: Superpowers inline con revisione finale separata dello stesso autore, senza subagent. Prima di qualunque esecuzione chiedere l'autorizzazione alla specifica fase e ai suoi budget. La preparazione di questo documento non autorizza motore, prototipo, test o modifica di produzione.

**Obiettivo:** verificare se più wave successive possano costruire una colorazione di Tait mantenendo le regioni precedenti e raccordandole quando una frontiera locale non offre più candidate F2–F5 ammissibili.

**Architettura dello studio:** definire prima regioni/frontiere e politiche di conservazione; chiarirle con casi minimi; usare l'oracolo come riferimento separato; infine valutare una regola operativa sui soli dati disponibili alla costruzione. Una singola wave continua resta un termine di confronto, non una premessa.

**Strumenti eventuali:** documentazione e file già persistiti; solo con successiva autorizzazione, piccoli casi Python/NetworkX in un'arena separata, da ct via uv offline e bytecode disabilitato, cache/tmp dedicati. Nessuna modifica prevista a 4ct.py, FaceIndex, cache, dataset, certificati o selettori di produzione.

**Spec:** [nota e orientamento dell'utente](/Users/mario.stefanutti/mario/programming/github-stefanutti/maps-coloring-python/ct/debug/oracle-study/r1-rss-fix-part24-20261001-20261001-8774-1s2n8w4/note-wave-kempe-loops-to-verify-20261001.md). Questa specifica è una domanda di ricerca: non certifica estendibilità, sufficienza delle interfacce o esistenza di una scelta fino a theta.

## Vincoli globali e priorità

- Prima continuare/chiudere il lavoro R1 dell'oracolo. Avviare questo studio soltanto su nuova richiesta esplicita; nessuna automazione o attività in background.
- Non trasferire autorizzazioni, tentativi o budget R1. Non fare retry, riproduzione o replay per ottenere dati mancanti.
- Usare solo dati completi e identificati; un prefisso osservato senza stato salvato non è una fixture ricostruibile. Segnare NOT_AVAILABLE/NOT_ISOLATED.
- Nuovi artefatti sperimentali in una futura arena diretta sotto ct/debug/oracle-study, scelta e inventariata alla sua autorizzazione. Gli output nominati sotto sono relativi a quell'arena, non a produzione/docs.
- Preservare input, stato Git, arene e STOP precedenti; freeze delle fonti e conservazione prima/dopo ogni fase autorizzata. Nessun checkout/reset/stash/cleanup/commit.
- Nessun risultato su un campione implica una prova generale4CT. Un fallimento di una scelta parziale non dimostra che il grafo non sia colorabile.
- La garanzia globale riguarda una faccia di taglia<6. F5 è garantita quando F2/F3/F4 sono assenti globalmente; nessuna garanzia automatica vicino alla wave.

## Focus della revisione

1. Frontiera locale priva di F2–F5, con facce piccole lontane: distinguere stallo locale, ripartenza globale e assenza globale di candidate ammissibili.
2. Due regioni valide separatamente ma incompatibili al raccordo: non equiparare correttezza locale ed estendibilità.
3. Stesso aspetto della frontiera con connessioni bicolori diverse: non usare il solo bordo visibile come certificato completo.
4. Ciclo di Kempe che attraversa più regioni o zone lontane: nessuna modifica implicita delle regioni precedenti.
5. Uso nascosto dei colori completi dell'oracolo, perdita degli ID dopo riduzioni o dati mancanti: non dichiarare una regola costruttiva sulla base di informazioni indisponibili.

## F0 — Definizioni e chiarimento della frontiera

**Output:** definitions.md e boundary-examples.md. **Consuma:** nota e documentazione locale. **Produce:** un modello preciso e esempi controllabili, senza motore.

- [ ] Definire separatamente il grafo originale G0 e il ridotto Gt. Confrontare il modello iniziale su G0 fisso con il trasporto di regioni attraverso i certificati di Gt; non confonderli.
- [ ] Definire la regione cumulativa R dei lati colorati e la wave attiva W. Un vertice interno ha tutti i lati incidenti inclusi; uno di frontiera ha lati inclusi ed esclusi. Per una coppia di colori, gli estremi aperti sono i vertici con grado1 nel relativo sottografo della regione.
- [ ] Disegnare il ciclo rosso-verde A–B–C–D–A e la restrizione ai lati A–B/B–C: il ciclo completo è chiuso, la restrizione è un cammino. Spiegare come gli archi esterni possono chiuderlo, senza presentare questa restrizione come esempio completo di algoritmo wave.
- [ ] Definire i dati di frontiera: vertice/occorrenza dell'arco, colori assegnati/mancanti, coppia bicolore, connessioni degli estremi interne alla regione. Tenere separata la continuazione esterna conosciuta dall'oracolo.
- [ ] Formalizzare due politiche da confrontare: P0, colori già assegnati immutabili; P1, regione mai cancellata ma eventuali scambi certificati ammessi e registrati. P1 non è già approvata: richiede precisare le trasformazioni e l'assenso alla fase futura.
- [ ] Specificare "vicino" con adiacenza fra facce che condividono un arco, distinguendola dall'incidenza a un vertice. Distinguere faccia piccola presente da candidata realmente ammissibile.

**Gate:** un lettore deve poter ricostruire regione, frontiera e significato di conservazione senza interrogare una colorazione completa. Se il trasporto G0/Gt resta indefinito, non implementare la selezione multiwave.

## F1 — Raccordi fra regioni e casi minimi

**Output:** junction-cases.md e case-matrix.json. **Consuma:** definizioni F0. **Produce:** criteri candidati con esempi positivi/negativi e limiti espliciti.

- [ ] Separare validità locale della colorazione, compatibilità fra regioni ed esistenza di un'estensione completa. Registrare quale proprietà ogni controllo dimostra.
- [ ] Preparare un esercizio su K4: colorazione completa con matchings R={AB,CD}, G={AD,BC}, B={AC,BD}; mostrare due regioni di un solo lato e il loro raccordo. Il ciclo rosso-verde A–B–C–D–A coincide con quello di F0. È un esempio didattico di colorazione parziale, non di una wave completa.
- [ ] Studiare il caso con AB rosso e CD verde fissati: ogni regione è localmente valida, ma il raccordo completo su K4 è incompatibile. Verificarne l'argomento e, solo se autorizzato, l'enumerazione; non classificarlo come controesempio alla proposta wave prima che questa sia definita.
- [ ] Classificare tre eventi: estensione locale, stallo locale con nuova wave, ricongiungimento di wave. Per ciascuno dichiarare quali assegnazioni possono cambiare e quale verifica serve.
- [ ] Definire gli scambi ammessi in P1 e aggiornare tutte le informazioni di frontiera coinvolte. La sola esistenza di cicli bicolori su un risultato cubico colorato non è un criterio discriminante.
- [ ] Cercare esempi di frontiere apparentemente uguali con connessioni differenti, oppure dichiarare che il caso non è stato trovato. Non assumere sufficiente la firma di frontiera proposta.

**Gate:** ogni caso ha input/ID/colori, politica P0/P1, operazione e risultato atteso con giustificazione. Un caso negativo restringe il modello; non autorizza a cambiare silenziosamente la politica.

## F2 — Audit dei dati dell'oracolo disponibili

**Output:** oracle-case-audit.jsonl e unavailable-cases.md. **Consuma:** casi F1 e soli artefatti completi autorizzati. **Produce:** osservazioni riproducibili, separate dai dati che un algoritmo senza oracolo potrebbe usare.

- [ ] Inventariare manifest/source/code/config/SHA dei run completi disponibili. Iniziare con al massimo20 certificati di un solo run; elencare prima il criterio di scelta dei20, senza selezionare soltanto i casi favorevoli.
- [ ] Annotare per ciascun certificato famiglia, arco/faceID, scambi, distanza dalla regione attiva e appartenenza al ciclo complementare quando effettivamente ricostruibile.
- [ ] Classificare ogni campo come strutturale, disponibile dalla colorazione parziale o fornito soltanto dall'oracolo. I colori completi possono validare a posteriori, non guidare nascosti una regola dichiarata senza oracolo.
- [ ] Non dedurre rifiuti intermedi dai certificati accettati: run_chain non li conserva per i passi riusciti. Non ricostruire lo stato dai soli contatori del Terminale.
- [ ] Qualunque ricostruzione di stato, loader, replay o nuova sonda richiede autorizzazione e budget propri; la semplice preparazione di questo piano non li consente.

**Gate:** etichettare campi mancanti NOT_AVAILABLE e casi non isolati NOT_ISOLATED. Il main parte24 ora arrestato senza run non fornisce certificati da analizzare o un prefisso da riavviare.

## F3 — Esperimento minimo multiwave, soltanto se autorizzato

**Output:** experiment-protocol.md, proposed-budgets.json e, dopo eventuale esecuzione, multiwave-case-study.md. **Consuma:** F0–F2. **Produce:** valutazione circoscritta di una regola interamente definita.

- [ ] Specificare prima le regole deterministiche di scelta locale, esaurimento, ripartenza globale e raccordo, con tutti i dati accessibili dichiarati. Confrontare P0 e P1 soltanto se entrambe autorizzate.
- [ ] Separare baseline con colorazione completa nota, restrizione di quella colorazione a regioni e costruzione che non la consulta. Il successo della restrizione è automatico e non prova la costruzione.
- [ ] Proporre un primo campione di massimo4 casi con non più di8 vertici, compresi theta, K4 e almeno un raccordo incompatibile. I nomi/grafi/embedding e risultati attesi devono essere fissati nel protocollo prima del lancio.
- [ ] Definire un caso di stallo locale in zona F6+ con risorsa globale lontana. Se non è rappresentabile nel primo campione piccolo, proporre separatamente una fixture più grande con un altro budget; non estendere il campione automaticamente.
- [ ] Proporre limiti espliciti di wall/CPU/RSS/storage/diagnostica e conteggi per ricerca/esplorazione, inclusa finalizzazione, e richiederne approvazione. La sufficienza dei cap non è presunta; nessun trasferimento dei budget R1.
- [ ] Separare le verifiche di colori locali, embedding/cubicità/ponti del grafo completo corrente, raccordi e raggiungimento theta. Propria colorazione parziale non implica estendibilità.
- [ ] Primo STOP/errore o esaurimento del budget: conservare evidenze, niente retry e niente passaggio al caso successivo. Esplorazione troncata non equivale a enumerazione esaustiva.

**Gate:** protocollo e budget concreti revisionati, autorizzazione alla specifica esecuzione ricevuta; nessun prototipo o lancio nasce da questo piano da solo.

## F4 — Valutazione e chiusura scientifica

**Output:** study-report.md, study-final-review.txt e preservation.json. **Consuma:** tutti gli output autorizzati e i casi mancanti. **Produce:** conclusioni proporzionate all'evidenza e decisione sul passo successivo.

- [ ] Distinguere proprietà dimostrata, successo su casi finiti, controesempio a una regola particolare e questione aperta.
- [ ] Valutare separatamente stallo locale, ripartenza e raccordo; confrontare P0/P1 e annotare ogni modifica a regioni precedenti.
- [ ] Dichiarare esplicitamente se la scelta usa ancora l'oracolo. Nessun trasferimento a produzione senza nuova proposta, piano e autorizzazione.
- [ ] Revisione inline separata stesso autore, inventario finale e conservazione; nessuna estensione automatica alle151 mappe.

## Preparazione consegnata ora

Nota aggiornata e questo piano soltanto. Le fasi F0–F4 sono tutte non eseguite e non autorizzate. Non sono stati creati prototipi, fixture operative, comandi di lancio, budget sperimentali approvati o nuovi processi del motore. I futuri output e le proposte di budget sono deliberatamente da produrre nella relativa fase, prima della richiesta di esecuzione.

La priorità corrente resta R1. Il controllo di sola lettura del2 ottobre segnala main riga2 parte24 STOP_RESOURCE_OR_INTERRUPTION per cumulative clock/suspend inconsistency, ultimo contatore3284/8048, child_exit-15, process_group_resolvedtrue, preservation_oktrue, nessun run salvato. Questa osservazione non determina da sola se la causa sia sospensione o variazione dell'orologio; non autorizza retry/replay/ordinario.

Ruling Superpowers: writing-plans adattato a preparazione di ricerca futura, senza test/commit/implementazione o richiesta di avviare ora lo studio. La collocazione nell'arena corrente rispetta il freeze/inventario R1; non si modifica docs né il punto di ripresa.
