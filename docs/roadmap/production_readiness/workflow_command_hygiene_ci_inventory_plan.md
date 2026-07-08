# PRD-0.6 Workflow Command Hygiene and CI Inventory Plan

This plan records the controlled workflow hygiene work for PRD-0.6.

## Canonical command

```bash
PYTHONPATH=. python3 -m pytest
```

## Controlled changes

1. Apply a narrow workflow rewrite for direct `pytest` commands.
2. Preserve existing `python -m pytest` / `python3 -m pytest` commands.
3. Do not rewrite dependency install lines such as `pip install pytest`.
4. Capture the workflow inventory after the authority branch lands.
5. Defer dependency-install completion and broader CI contract cleanup to later PRD slices where needed.

## Deferred work

- PRD-0.7 handles OpenAPI and generated artifact canonicalisation.
- PRD-0.8 handles branch/release naming reconciliation.
- PRD-1+ remains blocked until PRD-0.10 closes.
