# EduBoost V2 Modular Architecture: Core Domain Modules

Maps the modular monolith's domain modules including authentication, POPIA consent management, IRT-based diagnostics, AI lesson generation, learner profiling, adaptive practice, and background jobs. Key entry points: guardian registration [1b], consent grant with audit [2c], diagnostic IRT calculation [3d], lesson generation pipeline [4e], archetype classification [5c], and ARQ job execution [8b].

## Trace ID: 1
**Title:** Guardian Registration Flow (Auth Module)

**Description:** Authentication module service layer. Traces guardian account creation with PII encryption, password hashing, and audit logging.

**Motivation:**
EduBoost V2's authentication module implements secure guardian registration with POPIA-compliant PII protection. The AuthService.register_guardian() method creates a deterministic hash_email() for duplicate detection without storing plaintext email. It checks for existing guardians via _guardian_repo.get_by_email_hash() to prevent duplicates. The guardian record is created with email_encrypted=encrypt_pii() for POPIA compliance, password_hash=hash_password() for secure credential storage, full_name_encrypted=encrypt_pii() for name protection, and verification_token=generate_token() for email verification. The write_audit_event() logs AuditAction.USER_REGISTERED for compliance trail. The AuthService.authenticate() method verifies credentials via hash_email(), _guardian_repo.get_by_email_hash(), and verify_password(), updates last_login_at, writes AuditAction.USER_LOGIN, and issues JWT tokens via create_access_token() and create_refresh_token(). This secure flow ensures PII protection, credential security, audit compliance, and session management.

**Details:**
- **Execution Flow:** AuthService.register_guardian() → hash_email(email) → Check for existing guardian → _guardian_repo.get_by_email_hash() → Create guardian record → _guardian_repo.create() → email_encrypted=encrypt_pii() → password_hash=hash_password() → full_name_encrypted=encrypt_pii() → verification_token=generate_token() → write_audit_event() → AuditAction.USER_REGISTERED → AuthService.authenticate() → Verify email/password → hash_email(email) → _guardian_repo.get_by_email_hash() → verify_password() → Update last_login_at → write_audit_event() → AuditAction.USER_LOGIN → create_access_token() → create_refresh_token()
- **Concurrency Safety:** Email hash is deterministic. Duplicate check is atomic. Repository operations use transactions. Audit logging is sequential. No distributed locks needed
- **Covered Objects:** Authentication, PII encryption, password hashing, audit logging, JWT tokens, guardian registration
- **Timeouts:** Hash computation: ~1-5ms. Duplicate check: ~10-50ms. Record creation: ~10-50ms. Audit logging: ~10-50ms. Total: ~31-155ms
- **Migration Path:** From plain storage to encrypted. Migration requires: 1) Add encryption, 2) Hash emails, 3) Add audit logging, 4) Update repository
- **Error Handling:** Duplicate errors raised. Encryption errors logged. Hash errors logged. Audit errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Encrypt PII at rest. Hash emails for lookup. Use bcrypt for passwords. Audit all actions. Validate inputs. Secure JWT tokens

**Trace text diagram:**
```
Guardian Registration Flow (Auth Module)
├── AuthService.register_guardian() <-- service.py:66
│   ├── hash_email(email) <-- 1a
│   ├── Check for existing guardian <-- service.py:111
│   │   └── _guardian_repo.get_by_email_hash() <-- service.py:111
│   ├── Create guardian record <-- 1b
│   │   └── _guardian_repo.create() <-- service.py:115
│   │       ├── email_encrypted=encrypt_pii() <-- 1c
│   │       ├── password_hash=hash_password() <-- service.py:119
│   │       ├── full_name_encrypted=encrypt_pii() <-- service.py:120
│   │       └── verification_token=generate_token() <-- service.py:124
│   └── write_audit_event() <-- 1d
│       └── AuditAction.USER_REGISTERED <-- service.py:129
│
└── AuthService.authenticate() <-- service.py:136
    ├── Verify email/password
    │   ├── hash_email(email) <-- service.py:169
    │   ├── _guardian_repo.get_by_email_hash() <-- service.py:170
    │   └── verify_password() <-- service.py:172
    ├── Update last_login_at <-- service.py:185
    ├── write_audit_event() <-- service.py:186
    │   └── AuditAction.USER_LOGIN <-- service.py:188
    └── create_access_token() <-- 1e
        └── create_refresh_token() <-- service.py:197
```

**Location ID: 1a**
- **Title:** Hash email for lookup
- **Description:** Create deterministic hash for duplicate detection without storing plaintext
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/auth/service.py:110

**Location ID: 1b**
- **Title:** Create guardian record
- **Description:** Persist encrypted guardian with hashed password and verification token
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/auth/service.py:115

**Location ID: 1c**
- **Title:** Encrypt PII at rest
- **Description:** POPIA-compliant encryption of personally identifiable information
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/auth/service.py:118

**Location ID: 1d**
- **Title:** Record audit event
- **Description:** Log USER_REGISTERED action for compliance trail
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/auth/service.py:127

**Location ID: 1e**
- **Title:** Issue JWT tokens
- **Description:** Generate access and refresh tokens for authenticated session
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/auth/service.py:193

### AI Guide: Guardian Registration and Authentication

**Motivation:**
EduBoost is a South African educational platform serving children (grades R-7), which means parental consent is legally required under POPIA (Protection of Personal Information Act). The auth module solves the problem of securely creating and authenticating guardian (parent) accounts while ensuring all personally identifiable information is encrypted at rest and every security-relevant action is audit-logged for compliance.

The system must prevent duplicate accounts, protect passwords using industry-standard hashing, and maintain a complete audit trail for regulatory purposes.

**Details:**

**Registration Flow**
Guardian registration begins by hashing the email address [1a] to create a deterministic lookup key without storing plaintext. This hash is checked against existing guardians to prevent duplicates.

The system then creates the guardian record [1b] with multiple layers of protection:

- Email addresses are encrypted using PII encryption [1c] before storage
- Passwords are hashed with bcrypt (not encrypted—they're one-way hashed)
- Full names and phone numbers are also PII-encrypted
- A secure verification token is generated for email confirmation
- Every registration is audit-logged [1d] with AuditAction.USER_REGISTERED for POPIA compliance tracking.

**Authentication Flow**
When a guardian logs in, the system hashes their provided email to look up the account, then verifies the password against the stored bcrypt hash. If authentication succeeds, it updates the last_login_at timestamp and logs the event. The system then issues JWT tokens [1e]—both an access token (short-lived) and a refresh token (longer-lived)—containing the guardian's ID, role, and verification status. These tokens authorize subsequent API requests.

**Security Properties**
- No plaintext PII: Email and names are encrypted; passwords are hashed
- Audit trail: Every registration and login attempt is logged with actor ID and timestamp
- Token-based auth: Stateless JWT tokens eliminate session storage requirements
- Duplicate prevention: Email hashing enables duplicate checks without exposing plaintext

## Trace ID: 2
**Title:** Consent Grant Lifecycle (Consent Module)

**Description:** POPIA consent service managing parental consent with audit trail. Coordinates with consent repository and audit services for compliance.

**Motivation:**
EduBoost V2's consent module implements POPIA-compliant parental consent management with audit trails. The ConsentService.__init__() initializes with self._repo = ConsentRepository(db) and self._audit_repo = AuditRepository(db) for data access. The consent_decision() method calls get_latest_for_learner() and derive_consent_state() to return ConsentPolicyDecision for canonical consent state. The require_active_consent() method recursively calls consent_decision() and if not decision.active, raises ConsentRequiredError to block unauthorized access. The grant() workflow calls _repo.grant() to CREATE parental_consent record with version, IP, and user agent metadata, then _append_audit() calls audit_repo.append() to INSERT audit_log event and FourthEstateService.record() to log consent.granted event. This consent lifecycle ensures POPIA compliance, audit trails, access control, and state management.

**Details:**
- **Execution Flow:** ConsentService.__init__() → self._repo = ConsentRepository(db) → self._audit_repo = AuditRepository(db) → consent_decision() → get_latest_for_learner() → derive_consent_state() → return ConsentPolicyDecision → require_active_consent() → consent_decision() [recursive call] → if not decision.active: → raise ConsentRequiredError → grant() workflow → _repo.grant() → CREATE parental_consent record → _append_audit() → audit_repo.append() → INSERT audit_log event → FourthEstateService.record() → consent.granted event
- **Concurrency Safety:** Consent decision is deterministic. Repository operations use transactions. Audit logging is sequential. No distributed locks needed
- **Covered Objects:** POPIA consent, consent lifecycle, audit trails, access control, state management
- **Timeouts:** Consent decision: ~10-50ms. Repository operations: ~10-50ms. Audit logging: ~10-50ms. Total: ~30-150ms
- **Migration Path:** From simple consent to POPIA compliance. Migration requires: 1) Add audit logging, 2) Implement state machine, 3) Add access control, 4) Update repository
- **Error Handling:** Consent errors raised. Repository errors logged. Audit errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Enforce POPIA compliance. Audit consent actions. Validate consent state. Block unauthorized access. Protect learner data. Validate guardian access

