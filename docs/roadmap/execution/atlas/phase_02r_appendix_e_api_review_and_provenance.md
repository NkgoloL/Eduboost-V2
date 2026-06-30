# Phase 2R Appendix E — Review Interfaces, Cross-Phase Integrations, APIs, Jobs, and Provenance

**Document version:** 1.4  
**Plan date:** 2026-06-16  
**Status:** Draft — approval required with the main Phase 2R execution plan  
**Canonical path:** `docs/roadmap/execution/atlas/phase_02r_appendix_e_api_review_and_provenance.md`  
**Parent plan:** `docs/roadmap/execution/atlas/phase_02r_execution_plan.md`  
**Purpose:** Human-review tooling, provenance display, study-plan/Phase 6/Phase 7 integrations, protected routes, authorisation, and durable jobs.

> This appendix is controlled by the main execution plan. A change that alters scope, architecture, success criteria, rights, thresholds, evidence, or audit requirements is a material plan amendment.

---

## 22. Human Review and Provenance Interfaces

### 22.1 Supported human-review interface

Phase 2R closure requires a supported authenticated review interface. Raw SQL and ad hoc API calls are not an acceptable operational review process.

The implementation may provide:

- an accessible administrator/reviewer web interface; or
- an approved authenticated review CLI for initial closure, with a web interface scheduled before operational scale.

The interface must support:

- original-source and rendered-page preview;
- page, section, table, figure, formula, and chunk provenance;
- source authority and rights evidence;
- extraction warnings and confidence;
- curriculum mapping proposals and corrections;
- language and translation status;
- decision reasons and reviewer comments;
- source-change and staleness impact review;
- corpus membership preview;
- immutable decision history;
- keyboard navigation, visible focus, labels, error summaries, and non-colour-only status.

Bulk navigation and batch triage are allowed. **Bulk approval without individual decision traceability is prohibited.**

### 22.2 Provenance display by audience

The implementation must define audience-specific provenance displays:

| Audience | Minimum provenance |
|---|---|
| Rights reviewer | Source version, rights basis, permissions, expiry/review trigger |
| Curriculum/extraction reviewer | Source version, rendered page, section/chunk, extraction warnings, mapping |
| Generated-content educator | Corpus version, curriculum nodes, source titles/pages, claim support, answer verification |
| Learner | Concise age-appropriate source attribution where permitted; no restricted raw source |
| Guardian | High-level curriculum/source and publication status where appropriate |
| Operator | Corpus/source versions, grounding status, failure reason, incident links |
| Auditor | Full immutable source, rights, mapping, retrieval, generation, verification, review, and activation chain |

Visibility must respect rights, privacy, security, and restricted-excerpt rules.


---

## 23. Cross-Phase Integration Requirements

### 23.1 Study-plan integration

Study plans must resolve only approved curriculum-node versions from the active corpus and approved prerequisite graph.

Persist:

```text
study_plan_id
corpus_version_id
curriculum_node_version_ids
prerequisite_edge_versions
coverage_snapshot_id
grounding_policy_version
source_snapshot_sha256
staleness_status
```

A study plan must not recommend a node lacking approved Tier 1 support. Source, mapping, graph, or corpus changes must trigger plan staleness evaluation.

### 23.2 Phase 7 coverage integration

Phase 7 coverage reporting must expose separate measures:

```text
authoritative_source_coverage
reviewed_mapping_coverage
approved_chunk_coverage
published_lesson_coverage
verified_assessment_coverage
language_delivery_coverage
```

A single combined “CAPS coverage” percentage is prohibited.

### 23.3 Phase 6 accounting integration

Phase 6 usage accounting must cover:

```text
source acquisition AI/inspection calls
OCR and extraction AI calls
embedding generation
mapping proposals
claim validation
answer verification
lesson/assessment generation
tutor turns
corpus evaluation
```

Usage records must include, where applicable:

```text
operation_type
source_version_id
corpus_version_id
provider
model
input_tokens
output_tokens
embedding_units
estimated_cost
actual_cost
reservation_id
finalisation_status
```

Rights, curriculum, extraction, mapping, corpus, or content approvals may never be purchased or inferred from budget completion.

---

## 24. APIs and Authorisation

### 24.1 Mandatory control-surface inventory

Exact URI shapes may be refined by ADR/OpenAPI review, but every governed operation below must have a supported, authenticated control surface and contract tests. Direct database manipulation is prohibited for routine operation.

