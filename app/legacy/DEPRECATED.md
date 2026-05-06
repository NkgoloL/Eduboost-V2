# Legacy Runtime Archive

The V2 modular monolith is the sole supported runtime for EduBoost SA.

This directory keeps compatibility shims and archived legacy entrypoints so
older imports can fail gracefully instead of breaking abruptly during the V2
cutover.

Supported runtime:

- `app.api_v2:app`
- `docker compose up --build`

Compatibility only:

- `app.api.main`
- `/api/v1/lessons/generate` returns `410 Gone`

Do not add new product work under `app/legacy/`.
