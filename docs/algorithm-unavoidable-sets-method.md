# S5: insiemi inevitabili, ricostruzione e programma di dimostrazione

Questo documento spiega l'idea matematica di S5 e propone un programma di
ricerca per dimostrarne la correttezza e il successo. Si riferisce al codice
introdotto il 23 settembre 2026 in [4ct.py](../ct/4ct.py) e
[ct_graph_utils.py](../ct/ct_graph_utils.py).

La descrizione operativa canonica rimane in [algorithm.md](algorithm.md).
Le basi teoriche sono in [v17](llm-vs-4ct/4ct-v17.md), soprattutto §§6, 8,
9.4, 9.17–9.18 e 10. I risultati sperimentali sono raccolti separatamente in
[s5-waterworld.md](s5-waterworld.md).

**S5 combina una scelta geometrica delle riduzioni con una ricerca
deterministica delle ricolorazioni.** I sette tipi inevitabili indicano dove
cercare; il criterio di mezzo ciclo decide quando una ricostruzione può
essere eseguita. Il collegamento che garantirebbe sempre il successo fra
queste due parti non è ancora dimostrato.

## 1. Modello e idea generale

Si considera una mappa sferica connessa, cubica, senza loop e senza ponti.
Gli archi paralleli sono ammessi, in particolare negli intermedi. L'assenza
di ponti è una precondizione matematica: non va confusa con la sola verifica
iniziale di planarità, cubicità e assenza di loop effettuata dalla CLI.

Una colorazione di Tait assegna tre colori agli archi, con tre colori
distinti a ogni vertice. Per l'equivalenza di Tait, questa è la formulazione
del problema dei quattro colori usata dal programma.

La riduzione elimina un arco e sopprime i suoi due estremi, rimasti di
grado due. Le due facce ai lati dell'arco si fondono; le altre facce
incidenti agli estremi perdono lati. Il filo di Arianna registra come
invertire l'operazione. Si arriva al grafo theta: due vertici collegati da
tre archi paralleli, immediatamente colorabile.

La ricostruzione percorre il filo in ordine inverso. Ogni passo suddivide
archi esistenti e reinserisce l'arco eliminato. La difficoltà è assegnare i
colori mantenendo una colorazione propria.

```text
curvatura positiva → scelta deterministica di una riduzione ammissibile
                                      ↓
                         pila di Arianna → grafo theta
                                      ↓
                ricostruzione: estensione diretta quando possibile
                                      ↓
                altrimenti ricerca di scambi completi di Kempe
                                      ↓
                         mezzo scambio e reinserimento
```

L'intuizione della selezione è creare facce piccole nelle vicinanze della
zona appena modificata, così da favorire una successione di passi semplici.
È una motivazione geometrica dell'euristica, non un teorema sulla futura
colorazione.

## 2. Perché i sette tipi sono inevitabili

Per una mappa cubica sferica valgono

$$
V-E+F=2,\qquad 3V=2E,\qquad \sum_f |f|=2E.
$$

Da queste identità segue la legge delle dodici unità di curvatura:

$$
\sum_f(6-|f|)=12.
$$

Distribuendo la carica delle facce sui vertici si ottiene, per un vertice
incidente a facce di taglia $a,b,c$,

$$
\kappa(v)=\frac6a+\frac6b+\frac6c-3,
\qquad \sum_v\kappa(v)=6F-3V=12.
$$

Supponiamo che tutte le facce abbiano almeno cinque lati e ordiniamo
$5\le a\le b\le c$. Un vertice positivo soddisfa

$$
\frac1a+\frac1b+\frac1c>\frac12.
$$

Se $a\ge6$ la disuguaglianza è impossibile, dunque $a=5$. Se $b\ge7$,
la somma è al massimo $1/5+2/7<1/2$. Restano due possibilità:

- $b=5$: serve $c<10$, dunque $c=5,6,7,8,9$;
- $b=6$: serve $c<15/2$, dunque $c=6,7$.

Questo produce esattamente i sette tipi della sezione 6 di v17:

| Facce incidenti | Carica del vertice |
| --- | ---: |
| $(5,5,5)$ | $3/5$ |
| $(5,5,6)$ | $2/5$ |
| $(5,5,7)$ | $9/35$ |
| $(5,6,6)$ | $1/5$ |
| $(5,5,8)$ | $3/20$ |
| $(5,5,9)$ | $1/15$ |
| $(5,6,7)$ | $2/35$ |

