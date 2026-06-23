---
title: "Environment Security Contract"
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

# Environment Security Contract

## Purpose

Production deployments must not rely on development placeholder secrets.

## Contract

The settings layer must preserve:

- `ENVIRONMENT` and `APP_ENV` production modes
- `is_production()`
- Azure Key Vault secret loading
- fail-closed `AZURE_KEY_VAULT_URL` requirement in production
- Key Vault secret names for JWT, encryption, Groq, and Anthropic keys

## Command

```bash
make environment-security-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_environment_security_contract.py -q --no-cov
```

## Production Key Vault Behavior

- Production Key Vault behavior tests cover fail-closed and refresh paths.