**Trace text diagram:**
```
POPIA Consent Lifecycle (app/modules/consent/)
├── ConsentService.__init__() <-- service.py:52
│   ├── self._repo = ConsentRepository(db) <-- service.py:82
│   └── self._audit_repo = AuditRepository(db) <-- service.py:84
├── consent_decision() <-- 2a
│   ├── get_latest_for_learner() <-- 2b
│   └── derive_consent_state() <-- service.py:93
│       └── return ConsentPolicyDecision <-- service.py:93
├── require_active_consent() <-- 2e
│   ├── consent_decision() [recursive call] <-- service.py:101
│   └── if not decision.active: <-- service.py:102
│       └── raise ConsentRequiredError <-- 2f
└── grant() workflow <-- service.py:114
    ├── _repo.grant() <-- 2c
    │   └── CREATE parental_consent record
    └── _append_audit() <-- 2d
        ├── audit_repo.append() <-- service.py:317
        │   └── INSERT audit_log event
        └── FourthEstateService.record() <-- service.py:325
            └── consent.granted event
```

**Location ID: 2a**
- **Title:** Derive consent state
- **Description:** Canonical consent decision for learner access control
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:90

**Location ID: 2b**
- **Title:** Fetch latest consent
- **Description:** Query repository for most recent consent record
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:92

**Location ID: 2c**
- **Title:** Grant consent record
- **Description:** Create new consent with version, IP, and user agent metadata
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:148

**Location ID: 2d**
- **Title:** Append audit event
- **Description:** Record consent.granted event with learner and version details
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:156

**Location ID: 2e**
- **Title:** Enforce active consent
- **Description:** Require active consent gate before learner data access
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:101

**Location ID: 2f**
- **Title:** Block unauthorized access
- **Description:** Raise exception when consent is missing or expired
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/consent/service.py:111

### AI Guide: Consent Grant Lifecycle

**Motivation:**
The consent module implements POPIA-compliant parental consent management for South African learners. Under POPIA (Protection of Personal Information Act), platforms processing children's data must obtain and maintain verifiable parental consent before any data collection or processing can occur.

This module solves a critical legal requirement: every learner data access must be gated by active, non-expired parental consent. Without this enforcement, the platform cannot legally operate in South Africa. The consent service acts as a mandatory checkpoint that blocks unauthorized access and creates an auditable compliance trail.

**Details:**

**Consent State Management**
The service maintains consent records with three key states: granted, expired, and revoked [2a]. Each consent record includes the policy version agreed to, IP address, user agent, and timestamps for compliance auditing.

The consent_decision() method [2a] queries the latest consent record [2b] and derives the canonical state using policy rules. This decision determines whether a learner's data can be accessed.

**Enforcement Gate**
The require_active_consent() method [2e] is the primary enforcement mechanism used throughout the application. It checks the consent decision and raises ConsentRequiredError [2f] if consent is missing, expired, or revoked. This method is called before any diagnostic session, lesson generation, or learner data retrieval.

**Grant Workflow**
When a guardian grants consent [2c], the service:
- Creates a new consent record in the repository with version and metadata
- Records a consent.granted audit event [2d] for compliance tracking
- Returns the consent object to the caller

The audit trail is critical—every consent state change is logged via either AuditRepository or FourthEstateService to ensure POPIA compliance officers can investigate any data access.

**Cross-Module Integration**
The consent service is injected as a dependency into other domain modules (lessons, diagnostics, practice). For example, LessonService calls require_active_consent() before generating any AI content to ensure the learner has valid parental permission.

This consent-first architecture ensures legal compliance is enforced at the service layer, not just at API boundaries.

## Trace ID: 3
**Title:** IRT Diagnostic Engine (Diagnostics Module)

**Description:** Item Response Theory 2PL adaptive assessment engine. Calculates learner ability (theta) and selects optimal items using Fisher information.

**Motivation:**
EduBoost V2's diagnostics module implements Item Response Theory (IRT) for adaptive assessment. The IRT Mathematical Functions include p_correct(theta, a, b) which computes 1/(1 + exp(-a*(theta-b))) for the 2PL probability function, and fisher_information(theta, a, b) which measures item's statistical information. The Item Selection Service's select_item_for_learner() method calls repo.get_unexposed_items() to filter by theta window & exposure control, then ranks by Fisher information. The _3pl_probability(theta, a, b, c) function extends IRT with guessing parameter for item selection. This IRT engine provides accurate ability estimation, adaptive item selection, and statistical optimization for diagnostic assessments.

**Details:**
- **Execution Flow:** IRT Mathematical Functions → p_correct(theta, a, b) → 1/(1 + exp(-a*(theta-b))) → fisher_information(theta, a, b) → measures item's statistical info → Item Selection Service → select_item_for_learner() → repo.get_unexposed_items() → filters by theta window & exposure → rank by Fisher information → _3pl_probability(theta, a, b, c) → extended IRT with guessing param
- **Concurrency Safety:** IRT calculations are deterministic. Item selection is per-learner. Repository operations use transactions. No distributed locks needed
- **Covered Objects:** IRT engine, 2PL model, Fisher information, adaptive selection, theta estimation
- **Timeouts:** IRT calculation: ~1-5ms. Item selection: ~10-50ms. Repository query: ~10-50ms. Total: ~21-105ms
- **Migration Path:** From static to adaptive assessments. Migration requires: 1) Implement IRT engine, 2) Add item selection, 3) Calibrate parameters, 4) Update repository
- **Error Handling:** IRT errors logged. Selection errors logged. Repository errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate item parameters. Protect learner data. Audit diagnostic results. Validate theta estimates. Filter sensitive data

**Trace text diagram:**
```
IRT Diagnostic Engine (Trace 3)
├── IRT Mathematical Functions
│   ├── p_correct(theta, a, b) <-- 3a
│   │   └── 1/(1 + exp(-a*(theta-b))) <-- 3b
│   └── fisher_information(theta, a, b) <-- 3c
│       └── measures item's statistical info <-- irt_engine.py:88
└── Item Selection Service <-- item_bank_service.py:46
    ├── select_item_for_learner() <-- item_bank_service.py:65
    │   ├── repo.get_unexposed_items() <-- 3d
    │   │   └── filters by theta window & exposure <-- item_bank_service.py:81
    │   └── rank by Fisher information
    └── _3pl_probability(theta, a, b, c) <-- 3e
        └── extended IRT with guessing param <-- item_bank_service.py:31
```

