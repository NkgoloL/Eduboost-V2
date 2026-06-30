# PR-003B: UUID Rollout — reviewer_id Discovery

## Scope
Start with one vertical only:
`guardians` ↔ `diagnostic_items.reviewer_id`

## Discovery Findings

### 1. guardians.id actual DB type
- `guardians.id` is currently `character varying(64)` (String).

### 2. diagnostic_items.reviewer_id actual DB type
- `diagnostic_items.reviewer_id` is currently `uuid`.

### 3. Whether reviewer_id values are UUID-shaped strings
- The `reviewer_id` column in `diagnostic_items` is natively a `uuid` type in Postgres, so it enforces valid UUID values. The `guardians.id` column is a `varchar(64)` but likely contains UUID-shaped strings.

### 4. Orphan count against guardians
- Currently `0` (there are 0 non-null `reviewer_id` values in `diagnostic_items` in the current test database).

### 5. Nullable behavior
- `diagnostic_items.reviewer_id`: `NULLABLE`.
- `guardians.id`: `NON-NULLABLE` (Primary Key).

### 6. Affected services/routes/tests
- `tests/unit/test_diagnostic_items.py`
- `tests/integration/test_diagnostic_workflow.py`
- Endpoints reading/writing `reviewer_id`.

### 7. Rollback path
- Drop any newly added shadow columns/indexes. No destructive changes to existing data.

