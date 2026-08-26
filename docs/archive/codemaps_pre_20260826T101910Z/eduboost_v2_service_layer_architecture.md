# EduBoost V2 Service Layer Architecture

Service layer implementing business logic across authentication, content generation, diagnostic assessments, POPIA compliance, and LLM orchestration. Key entry points include user login [1b], content artifact creation [2c], diagnostic session initialization [3b], and data export requests [4b].

## Trace ID: 1
**Title:** User Authentication Flow

**Description:** Auth service handling login with password verification, lockout checks, and token issuance

**Motivation:**
EduBoost V2 implements a comprehensive authentication service that handles user login with security best practices including password verification, account lockout after failed attempts, and JWT token issuance. The service uses a repository pattern for data access, separating business logic from data persistence. Password verification uses cryptographic hash comparison (bcrypt) to protect credentials. Account lockout prevents brute force attacks by temporarily locking accounts after too many failed attempts. Token issuance generates both access tokens (short-lived) and refresh tokens (long-lived with rotation) for secure session management. The service also handles password updates on successful login for hash rotation, ensuring passwords are re-hashed with the latest algorithm.

**Details:**
- **Execution Flow:** login() entry point → Repository layer find_by_email() → Business rules _is_locked_out() check → verify_password() → Success path _issue_token_pair() → create_access_token() → store_refresh_token() → Failure paths _record_failed_attempt() → _lock_account()
- **Concurrency Safety:** Login operations are stateless and thread-safe. Lockout checks use atomic operations on failed attempt counters. Token issuance is deterministic based on user data. No distributed locks needed as authentication is per-request. Multiple concurrent login attempts handled independently
- **Covered Objects:** AuthService, UserRepository, password verification, lockout logic, token issuance, access token creation, refresh token storage, failed attempt tracking, account lockout
- **Timeouts:** User lookup: ~10-50ms. Password verification: ~50-200ms. Lockout check: ~10-50ms. Token creation: ~10-50ms. Refresh token storage: ~10-50ms. Total login: ~100-400ms
- **Migration Path:** From basic auth to comprehensive auth service. Migration requires: 1) Implement password hashing, 2) Add lockout logic, 3) Integrate token issuance, 4) Add refresh token storage, 5) Update password hash rotation
- **Error Handling:** Nonexistent account returns same error as wrong password (prevents enumeration). Lockout raises AuthError with clear message. Password verification failure records attempt and may lock account. Token issuance failures logged. All errors returned as AuthError
- **Security Considerations:** Password hashing uses bcrypt with work factor. Lockout prevents brute force attacks. Same error for nonexistent vs wrong password prevents enumeration. Token issuance uses secure JWT with kid-based key rotation. Refresh tokens stored with hashing. IP tracking for lockout (optional)

**Trace text diagram:**
```
Authentication Flow (AuthService)
├── login() entry point <-- 1a
│   ├── Repository layer
│   │   └── find_by_email() <-- 1b
│   ├── Business rules
│   │   ├── _is_locked_out() check <-- 1c
│   │   └── verify_password() <-- 1d
│   ├── Success path
│   │   └── _issue_token_pair() <-- 1e
│   │       ├── create_access_token() <-- 1f
│   │       └── store_refresh_token() <-- 1g
│   └── Failure paths
│       ├── _record_failed_attempt() <-- auth_service.py:221
│       └── _lock_account() <-- auth_service.py:223
```

**Location ID: 1a**
- **Title:** Login Entry Point
- **Description:** Main authentication method accepting email and password
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_service.py:199

**Location ID: 1b**
- **Title:** User Lookup
- **Description:** Repository call to fetch user by email
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_service.py:204

**Location ID: 1c**
- **Title:** Lockout Check
- **Description:** Business rule enforcement for account lockout after failed attempts
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_service.py:212

**Location ID: 1d**
- **Title:** Password Verification
- **Description:** Cryptographic password hash comparison
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_service.py:220

**Location ID: 1e**
- **Title:** Token Issuance
- **Description:** Generate JWT access and refresh tokens for authenticated user
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_service.py:235

**Location ID: 1f**
- **Title:** Access Token Creation
- **Description:** Core token creation with user claims
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_service.py:405

**Location ID: 1g**
- **Title:** Refresh Token Storage
- **Description:** Persist refresh token to repository for rotation tracking
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/auth_service.py:412

### AI Guide: User Authentication Flow

**Motivation:**
The authentication service handles user login with security best practices including password verification, account lockout, and JWT token issuance. The complete login flow from credential verification to token generation ensures secure authentication while protecting against brute force attacks.

**Details:**

**Login Entry and User Lookup**
The login entry is the main authentication method accepting email and password, returning LoginResponse with tokens on success and raising AuthError on failure [1a]. User lookup is a repository call to fetch user by email, returning the user record with password hash or None if the user is not found [1b].

**Lockout Check and Password Verification**
The lockout check enforces business rules for account lockout by checking failed attempt count and lockout time, raising AuthError if locked [1c]. Password verification uses cryptographic hash comparison with bcrypt to verify the password against the stored hash [1d].

**Token Issuance and Storage**
Token issuance generates JWT access and refresh tokens, with the access token being short-lived (15 min) and the refresh token long-lived with rotation [1e]. Access token creation is the core token creation with user claims including user_id, role, and other claims using kid-based keyring [1f]. Refresh token storage persists the refresh token for rotation tracking by storing the hashed token with user_id and family_id [1g].

