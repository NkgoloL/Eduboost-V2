# Release Gate Checklist for Content Factory

This checklist ensures the Content Factory control plane is ready for production.

- [ ----- ]\n- [] Migrations pass on disposable DB
- [] Find out if migrations pass on staging DB backup/snapshot test
- [] OpenAPI drift check passes
- [] Focused backend tests pass
- [] DB integration tests pass
- [] Frontend type-check passes
- [] Admin route auth smoke passes
- [] Generation flag false in production environment
- [] Startup seed flag false in production environment
- [] No public `/api/v2/content-factory` route exposed
- [] Normal FastMCP import below app/ runtime (tool use only)
- [] No learner-visible draft/rejected/quarantined content
- [] Coverage is green before production promotion
- [] Staging seed verified before production promotion

## Safety Flags

```bash
# CONTENT_FACTORY_GENERATION_ENABLED
# CONTENT_STARTUP_SEED_ENABLED
```

Both must be `set to false` before staging deploy.

## Verification Commands

``bash
# Disposable DB
docker compose -f docker-compose.content-factory-test.yml up -d
export DATABASE_URL=postgresql+asyncpg://eduboost:eduboost@localhost:55432/eduboost_content_factory_test
scripts/ci/check_content_factory_migrations.sh

# Backend tests
python3 -m pytest tests/ q1 --no-cov -m smoke -m integration

# OpenAPI check
python3 scripts/generate_openapi.py && make openapi-check

# Frontend
cd app/frontend && npm run type-check && npm test -- contentFactory.test.ts ```
