# Local Pytest Evidence Capture

This document defines how EduBoost captures repository-local pytest evidence for release readiness.

## Commands

Capture all local pytest release evidence:

```bash
make capture-pytest-release-evidence
```

Validate captured evidence files:

```bash
make pytest-release-evidence-check
```

Capture individual scopes:

```bash
PYTHONPATH=. python3 scripts/capture_pytest_release_evidence.py unit
PYTHONPATH=. python3 scripts/capture_pytest_release_evidence.py integration
PYTHONPATH=. python3 scripts/capture_pytest_release_evidence.py full
```

## Evidence files

| Scope | File |
|---|---|
| Unit | `docs/release/unit_latest_green.txt` |
| Integration | `docs/release/integration_latest_green.txt` |
| Full pytest discovery | `docs/release/full_pytest_latest_green.txt` |

## Rules

- Local pytest evidence proves repository-local health only.
- It does not replace CI, staging smoke, migration proof, backup/restore drill, or human release signoff.
- Evidence files must include command, timestamp, return code, and passing summary.