## Trace ID: 2
**Title:** Content Artifact Creation & Validation

**Description:** Content Factory service validating and creating artifacts with ETL source provenance

**Motivation:**
EduBoost V2 implements a content factory service that creates and validates content artifacts with strict provenance requirements. The service ensures all generated content is traceable to approved ETL sources, preventing hallucination and ensuring educational quality. Validation includes schema presence checks, answer key verification for diagnostic items, and ETL source bundle validation. Source provenance checks enforce that sources are approved, indexed, and training-ready, with license compatibility and quality score thresholds. The service builds a source snapshot hash for traceability and stores validation reports for audit trails. This system ensures content quality and compliance with educational standards while enabling efficient content generation at scale.

**Details:**
- **Execution Flow:** ContentFactoryService.create_artifact() → Extract sources from payload → ContentValidationService validate_artifact_payload() → Schema presence check → Answer key verification → ETLProvenanceService validate_source_bundle() → Source citation loop (Check document_id/chunk_id, Approved status check, License compatibility, Quality score threshold) → Build source snapshot hash → Create ContentGenerationArtifact → Loop: Add ContentArtifactSource → Add ContentValidationReport
- **Concurrency Safety:** Artifact creation is stateless and thread-safe. Validation checks are read-only. Source provenance checks are deterministic. No distributed locks needed as operations are independent. Multiple concurrent artifact creations handled independently
- **Covered Objects:** ContentFactoryService, ContentValidationService, ETLProvenanceService, ContentGenerationArtifact, ContentArtifactSource, ContentValidationReport, ETL sources, source citations, validation rules
- **Timeouts:** Payload extraction: ~1-5ms. Validation: ~10-50ms. Source provenance check: ~50-200ms. Artifact creation: ~10-50ms. Source persistence: ~10-50ms. Total artifact creation: ~100-400ms
- **Migration Path:** From unvalidated content to validated artifacts. Migration requires: 1) Implement validation service, 2) Add ETL provenance checks, 3) Create artifact models, 4) Add source citation persistence, 5) Add validation report storage
- **Error Handling:** Validation failures return errors list. Source provenance failures prevent artifact creation. Schema failures fail validation. Answer key failures fail validation. All errors logged with clear messages
- **Security Considerations:** Source provenance ensures approved sources only. License compatibility checks prevent copyright issues. Quality score thresholds ensure educational quality. Validation reports provide audit trail. Source snapshot hash ensures traceability

**Trace text diagram:**
```
Content Factory Artifact Creation Flow
├── ContentFactoryService.create_artifact() <-- 2a
│   ├── Extract sources from payload <-- content_factory.py:176
│   ├── ContentValidationService
│   │   └── validate_artifact_payload() <-- 2b
│   │       ├── Schema presence check <-- content_factory.py:137
│   │       ├── Answer key verification <-- content_factory.py:141
│   │       └── ETLProvenanceService
│   │           └── validate_source_bundle() <-- 2c
│   │               ├── Source citation loop <-- content_factory.py:74
│   │               │   ├── Check document_id/chunk_id <-- content_factory.py:76
│   │               │   ├── Approved status check <-- 2d
│   │               │   ├── License compatibility <-- content_factory.py:90
│   │               │   └── Quality score threshold <-- content_factory.py:98
│   │               └── Build source snapshot hash <-- content_factory.py:115
│   ├── Create ContentGenerationArtifact <-- 2e
│   ├── Loop: Add ContentArtifactSource <-- 2f
│   └── Add ContentValidationReport <-- 2g
```

**Location ID: 2a**
- **Title:** Artifact Creation Entry
- **Description:** Main service method for creating content artifacts
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:170

**Location ID: 2b**
- **Title:** Validation Orchestration
- **Description:** Delegate to validation service for business rule checks
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:177

**Location ID: 2c**
- **Title:** Source Provenance Gate
- **Description:** ETL provenance validation ensuring approved source citations
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:145

**Location ID: 2d**
- **Title:** Source Status Check
- **Description:** Enforce that sources are approved/indexed/training_ready
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:84

**Location ID: 2e**
- **Title:** Artifact Instantiation
- **Description:** Create artifact model with validation-based status
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:185

**Location ID: 2f**
- **Title:** Source Citation Persistence
- **Description:** Store ETL source citations for traceability
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:206

**Location ID: 2g**
- **Title:** Validation Report Storage
- **Description:** Persist validation results for audit trail
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_factory.py:231

### AI Guide: Content Artifact Creation & Validation

**Motivation:**
The content factory service creates and validates content artifacts with strict provenance requirements. Artifacts are validated against ETL sources and stored with full traceability to ensure content quality and compliance with provenance requirements.

**Details:**

**Artifact Creation and Validation**
The artifact creation entry is the main service method for creating content artifacts, accepting a payload with artifact JSON and sources and returning ContentGenerationArtifact [2a]. Validation orchestration delegates to the validation service for business rule checks, validating schema, answer key, and source provenance [2b].

**Source Provenance and Status**
The source provenance gate performs ETL provenance validation ensuring approved source citations by checking document_id, chunk_id, status, license, and quality, and building a source snapshot hash [2c]. The source status check enforces that sources are approved/indexed/training_ready, only allowing approved sources for content generation [2d].

**Artifact and Citation Persistence**
Artifact instantiation creates the artifact model with validation-based status, setting status based on validation result and storing the artifact hash [2e]. Source citation persistence stores ETL source citations for traceability by linking artifacts to source chunks and storing citation metadata [2f]. Validation report storage persists validation results for the audit trail by storing validation errors and warnings to enable compliance auditing [2g].

