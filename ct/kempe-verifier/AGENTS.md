# Verificatore Kempe autonomo

Questo pacchetto studia stati di bordo nel duale Q della v16. Non è parte
della pipeline di riduzione e ricostruzione di `ct/4ct.py`.

- Leggere `README.md` e `docs/design.md` prima di modificare il modello.
- Mantenere Python >=3.9 e l'esecuzione senza dipendenze esterne.
- Non confondere partizioni di componenti di vertici con i matching primal
  del §9.8: sono strutture distinte.
- Preservare tutti gli esiti non esclusi da vincoli matematici giustificati.
- Le SCC del grafo may non certificano da sole l'assenza di classi concrete bad.
- Non trattare `unknown` come `good`, né uno switch interno opzionale come garantito.
- Documentare fonte e premessa di ogni nuova eliminazione.
- Non modificare la v16 per adattarla al programma.
- Tenere `results/` e le cache fuori da Git; mantenere solo esempi piccoli
  e deliberati in `examples/`.

## Verifica

Dalla cartella `ct/`:

```sh
PYTHONPATH="$PWD/kempe-verifier" python3 -m unittest discover -s kempe-verifier/tests -v
PYTHONPATH="$PWD/kempe-verifier" python3 -m kempe analyze --quotient-colors
```

Per modifiche matematiche verificare anche l'analisi senza `--quotient-colors`
e confrontare con gli invarianti e i risultati attesi nel README.
