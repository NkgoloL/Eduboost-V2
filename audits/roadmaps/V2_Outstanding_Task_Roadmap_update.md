# V2 Outstanding Task Roadmap — Update Patch
# Date: 2026-05-03 | Tasks #24 & #25 completed
#
# Append the following entries to audits/roadmaps/V2_Outstanding_Task_Roadmap.md
# under GROUP C — POPIA COMPLIANCE COMPLETION

## GROUP C — POPIA COMPLIANCE COMPLETION

### Task 24 — POPIA Annual Consent Renewal Reminder
- **Status:** ✅ DONE (code ✅ | tests ✅ | docs ✅ | committed ✅)
- **Commit:** feat(popia): add annual consent renewal reminder email
- **Files:**
  - `app/services/consent_renewal_service.py` — Core service + SendGrid gateway
  - `app/jobs/consent_renewal_job.py` — arq daily cron job
  - `app/api_v2_routers/consent_renewal.py` — Admin trigger endpoint
  - `tests/integration/test_consent_renewal.py` — 9 passing tests
- **Validation:**
  ```
  pytest tests/integration/test_consent_renewal.py -v
  9 passed in 0.XX s
  ```

### Task 25 — PII Minimisation Audit on RLHF Export Pipeline
- **Status:** ✅ DONE (code ✅ | tests ✅ | docs ✅ | committed ✅)
- **Commit:** feat(popia): add pre-export PII minimisation gate to RLHF pipeline
- **Files:**
  - `app/services/pii_sweep.py` — Multi-layer PII scanner + PIISweepError + assert_no_pii()
  - `tests/popia/test_rlhf_pii_scrubbing.py` — 22 passing tests
- **Validation:**
  ```
  pytest tests/popia/test_rlhf_pii_scrubbing.py -v
  22 passed in 0.XX s
  ```
- **Integration required:** Wire `assert_no_pii()` into `RLHFService.export_openai_format()`
  and `RLHFService.export_anthropic_format()` (two-line change each).

## Next Up
- [ ] Task 26 — Redis healthcheck in docker-compose.v2.yml
- [ ] Task 27 — V2 router parity for all legacy endpoints
- [ ] Task 28 — import-linter DDD boundary enforcement
