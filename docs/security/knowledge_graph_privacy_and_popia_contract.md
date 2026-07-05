---
title: "Knowledge Graph Privacy and POPIA Contract"
status: active
owner: privacy
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

# Knowledge Graph Privacy and POPIA Contract

## Purpose

This document defines privacy, POPIA, audit, and data-rights expectations for EduBoost learner graph data.

## Data classification

| Data | Classification |
|---|---|
| CAPS graph | Non-personal curriculum data. |
| Target graph | Non-personal educational policy/configuration data. |
| Learner graph | Derived personal information. |
| Evidence events | Personal information / educational records. |
| Parent explanations | Personal information when tied to a learner. |
| Aggregated anonymous graph analytics | Non-personal only if properly anonymised. |

## POPIA requirements

Learner graph data must participate in data export, correction request, processing restriction, erasure request where legally valid, consent-bound access control, retention rules, and audit logging.

## Explainability requirement

For every learner-state claim exposed to parents, guardians, educators, or learners, EduBoost should be able to explain which CAPS node the claim relates to, what evidence contributed, when the state was last updated, whether confidence is high or low, and what the next recommended action is.

## Access control

Graph APIs must enforce authenticated actor identity, guardian/learner relationship checks, educator or admin scope checks where applicable, active consent checks, and object-level authorisation.

## Evidence payload sensitivity

`kg_evidence_events.evidence_payload` can hold structured signals (scores, response times) or free-text content (open-ended answers, tutor chat excerpts). Structured evidence follows the standard learner-graph classification above. Free-text evidence that could contain a learner's own words must use the same field-level encryption pattern already established for guardian contact data (AES-256-GCM with HMAC for integrity) rather than being stored as plain JSON, since free text is harder to redact selectively during correction or partial-erasure requests.

## Erasure and retention

Erasure must not corrupt non-personal CAPS graph records. It must delete, anonymise, or restrict learner-specific state and evidence according to policy.

Recommended treatment: keep CAPS graph and target graph intact; erase or anonymise learner graph state and learner evidence events; retain minimum audit records required for legal and operational proof.

## Open item

This contract requires retention rules but does not set retention periods. A specific retention period for learner graph state and evidence events (e.g. tied to academic year, account closure, or a fixed maximum) needs sign-off from whoever owns POPIA compliance before KG-3 exit, so shadow-mode fixtures can test actual expiry behaviour rather than an assumed one.

## Audit event requirements

The following events should be audit logged: learner graph created, evidence event recorded, learner state updated, target graph generated, graph state exported, graph state corrected, graph state erased/restricted, graph-based generation approved, and graph-based recommendation shown to user.

## Safety boundary

Low-confidence learner graph inferences should not be presented as facts. Parent and learner surfaces must distinguish mastered, developing, needs support, and insufficient evidence.
