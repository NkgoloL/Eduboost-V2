# Study Material Expansion Implementation Plan

Date: 2026-06-02

Branch: `remediation/audit-roadmap-2026-06-02`

## Objective

Populate EduBoost with complete CAPS-aligned study material beyond the current Grade 4 Mathematics launch slice, covering all supported grades and subjects with the same production controls used for the existing launch artifacts.

The target is not simply to generate more JSON. The target is a repeatable curriculum-content pipeline that can ingest authoritative CAPS scope, generate candidate learning material, validate it, review/promote it, seed it into the application, measure coverage, and keep every learner-facing artifact traceable to a curriculum reference.

## Current Ground Truth

The repository currently contains a narrow but useful launch slice:

- One active content scope: `grade4_mathematics_en`.
- CAPS references in the active scope: `4.M.1.1`, `4.M.1.2`, `4.M.1.3`.
- Topic map: `data/caps/topic_maps/caps_topic_map_grade4_maths.json`.
- Diagnostic item bank: `data/generated/items/grade4_maths_launch_item_bank.json`.
- Lesson bank: `data/generated/lessons/grade4_maths_launch_lessons.json`.
- Assessment blueprints: `data/generated/assessment_blueprints/grade4_maths_launch_blueprints.json`.
- Study-plan templates: `data/generated/study_plans/grade4_maths_launch_templates.json`.
- Strict validator: `scripts/validate_launch_content.py`, currently hard-coded to Grade 4 Maths launch refs.

Verified launch thresholds today:

- 40 approved diagnostic items per launch CAPS ref.
- 8 approved lessons per launch CAPS ref.
- 4 assessment blueprint types per topic plus a baseline diagnostic.
- 3 study-plan template mappings per launch topic.

The content model is sound enough to scale, but the scope registry, validators, artifact naming, generation scripts, and CI gates need to be generalized before bulk population.

## Implementation Status - 2026-06-03

The artifact-layer population batch now covers every registered Grade R to Grade 7 English scope. The registry contains 51 scopes: 1 active launch scope (`grade4_mathematics_en`) and 50 review scopes. All 51 scopes have the required artifact-layer paths and files for topic maps, diagnostic item banks, lessons, assessment blueprints, and study-plan templates. The review-scope generation batch also wrote per-scope run manifests plus `data/generated/run_manifests/all_review_scopes_generation_summary.json`.

Generated review-scope totals from this batch:

- Review scopes populated: 50.
- Diagnostic items generated: 32,080.
- Lessons generated: 6,416.
- Assessment blueprints generated: 2,456.
- Study-plan template files generated: 50.

Operational caveat: the 50 newly populated non-launch scopes remain `review`, not learner-visible `active`. The generated artifacts are schema-valid, CAPS-ref linked, source-provenance backed, and ready for educator review/promotion workflows; they should not be represented as production-approved curriculum until Phase 7/8 promotion gates and human-review evidence are complete.

## Promotion Readiness Status - 2026-06-03

The next promotion-readiness batch adds file-backed manifests for all generated scope artifacts and extends coverage/promotion gates beyond diagnostic items and lessons. `scripts/curriculum/build_promotion_readiness_manifests.py` now writes per-scope manifests plus `data/generated/promotion_manifests/all_scopes_promotion_readiness_summary.json` with artifact hashes, idempotency keys, layer counts, staging eligibility, production eligibility, and rollback metadata.

Current promotion-readiness summary:

- Scopes evaluated: 51.
- Staging-eligible scopes: 1 (`grade5_mathematics_en` after lesson regeneration).
- Production-eligible scopes: 0.
- Review-blocked scopes: 50.
- Lesson-quarantined scopes: 50.
- Learner-visible scopes: 1.

Operational caveat: generated lesson files failed the new lesson-quality audit because they contained placeholder instructional content. Lesson-layer staging has been revoked until scopes are regenerated with `scope_lesson_generator_v2` and pass `scripts/curriculum/audit_generated_lesson_quality.py`. Review scopes remain non-learner-visible and must not be imported from file artifacts until lesson regeneration completes.

