# EduBoost V2 ORM Models: Domain Entities, Assessment System, Content Factory, and POPIA Compliance

Comprehensive map of EduBoost V2's SQLAlchemy ORM layer covering 40+ models across five subsystems: core domain (Guardian/LearnerProfile/ParentalConsent), IRT assessment (DiagnosticItem/ItemExposure/DiagnosticSession), content delivery (Lesson/KnowledgeGap), content factory (ContentGenerationArtifact/ContentScope), and auth extensions (SecureToken/OnboardingState/PrivacySettings). Key architectural patterns include bidirectional relationships via relationship(), CASCADE delete enforcement, POPIA compliance through soft-deletes and consent gating, IRT parameter storage for adaptive assessment, and AI generation metadata tracking.

## Trace ID: 1
**Title:** Guardian → LearnerProfile → ParentalConsent relationship chain

**Description:** Core domain models establishing the guardian-learner-consent hierarchy with POPIA compliance enforcement

**Trace text diagram:**
```
app/models/__init__.py - Core Domain Models
├── Guardian (Parent/Teacher Account) <-- 1a
│   ├── email_encrypted, password_hash <-- __init__.py:104
│   ├── subscription_tier (free/premium) <-- __init__.py:108
│   ├── stripe_customer_id <-- __init__.py:111
│   └── relationships
│       ├── learners: List[LearnerProfile] <-- 1b
│       ├── consents: List[ParentalConsent] <-- __init__.py:133
│       ├── secure_tokens: List[SecureToken] <-- __init__.py:134
│       ├── onboarding_state: OnboardingState <-- __init__.py:135
│       └── privacy_settings: PrivacySettings <-- __init__.py:136
│
├── LearnerProfile (Pseudonymized Learner) <-- 1c
│   ├── guardian_id FK → guardians.id <-- 1d
│   ├── pseudonym_id (unique, indexed) <-- __init__.py:146
│   ├── grade, language, archetype <-- __init__.py:149
│   ├── theta (IRT ability estimate) <-- __init__.py:152
│   ├── is_deleted (POPIA soft-delete) <-- __init__.py:156
│   └── relationships
│       ├── guardian: Guardian <-- __init__.py:161
│       ├── consents: List[ParentalConsent] <-- 1e
│       ├── diagnostic_sessions <-- __init__.py:165
│       ├── knowledge_gaps <-- __init__.py:163
│       └── lessons <-- __init__.py:166
│
└── ParentalConsent (POPIA Compliance) <-- 1f
    ├── guardian_id FK → guardians.id <-- __init__.py:188
    ├── learner_id FK → learner_profiles.id <-- __init__.py:189
    ├── policy_version, status <-- __init__.py:190
    ├── granted_at, expires_at, revoked_at <-- __init__.py:192
    └── @property is_active() <-- 1g
        └── checks: not revoked, not expired,
            status in {GRANTED, RENEWAL_REQUIRED}
```

**Location ID: 1a**
**Title:** Guardian model definition
**Description:** Parent/teacher account with encrypted email, subscription tier, and Stripe integration
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:99

**Location ID: 1b**
**Title:** Guardian owns multiple learners
**Description:** One-to-many relationship: guardian can manage multiple learner profiles
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:132

**Location ID: 1c**
**Title:** LearnerProfile model definition
**Description:** Pseudonymized learner with IRT theta, grade, language, and soft-delete support
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:142

**Location ID: 1d**
**Title:** Learner belongs to guardian
**Description:** Foreign key with CASCADE delete: removing guardian removes all learners
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:147

**Location ID: 1e**
**Title:** Learner has consent records
**Description:** One-to-many: learner can have multiple consent records (renewal/revocation history)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:162

**Location ID: 1f**
**Title:** ParentalConsent model definition
**Description:** POPIA compliance: tracks consent grants, expiry, revocation with audit trail
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:184

**Location ID: 1g**
**Title:** Consent active state computation
**Description:** Property checks not revoked, not expired, and status is GRANTED or RENEWAL_REQUIRED
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:206

### AI Guide: Guardian-Learner-Consent Relationship Chain

**Motivation:**
The guardian-learner-consent relationship chain establishes the core domain hierarchy for EduBoost V2's user management system. This three-tier model enables POPIA-compliant data handling by separating guardians (account holders) from learners (pseudonymized minors) with explicit consent tracking. The CASCADE delete relationships ensure data consistency when accounts are removed, while soft-delete support on learners enables POPIA-mandated data retention policies. The consent model provides audit trails for all consent grants, renewals, and revocations, ensuring compliance with South African data protection regulations.

