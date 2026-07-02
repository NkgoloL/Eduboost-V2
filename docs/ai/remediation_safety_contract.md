---
title: "Remediation Safety Contract"
status: "active"
owner: "ai-safety"
reviewers: "[ai-safety, curriculum, privacy]"
audience: "safety-reviewer"
source_of_truth: "false"
supersedes: "[]"
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: "60"
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/services, docs/ai]"
---

# Remediation Safety Contract

## Purpose

AI-generated remediation must target observed learner gaps without exposing
sensitive learner data, unsupported diagnoses, or unsafe guidance.

## Required Remediation Inputs

- learner grade
- learner subject
- CAPS strand or skill
- observed learner gap
- learner mastery state
- remediation objective
- consent-authorized learner identifier
- safety boundary instructions

## Remediation Safety Rules

- remediation must remain educational
- remediation must not label the learner with unsupported diagnoses
- remediation must avoid unsafe instructions
- remediation must not include sexual content
- remediation must not include self-harm content
- remediation must not expose another learner's data
- remediation must not reveal parent or guardian private data

## Remediation Quality Rules

- remediation must map to the observed learner gap
- remediation must provide a next learning step
- remediation must preserve CAPS alignment
- remediation must avoid punitive or shaming language
- remediation must include safe escalation to teacher/guardian support when needed

## Command

```bash
make remediation-safety-contract-check
```