La somma delle cariche è positiva, quindi almeno uno di questi tipi deve
comparire. La tabella è ordinata per carica decrescente, come nel codice.

L'insieme completo delle alternative geometriche è pertanto:

> Esiste una faccia di taglia 2, 3 o 4, oppure, se tutte le facce hanno
> almeno cinque lati, esiste uno dei sette tipi positivi.

Questa affermazione non dice ancora che uno degli archi proposti dal tipo
positivo superi il controllo dei ponti, né che la sua ricostruzione riesca
dalla colorazione che verrà effettivamente prodotta.

## 3. Come S5 usa questa informazione

### 3.1 Riduzioni piccole

S5 prova prima F2, poi F3, poi F4. All'interno di una taglia ordina gli archi
per grandezza decrescente della faccia adiacente e accetta la prima candidata
che supera il controllo dei ponti. I pareggi seguono l'ordine delle facce e
degli archi. Anche la scelta su F2 è deterministica.

F2, F3 e F4 hanno gestori di ricostruzione specifici. Per una dimostrazione
completa vanno giustificati anche questi gestori, comprese le degenerazioni
con archi paralleli e facce che si incontrano più volte.

### 3.2 Riduzioni pentagonali

Quando le fasi precedenti non hanno trovato una candidata, S5 classifica i
vertici dell'embedding corrente. Per ogni pentagono $f$ e arco $e$ sul suo
bordo, con faccia opposta $g$, considera nell'ordine:

1. se $f$ contiene un vertice di uno dei sette tipi positivi;
2. se $f$ tocca la regione attiva, la *wave*;
3. quante incidenze laterali degli estremi di $e$ appartengono a pentagoni;
4. la grandezza di $g$;
5. la carica del miglior vertice positivo contenuto in $f$.

Le priorità sono lessicografiche: una faccia positiva globale precede una
faccia non positiva locale. A parità dei primi criteri si preferiscono
più incidenze laterali pentagonali, una faccia opposta più grande e una
carica maggiore. Solo dopo l'ordinamento si prova la validità delle
riduzioni. Se nessuna candidata positiva funziona, si provano le altre F5.

Nel caso usuale di due facce laterali distinte, ciascun pentagono laterale
perde un lato e diventa F4. Questa è la ragione per favorire tali archi.
Il contatore del codice conta però **incidenze agli estremi**, non facce
distinte: se la stessa faccia laterale compare due volte, può perdere due
lati. Una prova deve trattare separatamente questo caso.

La positività riguarda un vertice contenuto in $f$: il codice non richiede
che l'arco scelto passi per quel vertice. Inoltre non elimina insieme le
tre facce del tipo positivo. Non si può quindi applicare direttamente un
ipotetico lemma su una precisa riduzione di una patch di tre facce senza
dimostrare che descriva proprio l'operazione eseguita.

### 3.3 Significato e limiti della wave

La wave memorizza vertici interessati dalle riduzioni. Una riduzione F5 la
avvia o la estende; le riduzioni piccole la estendono se è già attiva.
Una scelta F5 globale fuori dalla wave attiva provoca il suo azzeramento.

Si cerca così di continuare a lavorare nella stessa regione. Tuttavia la
wave non è, per definizione, un disco topologico né il bordo di un unico
oceano. S5 non conserva l'oceano fisso della costruzione costiera di v17.
Qualsiasi uso dei lemmi costieri deve prima ricostruirne e verificarne le
ipotesi sul passo considerato.

## 4. Perché servono ancora gli scambi di Kempe

In una colorazione propria di un grafo cubico, gli archi di due colori
formano cicli alternati disgiunti. Scambiare quei colori su un ciclo
completo conserva la colorazione propria: ogni suo vertice continua a
vedere una volta ciascuno dei tre colori.

Per ricostruire un F5 si devono suddividere due archi, indicati con $p,q$,
e collegare i nuovi vertici. Una coppia di colori è *ammissibile* se
contiene i colori di entrambi gli archi. Se questi colori sono diversi,
la coppia è obbligata; se sono uguali, ci sono due coppie possibili.

