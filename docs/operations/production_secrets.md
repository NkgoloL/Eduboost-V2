# Production Secrets Management

## Overview

EduBoost V2 production secrets are stored in **Azure Key Vault** with local `.env` file fallback for development environments. This document describes the secret storage strategy, access control, and rotation procedures.

## Secret Storage Locations

| Environment | Storage Location | Access Method |
|-------------|-----------------|---------------|
| Production | Azure Key Vault (`eduboost-v2-prod-kv`) | Managed Identity (ACA) |
| Staging | Azure Key Vault (`eduboost-v2-staging-kv`) | Managed Identity (ACA) |
| Local Development | `.env` file (gitignored) | File read |
| CI/CD | GitHub Actions Secrets | `${{ secrets.* }}` |

## Secrets Inventory

| Secret | Source | Production Storage |
|--------|--------|-------------------|
| `DATABASE_URL` | PostgreSQL | Azure Key Vault |
| `SECRET_KEY` | Generated | Azure Key Vault |
| `JWT_SIGNING_KEY` | Generated | Azure Key Vault |
| `REDIS_URL` | Azure Cache for Redis | Azure Key Vault |
| `SENTRY_DSN` | Sentry | Azure Key Vault |
| `STRIPE_API_KEY` | Stripe | Azure Key Vault |
| `ANTHROPIC_API_KEY` | Anthropic | Azure Key Vault |
| `GROQ_API_KEY` | Groq | Azure Key Vault |
| `AZURE_KV_URL` | Azure | Environment variable |
| `AZURE_CLIENT_ID` | Azure | Environment variable (Managed Identity) |

## Development `.env` File

The `.env` file is **not committed** to the repository. A template is provided at `.env.example` with placeholder values:

```
POSTGRES_PASSWORD=CHANGE_ME_devpassword
SECRET_KEY=CHANGE_ME_generate_a_strong_random_secret
```

All placeholder values use the `CHANGE_ME_` prefix to prevent accidental use in production.

## Access Control

- **Production Key Vault**: Access restricted to production ACA Managed Identity + Security Team Azure AD group
- **Staging Key Vault**: Access restricted to staging ACA Managed Identity + Developer Azure AD group
- **Local `.env`**: Developer's workstation

## Rotation Policy

- **JWT signing keys**: Rotated via `kid` mechanism in `app/core/token_config.py` (overlap window supported)
- **Database credentials**: Rotated on a schedule via Azure PostgreSQL flexible server rotation
- **API keys (LLM providers)**: Rotated immediately if compromised; otherwise per-provider schedule

## Emergency Procedure

If a secret is suspected compromised:
1. Rotate the affected secret in Azure Key Vault immediately
2. Update the application configuration to reference the new secret version
3. Restart affected services (ACA revision bump)
4. Document the incident in the security incident log
