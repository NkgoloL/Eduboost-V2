# ADR-022: Audit and Consent Table Ownership Options

## Status

Proposed

## Context

EduBoost V2 backend consolidation diagnostics are complete. Audit and consent call sites are inventoried, compatibility adapters exist, and terminal guards prevent destructive implementation.

The next phase requires explicit ownership decisions before schema consolidation or deletion.

## Option A — Conservative current-state model

- `audit_events` is canonical for new append-only audit writes.
- `audit_logs` is retained as historical/legacy data until legal/security approves migration or archival.
- `consent_records` and `parental_consents` remain separate until semantics are proven.
- Runtime implementation uses adapters/normalizers only.

**Default recommendation:** Accept as the first implementation posture.

## Option B — Audit canonicalization only

- `audit_events` becomes canonical for new writes.
- Legacy audit call sites migrate through `AuditRepositoryCompatAdapter`.
- Historical `audit_logs` remains read-only and retained.
- Consent persistence remains unchanged.

**Use when:** audit consolidation is needed before consent table decisions are complete.

## Option C — Consent runtime repair only

- No consent table merge.
- Constructor/signature compatibility is repaired.
- Active-consent runtime owner is documented.
- Consent audit events use canonical audit normalization.

**Use when:** runtime reliability is needed before data model decisions.

## Option D — Full table consolidation

- Merge or migrate audit/consent tables.
- Requires migration plan, data-retention approval, disposable DB proof, rollback plan, and release-owner signoff.

**Default status:** Not approved.

## Decision rules

- Do not discard audit or consent history without legal/security approval.
- Do not use `alembic stamp head` as a blind repair.
- Do not delete legacy repositories until call sites are migrated and full-suite evidence is green.
- Prefer adapter-backed runtime migration before schema mutation.