## Lesson Quality Remediation Status - 2026-06-03

The data-generator remediation batch from `../todos/data_generator_todo.md` is now implemented:

- Lesson quality contract and validator: `app/services/content_generation/generated_lesson_contract.py`
- Topic-map source context builder: `app/services/content_generation/topic_map_source_context.py`
- Scope lesson generator v2: `app/services/content_generation/scope_lesson_generator.py`
- Read-only audit and quarantine manifests: `scripts/curriculum/audit_generated_lesson_quality.py`
- Promotion/import gating via `ContentFilePromotionReadinessService` and `ContentFileArtifactImportService`

Current lesson-quality audit summary:

- Scopes with lesson files: 51.
- Scopes passing lesson-quality audit: 1 (`grade5_mathematics_en` regenerated).
- Scopes quarantined: 50.
- Total lessons audited: 6,440.
- Failed lessons remaining: 6,312.

Next batch: regenerate the remaining 50 review scopes with `scripts/curriculum/build_scope_content_artifacts.py --scope-id <scope>` and re-run the audit/manifest scripts until all scopes pass.

## Pilot Review Workflow Status - 2026-06-03

The next sharp-scope workflow is now in place for `grade5_mathematics_en`. `scripts/curriculum/build_pilot_review_packet.py` writes `data/generated/review_manifests/grade5_mathematics_en_educator_review.json` and produces a file-to-DB import plan over the generated artifact layers. The pilot currently remains `pending`, not educator-approved, with 833 importable records planned as `pending_review` DB artifacts until real educator approval metadata is attached.

Current pilot state:

- Pilot scope: `grade5_mathematics_en`.
- Review packet status: `pending`.
- Importable generated records: 833.
- Planned DB artifact status: `approved` after `dev_approved` staging unlock.
- File-to-DB import behavior: idempotent by stable artifact ID/hash; repeat imports update existing artifacts and do not duplicate source or validation evidence rows.
- `dev_approved` scope count: 50 review scopes.
- Production activation: blocked until educator approval, legal approval, evidence URLs, approval timestamps, and intentional scope activation are present.

Operational caveat: `dev_approved` is a development/staging unlock only. It does not substitute synthetic approval for educator review or legal review, and it must not unlock learner-visible production promotion by itself.

## File Import Planning Status - 2026-06-03

The Phase 7 file-to-DB staging plan now covers every `review` scope. `scripts/curriculum/build_file_artifact_import_plan.py --status review` writes `data/generated/import_manifests/all_scopes_file_artifact_import_plan.json`, summarizing per-scope record counts, layer counts, stage unlock state, production unlock state, and import blockers before any database mutation is attempted.

Current review-scope import-plan summary:

- Review scopes planned for staging import: 50.
- Stage-unlocked scopes: 1.
- Production-unlocked scopes: 0.
- Planned file artifact records: 35,466 for scopes with regenerated lesson layers.
- Scopes with import-plan errors: 49 (lesson layer still quarantined).

Operational caveat: the import plan excludes quarantined lesson records and reports blocking errors until regenerated lessons pass the lesson-quality audit. Learner-visible production promotion remains blocked by scope activation plus educator/content and legal approval evidence.

## File Import Rollback Status - 2026-06-03

The Phase 7 rollback side now has a file-backed manifest for the review-scope import plan. `scripts/curriculum/build_file_artifact_rollback_manifest.py --status review` writes `data/generated/rollback_manifests/all_scopes_file_artifact_rollback_manifest.json`, listing the exact generated artifact IDs grouped by scope and layer plus the rollback actions needed to remove file-imported Content Factory records, source evidence rows, and validation evidence rows.

Current review-scope rollback-manifest summary:

- Rollback scopes covered: 50.
- Rollback-addressable artifact IDs: 41,754.
- Scopes with rollback-plan errors: 0.
- Production-unlocked scopes: 0.
- Rollback supported for staging/import artifacts: yes.

