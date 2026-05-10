# AI Prompt Secret Leakage Guard

## Purpose

Prompt-bearing string literals must not explicitly embed secret-bearing
configuration names.

This guard allows normal runtime configuration code to reference secret
environment variable names. It fails only when a prompt-like string literal
contains a secret marker.

## Secret Markers

- `JWT_SECRET`
- `JWT_SECRET_KEY`
- `ENCRYPTION_KEY`
- `ENCRYPTION_SALT`
- `BACKUP_ENCRYPTION_KEY`
- `GROQ_API_KEY`
- `ANTHROPIC_API_KEY`
- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_KEY_VAULT_URL`

## Prompt Surface Markers

- prompt
- system message
- user message
- lesson generation
- diagnostic generation
- remediation generation

## Command

```bash
make ai-prompt-secret-leakage-check
```
