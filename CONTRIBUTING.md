# Contributing to EduBoost SA

Thanks for contributing. EduBoost handles children’s learning and consent data,
so our bar is about correctness, clarity, and compliance as much as shipping
speed.

## Prerequisites

- Python 3.11+
- Node.js 20 LTS
- Docker Desktop with Compose v2
- Git 2.40+

## Environment Setup

```bash
git clone https://github.com/NkgoloL/Eduboost-V2.git
cd Eduboost-V2
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements/dev.txt
cd app/frontend && npm ci && cd ../..
```

Optional extras:

```bash
pip install -r requirements/docs.txt
pip install -r requirements/ml.txt --extra-index-url https://download.pytorch.org/whl/cpu
```

## Running the Stack

The default local runtime is the V2 stack:

```bash
docker compose up --build
```

Useful URLs:

- Frontend: `http://localhost:3050`
- API docs: `http://localhost:8000/docs`
- MkDocs: `http://localhost:8001`
- Prometheus: `http://localhost:9090`

Other compose files exist for explicit V2, ACA, and production-like scenarios.
If you are making a routine product change, start with the root Compose file.

Legacy paths remain only for compatibility and migration support. New feature
work should land in the V2 runtime surface.

## Development Workflow

Use a focused loop:

1. Add or update a failing test.
2. Implement the change in the active V2 surface.
3. Re-run the focused tests until green.
4. Run the POPIA sweep when learner-data handling is involved.
5. Update documentation when runtime, security, or operational behavior
   changes.

Preferred package flow:

- router -> service -> repository
- no direct DB logic in routers
- consent gating before learner-data access

## Testing

Backend:

```bash
pytest tests/ -v --tb=short
python scripts/popia_sweep.py --fail-on-issues
```

Frontend:

```bash
cd app/frontend
npm test
npm run test:coverage
npm run type-check
npm run lint
```

Documentation:

```bash
mkdocs build --strict
```

The current configured CI target is **80% minimum** for the coverage gates that
are enforced in workflow configuration.

## Dependency Updates

Pinned dependency locks are generated with `pip-compile`.

```bash
pip-compile requirements/base.in -o requirements/base.txt
pip-compile requirements/dev.in -o requirements/dev.txt
pip-compile requirements/docs.in -o requirements/docs.txt
pip-compile requirements/ml.in -o requirements/ml.txt
```

The root wrapper files (`requirements.txt`, `requirements-dev.txt`,
`requirements-docs.txt`, `requirements-ml.txt`) point to the environment-
specific lockfiles under `requirements/`.

## POPIA Rules

- Call `ConsentService.require_active_consent()` before learner-data access.
- Do not send real learner identifiers to LLM providers.
- Audit every consent mutation and erasure workflow.
- Run `python scripts/popia_sweep.py --fail-on-issues` before merging
  POPIA-sensitive changes.

## Docs and Audit Hygiene

When you change runtime behavior, also update the docs that describe it:

- [`README.md`](/README.md)
- [`SECURITY.md`](/SECURITY.md)
- [`docs/project_status.md`](/docs/project_status.md)
- [`docs/v2_migration.md`](/docs/v2_migration.md)
- root [`TODO.md`](/TODO.md) when an audit-tracked item changes state

The goal is one source of truth, not a pile of confident but stale markdown.

## Branching and Commits

- Use short, focused branches.
- Follow Conventional Commits.
- Keep unrelated cleanup out of feature commits.

Examples:

- `feat(auth): add refresh-token rotation`
- `fix(popia): gate learner export behind active consent`
- `docs(readme): sync runtime claims with repo state`

## Release Expectations

Before a release cut:

- all relevant tests green
- POPIA sweep green
- `alembic check` green
- docs build clean with `mkdocs build --strict`
- CI green on the release branch or target branch

If something is blocked, document the gap clearly rather than smoothing it over.
