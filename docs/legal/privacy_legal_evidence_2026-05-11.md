# Privacy And Legal Evidence

Date: 2026-05-11
Branch: `codex/pr20-privacy-legal-evidence`
Base: `codex/pr19-database-resilience-evidence`

## Purpose

This document records the privacy, POPIA consent-gate, audit, and legal-document
evidence for the production-readiness PR series.

## Code Changes

- Added learner authorization and active POPIA consent checks to diagnostic session recovery, next-item, and response routes.
- Updated the POPIA consent-gate inventory generator to skip test modules and
  nested helper functions, so the inventory reflects production callable
  surfaces rather than test harness and nested closure artifacts.
- Regenerated the POPIA consent-gate allowlist, consent-gate inventory, and
  consent boundary matrix.

## Local Green Checks

The following commands passed:

```bash
make popia-consent-gate-check
make popia-consent-boundary-check
python3 scripts/check_popia_legal_evidence.py
python3 scripts/check_popia_consent_audit_evidence.py
python3 scripts/check_popia_consent_closure.py
python3 scripts/check_privacy_boundary_evidence.py
```

Observed result:

- POPIA consent-gate check reports 190 missing local consent markers, 190
  baseline allowlist entries, 0 new unallowlisted missing markers, and 0 stale allowlist entries.
- POPIA consent-boundary matrix check passed.
- POPIA/legal evidence check passed.
- POPIA consent/audit evidence check passed.
- POPIA consent closure check passed.
- Privacy boundary evidence check passed.

## Release Blockers

- Legal documents remain templates/evidence artifacts, not external legal
  advice or signed approval.
- The consent allowlist still needs human release review. Items that are not
  acceptable internal helpers should be converted to explicit local consent
  markers.
- Data export, erasure, correction, restriction, and audit-chain workflows still
  need staging execution evidence.

## Release Claim

This PR closes the automated POPIA consent-gate delta on the clean branch and
records legal/privacy evidence. It does not claim external legal sign-off,
staging POPIA workflow validation, or production privacy readiness.
