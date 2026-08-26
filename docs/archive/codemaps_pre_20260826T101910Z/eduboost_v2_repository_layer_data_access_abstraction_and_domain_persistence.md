# EduBoost V2 Repository Layer: Data Access Abstraction & Domain Persistence

Maps the repository pattern implementation across domain-specific persistence classes that encapsulate PostgreSQL access using async SQLAlchemy and specialized asyncpg paths. Key entry points include base repository CRUD [1b], learner creation persistence [2c], audit event hash chaining [3d], POPIA consent access gating [4e], diagnostic session state tracking [5c], item exposure tracking [6e], repository factory resolution [7c], and service-layer repository composition [8f].

## Trace ID: 1
**Title:** Base Repository Generic CRUD Operations

**Description:** Foundation pattern providing async CRUD for domain aggregates, used by specialized repositories.

**Motivation:**
EduBoost V2 uses repositories to keep persistence concerns separate from service and API logic. The generic BaseRepository gives domain repositories a consistent async CRUD foundation, reducing repeated SQLAlchemy boilerplate while preserving type safety through Python generics.

This matters because many modules need the same operations—get by ID, create, update, and delete—but the business meaning of each entity belongs outside the database abstraction. A shared base keeps persistence predictable while allowing specialized repositories to add domain queries.

**Details:**

**Generic Repository Contract**
The BaseRepository[ModelT] class [1a] binds a repository instance to a SQLAlchemy ORM model. Its methods operate on model classes rather than hardcoded tables, giving concrete repositories inherited behavior once they define their model type.

**Read Path**
The get(id, db) method executes an async SQLAlchemy select [1b] and returns scalar_one_or_none(). This provides a consistent optional-return pattern: callers receive either a model instance or None without having to inspect raw result sets.

**Create Path**
The create(db, **kwargs) method [1c] constructs an ORM instance from keyword arguments, adds it to the session, flushes the transaction [1d], then refreshes the instance. The flush persists enough state to generate IDs without committing the outer transaction, leaving commit/rollback ownership to the request or service boundary.

**Specialization Pattern**
Domain repositories such as GuardianRepository inherit the base CRUD behavior [1e] and add domain-specific methods like get_by_email_hash(). This keeps generic persistence mechanics in the base class while lookup logic tied to authentication remains in the auth repository.

**Trace text diagram:**
```text
Base Repository Pattern
├── BaseRepository[ModelT] class <-- 1a
│   ├── async get(id, db) <-- base.py:23
│   │   └── db.execute(select...) <-- 1b
│   │       └── return scalar_one_or_none() <-- base.py:25
│   ├── async create(db, **kwargs) <-- 1c
│   │   ├── instance = self.model(**kwargs) <-- base.py:51
│   │   ├── db.add(instance) <-- base.py:52
│   │   ├── db.flush() <-- 1d
│   │   └── db.refresh(instance) <-- base.py:54
│   ├── async update(instance, db, **kwargs) <-- base.py:57
│   └── async delete(instance, db) <-- base.py:65
└── Specialized Repositories
    └── GuardianRepository(BaseRepository) <-- 1e
        ├── inherits: get, create, update, delete
        └── adds: get_by_email_hash() <-- auth_repository.py:21
```

**Location ID: 1a**
- **Title:** Generic Repository Base
- **Description:** Type-safe base class for all repositories
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:18

**Location ID: 1b**
- **Title:** Async Query Execution
- **Description:** SQLAlchemy async select with type-safe model reference
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:24

**Location ID: 1c**
- **Title:** Generic Create Operation
- **Description:** Instantiate model, add to session, flush for ID
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:50

**Location ID: 1d**
- **Title:** Transaction Flush
- **Description:** Persist to DB without committing transaction
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/base.py:53

**Location ID: 1e**
- **Title:** Specialized Repository Inheritance
- **Description:** Guardian repository extends base with domain methods
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/auth_repository.py:16

### AI Guide: Base Repository Generic CRUD Operations

**Motivation:**
The base repository exists to standardize common persistence operations across EduBoost's domain model. It prevents each repository from re-implementing the same SQLAlchemy create/read/update/delete mechanics and makes repository behavior easier for agents and developers to predict.

