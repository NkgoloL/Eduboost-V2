# Environment Configuration Contract

## Purpose

This contract defines configuration and secret-management expectations for staging and production environments.

## Required Staging Variables

- DATABASE_URL
- REDIS_URL
- APP_SECRET_KEY
- CORS_ORIGINS
- ENVIRONMENT
- LOG_LEVEL

## Required Production Variables

- DATABASE_URL
- REDIS_URL
- APP_SECRET_KEY
- CORS_ORIGINS
- ENVIRONMENT
- LOG_LEVEL
- SENTRY_DSN
- OTEL_EXPORTER_OTLP_ENDPOINT

## Required Environment Controls

- production debug must be disabled
- production TLS is required
- production secrets must be externalized
- staging secrets must be externalized
- database migrations must be controlled
- observability must be enabled
- placeholder secrets are prohibited
- local-only variables are forbidden in production

## Boundary

This contract records environment-configuration readiness. It does not expose secret values or configure live environments.
