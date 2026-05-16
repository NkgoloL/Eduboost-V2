# Consent Runtime Compatibility Slice 001

**Status:** non-destructive implementation scaffold

## Scope

This slice introduces a consent runtime compatibility seam without merging consent tables or changing existing consent route behavior.

## Invariants

- `ConsentService` and `POPIADataRightsService` constructor surfaces are probed, not rewritten.
- Consent runtime operations normalize into audit-compatible event payloads.
- Read/write operation classification remains explicit in metadata.
- No `consent_records` / `parental_consents` merge is performed.

## Verification

```bash
make consent-runtime-compatibility-slice-check
```
