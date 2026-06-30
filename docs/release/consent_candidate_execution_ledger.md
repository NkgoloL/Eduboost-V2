# Consent Candidate Execution Ledger

**Status:** consent runtime execution harness active

## Executable candidates

| Candidate | Harness | Destructive? |
|---|---|---|
| consent.granted | normalized audit-compatible payload | no |
| consent.status.read | normalized audit-compatible payload | no |

## Boundary

The harness proves consent operation normalization. It does not merge `consent_records` and `parental_consents`.