**Details:**

**Type-Safe Base Pattern**
BaseRepository[ModelT] [1a] is a generic abstraction. Concrete repositories bind ModelT to a specific ORM model, which allows inherited methods to work with that model while keeping method signatures explicit.

**Flush Without Commit**
The create path flushes [1d] instead of committing. This is an important invariant: repositories stage and persist changes inside the current transaction, but they do not decide transaction boundaries. Route dependencies or services decide when to commit or roll back.

**Domain Extension Points**
Specialized repositories should inherit common CRUD where possible and add only queries that are meaningful to their domain. GuardianRepository [1e] demonstrates this by keeping auth-specific lookup behavior near the guardian persistence model.

## Trace ID: 2
**Title:** Learner Creation Flow: API → Repository → Database

**Description:** End-to-end trace showing how learner creation flows from API route through repository to persistence.

**Motivation:**
Learner creation is a core onboarding operation. The repository layer must convert validated API input into durable PostgreSQL records while keeping the route handler thin and preserving transaction control through the injected AsyncSession.

This flow demonstrates the application boundary between transport, persistence, and serialization: FastAPI receives the request, the repository persists the domain record, and Pydantic serializes the resulting ORM model into a response.

**Details:**

**Route Entry Point**
The POST /learners route receives an injected database session and current user context. It instantiates LearnerRepository(db) [2a], keeping data access behind a repository instead of embedding SQLAlchemy operations directly in the handler.

**Repository Create Call**
The route calls repo.create(...) [2b] with learner data derived from the request body and guardian context. The repository constructs a LearnerProfile model [2c], stages it in the session [2d], and flushes [2e] so PostgreSQL generates an ID.

**Response Serialization**
After persistence, LearnerResponse.model_validate() [2f] converts the ORM model into the API response contract. This isolates the client-facing schema from internal SQLAlchemy implementation details.

**Transaction Boundary**
The repository flushes but does not commit. The surrounding FastAPI database dependency controls commit/rollback, ensuring that learner creation participates in the same request-scoped transaction as any related operations.

**Trace text diagram:**
```text
Learner Creation Flow (API → Repository → DB)
│
├── POST /learners API Route Handler <-- learners.py:24
│   ├── Inject DB session from FastAPI <-- learners.py:27
│   ├── repo = LearnerRepository(db) <-- 2a
│   ├── await repo.create(...) <-- 2b
│   │   │
│   │   └── LearnerRepository.create() <-- repositories.py:62
│   │       ├── learner = LearnerProfile(**kwargs) <-- 2c
│   │       ├── self.db.add(learner) <-- 2d
│   │       └── await self.db.flush() <-- 2e
│   │           └── SQLAlchemy persists to PostgreSQL
│   │               └── Returns model with ID <-- repositories.py:66
│   │
│   └── return LearnerResponse.model_validate() <-- 2f
│       └── Pydantic serializes ORM → JSON
```

**Location ID: 2a**
- **Title:** Repository Instantiation in Route
- **Description:** Create repository with injected database session
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:30

**Location ID: 2b**
- **Title:** Repository Create Call
- **Description:** Invoke repository method with domain data
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:31

**Location ID: 2c**
- **Title:** Model Instantiation
- **Description:** Create SQLAlchemy model from kwargs
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:63

**Location ID: 2d**
- **Title:** Add to Session
- **Description:** Stage model for persistence in transaction
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:64

**Location ID: 2e**
- **Title:** Flush Transaction
- **Description:** Persist to database and generate ID
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:65

**Location ID: 2f**
- **Title:** Response Serialization
- **Description:** Convert ORM model to Pydantic response
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/learners.py:37

### AI Guide: Learner Creation Flow

**Motivation:**
This flow shows the clean request-to-persistence path that new repository-backed endpoints should follow. It keeps the API route focused on orchestration and response shaping while the repository owns model construction and persistence.

**Details:**

**API Boundary**
The route obtains a session and creates the repository [2a]. This makes repository usage request-scoped and avoids sharing AsyncSession instances across concurrent requests.

