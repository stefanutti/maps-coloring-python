# Final fix report — Split & Bridge label controls

## Modifica

Aggiornato `ct/tests/test_split_and_bridge_v2.py` senza modificare la produzione:

- il test update/reset registra ora le chiamate esatte al doppio Cytoscape, incluse le tuple `(selector, 'font-size', value)` e la successiva `update()` per nodi e archi;
- aggiunto un harness d'integrazione leggero che esegue la vera `syncGraphToCytoscape()` con configurazioni non predefinite (`17` e `13`), sostituisce gli elementi attraverso il doppio Cytoscape e verifica che le due dimensioni siano riapplicate con `update()`.

Il doppio sostituisce solo Cytoscape e le dipendenze di rendering; `syncGraphToCytoscape()` e le due funzioni di applicazione provengono dal JavaScript della pagina.

## RED / mutation check

Il nuovo harness è stato eseguito dopo una mutazione temporanea della produzione: rimozione delle due righe seguenti da `syncGraphToCytoscape()`:

```javascript
applyNodeLabelFontSize(config.nodeLabelFontSize);
applyEdgeLabelFontSize(config.edgeLabelFontSize);
```

Comando:

```bash
cd ct && ../.venv/bin/python -m pytest tests/test_split_and_bridge_v2.py::test_label_font_sizes_are_reapplied_after_sync_replaces_elements -q
```

Output:

```text
FAILED tests/test_split_and_bridge_v2.py::test_label_font_sizes_are_reapplied_after_sync_replaces_elements
Differing items:
{'labelCalls': []} != {'labelCalls': [['node', 'font-size', 17, True], ['edge', 'font-size', 13, True]]}
1 failed in 0.10s
```

Le due righe di produzione sono state quindi ripristinate senza altre modifiche alla pagina.

## GREEN e verifica

```bash
cd ct && ../.venv/bin/python -m pytest tests/test_split_and_bridge_v2.py -k 'label_font_size' -q
```

```text
2 passed, 12 deselected in 0.10s
```

```bash
cd ct && ../.venv/bin/python -m pytest tests/ -q
```

```text
42 passed in 0.26s
```

```bash
cd ct && git diff --check -- ct/web_split_and_bridge/split_and_bridge_v2.html ct/tests/test_split_and_bridge_v2.py
```

Exit code `0`, nessun errore di whitespace. Git ha emesso il warning ambientale non bloccante `fsmonitor_ipc__send_query: unspecified error on '.git/fsmonitor--daemon.ipc'`.

## Self-review

- Il test update/reset non può più passare se viene usata una proprietà diversa da `font-size`, un selettore diverso, un valore diverso, oppure se manca `update()`.
- Il nuovo test attraversa la sostituzione reale degli elementi nella funzione di sync; la mutazione ha dimostrato che l'assenza delle riapplicazioni viene rilevata.
- Le configurazioni nel harness (`17` e `13`) sono intenzionalmente diverse dai default, per distinguere la persistenza dallo stile iniziale.
- Produzione invariata: il comportamento richiesto era già corretto; la lacuna era esclusivamente nella copertura di regressione.