**Details:**

**Guardian Model Structure**
Guardian serves as the account holder with encrypted credentials and subscription management [1a]. The email_encrypted field stores encrypted email addresses for privacy, while password_hash uses bcrypt for secure authentication. Subscription tier (free/premium) and stripe_customer_id enable payment integration. Relationships to learners, consents, secure tokens, onboarding state, and privacy settings establish the guardian as the central entity in the user hierarchy [1b].

**LearnerProfile Pseudonymization**
LearnerProfile represents pseudonymized minors to protect learner identity per POPIA requirements [1c]. The guardian_id foreign key with CASCADE delete ensures that removing a guardian also removes all associated learners [1d]. Pseudonym_id provides a unique, indexed identifier for learners without exposing personal information. The is_deleted flag implements POPIA soft-delete, allowing data retention while marking records as deleted. Theta stores IRT ability estimates for adaptive assessment, while grade, language, and archetype enable personalized learning [1e].

**ParentalConsent POPIA Compliance**
ParentalConsent tracks consent lifecycle with full audit trail for POPIA compliance [1f]. The model links both guardian_id and learner_id to establish who consented for which learner. Policy_version, status, granted_at, expires_at, and revoked_at provide complete consent history. The is_active property dynamically computes consent validity by checking that consent is not revoked, not expired, and status is GRANTED or RENEWAL_REQUIRED [1g]. This enables runtime consent gating for sensitive operations.

## Trace ID: 2
**Title:** DiagnosticItem → ItemExposure tracking for IRT assessment

**Description:** Assessment system models linking diagnostic items with IRT parameters to learner exposure history

**Trace text diagram:**
```
DiagnosticItem Model (IRT Assessment Item)
├── Class definition <-- 2a
├── IRT Parameters
│   ├── difficulty_b (logit scale) <-- 2b
│   ├── discrimination_a (0.5-2.5) <-- 2c
│   └── guessing_c (0.0-0.35) <-- diagnostic_item.py:196
├── Item metadata
│   ├── caps_ref, grade, subject, topic <-- diagnostic_item.py:156
│   ├── stem, answer_key, options <-- diagnostic_item.py:168
│   └── review_status, safety_passed <-- diagnostic_item.py:206
├── Exposure tracking
│   ├── exposure_count, max_exposure <-- diagnostic_item.py:216
│   └── exposures relationship <-- 2d
│       └── → ItemExposure (one-to-many)
└── Selection logic
    └── is_available_for_selection() <-- 2g
        └── checks: approved + below cap <-- diagnostic_item.py:254

ItemExposure Model (Append-Only Log)
├── Class definition <-- 2e
├── Foreign key to item <-- 2f
│   └── ondelete="RESTRICT"
├── Event data
│   ├── learner_id, session_id <-- item_exposure.py:62
│   ├── served_at, answered_at <-- item_exposure.py:72
│   ├── learner_response <-- item_exposure.py:81
│   ├── is_correct (scored) <-- item_exposure.py:82
│   └── response_time_ms <-- item_exposure.py:83
└── Relationship back to item
    └── item: DiagnosticItem <-- item_exposure.py:86
```

**Location ID: 2a**
**Title:** DiagnosticItem model definition
**Description:** CAPS-aligned assessment item with IRT 3PL parameters (a, b, c) and review workflow
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/diagnostic_item.py:109

**Location ID: 2b**
**Title:** IRT difficulty parameter
**Description:** b parameter: item difficulty on logit scale (-3.0 to 3.0)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/diagnostic_item.py:190

**Location ID: 2c**
**Title:** IRT discrimination parameter
**Description:** a parameter: item discrimination (0.5 to 2.5), higher means better differentiates ability
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/diagnostic_item.py:193

**Location ID: 2d**
**Title:** Item tracks all exposures
**Description:** One-to-many: item has exposure history across all learners (lazy loading for performance)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/diagnostic_item.py:242

**Location ID: 2e**
**Title:** ItemExposure model definition
**Description:** Append-only log of item served to learner with response correctness and timing
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/item_exposure.py:27

**Location ID: 2f**
**Title:** Exposure links to item
**Description:** Foreign key with RESTRICT: cannot delete item if it has exposure history
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/item_exposure.py:56

**Location ID: 2g**
**Title:** Item selection eligibility
**Description:** Property checks if item is approved and below exposure cap for adaptive selection
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/diagnostic_item.py:251

