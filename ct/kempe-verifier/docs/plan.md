# Kempe Verifier Implementation Plan

**Goal:** prototipo eseguibile e conservativo per gli stati di bordo di Q.

**Architecture:** moduli separati per stato, enumerazione, mosse, analisi,
pairing primal e CLI. Esecuzione nella sessione corrente con test prima del codice.

**Tech Stack:** Python >=3.9, dataclasses, itertools, unittest, argparse, json.

**Spec:** `docs/design.md`.

## Vincoli globali

Non modificare le fonti. Non assumere realizzabilità degli stati astratti.
Non interpretare le SCC may come classi Kempe concrete. Non fare conteggi R5
sugli stati compressi. Preservare tutte le alternative non escluse dai vincoli.

## 1. Stato, enumerazione e R5

- [x] Scrivere `tests/test_model.py`: 240 parole proprie; 120 good, 120 bad;
  fan e settori; normalizzazione coerente sotto tutte le 24 permutazioni;
  accettazione dei blocchi non binari e rifiuto di partizioni malformate.
- [x] Eseguire `python3 -m unittest discover -s tests -v` e verificare fallimento.
- [x] Implementare `kempe/model.py`, `kempe/enumeration.py`, `kempe/explain.py`.
- [x] Rieseguire i test e controllare che passino.

## 2. Transizioni, grafi e pairing

- [x] Scrivere test per le due partizioni invarianti, tutti i successori,
  azioni remote, completezza contro grafi concreti, SCC e quantificatori.
- [x] Riprodurre §9.15 nei test: stessa partizione prima, diversa dopo.
- [x] Verificare fallimento, poi implementare `moves.py`, `analysis.py`, `pairing.py`.
- [x] Verificare il modello completo, senza limiti o ritagli dello spazio.

## 3. CLI, spiegazioni e documentazione

- [x] Testare CLI, JSON/DOT, motivi di esclusione e interruzioni per limiti.
- [x] Implementare `__main__.py`, README e un esempio di criterio personalizzato.
- [x] Eseguire test completi e analisi con etichette fisse e con quoziente S4.
- [x] Controllare gli artefatti JSON e i conteggi, registrare risultati e limiti.