Operational caveat: this rollback manifest covers non-production file-import artifacts. It does not authorize or perform production rollback; production promotion remains unavailable for review scopes until educator/content approval, legal approval, and intentional activation are complete.

## Target Coverage

### Supported Grades

EduBoost product copy and backend descriptions reference Grade R to Grade 7. The expansion should therefore cover:

- Grade R
- Grades 1, 2, 3
- Grades 4, 5, 6
- Grade 7

### Subject Coverage Policy

The implementation should not hard-code a guessed subject list into generation scripts. Instead, it should build an authoritative CAPS source inventory first, then derive scope records from that inventory.

Initial planning subjects by phase:

- Foundation Phase, Grade R to Grade 3:
  - Home Language
  - First Additional Language
  - Mathematics
  - Life Skills
- Intermediate Phase, Grade 4 to Grade 6:
  - Home Language
  - First Additional Language
  - Mathematics
  - Natural Sciences and Technology
  - Social Sciences
  - Life Skills
- Senior Phase entry, Grade 7:
  - Home Language
  - First Additional Language
  - Mathematics
  - Natural Sciences
  - Social Sciences
  - Technology
  - Economic Management Sciences
  - Creative Arts
  - Life Orientation

Language coverage should be phased. English should remain the first production language for platform validation. South African language localization should follow after the English artifact pipeline is stable, with translation/proofing controls rather than direct uncontrolled generation.

## Canonical Scope Model

Generalize `data/content_factory/scopes.json` into the source of truth for all curriculum slices.

Each scope should include:

- `scope_id`, for example `grade5_mathematics_en`.
- `grade`.
- `phase`, for example `foundation`, `intermediate`, `senior`.
- `subject_code`.
- `subject`.
- `language`.
- `curriculum`, default `CAPS`.
- `curriculum_version`.
- `status`, one of `planned`, `source_loaded`, `generating`, `review`, `active`, `retired`.
- `topic_map_path`.
- `caps_refs`.
- `source_documents`, with title, publisher, file/path/hash, and extraction date.
- `coverage_policy_id`.
- `review_policy_id`.

Recommended subject codes:

- `M`: Mathematics
- `HL`: Home Language
- `FAL`: First Additional Language
- `LS`: Life Skills
- `NST`: Natural Sciences and Technology
- `NS`: Natural Sciences
- `SS`: Social Sciences
- `TECH`: Technology
- `EMS`: Economic Management Sciences
- `CA`: Creative Arts
- `LO`: Life Orientation

## Artifact Set Per Scope

Every active scope should have the same artifact layers:

1. CAPS topic map
   - One canonical topic map per grade/subject/language.
   - Includes terms, weeks, topics, subtopics, assessment standards, prerequisites, vocabulary, misconceptions, and source citations.

2. Diagnostic item bank
   - Multiple-choice and short-response items where suitable.
   - Difficulty labels and IRT seed fields.
   - Misconception tags.
   - Answer-key verification.
   - CAPS reference linkage.
   - Safety and PII checks.

3. Lessons
   - At least the existing variants: `standard`, `visual`, `story`, `step_by_step`, `real_world_sa`, `exam_style`.
   - Phase-aware reading level and pedagogy.
   - Worked examples, practice questions, answer keys, remediation hints, extension prompts, and parent/teacher explanation notes.

4. Assessment blueprints
   - Baseline diagnostic per scope.
   - Topic diagnostic per CAPS ref.
   - Short practice quiz per CAPS ref.
   - Recheck assessment per CAPS ref.
   - Term review assessment per term.
   - End-of-year readiness assessment per grade/subject.

5. Study-plan templates
   - Weekly templates per scope.
   - Topic sequence.
   - Prerequisite graph.
   - Remediation mappings.
   - Extension mappings.
   - Term pacing templates.