**Location ID: 3a**
- **Title:** 2PL probability function
- **Description:** Item Characteristic Curve: P(correct | theta, a, b)
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/diagnostics/irt_engine.py:52

**Location ID: 3b**
- **Title:** Compute IRT probability
- **Description:** Logistic function with discrimination and difficulty parameters
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/diagnostics/irt_engine.py:82

**Location ID: 3c**
- **Title:** Fisher information metric
- **Description:** Measures statistical information item provides about ability
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/diagnostics/irt_engine.py:85

**Location ID: 3d**
- **Title:** Fetch candidate items
- **Description:** Query items in ability neighbourhood with exposure control
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/diagnostics/item_bank_service.py:78

**Location ID: 3e**
- **Title:** 3PL probability variant
- **Description:** Extended IRT model with guessing parameter for item selection
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/diagnostics/item_bank_service.py:30

### AI Guide: IRT Diagnostic Engine

**Motivation:**
EduBoost needs to accurately measure each learner's ability in mathematics to provide personalized instruction. Traditional fixed-difficulty tests fail because they waste time on questions that are too easy or too hard for the learner. The IRT (Item Response Theory) diagnostic engine solves this by adaptively selecting questions that maximize information gain about the learner's true ability level.

The system uses a 2-Parameter Logistic (2PL) model calibrated against the South African CAPS curriculum for grades R–7. Each diagnostic item has two parameters: discrimination (a) measuring how well it separates high and low ability learners, and difficulty (b) representing the ability level where 50% of learners answer correctly.

**Details:**

**IRT Probability Calculation**
The core mathematical function [3a] computes the probability a learner with ability θ (theta) will answer an item correctly using the logistic curve: P = 1/(1 + e^(-a(θ-b))) [3b]. When θ equals b, the probability is exactly 0.5. Higher discrimination values (a) make the curve steeper, meaning the item better distinguishes ability levels.

**Fisher Information**
The Fisher information metric [3c] quantifies how much statistical information an item provides about a learner's ability at a given θ level [3c at line 88]. Items with high discrimination and difficulty close to the learner's current θ estimate provide maximum information. This guides the adaptive item selection strategy.

**Adaptive Item Selection**
The ItemBankService [at line 46] orchestrates item selection for diagnostic sessions. When selecting the next item [at line 65], it queries the repository for unexposed items [3d] within a θ window (typically ±1.0 logit units) [at line 81]. This ensures items match the learner's ability level while preventing over-exposure.

**3PL Extension**
For more sophisticated item selection, the system supports a 3-Parameter Logistic (3PL) model [3e] that adds a guessing parameter (c) [at line 31]. This accounts for the fact that learners can guess correctly on multiple-choice items even when their ability is far below the item's difficulty.

## Trace ID: 4
**Title:** AI Lesson Generation Pipeline (Lessons Module)

**Description:** End-to-end lesson generation with CAPS validation, LLM gateway, PII redaction, schema validation, answer-key verification, and quality scoring.

**Motivation:**
EduBoost V2's lessons module implements end-to-end AI lesson generation with multiple validation phases. The LessonGenerator.generate pipeline starts with CAPS Validation Phase calling get_topic_context(caps_ref) to validate and fetch topic metadata. The Prompt Construction Phase calls _render_generation_prompt() with Jinja2 template.render() to build structured prompt. The LLM Invocation Phase calls _call_llm_with_error_handling() which invokes self._gateway.generate() with Groq primary / Anthropic fallback. The Safety & Parsing Phase calls redact_pii_text(llm_response) and _parse_and_validate_schema() with LessonCreate.model_validate(). The Quality Validation Phase calls self._validator.validate() executing 8 validation rules. The Answer Key Verification Phase calls _verify_answer_key() with second independent LLM call to compare derived vs original. The Quality Scoring Phase calls _compute_quality_score() with weighted correctness + CAPS. The Persistence Phase calls self._repo.create_lesson() with database commit. This comprehensive pipeline ensures CAPS alignment, LLM reliability, PII safety, schema compliance, quality validation, and answer accuracy.

**Details:**
- **Execution Flow:** LessonGenerator.generate → CAPS Validation Phase → get_topic_context(caps_ref) → Prompt Construction Phase → _render_generation_prompt() → Jinja2 template.render() → LLM Invocation Phase → _call_llm_with_error_handling() → self._gateway.generate() → Safety & Parsing Phase → redact_pii_text(llm_response) → _parse_and_validate_schema() → LessonCreate.model_validate() → Quality Validation Phase → self._validator.validate() → 8 validation rules executed → Answer Key Verification Phase → _verify_answer_key() → Second independent LLM call → Compare derived vs original → Quality Scoring Phase → _compute_quality_score() → Weighted: correctness + CAPS → Persistence Phase → self._repo.create_lesson() → Database commit
- **Concurrency Safety:** Generation is per-lesson. LLM calls are sequential. Validation is stateless. Repository operations use transactions. No distributed locks needed
- **Covered Objects:** AI lesson generation, CAPS validation, LLM gateway, PII redaction, schema validation, answer verification, quality scoring
- **Timeouts:** CAPS validation: ~10-50ms. Prompt rendering: ~1-5ms. LLM invocation: ~1-5s. PII redaction: ~10-50ms. Schema validation: ~10-50ms. Quality validation: ~50-200ms. Answer verification: ~1-3s. Quality scoring: ~1-5ms. Persistence: ~10-50ms. Total: ~2.5-8.5s
- **Migration Path:** From simple to comprehensive pipeline. Migration requires: 1) Add CAPS validation, 2) Implement LLM gateway, 3) Add PII redaction, 4) Add validation phases
- **Error Handling:** CAPS errors raised. LLM errors retried. Validation errors logged. Answer verification logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate CAPS alignment. Redact PII from output. Validate schema. Verify answer keys. Score quality. Protect learner data

**Trace text diagram:**
```
Lesson Generation Pipeline (LessonGenerator.generate) <-- lesson_generator.py:118
├── CAPS Validation Phase
│   └── get_topic_context(caps_ref) <-- 4a
├── Prompt Construction Phase
│   └── _render_generation_prompt() <-- 4b
│       └── Jinja2 template.render() <-- lesson_generator.py:283
├── LLM Invocation Phase
│   └── _call_llm_with_error_handling() <-- 4c
│       └── self._gateway.generate() <-- lesson_generator.py:311
├── Safety & Parsing Phase
│   ├── redact_pii_text(llm_response) <-- 4d
│   └── _parse_and_validate_schema() <-- lesson_generator.py:184
│       └── LessonCreate.model_validate() <-- lesson_generator.py:369
├── Quality Validation Phase
│   └── self._validator.validate() <-- 4e
│       └── 8 validation rules executed
├── Answer Key Verification Phase
│   └── _verify_answer_key() <-- 4f
│       ├── Second independent LLM call <-- lesson_generator.py:417
│       └── Compare derived vs original <-- lesson_generator.py:459
├── Quality Scoring Phase
│   └── _compute_quality_score() <-- lesson_generator.py:217
│       └── Weighted: correctness + CAPS <-- lesson_generator.py:537
└── Persistence Phase
    └── self._repo.create_lesson() <-- 4g
        └── Database commit <-- lesson_generator.py:252
```

**Location ID: 4a**
- **Title:** Resolve CAPS reference
- **Description:** Validate and fetch topic metadata from canonical CAPS map
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:150