**Persistence Boundary**
The repository create call [2b] stages and flushes the LearnerProfile [2c][2d][2e]. Because the repository does not commit, this flow remains composable with additional operations in the same request.

**Serialization Boundary**
The response model [2f] gives the API a stable contract even if ORM internals change. Future learner fields should be exposed intentionally through Pydantic, not by returning raw ORM state.

## Trace ID: 3
**Title:** Audit Repository Append-Only Chain with Hash Verification

**Description:** Security-critical audit logging with cryptographic chain verification for tamper evidence.

**Motivation:**
EduBoost handles learner data, guardian consent, authentication events, and compliance workflows, so the audit log must be trustworthy. The audit repository implements an append-only hash chain so audit records can later be checked for tampering.

This is especially important for POPIA accountability: compliance teams need evidence that events were recorded in order and were not silently modified after the fact.

**Details:**

**Append Entry Point**
record() [3a] is the audit append entry point. It validates the payload, fetches the latest hash [3b], computes the new event hash [3c], signs the event with HMAC [3d], and stages the audit event for persistence [3e].

**Hash Chain Construction**
Each event includes a pointer to the previous event hash. The event hash is computed from canonical JSON so equivalent payloads produce deterministic digests, while the HMAC binds the current hash to the previous hash using a secret.

**Tamper Verification**
verify_chain() reads events in order and recomputes expected hashes. If stored values differ from recomputed values, chain verification records an error [3f]. This detects modified payloads, broken previous-hash links, or invalid signatures.

**Security Properties**
The audit repository is append-oriented: callers add events rather than editing history. Tamper evidence depends on stable canonicalization, secret HMAC material, and consistent ordering by creation timestamp.

**Trace text diagram:**
```text
Audit Repository Append-Only Chain
├── record() entry point <-- 3a
│   ├── _latest_hash() fetch chain tail <-- 3b
│   │   └── SELECT event_hash ORDER BY created_at <-- audit_repository.py:388
│   ├── _compute_hash() SHA-256 <-- 3c
│   │   └── hashlib.sha256(canonical_json) <-- audit_repository.py:66
│   ├── _compute_hmac() signature <-- 3d
│   │   └── hmac.new(secret, event_hash:prev) <-- audit_repository.py:72
│   └── self._db.add(event) persist <-- 3e
│       └── INSERT INTO audit_events <-- audit_repository.py:148
└── verify_chain() integrity check <-- audit_repository.py:292
    ├── SELECT all events ORDER BY created_at <-- audit_repository.py:314
    └── for each row: <-- audit_repository.py:324
        ├── recompute expected_hash <-- audit_repository.py:352
        └── if mismatch: errors.append() <-- 3f
```

**Location ID: 3a**
- **Title:** Audit Record Entry Point
- **Description:** Append audit event with automatic hash chaining
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/audit_repository.py:98

**Location ID: 3b**
- **Title:** Retrieve Chain Tail
- **Description:** Fetch previous event hash for chain linking
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/audit_repository.py:120

**Location ID: 3c**
- **Title:** Compute Event Hash
- **Description:** SHA-256 of canonical JSON payload
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/audit_repository.py:129

**Location ID: 3d**
- **Title:** HMAC Signature Generation
- **Description:** Cryptographic signature linking to previous event
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/audit_repository.py:130

**Location ID: 3e**
- **Title:** Persist Audit Event
- **Description:** Add chained event to append-only log
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/audit_repository.py:144

**Location ID: 3f**
- **Title:** Chain Verification
- **Description:** Detect tampering by recomputing hashes
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/audit_repository.py:355

### AI Guide: Audit Repository Append-Only Chain

**Motivation:**
The audit repository provides tamper-evident persistence for compliance events. It exists because ordinary database rows can be edited without obvious evidence unless the application adds its own integrity chain.

**Details:**

**Append-Only Event Recording**
record() [3a] builds each event from the previous chain tail [3b]. This creates an ordered audit history where every new event depends cryptographically on the event before it.

