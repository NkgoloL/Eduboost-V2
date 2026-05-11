# Privacy Boundary Evidence

This document is the review index for the privacy-boundary PR. It does not
claim production readiness by itself; it points to the implementation and
verification evidence that must stay green before real learner data or public
beta use.

## Object Authorization

- Policy documentation: `docs/security/object_authorization.md`
- Dependency wiring: `docs/security/authorization_dependencies.md`
- Phase 2 evidence check: `make phase2-authz-check`
- Phase 2 closure check: `make phase2-authz-closure`

## Consent Gates

- Route inventory: `docs/security/popia_consent_gate_inventory.md`
- Boundary matrix: `docs/security/popia_consent_boundary_matrix.md`
- Gate inventory check: `make popia-consent-gate-check`
- Boundary check: `make popia-consent-boundary-check`
- Route-order/source checks: `make popia-consent-order-check` and
  `make popia-consent-source-check`

## POPIA Data Rights

- Data-rights documentation: `docs/compliance/popia_data_rights.md`
- Retention documentation: `docs/compliance/data_retention_policy.md`
- Authorization wiring docs:
  `docs/security/popia_data_export_authorization_wiring.md`,
  `docs/security/popia_deletion_request_authorization_wiring.md`,
  `docs/security/popia_deletion_execute_authorization_wiring.md`,
  `docs/security/popia_correction_request_authorization_wiring.md`, and
  `docs/security/popia_restriction_request_authorization_wiring.md`

## Audit Completeness

- Audit event contract: `docs/security/audit_event_contracts.md`
- Consent/audit baseline: `docs/security/POPIA_CONSENT_AUDIT_BASELINE.md`
- Consent rejection audit: `docs/security/consent_rejection_audit.md`
- Audit contract check: `make audit-contract-check`
- POPIA consent/audit evidence check: `make popia-consent-audit-check`

## Aggregate Check

Run the aggregate privacy boundary check with:

```bash
make privacy-boundary-check
```

This check verifies that the object-authorization, consent, POPIA data-rights,
and audit evidence files and scripts remain present and wired through Make.

## Verification Gaps

- GitHub branch protection and required-check enforcement still need repository
  settings evidence.
- POPIA/legal documents still require legal review before public beta.
- Staging evidence is still required before these checks can support a release
  go/no-go decision.