**Location ID: 4b**
- **Title:** Render Jinja2 prompt
- **Description:** Build structured prompt with topic, difficulty, misconceptions
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:166

**Location ID: 4c**
- **Title:** Call LLM gateway
- **Description:** Invoke Groq primary / Anthropic fallback with retry logic
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:174

**Location ID: 4d**
- **Title:** Redact PII from output
- **Description:** Safety layer removes personally identifiable information
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:181

**Location ID: 4e**
- **Title:** Run validation rules
- **Description:** Execute all 8 quality and safety validators
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:191

**Location ID: 4f**
- **Title:** Verify answer key
- **Description:** Independent second LLM call to validate practice question answers
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:205

**Location ID: 4g**
- **Title:** Persist lesson
- **Description:** Save validated lesson with metadata to database
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/lesson_generator.py:251

### AI Guide: AI Lesson Generation Pipeline

**Motivation:**
The AI Lesson Generation Pipeline solves the problem of creating personalized, curriculum-aligned educational content at scale for South African primary school learners. Instead of manually writing thousands of lessons for different grades, topics, difficulty levels, and learner misconceptions, the system uses LLMs to generate CAPS-aligned lessons on demand while enforcing strict quality, safety, and correctness guarantees.

The pipeline must ensure that no lesson reaches the database without passing all validators [4e], and critically, that no lesson is marked as verified without a second independent LLM agreeing on every practice question answer [4f]. This prevents the propagation of incorrect educational content to learners.

**Details:**

**CAPS Validation**
Every lesson generation starts by validating the requested CAPS reference (e.g., "4.M.1.1" for Grade 4 Mathematics) against the canonical topic map [4a]. This ensures the system only generates content for topics that exist in the South African curriculum and provides the necessary metadata (grade, term, subject, learning objectives) for prompt construction.

**Prompt Construction**
The system uses Jinja2 templates to render structured prompts [4b] that include the topic metadata, desired difficulty level (foundational/developing/on_level/extending), and any learner-specific misconception tags from previous diagnostic assessments. This templating approach ensures consistent, well-structured prompts across all lesson generations.

**LLM Gateway with Fallback**
The pipeline calls the LLM gateway with error handling [4c], which implements a Groq primary / Anthropic fallback strategy. If the primary provider fails or times out, the system automatically retries with the fallback provider, ensuring high availability for lesson generation requests.

**Safety Layer**
Before parsing the LLM response, the system runs PII redaction [4d] to remove any personally identifiable information that might have been hallucinated by the model. This is a critical POPIA compliance step that prevents accidental data leakage.

**Schema Validation**
The raw JSON from the LLM is parsed and validated against the LessonCreate Pydantic schema, which enforces the required structure: explanation, worked examples, practice questions, answer key, remediation hints, and metadata fields. Malformed responses are rejected immediately.

**Quality Gates**
The validator runs 8 distinct quality rules [4e] covering CAPS alignment, content safety, pedagogical completeness, readability, and inclusiveness. Any lesson failing these rules is rejected and never persisted.

**Answer Key Verification**
The most critical quality gate is independent answer-key verification [4f]. The system makes a second LLM call without showing the original answer key, asking the model to solve each practice question independently. Only if the derived answers match the original answers for all questions is the lesson marked as answer_key_verified=true. Disagreements trigger human review.

**Quality Scoring**
A composite quality score (0.0–1.0) is computed using weighted dimensions: 35% correctness (answer key verification), 25% CAPS alignment, 20% clarity, 10% pedagogical completeness, and 10% safety. This score determines the lesson's review status: approved (≥0.85), ai_generated (≥0.70), or requires_review (<0.70).

**Persistence**
Only after passing all gates does the lesson get persisted to the database [4g] with full metadata including provider, model version, token usage, generation latency, and quality metrics. The database commit finalizes the transaction, making the lesson available to learners.

## Trace ID: 5
**Title:** Learner Archetype Profiling (Learners Module)

**Description:** Ether service for psychological archetype classification using Kabbalistic model. Eliminates cold-start lag with 5-question micro-diagnostic.

**Motivation:**
EduBoost V2's learners module implements the Ether service for psychological archetype classification using a Kabbalistic model to eliminate cold-start lag. The cold-start onboarding flow uses a five-question micro-diagnostic covering learning preference, activity type, reward preference, learning style, and self-description. The archetype classification engine uses a scoring matrix lookup mapping (question_id, answer) to scores, and likelihood weights for ten archetypes: Keter (Crown) - reflective, Chokmah (Wisdom) - inquisitive, Binah (Understanding) - analytical, Chesed (Kindness) - collaborative, Gevurah (Strength) - competitive, Tiferet (Beauty) - creative, Netzach (Victory) - visual, Hod (Splendor) - structured, Yesod (Foundation) - hands-on, and Malkuth (Kingdom) - practical. The engine aggregates scores across answers and uses LLM prompt tone modifiers to personalize lesson content by archetype. This psychological profiling enables personalized learning experiences from the first session.

**Details:**
- **Execution Flow:** Cold-start onboarding flow → Five-question micro-diagnostic → Question 1: Learning preference → Question 2: Activity type → Question 3: Reward preference → Question 4: Learning style → Question 5: Self-description → Answer collection → [(q_id, answer), ...] → Archetype classification engine → Scoring matrix lookup → (question_id, answer) → scores → Likelihood weights → Keter (Crown) - reflective → Chokmah (Wisdom) - inquisitive → Binah (Understanding) - analytical → Chesed (Kindness) - collaborative → Gevurah (Strength) - competitive → Tiferet (Beauty) - creative → Netzach (Victory) - visual → Hod (Splendor) - structured → Yesod (Foundation) - hands-on → Malkuth (Kingdom) - practical → Aggregate scores across answers → LLM prompt tone modifiers → Personalize lesson content by archetype
- **Concurrency Safety:** Classification is per-learner. Scoring is deterministic. Aggregation is stateless. No distributed locks needed
- **Covered Objects:** Learner profiling, archetype classification, Kabbalistic model, cold-start elimination, personalization
- **Timeouts:** Diagnostic collection: ~10-50ms. Scoring: ~1-5ms. Aggregation: ~1-5ms. Total: ~12-60ms
- **Migration Path:** From generic to personalized. Migration requires: 1) Implement diagnostic, 2) Add scoring matrix, 3) Add archetype weights, 4) Update LLM prompts
- **Error Handling:** Diagnostic errors logged. Scoring errors logged. Aggregation errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate diagnostic answers. Protect learner data. Audit classification results. Validate archetype assignment. Filter sensitive data

**Trace text diagram:**
```
Learner Archetype Profiling (Ether Service)
├── Cold-start onboarding flow
│   ├── Five-question micro-diagnostic <-- 5a
│   │   ├── Question 1: Learning preference <-- ether_service.py:37
│   │   ├── Question 2: Activity type <-- ether_service.py:47
│   │   ├── Question 3: Reward preference <-- ether_service.py:57
│   │   ├── Question 4: Learning style <-- ether_service.py:67
│   │   └── Question 5: Self-description <-- ether_service.py:77
│   └── Answer collection
│       └── [(q_id, answer), ...]
├── Archetype classification engine
│   ├── Scoring matrix lookup <-- 5b
│   │   └── (question_id, answer) → scores
│   ├── Likelihood weights <-- 5c
│   │   ├── Keter (Crown) - reflective <-- ether_service.py:94
│   │   ├── Chokmah (Wisdom) - inquisitive <-- ether_service.py:95
│   │   ├── Binah (Understanding) - analytical <-- ether_service.py:98
│   │   ├── Chesed (Kindness) - collaborative <-- ether_service.py:95
│   │   ├── Gevurah (Strength) - competitive <-- ether_service.py:97
│   │   ├── Tiferet (Beauty) - creative <-- ether_service.py:100
│   │   ├── Netzach (Victory) - visual <-- ether_service.py:96
│   │   ├── Hod (Splendor) - structured <-- ether_service.py:96
│   │   ├── Yesod (Foundation) - hands-on <-- ether_service.py:97
│   │   └── Malkuth (Kingdom) - practical <-- ether_service.py:99
│   └── Aggregate scores across answers
└── LLM prompt tone modifiers
    └── Personalize lesson content by archetype
```

