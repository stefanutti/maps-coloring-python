# Contesto per Codex/Work — progetto `maps-coloring-python`

Sto lavorando a un approccio sperimentale al teorema dei quattro colori usando la formulazione in termini di grafi planari cubici e Tait 3-edge-coloring.

Il punto di partenza sono mappe/grafi cubici planari in cui **tutte le facce hanno grado almeno 5**: quindi inizialmente non ci sono F2, F3 o F4. Possono esserci F5, F6, F7, F8 e anche facce molto grandi. Per Eulero vale

$$
\sum_k (6-k)F_k=12,
$$

quindi, quando non esistono F2/F3/F4,

$$
F_5=12+\sum_{k\ge7}(k-6)F_k.
$$

L'idea è ridurre la mappa fino al **grafo $\theta$**. Quando non ci sono F2/F3/F4, si sceglie un pentagono F5 e una delle sue possibili riduzioni/escavazioni. Questa operazione può generare localmente F2, F3 o F4, che poi possono essere eliminate con riduzioni semplici. Si continua così fino a $\theta$, memorizzando l'intero stack/albero delle riduzioni.

Poi si ricostruisce il grafo in ordine inverso. Durante la ricostruzione si usa la Tait 3-edge-coloring e, quando necessario, si fanno **Kempe switches** sulle componenti bicolori. Se una sequenza di riduzioni conduce a un punto in cui la ricostruzione non può proseguire, quella scelta può essere considerata un ramo sbagliato e si può esplorare un'altra scelta precedente.

L'obiettivo teorico che mi interessa è soprattutto questo:

$$
\boxed{\text{dimostrare che esiste sempre almeno un ramo di riduzione fino a }\theta\text{ che sia completamente ricostruibile}}
$$

Non mi interessa necessariamente trovare subito la strategia ottima o più efficiente: mi basta inizialmente una dimostrazione di **esistenza**.

Per studiare il problema sto preparando circa **2.000 mappe da circa 7.000 facce ciascuna**, già correttamente colorate con una **Tait 3-edge-coloring**. Queste colorazioni serviranno come **oracolo**.

Voglio modificare il programma in modo che, durante la riduzione, per ogni stato e per ogni F5/riduzione candidata vengano registrate due classi separate di informazioni:

1. **informazioni oracle/cromatiche**, cioè tutto ciò che deriva dalla Tait coloring nota;
2. **informazioni strutturali color-blind**, cioè proprietà ricavabili dal solo grafo non colorato.

Per ogni candidato vorrei registrare almeno:

- identificatore della mappa;
- stato corrente della riduzione;
- F5 scelto;
- quale delle possibili riduzioni del pentagono viene applicata;
- firma locale del pentagono, a partire almeno dai gradi delle 5 facce adiacenti;
- eventualmente primo, secondo e successivi anelli di vicinato;
- distanze da altri F5;
- cicli corti, simmetrie e altre proprietà strutturali locali;
- pattern cromatico locale dato dalla Tait coloring;
- se la riduzione porta o meno a una sequenza completamente ricostruibile;
- numero di Kempe switches richiesti;
- profondità raggiunta;
- eventuale punto di fallimento;
- backtracking necessario;
- qualunque altra caratteristica utile a distinguere i rami buoni da quelli cattivi.

L'esperimento deve mantenere rigorosamente separate la vista **oracle** e quella **color-blind**, perché lo scopo finale è:

$$
\text{oracle cromatico}
\rightarrow
\text{scoperta di pattern}
\rightarrow
\text{regola puramente strutturale}
\rightarrow
\text{possibile lemma/dimostrazione}.
$$

Vorrei iniziare con analisi semplici e interpretabili, non con machine learning complesso. Prima cerchiamo regole discrete, invarianti, classi di configurazioni, firme locali, alberi decisionali leggibili e possibili condizioni sufficienti. Solo successivamente, se serve, potremo usare tecniche più sofisticate.

Importante: se faremo train/test o analisi statistiche, **la separazione deve avvenire per mappa intera**, mai dividendo stati della stessa mappa tra train e test.

Ora esamina il repository `maps-coloring-python` e aiutami prima di tutto a capire:

- come è rappresentata attualmente una mappa;
- come sono rappresentate facce, edge, colori e adiacenze;
- quali riduzioni F2/F3/F4/F5 esistono già;
- come viene gestita la Tait coloring;
- come viene implementata la ricostruzione;
- se esistono già Kempe switches e backtracking;
- dove conviene aggiungere il logging dell'albero delle riduzioni e il dataset sperimentale.

**Non modificare ancora l'algoritmo matematico alla cieca.** Prima fai una ricognizione del codice e proponi un piano concreto delle modifiche, indicando file, classi e funzioni coinvolte. Poi procediamo per passi piccoli e verificabili.
