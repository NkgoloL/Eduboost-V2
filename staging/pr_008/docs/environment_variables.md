# Environment Variables

`.env.example` is the canonical template. Production values must come from Azure Key Vault or an equivalent managed secret store, not from committed files.

| Variable | Scope | Required | Sensitive | Notes |
|---|---|---:|---:|---|
| `APP_ENV` | all | yes | no | `development`, `test`, `staging`, or `production` |
| `APP_VERSION` | all | yes | no | Release/build version |
| `ALLOWED_ORIGINS` | all | yes | no | No wildcard in staging/production |
| `DATABASE_URL` | all | yes | yes | Async SQLAlchemy URL |
| `SYNC_DATABASE_URL` | migration | yes | yes | Sync URL for Alembic/operator tools |
| `REDIS_URL` | all | yes | yes | Redis cache/session URL |
| `JWT_SECRET` | all | yes | yes | Minimum 32 chars outside tests |
| `ENCRYPTION_KEY` | all | yes | yes | 32-byte base64 field-encryption key |
| `ENCRYPTION_SALT` | all | yes | yes | KDF/audit salt material |
| `AUDIT_HMAC_SECRET` | staging/prod | yes | yes | Tamper-evident audit signatures |
| `BACKUP_ENCRYPTION_KEY` | staging/prod | yes | yes | Backup encryption passphrase/material |
| `AZURE_KEY_VAULT_URL` | staging/prod | yes | no | Managed secret source |
| `SENTRY_DSN` | staging/prod | yes | yes-ish | Error telemetry endpoint |
| `GROQ_API_KEY` | optional | no | yes | LLM provider |
| `ANTHROPIC_API_KEY` | optional | no | yes | LLM fallback provider |
| `SENDGRID_API_KEY` | optional | no | yes | Email provider |
| `STRIPE_SECRET_KEY` | optional | no | yes | Billing provider |
| `NEXT_PUBLIC_API_URL` | frontend | yes | no | Browser-visible API URL |
| `NEXT_PUBLIC_SENTRY_DSN` | frontend | no | no | Browser-visible Sentry DSN |

Validate environment readiness:

```bash
python scripts/validate_runtime_env.py --env staging --env-file .env.staging
```