## Trace ID: 3
**Title:** Diagnostic Session Lifecycle

**Description:** Diagnostic session service orchestrating IRT-based adaptive assessment with Redis state management

**Motivation:**
EduBoost V2 implements a diagnostic session service that orchestrates IRT (Item Response Theory) based adaptive assessments. The service uses Redis for state management to enable fast, scalable session handling without database bottlenecks. IRT engine initialization creates session state with ability estimate (theta) and item exposure tracking. Redis state persistence with 24h TTL ensures sessions are available for recovery while preventing memory bloat. The service implements adaptive item selection based on current ability estimate, selecting items that maximize information gain. Response recording updates the ability estimate and records item exposure. Session finalization generates final results with ability estimate and knowledge gap topics. Session recovery enables learners to resume interrupted sessions, improving user experience.

**Details:**
- **Execution Flow:** Session Creation Flow (create_session() entry → IRT engine initialization → Redis state persistence → _save_state() helper → redis.set(key, json, TTL)) → Item Delivery Flow (next_item() method → _load_state() from Redis → IRT adaptive selection → _save_state() update) → Response Recording Flow (record_response() method → _load_state() from Redis → Repository fetch item ORM → IRT engine update theta → Redis state update → Finalization check → session_result()) → Session Recovery (recover_session() from Redis)
- **Concurrency Safety:** Session operations use Redis for state management. Redis provides atomic operations for state updates. IRT engine operations are deterministic per session. No distributed locks needed as Redis handles concurrency. Multiple sessions handled independently
- **Covered Objects:** DiagnosticSessionService, IRT engine, Redis state management, session state, item selection, response recording, session finalization, session recovery, item repository
- **Timeouts:** Session creation: ~10-50ms. IRT initialization: ~10-50ms. Redis persistence: ~10-50ms. Item selection: ~10-50ms. Response recording: ~10-50ms. Session finalization: ~10-50ms. Total session operation: ~50-250ms
- **Migration Path:** From database-only state to Redis-backed state. Migration requires: 1) Implement Redis state management, 2) Add IRT engine integration, 3) Implement adaptive item selection, 4) Add session recovery, 5) Set TTL for session cleanup
- **Error Handling:** Redis connection failures logged. IRT engine failures logged. Session not found raises error. Invalid state logged. All errors returned with clear messages
- **Security Considerations:** Session state stored in Redis with TTL. Session IDs are UUIDs (unguessable). Item exposure tracking prevents item reuse. Ability estimates are per-learner. Session recovery requires session ID

**Trace text diagram:**
```
Diagnostic Session Service
├── Session Creation Flow
│   ├── create_session() entry <-- 3a
│   │   ├── IRT engine initialization <-- 3b
│   │   └── Redis state persistence <-- 3c
│   │       └── _save_state() helper <-- diagnostic_session_service.py:253
│   │           └── redis.set(key, json, TTL) <-- diagnostic_session_service.py:257
├── Item Delivery Flow
│   ├── next_item() method <-- diagnostic_session_service.py:116
│   │   ├── _load_state() from Redis <-- diagnostic_session_service.py:259
│   │   ├── IRT adaptive selection <-- 3d
│   │   └── _save_state() update <-- diagnostic_session_service.py:136
└── Response Recording Flow
    ├── record_response() method <-- diagnostic_session_service.py:141
    │   ├── _load_state() from Redis <-- diagnostic_session_service.py:165
    │   ├── Repository fetch item ORM <-- diagnostic_session_service.py:176
    │   ├── IRT engine update theta <-- 3e
    │   ├── Redis state update <-- 3f
    │   └── Finalization check
    │       └── session_result() <-- 3g
    └── Session Recovery (P4-09)
        └── recover_session() from Redis <-- diagnostic_session_service.py:225
```

**Location ID: 3a**
- **Title:** Session Creation Entry
- **Description:** Initialize new diagnostic session for learner
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/diagnostic_session_service.py:82

**Location ID: 3b**
- **Title:** IRT Engine Initialization
- **Description:** Delegate to IRT engine for session state creation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/diagnostic_session_service.py:100

**Location ID: 3c**
- **Title:** Redis State Persistence
- **Description:** Store session state in Redis with 24h TTL
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/diagnostic_session_service.py:106

**Location ID: 3d**
- **Title:** Adaptive Item Selection
- **Description:** IRT engine selects next item based on current ability estimate
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/diagnostic_session_service.py:133

**Location ID: 3e**
- **Title:** Response Recording
- **Description:** Update ability estimate and record exposure
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/diagnostic_session_service.py:181

**Location ID: 3f**
- **Title:** State Update Persistence
- **Description:** Save updated theta and response history to Redis
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/diagnostic_session_service.py:188

**Location ID: 3g**
- **Title:** Session Finalization
- **Description:** Generate final result with ability estimate and gap topics
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/diagnostic_session_service.py:214

### AI Guide: Diagnostic Session Lifecycle

**Motivation:**
The diagnostic session service orchestrates IRT-based adaptive assessments with Redis state management. Sessions are created, items are delivered adaptively, and responses are recorded to provide accurate ability estimation through Item Response Theory.

**Details:**