**Cryptographic Integrity**
The repository computes both a SHA-256 event hash [3c] and an HMAC signature [3d]. The hash detects payload changes, while the HMAC protects against attackers who can recompute hashes but do not know the secret.

**Verification Workflow**
verify_chain() recomputes event hashes and signatures, adding mismatches to an error list [3f]. Run this during audits, incident response, or release verification when audit-log integrity matters.

## Trace ID: 4
**Title:** Consent Repository POPIA Compliance Flow

**Description:** Parental consent lifecycle management with active consent validation for learner data access.

**Motivation:**
EduBoost processes children's educational data, so learner access must be guarded by active parental consent. The repository layer supports POPIA compliance by persisting consent grants, revocations, and active-consent checks used by API dependencies.

This flow ensures that learner data access is not merely a frontend convention; it is enforced server-side before protected data can be returned.

**Details:**

**Active Consent Gate**
The API dependency require_active_consent() [4a] asks the consent repository for active consent [4b]. If no active record exists, the dependency raises ConsentRequiredError [4e], blocking learner data access with an HTTP 403 response.

**Grant Persistence**
ConsentRepository.grant() creates a ParentalConsent record [4c] containing learner, guardian, policy version, IP/user-agent metadata, and granted state. This records which guardian consented and which policy version was accepted.

**Revocation Persistence**
ConsentRepository.revoke() updates existing consent records [4d] to withdrawn status and sets revoked_at. This creates a durable state change that future active-consent queries should not treat as valid consent.

**Compliance Boundary**
The repository stores consent facts, while dependencies and services enforce decisions. This separation makes it possible to audit consent state independently from the API routes that depend on it.

**Trace text diagram:**
```text
POPIA Consent Compliance Flow
├── API Route Dependency Injection
│   └── require_active_consent() gate <-- 4a
│       └── repo.get_active(learner_id, db) <-- dependencies.py:80
│           └── ConsentRepository <-- consent_repository.py:17
│               └── fetchrow() query <-- 4b
│                   └── SELECT * FROM consent_records <-- consent_repository.py:25
│                       WHERE learner_id = $1
│                       ORDER BY created_at DESC
├── Consent Grant Flow
│   └── ConsentRepository.grant() <-- repositories.py:160
│       └── ParentalConsent() instantiation <-- 4c
│           └── INSERT INTO parental_consents <-- repositories.py:176
│               ├── learner_id, guardian_id <-- repositories.py:170
│               ├── policy_version <-- repositories.py:172
│               └── status='granted' <-- repositories.py:174
├── Consent Revocation Flow
│   └── ConsentRepository.revoke() <-- repositories.py:180
│       └── UPDATE parental_consents <-- 4d
│           └── SET status='withdrawn',
│               revoked_at=NOW()
└── Access Control Enforcement
    └── if consent is None <-- dependencies.py:82
        └── raise ConsentRequiredError() <-- 4e
            └── HTTP 403 blocks learner data access
```

**Location ID: 4a**
- **Title:** Active Consent Check
- **Description:** Dependency injection gate for learner routes
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/dependencies.py:80

**Location ID: 4b**
- **Title:** Query Active Consent
- **Description:** Fetch latest consent record for learner
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/consent_repository.py:24

**Location ID: 4c**
- **Title:** Grant Consent Record
- **Description:** Create new consent with policy version
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:169

**Location ID: 4d**
- **Title:** Revoke Consent
- **Description:** Update existing consent to withdrawn state
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/repositories.py:187

**Location ID: 4e**
- **Title:** Block Access Without Consent
- **Description:** Enforce POPIA compliance at API boundary
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/dependencies.py:84

### AI Guide: Consent Repository POPIA Compliance Flow

**Motivation:**
The consent repository exists to make parental consent durable, queryable, and enforceable. It supports legal compliance by ensuring the API can prove whether learner access was allowed at the time of a request.

**Details:**

**Access Gate Query**
The dependency layer calls the repository before protected learner-data operations [4a][4b]. If no active consent is returned, ConsentRequiredError [4e] prevents access.

