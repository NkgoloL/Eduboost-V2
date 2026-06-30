# EduBoost V2 Architecture Decision Records (ADR) System: Governance, Validation, and Runtime Enforcement

Maps the ADR documentation governance system from definition through validation to runtime enforcement. The system defines 28 ADRs covering architecture (modular monolith), privacy (POPIA-first), runtime (Python 3.12.3), deployment, and production readiness across 11 operational domains. Key enforcement points include ADR validation contracts [1b], Python version enforcement [3a→3d], import boundary checks [4b], and CI-driven production readiness verification [8c].

## Trace ID: 1
**Title:** ADR Record Definition and Validation Contract

**Description:** Documentation governance module defining ADR structure, status lifecycle, and validation rules. Foundation for all ADR enforcement.

**Trace text diagram:**
```
ADR Validation System
├── Enum Definitions
│   └── AdrStatus enum (proposed/accepted/...) <-- 1a
├── ADR Record Dataclass
│   ├── @dataclass(frozen=True) definition <-- 1b
│   │   ├── Fields: adr_id, path, title, status <-- production_readiness_contracts.py:124
│   │   ├── Fields: decision_date, owner <-- production_readiness_contracts.py:128
│   │   └── Fields: context/decision/consequences <-- production_readiness_contracts.py:130
│   └── validate() method <-- 1c
│       ├── Check ADR-### format <-- production_readiness_contracts.py:137
│       ├── Check path under docs/adr/ <-- production_readiness_contracts.py:139
│       ├── Validate required sections present <-- production_readiness_contracts.py:147
│       └── Accepted ADR decision check <-- 1d
└── Default ADR Registry
    └── DEFAULT_ADRS tuple with samples <-- 1e
        ├── ADR-017: Documentation governance <-- production_readiness_contracts.py:350
        └── ADR-015: Security posture <-- production_readiness_contracts.py:351
```

**Location ID: 1a**
**Title:** ADR Status Enumeration
**Description:** Defines lifecycle states: proposed, accepted, superseded, rejected
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/documentation_governance/production_readiness_contracts.py:29

**Location ID: 1b**
**Title:** ADR Record Structure
**Description:** Immutable dataclass capturing ADR metadata: ID, path, title, status, decision date, owner, and section presence
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/documentation_governance/production_readiness_contracts.py:123

**Location ID: 1c**
**Title:** ADR Validation Logic
**Description:** Validates ADR-### format, path location, required sections (context, decision, consequences)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/documentation_governance/production_readiness_contracts.py:135

**Location ID: 1d**
**Title:** Accepted ADR Enforcement
**Description:** Requires decision section for accepted ADRs, blocking incomplete documentation
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/documentation_governance/production_readiness_contracts.py:145

**Location ID: 1e**
**Title:** Sample ADR Registry
**Description:** Default ADR records including ADR-017 (documentation governance) and ADR-015 (security posture)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/documentation_governance/production_readiness_contracts.py:349

### AI Guide: ADR Record Definition and Validation Contract

**Motivation:**
The ADR validation system establishes the foundation for architectural governance through structured documentation. Immutable dataclasses ensure ADR metadata integrity. Validation rules enforce consistent formatting and required sections. Status lifecycle tracking enables decision traceability. This system transforms architectural decisions from informal discussions into enforceable contracts that guide development and prevent architectural drift.

**Details:**

**ADR Structure Definition**
The AdrRecord dataclass captures complete ADR metadata with frozen immutability [1b]. Fields include adr_id, path, title, status, decision_date, owner, and section presence flags. The frozen decorator prevents accidental modification after creation. This structure provides a single source of truth for ADR metadata.

**Validation Contract Enforcement**
The validate() method enforces strict formatting rules [1c]. ADR-### format ensures consistent identification. Path validation under docs/adr/ maintains organized structure. Required section checks (context, decision, consequences) guarantee complete documentation. Accepted ADRs require decision sections, preventing incomplete approvals [1d].

