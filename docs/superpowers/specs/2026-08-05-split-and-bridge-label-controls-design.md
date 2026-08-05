# Split & Bridge V2 — controlli tipografici e layout pannelli

## Obiettivo

Migliorare la regolazione visiva del grafo in `split_and_bridge_v2.html` senza alterare la trasformazione Split & Bridge o la fisica del grafo.

## Interfaccia

La sezione **Aspetto** del pannello **Parametri** conterrà due nuovi campi numerici indipendenti:

- **Dimensione caratteri nodi**, valore predefinito `11` px;
- **Dimensione caratteri archi**, valore predefinito `9` px.

Ogni campo aggiornerà immediatamente le rispettive etichette Cytoscape e avrà il pulsante di ripristino già usato dagli altri parametri. I valori minimi saranno rispettivamente `8` px per i nodi e `7` px per gli archi, così le etichette non potranno diventare accidentalmente illeggibili.

Il pannello **Trasformazione** sarà ancorato in alto a sinistra, a `1rem` dai bordi della workspace. Il drawer **Parametri** resterà ancorato a destra. La larghezza adattiva già presente sarà conservata per evitare fuoriuscite sugli schermi stretti.

## Stato e aggiornamento

I valori `nodeLabelFontSize` ed `edgeLabelFontSize` entreranno in `DEFAULT_CONFIG` e `config`. Le definizioni dei controlli useranno lo stesso percorso dichiarativo degli altri parametri, comprese validazione, sincronizzazione iniziale e ripristino.

Due funzioni dedicate applicheranno le dimensioni allo stile Cytoscape di nodi e archi. Saranno richiamate sia durante l'inizializzazione del renderer sia dopo la sincronizzazione completa del grafo, così il valore scelto sopravvive a trasformazioni e ricostruzioni degli elementi.

## Compatibilità e gestione errori

I campi accetteranno solo valori numerici entro il minimo dichiarato. Valori non validi saranno normalizzati dal meccanismo esistente dei controlli di configurazione. Se Cytoscape non è ancora inizializzato, il valore resterà nella configurazione e verrà applicato alla successiva inizializzazione.

## Verifica

I test automatici copriranno:

- presenza e valori predefiniti dei due controlli;
- aggiornamento indipendente delle etichette di nodi e archi;
- ripristino ai valori predefiniti;
- persistenza delle dimensioni dopo la sincronizzazione del grafo;
- posizionamento del pannello Trasformazione sul lato sinistro;
- regressione dell'intera suite esistente e validità sintattica dello JavaScript incorporato.

## Fuori ambito

Non cambiano colori, font, visibilità predefinita delle etichette, dimensione di nodi e archi, comportamento del drawer Parametri o logica Split & Bridge.
