# Design: formattazione delle note di progetto

## Obiettivo

Migliorare la leggibilità e la consultabilità di `docs/notes.md` senza alterarne il contenuto tecnico né tradurre le sezioni. Correggere i refusi evidenti nella lingua originale di ogni passaggio.

## Struttura

- Aggiungere un titolo principale e un breve indice iniziale.
- Conservare l'ordine attuale delle note.
- Trasformare ciascuna data in un'intestazione di secondo livello.
- Usare intestazioni di terzo o quarto livello per gli argomenti interni.
- Non suddividere il documento in più file.

## Convenzioni Markdown

- Uniformare elenchi puntati e numerati secondo Markdown standard.
- Racchiudere nomi di file, funzioni, opzioni CLI e identificatori in backtick.
- Racchiudere output diagnostici e profili prestazionali in blocchi di codice `text`.
- Racchiudere lo pseudocodice in un blocco di codice dedicato.
- Eliminare indentazioni accidentali, spazi doppi e interruzioni di riga che spezzano le frasi.
- Mantenere completi i dump e gli esempi tecnici.

## Revisione linguistica

- Correggere errori ortografici, grammaticali e di battitura evidenti.
- Conservare italiano e inglese così come sono distribuiti nel documento.
- Non cambiare il significato di requisiti, osservazioni, log o risultati sperimentali.
- Non uniformare terminologia tecnica quando la variante potrebbe riflettere una distinzione intenzionale.

## Verifica

- Controllare che tutti i blocchi di codice siano chiusi correttamente.
- Controllare la gerarchia delle intestazioni e i collegamenti dell'indice.
- Confrontare il documento risultante con l'originale per accertare che nessuna sezione o riga tecnica sia stata omessa.
- Esaminare il diff finale per escludere modifiche estranee.

## Ambito escluso

- Traduzione delle sezioni.
- Riscrittura o aggiornamento delle specifiche algoritmiche.
- Rimozione o sintesi dei log storici.
- Modifiche al codice Python o ad altri documenti.