**Status Lifecycle Management**
AdrStatus enum defines clear lifecycle states: proposed, accepted, superseded, rejected [1a]. This enables tracking decision evolution and maintaining historical context. Status transitions are controlled through validation, ensuring proper governance processes are followed.

**Default Registry Configuration**
DEFAULT_ADRS provides baseline ADR records for system validation [1e]. Includes critical ADRs like documentation governance (ADR-017) and security posture (ADR-015). This registry serves as both validation input and documentation of key architectural decisions.

## Trace ID: 2
**Title:** Documentation Governance Decision Validation

**Description:** Validates that documentation governance decisions meet production readiness requirements with claim discipline and stale doc review.

**Trace text diagram:**
```
Documentation Governance Validation System
├── Contract Definition
│   ├── DocumentationGovernanceDecision <-- 2a
│   │   ├── adr_lifecycle_required: bool <-- production_readiness_contracts.py:65
│   │   ├── claim_discipline_required: bool <-- production_readiness_contracts.py:66
│   │   ├── stale_doc_review_required: bool <-- production_readiness_contracts.py:67
│   │   └── external_claim_boundary_required <-- production_readiness_contracts.py:70
│   └── validate() method <-- 2b
│       └── checks all required flags are True <-- production_readiness_contracts.py:86
├── Claim Discipline Enforcement
│   ├── contains_unbounded_production_claim() <-- 2c
│   │   ├── detects: "production ready", "guaranteed" <-- production_readiness_contracts.py:317
│   │   └── requires: "repository-side", "does not
│   │       authorize" <-- production_readiness_contracts.py:318
│   └── validate_claims_for_release() <-- 2d
│       ├── iterates over ClaimRecord tuple <-- production_readiness_contracts.py:328
│       └── calls contains_unbounded_production
│           _claim <-- production_readiness_contracts.py:330
└── Readiness Report Aggregation
    └── default_documentation_governance_readiness
        _report() <-- 2e
        ├── validates DEFAULT_DOCUMENTATION_DECISION <-- production_readiness_contracts.py:385
        ├── validates DEFAULT_DOC_INVENTORY entries <-- production_readiness_contracts.py:386
        ├── validates DEFAULT_ADRS <-- production_readiness_contracts.py:387
        ├── calls validate_claims_for_release() <-- production_readiness_contracts.py:388
        └── returns dict with all validation issues <-- production_readiness_contracts.py:384
```

**Location ID: 2a**
**Title:** Governance Decision Contract
**Description:** Defines required governance controls: ADR lifecycle, claim discipline, stale doc review, release notes
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/documentation_governance/production_readiness_contracts.py:62

**Location ID: 2b**
**Title:** Governance Validation Entry
**Description:** Validates ADR path location and required governance flags
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/documentation_governance/production_readiness_contracts.py:72

**Location ID: 2c**
**Title:** Claim Discipline Enforcement
**Description:** Detects unbounded production claims without proper boundary phrases
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/documentation_governance/production_readiness_contracts.py:315

**Location ID: 2d**
**Title:** Release Claim Validation
**Description:** Validates all claims and checks for unbounded production claims before release
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/documentation_governance/production_readiness_contracts.py:326

**Location ID: 2e**
**Title:** Readiness Report Generation
**Description:** Aggregates validation results across ADRs, claims, release notes, and stale documentation
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/modules/documentation_governance/production_readiness_contracts.py:381

### AI Guide: Documentation Governance Decision Validation

**Motivation:**
Documentation governance validation ensures production readiness through systematic claim discipline and evidence verification. Required governance flags (ADR lifecycle, claim discipline, stale doc review) enforce comprehensive documentation practices. Claim discipline prevents unbounded production claims without proper boundary language. Readiness report aggregation provides unified validation status across all governance domains. This system transforms documentation from optional artifact to enforceable production gate.

**Details:**

**Governance Contract Definition**
DocumentationGovernanceDecision defines required governance controls [2a]. Flags include adr_lifecycle_required, claim_discipline_required, stale_doc_review_required, and external_claim_boundary_required. These flags ensure comprehensive governance coverage. The validate() method checks all flags are True before allowing production progression [2b].

