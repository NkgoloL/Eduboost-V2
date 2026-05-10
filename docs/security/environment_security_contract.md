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
