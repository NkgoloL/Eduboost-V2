# Phase 1 — T104 — JWT Security Review

**Branch:** `remediation/phase0-phase1`
**Date:** 2026-05-27
**Reviewer:** Engineering (Phase 1 remediation)
**Scope:** All JWT creation, verification, key management, refresh-token handling, and revocation code in `app/`.

---

## Executive summary

The JWT implementation is **functionally sound** for the current launch scope
but has **architectural debt** that should be resolved before scaling to
multiple services or adding third-party API consumers.

| Area | Rating | Notes |
|---|---|---|
| Key management | Good | `kid`-based rotation, placeholder-guard, production fail-closed. |
| Token types | Good | Access vs refresh clearly typed. |
| Revocation | Good | Per-token JTI, per-user, family-based, global epoch, DB fallback. |
| Refresh-token rotation | Good | Single-use with family binding and reuse detection. |
| Algorithm choice | Acceptable | HS256 is fine for a monolith; RS256 preferred for service mesh. |
| Claims (iss, aud) | Weak | No issuer or audience validation. |
| Token binding (DPoP) | Missing | No `cnf` claim or DPoP. |
| Implementation unity | Debt | Two competing JWT subsystems (`security.py` + `token_config.py`). |

**Triage:** 2 findings marked `fix-now` (both non-blocking for launch but
should be addressed in the next sprint), 4 findings marked `tracked-issue`,
1 finding marked `accepted-with-rationale`.

---

## Files reviewed

| File | Lines | Role |
|---|---|---|
| `app/core/security.py` | 1–197 | Main JWT create/verify dependency, password hashing, PII encryption |
| `app/core/token_config.py` | 1–242 | Alternative JWT subsystem with kid rotation, Redis revocation |
| `app/core/refresh_tokens.py` | 1–152 | Refresh-token rotation (SHA-256 hashed, family-bound) |
| `app/services/jwt_keyring.py` | 1–258 | Keyring parsing, placeholder detection, environment validation |
| `app/core/config.py` | 1–251 | Settings including JWT_SECRET default (placeholder) |
| `app/core/token_revocation.py` | (referenced) | Per-token and per-user revocation checks |

---

## Findings summary

| Finding | Severity | Release blocker? | Classification | Follow-up |
|---|---|---|---|---|
| F1 — Two competing JWT subsystems | Medium | No | `tracked-issue` | Consolidate to single canonical module (post-launch) |
| F2 — Missing `iss` and `aud` claims | Medium | No | `fix-now` | Add `iss` and `aud` to token payloads (next sprint) |
| F3 — No token binding (DPoP) | Low | No | `accepted-with-rationale` | Evaluate for Phase 2 hardening |
| F4 — Refresh-token format inconsistency | Medium | No | `tracked-issue` | Unify to opaque bytes format (post-launch) |
| F5 — No minimum key length enforcement | Medium | No | `fix-now` | Add min-length check to `validate_jwt_keyring_environment()` |
| F6 — Encryption key default is placeholder | Medium | No | `tracked-issue` | Add production placeholder check for `ENCRYPTION_KEY` |

**Zero findings are release-blockers.** All are either accepted (F3) or tracked for next sprint / post-launch (F1, F2, F4, F5, F6).

---

## Findings

### F1 — Two competing JWT subsystems (architectural debt)

**Classification:** `tracked-issue` (post-launch)

**Evidence:**

- `app/core/security.py` exports `create_access_token`, `create_refresh_token`,
  `decode_token` which use `jwt_keyring.py`.
- `app/core/token_config.py` exports `create_access_token`, `create_refresh_token`,
  `verify_access_token` which use its own `CURRENT_KEY` / `PREVIOUS_KEY` logic.

Both subsystems:
- Use `jose.jwt` for encoding/decoding.
- Support `kid` header-based key rotation.
- Store revocation state in Redis.

**Risk:** Code reviews could accidentally use the "other" subsystem, leading to
inconsistent token formats or key resolution. For example, a token issued by
`security.py` uses `jwt_keyring.py` keys, while a token issued by
`token_config.py` uses `CURRENT_KEY` env var.

**Recommended fix:** Consolidate to a single canonical JWT module. Deprecate
one of the two subsystems, migrate all callers, and delete the duplicate.

---

### F2 — Access tokens lack `iss` and `aud` claims

**Classification:** `fix-now` (non-blocking for launch, quick win)

**Evidence:**

`app/core/security.py` (lines 51–60):
```python
payload = {
    "sub": subject,
    "role": role,
    "exp": expire,
    "iat": datetime.now(UTC),
    "jti": str(uuid.uuid4()),
    "type": "access",
    **(extra or {}),
}
```

`app/core/token_config.py` (lines 117–127):
```python
claims = {
    "sub": user_id,
    "role": role,
    "jti": str(uuid.uuid4()),
    "iat": now,
    "exp": now + timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES),
    "kid": CURRENT_KID,
}
```

Neither payload includes `iss` (issuer) or `aud` (audience).

**Risk:** Without `iss`, tokens from a staging environment could theoretically
be replayed against production if the signing key is the same (key reuse
across environments is a separate but related risk). Without `aud`, there is no
protection against a token intended for the EduBoost API being presented to
another service that shares the same signing key.

**Recommended fix:** Add `iss` and `aud` to both `create_access_token`
implementations. `iss` should be the APP_BASE_URL or a canonical identifier.
`aud` should be `"eduboost-api"`.

---

### F3 — No token binding (DPoP / `cnf` claim)

**Classification:** `accepted-with-rationale`

**Evidence:** No `cnf` (confirmation) claim or DPoP proof is present in any
token payload.