Il criterio di v17 §8.2, CONDITION-1, è:

> Gli archi $p,q$ appartengono allo stesso ciclo di Kempe di una coppia
> ammissibile.

Tagliando quel ciclo nei punti di suddivisione e scambiando i colori su uno
dei due tratti, si ottengono i colori necessari agli estremi. Il nuovo arco
riceve il terzo colore. Questo giustifica il **mezzo scambio**.

Se CONDITION-1 non vale, S5 cerca una sequenza di scambi completi che la
renda vera. La scelta è deterministica e include cicli lontani dalla
finestra di reinserimento. Il numero di scambi necessari non è fissato a
priori, salvo il limite imposto alla ricerca.

I cicli lontani sono essenziali nel modello: possono lasciare invariati i
colori della finestra ma cambiare quali archi appartengono allo stesso
ciclo. Per questo la ricerca conserva l'intera colorazione, con chiavi
distinte per gli archi paralleli. Una parola come `ABAC` non identifica
uno stato sufficiente per decidere quali riparazioni saranno possibili
dopo altri scambi; v17 §§9.14–9.18 discute precisamente questo problema.

## 5. La ricerca vista come un problema matematico finito

Sia $H$ un intermedio colorato e sia $r$ il record di Arianna da invertire.
Si consideri il grafo finito delle colorazioni $\mathcal K(H)$:

- un vertice è una colorazione propria degli archi, con nomi dei colori e
  identità degli archi fissati;
- due vertici sono adiacenti quando differiscono per uno scambio completo
  su un ciclo bicolore.

Gli scambi sono involuzioni, quindi le componenti connesse di
$\mathcal K(H)$ sono le classi di equivalenza di Kempe. Indichiamo con
$\mathcal C_H(\varphi)$ la classe della colorazione corrente $\varphi$ e
con $\mathcal A_r(H)$ le colorazioni che soddisfano CONDITION-1 per il
reinserimento registrato da $r$. In presenza di archi paralleli occorre
esplicitare le occorrenze ammesse degli archi da suddividere, coerentemente
con l'embedding e il record.

Il problema cercato da S5 è esattamente

$$
\mathcal C_H(\varphi)\cap\mathcal A_r(H)\ne\varnothing.
\tag{R-S5}
$$

Questa formulazione separa due domande:

| Domanda | Significato |
| --- | --- |
| La ricerca trova ogni stato raggiungibile, se ha risorse sufficienti? | Proprietà dell'esplorazione di un grafo finito. |
| Nella componente esplorata esiste uno stato accettabile? | Proprietà matematica del grafo, della riduzione e della colorazione. |

La prima non implica la seconda.

### 5.1 Completezza relativa della ricerca

**Proposizione sul modello della ricerca.** Se il budget non esclude stati,
la ricerca termina e trova una riparazione se e solo se vale (R-S5).

*Argomento.* Se $m=|E(H)|$, ci sono al massimo $3^m$ assegnazioni di colori,
quindi un numero finito di colorazioni proprie. Ogni nuovo stato è
memorizzato una sola volta. Le espansioni sui cicli che toccano gli archi
marcati e quelle sugli altri cicli, insieme, comprendono tutti gli scambi
ammessi. L'alternanza delle code permette di processare entrambe le fasi;
a esaurimento delle code, tutti gli stati della componente raggiungibile
sono stati visitati. Gli stati accettabili vengono riconosciuti con il
test di ciclo comune. I predecessori ricostruiscono una sequenza valida. ∎

Il codice alterna gruppi di al massimo otto espansioni locali con
espansioni remote. Ordina i cicli remoti per distanza topologica dagli
archi marcati e poi per lunghezza decrescente; dà precedenza ai nuovi stati
prodotti da queste espansioni. Sono priorità di esplorazione, senza una
dimostrazione di ottimalità. Per trasformare la proposizione sul modello
in una prova del programma va verificata la corrispondenza di ogni ciclo,
stato e predecessore con la rappresentazione Python.

La ricerca corrente usa un budget finito, di default 10.000 colorazioni
distinte memorizzate. Un numero massimo di scambi lungo una soluzione
**non basta** a giustificare questo limite: prima della soluzione, l'ordine
di esplorazione può memorizzare molti altri stati.

