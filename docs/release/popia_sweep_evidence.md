# POPIA Sweep Evidence

Generated: `2026-05-22T14:38:42.058754+00:00`

Command: `/home/nkgolol/Dev/SandBox/dev/Eduboost-V2/.venv/bin/python scripts/popia_sweep.py --fail-on-issues`

Return code: `1`

```text
Scanning 265 Python files in /home/nkgolol/Dev/SandBox/dev/Eduboost-V2/app...
================================================================================
  POPIA CHAOS SWEEP REPORT — EduBoost SA
  2026-05-22T14:38:41.513392+00:00
================================================================================
  Files scanned:        265
  Endpoints checked:    48
  Consent gates found:  22
  Issues found:         12
    • Critical:         0
    • High:             12
--------------------------------------------------------------------------------

🟠 HIGH (12 issues)
--------------------------------------------------------------------------------
  [pii_pattern_detected] app/services/auth_token_claims.py:146
  Raw PII pattern '\.(?:email|phone|date_of_birth|id_number)\b' found in
  source.
  >> "email_encrypted=user.email",

  [pii_pattern_detected] app/services/auth_token_claims.py:147
  Raw PII pattern '\.(?:email|phone|date_of_birth|id_number)\b' found in
  source.
  >> "email_encrypted = user.email",

  [pii_pattern_detected] app/services/auth_token_claims.py:148
  Raw PII pattern '\.(?:email|phone|date_of_birth|id_number)\b' found in
  source.
  >> "email_encrypted=request.email",

  [pii_pattern_detected] app/services/auth_token_claims.py:149
  Raw PII pattern '\.(?:email|phone|date_of_birth|id_number)\b' found in
  source.
  >> "email_encrypted = request.email",

  [pii_pattern_detected] app/services/auth_token_claims.py:150
  Raw PII pattern '\.(?:email|phone|date_of_birth|id_number)\b' found in
  source.
  >> "email_encrypted=body.email",

  [pii_pattern_detected] app/services/auth_token_claims.py:151
  Raw PII pattern '\.(?:email|phone|date_of_birth|id_number)\b' found in
  source.
  >> "email_encrypted = body.email",

  [missing_audit_log] app/services/popia_consent_lifecycle_adapter.py:215
  Function 'grant' modifies consent without writing an audit log entry. POPIA
  requires an immutable audit trail for all consent changes.
  >> def grant(...)

  [missing_audit_log] app/services/popia_consent_lifecycle_adapter.py:234
  Function 'revoke' modifies consent without writing an audit log entry. POPIA
  requires an immutable audit trail for all consent changes.
  >> def revoke(...)

  [pii_pattern_detected] app/services/auth_transactional_registration.py:66
  Raw PII pattern '\.(?:email|phone|date_of_birth|id_number)\b' found in
  source.
  >> email=data.email,

  [pii_pattern_detected] app/services/auth_transactional_registration.py:103
  Raw PII pattern '\.(?:email|phone|date_of_birth|id_number)\b' found in
  source.
  >> email=data.email,

  [pii_pattern_detected] app/services/auth_db_lifecycle_proof.py:192
  Raw PII pattern '["\'][\w.+-]+@[\w-]+\.[\w.-]+["\']' found in source.
  >> email="dev.guardian@example.com",

  [pii_pattern_detected] app/services/auth_db_lifecycle_proof.py:215
  Raw PII pattern '["\'][\w.+-]+@[\w-]+\.[\w.-]+["\']' found in source.
  >> email = _find_by_name(kwargs, {"email", "guardian_email", "username"}) or "guardian.success@example.com"

================================================================================

❌  Sweep failed: 0 critical + 12 high issues.

```