**Session Creation and IRT Initialization**
The session creation entry initializes a new diagnostic session for the learner, accepting learner_id and prior_theta and returning session_id [3a]. IRT engine initialization delegates to the IRT engine for session state creation, creating the initial theta estimate and setting item exposure tracking [3b].

**Redis State Persistence**
Redis state persistence stores the session state in Redis with 24h TTL to enable fast state retrieval and automatic cleanup after expiry [3c]. This ensures that session state is quickly accessible and automatically cleaned up.

**Adaptive Item Selection and Response Recording**
Adaptive item selection uses the IRT engine to select the next item based on the current ability estimate, maximizing information gain and tracking item exposure [3d]. Response recording updates the ability estimate and records exposure using the IRT model to update theta and records response history [3e].

**State Update and Finalization**
State update persistence saves the updated theta and response history to Redis with atomic state update to maintain session consistency [3f]. Session finalization generates the final result with ability estimate and gap topics, marks the session as completed, and returns the diagnostic result [3g].

## Trace ID: 4
**Title:** POPIA Data Export Request

**Description:** POPIA service orchestrating data subject rights with consent verification and audit logging

**Motivation:**
EduBoost V2 implements a POPIA (Protection of Personal Information Act) compliant data export service that handles data subject rights requests. The service verifies user authorization before exporting data, ensuring only authorized users can access learner data. Consent verification ensures active consent exists before exporting, complying with POPIA requirements. Data aggregation collects learner data from multiple tables (diagnostic sessions, lessons, knowledge gaps, parental consent) into a comprehensive export payload. Audit logging records all export requests for compliance trail, enabling regulatory audits. The service supports multiple export formats (JSON, CSV) for flexibility. This system ensures POPIA compliance while providing data subjects with access to their personal information.

**Details:**
- **Execution Flow:** POPIADataRightsService → build_learner_export() → load_learner_for_read() → LearnerRepository.get_by_id() → require_learner_read_for_current_user() → ConsentService.require_active_consent() → _export_payload() → SELECT DiagnosticSession → SELECT Lesson → SELECT KnowledgeGap → SELECT ParentalConsent → AuditRepository.append() → return export with status → _to_csv() (if format=csv)
- **Concurrency Safety:** Export operations are read-only and thread-safe. Authorization checks are deterministic. Consent verification is read-only. No distributed locks needed as operations are independent. Multiple concurrent exports handled independently
- **Covered Objects:** POPIADataRightsService, LearnerRepository, ConsentService, AuditRepository, diagnostic sessions, lessons, knowledge gaps, parental consent, export payload, audit logging
- **Timeouts:** Authorization check: ~10-50ms. Consent verification: ~10-50ms. Data aggregation: ~100-500ms. Audit logging: ~10-50ms. CSV generation: ~50-200ms. Total export: ~200-850ms
- **Migration Path:** From manual data export to POPIA-compliant service. Migration requires: 1) Implement authorization checks, 2) Add consent verification, 3) Implement data aggregation, 4) Add audit logging, 5) Support multiple export formats
- **Error Handling:** Authorization failures raise error. Consent failures raise error. Data aggregation failures logged. Audit logging failures logged. All errors returned with clear messages
- **Security Considerations:** Authorization checks ensure only authorized access. Consent verification ensures POPIA compliance. Audit logging provides compliance trail. Export data limited to learner's own data. CSV generation handles sensitive data carefully

**Trace text diagram:**
```
POPIA Data Export Flow
├── POPIADataRightsService <-- popia_service.py:51
│   ├── build_learner_export() <-- 4a
│   │   ├── load_learner_for_read() <-- 4b
│   │   │   ├── LearnerRepository.get_by_id() <-- popia_service.py:59
│   │   │   └── require_learner_read_for_current_user() <-- popia_service.py:62
│   │   ├── ConsentService.require_active_consent() <-- 4c
│   │   ├── _export_payload() <-- 4d
│   │   │   ├── SELECT DiagnosticSession <-- 4e
│   │   │   ├── SELECT Lesson <-- popia_service.py:219
│   │   │   ├── SELECT KnowledgeGap <-- popia_service.py:220
│   │   │   └── SELECT ParentalConsent <-- popia_service.py:221
│   │   ├── AuditRepository.append() <-- 4f
│   │   └── return export with status <-- popia_service.py:103
│   └── _to_csv() (if format=csv) <-- popia_service.py:100
```

**Location ID: 4a**
- **Title:** Export Request Entry
- **Description:** Main method for POPIA data export requests
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/popia_service.py:72

**Location ID: 4b**
- **Title:** Authorization Check
- **Description:** Verify user has read access to learner data
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/popia_service.py:80

**Location ID: 4c**
- **Title:** Consent Verification
- **Description:** Ensure active consent exists before exporting data
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/popia_service.py:81

**Location ID: 4d**
- **Title:** Data Aggregation
- **Description:** Collect learner data from multiple tables
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/popia_service.py:83

**Location ID: 4e**
- **Title:** Session Data Query
- **Description:** Fetch diagnostic sessions for export payload
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/popia_service.py:218

**Location ID: 4f**
- **Title:** Audit Event Recording
- **Description:** Log export request for compliance trail
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/popia_service.py:84

### AI Guide: POPIA Data Export Request

**Motivation:**
The POPIA service handles data subject rights requests with authorization checks, consent verification, and audit logging. Data exports are performed in compliance with POPIA requirements to ensure that data subject rights are respected and all actions are auditable.

**Details:**