6. Run manifest
   - Generator version.
   - Source hashes.
   - Prompt template versions.
   - Model/provider metadata.
   - Counts generated, rejected, reviewed, approved.
   - Validation results.

## Minimum Content Targets

Use a tiered target so the project can ship progressively without pretending the full curriculum is done.

### Pilot Target Per CAPS Ref

- 20 approved diagnostic items.
- 4 approved lessons.
- 3 assessment blueprints.
- 1 study-plan mapping.

### Production Target Per CAPS Ref

- 40 approved diagnostic items.
- 8 approved lessons.
- 4 assessment blueprints.
- 3 study-plan mappings.

### Mature Target Per CAPS Ref

- 80 approved diagnostic items.
- 12 approved lessons.
- 6 assessment blueprints.
- 5 study-plan/remediation mappings.
- Calibrated IRT parameters from learner telemetry.

The existing Grade 4 Mathematics launch slice already meets the production target for its three launch refs. It does not yet cover all Grade 4 Mathematics CAPS refs.

## Implementation Phases

### Phase 1 - Generalize Content Infrastructure

Goal: make the current Grade 4 Maths pipeline work for any scope.

Tasks:

- Replace `LAUNCH_REFS` hard-coding in validators/builders with scope-driven input.
- Add `scripts/curriculum/validate_scope_content.py`.
- Add `scripts/curriculum/build_scope_content_artifacts.py`.
- Add `scripts/curriculum/report_content_coverage.py`.
- Normalize artifact naming: `grade{grade}_{subject_slug}_{language}_{layer}.json`.
- Make `data/content_factory/scopes.json` the registry used by builders and validators.
- Add CI checks for schema validity and minimum coverage on active scopes.

Acceptance checks:

- Existing Grade 4 Maths artifacts validate through the new generic validator.
- `scripts/validate_launch_content.py` becomes a wrapper or compatibility shim.
- Coverage report lists active/planned scopes and gaps.

### Phase 2 - Authoritative CAPS Source Inventory

Goal: create complete scope definitions from real curriculum sources.

Tasks:

- Create `data/caps/source_documents/manifest.json`.
- Add one source record per CAPS document used.
- Store source hash, publisher, curriculum phase, grade range, subjects, language, and retrieval/proofing metadata.
- Build extraction templates for topic maps.
- Add human-review checkpoints for every extracted topic map.

Acceptance checks:

- Every planned scope points to an authoritative source document.
- Every topic map has source citations and a reviewer/proofing status.
- No generation can run for a scope without an approved topic map.

### Phase 3 - Complete Grade 4 Mathematics

Goal: finish the current strongest area before broad expansion.

Tasks:

- Expand Grade 4 Mathematics from the current three Term 1 refs to all Grade 4 Mathematics CAPS refs across all four terms.
- Generate/validate production-target diagnostic items, lessons, blueprints, and study-plan mappings.
- Keep the existing launch slice active while marking new refs as `review` until validated.

Acceptance checks:

- All Grade 4 Mathematics refs have topic maps.
- All Grade 4 Mathematics refs meet at least pilot targets.
- Priority refs meet production targets.
- Learner-facing coverage endpoint reports no unknown active Grade 4 Mathematics refs.

### Phase 4 - Expand Mathematics Grade R to Grade 7

Goal: build complete Mathematics coverage across supported grades.

Order:

1. Grade 5 Mathematics
2. Grade 6 Mathematics
3. Grade 3 Mathematics
4. Grade 2 Mathematics
5. Grade 1 Mathematics
6. Grade R Mathematics/Numeracy-aligned scope
7. Grade 7 Mathematics

Rationale:

- Grade 4 already gives reusable intermediate-phase patterns.
- Grades 5 and 6 share closer structure with Grade 4.
- Foundation Phase needs different pedagogy, language level, and item types.
- Grade 7 introduces senior-phase readiness and more formal assessment patterns.

Acceptance checks:

- Each Mathematics scope reaches pilot target before becoming learner-visible.
- Each Mathematics scope reaches production target before marketing claims say it is complete.

