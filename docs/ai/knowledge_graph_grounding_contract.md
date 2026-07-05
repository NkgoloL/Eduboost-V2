---
title: "Knowledge Graph AI Grounding Contract"
status: active
owner: ai-safety
reviewers: [architecture, product, privacy, curriculum, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-05
review_interval_days: 60
evidence_command: make kg000-formal-kg-roadmap-approval-check
code_anchors: []
---

# Knowledge Graph AI Grounding Contract

## Purpose

This contract defines how AI-generated lessons, assessments, tutor responses, explanations, and remediation plans must use the knowledge graph model.

## Principle

AI may generate educational language and activity variants, but it may not invent curriculum truth, learner state, or mastery claims.

## Required inputs for generation

Every graph-grounded generation request must include learner context authorised for the requesting actor, target CAPS graph node or nodes, target graph expectations, learner graph gap profile, prerequisite status, misconception markers where available, approved source evidence (retrieved via the existing Phase 2 `RetrievalService`, scoped to the target graph nodes), desired intervention type, and safety/age-appropriateness constraints.

## Required outputs

Every generated lesson or assessment must return target graph node IDs, source evidence references, prerequisite assumptions, learning objective, explanation or activity content, assessment/check-for-understanding component, expected evidence event type, remediation path if the learner fails, and refusal/escalation reason where generation is unsafe or ungrounded.

## Prohibited outputs

AI output must not create new authoritative CAPS graph nodes, claim mastery without evidence, override IRT or learner graph state directly, expose raw sensitive learner inference in a learner-facing or parent-facing response, generate content for unapproved CAPS nodes in production, or ignore known prerequisite blockers.

## Grounding failure behaviour

If required graph context or source evidence is missing, generation must fail closed with a structured error. It must not silently fall back to generic lesson generation for production paths.

## Review and evidence

Generated content can only move to approved status after validation confirms graph node references are valid, source evidence exists, generated content matches the intended grade and topic, assessment checks the stated objective, safety checks passed, and reviewer status is recorded where required.