## 6. Che cosa significa «dimostrare S5»

È utile distinguere quattro obiettivi.

| Obiettivo | Obbligo di prova |
| --- | --- |
| Correttezza dell'output riuscito | Riduzioni invertibili, scambi validi, topologia conservata e colorazione propria finale. |
| Terminazione con esito o errore | Ogni riduzione accettata diminuisce il numero di facce; ogni ricerca è finita. |
| Successo universale con ricerca sufficientemente ampia | Esistenza delle riduzioni e validità di (R-S5) per tutti gli stati effettivamente prodotti. |
| Successo universale del programma con budget 10.000 | Anche un limite dimostrato sugli stati memorizzati prima di ogni successo, per l'ordine implementato. |

I primi due obiettivi non includono la garanzia di colorare ogni input:
un programma che termina segnalando un impasse può soddisfarli.

### 6.1 Obblighi strutturali

Occorre dimostrare che, su ogni intermedio ammissibile con più di tre facce:

1. esiste almeno una candidata fra quelle effettivamente scandite da S5;
2. una candidata accettata mantiene connessione, planarità, cubicità,
   assenza di loop e assenza di ponti;
3. il record di Arianna permette di invertire esattamente l'operazione;
4. il numero di facce diminuisce di uno e quello dei vertici di due.

La diminuzione dà una misura di terminazione della riduzione. Da sola non
prova che la prossima candidata esista. Analogamente, Euler garantisce
facce piccole, ma occorre un lemma ulteriore sull'ammissibilità dei loro
archi. Va anche giustificato che il controllo dei ponti sulla faccia fusa
sia sufficiente, nel contesto degli invarianti, comprese le eccezioni F2.

L'Extension Theorem di v17 garantisce una possibile escavazione costiera
sotto le proprie ipotesi. Non è automaticamente un lemma di esistenza per
la scansione F2–F5 e per le priorità specifiche di S5.

### 6.2 L'obbligo cromatico centrale

Per la strategia attuale, l'obiettivo preciso è:

> Per ogni input ammissibile, ogni record F5 e ogni colorazione intermedia
> che la ricostruzione S5 raggiunge prima di quel record, vale (R-S5).

Questo è un obiettivo da dimostrare o confutare, non un risultato acquisito.
La colorazione corrente dipende anche dalle scelte dei passi precedenti.
Provare che ciascun reinserimento riesca da *qualche* colorazione, presa
separatamente, non garantisce una successione compatibile di reinserimenti.

Una versione più forte, spesso più semplice da enunciare, richiederebbe
(R-S5) per **ogni** colorazione propria di ogni intermedio e per ogni
riduzione che S5 può scegliere. Se fosse vera, risolverebbe il problema
della compatibilità. Potrebbe però essere falsa anche se S5 funziona
sempre: una classe ostile potrebbe non essere mai raggiunta dal programma.

### 6.3 Perché R₅ di v17 non basta per questa implementazione

R₅ riguarda l'esistenza di una scelta riuscita fra cinque cancellazioni
di un pentagono e le colorazioni dei rispettivi intermedi, nella classe
specificata da v17. S5 fissa invece una cancellazione con la sua euristica
e parte da una colorazione già determinata dalla ricostruzione.

Il passaggio logico mancante è fra

$$
\exists\,\text{cancellazione}\;\exists\,\text{colorazione riparabile}
$$

e la riparabilità della **cancellazione scelta**, nella **classe di Kempe
raggiunta**. La ricerca attuale non cambia la cancellazione, non torna
indietro nella pila e non salta in un'altra classe di Kempe.

Anche usando il teorema dei quattro colori già noto, l'esistenza di una
colorazione della mappa originale non dimostra questo passaggio. Per una
nuova dimostrazione indipendente del teorema non si potrebbe inoltre usare
il teorema stesso per giustificare il passo di estensione.

### 6.4 Schema di un teorema condizionale

Supponiamo dimostrati gli obblighi strutturali, la correttezza e riuscita
dei gestori F2/F3/F4, e (R-S5) per ogni stato F5 effettivamente raggiunto.
Supponiamo inoltre che nessuna ricerca venga troncata dal budget.