### AI Guide: Diagnostic Item and Exposure Tracking

**Motivation:**
The DiagnosticItem and ItemExposure models implement Item Response Theory (IRT) assessment with exposure tracking for adaptive learning. DiagnosticItem stores CAPS-aligned assessment items with 3-parameter logistic (3PL) IRT parameters (difficulty, discrimination, guessing) that enable adaptive item selection based on learner ability. ItemExposure provides an append-only log of every item served to learners, enabling exposure cap enforcement to prevent item overuse and IRT parameter recalibration. The RESTRICT foreign key ensures items with exposure history cannot be deleted, preserving assessment integrity.

**Details:**

**IRT Parameter Storage**
DiagnosticItem stores IRT 3PL parameters for adaptive assessment [2a]. Difficulty_b (b parameter) represents item difficulty on logit scale (-3.0 to 3.0), where higher values indicate harder items [2b]. Discrimination_a (a parameter) ranges from 0.5 to 2.5, with higher values indicating better ability to discriminate between learners of different ability levels [2c]. Guessing_c (c parameter) ranges from 0.0 to 0.35, representing the probability of correct guessing. These parameters enable the IRT engine to select items that match learner ability for optimal measurement precision.

**Exposure Tracking and Caps**
ItemExposure maintains an append-only log of every item served to learners [2e]. Each exposure record captures learner_id, session_id, served_at, answered_at, learner_response, is_correct, and response_time_ms. The foreign key to DiagnosticItem uses ondelete="RESTRICT" to prevent deletion of items that have exposure history, preserving assessment data integrity [2f]. DiagnosticItem tracks exposure_count and max_exposure to enforce exposure caps, preventing item overuse that could compromise assessment security [2d].

**Item Selection Logic**
The is_available_for_selection property determines if an item can be served in an assessment [2g]. It checks that the item is approved (review_status and safety_passed) and that exposure_count is below max_exposure. This gate ensures only vetted items are used and prevents item overexposure. The lazy-loaded exposures relationship allows efficient access to exposure history when needed without impacting item selection performance.

## Trace ID: 3
**Title:** LearnerProfile → DiagnosticSession → KnowledgeGap flow

**Description:** Assessment workflow linking learner to diagnostic sessions that identify knowledge gaps

**Trace text diagram:**
```
LearnerProfile Model <-- __init__.py:142
├── diagnostic_sessions relationship <-- 3a
│   └── One-to-many: learner → sessions
│
└── DiagnosticSession Model
    ├── class DiagnosticSession(Base) <-- 3b
    ├── theta_before: IRT ability estimate <-- 3c
    ├── gap_topics: JSONB array <-- 3d
    │   └── Topics where learner struggled
    └── learner_id foreign key <-- __init__.py:311
        └── CASCADE delete with learner

LearnerProfile Model (continued) <-- __init__.py:142
├── knowledge_gaps relationship <-- 3e
│   └── One-to-many: learner → gaps
│
└── KnowledgeGap Model
    ├── class KnowledgeGap(Base) <-- 3f
    ├── severity: Float 0-1 <-- 3g
    │   └── Gap prioritization score
    └── learner_id foreign key <-- __init__.py:348
        └── CASCADE delete with learner
```

**Location ID: 3a**
**Title:** Learner has diagnostic sessions
**Description:** One-to-many: learner accumulates diagnostic assessment attempts over time
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:165

**Location ID: 3b**
**Title:** DiagnosticSession model definition
**Description:** IRT assessment session with theta estimates, responses, and identified gaps
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:307

**Location ID: 3c**
**Title:** Pre-assessment ability estimate
**Description:** IRT theta before session: learner's estimated ability on logit scale
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:313

**Location ID: 3d**
**Title:** Session identifies gaps
**Description:** JSONB array of topics where learner struggled during assessment
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:317

**Location ID: 3e**
**Title:** Learner has persistent gaps
**Description:** One-to-many: learner accumulates identified knowledge gaps from diagnostics
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:163

**Location ID: 3f**
**Title:** KnowledgeGap model definition
**Description:** Persistent record of learner's topic weakness with severity and resolution tracking
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:344

**Location ID: 3g**
**Title:** Gap severity score
**Description:** Float 0-1: severity of knowledge gap (0=mild, 1=critical) for prioritization
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:352

### AI Guide: Diagnostic Session and Knowledge Gap Flow

