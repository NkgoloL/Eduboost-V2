# Contributing to EduBoost SA

Thanks for showing up for this project. EduBoost handles learning data for
children, so our contribution bar is about correctness, empathy, and
compliance as much as shipping speed.

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

The default runtime is V2:

```bash
docker compose up --build
```

Useful URLs:

- Frontend: `http://localhost:3050`
- API docs: `http://localhost:8000/docs`
- MkDocs: `http://localhost:8001`
- Prometheus: `http://localhost:9090`

Legacy runtime paths are archived for compatibility only and must not receive
new feature work.

## Development Workflow

Use the TDD loop:

1. Add or update a failing test.
2. Implement the change in the V2 runtime.
3. Re-run the focused tests until green.
4. Run the POPIA sweep.
5. Update the audit tracking files for meaningful task batches.

Preferred package flow:

- router → service → repository
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

Coverage target: **80% minimum**. CI enforces the same floor for backend and
frontend gates.

## Dependency Updates

The pinned dependency locks are generated with `pip-compile`.

Update a lockfile like this:

```bash
pip-compile requirements/base.in -o requirements/base.txt
pip-compile requirements/dev.in -o requirements/dev.txt
pip-compile requirements/docs.in -o requirements/docs.txt
pip-compile requirements/ml.in -o requirements/ml.txt
```

The root wrapper files (`requirements.txt`, `requirements-dev.txt`,
`requirements-docs.txt`, `requirements-ml.txt`) exist for convenience and point
to the environment-specific lockfiles under `requirements/`.

## POPIA Rules

- Call `ConsentService.require_active_consent()` before learner-data access.
- Do not send real learner identifiers to LLM providers.
- Audit every consent mutation and erasure workflow.
- Run `python scripts/popia_sweep.py --fail-on-issues` before committing.

## Branching and Commits

- Use short, focused branches.
- Follow Conventional Commits.
- Keep unrelated cleanup out of feature commits.

Examples:

- `feat(auth): add refresh-token rotation`
- `fix(popia): gate learner export behind active consent`
- `docs(readme): reflect V2 GA runtime`

## Release Expectations

Before a release cut:

- all tests green
- POPIA sweep green
- `alembic check` green
- docs build clean with `mkdocs build --strict`
- CI green on `master`

If something is externally blocked, document it clearly rather than hand-waving it.