**Claim Discipline Enforcement**
contains_unbounded_production_claim() detects problematic language like "production ready" or "guaranteed" [2c]. Requires boundary phrases like "repository-side" or "does not authorize" for proper claim discipline. validate_claims_for_release() iterates through ClaimRecord tuple to validate all claims [2d]. This prevents overconfident production claims without evidence.

**Readiness Report Aggregation**
default_documentation_governance_readiness_report() provides unified validation status [2e]. Validates DEFAULT_DOCUMENTATION_DECISION, DEFAULT_DOC_INVENTORY entries, and DEFAULT_ADRS. Calls validate_claims_for_release() for claim discipline. Returns comprehensive dict with all validation issues for production readiness assessment.

## Trace ID: 3
**Title:** Python 3.12.3 Runtime Enforcement (ADR-001)

**Description:** Traces Python version declaration from .python-version through deployment config to CI enforcement, implementing ADR-001's single runtime decision.

**Trace text diagram:**
```
Python 3.12.3 Runtime Enforcement (ADR-001)
├── Source of Truth
│   └── .python-version file <-- 3a
│       └── Contains: "3.12.3"
├── Deployment Configuration
│   └── render.yaml <-- 3b
│       ├── PYTHON_VERSION env var <-- render.yaml:17
│       └── References ADR-001 in comment <-- render.yaml:16
├── CI/CD Pipeline
│   └── .github/workflows/ci-cd.yml
│       ├── Environment variables <-- 3c
│       │   └── PYTHON_VERSION: "3.12.3"
│       └── Job setup <-- 3d
│           └── actions/setup-python@v6 <-- ci-cd.yml:26
│               └── python-version: ${{ env.PYTHON_VERSION }}
└── Developer Documentation
    └── README.md prerequisites <-- 3e
        └── Links to ADR-001 for rationale
```

**Location ID: 3a**
**Title:** Canonical Python Version
**Description:** Single source of truth for Python runtime version (ADR-001)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.python-version:1

**Location ID: 3b**
**Title:** Render Deployment Config
**Description:** Enforces Python 3.12.3 in production Render deployment with ADR-001 comment
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/render.yaml:17

**Location ID: 3c**
**Title:** CI Environment Variable
**Description:** Sets Python version for all CI jobs
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:12

**Location ID: 3d**
**Title:** CI Python Setup
**Description:** Uses environment variable to configure Python in GitHub Actions
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:28

**Location ID: 3e**
**Title:** Documentation Reference
**Description:** Links prerequisites to ADR-001 for developer onboarding
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/README.md:49

### AI Guide: Python 3.12.3 Runtime Enforcement (ADR-001)

**Motivation:**
Python version enforcement implements ADR-001's single runtime decision across development, CI, and production environments. .python-version serves as canonical source of truth. CI/CD pipeline enforces version consistency through environment variables. Render deployment configuration ensures production runtime matches development. This systematic enforcement prevents Python version drift and ensures consistent behavior across all environments.

**Details:**

**Source of Truth Management**
.python-version file contains "3.12.3" as canonical version specification [3a]. This file is read by version management tools and serves as single source of truth. All other configuration references this file either directly or through aligned values. This prevents version conflicts across different tooling.

**CI/CD Pipeline Enforcement**
.github/workflows/ci-cd.yml sets PYTHON_VERSION: "3.12.3" environment variable [3c]. actions/setup-python@v6 uses this variable via ${{ env.PYTHON_VERSION }} [3d]. This ensures all CI jobs run with consistent Python version. Environment variable approach enables easy version updates while maintaining consistency.

**Production Runtime Alignment**
render.yaml enforces PYTHON_VERSION: "3.12.3" in production deployment [3b]. Comment references ADR-001 for rationale documentation. This ensures production runtime matches development and CI environments. Systematic enforcement prevents runtime surprises from version mismatches.