**Motivation:**
The LearnerProfile to DiagnosticSession to KnowledgeGap flow implements the assessment-to-remediation pipeline. DiagnosticSession captures IRT assessment results including ability estimates (theta) and identified gap topics, enabling tracking of learner progress over time. KnowledgeGap provides persistent records of learner weaknesses with severity scores for targeted lesson generation. The CASCADE delete relationships ensure that when a learner is deleted, all associated sessions and gaps are removed, maintaining data consistency.

**Details:**

**Diagnostic Session Tracking**
DiagnosticSession stores complete assessment session data for IRT analysis [3b]. Theta_before and theta_after capture learner ability estimates before and after the session, enabling measurement of learning gains [3c]. Responses field stores item-level responses in JSONB format for detailed analysis. Gap_topics is a JSONB array identifying topics where the learner struggled during the assessment [3d]. Session_state tracks the assessment lifecycle (in_progress, completed, abandoned). The learner_id foreign key with CASCADE delete ensures sessions are removed when the learner is deleted.

**Knowledge Gap Persistence**
KnowledgeGap provides persistent tracking of learner weaknesses identified across multiple diagnostic sessions [3f]. Each gap record includes subject, topic, severity (0-1 float for prioritization), resolved flag, and timestamps [3g]. Severity scores enable gap prioritization for lesson generation, focusing on the most critical weaknesses first. The resolved flag tracks whether a gap has been addressed through lessons. The learner_id foreign key with CASCADE delete ensures gaps are removed when the learner is deleted.

**Assessment-to-Remediation Pipeline**
The flow from DiagnosticSession to KnowledgeGap enables automated remediation. After a diagnostic session completes, the IRT engine identifies gap_topics based on item response patterns. These topics are persisted as KnowledgeGap records with severity scores. The lesson generation system queries KnowledgeGap to create targeted lessons addressing specific weaknesses. This closed-loop system enables continuous assessment and personalized learning.

## Trace ID: 4
**Title:** Lesson model with AI generation metadata and learner linkage

**Description:** Content delivery model storing AI-generated lessons with quality metrics, CAPS alignment, and learner context

**Trace text diagram:**
```
Lesson Model Architecture
├── Lesson ORM Definition <-- 4a
│   ├── Learner Relationship
│   │   └── learner_id FK (CASCADE) <-- 4b
│   ├── Knowledge Gap Linkage
│   │   └── knowledge_gap_id FK (optional) <-- 4c
│   ├── Content Storage
│   │   └── content: Text field <-- 4d
│   ├── Quality Metrics
│   │   └── alignment_confidence: Float <-- 4e
│   └── AI Generation Metadata
│       ├── provider: String <-- 4f
│       └── token_usage: JSONB <-- 4g
└── Relationships to Other Models
    ├── → LearnerProfile (many-to-one) <-- __init__.py:539
    ├── → KnowledgeGap (optional many-to-one)
    └── Used by LessonRepository <-- lesson_repository.py:15
```

**Location ID: 4a**
**Title:** Lesson model definition
**Description:** AI-generated CAPS-aligned lesson with content, metadata, and quality tracking
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:481

**Location ID: 4b**
**Title:** Lesson belongs to learner
**Description:** Foreign key: lesson is personalized for specific learner with CASCADE delete
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:485

**Location ID: 4c**
**Title:** Lesson targets gap
**Description:** Optional link: lesson can be generated to address specific knowledge gap
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:486

**Location ID: 4d**
**Title:** Lesson content storage
**Description:** Text field: full markdown/HTML lesson content generated by LLM
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:492

**Location ID: 4e**
**Title:** CAPS alignment score
**Description:** Float 0-1: confidence that lesson aligns with CAPS curriculum requirements
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:508

**Location ID: 4f**
**Title:** LLM provider tracking
**Description:** String: which AI provider generated this lesson (groq, anthropic, etc.)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:515

**Location ID: 4g**
**Title:** Token usage metadata
**Description:** JSONB: tracks prompt/completion tokens for cost analysis and monitoring
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:518

### AI Guide: Lesson Model with AI Generation Metadata

**Motivation:**
The Lesson model stores AI-generated personalized lessons with comprehensive metadata for quality tracking and cost management. Lessons are linked to specific learners (personalization) and optionally to knowledge gaps (targeted remediation). The model tracks AI generation metadata including provider, model version, token usage, and generation latency for cost analysis and performance monitoring. Quality metrics like alignment_confidence, pii_check_passed, and answer_key_verified ensure lesson quality before delivery to learners.