### Phase 5 - Expand High-Impact Non-Math Subjects

Goal: add breadth without losing review quality.

Recommended order:

1. English/Home Language and First Additional Language scaffolding.
2. Natural Sciences and Technology for Grades 4 to 6.
3. Natural Sciences for Grade 7.
4. Life Skills for Grade R to 6 and Life Orientation for Grade 7.
5. Social Sciences for Grades 4 to 7.
6. Technology, EMS, and Creative Arts for Grade 7.

Language-subject handling:

- Treat language learning differently from content subjects.
- Add reading comprehension passages, vocabulary, grammar, writing prompts, oral-language tasks, and rubric-based assessment blueprints.
- Avoid using only multiple-choice items for language subjects.

Acceptance checks:

- Each subject has a subject-specific schema extension where required.
- Validators reject artifacts that use Mathematics-only assumptions in language/life-skills/social-science subjects.

### Phase 6 - Localization and South African Language Expansion

Goal: support language diversity without weakening trust.

Tasks:

- Start from approved English artifacts where translation is appropriate.
- Use source-language topic maps for Home Language subjects where translation is not enough.
- Add translation memory and glossary files.
- Add bilingual reviewer workflow.
- Track source artifact ID and translated artifact ID separately.

Acceptance checks:

- Localized artifacts retain CAPS ref, meaning, grade level, and safety status.
- A reviewer fluent in the target language is recorded before learner visibility.

### Phase 7 - Database Seeding and Promotion

Goal: move generated files into application-serving storage reliably.

Tasks:

- Generalize seeding scripts for all artifact layers.
- Promote only `approved` artifacts into production tables.
- Preserve provenance metadata in database records.
- Add idempotent upserts keyed by stable artifact IDs.
- Add rollback manifests.

Acceptance checks:

- Re-running seed scripts does not duplicate artifacts.
- Promotion can be tested from clean database to active content state.
- Rollback can remove/promote by manifest ID.

### Dev Approval Policy

`dev_approved` is allowed as an interim development stamp for generated scope artifacts that have been reviewed by the implementation owner for structure, schema validity, source linkage, and staging/import readiness. It may unlock DB import and staging preparation by mapping generated file artifacts to approved Content Factory records for non-production workflows. It must not satisfy production approval. Production remains blocked until educator/content approval and legal approval evidence are recorded separately, with reviewer/approver identity, evidence URL, and timestamp.

### Phase 8 - Quality, Safety, and Human Review Operations

Goal: keep content quality high as volume increases.

Required gates:

- Schema validation.
- CAPS reference validation.
- Source citation validation.
- Answer-key verification.
- Age/phase reading-level check.
- PII check.
- Safety classification.
- Bias/cultural-context check.
- Duplicate/similarity check.
- Reviewer approval for production status.

Review workflow:

- Auto-generation creates `candidate` artifacts.
- Automated gates move passing artifacts to `review_ready`.
- Educator review moves artifacts to `approved` or `rejected`.
- Production promotion only reads `approved` artifacts.

Acceptance checks:

- No learner-visible route returns `candidate` or `review_ready` content.
- Every approved artifact has validation evidence and reviewer/provenance metadata.

### Phase 9 - Coverage Observability

Goal: make missing material visible to admins and CI.

Tasks:

- Extend content coverage service to report by grade, subject, term, CAPS ref, and artifact layer.
- Add dashboard views for active/planned/review scopes.
- Add coverage threshold alerts.
- Add CI summary artifact for coverage deltas.

Acceptance checks:

- Admin can see exact missing refs by subject/grade.
- CI fails when active scope coverage drops below target.
- Coverage reports distinguish `planned`, `review`, and `active` states.

## Engineering Work Items

### New/Changed Files

Planned files:

