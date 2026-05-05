# EduBoost V2 Environment Variables

This document lists all environment variables required for the platform, their purpose, and security implications.

## ── Core Application ────────────────────────────────────────────────────────

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `APP_NAME` | No | `EduBoost SA` | Human-readable name. |
| `ENVIRONMENT` | Yes | `development` | `development`, `staging`, or `production`. |
| `APP_VERSION` | No | `2.0.0` | Semantic version of the release. |
| `DEBUG` | No | `False` | Enables verbose error messages and FastAPI docs. |

## ── Database & Persistence ──────────────────────────────────────────────────

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | SQLAlchemy URL (e.g. `postgresql+asyncpg://...`). |
| `REDIS_URL` | Yes | - | Redis connection string (e.g. `redis://...`). |

## ── Security & Authentication ───────────────────────────────────────────────

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET` | Yes | - | Secret key for signing JWTs (min 32 chars). |
| `ENCRYPTION_KEY` | Yes | - | 32-byte Base64 key for PII encryption at rest. |
| `ENCRYPTION_SALT` | Yes | - | Salt for derivation of PII keys. |

## ── AI & LLM Providers ───────────────────────────────────────────────────────

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes* | - | API key for Groq (Primary provider). |
| `ANTHROPIC_API_KEY` | Yes* | - | API key for Anthropic (Fallback provider). |

*At least one must be provided for lesson generation to function.*

## ── Observability ──────────────────────────────────────────────────────────

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SENTRY_DSN` | No | - | Sentry Data Source Name for error tracking. |
| `POSTHOG_API_KEY`| No | - | Analytics key for PostHog. |

## ── Infrastructure (Production) ─────────────────────────────────────────────

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AZURE_KEY_VAULT_URL` | Yes** | - | URL for Azure Key Vault (e.g. `https://vault.vault.azure.net`). |

**Required only in `production` environment.*
