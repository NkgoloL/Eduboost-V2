# POPIA Data-Rights Consent Boundary

## Active Consent Gate

```text
GET /api/v2/popia/data-export/{learner_id}
```

The export endpoint discloses learner data and therefore requires:

1. learner read authorization
2. active POPIA consent

## Data-Subject Rights Workflows

These routes are not blocked by active consent.

The following routes remain object-authorized but are **not** blocked by active
consent, because they are data-subject rights workflows:

```text
POST /api/v2/popia/deletion-request/{learner_id}
POST /api/v2/popia/deletion-cancel/{learner_id}
POST /api/v2/popia/correction-request/{learner_id}
POST /api/v2/popia/restriction-request/{learner_id}
GET /api/v2/popia/deletion-status/{learner_id}
```

Blocking these routes on active consent could prevent a guardian from exercising
rights after consent has been withdrawn or expired.

## Verification

```bash
pytest -c pytest.ini tests/unit/test_popia_data_rights_consent_boundary.py -q --no-cov
```
