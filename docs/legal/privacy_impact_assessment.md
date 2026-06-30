# Privacy Impact Assessment (DPIA-style)

**Status:** Draft — Pending legal review  
**Date:** 2026-06-12  
**Phase:** 8 (B.8)  
**Owner:** Information Officer / Engineering  
**POPIA reference:** Section 71 (privacy impact assessment obligation)

---

## 1. Overview

EduBoost SA is an AI-powered adaptive learning platform for South African learners (Grades R–7). It collects, processes, and stores personal information about **children (minors)** and their **parents/guardians**. Given the involvement of minors and AI-generated content, a privacy impact assessment is required.

---

## 2. Data Processing Activities

| Activity | Data Subjects | Personal Information | Lawful Basis |
|---|---|---|---|
| Guardian account registration | Guardian (adult) | Email, password hash, name | Contract |
| Learner profile creation | Learner (minor) | Name, grade, language, learning style | Parental consent |
| Diagnostic assessment | Learner (minor) | Answer patterns, knowledge gaps, IRT theta | Parental consent |
| AI lesson generation | Learner (minor) | Pseudonymised context only | Parental consent |
| Learning progress tracking | Learner (minor) | XP, streaks, mastery scores | Parental consent |
| Parental reporting | Guardian (adult) | Receives learner progress summary | Contract |
| Data export (POPIA §24) | Guardian + Learner | Full learner data bundle | Legal obligation |
| Data erasure (POPIA §24) | Guardian + Learner | Full erasure with audit retention | Legal obligation |
| Audit logging | Guardian + Learner | Action metadata (no PII in fields) | Legal obligation |
| Analytics | Guardian (adult) | Pseudonymised events | Legitimate interest + opt-out |

---

## 3. Special Categories

Learner data relates to **children under 18**, which requires heightened protection under POPIA section 34:

- Parental/guardian consent is **mandatory** before any processing
- Consent is versioned to a specific privacy notice
- Consent is enforced at the API layer via `ConsentGate` middleware
- Erasure and export rights are available to the responsible party (guardian)

No special categories (health, biometric, religious, political data) are processed beyond educational performance data.

---

## 4. Risk Assessment

| Risk | Likelihood | Impact | Mitigation | Residual Risk |
|---|---|---|---|---|
| Minor's data exposed to unauthorised parties | Low | High | Role-based access, consent gate, object-level authorization | Low |
| LLM provider receives PII | Low | High | Pseudonymisation enforced in prompt construction; tested by `test_ai_prompt_secret_leakage.py` | Low |
| Consent bypass by guardian | Low | High | Every learner-data route enforces active consent check | Low |
| Audit trail tampered | Very Low | High | Chained SHA-256 hash + HMAC; append-only table; verification script | Very Low |
| Guardian email exposed in data breach | Medium | High | Email encrypted at rest (AES-256); hashed for lookup | Low |
| Unauthorised erasure of audit records | Very Low | High | DB-level: app role has no DELETE on audit_events; trigger enforcement | Very Low |
| Teacher accessing unassigned learners | Low | Medium | Object-level authorization: `can_view_learner` checks assigned_learner_ids | Very Low |
| Support operator accessing PII | Low | Medium | Support role returns meta only; PII fields gated at repository layer | Low |
| Retention period exceeded | Medium | Medium | Retention policy defined; automated expiry for Redis/logs; POPIA service for erasure | Low |
| Cross-border data transfer (LLM providers) | Medium | Medium | SCCs pending; data minimisation enforced | Medium — DPAs pending |

---

## 5. Data Subject Rights Compliance

| Right | Implementation | Status |
|---|---|---|
| Right of access (§23) | `/api/v2/popia/exports` — JSON + CSV export | ✅ Implemented |
| Right of correction (§24) | `/api/v2/popia/correction` | ✅ Implemented |
| Right of deletion/erasure (§24) | `/api/v2/popia/erasure` with legal-hold checks | ✅ Implemented |
| Right to restrict processing (§11) | `/api/v2/popia/restriction` | ✅ Implemented |
| Right to withdraw consent (§11) | `/api/v2/popia/consent/withdraw` | ✅ Implemented |
| Right to object to processing (§11) | Handled via processing restriction + erasure | ✅ Implemented |
| Right to be informed (§18) | Privacy notice versioning in consent system | ✅ Implemented |
| Notification of security compromise (§22) | SECURITY.md; incident response runbook | ⚠️ Runbook pending |

---

## 6. Information Officer

**Name:** [To be designated — POPIA §55]  
**Email:** privacy@eduboost.co.za  
**Registration:** [Registration with Information Regulator pending — POPIA §57]

---

## 7. Mitigations In Place

### Technical Controls
- ✅ Email encrypted at rest (AES-256 via Fernet)
- ✅ Passwords hashed (bcrypt, cost factor 12)
- ✅ Consent gate enforced on all learner-data routes
- ✅ Object-level authorization on every data access path
- ✅ Append-only audit log with hash chain and HMAC
- ✅ PII stripped from LLM prompts (pseudonymisation)
- ✅ JWT access tokens short-lived (15 min); refresh token rotation
- ✅ HttpOnly, Secure, SameSite cookies for session tokens
- ✅ Nonce-based CSP in production (no unsafe-inline)
- ✅ HSTS in production

### Organisational Controls
- ⚠️ DPAs with LLM providers pending
- ⚠️ Information Regulator registration pending
- ⚠️ Staff privacy training pending
- ✅ SECURITY.md security disclosure policy in place
- ✅ Data inventory documented
- ✅ Data retention policy documented
- ✅ Subprocessor register documented

---

## 8. Residual Risks Requiring Further Action

| Risk | Action Required | Owner | Priority |
|---|---|---|---|
| Cross-border transfer to LLM providers | Sign DPAs with Groq, Anthropic | Legal | P0 before public beta |
| Information Regulator registration | Register as responsible party | Legal | P0 before public beta |
| Staff privacy training | Run POPIA awareness training | HR | P1 |
| Penetration test | Commission external pen-test | Security | P1 before public launch |
| Legal hold operationalisation | Legal review of `ErasureRequest.legal_hold` field | Legal | P1 |

---

## 9. Sign-off

| Role | Name | Date | Status |
|---|---|---|---|
| Information Officer | [Pending designation] | — | ⚠️ Pending |
| Legal Counsel | [Pending] | — | ⚠️ Pending legal review |
| Engineering Lead | — | 2026-06-12 | ✅ Technical review complete |

---

## References

- `docs/data_inventory.md`
- `docs/data_retention_policy.md`
- `docs/subprocessor_register.md`
- `docs/POPIA_COMPLIANCE.md`
- `docs/popia_erasure.md`
- `SECURITY.md`
- Phase 8 execution plan §B.8
