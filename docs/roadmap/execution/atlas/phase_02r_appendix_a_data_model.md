# Phase 2R Appendix A — Detailed Authoritative Data Model

**Document version:** 1.4  
**Plan date:** 2026-06-16  
**Status:** Draft — approval required with the main Phase 2R execution plan  
**Canonical path:** `docs/roadmap/execution/atlas/phase_02r_appendix_a_data_model.md`  
**Parent plan:** `docs/roadmap/execution/atlas/phase_02r_execution_plan.md`  
**Purpose:** Authoritative tables, immutable version layers, inventory versions, structured rights conditions, reviewed translations, corpus manifests, database-atomic activation, transactional outbox, active bindings, and minimum constraints.

> This appendix is controlled by the main execution plan. A change that alters scope, architecture, success criteria, rights, thresholds, evidence, or audit requirements is a material plan amendment.

---

## 9. Required Immutable Data Layers

The authoritative model must preserve this sequence as separate entities:

```text
Logical source
→ acquired source version
→ original file/object
→ extraction run/version
→ page
→ section/table/figure/formula
→ chunk version
→ curriculum node/version
→ reviewed source-to-node mapping
→ source/extraction/mapping reviews
→ corpus version and membership
→ embedding/index projection
→ generation/tutor grounding record
→ claim and answer verification
→ generated artifact review/publication
→ staleness impact and resolution
```

### 9.1 Proposed authoritative tables

Exact names may change through ADR review, but the semantics may not be weakened.

### 9.1.1 Immutable authority, events, and rebuildable projections

Authoritative facts and decisions are append-only. Where the proposed schemas contain fields named `status`, `review_status`, `lifecycle_status`, or similar, the implementation must either:

1. make the field immutable at row creation; or
2. name and implement it explicitly as a rebuildable `*_projection` derived from append-only events/reviews.

A projection may be updated for query efficiency, but it is never the audit authority. Corrections create superseding versions or decisions. Frozen source versions, extraction outputs, mappings, translation versions, corpus manifests, memberships, activation events, and answer-verification records are never rewritten. Application database roles must be denied `UPDATE`/`DELETE` on append-only authority tables except through an audited break-glass maintenance procedure.


#### `curriculum_source_inventory_versions`

Immutable signed inventory scope:

```text
inventory_version_id
curriculum_code
phase
grade
subject_code
terms
strands
language_policy
lifecycle_state_projection
manifest_sha256
frozen_at
frozen_by
reviewed_by
reviewed_at
supersedes_inventory_version_id
```

#### `curriculum_source_inventory_items`

```text
inventory_item_id
inventory_version_id
source_category
required_for_closure
expected_authority_tier
expected_language_status
located
logical_source_id
source_version_id
absence_reason
open_issue
item_sha256
```

#### `curriculum_source_inventory_reviews`

Append-only review and approval decisions for the inventory version and items. A corpus version must reference an immutable approved `inventory_version_id`; an unconstrained string is insufficient.

#### `curriculum_sources`

Logical document identity:

```text
source_id
publisher
authority_tier
official_source_url
document_title
document_type
country
curriculum
phase
grade
subject
canonical_language
copyright_owner
lifecycle_state_projection
created_at
created_by
```

#### `curriculum_source_versions`

Immutable acquired version identity:

```text
source_version_id
source_id
version_label
publication_date
effective_from
effective_to
supersedes_source_version_id
amended_by_source_version_id
retrieved_at
retrieval_method
http_etag
http_last_modified
redirect_chain
content_type
content_length
original_sha256
lifecycle_state_projection
created_at
created_by
```

No update may replace content-bearing fields. Corrections create a new record or an append-only correction event.

#### `curriculum_source_files`

```text
source_file_id
source_version_id
object_uri
object_version_id
filename
media_type
size_bytes
sha256
malware_scan_status
malware_scan_engine
malware_scan_at
immutable_storage_verified
retention_class
created_at
```

#### `curriculum_rights_decisions`

Version-bound, append-only rights decision:

```text
rights_decision_id
source_version_id
decision_status
may_store_original
may_extract
may_embed
may_use_for_retrieval
may_include_in_model_prompt
may_generate_derivatives
may_translate
may_publish_translation
may_show_excerpt_to_educator
may_show_excerpt_to_learner
may_redistribute
may_use_commercially
may_use_for_model_training
requires_attribution
attribution_text
attribution_policy_version
conditions_json
permitted_channels
permitted_languages
permitted_jurisdictions
maximum_excerpt_length
basis_type
basis_reference
reviewer_id
reviewed_at
expires_at
review_trigger
supersedes_rights_decision_id
notes
```