**Details:**

**Lesson Personalization and Targeting**
Lesson is personalized for specific learners through the learner_id foreign key with CASCADE delete [4a, 4b]. This ensures lessons are removed when learners are deleted. The optional knowledge_gap_id foreign key links lessons to specific knowledge gaps for targeted remediation [4c]. This enables the system to generate lessons addressing identified weaknesses. Grade, subject, language, and archetype fields enable curriculum-aligned content generation.

**Content Storage and Quality Metrics**
The content field stores full lesson content as text (markdown/HTML) generated by LLMs [4d]. Quality metrics include alignment_confidence (0-1 float measuring CAPS alignment) [4e], pii_check_passed (PII safety check), answer_key_verified (answer key validation), quality_score (overall quality), and trust_label (JSONB with detailed quality breakdown). These metrics ensure only high-quality lessons are delivered to learners.

**AI Generation Metadata**
The model tracks comprehensive AI generation metadata for cost analysis and monitoring [4f, 4g]. Provider and model_version fields identify which AI service generated the lesson. Token_usage (JSONB) tracks prompt and completion token counts for cost calculation. Generation_latency_ms measures generation time. Prompt_template_version enables tracking of prompt engineering iterations. Reviewed_at and reviewed_by fields support human review workflows.

## Trace ID: 5
**Title:** ContentGenerationArtifact → ContentArtifactSource → ContentArtifactReview pipeline

**Description:** Content factory models tracking AI-generated artifacts from generation through review to production promotion

**Trace text diagram:**
```
Content Factory Artifact Lifecycle
├── ContentGenerationArtifact model <-- 5a
│   ├── artifact_json (JSONB payload) <-- 5b
│   ├── status (lifecycle enum) <-- 5c
│   │   └── GENERATED → PENDING_REVIEW → APPROVED <-- content_factory.py:41
│   ├── sources relationship (1-to-many) <-- 5d
│   │   └── ContentArtifactSource model <-- 5e
│   │       ├── source_document_id <-- content_factory.py:233
│   │       ├── source_chunk_id <-- content_factory.py:234
│   │       └── ETL provenance metadata <-- content_factory.py:251
│   └── reviews relationship (1-to-many) <-- 5f
│       └── ContentArtifactReview model <-- 5g
│           ├── reviewer_id <-- content_factory.py:277
│           ├── review_action (approve/reject) <-- content_factory.py:278
│           └── quality_score <-- content_factory.py:283
```

**Location ID: 5a**
**Title:** ContentGenerationArtifact definition
**Description:** Central model for AI-generated content with lifecycle status and quality metrics
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:176

**Location ID: 5b**
**Title:** Artifact payload storage
**Description:** JSONB: full generated content (lesson, item, blueprint) stored as structured JSON
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:201

**Location ID: 5c**
**Title:** Artifact lifecycle status
**Description:** Enum: tracks artifact through GENERATED → PENDING_REVIEW → APPROVED → PROMOTED
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:195

**Location ID: 5d**
**Title:** Artifact has source provenance
**Description:** One-to-many: artifact links to source documents/chunks used in generation
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:217

**Location ID: 5e**
**Title:** ContentArtifactSource definition
**Description:** Provenance record linking artifact to source curriculum documents and ETL metadata
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:228

**Location ID: 5f**
**Title:** Artifact has review history
**Description:** One-to-many: artifact accumulates human review actions (approve/reject/quarantine)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:218

**Location ID: 5g**
**Title:** ContentArtifactReview definition
**Description:** Review record with reviewer ID, action (approve/reject), reason, and quality score
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:272

### AI Guide: Content Factory Artifact Lifecycle

**Motivation:**
The ContentGenerationArtifact, ContentArtifactSource, and ContentArtifactReview models implement a complete content factory pipeline with provenance tracking and human review. ContentGenerationArtifact stores AI-generated content with lifecycle status tracking from generation through review to production promotion. ContentArtifactSource provides provenance by linking artifacts to source curriculum documents and ETL metadata. ContentArtifactReview enables human review workflow with approval/rejection actions and quality scoring. This system ensures content quality, traceability, and regulatory compliance.

**Details:**

**Artifact Lifecycle Management**
ContentGenerationArtifact is the central model for AI-generated content [5a]. The artifact_json field stores the full generated content (lesson, item, blueprint) as structured JSON [5b]. Status enum tracks the artifact lifecycle: GENERATED → PENDING_REVIEW → APPROVED → PROMOTED [5c]. This enables workflow gating where only approved artifacts are promoted to production. Artifact_hash provides deduplication and integrity checking. Schema_version enables schema evolution support.

