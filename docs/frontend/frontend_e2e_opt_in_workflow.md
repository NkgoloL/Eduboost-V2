# Frontend E2E Opt-In Workflow

## Purpose

The opt-in frontend E2E workflow runs browser journeys only when manually
triggered with an explicit frontend base URL and optional web server command.

## Workflow

- `.github/workflows/frontend-e2e-opt-in.yml`

## Inputs

- `frontend_base_url`
- `learner_path`
- `parent_path`
- `web_server_command`

## Commands

```bash
make frontend-e2e-mocked
make frontend-e2e-smoke
```

## Safety Boundary

The workflow must not run automatically on every pull request until the frontend
runtime is stable. It must not require production credentials, live learner
data, or live parent data.