**Developer Documentation**
README.md prerequisites section links Python 3.12.3 requirement to ADR-001 [3e]. This provides developers with rationale for version choice and directs them to architectural decision documentation. Clear documentation supports developer onboarding and decision understanding.

## Trace ID: 4
**Title:** Modular Monolith Import Boundary Enforcement (ADR-0001)

**Description:** Import linter configuration enforcing strict layering: routers must not directly import repositories, implementing the modular monolith architecture decision.

**Trace text diagram:**
```
Modular Monolith Architecture Enforcement
├── ADR-0001 Decision Document <-- 4a
│   └── "Strict Modular Monolith" declaration <-- 0001-modular-monolith.md:10
│
├── Import Linter Configuration
│   ├── .importlinter file <-- 4b
│   │   └── Contract definition <-- 4c
│   │       ├── source: app.api_v2_routers <-- .importlinter:9
│   │       └── forbidden: app.repositories <-- .importlinter:11
│   │
│   └── Allowed exceptions list <-- .importlinter:13
│       └── (consent, content_factory, etc.) <-- .importlinter:14
│
├── CI Enforcement Pipeline
│   └── .github/workflows/ci-cd.yml <-- ci-cd.yml:1
│       └── lint job <-- ci-cd.yml:20
│           └── "Enforce DDD boundaries" step <-- 4d
│               └── runs: lint-imports <-- ci-cd.yml:57
│
└── Runtime Implementation
    └── app/api_v2.py entrypoint <-- 4e
        └── Comment: "Strict Modular Monolith" <-- api_v2.py:3
        └── FastAPI application setup
```

**Location ID: 4a**
**Title:** Architectural Decision
**Description:** ADR-0001 establishes modular monolith with controlled cross-module communication
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/adr/0001-modular-monolith.md:10

**Location ID: 4b**
**Title:** Router-Repository Boundary Contract
**Description:** Forbidden import contract preventing routers from directly accessing repositories
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.importlinter:5

**Location ID: 4c**
**Title:** Boundary Definition
**Description:** Specifies that api_v2_routers cannot import from repositories module
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.importlinter:10

**Location ID: 4d**
**Title:** CI Boundary Enforcement
**Description:** Runs import-linter in CI to block PRs violating architectural boundaries
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:56

**Location ID: 4e**
**Title:** Runtime Implementation
**Description:** FastAPI entrypoint comment reinforcing modular monolith architecture
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:3

### AI Guide: Modular Monolith Import Boundary Enforcement (ADR-0001)

**Motivation:**
Import boundary enforcement implements ADR-0001's modular monolith architecture through automated linting. .importlinter configuration prevents routers from directly importing repositories, enforcing service layer mediation. CI pipeline blocks PRs that violate architectural boundaries. Allowed exceptions list provides controlled escape hatches. This systematic enforcement prevents architectural drift and maintains clean separation of concerns.

**Details:**

**Architectural Decision Foundation**
ADR-0001 declares "Strict Modular Monolith" architecture [4a]. Establishes controlled cross-module communication through service layers. Defines clear boundaries between presentation (routers), business logic (services), and data access (repositories). This decision provides the rationale for import boundary enforcement.

**Import Linter Configuration**
.importlinter defines forbidden import contract [4b, 4c]. source: app.api_v2_routers cannot import from forbidden: app.repositories. This enforces service layer mediation between routers and repositories. allow_indirect_imports = True permits transitive imports through service layers.

**CI Pipeline Enforcement**
.github/workflows/ci-cd.yml runs "Enforce DDD boundaries" step [4d]. lint-imports command executes import-linter validation. CI failure blocks PR merge until boundary violations are resolved. This automated enforcement prevents architectural drift during development.

**Allowed Exceptions Management**
.importlinter includes allowed exceptions list for specific cases [4c]. Exceptions include consent, content_factory, and other justified cross-boundary imports. This provides controlled flexibility while maintaining overall architectural integrity. Each exception represents deliberate architectural decision.

