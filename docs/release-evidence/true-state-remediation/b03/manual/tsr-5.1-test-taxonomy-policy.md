# TSR-5.1 Test Taxonomy and Marker Policy

## Taxonomy
- `unit`: Fast, isolated unit tests (<50ms, no network/DB)
- `integration`: DB/Redis backed integration tests
- `runtime`: Full stack readiness probe and live migrations
- `governance`: Release evidence and contract consistency checks
- `advisory`: Quality gates (Ruff, mypy, Bandit, audits)

## Review Metadata
- **Reviewer**: Nkgolo Lebelo (Lead Engineer, Self-Review)
- **Decision**: `completed`
- **Conflict Disclosure**: Self-review by sole developer; not independent approval.