**Consent Lifecycle Writes**
Grant and revoke operations [4c][4d] turn guardian decisions into database state. Grant records should preserve policy-version metadata; revocation writes must ensure withdrawn consent is no longer treated as active.

**Layer Responsibility**
Repositories persist and retrieve consent records. Services and dependencies interpret those records as authorization decisions. Keeping this boundary clear prevents persistence code from becoming policy code while still enabling strong compliance enforcement.

## Trace ID: 5
**Title:** Diagnostic Session Repository Lifecycle

**Description:** IRT diagnostic session creation and state management with theta tracking and response recording.

**Motivation:**
Adaptive diagnostics require durable session state: initial theta, current state, items served, and learner responses must survive across API calls. The diagnostic session repository encapsulates this persistence so diagnostic services can focus on IRT logic and item selection.

The repository also preserves the auditability of diagnostic progression by keeping response history and served-item counts with the session record.

**Details:**

**Session Creation**
create_session() [5a] instantiates a DiagnosticSession [5b] with learner_id, theta_before, session state, and initial response metadata. It adds the session to the transaction [5c], flushes, refreshes, and returns the generated session ID.

**Response Accumulation**
append_response() [5d] fetches the existing session, copies the responses JSON structure, appends the new item response [5e], updates items_served [5f], then flushes the updated session. This keeps session progress in one aggregate record.

**State Tracking Invariant**
The response array and items_served count should move together. If responses are appended without updating the count, analytics and session-expiry jobs may misinterpret session progress.

**Trace text diagram:**
```text
Diagnostic Session Repository Lifecycle
├── API/Service Layer Entry
│   └── create_session() called <-- 5a
│       ├── DiagnosticSession model instantiated <-- 5b
│       │   ├── learner_id set <-- diagnostic_session_repository.py:18
│       │   ├── theta_before = 0.0 (initial ability) <-- diagnostic_session_repository.py:19
│       │   ├── session_state = "initialising" <-- diagnostic_session_repository.py:21
│       │   └── theta_history initialized <-- diagnostic_session_repository.py:26
│       ├── self.db.add(session) <-- 5c
│       ├── await self.db.flush() <-- diagnostic_session_repository.py:30
│       └── await self.db.refresh(session) <-- diagnostic_session_repository.py:31
│           └── return session with ID <-- diagnostic_session_repository.py:32
└── Response Recording Flow
    └── append_response() called <-- 5d
        ├── get_session() fetch existing <-- diagnostic_session_repository.py:51
        ├── items.append(response) <-- 5e
        ├── session.items_served updated <-- 5f
        ├── self.db.add(session) <-- diagnostic_session_repository.py:60
        └── await self.db.flush() <-- diagnostic_session_repository.py:61
            └── return updated session <-- diagnostic_session_repository.py:63
```

**Location ID: 5a**
- **Title:** Session Creation Entry
- **Description:** Initialize diagnostic with ability estimate
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/diagnostic_session_repository.py:16

**Location ID: 5b**
- **Title:** Instantiate Session Model
- **Description:** Create session with initial theta and state
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/diagnostic_session_repository.py:17

**Location ID: 5c**
- **Title:** Stage Session
- **Description:** Add session to transaction
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/diagnostic_session_repository.py:29

**Location ID: 5d**
- **Title:** Record Item Response
- **Description:** Append learner response to session
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/diagnostic_session_repository.py:50

**Location ID: 5e**
- **Title:** Update Response Array
- **Description:** Accumulate responses in JSONB field
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/diagnostic_session_repository.py:56

**Location ID: 5f**
- **Title:** Track Item Count
- **Description:** Maintain count of administered items
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/diagnostic_session_repository.py:59

### AI Guide: Diagnostic Session Repository Lifecycle

**Motivation:**
The diagnostic session repository preserves assessment continuity. It lets adaptive diagnostic services resume from persisted theta and response history instead of rebuilding session state from transient memory.

**Details:**

**Session Bootstrap**
create_session() [5a] creates the database aggregate that represents one diagnostic attempt. Initial theta and state [5b] give the IRT engine a known starting point.