**Location ID: 5a**
- **Title:** Onboarding questions
- **Description:** Five-question micro-diagnostic for first-session classification
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/learners/ether_service.py:34

**Location ID: 5b**
- **Title:** Scoring matrix
- **Description:** Maps (question_id, answer) to archetype likelihood scores
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/learners/ether_service.py:93

**Location ID: 5c**
- **Title:** Archetype weights
- **Description:** Likelihood scores for Kabbalistic archetype classification
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/learners/ether_service.py:94

### AI Guide: Learner Archetype Profiling

**Motivation:**
EduBoost faces a cold-start problem: when a new learner first uses the platform, the system has no data about their learning style, preferences, or cognitive approach. Traditional adaptive systems require 8-10 interaction events before they can personalize content effectively, creating a poor initial experience.

The Ether service solves this by classifying learners into psychological archetypes during onboarding using a 5-question micro-diagnostic [5a]. This enables immediate personalization of lesson content tone and teaching approach from the very first session, eliminating the cold-start lag entirely.

**Details:**

**Onboarding Questions**
The system presents five carefully designed questions [5a] that probe different dimensions of learning preference:

- Learning preference when confused (reflective vs. inquisitive vs. visual vs. hands-on)
- Activity type preference (puzzles vs. creating vs. stories vs. competition)
- Reward preference (badges vs. praise vs. progress charts vs. harder challenges)
- Learning style (step-by-step vs. story-based vs. quick summary vs. observation)
- Self-description (curious vs. determined vs. creative vs. caring)

**Kabbalistic Archetype Model**
Each answer maps to likelihood scores for ten Kabbalistic archetypes [5b][5c]:

- Keter (Crown) - reflective, contemplative learners
- Chokmah (Wisdom) - inquisitive, question-driven learners
- Binah (Understanding) - analytical, systematic learners
- Chesed (Kindness) - collaborative, socially-motivated learners
- Gevurah (Strength) - competitive, challenge-seeking learners
- Tiferet (Beauty) - creative, aesthetic learners
- Netzach (Victory) - visual, spatial learners
- Hod (Splendor) - structured, procedural learners
- Yesod (Foundation) - hands-on, experiential learners
- Malkuth (Kingdom) - practical, application-focused learners

The scoring matrix [5b] maps each (question_id, answer) pair to archetype probabilities. For example, answering "Think about it quietly on my own" to question 1 gives Keter: 0.64, Binah: 0.23 [5c].

**Personalization Impact**
Once classified, the archetype modifies LLM prompt tone when generating lessons. A Keter learner receives more reflective, contemplative explanations, while a Yesod learner gets hands-on, activity-based content. This happens from the first lesson, not after weeks of usage data collection.

The system aggregates scores across all five answers to determine the dominant archetype, enabling nuanced classification beyond simple binary categories.

## Trace ID: 6
**Title:** Adaptive Practice Selection (Practice Module)

**Description:** Practice generator selecting items based on diagnostic gaps, IRT ability, and exposure control for spaced repetition.

**Motivation:**
EduBoost V2's practice module implements adaptive practice selection with spaced repetition. The PracticeGenerator.select_items() method initializes served_ids set and for each gap_topic in gap_topics, filters candidates by criteria: match caps_ref to gap, exclude served_ids, check theta window (±0.5), and verify review_status == "approved". It sorts by difficulty match and selects top per_gap items. The SpacedRepetitionScheduler.update_schedule() implements SM-2 variant: if incorrect, interval=1 and reduce EF; if first review, interval=1; if second review, interval=3 and boost EF; else, interval *= EF and cap EF at 3.0. This adaptive approach provides gap-targeted practice, difficulty matching, exposure control, and spaced repetition for optimal learning.

**Details:**
- **Execution Flow:** PracticeGenerator.select_items() → Initialize served_ids set → For each gap_topic in gap_topics → Filter candidates by criteria → Match caps_ref to gap → Exclude served_ids → Check theta window (±0.5) → Verify review_status == "approved" → Sort by difficulty match → Select top per_gap items → Return selected items list → SpacedRepetitionScheduler → update_schedule() → If incorrect: interval=1, reduce EF → If first review: interval=1 → If second review: interval=3, boost EF → Else: interval *= EF, cap EF at 3.0
- **Concurrency Safety:** Selection is per-learner. Scheduling is per-item. Repository operations use transactions. No distributed locks needed
- **Covered Objects:** Adaptive practice, gap targeting, IRT matching, exposure control, spaced repetition
- **Timeouts:** Item selection: ~10-50ms. Filtering: ~10-50ms. Sorting: ~1-5ms. Scheduling: ~1-5ms. Total: ~22-110ms
- **Migration Path:** From static to adaptive practice. Migration requires: 1) Implement gap targeting, 2) Add IRT matching, 3) Add exposure control, 4) Implement spaced repetition
- **Error Handling:** Selection errors logged. Filtering errors logged. Scheduling errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate gap data. Protect learner data. Audit practice results. Validate theta estimates. Filter sensitive data

**Trace text diagram:**
```
Adaptive Practice Selection Pipeline
├── PracticeGenerator.select_items() <-- 6a
│   ├── Initialize served_ids set <-- practice_generator.py:18
│   ├── For each gap_topic in gap_topics <-- practice_generator.py:20
│   │   ├── Filter candidates by criteria <-- 6b
│   │   │   ├── Match caps_ref to gap <-- practice_generator.py:23
│   │   │   ├── Exclude served_ids <-- practice_generator.py:24
│   │   │   ├── Check theta window (±0.5) <-- practice_generator.py:25
│   │   │   └── Verify review_status == "approved" <-- practice_generator.py:26
│   │   ├── Sort by difficulty match <-- 6c
│   │   └── Select top per_gap items <-- practice_generator.py:29
│   └── Return selected items list <-- practice_generator.py:30
│
└── SpacedRepetitionScheduler
    └── update_schedule() <-- 6d
        ├── If incorrect: interval=1, reduce EF <-- spaced_repetition_scheduler.py:18
        ├── If first review: interval=1 <-- spaced_repetition_scheduler.py:21
        ├── If second review: interval=3, boost EF <-- spaced_repetition_scheduler.py:24
        └── Else: interval *= EF, cap EF at 3.0 <-- spaced_repetition_scheduler.py:27
```

**Location ID: 6a**
- **Title:** Select practice items
- **Description:** Adaptive selection from gaps with theta-based difficulty matching
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/practice/practice_generator.py:9

**Location ID: 6b**
- **Title:** Filter candidates
- **Description:** Match items to gap topics, theta window, and approval status
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/practice/practice_generator.py:21

**Location ID: 6c**
- **Title:** Sort by difficulty match
- **Description:** Rank items by proximity to learner ability estimate
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/practice/practice_generator.py:28

**Location ID: 6d**
- **Title:** Update review schedule
- **Description:** SM-2 variant for spaced repetition intervals
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/practice/spaced_repetition_scheduler.py:17

### AI Guide: Adaptive Practice Selection