## Trace ID: 5
**Title:** Startup DDL Migration Strategy (ADR-002)

**Description:** Temporary startup DDL repair mechanism being migrated to Alembic, with advisory locks preventing concurrent execution across workers.

**Trace text diagram:**
```
Startup DDL Migration Strategy (ADR-002)

ADR-002 Documentation
├── Migration Decision <-- 5a
│   └── Schema ownership: Alembic (canonical) <-- ADR-002-startup-ddl-repair.md:74
│       └── Startup DDL: transitional only
├── Concurrency Safety Design <-- 5d
│   └── pg_try_advisory_lock(443352, 20260524) <-- ADR-002-startup-ddl-repair.md:29
│       └── Prevents concurrent worker execution <-- ADR-002-startup-ddl-repair.md:30
└── Migration Plan (3 Phases) <-- 5e
    ├── Phase A: Create Alembic migration <-- ADR-002-startup-ddl-repair.md:79
    ├── Phase B: Remove startup DDL <-- ADR-002-startup-ddl-repair.md:88
    └── Phase C: Add CI prevention gate <-- ADR-002-startup-ddl-repair.md:96

Runtime Implementation (app/api_v2.py)
├── run_startup_migrations() <-- 5b
│   ├── Production-only guard <-- 5c
│   │   └── if not settings.is_production() <-- api_v2.py:36
│   ├── Advisory lock acquisition
│   ├── DDL repairs (7 statements) <-- api_v2.py:43
│   │   ├── guardians.email_verified column <-- api_v2.py:45
│   │   ├── tokenpurpose enum
│   │   ├── secure_tokens table
│   │   └── [4 more repairs...]
│   └── Log success/failure <-- api_v2.py:42
└── FastAPI lifespan context
    └── Calls run_startup_migrations()
```

**Location ID: 5a**
**Title:** Migration Decision
**Description:** ADR-002 declares Alembic as canonical owner, startup DDL as temporary
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/adr/ADR-002-startup-ddl-repair.md:74

**Location ID: 5b**
**Title:** Startup Migration Function
**Description:** Temporary DDL repair function executed at application startup
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:35

**Location ID: 5c**
**Title:** Production-Only Guard
**Description:** Startup DDL only runs in production to avoid dev/test drift
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/api_v2.py:36

**Location ID: 5d**
**Title:** Concurrency Safety
**Description:** Advisory lock ensures only one worker executes DDL repairs
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/adr/ADR-002-startup-ddl-repair.md:29

**Location ID: 5e**
**Title:** Migration Plan
**Description:** Phased approach: create Alembic migration, deploy, then remove startup DDL
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/adr/ADR-002-startup-ddl-repair.md:79

### AI Guide: Startup DDL Migration Strategy (ADR-002)

**Motivation:**
Startup DDL migration strategy implements ADR-002's transitional approach to schema management. Alembic serves as canonical schema owner while startup DDL provides temporary bridge. Advisory locks prevent concurrent execution across multiple workers. Production-only guard avoids dev/test environment drift. Three-phase migration plan ensures systematic transition to proper migration management.

**Details:**

**Migration Decision Framework**
ADR-002 declares Alembic as canonical schema owner, startup DDL as transitional mechanism [5a]. This dual approach enables immediate production fixes while establishing proper migration discipline. Startup DDL addresses urgent schema issues without full migration pipeline overhead.

**Concurrency Safety Implementation**
pg_try_advisory_lock(443352, 20260524) prevents concurrent worker execution [5d]. Unique lock key (443352, 20260524) identifies this specific migration operation. Only one worker acquires lock and executes DDL repairs. This prevents race conditions and schema corruption in multi-worker deployments.

**Production-Only Execution**
run_startup_migrations() includes production-only guard [5b, 5c]. if not settings.is_production(): return prevents DDL execution in development and test environments. This avoids schema drift between environments and ensures migration discipline is maintained for non-production deployments.

