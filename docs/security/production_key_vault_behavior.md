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
