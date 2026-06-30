# EduBoost V2 End-to-End System Startup Guide

**Last Updated:** 2026-06-05  
**Status:** In Progress - System Startup Phase

## Architecture Overview

The EduBoost V2 system consists of:

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                    │
│              Port: 3000 (with dev server)               │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│              API Server (FastAPI)                       │
│              Port: 8000                                 │
│          (app.api_v2:app - canonical V2 surface)        │
└─────────────────────┬───────────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │Postgres │ │ Redis   │ │Supabase │
    │ Port    │ │ Port    │ │Services │
    │ 54322   │ │ 6379    │ │ 54321   │
    └─────────┘ └─────────┘ └─────────┘
```

## System Status

### ✅ Currently Running

- **Supabase Local Development Stack**: Running
  - PostgreSQL: `postgresql://postgres:postgres@127.0.0.1:54322/postgres`
  - Studio: http://127.0.0.1:54323
  - REST API: http://127.0.0.1:54321/rest/v1
  - Project URL: http://127.0.0.1:54321

### 🔄 In Progress

- **Unit Tests**: Running in background (tests/unit suite)
- **Test Fixes**: 
  - ✅ Fixed syntax error in `tests/unit/test_seed_staging_review_scopes.py`
  - ✅ Architecture boundaries verified (lint-imports passing)

### ⏳ Next Steps

1. **API Server**: Start FastAPI backend
2. **Frontend**: Start Next.js development server  
3. **Ingestion Pipeline**: Run outstanding CAPS acquisition phases
4. **System Health**: Run end-to-end smoke tests

## Startup Sequence

### Step 1: Backend API Service

```bash
cd /home/azureuser/Dev/SandBox/ml/Eduboost-V2

# Activate venv
source .venv/bin/activate

# Run migrations
alembic upgrade head

# Start API server (development mode)
uvicorn app.api_v2:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Health check: `curl http://localhost:8000/ready`

### Step 2: Frontend Development Server

```bash
cd /home/azureuser/Dev/SandBox/ml/Eduboost-V2/app/frontend

# Install dependencies (one-time)
pnpm install --frozen-lockfile

# Start dev server
pnpm dev
```

Expected output:
```
➜  Local:   http://localhost:3000
```

### Step 3: Ingestion Pipeline Execution

After both services are running, trigger the CAPS acquisition pipeline:

```bash
cd /home/azureuser/Dev/SandBox/ml/Eduboost-V2

# Run CAPS source acquisition phases
python3 scripts/curriculum/resolve_dbe_caps_urls.py
python3 scripts/curriculum/download_caps_sources.py
python3 scripts/curriculum/extract_caps_source_text.py
python3 scripts/curriculum/build_topic_map_worklist.py
python3 scripts/curriculum/scaffold_topic_map_drafts.py
python3 scripts/curriculum/validate_topic_maps.py
```

## Outstanding Ingestion Pipeline Phases

Per `../caps/caps_source_acquisition_plan_v2.md`:

| Phase | Component | Status | Blocker | Action |
|-------|-----------|--------|---------|--------|
| Source URLs | resolve_dbe_caps_urls.py | ✅ Complete | None | Already implemented |
| Source Files | download_caps_sources.py | ✅ Complete | None | Verify hashes |
| Text Extraction | extract_caps_source_text.py | ✅ Complete | None | Verify completeness |
| Topic Maps | build_topic_map_worklist.py | 🔄 In Progress | Topic validation | Review draft maps |
| Validation | validate_topic_maps.py | 🔄 In Progress | Schema compliance | Run gates |
| Generation Ready | Scope status promotion | ⏳ Blocked | Map approval | Requires human review |

## Environment Variables

Create `.env` file at project root (already should be set up via Supabase):

```bash
# API Configuration
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:54322/postgres
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-dev-secret-key

# Supabase
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_ANON_KEY=<your-supabase-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-supabase-service-role-key>
```

## Health Checks

### API Health

```bash
# Readiness check
curl http://localhost:8000/ready

# Full health
curl http://localhost:8000/health/deep

# OpenAPI docs
curl http://localhost:8000/docs
```

### Database Health

```bash
# PostgreSQL
psql -h 127.0.0.1 -p 54322 -U postgres -d postgres -c "SELECT version();"

# Redis
redis-cli -p 6379 PING
```

### Frontend Health

```bash
# Check if running
curl http://localhost:3000

# Frontend logs should show:
# - Next.js dev server ready
# - Routes compiled
```

## Ingestion Pipeline Health

```bash
# After starting API, trigger pipeline status check:
curl -X GET http://localhost:8000/api/v2/pipeline/status

# Expected response:
{
  "status": "healthy",
  "total_documents": 23,
  "documents_by_status": {
    "source_loaded": 23,
    "topic_map_approved": 0,
    "generation_ready": 0
  },
  "pending_actions": [...]
}
```

## Troubleshooting

### Supabase Connection Issues

```bash
# Check Supabase status
supabase status

# Restart if needed
supabase stop
supabase start
```

### Frontend Build Issues

```bash
# Clear node_modules and lockfile
cd app/frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install --frozen-lockfile
```

### API Connection Issues

```bash
# Check if port is in use
lsof -i :8000

# Check environment
source .venv/bin/activate
python -c "from app.core.config import settings; print(settings.DATABASE_URL)"
```

## Next Phases After System Start

1. **Run Full System Smoke Tests** - `make test-e2e-opt-in-workflow`
2. **Execute CAPS Ingestion** - Run all phases of the acquisition pipeline
3. **Validate Topic Maps** - Human review and approval of generated maps
4. **Generate Content** - Trigger lesson generation for approved topics
5. **Import to Database** - Populate learner-visible content
6. **Beta Readiness** - Run final release checklist

## Performance Baseline

Expected startup times:

- Supabase: 30-60s (already running)
- API: 5-10s
- Frontend: 10-15s  
- Full system ready: ~1 minute

## Monitoring & Logs

```bash
# API logs (when running)
# Watch http://localhost:8000/metrics for Prometheus metrics

# Frontend logs (when running)
# Check browser console at http://localhost:3000

# Supabase logs
supabase logs --follow
```

## References

- Architecture: [docs/architecture.md](docs/architecture.md)
- CAPS Plan: [../caps/caps_source_acquisition_plan_v2.md](../caps/caps_source_acquisition_plan_v2.md)
- Data Generator TODO: [../todos/data_generator_todo.md](../todos/data_generator_todo.md)
- Roadmap: [../roadmap/roadmap.md](../roadmap/roadmap.md)
- TODO: [../todos/todo.md](../todos/todo.md)

---

**Generated:** 2026-06-05  
**By:** System Startup Automation  
**Status:** Active Implementation
