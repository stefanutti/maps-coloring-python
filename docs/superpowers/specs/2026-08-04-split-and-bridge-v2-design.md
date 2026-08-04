# Split & Bridge V2 — Design

## Obiettivo

Creare `ct/web_split_and_bridge/split_and_bridge_v2.html` come restyling autonomo di `split_and_bridge.html`. La nuova versione deve rendere il grafo l'elemento dominante, migliorare la gerarchia dei comandi e preservare il comportamento esistente.

## Direzione visiva

Il design scelto combina il layout **Canvas immersivo** con il tema **Graphite caldo**:

- sfondo grafite profondo con texture puntinata discreta;
- superfici flottanti scure e leggermente traslucide;
- arancio caldo per l'azione primaria e gli archi selezionati;
- verde per i nodi e gli stati positivi;
- tipografia moderna, compatta e leggibile;
- bordi sottili, ombre morbide e animazioni brevi.

Il risultato deve sembrare uno strumento scientifico contemporaneo, non una dashboard generica.

## Struttura dell'interfaccia

### Header

Un header sottile contiene il marchio `4CT`, il titolo `Split & Bridge` e statistiche aggiornate del grafo. Non ospita i parametri e non deve sottrarre spazio significativo al canvas.

### Canvas

Il contenitore Cytoscape occupa tutto lo spazio residuo. Una griglia puntinata molto tenue dà profondità senza interferire con archi ed etichette. Il canvas continua a gestire trascinamento dei nodi, curvatura manuale degli archi, zoom, pan e selezione degli archi con il tasto destro.

### Pannello Split & Bridge

Un pannello flottante in alto a destra contiene:

- il campo con i due identificativi degli archi;
- lo stato della selezione;
- il pulsante primario `Split & Bridge`;
- un breve suggerimento sull'interazione con il tasto destro.

Il campo conserva l'ID `edgeSplitInput` e il pulsante conserva l'ID `btnSplitEdges`.

### Dock inferiore

Un dock compatto, centrato in basso, raccoglie i controlli secondari:

- etichette nodi;
- etichette archi;
- debug;
- esportazione DOT;
- apertura del pannello parametri.

I controlli mantengono gli ID attuali, così la logica esistente può essere riutilizzata senza modifiche invasive.

### Pannello parametri

I parametri grafici e fisici si aprono in un drawer laterale destro. Il drawer:

- è chiuso all'avvio;
- raggruppa i campi in `Aspetto` e `Fisica`;
- conserva valori, limiti, pulsanti di reset e ID esistenti;
- si chiude con un pulsante esplicito, con `Escape` o cliccando sul backdrop;
- non blocca l'uso del canvas quando è chiuso.

## Comportamento e compatibilità

La versione V2 conserva:

- Graphology e Cytoscape caricati dagli stessi CDN;
- creazione del grafo iniziale;
- algoritmo Split & Bridge;
- simulazione fisica;
- gestione degli archi paralleli;
- trascinamento dei nodi e modifica della curvatura;
- selezione degli archi e sincronizzazione del campo;
- esportazione DOT;
- toggle di etichette e debug;
- configurazione e reset dei parametri;
- diagnostica e scorciatoia `Shift+D`.

Le aggiunte JavaScript sono limitate alla gestione del drawer, all'aggiornamento delle statistiche visive e ai messaggi di stato dell'interfaccia. `split_and_bridge.html` resta invariato.

## Responsive e accessibilità

- Su desktop, pannello azione e dock galleggiano sopra il canvas.
- Su schermi stretti, il pannello azione diventa una fascia compatta e il dock può andare a capo senza coprire i comandi principali.
- Il drawer usa una larghezza fluida con limite massimo.
- Pulsanti e input mantengono etichette accessibili, focus visibile e target adeguati.
- Le animazioni rispettano `prefers-reduced-motion`.
- Colori di stato non sono l'unico indicatore della selezione.

## Gestione degli errori

Gli errori di input vengono mostrati nel pannello azione con un messaggio breve e visibile, oltre al logging di debug esistente. Gli errori globali continuano a essere intercettati dalla diagnostica attuale. Se le librerie CDN non sono disponibili, la pagina mostra un messaggio di inizializzazione leggibile invece di restare apparentemente vuota.

## Verifica

La verifica comprende:

1. controllo statico degli ID richiesti e della sintassi JavaScript;
2. apertura della pagina nel browser senza errori console;
3. selezione di due archi e operazione Split & Bridge;
4. apertura, modifica, reset e chiusura del drawer parametri;
5. toggle etichette e debug;
6. esportazione DOT;
7. controllo visivo a larghezza desktop e mobile;
8. conferma che il file originale non sia stato modificato.

## Fuori ambito

Non sono previsti nuovi algoritmi, persistenza locale, backend, sostituzione di Cytoscape o Graphology, nuovi formati di importazione o modifiche al resto del progetto.