**Source Provenance Tracking**
ContentArtifactSource provides complete provenance by linking artifacts to source documents [5d, 5e]. Source_document_id and source_chunk_id identify the specific curriculum content used in generation. ETL metadata includes extraction timestamp, normalization status, and quality scores. This provenance enables content auditing, regulatory compliance, and reproducibility. The one-to-many relationship allows artifacts to cite multiple source documents.

**Human Review Workflow**
ContentArtifactReview enables human review of AI-generated content [5f, 5g]. Each review record includes reviewer_id, review_action (approve/reject/quarantine), reason, and quality_score. The one-to-many relationship allows multiple reviews per artifact, enabling review history and re-review. This workflow ensures content quality before promotion to production. Review actions trigger status transitions in the artifact lifecycle.

## Trace ID: 6
**Title:** ContentScope → ContentCoverageTarget → ContentGenerationRun orchestration

**Description:** Content factory planning models defining generation scopes, coverage targets, and batch run coordination

**Trace text diagram:**
```
Content Factory Planning & Orchestration
├── ContentScope: Generation Boundary
│   ├── ContentScope model definition <-- 6a
│   └── scope_id primary key <-- 6b
│       (e.g., "grade4_mathematics_en_CAPS")
│
├── ContentCoverageTarget: Artifact Quotas
│   ├── ContentCoverageTarget model <-- 6c
│   │   (per CAPS ref within scope)
│   └── target_count specification <-- 6d
│       (how many artifacts needed)
│
└── ContentGenerationRun: Batch Execution
    ├── ContentGenerationRun model <-- 6e
    │   (coordinates multiple tasks)
    ├── scope_id foreign key <-- 6f
    │   (links run to scope boundary)
    └── ContentGenerationTask model <-- 6g
        (individual task with retry logic)
```

**Location ID: 6a**
**Title:** ContentScope definition
**Description:** Defines generation boundary: grade + subject + language + curriculum combination
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:78

**Location ID: 6b**
**Title:** Scope identifier
**Description:** String PK: composite key like 'grade4_mathematics_en_CAPS' for scope identity
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:81

**Location ID: 6c**
**Title:** ContentCoverageTarget definition
**Description:** Specifies how many artifacts needed per CAPS reference within a scope
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:104

**Location ID: 6d**
**Title:** Target artifact count
**Description:** Integer: how many items/lessons/blueprints needed for this CAPS ref
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:114

**Location ID: 6e**
**Title:** ContentGenerationRun definition
**Description:** Batch generation job coordinating multiple tasks across a scope
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:124

**Location ID: 6f**
**Title:** Run targets scope
**Description:** Foreign key: generation run operates within specific content scope boundary
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:128

**Location ID: 6g**
**Title:** ContentGenerationTask definition
**Description:** Individual generation task within run with retry logic and dependency tracking
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/content_factory.py:139

### AI Guide: Content Factory Planning and Orchestration

**Motivation:**
The ContentScope, ContentCoverageTarget, ContentGenerationRun, and ContentGenerationTask models implement content factory planning and orchestration. ContentScope defines generation boundaries (grade + subject + language + curriculum). ContentCoverageTarget specifies artifact quotas per CAPS reference within a scope. ContentGenerationRun coordinates batch generation jobs across a scope. ContentGenerationTask represents individual generation tasks with retry logic. This hierarchical planning system enables systematic content generation with clear targets and progress tracking.

**Details:**

**Generation Boundary Definition**
ContentScope defines the generation boundary as a combination of grade, subject_code, language, and curriculum [6a]. The scope_id serves as a composite primary key (e.g., "grade4_mathematics_en_CAPS") for scope identity [6b]. This enables scoped content generation ensuring curriculum alignment. Scopes can be defined for different grade levels, subjects, languages, and curricula (CAPS, etc.).

**Coverage Target Specification**
ContentCoverageTarget specifies how many artifacts are needed per CAPS reference within a scope [6c]. Each target includes caps_ref, artifact_type (lesson/item/blueprint), target_count, and minimum_approved_sources [6d]. Target_count defines the quota for that CAPS reference. Minimum_approved_sources ensures content diversity by requiring multiple source documents. This enables systematic coverage of curriculum requirements.

