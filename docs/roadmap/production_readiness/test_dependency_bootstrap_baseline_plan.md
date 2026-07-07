# Test/dependency bootstrap baseline plan

## Objective

Create a deterministic baseline describing how EduBoost's test and dependency environment is expected to bootstrap before deeper PRD-0 repair work begins.

## Baseline categories

1. Python runtime and dependency declarations.
2. Backend test tool declarations.
3. Pytest configuration sources.
4. Frontend package-manager and test-tool declarations.
5. CI command hygiene inventory.
6. Known deferred test/collection stabilisation boundary.

## Canonical command direction

Dependency installation should include:

```bash
pip install -r requirements.txt && pip install -r requirements/dev.txt
```

Backend test invocations should converge on:

```bash
PYTHONPATH=. python3 -m pytest ...
```

This avoids PATH-dependent `pytest` failures observed during the KG and PRD streams.

## Deferred work

PRD-0.4 only records the baseline. It intentionally defers:

- failing test collection triage to PRD-0.5;
- workflow command convergence to PRD-0.6;
- OpenAPI/generated artifact canonicalisation to PRD-0.7.