```text
# Inventory versioning, freeze, review, and absence decisions
POST /admin/curriculum-source-inventories
GET  /admin/curriculum-source-inventories/{inventory_version_id}
POST /admin/curriculum-source-inventories/{inventory_version_id}/items
POST /admin/curriculum-source-inventories/{inventory_version_id}/freeze
POST /admin/curriculum-source-inventories/{inventory_version_id}/reviews
POST /admin/curriculum-source-inventory-items/{inventory_item_id}/reviews
POST /admin/curriculum-source-inventory-items/{inventory_item_id}/absence-decisions

# Logical sources, immutable versions, and rights lifecycle
POST /admin/curriculum-sources
GET  /admin/curriculum-sources
GET  /admin/curriculum-sources/{source_id}
POST /admin/curriculum-sources/{source_id}/versions
POST /admin/curriculum-source-versions/{version_id}/rights-decisions
POST /admin/curriculum-rights-decisions/{decision_id}/supersede
POST /admin/curriculum-rights-decisions/{decision_id}/expire
POST /admin/curriculum-rights-decisions/{decision_id}/withdraw
POST /admin/curriculum-source-versions/{version_id}/acquire

# Extraction run status, retry, quarantine, page/chunk review
POST /admin/curriculum-source-versions/{version_id}/extract
GET  /admin/curriculum-extraction-runs/{extraction_run_id}
POST /admin/curriculum-extraction-runs/{extraction_run_id}/retry
POST /admin/curriculum-extraction-runs/{extraction_run_id}/quarantine
GET  /admin/curriculum-source-versions/{version_id}/pages
POST /admin/curriculum-source-pages/{page_version_id}/reviews
POST /admin/curriculum-source-chunks/{chunk_version_id}/reviews

# Mapping and reviewed derivative translations
POST /admin/curriculum-mappings/{mapping_version_id}/reviews
POST /admin/curriculum-chunk-translations
GET  /admin/curriculum-chunk-translations/{translation_version_id}
POST /admin/curriculum-chunk-translations/{translation_version_id}/language-reviews
POST /admin/curriculum-chunk-translations/{translation_version_id}/curriculum-meaning-reviews

# Corpus build, independent review, freeze, activation, rollback
POST /admin/curriculum-corpus/build
GET  /admin/curriculum-corpus/versions
GET  /admin/curriculum-corpus/{corpus_version_id}
POST /admin/curriculum-corpus/{corpus_version_id}/reviews
POST /admin/curriculum-corpus/{corpus_version_id}/freeze
POST /admin/curriculum-corpus/{corpus_version_id}/activate
POST /admin/curriculum-corpus/{corpus_version_id}/rollback
GET  /admin/curriculum-corpus/active-bindings
GET  /admin/curriculum-corpus/outbox
POST /admin/curriculum-corpus/outbox/{outbox_event_id}/retry

# Source changes, eligibility, stale-artifact impact and disposition
GET  /admin/curriculum-source-changes
POST /admin/curriculum-source-changes/{event_id}/resolve
GET  /admin/curriculum-staleness-impacts
POST /admin/curriculum-staleness-impacts/{impact_id}/dispositions
GET  /admin/curriculum-coverage

# Maker-checker assignment and workload control
POST /admin/curriculum-review-assignments
GET  /admin/curriculum-review-assignments
POST /admin/curriculum-review-assignments/{assignment_id}/accept
POST /admin/curriculum-review-assignments/{assignment_id}/reassign
```

### 24.1.1 Interface ownership matrix

| Governed operation | Required operational surface | Background component | Direct SQL allowed? |
|---|---|---|---|
| Inventory create/freeze/approve and absence decision | Admin API plus reviewer UI/approved CLI | Validator/signing service | No |
| Rights decision/supersession/expiry/withdrawal | Rights-review UI/CLI plus API | Expiry/revalidation job | No |
| Acquisition and malware quarantine | Operator UI/CLI plus API | Durable acquisition/scan jobs | No |
| Extraction status/retry/quarantine and review | Reviewer UI/CLI plus API | Extraction/retry jobs | No |
| Mapping proposal/review | Curriculum-review UI/CLI plus API | Proposal job only | No |
| Translation proposal/language/curriculum review | Language-review UI/CLI plus API | Draft-generation job only | No |
| Corpus review/freeze/activation/rollback | Release/governance UI/CLI plus API | Build and outbox jobs | No |
| Source-change and stale-artifact disposition | Operations/reviewer UI/CLI plus API | Impact and staleness jobs | No |
| Review assignment/maker-checker enforcement | Governance UI/CLI plus API | Notification/escalation job | No |


### 24.2 API requirements

- role-based authorisation and least privilege;
- actor identity from authenticated server context;
- no client-supplied approval or activation state;
- machine-enforced evaluation of structured rights conditions, including language, channel, jurisdiction, excerpt, and attribution constraints;
- strict Pydantic schemas and enum validation;
- idempotency keys for acquisition, extraction, build, activation, and rollback;
- immutable review history;
- pagination and bounded exports;
- redacted operational responses for restricted sources;
- OpenAPI generation and drift verification;
- contract tests for every route;
- audit event on every state-changing operation;
- transactional-outbox event on activation and other externally published domain changes;
- explicit review-assignment and maker-checker checks before accepting a decision;
- supported review-interface or authenticated CLI contract tests for inventory, absence, rights lifecycle, extraction retry/quarantine, mapping, translation, corpus review/activation, source change, staleness disposition, and assignment decisions;
- accessibility checks for any web-based reviewer interface;

---

## 25. Durable Jobs

Implement or extend idempotent, observable jobs:

```text
acquire_curriculum_source
scan_curriculum_source
extract_curriculum_source
review_extraction_queue
chunk_curriculum_source
embed_curriculum_chunks
rebuild_curriculum_graph
build_curriculum_corpus
activate_curriculum_corpus
process_curriculum_domain_outbox
reindex_curriculum_corpus
detect_source_version_changes
expire_and_revalidate_rights_decisions
assess_artifact_staleness
mark_stale_generated_artifacts
evaluate_grounding
migrate_legacy_artifacts
```


All AI-, OCR-, embedding-, validation-, verification-, generation-, and tutor-related jobs must reserve and finalise usage through Phase 6 accounting. Non-AI deterministic parsing may record operational counters without token reservations.

Jobs must:

- use durable state and resumable checkpoints;
- be safe under retries;
- persist input/output hashes;
- emit metrics and structured audit events;
- never auto-approve rights, extraction, mappings, content, answer verification, or activation;
- enforce tenant and source access boundaries;
- stop on checksum mismatch or policy ineligibility;
- process outbox records idempotently with deduplication, retry, backoff, dead-letter alerts, and binding-epoch-safe cache handling;
- never allow delayed outbox processing to determine which corpus is authoritative.

---

