# Generated Artifact Hygiene Contract

## Purpose

Generated local artifacts must not block release commits, rebase operations, or
beta evidence closure.

## Generated Artifacts Excluded From Release Evidence

- `coverage.xml`
- `.coverage`
- `.pytest_cache/`
- `.hypothesis/`
- `htmlcov/`
- `node_modules/`
- `playwright-report/`
- `test-results/`
- `temp/`
- `.mypy_cache/`
- `.ruff_cache/`
- `__pycache__/`

## Required Git Hygiene Rules

- generated coverage output is not release evidence
- generated cache directories are not release evidence
- unresolved generated files must be removed before commit
- coverage.xml conflicts must be resolved by removal, not manual merge
- release commits must include only source, docs, workflow, and test evidence
- force-push is not the default recovery path

## Required `.gitignore` Entries

```text
coverage.xml
.coverage
.pytest_cache/
.hypothesis/
htmlcov/
playwright-report/
test-results/
temp/
.mypy_cache/
.ruff_cache/
```

## Command

```bash
make generated-artifact-hygiene-check
```
