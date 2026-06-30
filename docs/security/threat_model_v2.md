---
title: "EduBoost V2 Threat Model"
status: active
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, app/security]
---

# EduBoost V2 Threat Model

**Date**: 2026-06-12  
**Version**: 1.0  
**Scope**: EduBoost V2 API, Auth, Data, and LLM surfaces  
**Methodology**: STRIDE + Attack Tree

---

## 1. Executive Summary

This threat model covers the V2 architecture surfaces: authentication, session management, API endpoints, data handling, infrastructure, and LLM integration. The model identifies key attack vectors and existing mitigations, providing a foundation for security testing and hardening.

---

## 2. System Overview

### 2.1 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CDN / WAF                                 │
│                     (Azure Front Door)                          │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API Gateway (FastAPI)                       │
│                 https://api.eduboost.co.za                      │
└─────────────────────────────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Auth Layer   │    │  Service Layer  │    │  LLM Gateway    │
│ (JWT + Redis) │    │ (Business Logic)│    │ (OpenAI/Anthropic) │
└───────────────┘    └─────────────────┘    └─────────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL  │    │    Redis        │    │  POPIA Sweep    │
│  (PII Store)  │    │  (Sessions)     │    │ (PII Scrubber)  │
└───────────────┘    └─────────────────┘    └─────────────────┘
```

### 2.2 Key Components

| Component | Technology | Trust Boundary |
|-----------|------------|-----------------|
| API | FastAPI (Python 3.12) | Public → Internal |
| Auth | JWT + Redis | Public → Token validation |
| Database | PostgreSQL (pgcrypto) | Internal |
| Cache | Redis | Internal |
| LLM Gateway | Python async | Internal → External |
| Key Vault | Azure Key Vault | Internal → Secret store |

---

## 3. Trust Boundaries

| Boundary | Description | Ingress Points |
|----------|-------------|-----------------|
| B1 | Internet → API | `/api/v2/*`, `/health`, `/docs` |
| B2 | API → Auth Service | Dependency injection |
| B3 | API → Database | SQLAlchemy async sessions |
| B4 | API → Redis | `redis.asyncio` |
| B5 | API → LLM Provider | HTTPS to OpenAI/Anthropic |
| B6 | API → Azure KV | HTTPS to Key Vault |

---

## 4. Threat Surface Analysis (STRIDE)

### 4.1 Authentication Surfaces

| Threat | Description | Existing Mitigation |
|--------|-------------|---------------------|
| **S** - Token Forgery | Attacker forges JWT to impersonate users | RS256 signing, short expiry (15min) |
| **T** - Token Reuse | Stolen refresh token reused across sessions | Rotation on use, single-use tokens |
| **R** - Session Hijacking | Redis session stolen/overwritten | HttpOnly secure cookies, IP binding |
| **I** - Credential Stuffing | Brute-force login attempts | Rate limiting (10 req/min), account lockout |

**Additional Controls Needed**:
- [ ] Token binding to device fingerprint
- [ ] Anomaly detection for unusual refresh patterns

### 4.2 Session Surfaces

| Threat | Description | Existing Mitigation |
|--------|-------------|---------------------|
| **S** - Session Poisoning | Manipulate Redis session data | JSON serialization, schema validation |
| **T** - Session Persistence | Extend session beyond expiry | Absolute timeout (24h), sliding window |
| **R** - Unauthorized Session Access | Cross-user session read | Redis ACLs, namespace isolation |
| **E** - Denial of Service | Exhaust Redis connections | Connection pooling, fail-closed |

**Existing Controls**:
- `app/core/session.py`: In-memory session with Redis fallback
- Token revocation on logout (`app/core/token_revocation.py`)

### 4.3 API Surfaces

| Threat | Description | Existing Mitigation |
|--------|-------------|---------------------|
| **I** - Broken Access Control | Access other users' data | Ownership checks in every route |
| **I** - IDOR | Manipulate resource IDs | UUIDs, authorization decorators |
| **T** - Rate Limiting Abuse | Bypass rate limits | Per-IP + per-user limits |
| **D** - API DoS | Exhaust server resources | Connection limits, timeouts |

**Protected Endpoints**:
- `/api/v2/learners/{id}` → `require_learner_read_for_current_user`
- `/api/v2/consent/*` → `require_active_consent_for_current_user`
- `/api/v2/popia/*` → Authorization via service layer

**Gaps Identified**:
- [ ] Missing rate limiting on `/auth/refresh`
- [ ] No API versioning for security patches

### 4.4 Data Surfaces

| Threat | Description | Existing Mitigation |
|--------|-------------|---------------------|
| **I** - PII Exposure | Read plaintext PII | pgcrypto encryption-at-rest |
| **I** - Data Exfiltration | Bulk export of learner data | Consent gate on `/popia/export` |
| **I** - Pseudonym Bypass | Map pseudonym to real identity | Separate pseudonym_id for LLM |
| **T** - Data Tampering | Modify audit records | Immutable audit_events table |

**POPIA Compliance**:
- Learner ID → Pseudonym ID mapping for LLM calls
- `app/services/popia_sweep.py`: PII scrubbing before LLM
- 30-day erasure SLA with grace period

### 4.5 Infrastructure Surfaces

| Threat | Description | Existing Mitigation |
|--------|-------------|---------------------|
| **S** - Container Escape | Break out of container | Non-root user (appuser), read-only root |
| **I** - Secrets Leak | Expose .env or keys | Azure Key Vault, no .env in repo |
| **T** - Network Egress | Exfiltrate data via DNS | NSG rules, WAF blocking |
| **E** - Crypto Key Theft | Steal DB encryption keys | Azure KV with HSM |

**Existing Controls**:
- Docker: non-root, read-only filesystem
- Azure: Private endpoints, VNet isolation
- `.env.example`: Template only, no secrets

### 4.6 LLM Surfaces

| Threat | Description | Existing Mitigation |
|--------|-------------|---------------------|
| **I** - Prompt Injection | Malicious input bypasses guardrails | `app/core/judiciary.py`: content screening |
| **I** - PII Leakage | Model outputs learner PII | `popia_sweep.py` pre-scrub |
| **T** - Model DoS | Exhaust LLM quota | Budget guardrails, caching |
| **S** - Toxic Output | Model generates harmful content | Judiciary gate (verdict="REJECTED") |

**Judiciary Gate Flow**:
```
User Prompt → popia_sweep (scrub PII) → LLM → JudiciaryServiceV2.check() → Safe?
```

**Gaps**:
- [ ] No input token limit enforcement
- [ ] Output not validated for PII re-appearance

---

## 5. Threat Matrix

| ID | Surface | Threat | Likelihood | Impact | Mitigation Status |
|----|---------|--------|------------|--------|-------------------|
| T01 | Auth | JWT forgery | Low | Critical | ✅ Mitigated |
| T02 | Auth | Token replay | Medium | High | ✅ Mitigated |
| T03 | Session | Redis injection | Low | High | ✅ Mitigated |
| T04 | API | IDOR | Medium | Critical | ✅ Mitigated |
| T05 | API | Rate limit bypass | Medium | Medium | ⚠️ Partial |
| T06 | Data | PII at rest exposure | Low | Critical | ✅ Mitigated |
| T07 | Data | Bulk export leak | Low | Critical | ✅ Mitigated |
| T08 | Infra | Secrets in logs | Low | High | ✅ Mitigated |
| T09 | LLM | Prompt injection | High | High | ✅ Mitigated |
| T10 | LLM | PII in output | Medium | Critical | ⚠️ Partial |

---

## 6. Recommended Security Controls

### High Priority

1. **T05 - Rate Limiting Enhancement**
   - Add rate limit to `/auth/refresh` endpoint
   - Implement per-device fingerprint limits

2. **T10 - LLM Output PII Validation**
   - Add post-processing PII scan on LLM outputs
   - Block output if PII detected

### Medium Priority

3. **Token Binding**
   - Bind JWT to device fingerprint
   - Detect session hijacking via fingerprint mismatch

4. **Input Token Limits**
   - Enforce max input tokens on LLM prompts
   - Truncate long prompts with warning

---

## 7. Security Testing Checklist

- [ ] JWT forgery attempt (modify payload, check signature validation)
- [ ] Token replay across sessions
- [ ] IDOR on learner endpoints (access other learner's data)
- [ ] Rate limit bypass attempts
- [ ] Prompt injection on lesson generation
- [ ] PII leakage in LLM outputs
- [ ] Consent gate bypass attempts
- [ ] Bulk data export authorization

---

## 8. References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [STRIDE Methodology](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-stride)
- [POPIA Act](https://popia.co.za/)
- `app/core/auth.py` - JWT handling
- `app/core/judiciary.py` - Content screening
- `app/services/popia_sweep.py` - PII scrubbing