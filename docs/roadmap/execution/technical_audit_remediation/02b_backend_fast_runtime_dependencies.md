# Technical Audit Remediation Phase 02B — Backend Fast Runtime Dependencies

**Status:** implementation assets ready  
**Depends on:** Phase 02A failed-gate diagnostics  
**Authority gate:** `make test-fast` remains authoritative and must not be weakened.

## Problem

The first backend-fast authority run failed with a large import/dependency cluster before the remaining application defects could be isolated. The Makefile runs backend fast tests with:

```text
.venv/bin/python -m pytest -c pytest.ini tests/unit -n auto --no-cov -m "not governance and not slow and not llm and not e2e" -q
```

The failure diagnostics captured missing modules in that authority path, including FastAPI/runtime, diagnostics, POPIA, OpenAPI, and worker dependencies.

## Objective

Make the backend-fast authority Python environment reproducible and verifiable before retrying `make test-fast`.

## Deliverables

- Runtime dependency verifier for the Makefile authority interpreter.
- `.venv` synchronization script using `requirements/dev.txt`.
- Environment evidence collector.
- Focused unit tests for the verifier.
- Blocker register update.

## Boundary

This slice does not create passing backend-fast evidence. It only proves the authority Python environment is dependency-complete. Passing backend-fast evidence remains blocked until the full `make test-fast` command exits 0.

## KG north-star note

No runtime knowledge-graph work is introduced. Future KG-friendly behavior is preserved only by keeping curriculum/corpus/tutor modules importable under the normal backend-fast gate.