**Export Entry and Authorization**
The export request entry is the main method for POPIA data export requests, accepting learner_id and format and returning the export payload [4a]. The authorization check verifies that the user has read access to learner data by checking user permissions and raising an error if unauthorized [4b].

**Consent Verification**
Consent verification ensures that active consent exists before exporting data by checking consent status and raising an error if no consent [4c]. This ensures that data is only exported with proper consent.

**Data Aggregation and Query**
Data aggregation collects learner data from multiple tables including diagnostic sessions, lessons, knowledge gaps, and parental consent to build a comprehensive export [4d]. The session data query fetches diagnostic sessions for the export payload by querying the session table and including session metadata and results [4e].

**Audit Logging**
Audit event recording logs the export request for the compliance trail by recording the actor, timestamp, and data exported to enable regulatory audits [4f]. This provides a complete audit trail for all data export operations.

## Trace ID: 5
**Title:** LLM Gateway with Fallback

**Description:** LLM gateway orchestrating provider requests with retry, timeout, and development fallback

**Motivation:**
EduBoost V2 implements an LLM gateway that orchestrates requests across multiple LLM providers with fallback capabilities. The gateway checks a generation enabled flag to allow disabling LLM generation for testing or cost control. It builds a provider list with fallback ordering, trying primary providers first before falling back to secondary providers. Health checks verify provider availability before requests, avoiding failures on unhealthy providers. Retry logic handles transient failures with configurable retry counts. Timeout policies prevent hanging requests. When all providers fail, the gateway activates a deterministic mock provider for development and CI, ensuring tests can run without external dependencies. This system provides resilience, cost control, and development flexibility for LLM integration.

**Details:**
- **Execution Flow:** CanonicalLLMGateway.complete() → Check generation enabled flag → Build provider list with fallback → For each provider (with retry loop) → provider.health() check → provider.complete() call → (on success) Build LLMGatewayResponse → (on all failures) Fallback provider activation → DeterministicMockProvider → .complete() mock impl
- **Concurrency Safety:** Gateway operations are stateless and thread-safe. Provider health checks are independent. Retry logic is per-request. No distributed locks needed as operations are independent. Multiple concurrent requests handled independently
- **Covered Objects:** CanonicalLLMGateway, provider health checks, provider requests, retry logic, timeout policies, fallback provider, DeterministicMockProvider, LLMGatewayResponse, LLMGatewayMetadata
- **Timeouts:** Health check: ~10-50ms. Provider request: ~1-10s (with timeout). Retry delay: ~100-1000ms. Fallback activation: ~10-50ms. Total request: ~1-30s depending on retries
- **Migration Path:** From single provider to multi-provider gateway. Migration requires: 1) Implement provider interface, 2) Add health checks, 3) Implement retry logic, 4) Add fallback provider, 5) Configure provider ordering
- **Error Handling:** Provider failures trigger retry. All provider failures trigger fallback. Health check failures skip provider. Timeout failures trigger retry. All errors logged with clear messages
- **Security Considerations:** Generation enabled flag allows cost control. Health checks prevent requests to unhealthy providers. Timeout policies prevent hanging. Fallback provider for development only. Provider credentials stored securely

**Trace text diagram:**
```
LLM Gateway Request Flow
├── CanonicalLLMGateway.complete() <-- 5a
│   ├── Check generation enabled flag <-- gateway.py:141
│   ├── Build provider list with fallback <-- gateway.py:145
│   └── For each provider (with retry loop) <-- gateway.py:151
│       ├── provider.health() check <-- 5b
│       ├── provider.complete() call <-- 5c
│       │   └── (on success)
│       │       └── Build LLMGatewayResponse <-- 5d
│       └── (on all failures)
│           └── Fallback provider activation <-- 5e
│               └── DeterministicMockProvider <-- gateway.py:96
│                   └── .complete() mock impl <-- 5f
```

**Location ID: 5a**
- **Title:** Gateway Entry Point
- **Description:** Main completion method with provider orchestration
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/llm/gateway.py:140

**Location ID: 5b**
- **Title:** Health Check
- **Description:** Verify provider availability before request
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/llm/gateway.py:152

**Location ID: 5c**
- **Title:** Provider Request
- **Description:** Execute LLM completion with timeout policy
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/llm/gateway.py:158

**Location ID: 5d**
- **Title:** Success Response
- **Description:** Return result with comprehensive metadata
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/llm/gateway.py:163

**Location ID: 5e**
- **Title:** Fallback Activation
- **Description:** Use deterministic mock provider when all providers fail
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/llm/gateway.py:190

**Location ID: 5f**
- **Title:** Mock Provider Implementation
- **Description:** Deterministic provider for development and CI
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/llm/gateway.py:109

### AI Guide: LLM Gateway with Fallback

**Motivation:**
The LLM gateway orchestrates requests across multiple LLM providers with retry, timeout, and fallback capabilities. The gateway provides resilience and development flexibility for LLM integration by using health checks, fallback mechanisms, and deterministic mock providers.

**Details:**

**Gateway Entry and Health Check**
The gateway entry point is the main completion method with provider orchestration, accepting LLMGatewayRequest and returning LLMGatewayResponse [5a]. The health check verifies provider availability before request by checking provider health status and skipping unhealthy providers [5b].

**Provider Request and Response**
The provider request executes LLM completion with timeout policy by calling provider.complete() with timeout and handling provider-specific errors [5c]. The success response returns the result with comprehensive metadata including content, latency, provider info, and fallback status [5d].

