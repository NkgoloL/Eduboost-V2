---
title: "Python Dependency Audit Policy"
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
code_anchors: [docs/security/README.md, requirements.txt, requirements/base.txt, requirements/dev.txt]
---

# Python Dependency Audit Policy

**Status:** RR-006 control policy  
**Applies to:** Python runtime, development, documentation, and ML dependency files.

## Required files

The dependency audit must consider the dependency files that exist in the repository root, including:

- `requirements.txt`
- `requirements-dev.txt`
- `requirements-docs.txt`
- `requirements-ml.txt`

## Required CI control

Python dependency changes must be auditable through `pip-audit` or an equivalent vulnerability-audit tool. Critical vulnerabilities must block release claims unless a dated, owner-signed waiver is recorded.

## Local command

```bash
python3 -m pip install pip-audit
pip-audit -r requirements.txt
pip-audit -r requirements-dev.txt
pip-audit -r requirements-docs.txt
pip-audit -r requirements-ml.txt
```

## Boundary

This policy does not authorise production release. It defines the dependency-audit requirement that must be satisfied before a future release claim.