**Response History Management**
append_response() [5d] stores each learner answer in the session response array [5e]. The repository also updates items_served [5f], making progress queries and expiry jobs reliable.

**Operational Consideration**
Because responses are stored in a mutable JSON structure, updates should copy and reassign the structure before flushing. This ensures SQLAlchemy detects the change and persists the updated response history.

## Trace ID: 6
**Title:** Item Bank Repository with Exposure Tracking

**Description:** Diagnostic item management with per-learner exposure tracking and difficulty-based selection.

**Motivation:**
Adaptive diagnostics must avoid repeatedly serving the same items to a learner, both to maintain measurement validity and to reduce memorization effects. The item bank repository implements exposure-aware queries and atomic exposure counters.

This repository is a key part of fair diagnostic delivery: item selection can use difficulty and CAPS filters while excluding items a learner has already seen.

**Details:**

**Unexposed Selection Query**
get_unexposed_items() [6a] builds a subquery of item IDs already seen by the learner [6b]. The main diagnostic item query filters out those IDs [6c], applies quality and exposure constraints, then orders by difficulty.

**Exposure Recording**
When an item is served, record_exposure() [6d] creates an ItemExposure record and increments the diagnostic item's exposure_count [6e][6f]. Recording both the learner-specific exposure and aggregate exposure counter supports personalization and global item-bank health.

**Concurrency Safety**
The exposure counter uses a database-side UPDATE expression rather than read-modify-write in Python. This makes concurrent exposure increments safer because PostgreSQL applies the increment atomically.

**Trace text diagram:**
```text
Item Bank Repository Exposure Tracking
├── Unexposed Item Selection Flow
│   ├── get_unexposed_items() entry <-- 6a
│   │   ├── Build exposure subquery <-- 6b
│   │   │   └── SELECT item_id FROM exposures <-- item_bank_repository.py:79
│   │   │       WHERE learner_id = $1
│   │   ├── Filter query with NOT IN <-- 6c
│   │   │   └── WHERE item_id NOT IN (subquery) <-- item_bank_repository.py:94
│   │   └── Execute query & return items <-- item_bank_repository.py:105
│   │       └── ORDER BY difficulty_b ASC <-- item_bank_repository.py:96
└── Exposure Recording Flow
    ├── record_exposure() entry <-- 6d
    │   ├── Create ItemExposure record <-- item_bank_repository.py:214
    │   │   └── INSERT INTO item_exposure <-- item_bank_repository.py:220
    │   ├── Atomic counter update <-- 6e
    │   │   └── UPDATE diagnostic_items <-- 6f
    │   │       SET exposure_count = exposure_count + 1
    │   └── Flush transaction <-- item_bank_repository.py:228
    │       └── await self.db.flush()
```

**Location ID: 6a**
- **Title:** Query Unexposed Items
- **Description:** Select items learner hasn't seen yet
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:64

**Location ID: 6b**
- **Title:** Build Exposure Subquery
- **Description:** Subquery for learner's item history
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:78

**Location ID: 6c**
- **Title:** Filter Exposed Items
- **Description:** Exclude items in exposure history
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:94

**Location ID: 6d**
- **Title:** Record Item Exposure
- **Description:** Log that learner saw this item
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:206

**Location ID: 6e**
- **Title:** Increment Exposure Counter
- **Description:** Atomic update of item exposure count
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:222

**Location ID: 6f**
- **Title:** Atomic Counter Update
- **Description:** Increment without race conditions
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/repositories/item_bank_repository.py:225

### AI Guide: Item Bank Repository with Exposure Tracking

**Motivation:**
The item bank repository protects assessment quality by ensuring learners receive appropriate, approved, not-yet-exposed diagnostic items. It also tracks item exposure so the platform can avoid overusing individual items.

**Details:**

**Exposure-Aware Filtering**
The repository builds an exposure subquery [6b] and applies it to the main selection [6c]. This keeps the selection logic in SQL, where filtering can use indexes and execute close to the data.

**Atomic Usage Accounting**
record_exposure() [6d] writes a learner-specific exposure record and increments the item exposure counter [6e][6f]. The database-side increment avoids the classic race where two workers read the same count and write back the same incremented value.