**Phased Migration Plan**
Three-phase approach ensures systematic transition [5e]. Phase A: Create comprehensive Alembic migration covering all startup DDL repairs. Phase B: Deploy Alembic migration and remove startup DDL. Phase C: Add CI gate preventing future startup DDL additions. This plan provides clear path to proper migration discipline.

## Trace ID: 6
**Title:** LLM Provider Abstraction Implementation (ADR-003)

**Description:** LLM gateway implementing provider abstraction with Anthropic and Groq clients, Redis caching, and structured output validation per ADR-003.

**Trace text diagram:**
```
LLM Provider Abstraction (ADR-003)
├── ADR-003 Decision Document
│   └── Provider abstraction mandate <-- 6a
│
├── LLM Gateway Implementation
│   ├── Provider client globals
│   │   ├── _groq_client: AsyncGroq | None <-- 6b
│   │   └── _anthropic_client: AsyncAnthropic <-- llm_gateway.py:40
│   │
│   ├── Lazy client initialization
│   │   ├── _get_groq() factory <-- 6c
│   │   │   └── AsyncGroq(api_key=...) <-- llm_gateway.py:48
│   │   └── _get_anthropic() factory <-- 6d
│   │       └── AsyncAnthropic(api_key=...) <-- llm_gateway.py:55
│   │
│   └── Safety & validation layer <-- 6e
│       ├── JudiciaryService (content safety) <-- llm_gateway.py:32
│       ├── CAPSAlignmentValidator (curriculum) <-- llm_gateway.py:33
│       └── AI safety utilities (PII redaction) <-- llm_gateway.py:34
│
└── Runtime Integration
    └── Structured output validation <-- 0003-llm-provider-abstraction.md:14
        └── Pydantic-enforced JSON mode <-- llm_gateway.py:6
```

**Location ID: 6a**
**Title:** Abstraction Decision
**Description:** ADR-003 mandates provider abstraction for swappability and testability
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/adr/0003-llm-provider-abstraction.md:10

**Location ID: 6b**
**Title:** Provider Client Globals
**Description:** Lazy-initialized provider clients for Groq and Anthropic
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:38

**Location ID: 6c**
**Title:** Groq Client Factory
**Description:** Lazy initialization of Groq client with API key from settings
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:45

**Location ID: 6d**
**Title:** Anthropic Client Factory
**Description:** Lazy initialization of Anthropic client with API key from settings
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:52

**Location ID: 6e**
**Title:** Safety and Validation Integration
**Description:** Imports safety validators and CAPS alignment per ADR-003 structured output requirements
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/llm_gateway.py:32

### AI Guide: LLM Provider Abstraction Implementation (ADR-003)

**Motivation:**
LLM provider abstraction implements ADR-003's requirement for swappable AI providers. Lazy initialization prevents unnecessary API client creation. Factory pattern enables clean provider switching. Safety and validation layer ensures content compliance. Structured output validation with Pydantic enforces reliable AI responses. This abstraction enables provider switching without application code changes.

**Details:**

**Abstraction Decision Implementation**
ADR-003 mandates provider abstraction for swappability and testability [6a]. Application code calls internal LLM gateway rather than direct provider APIs. This enables provider switching without code changes. Abstraction layer also facilitates testing with mock providers.

**Lazy Client Initialization**
_groq_client and _anthropic_client globals hold lazy-initialized provider clients [6b]. _get_groq() factory creates AsyncGroq client with API key from settings [6c]. _get_anthropic() factory creates AsyncAnthropic client similarly [6d]. Lazy initialization prevents unnecessary connections during startup.

**Safety and Validation Layer**
llm_gateway.py imports JudiciaryService for content safety [6e]. CAPSAlignmentValidator ensures curriculum compliance. AI safety utilities provide PII redaction and quality scoring. This validation layer enforces ADR-003 requirements for safe AI usage.

**Structured Output Enforcement**
Pydantic models enforce structured JSON output from AI providers [6e]. This prevents malformed AI responses and ensures type safety. Structured output validation enables reliable integration of AI responses into application workflows.

## Trace ID: 7
**Title:** POPIA-First Design in Action (ADR-002)