Allora S5 ricostruisce una colorazione di Tait dell'input: la riduzione
raggiunge theta per diminuzione del numero di facce; theta ha una
colorazione propria; per induzione sulla pila, i gestori piccoli o la
ricerca completa seguita dal mezzo scambio producono una colorazione
propria dell'intermedio successivo. L'invertibilità dei record identifica
l'ultimo grafo con l'input.

Questo schema individua dove concentrare la ricerca: **la dimostrazione
di (R-S5), con le ipotesi esatte dell'algoritmo**. Il limite operativo
richiede una giustificazione quantitativa aggiuntiva.

## 7. Direzioni concrete per una dimostrazione

### A. Cercare un invariante delle colorazioni prodotte da S5

È la direzione più aderente all'implementazione. Invece di tentare subito
un teorema su tutte le colorazioni possibili, si può cercare una proprietà
$I(H,\varphi,\mathcal R)$, dove $\mathcal R$ è la pila dei reinserimenti
ancora da eseguire.

La proprietà dovrebbe valere su theta, essere conservata dai gestori
F2/F3/F4 e dalle riparazioni F5 effettivamente scelte, e implicare (R-S5)
per il prossimo record. Includere la pila permette di esprimere vincoli
fra reinserimenti consecutivi, che una proprietà del solo grafo ignora.

Possibili ingredienti da studiare sono le connessioni delle regioni
bicolori dietro gli archi marcati e le connessioni lungo separatori piccoli.
Sono candidati per la ricerca, non invarianti già verificati. La sola
frontier di S5 non contiene queste informazioni cromatiche.

### B. Risolvere i nuclei R2 tramite separatori e cicli remoti

V17 §9.4 riduce la difficoltà del gap 2 a un nucleo con parola `ABAC`,
archi estremi su cicli distinti della coppia forzata e un ulteriore
collegamento bicolore che blocca la riparazione immediata.

Le sezioni 9.17–9.18 suggeriscono due sottoproblemi: un separatore
monocromatico fra i cicli marcati, oppure una catena di incidenze fra cicli
remoti. Nel primo caso si può studiare quando i collegamenti sui due lati
del taglio consentano la riparazione; nel secondo serve controllare come
uno scambio modifica la catena utilizzata.

Prima di applicare questi risultati a S5 bisogna verificare le ipotesi
costiere e di connettività per i suoi intermedi. Le escavazioni non
preservano automaticamente la classe $C$ di v17, e le sue ipotesi sui
controesempi minimi non valgono per ogni mappa incontrata dal programma.

Una prova di progresso potrebbe usare una quantità ben fondata che
diminuisce lungo **scambi appositamente scelti**. Non può diminuire lungo
ogni scambio, perché ciascuno è reversibile. Inoltre la normale distanza
nel grafo d'incidenza fra i cicli estremi vale già due in ogni nucleo R2
di v17 §9.16: non fornisce la diminuzione cercata. Neppure la distanza
topologica usata nel codice è attualmente una funzione di progresso
dimostrata.

### C. Raffinare i sette tipi in configurazioni realmente riducibili

Il tipo $(5,5,7)$ specifica tre taglie, ma lascia molta libertà nelle
adiacenze, nelle connessioni esterne e nelle classi di colorazione.
Un programma alternativo consiste nell'arricchire i tipi con una patch
precisa, un bordo marcato e una riduzione specifica.

