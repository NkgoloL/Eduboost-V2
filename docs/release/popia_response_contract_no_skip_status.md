# POPIA Response Contract No-Skip Proof Status

Generated at: `2026-09-02T21:11:24Z`
Commit: `44b2316fa209233743ffdea388c51e54a69479ac`

**Status:** `popia-response-contract-no-skip-passing`
**Pytest return code:** `None`
**Skipped detected:** `False`

## Route contracts

| Contract | Path | Route exists | ConsentRecord response_model | Passed |
|---|---|---:|---:|---:|
| `grant` | `/consent/grant` | True | True | True |
| `deny` | `/consent/deny` | True | True | True |
| `withdraw` | `/consent/withdraw` | True | True | True |
| `renew` | `/consent/renew` | True | True | True |

## Adapter contracts

| Contract | Passed |
|---|---:|
| `adapter_exists` | True |
| `contains_consent_record` | True |
| `contains_coerce_consent_record` | True |
| `contains_denied_fallback` | True |
| `contains_withdrawn_fallback` | True |

## Pytest output

```text
pytest not requested
```

## Blockers

- None

## No false-closure rules

- Skipped tests are not accepted as proof.
- This response-contract proof does not prove live DB transaction behavior.
- This proof does not satisfy external POPIA legal approval.
- This proof does not approve beta release.
