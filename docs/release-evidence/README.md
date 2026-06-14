# EduBoost Release Evidence Repository

**Purpose:** This directory stores the authoritative evidence packages for all 13 roadmap phases plus audit remediation.

## Directory Structure

```
release-evidence/
├── programme-baseline/     # Programme-level baseline documents
├── audit-remediation/       # Independent audit remediation evidence
├── phase-00/               # Environment and Reproducibility
├── phase-01/               # Batch AI Content Generation
├── phase-02/               # Semantic Retrieval
├── phase-03/               # Educator Consensus and Content Governance
├── phase-04/               # IRT Quality and Self-Healing Controls
├── phase-05/               # Learner AI Tutor
├── phase-06/               # Monitoring, Budget, and Production Hardening
├── phase-07/               # Beta Content Coverage and Language Readiness
├── phase-08/               # Architecture and Codebase Assurance
├── phase-09/               # CI Authority and Reproducible Evidence
├── phase-10/               # Product Readiness
├── phase-11/               # Operations Readiness
├── phase-12/               # External Review and Governance
└── phase-13/               # Controlled Beta
```

## Evidence Package Contents

Each phase directory should contain:

| File | Purpose |
|---|---|
| `phase_<NN>_evidence_index.md` | Authoritative manifest for all evidence items |
| `phase_<NN>_audit_report.md` | Independent phase audit with closure verdict |
| `*.log`, `*.json`, `*.xml` | Raw test and verification outputs |
| `*.md` | Supporting analysis and reports |
| `screenshots/` | Visual evidence (where applicable) |

## Evidence Index Requirements

Each evidence index must document:

- Phase, roadmap version, execution-plan version, and evidence-pack version
- Canonical branch, base commit, merge commit, build/image digest
- Every roadmap exit criterion mapped to evidence items
- Exact command, expected result, actual result, exit code, duration
- Test counts: passed, failed, skipped, xfailed, warnings
- Hashes for generated reports, manifests, datasets
- Evidence sensitivity classification and retention period

## Access Control

| Evidence Type | Classification | Access |
|---|---|---|
| Test results, logs | Internal | Team members |
| Signed reviews | Restricted | Approvers only |
| Security scan results | Restricted | Security owner |
| Penetration test reports | Restricted | Security + Release Manager |

## Quality Rules

- **Raw or machine-readable output** required where practical
- **Screenshots** are supporting evidence only—cannot be sole proof
- **Every artifact** must have a hash or immutable reference
- **Contextual evidence** (from different commit/environment) must be labelled as such
- **Missing mandatory evidence** prevents pack from being frozen

## Programme Baseline

Programme-level baseline documents (this plan, programme-level ADRs, risk register) are stored in `programme-baseline/`.

## Related Documents

- Full lifecycle roadmap: `docs/roadmap/EduBoost_Full_Lifecycle_Delivery_and_Beta_Readiness_Plan.md`
- Phase status register: `docs/roadmap/PHASE_STATUS_REGISTER.md`
- Execution templates: `docs/roadmap/execution/phase_*_template.md`