**Batch Job Orchestration**
ContentGenerationRun coordinates batch generation jobs across a scope [6e]. The scope_id foreign key links the run to a specific scope boundary [6f]. Status tracks the run lifecycle (pending, running, completed, failed). Requested_by identifies who initiated the run. ContentGenerationTask represents individual generation tasks within a run [6g]. Tasks include retry logic, dependency tracking, and status updates. This hierarchical structure enables parallel task execution with centralized coordination.

## Trace ID: 7
**Title:** SecureToken → OnboardingState → PrivacySettings auth extensions

**Description:** Authentication extension models for password reset, email verification, onboarding progress, and POPIA privacy controls

**Trace text diagram:**
```
Guardian Model <-- __init__.py:99
├── secure_tokens relationship <-- __init__.py:134
│   └── SecureToken Model <-- 7a
│       ├── user_id ForeignKey to guardians <-- 7b
│       ├── purpose (PASSWORD_RESET | EMAIL_VERIFY) <-- auth_extensions.py:67
│       ├── token_hash (bcrypt, never plaintext) <-- auth_extensions.py:68
│       ├── expires_at timestamp <-- auth_extensions.py:69
│       ├── used_at timestamp <-- auth_extensions.py:70
│       └── is_valid() property <-- 7c
├── onboarding_state relationship <-- __init__.py:135
│   └── OnboardingState Model <-- 7d
│       ├── email_verified boolean <-- auth_extensions.py:116
│       ├── profile_complete boolean <-- auth_extensions.py:117
│       ├── guardian_consent boolean <-- auth_extensions.py:118
│       ├── diagnostic_done boolean <-- auth_extensions.py:119
│       ├── plan_accepted boolean <-- auth_extensions.py:120
│       └── is_complete() property <-- 7e
└── privacy_settings relationship <-- __init__.py:136
    └── PrivacySettings Model <-- 7f
        ├── analytics_enabled boolean <-- auth_extensions.py:192
        ├── ai_improvement boolean <-- auth_extensions.py:193
        ├── marketing_emails boolean <-- auth_extensions.py:194
        ├── data_retention_days integer <-- 7g
        ├── show_leaderboard boolean <-- auth_extensions.py:196
        ├── export_requested_at timestamp <-- auth_extensions.py:198
        └── deletion_requested_at timestamp <-- auth_extensions.py:199
```

**Location ID: 7a**
**Title:** SecureToken definition
**Description:** One-use expiring token for password reset and email verification flows
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/auth_extensions.py:51

**Location ID: 7b**
**Title:** Token belongs to guardian
**Description:** Foreign key: token is issued for specific guardian with CASCADE delete
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/auth_extensions.py:64

**Location ID: 7c**
**Title:** Token validity check
**Description:** Property checks token not expired and not already used for consumption safety
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/auth_extensions.py:86

**Location ID: 7d**
**Title:** OnboardingState definition
**Description:** Tracks 5-step learner onboarding: email verify → profile → consent → diagnostic → plan
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/auth_extensions.py:97

**Location ID: 7e**
**Title:** Onboarding completion check
**Description:** Property checks all 5 onboarding steps completed for flow gating
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/auth_extensions.py:133

**Location ID: 7f**
**Title:** PrivacySettings definition
**Description:** POPIA-aligned per-user privacy controls: analytics, AI improvement, data retention
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/auth_extensions.py:172

**Location ID: 7g**
**Title:** Data retention period
**Description:** Integer: learner-selected retention window (90/365/730/0=unlimited) for POPIA compliance
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/auth_extensions.py:195

### AI Guide: Authentication Extensions for Security and POPIA Compliance

**Motivation:**
The SecureToken, OnboardingState, and PrivacySettings models extend the Guardian model with authentication workflows, onboarding tracking, and POPIA privacy controls. SecureToken implements one-use expiring tokens for password reset and email verification with bcrypt hashing for security. OnboardingState tracks the 5-step onboarding journey (email verify → profile → consent → diagnostic → plan) with completion gating. PrivacySettings provides granular per-user privacy controls aligned with POPIA section 11, including data retention periods and export/deletion request tracking.

**Details:**

**Secure Token Management**
SecureToken implements one-use expiring tokens for password reset and email verification flows [7a]. The user_id foreign key with CASCADE delete links tokens to guardians [7b]. Purpose field distinguishes between PASSWORD_RESET and EMAIL_VERIFY tokens. Token_hash stores bcrypt-hashed tokens (never plaintext) for security. Expires_at defines token lifetime. Used_at tracks when token was consumed. The is_valid property checks that token is not expired and not already used, preventing replay attacks [7c].

