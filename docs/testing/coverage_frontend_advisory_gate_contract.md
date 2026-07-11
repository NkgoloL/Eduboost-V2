# Coverage, Frontend Quality, and Advisory Gate Contract

**PRD:** PRD-11.0R.RUNTIME-RESTORE-5
**Status:** Authority contract
**Last reviewed:** 2026-07-10T22:55:00+00:00

This contract converts the PRD-11.3R coverage definition and the PRD-11.1R/11.2R taxonomy into executable release-blocking advisory gates.

## Release-blocking gate families

1. **Coverage execution** — a fresh coverage report must be generated from current code, failure exits must be preserved, and the documentation-defined threshold must be met.
2. **Frontend quality** — lint, Vitest, and production build must pass from independent command output.
3. **Advisory/static quality** — Ruff, mypy, Bandit, dependency audits, generated contracts, and secret-baseline review must be independently executed and recorded.
4. **Generated contract drift** — OpenAPI and route inventory checks must be read-only and clean.
5. **Dependency/security audit** — Python and frontend audits must resolve and produce reviewable outputs.
6. **Secret baseline** — scan output and baseline review must be small enough to be human-reviewable, with blockers recorded when not green.

Presence-only evidence and governance substitution are forbidden as release evidence.

This PRD slice records the command contracts and keeps all green-state booleans false until actual independent command outputs pass.
