# Data Generator Remediation TODO

Date: 2026-06-03

Branch: `implementation/study-material-expansion-foundation`

## Purpose

Fix the generated lesson-data failure discovered during review of the Study Material Expansion artifacts. The current lesson files are schema-shaped placeholders, not usable educational lessons. This plan defines the work required to quarantine the bad layer, upgrade validators, regenerate lessons with real instructional content, and refill all missing required fields before any staging, production promotion, or learner-visible claim can proceed.

This file is intentionally operational. It should drive the next implementation batches.

## Incident Summary

Manual review and random sampling found the generated lessons follow a repeated template rather than teaching the CAPS topic.

Observed defects:

- Every sampled lesson uses generic worked-example steps such as `Start with the known facts`, `Work one step at a time`, `Write the answer clearly`, and `Explain why the answer makes sense`.
- The worked-example answer is repeatedly `The final answer is checked and explained.`
- Practice questions restate the topic rather than assess the skill, for example `Which answer shows the best idea for [topic]?`.
- The correct option is always `A`.
- Answer keys repeat the same answer text within each lesson.
- The material claims topic linkage, but it does not actually teach the topic or provide topic-specific modelling.
- Teacher/parent guidance is absent or generic.

Aggregate evidence from the generated lesson set:

- Lesson files inspected: 51.
- Lesson records inspected: 6,440.
- Missing `lesson_body`: 6,440 / 6,440.
- Missing `title`: 6,440 / 6,440.
- Missing `scope_id`: 6,440 / 6,440.
- Missing `variant`: 6,440 / 6,440.
- Missing `teacher_notes`: 6,440 / 6,440.
- Missing `parent_notes`: 6,440 / 6,440.
- Missing `extension_prompts`: 6,440 / 6,440.
- Practice questions with correct option `A`: 19,320 / 19,320.
- Lessons with internally identical answer keys: 6,440 / 6,440.

Conclusion: the generated lesson layer is invalid as educational content. Counts, hashes, and source provenance are not enough; lesson substance must be validated before staging or promotion.

## Current Risk

The review-scope lesson layer has already been included in generation summaries, promotion readiness manifests, import plans, and rollback manifests. Those artifacts correctly block production, but they currently overstate staging/import readiness because they treat placeholder lessons as acceptable generated records.

Immediate risk controls required:

- Revoke lesson-layer staging eligibility for all review scopes until lesson quality validators pass.
- Preserve diagnostic item, blueprint, topic-map, and study-plan work only if their own quality audits pass separately.
- Keep all 50 review scopes non-learner-visible.
- Do not run DB import for generated lessons until this plan is implemented.

## Desired End State

Every generated lesson must be a real CAPS-aligned teaching artifact, not a template placeholder.

Each lesson record must include:

- `lesson_id` stable deterministic UUID.
- `scope_id` matching the scope registry.
- `caps_ref` matching the topic map and scope refs.
- `title` that names the grade, topic, and lesson focus.
- `variant`, one of `standard`, `visual`, `story`, `step_by_step`, `real_world_sa`, `exam_style` unless a subject-specific variant set is explicitly defined.
- `lesson_body` with actual teaching content.
- `learning_objectives` that are topic-specific, not only generic skills.
- `worked_examples` with concrete topic-specific questions, full solutions, and correct answers.
- `practice_questions` that vary by question, option order, and reasoning path.
- `answer_key` with correct answers that match the questions and are not all identical.
- `remediation_hints` tied to real misconceptions for the CAPS ref.
- `extension_prompts` that require deeper thinking or application.
- `teacher_notes` with classroom guidance, common errors, pacing, and assessment cues.
- `parent_notes` with plain-language support guidance.
- `source_citations` or equivalent source linkage back to the topic map/source document.
- `reading_level` or phase-appropriate language marker.
- `safety_status`, `pii_status`, and validation metadata.

## Non-Negotiable Quality Rules

Automated validation must reject a lesson if any of these are true:

