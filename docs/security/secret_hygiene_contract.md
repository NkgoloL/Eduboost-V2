# Secret Hygiene Contract

## Purpose

This contract defines secret scanning, exposure, and rotation requirements.

## Required Secret Hygiene Rules

- API keys and tokens are detected
- private keys are detected
- password-like assignments are detected
- secret exposure blocks commit or merge
- exposed secrets require rotation
- secret scan evidence is retained
- production secrets are externalized
- placeholder secrets are rejected in production
- raw secret values must not be logged

## Boundary

This contract records secret hygiene readiness. It does not rotate secrets or expose secret values.
