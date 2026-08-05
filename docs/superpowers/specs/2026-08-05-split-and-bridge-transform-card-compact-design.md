# Split & Bridge V2 — pannello Trasformazione compatto

## Obiettivo

Rendere il pannello flottante **Trasformazione** meno invasivo nelle finestre strette e migliorare la gerarchia verticale dei suoi controlli, senza modificare la logica Split & Bridge.

## Layout

La larghezza desktop della `.command-card` resta `min(22rem, calc(100% - 2rem))`. Nel breakpoint esistente `max-width: 760px`, il pannello usa `width: 60%` e mantiene l'ancoraggio `top: 1rem`, `left: 1rem`, `right: auto`.

Il pannello resta adattivo: larghezza e padding devono rientrare nella workspace anche su schermi stretti. Testi lunghi possono andare a capo senza produrre overflow orizzontale.

## Stati e spaziatura

Il contenuto iniziale di `#actionStatus` sarà vuoto. L'elemento con `aria-live="polite"` resta nel DOM per comunicare messaggi di successo o errore dopo un'azione, ma quando è vuoto non occupa spazio visivo.

Tra `#selectionStatus` e `.command-actions` viene introdotto uno spazio verticale esplicito, così la riga “0 di 2 archi selezionati” non risulta attaccata al pulsante. Gli altri spazi e stili del pannello restano invariati.

## Accessibilità e comportamento

La rimozione del messaggio iniziale non elimina la regione live. `setActionStatus()` continua a mostrare messaggi e toni dopo la trasformazione o in caso di input non valido. Non cambiano selezione degli archi, pulsante, suggerimento, colori o focus.

## Verifica

I test automatici devono verificare:

- larghezza desktop invariata e larghezza mobile al `60%`;
- ancoraggio mobile ancora in alto a sinistra;
- `#actionStatus` inizialmente vuoto e ancora configurato come regione live;
- stato vuoto nascosto senza impedire la visualizzazione dei messaggi successivi;
- spazio verticale esplicito prima del pulsante;
- suite completa e assenza di errori di whitespace.

## Fuori ambito

Non cambiano drawer Parametri, controlli tipografici, grafo, fisica, trasformazione, toolbar o pagina HTML originale.