**Fallback and Mock Provider**
Fallback activation uses a deterministic mock provider when all providers fail to ensure development and CI can run without external dependencies [5e]. The mock provider implementation is a deterministic provider for development and CI that returns predictable responses without external API calls [5f].

## Trace ID: 6
**Title:** Content Generation Execution

**Description:** Content generation executor orchestrating LLM generation with source context and artifact persistence

**Motivation:**
EduBoost V2 implements a content generation executor that orchestrates LLM-based content generation with source context and artifact persistence. The executor validates tasks and updates status before execution, ensuring only valid tasks are processed. Source context building fetches ETL source chunks from the database to provide context for generation, improving content quality and relevance. Provider initialization selects the appropriate LLM or deterministic provider based on configuration. Content generation calls the provider with source context to generate content. Artifact creation loop validates and deduplicates artifacts before persistence, preventing duplicate content. The content factory service validates artifacts against business rules before persistence. Task completion updates task status based on results, enabling tracking of generation progress. This system enables scalable, high-quality content generation with full traceability.

**Details:**
- **Execution Flow:** execute_task() entry → Task validation & status update → Source context building → source_context_service.build_context() → Fetch ETL chunks from DB → Provider initialization → get_content_generation_provider() → Returns LLM or deterministic provider → Content generation → _call_provider() → Provider.complete() with chunks → Artifact creation loop → Validation & deduplication checks → create_artifact() → ContentFactoryService validation → Artifact model instantiation → Source citations persistence → Task completion → Update task.status based on results
- **Concurrency Safety:** Task execution is stateless and thread-safe. Source context building is read-only. Provider initialization is deterministic. No distributed locks needed as operations are independent. Multiple concurrent tasks handled independently
- **Covered Objects:** ContentGenerationExecutor, SourceContextService, provider factory, LLM providers, ContentFactoryService, ContentGenerationArtifact, ContentArtifactSource, task status, validation rules
- **Timeouts:** Task validation: ~1-5ms. Source context building: ~50-200ms. Provider initialization: ~10-50ms. Content generation: ~1-10s. Artifact creation: ~10-50ms. Task completion: ~1-5ms. Total task execution: ~1-10s
- **Migration Path:** From manual generation to orchestrated executor. Migration requires: 1) Implement task validation, 2) Add source context building, 3) Integrate provider factory, 4) Add artifact creation, 5) Implement task status tracking
- **Error Handling:** Task validation failures fail task. Source context failures fail task. Provider failures fail task. Artifact creation failures logged. All errors logged with clear messages
- **Security Considerations:** Source context from approved ETL sources only. Provider selection based on configuration. Artifact validation ensures quality. Task status tracking enables audit. Source citations provide traceability

**Trace text diagram:**
```
Content Generation Task Execution
├── execute_task() entry <-- 6a
│   ├── Task validation & status update <-- content_generation_executor.py:71
│   ├── Source context building <-- 6b
│   │   └── source_context_service.build_context()
│   │       └── Fetch ETL chunks from DB
│   ├── Provider initialization <-- 6c
│   │   └── get_content_generation_provider()
│   │       └── Returns LLM or deterministic provider
│   ├── Content generation <-- 6d
│   │   └── _call_provider()
│   │       └── Provider.complete() with chunks
│   ├── Artifact creation loop <-- content_generation_executor.py:96
│   │   ├── Validation & deduplication checks <-- content_generation_executor.py:99
│   │   └── create_artifact() <-- 6e
│   │       ├── ContentFactoryService validation <-- content_factory.py:177
│   │       ├── Artifact model instantiation <-- content_factory.py:185
│   │       └── Source citations persistence <-- content_factory.py:206
│   └── Task completion <-- 6f
│       └── Update task.status based on results
```

**Location ID: 6a**
- **Title:** Task Execution Entry
- **Description:** Execute a single content generation task
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:68

**Location ID: 6b**
- **Title:** Source Context Building
- **Description:** Fetch ETL source chunks for generation context
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:83

**Location ID: 6c**
- **Title:** Provider Factory
- **Description:** Get configured LLM or deterministic provider
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:87

**Location ID: 6d**
- **Title:** LLM Generation Call
- **Description:** Generate content using provider with source context
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:89

**Location ID: 6e**
- **Title:** Artifact Persistence
- **Description:** Create artifact with source citations via content factory
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:105

**Location ID: 6f**
- **Title:** Task Status Update
- **Description:** Mark task as succeeded or failed based on results
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/content_generation_executor.py:144

### AI Guide: Content Generation Execution

**Motivation:**
The content generation executor orchestrates LLM-based content generation with source context and artifact persistence. Tasks are validated, executed, and tracked to ensure high-quality content generation with full traceability.

**Details:**

**Task Execution and Source Context**
The task execution entry executes a single content generation task, accepting task_id and updating task status during execution [6a]. Source context building fetches ETL source chunks for generation context to provide context for LLM generation and improve content quality [6b].

**Provider Factory and LLM Generation**
The provider factory gets the configured LLM or deterministic provider, selecting the provider based on configuration to enable development flexibility [6c]. The LLM generation call generates content using the provider with source context by calling provider.complete() with chunks and returning generated content [6d].

**Artifact Persistence and Task Status**
Artifact persistence creates an artifact with source citations via the content factory, validating artifacts before persistence and storing source citations for traceability [6e]. The task status update marks the task as succeeded or failed based on results, updating task metadata to enable tracking of generation progress [6f].