- `data/caps/source_documents/manifest.json`
- `data/caps/topic_maps/{scope_id}.json`
- `data/generated/items/{scope_id}_item_bank.json`
- `data/generated/lessons/{scope_id}_lessons.json`
- `data/generated/assessment_blueprints/{scope_id}_blueprints.json`
- `data/generated/study_plans/{scope_id}_templates.json`
- `data/generated/run_manifests/{scope_id}_{run_id}.json`
- `scripts/curriculum/validate_scope_content.py`
- `scripts/curriculum/build_scope_content_artifacts.py`
- `scripts/curriculum/report_content_coverage.py`
- `tests/unit/test_scope_content_validator.py`
- `tests/integration/test_content_scope_promotion.py`

Files to generalize:

- `scripts/validate_launch_content.py`
- `scripts/curriculum/build_launch_content_artifacts.py`
- `scripts/curriculum/build_launch_item_bank.py`
- `data/content_factory/scopes.json`
- `data/content_factory/coverage_targets.json`
- `app/modules/lessons/caps_topic_map_service.py`
- `app/services/content_coverage_service.py`
- `app/api_v2_routers/content_factory.py`
- `app/api_v2_routers/learner_content.py`

## Data Model Requirements

Before full population, confirm database support for:

- Grade and subject scope lookup.
- Multiple languages per scope.
- Artifact provenance metadata.
- Review status and reviewer identity.
- Versioned artifacts.
- Promotion manifests.
- Artifact deactivation without deletion.
- Source citation fields.

If any of these are missing, add migrations before bulk seeding.

## Generation Strategy

Recommended generation mode:

1. Deterministic scaffold from topic map.
2. LLM-assisted candidate generation using approved prompt templates.
3. Automated validation and answer-key checking.
4. Similarity/deduplication pass.
5. Educator review.
6. Promotion to approved artifact bank.

Do not generate the entire curriculum in one unreviewed batch. Generate per scope, per term, with coverage reports after every run.

## Suggested Rollout Waves

### Wave 0 - Pipeline Generalization

- No new curriculum claims.
- General validator works for Grade 4 Maths.
- Coverage report exists.

### Wave 1 - Full Grade 4 Mathematics

- Complete all Grade 4 Mathematics refs.
- Establish production operating rhythm.

### Wave 2 - Intermediate Phase Mathematics

- Grade 5 Mathematics.
- Grade 6 Mathematics.

### Wave 3 - Foundation/Senior Mathematics

- Grade R to Grade 3 numeracy/mathematics.
- Grade 7 Mathematics.

### Wave 4 - Language and NST

- English language scopes.
- Natural Sciences and Technology Grades 4 to 6.
- Natural Sciences Grade 7.

### Wave 5 - Remaining Subjects

- Life Skills and Life Orientation.
- Social Sciences.
- Technology.
- EMS.
- Creative Arts.

### Wave 6 - Localization

- Prioritized South African languages based on product strategy, user demand, and reviewer availability.

## Acceptance Definition for `Complete Scope`

A grade/subject/language scope is complete when:

- Topic map covers all CAPS terms/refs for that scope.
- All topic-map refs have source citations.
- Every ref meets production target counts.
- All artifacts pass automated validators.
- All learner-visible artifacts are approved.
- Study-plan templates cover all terms.
- Baseline, topic, practice, recheck, term, and year-end assessments exist.
- Seed/promotion is idempotent.
- Coverage endpoint reports the scope as complete.
- CI validates the scope without hard-coded exceptions.

## Immediate Next Implementation Batch

1. Add generic scope validator while preserving `validate_launch_content.py` compatibility.
2. Add content coverage report command over `data/content_factory/scopes.json`.
3. Convert Grade 4 Maths launch validation to use the generic scope registry.
4. Add planned scope records for all Grade R to 7 subjects with `status: planned` and empty `caps_refs` until source extraction is approved.
5. Add source-document manifest schema and a placeholder manifest with no learner-visible activation.
6. Add tests proving planned scopes do not count as active content and cannot be served to learners.

This keeps the next PR small, avoids pretending content exists before it has been reviewed, and creates the machinery needed to populate the rest of the curriculum safely.