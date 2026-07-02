---
title: "RR-005 Ruff Debt Inventory"
status: active
owner: engineering
audience: developer
source_of_truth: true
evidence_command: "ruff check app tests scripts --statistics"
---

# RR-005 Ruff Debt Inventory

RR-005 refreshes the Ruff debt baseline without requiring all non-blocking style debt to be eliminated in this slice.

## Canonical commands

```bash
ruff check app tests scripts --statistics
ruff check app tests scripts --output-format=json
```

## Closure interpretation

- Ruff findings are expected until specific burn-down PRs remove them.
- RR-005 requires the inventory to be current and auditable.
- Release-blocking correctness checks remain separate from broad non-blocking style debt.

## Follow-up backlog

The capture output records `statistics_counts`, JSON finding summaries, and top files when Ruff is available. If Ruff is unavailable in a local environment, the capture script preserves the existing `docs/backlog/ruff_debt.md` baseline and records the tool-availability limitation.
