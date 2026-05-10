# Production Secret Placeholder Guard

## Purpose

Development placeholder secrets may exist in defaults for local execution, but
production must fail closed and load real secret values from Azure Key Vault.

## Guarded Configuration

- `JWT_SECRET`
- `ENCRYPTION_KEY`
- `ENCRYPTION_SALT`
- `AUDIT_HMAC_SECRET`
- LLM provider API keys

## Required Production Gate

Production mode must preserve:

- `is_production()`
- `load_production_secrets_from_key_vault`
- `refresh_from_key_vault`
- `AZURE_KEY_VAULT_URL is required when APP_ENV is production`
- `Azure Key Vault returned an empty value`

## Command

```bash
make production-secret-placeholder-check
```

## Verification

```bash
pytest -c pytest.ini tests/unit/test_production_secret_placeholders.py -q --no-cov
```

## Production Key Vault Behavior

- Production Key Vault behavior tests verify placeholder replacement and empty-secret failure.