**Motivation:**
EduBoost's practice module implements adaptive practice selection to optimize learning efficiency. Instead of presenting random practice items, the system selects items based on diagnostic gaps, IRT ability estimates, and spaced repetition principles. This ensures learners practice topics they struggle with at an appropriate difficulty level, with review intervals optimized for long-term retention.

The system uses the SM-2 spaced repetition algorithm variant to schedule reviews: items answered incorrectly are reviewed sooner (interval=1), while correctly answered items have their review intervals multiplied by an easiness factor (EF) capped at 3.0. This balances practice frequency with cognitive load.

**Details:**

**Adaptive Item Selection**
The PracticeGenerator.select_items() method [6a] orchestrates the selection process. For each gap topic identified from diagnostic results, it filters candidate items [6b] using multiple criteria:

- Match the CAPS reference to the gap topic
- Exclude items already served in the current session (served_ids)
- Check the theta window (±0.5 logit units) to match learner ability
- Verify review_status == "approved" to ensure quality

**Difficulty Matching**
After filtering, items are sorted by difficulty match [6c]—the absolute difference between the item's difficulty parameter and the learner's current theta estimate. Items closest to the learner's ability level are selected first, ensuring practice is neither too easy nor too hard.

**Spaced Repetition Scheduling**
The SpacedRepetitionScheduler.update_schedule() method [6d] implements an SM-2 variant optimized for primary school learners:

- If incorrect: interval=1 day, reduce EF by 0.2
- If first review: interval=1 day
- If second review: interval=3 days, boost EF by 0.1
- Otherwise: interval *= EF, cap EF at 3.0

This aggressive initial spacing (1-3 days) is appropriate for primary school learners who benefit from more frequent review, while the EF cap prevents intervals from becoming too long.

**Exposure Control**
The served_ids set prevents item repetition within a single practice session, ensuring variety and preventing over-exposure to specific items. This is particularly important for diagnostic items that should not be memorized.

## Trace ID: 7
**Title:** Mastery Model Computation (Progress Module)

**Description:** Progress tracking with IRT-based mastery scoring, learning velocity, and risk signals for intervention.

**Motivation:**
EduBoost V2's progress module implements comprehensive mastery tracking with IRT-based scoring. The IRT Ability → Mastery Conversion uses theta_to_mastery() with erf(theta / sqrt(2)) normalization to transform ability to 0-1 mastery score. The Composite Mastery Score Calculation uses compute_mastery_score() with weighted components: mastery_theta (from IRT), practice_accuracy component, recency_days decay, consistency_ratio component, confidence (from SE), and weighted sum (40/25/15/10/10). The Learning Analytics Service includes Learning Velocity Tracking with compute_velocity() calculating delta_mastery / weeks_elapsed, Risk Signal Classification with compute_risk_signal() classifying as urgent (score<0.4 OR idle>30d), at_risk (score<0.6 OR idle>14d), or on_track (otherwise), and Next Best Activities ranked by priority & mastery score. This comprehensive tracking provides accurate mastery measurement, learning velocity, risk identification, and intervention guidance.

**Details:**
- **Execution Flow:** IRT Ability → Mastery Conversion → theta_to_mastery() → erf(theta / sqrt(2)) normalization → Composite Mastery Score Calculation → compute_mastery_score() → mastery_theta (from IRT) → practice_accuracy component → recency_days decay → consistency_ratio component → confidence (from SE) → weighted sum (40/25/15/10/10) → Learning Analytics Service → Learning Velocity Tracking → compute_velocity() → delta_mastery / weeks_elapsed → Risk Signal Classification → compute_risk_signal() → urgent: score<0.4 OR idle>30d → at_risk: score<0.6 OR idle>14d → on_track: otherwise → Next Best Activities → ranked by priority & mastery score
- **Concurrency Safety:** Mastery calculation is deterministic. Velocity calculation is stateless. Risk classification is deterministic. No distributed locks needed
- **Covered Objects:** Mastery tracking, IRT conversion, learning velocity, risk signals, intervention guidance
- **Timeouts:** Theta conversion: ~1-5ms. Composite score: ~1-5ms. Velocity calculation: ~1-5ms. Risk classification: ~1-5ms. Total: ~4-20ms
- **Migration Path:** From simple to comprehensive tracking. Migration requires: 1) Implement IRT conversion, 2) Add composite scoring, 3) Add velocity tracking, 4) Add risk classification
- **Error Handling:** Conversion errors logged. Scoring errors logged. Velocity errors logged. Risk errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate theta estimates. Protect learner data. Audit mastery results. Validate risk signals. Filter sensitive data

**Trace text diagram:**
```
Progress Tracking & Mastery Model
├── IRT Ability → Mastery Conversion
│   └── theta_to_mastery() <-- 7a
│       └── erf(theta / sqrt(2)) normalization <-- mastery_model.py:16
├── Composite Mastery Score Calculation
│   └── compute_mastery_score() <-- 7b
│       ├── mastery_theta (from IRT) <-- mastery_model.py:38
│       ├── practice_accuracy component <-- mastery_model.py:39
│       ├── recency_days decay <-- mastery_model.py:40
│       ├── consistency_ratio component <-- mastery_model.py:41
│       ├── confidence (from SE) <-- mastery_model.py:42
│       └── weighted sum (40/25/15/10/10) <-- 7c
└── Learning Analytics Service
    ├── Learning Velocity Tracking
    │   └── compute_velocity() <-- 7d
    │       └── delta_mastery / weeks_elapsed <-- learning_velocity_service.py:15
    ├── Risk Signal Classification
    │   └── compute_risk_signal() <-- 7e
    │       ├── urgent: score<0.4 OR idle>30d <-- learning_velocity_service.py:18
    │       ├── at_risk: score<0.6 OR idle>14d <-- learning_velocity_service.py:20
    │       └── on_track: otherwise <-- learning_velocity_service.py:22
    └── Next Best Activities <-- learning_velocity_service.py:24
        └── ranked by priority & mastery score <-- learning_velocity_service.py:42
```

**Location ID: 7a**
- **Title:** Convert theta to mastery
- **Description:** Transform IRT ability to 0-1 mastery score using error function
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/progress/mastery_model.py:15

**Location ID: 7b**
- **Title:** Compute composite score
- **Description:** Weighted combination of theta, practice, recency, consistency
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/progress/mastery_model.py:31

**Location ID: 7c**
- **Title:** Weight mastery dimensions
- **Description:** 40% ability, 25% practice, 15% recency, 10% consistency, 10% confidence
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/progress/mastery_model.py:43

**Location ID: 7d**
- **Title:** Compute learning velocity
- **Description:** Rate of mastery change per week from snapshot history
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/progress/learning_velocity_service.py:8

**Location ID: 7e**
- **Title:** Compute risk signal
- **Description:** Classify learner as urgent, at_risk, or on_track for intervention
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/progress/learning_velocity_service.py:17

### AI Guide: Mastery Model Computation

**Motivation:**
EduBoost's progress module implements comprehensive mastery tracking to measure learner progress accurately and identify learners needing intervention. Instead of simple percentage scores, the system uses IRT-based ability estimates combined with practice performance, recency, consistency, and confidence to create a holistic mastery score.

The system also tracks learning velocity (rate of mastery change over time) and computes risk signals to classify learners as urgent, at-risk, or on-track. This enables proactive intervention by guardians and teachers before learners fall behind.

**Details:**

**IRT Ability to Mastery Conversion**
The theta_to_mastery() function [7a] transforms IRT ability estimates (theta, typically ranging from -5 to +5) to a 0-1 mastery score using the error function: mastery = 0.5 * (1 + erf(θ / √2)). This normalization maps theta to a percentage-like score where 0.5 represents average ability, 0.0 represents very low ability, and 1.0 represents very high ability.

