# Legacy Test Archive

These tests target the retired pre-V2 runtime surface:

- `app.api.services.*`
- `app.api.ml.*`
- `app.api.constitutional_schema.*`
- Celery-first task orchestration
- broker-first audit plumbing

They are kept for historical reference while EduBoost SA runs exclusively on
the V2 modular monolith. The supported default pytest suite excludes this
directory through `pytest.ini`.
