---
title: "Knowledge Graph Pivot Risk Register"
status: active
owner: risk
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

# Knowledge Graph Pivot Risk Register

## Purpose

This register tracks risks introduced by pivoting EduBoost's core learning model to a knowledge graph architecture.

| ID | Risk | Severity | Likelihood | Mitigation | Owner |
|---|---|---:|---:|---|---|
| KG-R1 | Pivot expands scope beyond Grade 4 Mathematics beta before foundations are proven. | High | Medium | Keep beta scope fixed; require roadmap approval for scope expansion. | Product / Engineering |
| KG-R2 | CAPS graph mappings contain incorrect prerequisite or topic relationships. | High | Medium | Use review statuses, source evidence, and curriculum reviewer approval before production use. | Curriculum Review |
| KG-R3 | Learner graph state is treated as fact despite low evidence/confidence. | High | Medium | Store confidence and evidence count; display low-confidence states as insufficient evidence. | Engineering / UX |
| KG-R4 | POPIA data-rights workflows omit learner graph or evidence event data. | Critical | Medium | Add graph fixtures to export, correction, restriction, and erasure tests. | Security / Compliance |
| KG-R5 | AI generation invents graph relationships or unsupported mastery claims. | High | Medium | Fail closed when graph grounding is missing; validate output metadata. | AI Safety |
| KG-R6 | PostgreSQL graph queries become slow as graph coverage grows. | Medium | Medium | Start with indexes and measured query plans; evaluate graph database only after evidence. | Backend |
| KG-R7 | Existing diagnostics, IRT, and progress logic diverge from graph state. | High | High | Run learner graph in shadow mode; compare outputs before authority switch. | Diagnostics / Backend |
| KG-R8 | Documentation and implementation drift after the pivot. | Medium | High | Require docs verifier and index updates in PR checks. | Engineering |
| KG-R9 | Parent-facing explanations become too technical. | Medium | Medium | Define user-facing explanation vocabulary and UX tests. | Product / UX |
| KG-R10 | Badges reward activity instead of verified learning progress. | Medium | Medium | Tie gamification to evidence-backed graph transitions. | Product |
| KG-R11 | Authority switch happens before full verification. | Critical | Low | Require explicit gate approval and green verification checklist. | Release Manager |
| KG-R12 | Existing audit blockers remain unresolved and undermine pivot implementation. | Critical | Medium | Keep audit blockers as prerequisites in roadmap. | Engineering |
| KG-R13 | `verify_phase02r_knowledge_graph_pivot_docs.py` passing is mistaken for evidence that mappings, schema, or generation are correct. It only confirms required files exist and index files reference them. | High | High | Treat a docs-verifier pass as necessary but not sufficient; require the schema, CAPS graph, target graph, learner graph, and generation-grounding verifiers (see verification plan) before any "recorded" or "done" status is reported at phase-gate reviews. | Engineering / Release Manager |
| KG-R14 | Graph-grounded generation builds a second, parallel retrieval mechanism instead of reusing the existing Phase 2 `EmbeddingService`/`RetrievalService`, producing two definitions of "approved source evidence." | Medium | Medium | Require grounded generation and CAPS mapping work to call the existing retrieval service; treat a new retrieval implementation as a documentation/architecture deviation requiring ADR update. | Engineering |

## Active controls

- ADR-030 defines the architectural decision.
- Documentation verifier confirms core docs and indexes exist.
- Phase 02R gates continue to control source acquisition, extraction, retrieval, generation, tutor integration, migration, and closure.
- Graph state remains shadow-mode until evidence supports authority switch.
