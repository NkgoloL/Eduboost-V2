# Frontend Build Test Lint Contract

## Purpose

Cluster G frontend readiness requires explicit commands for dependency install,
static checks, unit tests, production build, and browser journey execution.

## Required Command Areas

- install frontend dependencies
- run frontend lint
- run frontend typecheck
- run frontend unit tests
- run frontend production build
- run frontend Playwright smoke
- run frontend Playwright mocked journeys
- run frontend accessibility static check

## Package Script Expectations

A frontend `package.json` should expose scripts for at least the following
capabilities when the frontend package is present:

- `build`
- `test`
- `lint`
- `typecheck`
- `dev` or `start`

## CI Boundary

The static evidence checks must pass even before the frontend package metadata is
fully normalized. Runtime build/test commands may be wired as opt-in until the
frontend package and server command are stable. Missing package scripts
are advisory until the frontend package location and scripts are canonical.

## Command

```bash
make frontend-build-test-lint-contract-check
```