- `lesson_body` is missing, empty, or below a minimum length threshold.
- `title`, `scope_id`, `variant`, `teacher_notes`, `parent_notes`, or `extension_prompts` is missing.
- Worked-example solution steps match the known placeholder phrases.
- Worked-example answer equals `The final answer is checked and explained.`
- More than one practice question in a lesson has the same `question_text`.
- All practice questions use the same correct option.
- All answer-key entries in a lesson have the same answer text.
- Question text is only `Which answer shows the best idea for [topic]?` or another generic topic-restatement pattern.
- Options are generic study behaviours instead of topic-specific answers.
- The lesson does not include at least one concrete example using grade-appropriate content.
- Teacher notes only restate the lesson or use generic instruction language.
- Parent notes only restate the lesson or use generic instruction language.
- The content cannot be traced to the scope topic map and source document.

## Phase 0 - Quarantine Bad Lesson Layer

Goal: prevent the current placeholder lessons from being treated as staging-ready.

Tasks:

- Add a lesson-quality audit script, initially read-only, that reports the failure counts above.
- Add a quarantine manifest under `data/generated/quality_manifests/` for generated lessons.
- Update promotion readiness so review scopes are not `staging_eligible` when the lesson layer fails the quality audit.
- Update file import planning so lesson records with failed quality status are excluded or the scope import plan reports a blocking error.
- Regenerate promotion/import/rollback manifests after quarantine logic lands.
- Update `../curriculum/StudyMaterialExpansionPlan.md` to state that lesson-layer staging has been revoked pending regeneration.

Acceptance checks:

- Current generated lesson set fails the new quality audit.
- All 50 review scopes become blocked for full-layer staging because lessons are quarantined.
- Production remains blocked as before.
- No existing active Grade 4 launch lesson behavior regresses unless the active launch lesson files also fail the new audit.

## Phase 1 - Add Lesson Content Contract

Goal: define what a valid lesson must contain before generator work resumes.

Tasks:

- Add or extend a domain model for generated lesson records.
- Define required fields and minimum structure by subject family:
  - Mathematics.
  - Languages.
  - Natural sciences / technology.
  - Social sciences.
  - Life skills / life orientation.
  - Creative arts.
  - Coding and robotics.
- Add subject-specific validation rules for question type, examples, and teacher/parent notes.
- Add fixture tests with one valid lesson and several invalid placeholder lessons.

Acceptance checks:

- Placeholder template lessons fail deterministically.
- A hand-written valid fixture passes.
- Validator errors point to exact `lesson_id`, `caps_ref`, field, and reason.

## Phase 2 - Fix Generator Inputs

Goal: provide enough source and topic context for the generator to write real lessons.

Tasks:

- Audit topic maps for the information needed by lessons: term, week, topic, subtopic, vocabulary, misconceptions, examples, prerequisites, and source citations.
- Where topic maps lack enough lesson-specific detail, add extraction work items rather than generating vague content.
- Build a source-context payload per `scope_id` + `caps_ref`.
- Include grade, phase, subject, language, CAPS ref, topic title, subtopics, vocabulary, misconceptions, prerequisite refs, and citation snippets in the generator payload.
- Ensure lesson generator does not rely only on topic names.

Acceptance checks:

- Every generated lesson run manifest records the source-context hash.
- Generator refuses to run when source context is missing or too thin.
- The generated prompt/payload can be inspected for each failed lesson.

## Phase 3 - Rewrite Lesson Generator

Goal: generate complete, varied, subject-aware lessons.

Tasks:

- Replace the placeholder lesson scaffold in `app/services/content_generation/lesson_generator.py` or equivalent generator code.
- Generate one lesson per `caps_ref` and variant, with variant-specific pedagogy.
- Ensure each lesson has:
  - A concrete mini-teaching sequence.
  - At least two worked examples with specific values, passages, scenarios, source prompts, or practical tasks as appropriate.
  - At least three varied practice questions.
  - A matching answer key.
  - Remediation and extension sections.
  - Teacher and parent notes.
- Add deterministic variation so option `A` is not always correct.
- Add subject-specific generators where the common generator would be too generic.

Acceptance checks:

- Random samples across subjects no longer share the same wording pattern.
- Correct answer distribution is balanced enough to avoid a single-option pattern.
- Practice questions within a lesson are distinct.
- Worked examples include topic-specific answers, not generic confirmation text.

## Phase 4 - Regenerate Lessons Safely

Goal: replace bad lesson files with validated lesson content.
