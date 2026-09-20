# Verifica della consegna

Data: 16 settembre 2026. Runtime: Python 3.9.6, macOS.
Nessuna dipendenza Python esterna richiesta.

## Test completi

```sh
python3 -m unittest discover -s tests -v
```

Esito: **29 test passati**, 11,649 secondi nell'ultima esecuzione.
I due test di regressione per alias hard-link e spiegazioni delle mosse
sono stati eseguiti prima delle correzioni, riproducendo entrambi i difetti;
dopo le correzioni passano. Una revisione indipendente ha ricontrollato
modello, quantificatori e correzioni senza ulteriori rilievi aperti.

## Analisi complete

```sh
python3 -m kempe analyze --quotient-colors --include-graph \
  --output results/quotient.json --explain results/explain.jsonl \
  --dot results/quotient.dot
python3 -m kempe analyze --output results/labeled.json
python3 -m kempe pairing-example --output results/pairing-example.json
```

Entrambe le analisi hanno terminato con codice 0, senza limiti raggiunti.
Risultati confermati nei JSON:

- Etichette fisse: 2.160 stati, 101.520 archi, 120 candidati nel nucleo bad.
- Quoziente S4: 90 stati, 1.530 archi, 5 candidati nel nucleo bad.
- Una SCC del grafo may completo; nessuna SCC interamente bad.
- `r5_proved=false` e `all_states_forced_good=false` in entrambi i rapporti.
- Registro explain: 52.504 eventi, pari alla somma dei contatori del rapporto.

`results/locked-candidates.json` estrae i cinque stati dal rapporto quoziente
e conserva il riferimento alla v16. Non costituisce una certificazione di
realizzabilità. I conteggi sono di stati astratti, non di colorazioni concrete.

## Ambito della verifica

Il pacchetto è autonomo. La verifica sopra documenta la prima consegna.
Successivamente il pacchetto è stato copiato in `ct/kempe-verifier/` del
repository della fonte. Il documento v16, i file sincronizzati del progetto
e il programma esistente `ct/4ct.py` non sono stati modificati.
I test su grafi concreti controllano casi finiti e non dimostrano R5.


## Verifica dopo la copia in `ct/kempe-verifier/`

Eseguita il 16 settembre 2026 con `ct/` come directory di lavoro:

```sh
PYTHONPATH="$PWD/kempe-verifier" python3 -m unittest discover -s kempe-verifier/tests -v
../.venv/bin/python -m pytest -p no:cacheprovider tests -q
../.venv/bin/python 4ct.py -s1 -r2 10
```

- Test del verificatore: **29 passati** (11,747 secondi).
- Test esistenti del repository: **28 passati** (0,14 secondi).
- Controllo della pipeline principale: codice 0; ricostruzione completata,
  grafo ricreato uguale all'originale secondo il controllo della pipeline.
- Analisi dal nuovo percorso: 90 stati modulo S4, 5 candidati nel nucleo bad,
  `r5_proved=false`.
- Verificati anche i comandi `moves` sull'esempio `examples/locked-b0.json`
  e `analyze --classifier examples.custom_classifier:classify` da `ct/`.
- Codice e test Python copiati senza modifiche rispetto al prototipo verificato.
- Hash della v16 invariato; nessuna modifica ai file tracciati preesistenti.
- `git diff --check` senza errori; `results/` e cache escluse da Git.

Per queste verifiche sono state disabilitate le cache bytecode Python e
sono stati scritti i rapporti di controllo temporanei fuori dal repository.
La pipeline principale ha prodotto i suoi consueti artefatti ignorati in `ct/debug/`.
