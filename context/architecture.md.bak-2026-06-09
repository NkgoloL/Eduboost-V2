# Architecture

## Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Runtime | Python | 3.11+ |
| HTTP Framework | FastAPI | 0.104+ |
| Database | PostgreSQL | 15+ |
| ORM | SQLAlchemy | 2.0+ |
| Async Driver | asyncpg | 0.28+ |
| Validation | Pydantic | v2 |
| Testing | pytest | 7.4+ |
| AI/LLM | OpenAI GPT-4o | — |
| Frontend | React | 18+ |
| Monitoring | Prometheus | — |

## Folder Structure

```
app/
├── api_v2.py                    # FastAPI app entrypoint
├── api_v2_routers/              # HTTP routers by domain
│   ├── auth.py, ether.py, diagnostics.py, practice.py, study_plans.py, gamification.py, parent.py, admin.py
├── modules/                     # Business logic
│   ├── learners/, assessment/, practice/, study_plans/, content_factory/, gamification/
├── repositories/                # Data access layer
├── models/                      # SQLAlchemy ORM models
├── domain/                      # Domain entities & schemas
├── core/                        # Infrastructure (database, config, logging, security)
├── middleware/                  # FastAPI middleware
├── services/                    # Shared services
└── utils/                       # Utilities

tests/
├── api/                         # Router tests
├── modules/                     # Service tests
└── integration/                 # End-to-end tests
```

## Data Flow

1. **Request Flow:** Client HTTP → FastAPI Router → Service → Repository → Database → ORM → Domain → Response
2. **Diagnostic Session:** Start → Select item (IRT) → User responds → Update theta/SE → Check termination
3. **Practice Session:** Start → Select items (difficulty proximity + spaced rep) → User responds → Award points → Update mastery
4. **ETL Pipeline:** Upload → Parse → Extract items → Map to CAPS → Create artifacts → Review queue

## Database Schema (Core Tables)

- `learners` - learner profile
- `diagnostic_sessions` - assessment state and responses
- `learner_mastery` - topic mastery (theta, SE, status)
- `practice_items` - item pool
- `practice_sessions` - session tracking
- `study_plans` - study plan records
- `audit_logs` - POPIA compliance audit trail

## System Invariants

1. All learner data queries scoped to learner_id
2. IRT theta/SE always updated together, never stale
3. Mastery status only improves or stays same, never regresses
4. POPIA consent always checked before analytics
5. All database writes include audit logging
6. Items only served if review_status = 'approved'
7. No hardcoded secrets - config from env vars only
8. All async operations wrapped in try/catch
9. All responses wrapped in EnvelopedRoute
10. Practice items filtered by difficulty proximity (θ ± 0.3)