## Trace ID: 7
**Title:** Consent Lifecycle Management

**Description:** Consent service managing POPIA consent grants, renewals, and withdrawals with audit trail

**Motivation:**
EduBoost V2 implements a consent service that manages POPIA consent grants, renewals, and withdrawals with full audit trail. The service handles consent grants by checking for existing consent records and applying domain model transitions. If existing consent exists, the service updates it with the new privacy notice version. If no existing consent, the service creates a new consent record. Consent withdrawals require an existing consent record and apply the withdrawal state transition. All consent operations are persisted to the repository and logged to the audit repository for compliance trail. The service uses domain model transitions to ensure valid state changes (grant, withdraw, renew). This system ensures POPIA compliance while providing clear audit trails for regulatory requirements.

**Details:**
- **Execution Flow:** grant() entry point → get_active_for_learner() repo query → Consent domain model transition → existing.grant(version) → new ConsentRecord().grant(version) → consent_repo.update() persist → audit_repo.record() event log → withdraw() entry point → _require_consent_record() helper → get_active_for_learner() query → record.withdraw() transition → consent_repo.update() persist → audit_repo.record() event log
- **Concurrency Safety:** Consent operations use repository for persistence. Domain model transitions are deterministic. Audit logging is append-only. No distributed locks needed as operations are independent. Multiple concurrent consent operations handled by repository
- **Covered Objects:** ConsentService, ConsentRepository, AuditRepository, ConsentRecord, domain model transitions, consent grants, consent withdrawals, audit logging
- **Timeouts:** Consent lookup: ~10-50ms. Domain model transition: ~1-5ms. Repository persistence: ~10-50ms. Audit logging: ~10-50ms. Total consent operation: ~30-150ms
- **Migration Path:** From manual consent tracking to service-based management. Migration requires: 1) Implement consent repository, 2) Add domain model transitions, 3) Implement grant/withdraw operations, 4) Add audit logging, 5. Integrate with POPIA service
- **Error Handling:** Consent not found raises error. Invalid state transition raises error. Repository failures logged. Audit logging failures logged. All errors returned with clear messages
- **Security Considerations:** Consent operations require authorization. Audit logging provides compliance trail. Domain model ensures valid state changes. Consent records linked to learner_id. Privacy notice version tracked

**Trace text diagram:**
```
Consent Service - Grant/Withdraw Flow
├── grant() entry point <-- 7a
│   ├── get_active_for_learner() repo query <-- 7b
│   ├── Consent domain model transition
│   │   ├── existing.grant(version) <-- 7c
│   │   └── new ConsentRecord().grant(version) <-- consent_service.py:59
│   ├── consent_repo.update() persist <-- 7d
│   └── audit_repo.record() event log <-- 7e
│
└── withdraw() entry point <-- 7f
    ├── _require_consent_record() helper <-- consent_service.py:217
    │   └── get_active_for_learner() query <-- consent_service.py:218
    ├── record.withdraw() transition <-- 7g
    ├── consent_repo.update() persist <-- consent_service.py:122
    └── audit_repo.record() event log <-- consent_service.py:123
```

**Location ID: 7a**
- **Title:** Grant Consent Entry
- **Description:** Main method for granting parental consent
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/consent_service.py:42

**Location ID: 7b**
- **Title:** Existing Consent Check
- **Description:** Query repository for active consent record
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/consent_service.py:54

**Location ID: 7c**
- **Title:** Domain Model Update
- **Description:** Apply grant transition on existing consent domain object
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/consent_service.py:56

**Location ID: 7d**
- **Title:** Repository Persistence
- **Description:** Save updated consent record to database
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/consent_service.py:57

**Location ID: 7e**
- **Title:** Audit Event Recording
- **Description:** Log consent grant for compliance audit trail
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/consent_service.py:67

**Location ID: 7f**
- **Title:** Withdraw Consent
- **Description:** Handle consent withdrawal request
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/consent_service.py:115

**Location ID: 7g**
- **Title:** Withdrawal Transition
- **Description:** Apply withdrawal state transition on domain model
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/consent_service.py:121

### AI Guide: Consent Lifecycle Management

**Motivation:**
The consent service manages POPIA consent grants, renewals, and withdrawals with full audit trail. Consent operations are performed with domain model transitions and audit logging to ensure compliance with POPIA requirements and maintain a complete audit trail.

**Details:**

**Grant Consent and Existing Check**
The grant consent entry is the main method for granting parental consent, accepting learner_id, actor_id, and privacy_notice_version and returning ConsentRecord [7a]. The existing consent check queries the repository for an active consent record to check if consent already exists and enable consent renewal [7b].

**Domain Model and Repository Persistence**
The domain model update applies the grant transition on the existing consent domain object, updating the privacy notice version and ensuring valid state transition [7c]. Repository persistence saves the updated consent record to the database to persist consent state and return the updated record [7d].

**Audit Logging and Withdrawal**
Audit event recording logs the consent grant for the compliance audit trail by recording the actor, timestamp, and consent details to enable regulatory audits [7e]. Withdraw consent handles the consent withdrawal request by accepting learner_id and actor_id and returning the updated ConsentRecord [7f]. The withdrawal transition applies the withdrawal state transition on the domain model, changing consent status to withdrawn and ensuring valid state transition [7g].

## Trace ID: 8
**Title:** Lesson Generation with Quota Control

**Description:** Lesson service orchestrating LLM generation with quota checks, semantic caching, and audit logging

