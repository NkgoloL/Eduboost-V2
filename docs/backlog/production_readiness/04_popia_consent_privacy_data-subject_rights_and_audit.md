# 4. POPIA consent, privacy, data-subject rights, and audit

## 4.1 Consent lifecycle

- [ ] `P0` Define consent state `pending`.
- [ ] `P0` Define consent state `granted`.
- [ ] `P0` Define consent state `denied`.
- [ ] `P0` Define consent state `expired`.
- [ ] `P0` Define consent state `withdrawn`.
- [ ] `P0` Define consent state `renewal_required`.
- [ ] `P0` Implement consent grant flow.
- [ ] `P0` Implement consent denial flow.
- [ ] `P0` Implement consent withdrawal flow.
- [ ] `P0` Implement consent renewal flow.
- [ ] `P0` Implement consent expiry handling.
- [ ] `P0` Implement restricted mode after consent expiry if applicable.
- [ ] `P0` Tie consent to privacy notice version.
- [ ] `P0` Tie consent to guardian identity.
- [ ] `P0` Tie consent to learner identity.
- [ ] `P0` Audit every consent state change.
- [ ] `P1` Add consent expiry notification schedule.
- [ ] `P1` Add grace period policy if required.
- [ ] `P1` Add consent status dashboard for guardians.
- [ ] `P2` Add school-mediated consent model if institutional deployments enter scope.

## 4.2 Declarative consent enforcement

- [ ] `P0` Make consent enforcement declarative through FastAPI dependency or middleware.
- [verify] `P0` Add consent gate checker. Evidence: `scripts/generate_consent_gate_inventory.py`, `scripts/check_consent_gate_inventory.py`, `make popia-consent-gate-check`.
- [verify] `P0` Identify all learner-data routes. Evidence: `docs/security/popia_consent_gate_inventory.md`, `docs/security/privacy_boundary_evidence.md`.
- [verify] `P0` Mark consent-required route patterns. Evidence: `docs/security/popia_consent_boundary_matrix.md`, `scripts/check_popia_consent_boundary_matrix.py`.
- [verify] `P0` Fail CI if consent-required route lacks consent gate. Evidence: `.github/workflows/privacy-boundary.yml`, `scripts/check_privacy_boundary_evidence.py`; verification gap: required-check enforcement must be configured in GitHub branch protection.
- [verify] `P0` Add negative test for diagnostics without consent. Evidence: `docs/security/diagnostics_consent_gate.md`, `tests/unit/test_diagnostics_consent_gate_wiring.py`.
- [verify] `P0` Add negative test for lessons without consent. Evidence: `docs/security/lesson_generation_consent_gate.md`, `tests/unit/test_lesson_generation_consent_gate_wiring.py`.
- [verify] `P0` Add negative test for learner profile access without consent. Evidence: `docs/security/learner_read_consent_gate.md`, `tests/unit/test_learner_read_consent_gate_wiring.py`.
- [verify] `P0` Add negative test for study plan access without consent. Evidence: `docs/security/study_plan_consent_gate.md`.
- [verify] `P0` Add negative test for gamification without consent. Evidence: `docs/security/gamification_consent_gate.md`, `tests/unit/test_gamification_consent_gate_wiring.py`.
- [ ] `P0` Add negative test for analytics processing without consent.
- [ ] `P0` Add negative test for RLHF feedback without consent.
- [ ] `P0` Add negative test for parent reports without consent.
- [ ] `P0` Add negative test for data export without consent/authority.
- [ ] `P0` Add negative test for erasure request without authority.
- [verify] `P1` Add route-level consent policy documentation. Evidence: `docs/security/privacy_boundary_evidence.md`, `docs/security/popia_consent_gate_inventory.md`, `docs/security/popia_consent_boundary_matrix.md`.

## 4.3 Data subject rights

- [ ] `P0` Implement data export request creation.
- [ ] `P0` Implement data export status endpoint.
- [ ] `P0` Implement data export download endpoint.
- [ ] `P0` Implement machine-readable JSON export.
- [ ] `P0` Implement machine-readable CSV export.
- [ ] `P1` Implement guardian-friendly PDF export summary.
- [ ] `P0` Implement erasure request creation.
- [ ] `P0` Implement erasure status endpoint.
- [ ] `P0` Implement erasure approval/review queue.
- [ ] `P0` Implement erasure execution with audit-retention exceptions.
- [ ] `P0` Implement correction/update workflow.
- [ ] `P0` Implement processing restriction workflow.
- [ ] `P0` Implement SLA tracking for export requests.
- [ ] `P0` Implement SLA tracking for erasure requests.
- [ ] `P1` Add admin review queue for billing/school/legal-retention conflicts.
- [ ] `P1` Add notification to guardian when export is ready.
- [ ] `P1` Add notification to guardian when erasure completes.
- [verify] `P1` Add tests for export workflow. Evidence: `tests/integration/test_popia_data_export_authorization.py`, `tests/integration/test_parent_export_authorization.py`; verification gap: full export artifact generation still requires release evidence.
- [verify] `P1` Add tests for erasure workflow. Evidence: `tests/popia/test_right_to_erasure.py`, `tests/integration/test_parent_erasure_authorization.py`, `tests/integration/test_popia_deletion_request_authorization.py`.
- [verify] `P1` Add tests for correction workflow. Evidence: `tests/integration/test_popia_correction_request_authorization.py`.
- [verify] `P1` Add tests for restriction workflow. Evidence: `tests/integration/test_popia_restriction_request_authorization.py`.

## 4.4 Data minimization and inventory