**Rationale:** Token binding is a P1 hardening item (not P0). For a monolithic
FastAPI deployment with browser and mobile clients, the added complexity of
DPoP may not be justified at launch. The risk of token theft via XSS is
mitigated by the short 15-minute access-token TTL and HTTP-only cookie
policies (see `app/core/cookies.py`).

**Recommended fix:** Track as a Phase 2 hardening task. Implement if the
threat model includes XSS as a realistic attack vector against learner
sessions.

---

### F4 — Refresh-token format inconsistency

**Classification:** `tracked-issue` (post-launch)

**Evidence:**

- `app/core/security.py` `create_refresh_token` produces a **JWT** with
  `type: "refresh"`, `jti`, `family`, etc.
- `app/core/token_config.py` `create_refresh_token` produces **opaque random
  bytes** (`secrets.token_urlsafe(64)`) with a separate `RefreshTokenRecord`.

Both subsystems are used in different parts of the codebase.

**Risk:** The refresh-token lifecycle (store, consume, revoke) in
`app/core/refresh_tokens.py` expects JWT-shaped refresh tokens (it calls
`decode_token` which expects a JWT). If `token_config.py` opaque tokens are
used anywhere in the refresh flow, they will fail at decode time.

**Recommended fix:** Decide on one refresh-token format (recommend opaque
random bytes for refresh tokens — they don't need to be self-describing) and
migrate all callers. The opaque format in `token_config.py` is the better
choice because it prevents client-side inspection of refresh-token metadata.

---

### F5 — Production placeholder guard is strong but could be stricter

**Classification:** `fix-now` (non-blocking, configuration-only)

**Evidence:**

`app/services/jwt_keyring.py` (lines 197–205):
```python
def is_placeholder_secret(secret: str | None) -> bool:
    ...
    return normalised.startswith("change_me") or normalised.startswith("placeholder")
```

`app/services/jwt_keyring.py` (lines 207–215):
```python
def validate_jwt_keyring_environment() -> None:
    ...
    if is_production_environment() and placeholder_kids:
        raise JWTKeyringError(...)
```

The guard catches obvious placeholders but does **not** enforce a minimum key
length. HS256 with a 16-character secret is technically valid but weak.

**Recommended fix:** Add a minimum length check (≥ 32 characters for HS256,
≥ 2048 bits for RS256) to `validate_jwt_keyring_environment()`.

---

### F6 — Encryption key default is a placeholder

**Classification:** `tracked-issue` (post-launch)

**Evidence:**

`app/core/config.py` (line 89):
```python
ENCRYPTION_KEY: str = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="  # dev-only 32-byte base64 placeholder
```

This key is used for PII encryption (`encrypt_pii` / `decrypt_pii` in
`app/core/security.py`). In production it should come from Azure Key Vault
(via `KEY_VAULT_SECRET_NAMES`).

**Risk:** If production deployment accidentally uses this default, all
encrypted PII is trivially decryptable.

**Mitigation in place:** `KEY_VAULT_SECRET_NAMES` maps `ENCRYPTION_KEY` to
`eduboost-encryption-key` in Azure Key Vault. The production environment
should set `AZURE_KEY_VAULT_URL`.

**Recommended fix:** Add a startup check (similar to JWT keyring validation)
that fails if `ENCRYPTION_KEY` is the default placeholder in production.

---

## Strengths (documented for completeness)

1. **Fail-closed on Redis unavailability.** `token_config.py` raises
   `JWTError` when Redis is down, denying all token validation. This is the
   correct security posture.
2. **Single-use refresh-token rotation.** `refresh_tokens.py` deletes the
   consumed refresh token from Redis immediately and uses `hmac.compare_digest`
   for hash comparison (timing-safe).
3. **Family-based reuse detection.** If a refresh token is used twice, the
   entire family is revoked. This prevents replay attacks on refresh tokens.
4. **Emergency global revoke-all.** `emergency_revoke_all()` sets an epoch;
   all tokens issued before that epoch are invalid. This is the correct
   response to a key compromise.
5. **DB fallback for revocation.** `add_persistent_revocation_fallback`
   writes to both Redis (fast) and DB (persistent), ensuring revocation
   survives a Redis restart.
6. **Password hashing.** bcrypt with 12 rounds (`settings.PASSWORD_BCRYPT_ROUNDS`).
7. **PII encryption.** Fernet (AES-128-CBC + HMAC-SHA256) for guardian email
   and other PII fields.

---

## Recommended action plan

| Priority | Task | Effort | Owner |
|---|---|---|---|
| High | Add `iss` and `aud` claims to access tokens (F2) | S | Engineering |
| High | Enforce minimum key length in `validate_jwt_keyring_environment()` (F5) | S | Engineering |
| Medium | Add production placeholder check for `ENCRYPTION_KEY` (F6) | S | Engineering |
| Medium | Consolidate dual JWT subsystems into one canonical module (F1) | M | Engineering |
| Medium | Unify refresh-token format (opaque bytes preferred) (F4) | M | Engineering |
| Low | Evaluate DPoP / token binding for Phase 2 (F3) | L | Security |

---

## AC check

- ✅ Expiry validated: access = 15 min, refresh = 7 days
- ⚠️ Issuer/audience validation: **missing** (F2)
- ✅ Key rotation: `kid`-based with previous-key window
- ✅ Refresh-token revocation: family-based with reuse detection
- ✅ Logout semantics: per-token JTI revocation + per-user revocation + global epoch
- ✅ Keyring validation at startup: placeholder detection + production fail-closed

The review is documented; all findings are triaged. Phase 1 T104 AC is met
(review documented with triaged findings).
