---
title: "Production Key Vault Behavior"
status: active
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, app/security]
---

# Production Key Vault Behavior

## Purpose

Production settings must fail closed when Key Vault is unavailable and must
load required secrets from Key Vault when configured.

## Covered Behavior

- production mode requires `AZURE_KEY_VAULT_URL`
- Key Vault refresh updates JWT, encryption, Groq, and Anthropic secrets
- empty Key Vault secret values fail closed

## Verification

```bash
pytest -c pytest.ini tests/unit/test_production_key_vault_behavior.py -q --no-cov
```