**Adaptive Diagnostics Boundary**
The repository does not decide which item is pedagogically best; it returns safe candidates. The diagnostic service or IRT selection layer can then rank those candidates by information or difficulty match.

## Trace ID: 7
**Title:** Repository Dependency Injection Pattern

**Description:** Dynamic repository resolution and factory pattern for diagnostic module boundaries.

**Motivation:**
EduBoost uses dependency injection to keep modules testable and decoupled from concrete repository construction. The diagnostic module adds a dynamic resolver that can map repository names to classes at runtime, supporting module boundaries and test substitution.

This pattern helps agents and developers understand how repository dependencies enter services and route handlers without hardcoding all repository classes at every call site.

**Details:**

**Dynamic Class Resolution**
resolve_repository_class(name) uses a repository name-to-class mapping [7a] and imports modules dynamically [7b]. The resolved class is cached so repeated lookups do not repeatedly import the same module.

**Repository Factory**
repository(name, db) [7c] resolves the class and instantiates it with the active DB session [7d]. This gives diagnostic workflows a lightweight factory for repository dependencies.

**FastAPI Dependency Provider**
The FastAPI dependency layer exposes provider functions such as get_consent_repo() [7e]. Route handlers can request repository instances through dependency injection, making tests easier because providers can be overridden.

**Boundary Rule**
Dynamic resolution should be constrained to known repository names. It is useful for decoupling, but unrestricted dynamic imports would make module boundaries harder to reason about.

**Trace text diagram:**
```text
Repository Dependency Injection System
├── Diagnostic Module Boundary
│   ├── Repository name → class mapping <-- 7a
│   │   └── Dynamic module import <-- 7b
│   │       └── getattr(module, class_name) <-- diagnostic_repositories.py:75
│   └── Repository factory function <-- 7c
│       └── Instantiate with DB session <-- 7d
│           └── return cls(db) <-- diagnostic_repositories.py:89
└── FastAPI Dependency Layer
    └── Dependency provider function <-- 7e
        └── return ConsentRepository() <-- dependencies.py:29
            └── Injected into route handler <-- dependencies.py:62
                └── Route receives repo instance <-- dependencies.py:80
```

**Location ID: 7a**
- **Title:** Repository Class Resolver
- **Description:** Dynamic import with fallback candidates
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_deps/diagnostic_repositories.py:62

**Location ID: 7b**
- **Title:** Dynamic Module Import
- **Description:** Load repository module at runtime
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_deps/diagnostic_repositories.py:74

**Location ID: 7c**
- **Title:** Repository Factory
- **Description:** Instantiate repository with session
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_deps/diagnostic_repositories.py:87

**Location ID: 7d**
- **Title:** Repository Instantiation
- **Description:** Create repository instance with DB session
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_deps/diagnostic_repositories.py:89

**Location ID: 7e**
- **Title:** FastAPI Dependency Provider
- **Description:** Inject repository into route handlers
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/dependencies.py:28

### AI Guide: Repository Dependency Injection Pattern

**Motivation:**
Repository injection keeps services independent from concrete persistence construction. This improves testability, because services can receive fakes or mocks, and improves modularity, because each module can define how it resolves its persistence dependencies.

**Details:**

**Diagnostic Repository Resolution**
The diagnostic dependency helper resolves a repository class by name [7a], imports the module [7b], and constructs the repository with the current session [7c][7d]. This is useful where module configuration decides which repository implementation to use.

**FastAPI Provider Pattern**
FastAPI dependency providers [7e] expose repositories to routes without requiring route handlers to know construction details. Providers can also centralize future changes such as adding caching, wrappers, or instrumentation.

**Testing Implication**
When writing tests, override providers or pass fake repositories into services instead of patching SQLAlchemy internals. This keeps tests focused on service behavior rather than database mechanics.

## Trace ID: 8
**Title:** Service Layer Repository Composition

**Description:** How services aggregate multiple repositories for business logic orchestration.