**Composite Mastery Score**
The compute_mastery_score() function [7b] combines multiple dimensions into a single mastery score:

- mastery_theta (40%): IRT-based ability estimate
- practice_accuracy (25%): Recent practice question accuracy
- recency_days (15%): Decay factor based on days since last activity
- consistency_ratio (10%): Ratio of consistent vs. inconsistent performance
- confidence (10%): 1 - (standard_error / 2), measuring estimate reliability

The weighted sum [7c] ensures that ability is the primary factor while still accounting for practice performance and engagement.

**Learning Velocity Tracking**
The compute_velocity() function [7d] calculates the rate of mastery change per week by comparing mastery snapshots over time: velocity = delta_mastery / weeks_elapsed. Positive velocity indicates improvement, while negative velocity indicates regression. This metric helps identify whether a learner is accelerating, plateauing, or declining.

**Risk Signal Classification**
The compute_risk_signal() function [7e] classifies learners into three categories for intervention:

- urgent: mastery < 0.4 OR idle > 30 days OR velocity < -0.01
- at_risk: mastery < 0.6 OR idle > 14 days OR velocity < 0
- on_track: otherwise

These thresholds are calibrated for primary school learners and trigger alerts to guardians and teachers when intervention is needed.

**Next Best Activities**
The system ranks recommended activities by priority and mastery score to guide learners toward the most impactful next steps—typically diagnostic gaps with low mastery scores.

## Trace ID: 8
**Title:** Background Job Execution (Jobs Module)

**Description:** ARQ async worker for consent reminders, RLHF batch processing, diagnostic session expiry, and database backups with Prometheus metrics.

**Motivation:**
EduBoost V2's jobs module implements ARQ async worker for background job execution. The WorkerSettings Configuration includes functions registry and cron_jobs schedule with Daily 00:00 UTC: run_database_backup, Daily 06:00 UTC: consent reminders, and Hourly: expire_stale_diagnostic_sessions. The Consent Renewal Job (Daily 08:00 SAST) calls send_consent_renewal_reminders() and run_consent_reminder_cycle() which queries expiring consents, decrypts guardian emails, and sends SendGrid notifications. The Diagnostic Session Expiry (Hourly) calls expire_stale_diagnostic_sessions(), calculates 24h cutoff timestamp, UPDATEs DiagnosticSession WHERE..., and increments Prometheus metrics. The Database Backup Job (Daily 00:00 UTC) calls run_database_backup(), prepares environment with encryption key, executes scripts/backup_postgres.sh, and returns status + output tail. This background job system ensures automated maintenance, compliance reminders, session cleanup, and data protection.

**Details:**
- **Execution Flow:** WorkerSettings Configuration → functions registry → cron_jobs schedule → Daily 00:00 UTC: run_database_backup → Daily 06:00 UTC: consent reminders → Hourly: expire_stale_diagnostic_sessions → Consent Renewal Job (Daily 08:00 SAST) → send_consent_renewal_reminders() → run_consent_reminder_cycle() → Query expiring consents → Decrypt guardian emails → Send SendGrid notifications → Diagnostic Session Expiry (Hourly) → expire_stale_diagnostic_sessions() → Calculate 24h cutoff timestamp → UPDATE DiagnosticSession WHERE... → Increment Prometheus metrics → Database Backup Job (Daily 00:00 UTC) → run_database_backup() → Prepare environment with encryption key → Execute scripts/backup_postgres.sh → Return status + output tail
- **Concurrency Safety:** Jobs are scheduled independently. Database operations use transactions. No distributed locks needed
- **Covered Objects:** Background jobs, ARQ worker, consent reminders, session expiry, database backups, Prometheus metrics
- **Timeouts:** Consent reminders: ~1-5min. Session expiry: ~10-50ms. Database backup: ~5-30min. Total: ~6-35min
- **Migration Path:** From manual to automated jobs. Migration requires: 1) Implement ARQ worker, 2) Add cron schedules, 3) Implement job functions, 4) Add metrics
- **Error Handling:** Job failures logged. Decryption errors logged. Email errors logged. Backup errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate job payloads. Encrypt backups. Secure email sending. Audit job execution. Protect sensitive data. Validate cron schedules

**Trace text diagram:**
```
ARQ Background Job System
├── WorkerSettings Configuration <-- jobs.py:263
│   ├── functions registry <-- 8f
│   └── cron_jobs schedule <-- jobs.py:285
│       ├── Daily 00:00 UTC: run_database_backup <-- jobs.py:287
│       ├── Daily 06:00 UTC: consent reminders <-- jobs.py:289
│       └── Hourly: expire_stale_diagnostic_sessions <-- jobs.py:291
│
├── Consent Renewal Job (Daily 08:00 SAST)
│   ├── send_consent_renewal_reminders() <-- 8a
│   └── run_consent_reminder_cycle() <-- 8b
│       ├── Query expiring consents <-- jobs.py:48
│       ├── Decrypt guardian emails <-- jobs.py:226
│       └── Send SendGrid notifications <-- jobs.py:240
│
├── Diagnostic Session Expiry (Hourly)
│   ├── expire_stale_diagnostic_sessions() <-- 8c
│   ├── Calculate 24h cutoff timestamp <-- jobs.py:111
│   ├── UPDATE DiagnosticSession WHERE... <-- 8d
│   └── Increment Prometheus metrics <-- jobs.py:124
│
└── Database Backup Job (Daily 00:00 UTC)
    ├── run_database_backup() <-- 8e
    ├── Prepare environment with encryption key <-- jobs.py:164
    ├── Execute scripts/backup_postgres.sh <-- jobs.py:175
    └── Return status + output tail <-- jobs.py:187
```

**Location ID: 8a**
- **Title:** Consent reminder job
- **Description:** Daily cron at 08:00 SAST for expiring consent notifications
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/jobs.py:46

**Location ID: 8b**
- **Title:** Execute reminder cycle
- **Description:** Process expiring consents and send guardian emails
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/jobs.py:48

**Location ID: 8c**
- **Title:** Expire diagnostic sessions
- **Description:** Hourly job marks incomplete sessions older than 24h as abandoned
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/jobs.py:85

**Location ID: 8d**
- **Title:** Update stale sessions
- **Description:** Bulk update DiagnosticSession records past cutoff timestamp
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/jobs.py:113

**Location ID: 8e**
- **Title:** Database backup job
- **Description:** Daily encrypted PostgreSQL backup at 00:00 UTC
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/jobs.py:134

**Location ID: 8f**
- **Title:** Register worker functions
- **Description:** ARQ WorkerSettings with job registry and cron schedules
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/jobs.py:278

### AI Guide: Background Job Execution

**Motivation:**
EduBoost needs reliable background processing for work that should not block learner-facing API requests. The jobs module solves this by using ARQ async workers for scheduled compliance reminders, diagnostic cleanup, RLHF batch processing, and encrypted database backups.

These jobs protect operational reliability and POPIA compliance: guardians must be reminded before consent expires, stale diagnostic sessions must not remain active indefinitely, and backups must run automatically with encryption.

**Details:**

**Worker Registration**
WorkerSettings registers the ARQ functions [8f] and cron schedules that drive the background system. The schedule includes daily database backups, daily consent reminders, and hourly diagnostic session expiry. This central registry makes job availability explicit and keeps operational tasks separate from request/response code.

**Consent Renewal Reminders**
The consent reminder job [8a] delegates to run_consent_reminder_cycle() [8b]. The cycle queries expiring consent records, decrypts guardian email addresses only when needed for delivery, and sends notifications through SendGrid. This supports POPIA compliance by giving guardians enough notice to renew consent before learner access is interrupted.