**Motivation:**
EduBoost V2 implements a lesson generation service with quota control, semantic caching, and audit logging. The service uses semantic caching to avoid regenerating identical lessons, reducing costs and improving response times. Cache lookup checks Redis for existing lessons based on subject, topic, and learner profile. Quota enforcement checks and reserves daily token quotas before generation, preventing cost overruns. Redis atomic increment ensures quota tracking is thread-safe. LLM generation calls the provider to generate lesson content. Lesson persistence stores generated lessons in the repository for future reference. Audit logging records lesson generation events for analytics and compliance. This system enables efficient, cost-controlled lesson generation with full traceability.

**Details:**
- **Execution Flow:** LessonServiceV2.generate_lesson() → SemanticCacheService.get(key) → Redis cache lookup → QuotaService.check_and_reserve() → Redis.incrby(key, tokens) → Atomic quota increment → _call_llm() wrapper → LLM provider invocation → LessonRepository.create() → Database persistence → AuditService.log_event() → Audit trail recording → Returns lesson dict with content
- **Concurrency Safety:** Cache lookup is read-only and thread-safe. Quota enforcement uses atomic Redis operations. LLM generation is stateless. No distributed locks needed as Redis handles concurrency. Multiple concurrent generations handled independently
- **Covered Objects:** LessonServiceV2, SemanticCacheService, QuotaService, LLM providers, LessonRepository, Redis cache, quota tracking, audit logging
- **Timeouts:** Cache lookup: ~10-50ms. Quota check: ~10-50ms. LLM generation: ~1-10s. Lesson persistence: ~10-50ms. Audit logging: ~10-50ms. Total lesson generation: ~1-10s
- **Migration Path:** From uncontrolled generation to quota-controlled service. Migration requires: 1) Implement semantic caching, 2) Add quota enforcement, 3) Integrate LLM provider, 4) Add lesson persistence, 5) Implement audit logging
- **Error Handling:** Cache miss continues to generation. Quota exceeded raises error. LLM generation failure logged. Lesson persistence failure logged. All errors returned with clear messages
- **Security Considerations:** Quota enforcement prevents cost overruns. Semantic caching reduces costs. Audit logging provides traceability. Lesson content stored securely. Quota tracking uses atomic operations

**Trace text diagram:**
```
Lesson Generation Flow
├── LessonServiceV2.generate_lesson() <-- 8a
│   ├── SemanticCacheService.get(key) <-- 8b
│   │   └── Redis cache lookup <-- quota_service.py:141
│   ├── QuotaService.check_and_reserve() <-- 8c
│   │   └── Redis.incrby(key, tokens) <-- 8d
│   │       └── Atomic quota increment
│   ├── _call_llm() wrapper <-- 8e
│   │   └── LLM provider invocation
│   ├── LessonRepository.create() <-- 8f
│   │   └── Database persistence
│   └── AuditService.log_event() <-- 8g
│       └── Audit trail recording <-- audit_service.py:21
└── Returns lesson dict with content <-- lesson_service_v2.py:61
```

**Location ID: 8a**
- **Title:** Lesson Generation Entry
- **Description:** Main method for generating personalized lessons
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/lesson_service_v2.py:29

**Location ID: 8b**
- **Title:** Cache Lookup
- **Description:** Check semantic cache for existing lesson
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/lesson_service_v2.py:41

**Location ID: 8c**
- **Title:** Quota Enforcement
- **Description:** Check and reserve daily token quota before generation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/lesson_service_v2.py:47

**Location ID: 8d**
- **Title:** Redis Quota Increment
- **Description:** Atomic increment of daily token usage counter
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/quota_service.py:67

**Location ID: 8e**
- **Title:** LLM Generation
- **Description:** Call LLM provider to generate lesson content
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/lesson_service_v2.py:49

**Location ID: 8f**
- **Title:** Lesson Persistence
- **Description:** Store generated lesson in repository
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/lesson_service_v2.py:51

**Location ID: 8g**
- **Title:** Audit Logging
- **Description:** Record lesson generation event for analytics
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/lesson_service_v2.py:72

### AI Guide: Lesson Generation with Quota Control

**Motivation:**
The lesson generation service orchestrates LLM generation with quota checks, semantic caching, and audit logging. Lessons are generated efficiently with cost control and traceability by using semantic caching to reduce costs and enforcing quota limits to prevent overruns.

**Details:**

**Lesson Generation and Cache Lookup**
The lesson generation entry is the main method for generating personalized lessons, accepting learner_id, subject_code, and topic and returning a lesson dict with content [8a]. Cache lookup checks the semantic cache for an existing lesson by building a cache key from subject, topic, and learner profile and returning the cached lesson if found [8b].

**Quota Enforcement and Redis Increment**
Quota enforcement checks and reserves the daily token quota before generation to prevent cost overruns and raises an error if quota is exceeded [8c]. The Redis quota increment performs an atomic increment of the daily token usage counter to ensure thread-safe quota tracking and sets expiry on the first increment [8d].

**LLM Generation and Lesson Persistence**
LLM generation calls the LLM provider to generate lesson content by passing context and parameters and returning generated content [8e]. Lesson persistence stores the generated lesson in the repository to persist lesson metadata and content and enable future retrieval [8f].

**Audit Logging**
Audit logging records the lesson generation event for analytics by logging the learner, subject, topic, and tokens used to enable cost tracking [8g]. This provides a complete audit trail for all lesson generation events.