- [ ] `P0` Create or update `docs/data_inventory.md`.
- [ ] `P0` List every collected learner field.
- [ ] `P0` List every collected guardian field.
- [ ] `P0` List every collected diagnostic field.
- [ ] `P0` List every collected lesson/AI field.
- [ ] `P0` List every collected billing field.
- [ ] `P0` List purpose for each field.
- [ ] `P0` List lawful/consent basis for each field.
- [ ] `P0` List retention period for each field.
- [ ] `P0` List access roles for each field.
- [ ] `P0` List third-party exposure for each field.
- [ ] `P0` Remove non-essential learner data fields.
- [ ] `P0` Hash or tokenize identifiers where raw values are unnecessary.
- [ ] `P0` Separate identifiable operational data from analytics data.
- [ ] `P0` Prevent names, emails, phone numbers, and raw identifiers from LLM prompts.
- [ ] `P1` Create or update `docs/data_retention_policy.md`.
- [ ] `P1` Create or update `docs/subprocessor_register.md`.

## 4.5 Audit integrity

- [ ] `P0` Confirm sensitive events write to append-only PostgreSQL audit repository.
- [ ] `P0` Prevent application update/delete operations on audit records.
- [ ] `P0` Prevent database role update/delete on audit records where feasible.
- [ ] `P0` Add event hash to audit records.
- [ ] `P0` Add previous event hash to audit records.
- [ ] `P0` Add HMAC/signature to audit records.
- [ ] `P0` Add audit-chain verification script.
- [ ] `P0` Add audit event for login success.
- [ ] `P0` Add audit event for login failure.
- [ ] `P0` Add audit event for token refresh.
- [ ] `P0` Add audit event for logout.
- [ ] `P0` Add audit event for consent grant.
- [ ] `P0` Add audit event for consent renewal.
- [ ] `P0` Add audit event for consent withdrawal.
- [ ] `P0` Add audit event for consent expiry.
- [ ] `P0` Add audit event for learner profile create/update/delete.
- [ ] `P0` Add audit event for diagnostic start.
- [ ] `P0` Add audit event for diagnostic answer submission.
- [ ] `P0` Add audit event for diagnostic completion.
- [ ] `P0` Add audit event for lesson generation.
- [ ] `P0` Add audit event for LLM provider call.
- [ ] `P0` Add audit event for parent report generation.
- [ ] `P0` Add audit event for data export request.
- [ ] `P0` Add audit event for data export download.
- [ ] `P0` Add audit event for erasure request.
- [ ] `P0` Add audit event for erasure execution.
- [ ] `P0` Add audit event for admin access.
- [ ] `P0` Add audit event for billing changes.
- [ ] `P1` Add immutable retention rules for audit records.
- [verify] `P1` Add automated audit completeness tests. Evidence: `scripts/check_audit_event_contracts.py`, `tests/unit/test_audit_event_contracts.py`, `docs/security/audit_event_contracts.md`; verification gap: staging audit sink evidence still required.
- [ ] `P1` Build internal audit dashboard.

## 4.6 Legal/privacy docs

- [x] `P0` Draft Privacy Policy. Evidence: `docs/legal/privacy_legal_evidence_2026-05-11.md`.
- [x] `P0` Draft Terms of Service. Evidence: `docs/legal/privacy_legal_evidence_2026-05-11.md`.
- [x] `P0` Draft Parent Consent Notice. Evidence: `docs/legal/privacy_legal_evidence_2026-05-11.md`.
- [x] `P0` Draft Child-friendly Privacy Notice. Evidence: `docs/legal/privacy_legal_evidence_2026-05-11.md`.
- [ ] `P0` Draft Security Disclosure Policy.
- [ ] `P1` Complete DPIA-style privacy impact assessment.
- [ ] `P1` Conduct legal review of Privacy Policy.
- [ ] `P1` Conduct legal review of Terms of Service.
- [ ] `P1` Conduct legal review of Parent Consent Notice.
- [ ] `P1` Conduct legal review of Child-friendly Privacy Notice.
- [ ] `P1` Conduct legal review of data retention policy.
- [ ] `P1` Conduct legal review of subprocessor register.

## 4.7 Backend Consolidation Diagnostics

- [verify] `P0` Inventory all legacy audit call sites. Evidence: `docs/release/audit_callsite_inventory.md`, `scripts/generate_audit_callsite_inventory.py`, `make audit-compatibility-check`.
- [verify] `P0` Inventory all legacy consent call sites. Evidence: `docs/release/consent_callsite_inventory.md`, `scripts/generate_consent_callsite_inventory.py`, `make consent-compatibility-check`.
- [verify] `P0` Implement audit compatibility adapter. Evidence: `app/repositories/audit_compat.py`, `tests/unit/test_audit_callsite_inventory_and_compat.py`.
- [verify] `P0` Implement consent normalization service. Evidence: `app/services/consent_compat.py`, `tests/unit/test_consent_callsite_inventory_and_compat.py`.
- [verify] `P0` Establish backend consolidation readiness matrix. Evidence: `docs/release/backend_consolidation_readiness_matrix.md`, `make backend-consolidation-readiness-check`.
- [verify] `P0` Establish backend consolidation execution sequence. Evidence: `docs/release/backend_consolidation_execution_packet.md`, `make backend-consolidation-execution-packet-check`.
- [verify] `P0` Implement runtime compatibility probes. Evidence: `scripts/check_backend_runtime_probe_fixtures.py`, `make backend-runtime-probe-check`.
- [verify] `P0` Finalize terminal consolidation diagnostics. Evidence: `docs/release/backend_consolidation_terminal_report.md`, `make backend-consolidation-terminal-full-check`.

---

