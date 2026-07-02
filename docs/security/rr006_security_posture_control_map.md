---
title: "RR-006 Security Posture Control Map"
status: active
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-02
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, .github/workflows/rr006-security-posture.yml]
---

# RR-006 Security Posture Control Map

**Status:** active after RR-006 evidence capture  
**Register item:** RR-006  
**Scope:** V2 security posture for controlled beta and later release readiness.

## Required controls

| Control | Evidence anchor | Required state |
|---|---|---|
| V2 threat model | `docs/security/threat_model_v2.md` and `docs/security/rr006_threat_model_review.md` | reviewed and current enough for beta/security review |
| Pen-test checklist | `docs/security/v2_pen_test_checklist.md` | checklist exists and covers auth, authorization, POPIA, API, LLM, frontend, infra, and observability |
| Dependency vulnerability scanning | `.github/workflows/rr006-security-posture.yml` | CI-visible and release-blocking for critical findings unless explicitly waived |
| Python dependency audit | `.github/workflows/rr006-security-posture.yml` and `docs/security/python_dependency_audit_policy.md` | `pip-audit` or equivalent is required for Python dependency changes |
| Secrets scanning in pre-commit | `.pre-commit-config.yaml` | `detect-secrets` hook configured |
| Secrets scanning in CI | `.github/workflows/secrets-scan.yml` and `.github/workflows/rr006-security-posture.yml` | CI-visible scan required |
| Boundary preservation | `docs/roadmap/reconciliation/rr_006_security_posture_deepening_record.json` | no production release, deployment, public beta, release tag, or runtime KG authority |

## Boundary

RR-006 improves security posture only. It does not approve production deployment, public beta, release tagging, expanded learner migration, or runtime KG implementation.