A generic value such as `government_open` is metadata only and never sufficient by itself. `approved_with_conditions` is eligible only when every applicable structured condition is evaluated by policy code; free-text `notes` cannot substitute for enforceable conditions. Translation and publication of translations require independent explicit decisions.

#### `curriculum_extraction_runs`

```text
extraction_run_id
source_version_id
source_file_id
extractor_name
extractor_version
configuration_sha256
started_at
completed_at
run_state_projection
native_text_used
ocr_used
ocr_engine
warnings_json
quality_summary_json
output_manifest_sha256
```

#### `curriculum_source_pages`

```text
page_version_id
extraction_run_id
page_number
width
height
rotation
text_storage_mode
native_text_inline
native_text_object_uri
normalised_text_inline
normalised_text_object_uri
text_sha256
extraction_confidence
ocr_confidence
layout_json
warnings_json
access_classification
extraction_review_state_projection
```

#### `curriculum_source_sections`

```text
section_version_id
extraction_run_id
parent_section_version_id
section_type
heading
section_path
page_start
page_end
reading_order
text_sha256
extraction_review_state_projection
```

Section types must support paragraph groups, tables, figures/captions, worked examples, formulas, glossary entries, and assessment requirements.

#### `curriculum_source_chunks`

```text
chunk_version_id
source_version_id
extraction_run_id
section_version_id
page_start
page_end
chunk_order
language
text_storage_mode
text_inline
text_object_uri
text_sha256
authority_tier
quality_score
extraction_review_state_projection
rights_eligibility_state_projection
access_classification
active_from
active_to
created_at
```

Chunk content is immutable. Re-chunking creates new chunk versions.


#### `curriculum_chunk_translation_versions`

Reviewed derivative translations retain an explicit relationship to the authoritative source chunk:

```text
translation_version_id
source_chunk_version_id
target_language
translation_method
translated_text_storage_mode
translated_text_inline
translated_text_object_uri
translated_text_sha256
translator_or_generator_id
translation_rights_decision_id
publication_rights_decision_id
language_review_state_projection
language_reviewer_id
curriculum_meaning_review_state_projection
curriculum_reviewer_id
reviewed_at
lifecycle_state_projection
supersedes_translation_version_id
created_at
```

`translation_method` must distinguish `official_source`, `human_translation`, `machine_translation`, and `generated_explanation`. Machine drafts and generated explanations are never promoted to source authority. Eligibility requires an approved `translation_rights_decision_id`; learner/public publication additionally requires an approved `publication_rights_decision_id`, with all structured conditions satisfied.

#### `curriculum_nodes` and `curriculum_node_versions`

Nodes include:

```text
curriculum
phase
grade
subject
term
strand
topic
subtopic
skill
learning_objective
assessment_requirement
prerequisite
vocabulary
```

Every version stores a stable code, label, language, status, effective dates, and review state.

#### `curriculum_node_edges`

Supported relationships include:

```text
CONTAINS
REQUIRES
PRECEDES
DEPENDS_ON
ASSESSED_BY
EXEMPLIFIED_BY
DEFINED_IN
AMENDED_BY
SUPERSEDES
TRANSLATION_OF
```

#### `curriculum_source_mappings`

```text
mapping_version_id
chunk_version_id
curriculum_node_version_id
mapping_type
coverage_strength
proposed_by
proposal_method
proposal_model_version
proposal_confidence
mapping_review_state_projection
reviewer_id
reviewed_at
rationale
supersedes_mapping_version_id
```

Automated mapping proposals remain ineligible until human approval.

#### Review-domain tables

Keep separate append-only decisions for:

```text
curriculum_rights_reviews
curriculum_extraction_reviews
curriculum_mapping_reviews
generated_content_reviews
assessment_answer_verifications
publication_decisions
```

One decision domain may not implicitly approve another.

#### `curriculum_corpus_versions`

```text
corpus_version_id
curriculum_code
grade
subject_code
delivery_language
tenant_scope
activation_scope_key
language_policy
inventory_version_id
embedding_model
embedding_version
chunking_policy_version
grounding_policy_version
manifest_sha256
built_at
built_by
corpus_review_state_projection
reviewed_by
reviewed_at
supersedes_corpus_version_id
lifecycle_state_projection
```

#### `curriculum_corpus_memberships`

```text
corpus_version_id
chunk_version_id
mapping_version_id
source_version_id
membership_disposition
inclusion_reason
membership_sha256
```

All membership rows are immutable after the corpus is frozen.

