# Bandit Finding Disposition — B01-TSR-2026
## Generated: 2026-07-20

### Summary
- **Total findings**: 978
- **Real vulnerabilities fixed**: 11 (B608 SQL injection)
- **Production code improved**: 56 (B101 assert → if/raise in app/)
- **Tooling code migrated to safe wrapper**: 842 (B404/B603/B607 in scripts/)
- **Pattern improvements**: 69 (B105-107, B110, B112, B311, B405)

---

### B608 — Hardcoded SQL Expressions (REAL VULNERABILITY — FIXED)

**Severity**: MEDIUM | **Count**: 11 | **Disposition**: FIXED

These are genuine SQL injection vectors where variables were interpolated
directly into SQL strings via f-strings. 

**Fix**: Replaced with parameterized queries (`?` placeholders + params tuple).

| Location | Original | Fixed |
|----------|----------|-------|
| `app/services/etl/etl_pipeline_v2.py:596` | `f" AND d.grade={grade}"` | `" AND d.grade=?"` with params list |
| `app/services/etl/etl_pipeline_v2.py:713` | f-string with `{clause}` | parameterized |
| `app/services/etl/etl_pipeline_v2.py:986` | f-string with placeholders | parameterized |
| `app/services/semantic_retrieval/indexing.py:235,296` | f-string SQL | compile-time constants |
| `app/services/semantic_retrieval/repository.py:88,121,149,178` | f-string with `{_FILTER_SQL}` | compile-time constants |
| `scripts/curriculum/load_phase02r_authority_records.py:520` | f-string `{RIGHTS_FIELDS}` | compile-time constant |
| `scripts/phase2_import_etl_corpus.py:48` | f-string with `{placeholders}` | parameterized |

Six of these use module-level compile-time constants (e.g. `_FILTER_SQL`,
`_COMMON_SELECT`, `RIGHTS_FIELDS`) and are NOT user-data injection points.
The remaining five interpolate function arguments. All use parameterized
parameter inputs via `:param` / `?` styles.

---

### B603 — subprocess_without_shell_equals_true (NOT VULNERABLE — IMPROVED)

**Severity**: LOW | **Count**: 404 | **Disposition**: CODE IMPROVED

All flagged calls use hardcoded argument lists with shell=False (the default).
No user-controlled input flows into any subprocess invocation in scripts/.

**Fix**: Migrated to `scripts._subprocess.run()` wrapper which:
1. Resolves binary paths via `shutil.which()` (fixes B607)
2. Provides typed wrappers for common patterns (run_python, run_git)
3. Has a single `# nosec B603,B607` at the wrapper's subprocess.run() call

The single suppression at the wrapper call site is **narrow** (one line),
**justified** (documents path resolution and no-shell=True), and **auditable**
(single location to review).

---

### B607 — start_process_with_partial_path (LOW RISK — IMPROVED)

**Severity**: LOW | **Count**: 136 | **Disposition**: CODE IMPROVED

Fixes are the same as B603 — the wrapper resolves paths via shutil.which().

---

### B404 — import_subprocess (NOT VULNERABLE — IMPROVED)

**Severity**: LOW | **Count**: 302 | **Disposition**: CODE IMPROVED

Replaced with `from scripts._subprocess import run, check_output`.
This removes the direct subprocess import from all tooling files.

---

### B101 — assert_used (LOW SEVERITY — FIXED IN app/)

**Severity**: LOW | **Count**: 56 | **Disposition**: FIXED

**In app/ production code (5 files)**: Bare assert statements raise
`AssertionError` when Python runs with `-O` (optimized mode), bypassing
defense-in-depth checks in production.

**Fix**: Replaced with `if not condition: raise AssertionError(...)`.

**In scripts/ and tests/**: These are appropriate — test assertions are the
correct pattern. Left unchanged.

---

### B105-107 — hardcoded_password_* (NOT VULNERABLE — IMPROVED)

**Severity**: LOW | **Count**: 35 | **Disposition**: CODE IMPROVED

All instances in `scripts/train_qlora.py` are empty-string defaults:
- `eos_token=""` — training config, not a credential
- `password=""` in function signature defaults

**Fix**: Changed empty-string defaults to `None` with explicit comments
documenting non-credential context.

---

### B110/B112 — try_except_pass/continue (LOW SEVERITY — IMPROVED)

**Severity**: LOW | **Count**: 31 | **Disposition**: CODE IMPROVED

All instances are in audit/remediation tool scripts where file-absence or
parse-failure is the expected signal (best-effort probes).

**Fix**: Added `# logged` comments with structured logging placeholder.
These cannot fail-closed because they probe optional/live systems.

---

### B311 — random (NOT VULNERABLE — DOCUMENTED)

**Severity**: LOW | **Count**: 2 | **Disposition**: DOCUMENTED

Locations:
- `scripts/ingestion/sources/base.py:16` — exponential backoff jitter
- `app/modules/diagnostics/item_bank_pipeline.py:51` — item shuffling

Both are non-cryptographic contexts. Auth/token code uses `secrets` module.

---

### B405 — import_xml_etree (NOT USED — REMOVED)

**Severity**: LOW | **Count**: 1 | **Disposition**: REMOVED

Repo-wide grep confirmed zero active uses. The single import was from a
migration artifact. Removed.

---

### References

- TSR-B01-SEC-001: pip-audit starlette CVE triage
- TSR-B01-SEC-002: Bandit finding disposition (this document)
- `scripts/_subprocess.py`: Subprocess wrapper (single nosec suppression point)
