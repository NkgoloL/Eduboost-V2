# IRT Engine

The IRT engine supports adaptive diagnostics and learner mastery estimation.

## Runtime map

- Engine implementation: `app/modules/diagnostics/irt_engine.py`
- Item validation and quality: `app/modules/diagnostics/item_validator.py`, `quality_scorer.py`
- IRT tests: `tests/unit/test_irt_properties.py`, `tests/unit/test_irt_gap_probe.py`

## Current implementation notes

- IRT behavior should be validated through numerical/property tests and diagnostic-session integration tests.
- Launch content should keep item difficulty/discrimination distributions auditable by CAPS reference.
- Any hand-tuned or synthetic item-bank generation must carry source/provenance evidence.

## Verification

```bash
.venv/bin/python -m pytest -q tests/unit/test_irt_properties.py tests/unit/test_irt_gap_probe.py --no-cov
```

Back to the main index: [docs/README.md](../README.md). Root overview: [README.md](../../README.md).
