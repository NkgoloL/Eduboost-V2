# PR-002R Evidence Check

## Purpose

`make pr002r-check` verifies that the PR-002R runtime/API contract evidence
surface is present and internally linked.

It is a review gate for the PR-002R baseline. It does not replace behavioral
unit tests, OpenAPI drift checks, route inventory drift checks, runtime checks,
or CI.

## Command

```bash
make pr002r-check
```

Equivalent direct command:

```bash
python3 scripts/check_pr002r_evidence.py
```

Machine-readable output:

```bash
python3 scripts/check_pr002r_evidence.py --json
```

## Coverage

The checker verifies the presence of:

- runtime evidence docs,
- release evidence index,
- OpenAPI artifact,
- route inventory artifact,
- runtime checker,
- OpenAPI generator,
- route inventory generator,
- PR template,
- focused PR-002R tests,
- import-path baseline.

It also checks key content markers such as:

- `app.api_v2:app`,
- `make runtime-check`,
- `make openapi-check`,
- `make route-inventory-check`,
- production/public-beta non-approval language.

## Non-Goal

This checker does not prove production readiness. It only proves that the
PR-002R evidence bundle is structurally complete enough for review.
