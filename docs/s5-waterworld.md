# S5: studio e verifica sulle mappe Waterworld

Verifica del 23 settembre 2026, Python 3.9.6 e NetworkX 3.2.1.

## Risultato

Tutti i dieci file presenti `waterworld-1.planar` … `waterworld-10.planar`
sono stati ridotti e ricostruiti correttamente, con **zero scambi casuali**.
Ogni file conteneva una mappa. Il benchmark ha verificato colorazione propria,
cubicità, esaurimento della pila di Arianna, insieme dei vertici e multinsieme
esatto degli archi con gli identificatori originali, comprese le molteplicità.
Le funzioni che effettuano scelte casuali erano sostituite da un errore:
quindi il risultato non dipende soltanto dal contatore degli scambi casuali.

Sono stati ricostruiti complessivamente **124.422 vertici**. Degli **8.716 F5**,
6.521 hanno richiesto soltanto l'estensione diretta e 2.195 una ricerca,
per un totale di 2.640 scambi completi deterministici prima dei mezzi scambi.
Il massimo numero di stati esaminati in una ricerca è stato 61.
Questo contatore misura gli stati esaminati, non tutte le colorazioni già
memorizzate nella coda; il limite di 10.000 riguarda queste ultime.

| Mappa | Vertici | F5 diretti | F5 con ricerca | Scambi deterministici | Max stati esaminati | Secondi |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| waterworld-1.planar | 11388 | 329 | 122 | 137 | 49 | 23.528 |
| waterworld-2.planar | 13266 | 378 | 111 | 131 | 33 | 29.815 |
| waterworld-3.planar | 5576 | 330 | 91 | 112 | 33 | 8.766 |
| waterworld-4.planar | 18494 | 1155 | 363 | 433 | 33 | 89.927 |
| waterworld-5.planar | 15716 | 932 | 371 | 442 | 33 | 76.984 |
| waterworld-6.planar | 17496 | 1003 | 323 | 395 | 33 | 85.201 |
| waterworld-7.planar | 15582 | 931 | 314 | 379 | 33 | 68.373 |
| waterworld-8.planar | 30 | 1 | 0 | 0 | 0 | 0.002 |
| waterworld-9.planar | 10526 | 507 | 171 | 209 | 61 | 28.266 |
| waterworld-10.planar | 16348 | 955 | 329 | 402 | 33 | 84.315 |

I tempi comprendono riduzione e ricostruzione, senza profiling della CLI,
caricamento e verifiche finali. Sono misure di una singola esecuzione su questa
macchina, non una stima statistica né un confronto prestazionale con S4.
Tutte le scelte F5 hanno usato facce con un vertice positivo; il ripiego su
F5 generiche non è stato necessario. Una wave è stata interrotta sulla mappa 2.
Le mappe 9 e 10 sono state aggiunte durante il lavoro e verificate separatamente
con lo stesso codice e gli stessi parametri.

## Interpretazione matematica

Il metodo usa la lista inevitabile della sezione 6 di
[v17](llm-vs-4ct/4ct-v17.md) per ordinare le riduzioni. L'inevitabilità è una
conseguenza della curvatura; **non certifica la riducibilità cromatica** dei
sette tipi. V17 lascia aperto R₅ e distingue l'esistenza di una colorazione
riparabile dalla riparabilità di ogni classe di Kempe (§§9.18 e 10.3).
La distinzione fra inevitabilità e riducibilità è anche esplicita nella
[descrizione degli autori della dimostrazione RSST](https://thomas.math.gatech.edu/FC/fourcolor.html).
S5 non importa il catalogo RSST e non costituisce una nuova dimostrazione.

L'osservazione sperimentale è precisa: la selezione proposta **non elimina
la necessità di ricolorare**. Per eliminare la casualità, S5 affianca alla
selezione una ricerca deterministica delle sequenze di Kempe. Il criterio
di successo è CONDITION-1 di v17 §8.2, verificato sui cicli effettivi.
Si conserva l'intera colorazione con l'identità degli archi paralleli,
non soltanto la parola sul bordo. Questo evita l'errore discusso in
v17 §§9.14–9.18, dove uno scambio remoto modifica connessioni invisibili
nella parola locale.

Due ordini di ricerca inizialmente provati hanno raggiunto il limite di
10.000 colorazioni sulla prima Waterworld: una ricerca in ampiezza su tutti
i cicli e una che esauriva l'orbita locale prima di passare ai cicli remoti.
La prima disperdeva il budget su molte alternative lontane; la seconda
poteva consumarlo prima di esplorare quelle remote. L'ordine finale
alterna espansioni locali e remote. I risultati sopra appartengono a questo
ordine finale; non implicano che sia ottimale o che riesca su ogni mappa.

Una ricerca che termina senza soluzione distingue due casi: limite
raggiunto oppure classe di Kempe completamente esaurita. In entrambi i casi
S5 termina con errore senza ricorrere a scambi casuali. Nessuno dei due esiti
prova che il grafo sia incolorabile. La descrizione canonica di selezione,
priorità, ricerca e limiti è in [algorithm.md](algorithm.md).

## Riproduzione

Dalla directory `ct/`:

```bash
uv run --python ../.venv/bin/python python -m pytest tests -q
uv run --python ../.venv/bin/python python tests/benchmark_selection5.py
uv run --python ../.venv/bin/python python 4ct.py -s5 -p examples/planar/waterworld-8.planar
```

La suite finale ha prodotto **51 test superati**. Sono passati anche gli
smoke test `-s1 -r2 10`, `-s4 -r2 20` e la CLI S5 sulla mappa 8.
Il benchmark rimane separato dalla suite veloce e scopre automaticamente
anche eventuali nuovi file Waterworld. I dati di debug sono esclusi da Git.

Per rendere identificabile il campione, questi sono i prefissi SHA-256
(a 16 cifre esadecimali) dei file verificati:

| File | SHA-256, prefisso |
| --- | --- |
| waterworld-1.planar | `eeddcf419e5b8158` |
| waterworld-2.planar | `7cb29a13f8583a32` |
| waterworld-3.planar | `52cc053ee041872c` |
| waterworld-4.planar | `c4d07b2e4e753a38` |
| waterworld-5.planar | `ea685fa4a5f601f1` |
| waterworld-6.planar | `ce53a550a6c5cc60` |
| waterworld-7.planar | `5ca8c07fb7f9e0fe` |
| waterworld-8.planar | `50a7361df6552a83` |
| waterworld-9.planar | `9023e6b4988519fe` |
| waterworld-10.planar | `ede37b06b9548309` |
