# Verificatore Kempe pentagonale — specifica

## Fonte e ambito

Fonte letta: `maps-coloring-python/docs/llm-vs-4ct/4ct-v16.md`,
§§9.8, 9.14–9.15, 10.3–10.9. Il programma studia il bordo del grafo duale
Q del §10.4. Non identifica switch di vertici in Q e switch di archi in G_i.

## Rappresentazione

`State(boundary, partitions)` è immutabile. I colori sono 0,1,2,3 e i terminali
0,1,2,3,4 restano etichettati in ordine ciclico. Le sei partizioni indicizzate
dalle coppie di colori registrano le componenti bicolori che toccano il bordo.
Un blocco può contenere uno, due o più terminali: non è un perfect matching.
La forma canonica ordina blocchi e membri; una riduzione facoltativa per S4
rinomina anche le sei coppie. Non si quotientano rotazioni o riflessioni.

I veri `TransitionPairing` del §9.8 sono una struttura separata: matching sui
vertici di uno specifico ciclo, con chiusure vecchia e nuova e verifica delle
due pagine. Riprodurre il controesempio del §9.15 verifica la distinzione.

## Enumerazione

Si enumerano le 4^5 parole, si eliminano quelle non proprie sul ciclo, quindi
tutte le partizioni dei terminali attivi per ciascuna coppia. Sono obbligatori
la connettività lungo gli archi del bordo e l'assenza di attraversamenti fra
blocchi disgiunti della stessa coppia o di coppie di colori disgiunte.
Non si vietano attraversamenti fra coppie che condividono un colore.
Questi sono vincoli necessari: la realizzabilità simultanea in un Q del §10.4
non è certificata. Non si inventano parità, 5-connessione o altre eliminazioni.
Filtri aggiuntivi richiedono un motivo e una fonte dichiarati dal chiamante.

## Mosse conservative

Per ogni coppia e ogni blocco non vuoto si scambiano i colori su quel blocco.
Sono identiche le partizioni della coppia scambiata e della complementare.
Le altre quattro possono assumere qualsiasi valore ammissibile. Un'azione
identifica il blocco scambiato; i suoi successori sono alternative possibili,
non mosse indipendenti garantite. Un'azione opzionale per coppia rappresenta
un componente interno senza terminali, la cui esistenza non è garantita.

## Classificazione e ricerca

Default R5 §10.5: 3 colori good, 4 bad, con settori E_i/B_i e appartenenza ai fan.
La classificazione è sostituibile mediante callback Python.
Si costruisce il grafo may delle transizioni possibili e si calcolano SCC,
SCC interamente bad e SCC bad chiuse nel grafo completo.

Separatamente si calcola il massimo insieme X di stati bad che soddisfa:
per ogni stato in X e ogni azione garantita, almeno un successore è in X.
L'eliminazione avviene per livelli e certifica condizionalmente una strategia
di uscita da bad. Se la classificazione ammette unknown, solo l'eliminazione
da un secondo nucleo inizializzato con bad e unknown certifica una strategia
verso good, rispetto all'astrazione e ai filtri dichiarati.
Le azioni remote opzionali non possono forzare un'eliminazione.
Un nucleo non vuoto non certifica realizzabilità; zero SCC bad chiuse non
dimostra R5. Conteggi di stati astratti non sono conteggi di colorazioni di Q.

## Verifica e consegna

Solo libreria standard, Python >=3.9. CLI con JSON, DOT ed explain JSONL,
limiti che interrompono con errore senza analizzare un grafo troncato.
Test su parole, settori, planarità, simmetrie, transizioni concrete (anche
remote), §9.15, SCC e quantificatori del nucleo. README italiano con assunzioni,
comandi riproducibili e limiti logici.