**Motivation:**
Services often need more than one repository to complete a business workflow. The repository layer should provide focused data access methods, while services compose those repositories into higher-level operations such as POPIA data rights handling or diagnostic orchestration.

This trace shows how repository composition supports separation of concerns: repositories fetch and persist data, while services enforce workflow rules and coordinate multiple data sources.

**Details:**

**POPIA Service Composition**
POPIADataRightsService accepts an AsyncSession [8a] and creates LearnerRepository [8b], AuditRepository [8c], and consent-related dependencies. load_learner_for_read() delegates learner retrieval to the learner repository [8d], keeping data-rights service logic separate from SQLAlchemy queries.

**Diagnostic Service Constructor Injection**
DiagnosticServiceV2 receives repositories and quota services through its constructor [8e]. run_diagnostic() calls learner_repository.get_by_id() [8f], consults quota, and creates diagnostic sessions through the diagnostic repository.

**Composition Boundary**
Services may coordinate multiple repositories, but repositories should not call services. This preserves a one-way dependency direction: API → service → repository → database.

**Testability**
Constructor injection makes service tests straightforward. Tests can pass fake repositories with get_by_id() or create_session() methods, allowing business behavior to be verified without a database.

**Trace text diagram:**
```text
Service Layer Repository Composition
├── POPIA Service (Data Rights) <-- popia_service.py:51
│   ├── __init__(db: AsyncSession) <-- 8a
│   │   ├── self.learners = LearnerRepository(db) <-- 8b
│   │   └── self.audit = AuditRepository(db) <-- 8c
│   └── load_learner_for_read() <-- popia_service.py:58
│       └── await self.learners.get_by_id() <-- 8d
│
└── Diagnostic Service V2 (Assessment) <-- diagnostic_service_v2.py:6
    ├── __init__(learner_repo, quota, diag_repo) <-- 8e
    │   ├── self.learner_repository = learner_repo <-- diagnostic_service_v2.py:8
    │   ├── self.quota_service = quota_service <-- diagnostic_service_v2.py:9
    │   └── self.diagnostic_repository = diag_repo <-- diagnostic_service_v2.py:10
    └── run_diagnostic() <-- diagnostic_service_v2.py:12
        ├── await learner_repository.get_by_id() <-- 8f
        ├── await quota_service.get_cached() <-- diagnostic_service_v2.py:17
        └── await diagnostic_repository.create_session() <-- diagnostic_service_v2.py:20
```

**Location ID: 8a**
- **Title:** Service Constructor
- **Description:** Initialize service with database session
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/popia_service.py:52

**Location ID: 8b**
- **Title:** Compose Learner Repository
- **Description:** Service owns repository instance
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/popia_service.py:54

**Location ID: 8c**
- **Title:** Compose Audit Repository
- **Description:** Multiple repositories for cross-cutting concerns
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/popia_service.py:55

**Location ID: 8d**
- **Title:** Repository Method Call
- **Description:** Service delegates data access to repository
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/popia_service.py:59

**Location ID: 8e**
- **Title:** Dependency Injection Constructor
- **Description:** Service receives repositories as dependencies
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/diagnostic_service_v2.py:7

**Location ID: 8f**
- **Title:** Cross-Repository Coordination
- **Description:** Service orchestrates multiple repository calls
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/diagnostic_service_v2.py:13

### AI Guide: Service Layer Repository Composition

**Motivation:**
Repository composition lets services express business workflows without embedding SQL queries. This keeps persistence reusable and keeps service code focused on authorization, validation, orchestration, and domain rules.

**Details:**

**Session-Based Composition**
POPIADataRightsService builds repositories from a shared session [8a][8b][8c]. This lets related reads and writes participate in one transaction and keeps data-rights workflows consistent.

**Constructor Injection Composition**
DiagnosticServiceV2 receives dependencies through its constructor [8e], then orchestrates calls across learner, quota, and diagnostic persistence [8f]. This pattern is preferable when services need to be unit-tested independently of FastAPI.

**Layering Invariant**
The direction of dependency should remain API → service → repository. If repositories start invoking services or enforcing workflow policy, the boundary becomes unclear and tests become harder to isolate.