**Description:** POPIA compliance implementation with consent service, audit repository, and data subject rights service enforcing privacy-first architecture.

**Trace text diagram:**
```
POPIA-First Design Architecture (ADR-002)
├── ADR-002: Privacy-First Decision <-- 7a
│   └── "POPIA as architectural constraint"
│
├── Data Subject Rights Implementation
│   ├── POPIADataRightsService class <-- 7b
│   │   ├── Export workflows
│   │   ├── Erasure request handling
│   │   ├── Correction workflows
│   │   └── Processing restriction
│   └── POPIA SLA Constants <-- 7e
│       ├── EXPORT_SLA_DAYS = 30 <-- popia_service.py:40
│       ├── ERASURE_REVIEW_SLA_DAYS = 30 <-- popia_service.py:41
│       └── ERASURE_GRACE_DAYS = 30 <-- popia_service.py:42
│
└── Audit Trail Implementation
    └── FourthEstateService class <-- 7c
        └── record() method <-- 7d
            ├── event_type parameter <-- audit.py:27
            ├── actor_id parameter <-- audit.py:28
            ├── learner_pseudonym parameter <-- audit.py:29
            └── Append-only PostgreSQL storage
                └── AuditRepository.log() <-- audit.py:34
```

**Location ID: 7a**
**Title:** Privacy-First Decision
**Description:** ADR-002 establishes POPIA compliance as architectural constraint, not afterthought
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/docs/adr/0002-popia-first-design.md:10

**Location ID: 7b**
**Title:** Data Subject Rights Service
**Description:** Centralizes learner export, erasure, correction, and restriction workflows
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/popia_service.py:78

**Location ID: 7c**
**Title:** Audit Service
**Description:** Append-only audit trail for learner data access per ADR-002 auditability requirement
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/audit.py:16

**Location ID: 7d**
**Title:** Audit Event Recording
**Description:** Records sensitive actions with actor, learner pseudonym, and constitutional outcome
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/core/audit.py:25

**Location ID: 7e**
**Title:** POPIA SLA Constants
**Description:** Defines legally-required response timeframes for data subject rights requests
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/app/services/popia_service.py:40

### AI Guide: POPIA-First Design in Action (ADR-002)

**Motivation:**
POPIA-first design implements ADR-002's mandate for privacy as architectural constraint. POPIADataRightsService centralizes data subject rights workflows. FourthEstateService provides append-only audit trail for compliance. SLA constants enforce legally-required response times. This implementation transforms privacy from afterthought to foundational architectural principle.

**Details:**

**Privacy-First Architecture**
ADR-002 establishes POPIA compliance as architectural constraint, not afterthought [7a]. Consent state must be explicit and enforceable by backend dependencies. Audit trail must capture all learner data access. Data subject rights must be implementable within system constraints. This decision drives privacy-aware system design.

**Data Subject Rights Implementation**
POPIADataRightsService centralizes learner export, erasure, correction, and restriction workflows [7b]. Implements POPIA requirements for data access and control. Provides unified interface for privacy operations. Service design ensures consistent handling of all data subject rights requests.

**Audit Trail Implementation**
FourthEstateService provides append-only audit trail per ADR-002 requirements [7c]. record() method captures event_type, actor_id, learner_pseudonym [7d]. AuditRepository.log() stores events in PostgreSQL with append-only guarantees. This audit trail enables compliance verification and accountability.

**SLA Enforcement**
POPIA_SLA constants define legally-required response timeframes [7e]. EXPORT_SLA_DAYS = 30 for data export requests. ERASURE_REVIEW_SLA_DAYS = 30 for erasure request review. ERASURE_GRACE_DAYS = 30 for erasure grace period. These constants enforce POPIA compliance requirements.

## Trace ID: 8
**Title:** Production Readiness Verification Pipeline

**Description:** CI workflow orchestrating production readiness checks across all 11 operational domains with Python 3.12.3 enforcement and coverage thresholds.

