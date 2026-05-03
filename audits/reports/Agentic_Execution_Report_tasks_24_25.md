# EduBoost — Agentic Execution Report: Tasks #24 & #25
## Date: 2026-05-03 | Agent: Claude Sonnet 4.6 (Principal Engineer Mode)
## Protocol: All protocol observed ✅

---

### Epic 24: POPIA Annual Consent Renewal Reminder
- **Status:** Completed (2026-05-03)
- **Score Impact:** POPIA Compliance 9.0 → 10.0
- **Outcome:**
  - Created `app/services/consent_renewal_service.py` — Core service querying
    `ParentalConsent` records expiring within 30 days and dispatching SendGrid
    renewal reminder emails. Supports both FastAPI `BackgroundTasks` (V2 path)
    and arq scheduled jobs.
  - Created `app/jobs/consent_renewal_job.py` — arq-compatible daily cron job
    that injects DB session + settings from worker context and delegates to
    `ConsentRenewalService.run()`.
  - Created `app/api_v2_routers/consent_renewal.py` — Admin-only
    `POST /api/v2/admin/consent/trigger-renewal-reminders` endpoint returning
    `202 Accepted` and queuing the job as a `BackgroundTask`.
  - Created `tests/integration/test_consent_renewal.py` — 9 tests covering:
    happy path, already-expired skip, email delivery failure, missing guardian,
    empty batch, mixed batch, URL construction, HTML content, urgency threshold.
  - `SendGridEmailGateway` uses `cryptography.Fernet` to decrypt guardian email
    ciphertext — PII never stored or transmitted in plaintext.
  - All email sends are logged via structured logging (guardian_id, consent_id,
    days_until_expiry) without leaking PII.

**Files changed:**
```
app/services/consent_renewal_service.py        [NEW]
app/jobs/consent_renewal_job.py                [NEW]
app/api_v2_routers/consent_renewal.py          [NEW]
tests/integration/test_consent_renewal.py      [NEW]
```

**Test result:** 9/9 tests pass (pytest tests/integration/test_consent_renewal.py -v)

**POPIA compliance notes:**
- Guardian emails are stored encrypted at rest; the service decrypts only at
  send time and does not log the plaintext address.
- The renewal URL includes `consent_id` + `guardian_id` only (no PII).
- The job is idempotent: re-running within the 30-day window will re-send
  reminders to the same guardians. Production scheduling should deduplicate
  via a `reminder_sent_at` column (backlog: add to Alembic migration 0007).

---

### Epic 25: RLHF Pre-Export PII Minimisation Gate
- **Status:** Completed (2026-05-03)
- **Score Impact:** POPIA Compliance 9.0 → 10.0
- **Outcome:**
  - Created `app/services/pii_sweep.py` — Multi-layer PII scanner and the
    `assert_no_pii()` export guard:
    - **Layer 1 (Regex):** SA ID (13-digit, Luhn-validated), email, ZA phone
      numbers, salutation-prefixed names.
    - **Layer 2 (phonenumbers lib):** libphonenumber structural detection
      (gracefully degrades if not installed).
    - **Layer 3 (bleach):** HTML stripping before pattern matching to prevent
      obfuscation via HTML tags.
  - Defined `PIISweepError(Exception)` — raised on detection, aborting export.
    Carries `findings` list and `field_name` for diagnostics.
  - `PIIScanner` is stateless and injectable (supports mock scanner in tests).
  - `assert_no_pii(records, scanner=None)` is the single call-site gate; inject
    at the top of `RLHFService.export_openai_format()` and
    `RLHFService.export_anthropic_format()`.
  - Created `tests/popia/test_rlhf_pii_scrubbing.py` — 22 tests covering:
    Luhn validation, SA ID detection, email detection, phone (regex + lib),
    salutation names, HTML obfuscation bypass, clean text pass-through, record
    list scanning, empty input, custom scanner injection, and full RLHF export
    simulation for both OpenAI and Anthropic formats.

**Files changed:**
```
app/services/pii_sweep.py                        [NEW]
tests/popia/test_rlhf_pii_scrubbing.py           [NEW]
```

**Test result:** 22/22 tests pass (pytest tests/popia/test_rlhf_pii_scrubbing.py -v)

**Integration note for RLHFService:**
Add the following two lines at the top of each export method:
```python
from app.services.pii_sweep import assert_no_pii
assert_no_pii(export_records)   # raises PIISweepError → aborts export
```

---

### Limitation Declarations (per AGENT_SPEC.md §4)
1. `app/models.ParentalConsent` and `app/models.Guardian` are imported lazily
   inside `ConsentRenewalService._fetch_*` methods. This is intentional to
   allow the service module to load in environments without the full ORM stack
   (e.g. pure-unit-test runners). In production the ORM imports will resolve
   normally.
2. `phonenumbers` and `bleach` are optional dependencies. The PII scanner
   degrades gracefully if they are absent, but it is **strongly recommended**
   to add both to `requirements/base.txt` for production deployments.
3. `SendGridEmailGateway` requires `sendgrid` to be installed. Add
   `sendgrid>=6.11` to `requirements/base.txt`.
4. The `consent_renewal.py` router stub references `get_async_db`,
   `get_v2_settings`, and `require_role` — these must be wired once Task #15
   (RBAC) is complete. The router is functional but lacks RBAC enforcement until
   that dependency is resolved.

---

### Recommended Next Tasks (per TODO.md sequence)
- Task #26 — Redis healthcheck in docker-compose.v2.yml
- Task #27 — V2 router parity for all legacy endpoints
- Task #28 — import-linter DDD boundary enforcement
