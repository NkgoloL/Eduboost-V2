# 3. Authentication, sessions, RBAC, and object-level authorization

## 3.1 Authentication flows

- [ ] `P0` Verify guardian signup success path.
- [ ] `P0` Verify guardian signup validation errors.
- [ ] `P0` Verify duplicate email handling.
- [ ] `P0` Verify login success path.
- [ ] `P0` Verify login invalid password path.
- [ ] `P0` Verify login nonexistent account path.
- [ ] `P0` Verify logout revokes current token.
- [ ] `P0` Verify logout clears refresh cookie where applicable.
- [ ] `P0` Verify refresh-token success path.
- [ ] `P0` Verify refresh-token expired path.
- [ ] `P0` Verify refresh-token reuse detection.
- [ ] `P0` Verify refresh-token family revocation.
- [ ] `P0` Verify email verification flow.
- [ ] `P0` Verify password reset request.
- [ ] `P0` Verify password reset token expiry.
- [ ] `P0` Verify password reset completion.
- [ ] `P0` Verify password reset invalid token behavior.
- [ ] `P1` Add account lockout or risk-based throttling after repeated failures.
- [ ] `P1` Add security alert event for suspicious auth behavior.
- [ ] `P1` Add tests for all auth abuse paths.

## 3.2 Password security

- [ ] `P0` Verify password hashing uses bcrypt or Argon2id with tuned cost.
- [ ] `P0` Verify configured bcrypt rounds are production-safe.
- [ ] `P0` Verify password strength policy.
- [ ] `P0` Add password strength tests.
- [ ] `P1` Add breached-password check if feasible.
- [ ] `P1` Add password change flow.
- [ ] `P1` Add password change audit event.
- [ ] `P2` Add optional passphrase guidance.

## 3.3 Token policy

- [ ] `P0` Confirm access-token TTL is 15 minutes or documented override.
- [ ] `P0` Confirm refresh-token TTL is 7 days or documented override.
- [ ] `P0` Verify refresh tokens are hashed at rest.
- [ ] `P0` Verify refresh tokens are revocable.
- [ ] `P0` Verify refresh tokens are bound to token family.
- [ ] `P0` Verify refresh-token rotation on use.
- [ ] `P0` Verify token-family reuse detection.
- [ ] `P0` Verify Redis-backed revocation.
- [ ] `P0` Decide behavior when Redis revocation store is unavailable.
- [ ] `P1` Add persistent fallback for revocation if required.
- [ ] `P1` Add JWT signing-key rotation with `kid`.
- [ ] `P1` Add current signing key.
- [ ] `P1` Add previous signing key validation window.
- [ ] `P1` Add emergency revoke-all procedure.
- [ ] `P1` Add tests for `kid` rotation.
- [ ] `P1` Add tests for emergency revoke-all.

## 3.4 Cookie security

- [ ] `P0` Verify cookies are `HttpOnly`.
- [ ] `P0` Verify cookies are `Secure` in production.
- [ ] `P0` Verify cookies use correct `SameSite`.
- [ ] `P0` Verify cookie domain is correct per environment.
- [ ] `P0` Verify cookie path is correct.
- [ ] `P0` Verify no refresh token is JavaScript-readable.
- [ ] `P0` Verify no access token is stored insecurely in frontend.
- [ ] `P1` Add cookie policy tests.
- [ ] `P1` Document cookie strategy.

## 3.5 RBAC and roles

- [ ] `P0` Define role `learner`.
- [ ] `P0` Define role `parent` or `guardian`.
- [ ] `P0` Define role `teacher`.
- [ ] `P0` Define role `admin`.
- [ ] `P0` Define role `support_operator`.
- [ ] `P0` Define role `content_reviewer`.
- [ ] `P0` Define role `compliance_auditor`.
- [ ] `P1` Document role permissions.
- [ ] `P1` Add tests for each role.
- [ ] `P1` Add route policy matrix.

## 3.6 Object-level authorization

- [ ] `P0` Add policy helper `can_view_learner`.
- [ ] `P0` Add policy helper `can_update_learner`.
- [ ] `P0` Add policy helper `can_generate_lesson_for_learner`.
- [ ] `P0` Add policy helper `can_start_diagnostic_for_learner`.
- [ ] `P0` Add policy helper `can_view_study_plan`.
- [ ] `P0` Add policy helper `can_view_parent_report`.
- [ ] `P0` Add policy helper `can_export_learner_data`.
- [ ] `P0` Add policy helper `can_request_erasure`.
- [ ] `P0` Add policy helper `can_view_billing`.
- [ ] `P0` Add test that learner cannot access another learner.
- [ ] `P0` Add test that guardian can access only linked learners.
- [ ] `P0` Add test that teacher can access only assigned learners/classes.
- [ ] `P0` Add test that support cannot view unnecessary PII.
- [ ] `P0` Add test that compliance auditor can view audit records without broad data mutation rights.
- [ ] `P0` Add audit events for privileged access.
- [verify] `P1` Add policy tests for every router. Evidence: `docs/security/PHASE2_AUTHORIZATION_CLOSURE.md`, `scripts/check_phase2_authorization_evidence.py`, `scripts/check_privacy_boundary_evidence.py`; verification gap: every router still needs item-level reconciliation before this can become `[x]`.
- [ ] `P1` Move from basic RBAC to policy-based authorization for sensitive workflows.
- [ ] `P2` Add tightly audited admin impersonation only if absolutely required.

## 3.7 Rate limiting and abuse prevention

- [ ] `P0` Add rate limit to login.
- [ ] `P0` Add rate limit to signup.
- [ ] `P0` Add rate limit to refresh.
- [ ] `P0` Add rate limit to password reset.
- [ ] `P0` Add rate limit to email verification.
- [ ] `P0` Add rate limit to LLM lesson generation.
- [ ] `P0` Add rate limit to data export.
- [ ] `P0` Add rate limit to billing webhook endpoints if applicable.
- [ ] `P1` Add account-level throttling.
- [ ] `P1` Add IP-level throttling.
- [ ] `P1` Add risk-based throttling.
- [ ] `P1` Add rate-limit tests.

---

