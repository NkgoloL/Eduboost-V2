# POPIA data-subject-rights workflow

EduBoost supports the POPIA operational baseline for learner and guardian data:

| Right | Endpoint | SLA target | Audit event | Notes |
|---|---|---:|---|---|
| Access/export | `GET /api/v2/popia/data-export/{learner_id}` | 30 days | `data_export.requested` | JSON by default, CSV via `?export_format=csv`. |
| Erasure request | `POST /api/v2/popia/deletion-request/{learner_id}` | 30 days | `erasure.requested` | Soft-deletes immediately, preserves append-only audit records. |
| Erasure cancel | `POST /api/v2/popia/deletion-cancel/{learner_id}` | immediate | `erasure.cancelled` | Available during grace/review period. |
| Correction | `POST /api/v2/popia/correction-request/{learner_id}` | 30 days | `data_subject.correction_requested` | Supports learner `display_name`, `grade`, and `language`. |
| Restriction | `POST /api/v2/popia/restriction-request/{learner_id}` | 30 days | `processing.restricted` | Revokes active consent and blocks optional learner processing. |

## Consent states

Canonical states are defined in `app/core/consent_policy.py` and persisted on `parental_consents.status`:

- `pending`
- `granted`
- `denied`
- `expired`
- `withdrawn`
- `renewal_required`

`granted` and `renewal_required` are active for core educational processing. `pending`, `denied`, `expired`, and `withdrawn` block learner-data processing.

## Audit retention exception

Erasure never removes append-only audit records. Audit payloads must use learner pseudonyms or metadata only; raw PII is rejected by `AuditRepository`.
