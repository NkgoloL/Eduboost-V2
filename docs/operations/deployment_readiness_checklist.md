# Deployment Readiness Checklist

## Runtime Contract

- `make runtime-check`
- `make openapi-check`
- `make route-inventory-check`

## Authorization Contract

- `make phase2-authz-check`
- `make learner-authz-check`
- `make phase2-authz-closure`

## POPIA Consent/Audit Contract

- `make popia-consent-closure-check`
- `make popia-consent-gate-check`
- `make popia-consent-boundary-check`
- `make popia-consent-order-check`
- `make popia-consent-source-check`
- `make popia-consent-rejection-audit-check`

## Environment Contract

- `make environment-security-check`
- `make dev-only-endpoint-check`
- `make production-secret-placeholder-check`

## Production Requirements

Production must use Azure Key Vault for required secrets and must fail closed
when `AZURE_KEY_VAULT_URL` is missing.

## Release Evidence

Before staging or production release, attach command output for all checklist
items to the PR or release evidence record.
