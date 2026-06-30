# Backend testing

## Profiles

| Command | When to use |
|---------|-------------|
| `make test` / `make test-fast` | Daily development and PR feedback (parallel, no coverage) |
| `make test-integration` | API/DB integration paths |
| `make test-coverage` | Pre-merge or weekly; enforces `COVERAGE_THRESHOLD` (default 67%) |
| `make test-coverage-full` | Full tree including governance tests; no fail-under |
| `make test-governance` | Release/evidence/doc-contract meta-tests only |

## Configuration

- **`pytest.ini`** — default fast profile (no `--cov`).
- **`pytest-coverage.ini`** — coverage instrumentation + HTML/XML reports.
- **`.coveragerc`** — async-safe tracing (`concurrency = greenlet,thread`).

Governance tests are auto-tagged from filename heuristics in `tests/governance_markers.py` and excluded from the PR fast gate via `-m "not governance …"`.

## CI

- **Fast gate:** `tests/unit` with `pytest-xdist` (`-n auto`), `--no-cov`.
- **Integration:** `tests/integration`, `--no-cov`.
- **Coverage job:** `make test-coverage` after migrations (unit + integration, ratchet threshold).