**Onboarding Progress Tracking**
OnboardingState tracks the 5-step learner onboarding journey [7d]. Boolean fields track completion of each step: email_verified, profile_complete, guardian_consent, diagnostic_done, and plan_accepted. The is_complete property checks all 5 steps are completed for flow gating [7e]. This enables progressive onboarding where users complete steps at their own pace. The relationship to Guardian ensures onboarding state is removed when the guardian is deleted.

**POPIA Privacy Controls**
PrivacySettings provides granular per-user privacy controls aligned with POPIA section 11 [7f]. Boolean flags control analytics_enabled, ai_improvement, marketing_emails, and show_leaderboard. Data_retention_days allows users to select retention windows (90/365/730/0=unlimited) for POPIA compliance [7g]. Export_requested_at and deletion_requested_at timestamps track POPIA data export and deletion requests. These controls give users agency over their data while enabling the system to comply with South African data protection regulations.

## Trace ID: 8
**Title:** Base declarative class and database session factory

**Description:** Core database infrastructure establishing SQLAlchemy async engine and session management

**Trace text diagram:**
```
SQLAlchemy ORM Infrastructure
├── Model Layer (app/models/)
│   └── Import Base from core.database <-- 8a
│       └── class Base(DeclarativeBase) <-- 8b
│
└── Database Core (app/core/database.py)
    ├── Engine Setup
    │   └── create_async_engine() <-- 8c
    │       └── AsyncSessionLocal factory <-- 8d
    │
    └── FastAPI Integration
        └── async def get_db() <-- 8e
            ├── yield session <-- database.py:65
            ├── Success Path
            │   └── await session.commit() <-- 8f
            └── Error Path <-- database.py:67
                └── await session.rollback() <-- 8g
```

**Location ID: 8a**
**Title:** Import declarative base
**Description:** All models inherit from shared Base for SQLAlchemy ORM mapping
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/models/__init__.py:29

**Location ID: 8b**
**Title:** Base declarative class
**Description:** Shared declarative base for all ORM models using SQLAlchemy 2.0 style
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:57

**Location ID: 8c**
**Title:** Async engine creation
**Description:** Creates async PostgreSQL engine with asyncpg driver and connection pooling
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:39

**Location ID: 8d**
**Title:** Session factory creation
**Description:** Configures async session maker with explicit commit/flush for transaction control
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:41

**Location ID: 8e**
**Title:** FastAPI dependency factory
**Description:** Yields async session per request with automatic commit/rollback/close
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:61

**Location ID: 8f**
**Title:** Session commit on success
**Description:** Commits transaction if no exceptions raised during request handling
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:66

**Location ID: 8g**
**Title:** Session rollback on error
**Description:** Rolls back transaction on exception to maintain database consistency
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/database.py:68

### AI Guide: SQLAlchemy ORM Infrastructure

**Motivation:**
The Base declarative class and database session factory establish the core SQLAlchemy ORM infrastructure for EduBoost V2. All models inherit from a shared Base class for consistent ORM mapping. The async engine with asyncpg driver enables high-performance asynchronous database operations. The session factory provides async sessions with explicit transaction control. The FastAPI dependency injection pattern yields sessions per request with automatic commit/rollback/close, ensuring database consistency and proper resource cleanup.

**Details:**

**Declarative Base Setup**
All models import Base from app.core.database [8a]. Base is a shared DeclarativeBase class using SQLAlchemy 2.0 style [8b]. This provides consistent ORM mapping across all models. The declarative base enables model definition using Python classes with type hints, improving type safety and IDE support. All models inherit from Base, ensuring they are registered with the SQLAlchemy metadata.

**Async Engine Configuration**
create_async_engine creates an async PostgreSQL engine with the asyncpg driver [8c]. Engine configuration includes connection pooling, pool size limits, and connection timeout settings. The async engine enables non-blocking database operations, critical for FastAPI's async architecture. AsyncSessionLocal is a session factory configured with expire_on_commit=False for detached object access [8d]. This pattern allows objects to be accessed after session commit without lazy loading issues.

**FastAPI Dependency Injection**
The get_db function is a FastAPI dependency that yields async sessions per request [8e]. The async context manager ensures proper session lifecycle management. On success, the session commits [8f]. On exception, the session rolls back to maintain database consistency [8g]. The finally block ensures the session is always closed, preventing connection leaks. This pattern provides automatic transaction management per request with proper error handling.
