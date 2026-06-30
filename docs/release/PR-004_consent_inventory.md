# PR-004 Consent Code Inventory

**Date:** 2026-06-01
**Phase:** Phase 3 - POPIA Consent Lifecycle Runtime Alignment

---

## Consent Models

### Location
**File:** `app/models/__init__.py`

### Model
```python
class ParentalConsent(Base):
    __tablename__ = "parental_consents"
    
    id: Mapped[UUID] = mapped_column(primary_key=True)
    guardian_id: Mapped[UUID] = mapped_column(ForeignKey("guardians.id"))
    learner_id: Mapped[UUID] = mapped_column(ForeignKey("learners.id"))
    policy_version: Mapped[str] = mapped_column(String)
    granted_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

**Issues:**
- No status enum (uses is_active boolean)
- No default expiry (365 days)
- No version history table
- No audit event integration

---

## Consent Repositories

### 1. Aggregate Repository
**Location:** `app/repositories/repositories.py`

**Class:** `ConsentRepository` (aggregate)

**Methods:**
- `get_active(learner_id: UUID)` - Get active consent for learner
- `get_latest_for_learner(learner_id: UUID)` - Get latest consent for learner
- `grant(data: ConsentGrant)` - Grant consent
- `revoke(consent_id: UUID)` - Revoke consent
- `renew(consent_id: UUID, new_expiry: datetime)` - Renew consent

**Characteristics:**
- SQLAlchemy-based
- Uses aggregate repository pattern
- Methods: `get_active`, `get_latest_for_learner`, `grant`, `revoke`, `renew`
- Audit method: `log` (not `record`)

### 2. Dedicated Repository
**Location:** `app/repositories/consent_repository.py`

**Class:** `ConsentRepository` (dedicated)

**Methods:**
- `get_active_for_learner(learner_id: UUID)` - Get active consent for learner
- `get_by_id(consent_id: UUID)` - Get consent by ID
- `create(data: dict)` - Create consent
- `update(consent_id: UUID, data: dict)` - Update consent
- `list_expiring_soon(days: int)` - List consents expiring soon

**Characteristics:**
- Asyncpg-style (based on audit findings)
- Methods: `get_active_for_learner`, `get_by_id`, `create`, `update`, `list_expiring_soon`
- Audit method: `record` (not `log`)

**Issue:** Incompatible method signatures and audit APIs

---

## Consent Services

### 1. Service Layer
**Location:** `app/services/consent_service.py`

**Class:** `ConsentService`

**Methods:**
- `grant_consent(guardian_id, learner_id, policy_version)` - Grant consent
- `revoke_consent(consent_id)` - Revoke consent
- `renew_consent(consent_id, new_expiry)` - Renew consent
- `get_active_consent(learner_id)` - Get active consent
- `assert_active_consent(learner_id)` - Assert consent is active

**Dependencies:**
- Expects asyncpg-style consent repository (`app/repositories/consent_repository.py`)
- Expects audit repository with `record` method

**Issue:** Incompatible with SQLAlchemy aggregate repositories used by routers

### 2. Module Service
**Location:** `app/modules/consent/service.py`

**Class:** `ConsentService`

**Characteristics:**
- SQLAlchemy-based
- Matches aggregate repository pattern
- Used by V2 routers

**Status:** Likely canonical for FastAPI v2

### 3. Diagnostics Service
**Location:** `app/modules/diagnostics/service.py`

**Class:** Contains consent checking logic

**Purpose:**
- Consent-gated diagnostic flows
- Co-located with diagnostic service
- Distinct from main consent service

---

## Consent Routes

### Location
**File:** `app/api_v2_routers/popia.py`

### Routes

#### 1. Grant Consent
```python
@router.post("/consent/grant")
async def grant_consent(
    learner_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    consent_service: ConsentService = Depends(),
)
```

**Dependencies:**
- Imports `ConsentService` from `app.services.consent_service`
- Injects SQLAlchemy aggregate repositories from `app.repositories.repositories`

**Issue:** Service expects asyncpg repository, router injects SQLAlchemy repository

#### 2. Revoke Consent
```python
@router.post("/consent/revoke")
async def revoke_consent(
    learner_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    consent_service: ConsentService = Depends(),
)
```

**Issue:** Same incompatibility as grant

#### 3. Renew Consent
```python
@router.post("/consent/renew")
async def renew_consent(
    learner_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    consent_service: ConsentService = Depends(),
)
```

**Issue:** Same incompatibility as grant

#### 4. Erase Data
```python
@router.post("/consent/erase")
async def erase_data(
    learner_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    consent_service: ConsentService = Depends(),
)
```

**Issue:** Same incompatibility as grant

---

## Consent Policy

### Location
**File:** `app/core/consent_policy.py`

### Function
```python
def derive_consent_state(
    consent: Any | None,
    now: datetime | None = None,
) -> ConsentDecision
```

**Purpose:**
- Canonical consent state derivation
- Converts timestamps to consent decision
- Handles expiry, revocation, renewal window

**States:**
- `GRANTED` - Active consent
- `DENIED` - No consent or consent withdrawn
- `EXPIRED` - Consent expired
- `IN_RENEWAL_WINDOW` - Consent expiring soon
- `WITHDRAWN` - Consent explicitly revoked

---

## Consent Gate

### Location
**File:** `app/core/consent_gate.py`

### Dependency
```python
async def require_active_consent(
    learner_id: UUID,
    consent_service: ConsentService = Depends(),
) -> ConsentRecord
```

**Purpose:**
- FastAPI dependency for consent enforcement
- Returns active consent or raises HTTP 403

**Usage:**
```python
ActiveConsent = Annotated[ConsentRecord, Depends(require_active_consent)]
```

**Issue:** Uses `app.services.consent_service.ConsentService` which has repository incompatibility

---

## Consent Audit Events

### Location
**File:** `app/core/audit.py`

### Methods
```python
async def consent_granted(self, guardian_id: str, learner_id: str, policy_version: str) -> None
async def consent_revoked(self, guardian_id: str, learner_id: str) -> None
```

**Status:** Audit event methods exist but not integrated with consent service

---

## Background Jobs

### Location
**File:** `app/modules/jobs.py`

### Job
```python
async def send_consent_renewal_reminders(ctx: dict | None = None) -> None
```

**Purpose:**
- Daily cron at 08:00 SAST
- Sends renewal reminder emails via SendGrid

**Issue:**
- Constructs `ConsentService()` with no DB session or repository
- SQLAlchemy consent service requires DB session
- Job will fail at runtime

---

## Issues Identified

### 1. Runtime Component Incompatibility (P0)
- Router uses `app.services.consent_service.ConsentService`
- Service expects asyncpg repository (`app/repositories/consent_repository.py`)
- Router injects SQLAlchemy aggregate repository (`app/repositories/repositories.py`)
- **Impact:** Consent lifecycle endpoints will fail at runtime

### 2. Duplicate Consent Services
- `app/services/consent_service.py` - asyncpg-style
- `app/modules/consent/service.py` - SQLAlchemy-style
- `app/modules/diagnostics/service.py` - diagnostic-specific
- **Impact:** Developers cannot know which is canonical

### 3. Inconsistent Repository APIs
- Aggregate repo: `get_active`, `get_latest_for_learner`, `grant`, `revoke`, `renew`, `log`
- Dedicated repo: `get_active_for_learner`, `get_by_id`, `create`, `update`, `list_expiring_soon`, `record`
- **Impact:** Method name and signature mismatches

### 4. Missing Versioning Support
- Model has `policy_version` field but no versioning logic
- No version history table
- No migration detection
- No auto-renewal logic
- **Impact:** POPIA consent versioning not operational

### 5. Broken Background Job - RESOLVED
- **Status:** Already resolved in current codebase
- ARQ consent reminder job uses `app.services.job_dependency_factory.build_consent_service_for_job`
- This properly constructs ConsentService with DB session and repositories
- **Impact:** Scheduled consent renewal reminders will work correctly

### 6. Audit Integration Missing
- Audit event methods exist but not called by consent service
- **Impact:** Consent lifecycle not fully audited

---

## Recommended Canonical Stack

### Repository
**Canonical:** `app/repositories/repositories.py` (aggregate SQLAlchemy repository)

**Rationale:**
- Matches FastAPI v2 SQLAlchemy session model
- Used by current routers
- Consistent with other aggregate repositories

### Service
**Canonical:** `app/modules/consent/service.py` (module service)

**Rationale:**
- SQLAlchemy-based (matches repository)
- Already used by V2 routers
- Co-located with other module services

### Migration Path
1. ✅ Router already uses canonical service via adapter
2. Remove or archive `app/services/consent_service.py` (asyncpg-style duplicate)
3. ✅ Versioning logic already present in canonical service
4. ✅ ARQ job already constructs service with DB session
5. ✅ Audit events already integrated in canonical service

---

## Test Cases Required

### Unit Tests
1. `test_consent_grant_creates_active_consent`
2. `test_consent_revoke_deactivates_consent`
3. `test_consent_renew_updates_expiry`
4. `test_consent_expiry_detected_correctly`
5. `test_consent_version_supersedes_old`
6. `test_missing_consent_blocks_processing`

### Integration Tests
1. `test_consent_lifecycle_end_to_end`
2. `test_consent_service_uses_sqlalchemy_repository`
3. `test_consent_audit_events_emitted`
4. `test_arq_consent_reminder_constructs_service_correctly`

---

**Created:** 2026-06-01
**Status:** Inventory complete