**Diagnostic Session Expiry**
The expire_stale_diagnostic_sessions() job [8c] runs hourly and computes a 24-hour cutoff timestamp. It bulk updates matching DiagnosticSession records [8d] to mark incomplete stale sessions as abandoned, then increments Prometheus metrics. This prevents old assessment state from affecting learner progress or analytics.

**Encrypted Database Backups**
The run_database_backup() job [8e] prepares the backup environment, injects the encryption key, executes scripts/backup_postgres.sh, and returns status metadata plus the output tail. Running backups through ARQ gives the platform a scheduled, auditable recovery mechanism without tying backups to API process uptime.

**Operational Safety**
Each job validates payloads before execution and reports meaningful results or metrics. Sensitive operations—such as decrypting guardian email addresses and passing backup encryption keys—are isolated to job execution paths, reducing accidental exposure in ordinary API flows.

## Trace ID: 9
**Title:** Module Integration with API (Router Registration)

**Description:** FastAPI application integrates modules via routers. Shows how domain modules expose HTTP endpoints through the V2 API.

**Motivation:**
EduBoost V2's modular architecture integrates domain modules with the FastAPI application via routers. The FastAPI Application (api_v2.py) imports module routers from app.modules.practice and app.api_v2_routers including lessons and diagnostics. The Router Registry maps module names to router instances with ("lessons", lessons.router), ("diagnostics", diagnostics.router), and ("practice", practice_router.router). The app.include_router() is called for each module. The Lessons Router imports LessonService, defines POST /lessons/generate endpoint with consent gate check, and calls service.generate_lesson_for_learner() with LessonService dependency injection. The Diagnostics Router imports ItemBankService. The LessonService.__init__() dependencies include ExecutiveService, LessonRepository, and ConsentService(db) for cross-module consent enforcement. This modular integration enables clean separation of concerns, dependency injection, and cross-module collaboration.

**Details:**
- **Execution Flow:** FastAPI Application (api_v2.py) → Module imports → from app.modules.practice import router → from app.api_v2_routers import lessons → from app.api_v2_routers import diagnostics → Router registry → ("lessons", lessons.router) → ("diagnostics", diagnostics.router) → ("practice", practice_router.router) → app.include_router() for each module → Lessons Router (api_v2_routers/lessons.py) → Import LessonService → POST /lessons/generate endpoint → Consent gate check → service.generate_lesson_for_learner() → LessonService dependency injection → Diagnostics Router (api_v2_routers/diagnostics.py) → Import ItemBankService → LessonService (modules/lessons/service.py) → __init__() dependencies → ExecutiveService → LessonRepository → ConsentService(db) → generate_lesson_for_learner() → Cross-module consent enforcement
- **Concurrency Safety:** Router registration is at startup. Dependency injection is per-request. Cross-module calls are synchronous. No distributed locks needed
- **Covered Objects:** Module integration, router registration, dependency injection, cross-module collaboration, consent enforcement
- **Timeouts:** Router registration: ~10-50ms. Dependency injection: ~1-5ms. Cross-module calls: ~10-50ms. Total: ~21-105ms
- **Migration Path:** From monolithic to modular. Migration requires: 1) Extract modules, 2) Create routers, 3) Register routers, 4) Wire dependencies
- **Error Handling:** Registration errors logged. Dependency errors logged. Cross-module errors logged. All errors logged with context. Sensitive data not logged
- **Security Considerations:** Validate router registration. Secure dependency injection. Enforce consent gates. Validate cross-module calls. Protect module boundaries

**Trace text diagram:**
```
FastAPI Application (api_v2.py)
├── Module imports <-- 9a
│   ├── from app.modules.practice import router
│   ├── from app.api_v2_routers import lessons <-- api_v2.py:239
│   └── from app.api_v2_routers import diagnostics <-- api_v2.py:239
├── Router registry <-- 9b
│   ├── ("lessons", lessons.router) <-- api_v2.py:270
│   ├── ("diagnostics", diagnostics.router) <-- api_v2.py:272
│   └── ("practice", practice_router.router) <-- api_v2.py:273
└── app.include_router() for each module

Lessons Router (api_v2_routers/lessons.py)
├── Import LessonService <-- 9c
├── POST /lessons/generate endpoint <-- lessons.py:30
│   ├── Consent gate check <-- lessons.py:42
│   └── service.generate_lesson_for_learner() <-- 9d
└── LessonService dependency injection <-- lessons.py:27

Diagnostics Router (api_v2_routers/diagnostics.py)
└── Import ItemBankService <-- 9e

LessonService (modules/lessons/service.py)
├── __init__() dependencies <-- service.py:67
│   ├── ExecutiveService <-- service.py:79
│   ├── LessonRepository <-- service.py:80
│   └── ConsentService(db) <-- 9f
└── generate_lesson_for_learner() <-- service.py:86
    └── Cross-module consent enforcement
```

**Location ID: 9a**
- **Title:** Import module routers
- **Description:** Load routers from modules and api_v2_routers packages
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:238

**Location ID: 9b**
- **Title:** Router registry
- **Description:** Central registry mapping module names to router instances
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:264

**Location ID: 9c**
- **Title:** Import lesson service
- **Description:** Router depends on module service for business logic
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/lessons.py:18

**Location ID: 9d**
- **Title:** Invoke service method
- **Description:** Router delegates to LessonService for lesson generation
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/lessons.py:45

**Location ID: 9e**
- **Title:** Import diagnostic services
- **Description:** Diagnostics router uses IRT engine and item bank service
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2_routers/diagnostics.py:21

**Location ID: 9f**
- **Title:** Cross-module dependency
- **Description:** LessonService depends on ConsentService for POPIA gate
- **Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/lessons/service.py:83

### AI Guide: Module Integration with API

**Motivation:**
EduBoost V2 uses a modular monolith architecture: domain modules own business logic, while FastAPI routers expose those capabilities through HTTP endpoints. This trace explains how the application composes modules at startup, registers routers consistently, and delegates request handling into module services.

The architecture keeps domain logic out of API plumbing while still allowing modules to collaborate. For example, lesson generation is exposed through the lessons router, but the LessonService depends on ConsentService so POPIA gates are enforced inside the service layer, not only at the route boundary.

**Details:**

**Router Imports**
The FastAPI application imports module routers and API router packages at startup [9a]. This includes routers from app.api_v2_routers such as lessons and diagnostics, plus module-owned routers such as practice. Import-time failures surface early during application startup instead of during learner requests.

**Central Router Registry**
The ROUTER_REGISTRY [9b] maps stable module names to router instances, then the application includes each router through app.include_router(). This provides a single integration point for the API surface and makes it easier to audit which modules are exposed under /api/v2.

**Route-to-Service Delegation**
The lessons router imports LessonService [9c] and the POST /lessons/generate endpoint delegates generation to service.generate_lesson_for_learner() [9d]. The router handles transport concerns—request parsing, current user extraction, and response shaping—while the service owns business rules, persistence, and cross-module checks.

**Diagnostics Module Integration**
The diagnostics router imports ItemBankService and related diagnostic services [9e]. This exposes IRT-backed assessment capabilities through the V2 API while keeping the mathematical item-selection logic in app/modules/diagnostics rather than embedding it in endpoint handlers.

**Cross-Module Consent Enforcement**
LessonService constructs a ConsentService dependency [9f], allowing lesson generation to require active parental consent before AI content is created. This is a critical architectural boundary: modules may collaborate through explicit service dependencies, but legal and security gates remain enforced in the service layer where business workflows execute.

**Modular Boundary Rules**
Routers should stay thin, services should own orchestration, and repositories should own persistence. New modules should follow the same integration pattern: define a module service, expose a router, register the router centrally, and use explicit dependencies for cross-module operations.