Servirebbero due risultati distinti: un catalogo inevitabile di tali patch
e una procedura di estensione valida per le condizioni esterne ammesse
da ciascuna riduzione. È la distinzione metodologica fra inevitabilità e
riducibilità presente nella
[dimostrazione RSST](https://thomas.math.gatech.edu/FC/fourcolor.html).
Le sette triple da sole non sono quel catalogo.

In classe $C$, v17 §6 dà un bordo di lunghezza fra 9 e 13 per l'unione
delle tre facce a un vertice positivo. Ciò suggerisce verifiche finite
delle condizioni al bordo. Il limite sul bordo non basta però: occorre
provare che la patch sia un disco e che le informazioni conservate
descrivano tutte le estensioni o tutte le transizioni utilizzate. Le
partizioni dei soli terminali in una coppia di colori non sono in generale
chiuse rispetto agli scambi successivi, come mostra v17 §9.15.

Una dimostrazione con un nuovo catalogo potrebbe richiedere una selezione
e record di ricostruzione diversi. Sarebbe una variante certificata del
metodo, non automaticamente una prova della S5 attuale.

### D. Rendere la scelta della riduzione parte della ricerca

Se si riesce a dimostrare soltanto un risultato esistenziale come R₅,
una variante può esplorare cancellazioni alternative e colorazioni di
intermedi diversi. Questo avvicina le scelte dell'algoritmo ai
quantificatori del teorema.

Bisognerebbe comunque provare che la ricerca copra le alternative
necessarie, che produca almeno una delle colorazioni utili e che le
scelte siano compatibili con i passi successivi. Cambiare solo arco,
ripetendo sempre una colorazione sfavorevole, non è sufficiente. S5 oggi
non implementa questa ricerca con ritorno sulle riduzioni precedenti.

## 8. Esperimenti utili per scegliere la congettura giusta

Il prossimo passo consigliato è studiare **classi complete di Kempe su
mappe piccole**, oltre a eseguire altre mappe grandi.

Per ogni piccolo intermedio e reinserimento marcato si possono enumerare
indipendentemente le colorazioni di Tait, costruire le classi sotto gli
scambi completi e marcare le colorazioni in $\mathcal A_r(H)$. Si confronta
poi la classe effettivamente prodotta da S5 con le altre classi.

Questo esperimento distingue casi logicamente diversi:

| Esito | Conseguenza |
| --- | --- |
| La ricerca finisce il budget | Informazione sulle risorse e sull'ordine di esplorazione; non prova l'ostilità. |
| Una classe completa non interseca $\mathcal A_r(H)$ | Confuta la riparabilità universale per quella coppia intermedio/reinserimento. |
| S5 raggiunge proprio quella classe | Fornisce un controesempio al successo della S5 attuale, anche aumentando il budget. |
| Una cancellazione o classe diversa riesce | Motiva una ricerca sulle riduzioni o un diverso invariante. |

L'oracolo di enumerazione dovrebbe essere indipendente dal cercatore di
produzione; ogni certificato trovato va riprodotto controllando i colori
a ogni passo. Per ogni caso difficile conviene conservare embedding,
record marcato, colorazione completa, chiavi degli archi, classe o budget
esplorato e sequenza di scambi. Va variato anche l'ordine di presentazione
e l'etichettatura: le priorità deterministiche del codice dipendono da
questi dati e non sono una canonicalizzazione del grafo.

La letteratura sull'equivalenza di Kempe offre famiglie di confronto:
belcastro e Haas dimostrano, per esempio, l'unicità della classe per grafi
cubici planari bipartiti 2-connessi. È una proprietà di una famiglia
specifica e non va estesa agli intermedi generali di S5. Anche in una
classe unica rimane da dimostrare che $\mathcal A_r(H)$ non sia vuoto per
il reinserimento scelto. Si veda il
[lavoro degli autori](https://arxiv.org/abs/1209.1730).

I test Waterworld già eseguiti verificano dieci istanze con zero scambi
casuali. In quelle esecuzioni 2.195 reinserimenti F5 hanno richiesto ricerca:
la selezione da sola non li ha resi direttamente reinseribili. Il massimo
di 61 stati esaminati osservato è un dato del campione, non un limite
matematico per tutte le mappe. I dettagli restano nel
[rapporto sperimentale](s5-waterworld.md).

## 9. Primo obiettivo di ricerca proposto

Conviene partire da questo enunciato, restringendolo inizialmente a una
famiglia di intermedi definita con precisione:

> Ogni colorazione che S5 produce nella famiglia scelta è in una classe
> di Kempe contenente una colorazione che soddisfa CONDITION-1 per il
> prossimo reinserimento F5 scelto da S5.

Prima si cercano controesempi piccoli con enumerazione completa. Se non
emergono, si tenta un invariante della colorazione e della pila, oppure
un lemma di riparazione basato sui separatori di v17. In parallelo si
formalizzano riduzioni e gestori piccoli. Soltanto dopo una prova di
raggiungibilità si affronta un limite quantitativo sul costo della ricerca.

Questo percorso separa tre risultati diversi: una procedura che elimina
la casualità, una procedura che riesce sempre e una procedura che riesce
sempre entro un limite di risorse dimostrato.