#### `curriculum_corpus_activations`

Immutable activation event ledger:

```text
activation_id
activation_scope_key
curriculum_code
grade
subject_code
delivery_language
tenant_scope
corpus_version_id
previous_corpus_version_id
activated_by
activated_at
reason
rollback_of_activation_id
event_sha256
```

Activation events are append-only and are never marked inactive or rewritten.

#### `curriculum_corpus_active_bindings`

Transactional current pointer:

```text
activation_scope_key
curriculum_code
grade
subject_code
delivery_language
tenant_scope
active_corpus_version_id
last_activation_id
updated_at
binding_epoch
row_version
```

A unique constraint on the complete activation key ensures one current binding. Activation locks and updates this binding while appending a new immutable activation event in the same transaction.

#### `curriculum_domain_outbox`

Transactional side-effect ledger:

```text
outbox_event_id
aggregate_type
aggregate_id
activation_scope_key
binding_epoch
corpus_version_id
event_type
payload_sha256
payload_json
idempotency_key
created_at
published_at
attempt_count
last_error
next_attempt_at
dead_lettered_at
```

The activation transaction appends outbox records for cache invalidation, audit publication, metrics, alerts, and staleness work. An idempotent consumer publishes them after commit. Retrieval safety must use the authoritative binding and versioned cache keys, not assume that cache eviction is immediate.

#### Grounding, validation, and staleness tables

Create or extend records for:

```text
artifact_grounding_records
tutor_grounding_records
grounding_claims
grounding_claim_support
claim_validation_results
assessment_answer_verifications
source_change_events
source_version_eligibility_events
corpus_eligibility_events
artifact_staleness_impacts
artifact_staleness_resolutions
```

### 9.2 Existing retrieval tables

`retrieval_source_documents` and `retrieval_source_chunks` may be retained as a search projection if sound, but they must:

- reference authoritative source/chunk/corpus version IDs;
- be rebuildable from a frozen corpus manifest;
- never overwrite the authoritative version history;
- key uniqueness by corpus and chunk version rather than a mutable logical document ID;
- include the corpus version in every query and hit;
- exclude every source/chunk not eligible under the active manifest;
- use cache keys containing the complete activation key, corpus version, and binding epoch;
- reject a cached result whose binding epoch no longer matches the authoritative active binding.

The current `ON CONFLICT (document_id) DO UPDATE` pattern must not remain the authority/versioning mechanism.

### 9.3 Minimum constraints and invariants

The approved ADR may strengthen these rules but may not omit them:

- immutable source-version uniqueness under the logical source and original checksum/version identity;
- immutable file/object uniqueness and checksum consistency;
- no self-supersession; acyclic supersession enforced through service policy plus recursive validation/tests;
- one current active binding per complete activation key;
- activation-event and active-binding foreign-key/epoch consistency;
- immutable corpus membership uniqueness by corpus, chunk version, mapping version, and source version;
- no frozen corpus mutation and no membership deletion through the application role;
- review-domain separation through distinct tables and foreign keys; one domain cannot satisfy another;
- maker-checker actor inequality where required, with explicit compensating-control records where approved;
- unique outbox idempotency keys and at-most-once logical effect under at-least-once delivery;
- answer-verification records bound to question, answer, reasoning, checker configuration, and artifact-version hashes;
- edits that change any bound hash invalidate prior verification;
- active-binding changes must reference an eligible frozen corpus and immutable activation event;
- source/corpus eligibility changes are append-only events, never edits to historical memberships;
- application roles cannot update/delete append-only authority tables outside an audited break-glass path.

Database constraints must enforce what PostgreSQL can express directly; service policy, transaction isolation, recursive checks, and integration tests must enforce the remainder.


### 9.4 Extracted-text storage and access model

ADR-02R-011 must be approved before the extraction schema is implemented.

The decision must compare:

```text
PostgreSQL full page/chunk text
object-store extraction artifacts with database references
hybrid storage
```

Regardless of the chosen model, PostgreSQL must retain:

- source, file, extraction, page, section, and chunk version identifiers;
- immutable hashes;
- page and section provenance;
- review and rights status;
- object/artifact references;
- access classification;
- retention and revalidation triggers.

The design must account for:

- database and backup growth;
- restricted-source duplication;
- row- and object-level access control;
- rights expiry or withdrawal;
- evidence minimisation;
- full-text search and pgvector projection rebuilds;
- deletion/retention constraints without corrupting audit history.

Full source text must not be copied into unrestricted logs, fixtures, reports, or evidence packs.


---