**Trace text diagram:**
```
EduBoost CI/CD Production Readiness Pipeline
├── Workflow Definition <-- 8a
│   ├── Environment Configuration <-- 8b
│   │   ├── PYTHON_VERSION: "3.12.3" <-- ci-cd.yml:12
│   │   ├── COVERAGE_THRESHOLD: "60" <-- ci-cd.yml:13
│   │   └── V2_ENTRYPOINT: "app.api_v2:app" <-- ci-cd.yml:14
│   │
│   ├── Quality Gates (parallel jobs)
│   │   ├── Lint & Type Check Job <-- 8c
│   │   │   ├── Setup Python 3.12.3 <-- ci-cd.yml:26
│   │   │   ├── Run ruff linter <-- ci-cd.yml:35
│   │   │   ├── Run mypy type checker <-- ci-cd.yml:38
│   │   │   ├── pip-audit security scan <-- ci-cd.yml:43
│   │   │   ├── Bandit SAST scan <-- ci-cd.yml:48
│   │   │   └── Import Boundaries <-- 8d
│   │   │
│   │   └── Documentation Quality Job <-- 8e
│   │       ├── Markdown linting <-- ci-cd.yml:82
│   │       └── Link validation <-- ci-cd.yml:87
│   │
│   └── Production Readiness Checks
│       ├── Backend consolidation
│       ├── POPIA consent audit
│       ├── Diagnostics assessment
│       └── 11 domain-specific checks
```

**Location ID: 8a**
**Title:** CI/CD Pipeline Entry
**Description:** Main workflow triggered on push, PR, and release events
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:1

**Location ID: 8b**
**Title:** Pipeline Environment
**Description:** Sets Python version (ADR-001), coverage threshold, and V2 entrypoint (ADR-005)
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:11

**Location ID: 8c**
**Title:** Lint and Type Check Job
**Description:** First gate: ruff, mypy, pip-audit, bandit SAST, and import boundary enforcement
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:20

**Location ID: 8d**
**Title:** Import Boundary Check
**Description:** Enforces modular monolith architecture (ADR-0001) via import-linter
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:56

**Location ID: 8e**
**Title:** Documentation Quality Gate
**Description:** Validates markdown and links supporting ADR-017 documentation governance
**Path:LineNumber:** /home/nkgolol/Dev/Development/Eduboost-V2/.github/workflows/ci-cd.yml:68

### AI Guide: Production Readiness Verification Pipeline

**Motivation:**
Production readiness verification pipeline implements systematic quality gates across all operational domains. Environment configuration enforces ADR decisions (Python 3.12.3, V2 entrypoint). Parallel quality gates provide comprehensive validation. Import boundary checks enforce architectural decisions. Documentation quality gates support ADR-017 governance. This pipeline transforms production readiness from manual assessment to automated verification.

**Details:**

**Pipeline Environment Configuration**
.github/workflows/ci-cd.yml sets PYTHON_VERSION: "3.12.3" enforcing ADR-001 [8b]. COVERAGE_THRESHOLD: "60" defines quality expectations. V2_ENTRYPOINT: "app.api_v2:app" specifies ADR-005 V2 runtime. Environment variables ensure consistent pipeline execution across all jobs.

**Quality Gates Implementation**
Lint & Type Check job provides comprehensive code quality validation [8c]. Setup Python 3.12.3 ensures version consistency. ruff linter checks code style. mypy type checker validates type annotations. pip-audit scans for security vulnerabilities. Bandit SAST identifies security issues. Import boundary enforcement validates ADR-0001.

**Architectural Enforcement**
Import boundary check runs lint-imports to enforce modular monolith architecture [8d]. This validates ADR-0001 compliance during CI. Import violations block PR merge until resolved. Automated enforcement prevents architectural drift.

**Documentation Governance**
Documentation Quality job validates markdown and links [8e]. Supports ADR-017 documentation governance requirements. Ensures documentation quality matches code quality. Markdown linting enforces consistent formatting. Link validation prevents broken documentation references.
