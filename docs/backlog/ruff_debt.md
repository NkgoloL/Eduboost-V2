# Ruff Debt Inventory

**Date:** 2026-06-09
**Baseline:** Phase 1.2 completion; correctness gates (E9, F63, F7, F82, F821) all pass

**Current checkpoint:** 2026-06-14 traceability closeout; correctness gates still pass and non-blocking debt is now 650 findings by `ruff check app tests scripts --statistics`.

## Summary

As of 2026-06-09, the codebase contains approximately **1,000 Ruff findings** beyond the release-blocking correctness checks. These are organized by severity category below. Correctness-blocking errors (E9, F63, F7, F82, F821) are **zero** and gated in CI.

As of the 2026-06-14 refresh, remaining non-blocking findings are:

| Code | Count | Description |
|------|------:|-------------|
| E402 | 402 | Module level import not at top of file |
| E701 | 137 | Multiple statements on one line (colon) |
| E702 | 94 | Multiple statements on one line (semicolon) |
| E741 | 10 | Ambiguous variable name |
| E712 | 7 | Equality comparison to false |

The 2026-06-14 pass removed the remaining `F601` duplicate dictionary-key
finding in `scripts/sync_git_to_redmine.py`. The original 2026-06-09 baseline
remains below for historical comparison.

## Release-Blocking Correctness Gate ✅

Passes CI and local validation:
- `E9`: Syntax errors → **0 findings**
- `F63`: Invalid type in format string → **0 findings**
- `F7`: Syntax errors in type comments → **0 findings**
- `F82`: Undefined variable in `__all__` → **0 findings**
- `F821`: Undefined name → **0 findings**

## Non-Blocking Debt by Category

### High Priority (Correctness or Semantic Issues)

| Code | Count | Severity | Description | Remediation |
|------|-------|----------|-------------|-------------|
| F401 | 306 | High | Unused import | Remove or use |
| F841 | 33 | High | Local variable never used | Remove or suppress |
| F811 | 30 | High | Redefined while unused | Rename or consolidate |
| F541 | 6 | Medium | F-string without placeholders | Remove or add content |
| F601 | 1 | Medium | Invalid f-string expression | Fix expression syntax |

**Action:** Fix all F-series findings in Phase 11 (Technical Debt Burn-Down) or as part of periodic code hygiene cycles.

### Medium Priority (Style and Conventions)

| Code | Count | Severity | Description | Remediation |
|------|-------|----------|-------------|-------------|
| E402 | 414 | Medium | Module level import not at top | Reorganize imports |
| E701 | 138 | Medium | Multiple statements on one line (colon) | Split lines |
| E702 | 94 | Medium | Multiple statements on one line (semicolon) | Split lines |
| E741 | 10 | Low | Ambiguous variable name (l, O, I) | Rename |
| E401 | 9 | Low | Multiple imports on one line | Split imports |

**Action:** Address as part of periodic style/hygiene passes. E402 is particularly prevalent and warrants a dedicated refactor pass to move imports to module tops.

### Low Priority (Edge Cases)

| Code | Count | Severity | Description |
|------|-------|----------|-------------|
| E712 | 3 | Low | Comparison to True/False with == | Use `is` |
| E711 | 1 | Low | Comparison to None with == | Use `is` |
| E713 | 1 | Low | Comparison to True with `in` | Restructure |

**Action:** Fix opportunistically during nearby refactors.

---

## Recommended Burn-Down Strategy

### Phase 11 (Technical Debt) Tasks

1. **F401 Unused Imports (306):** Automated removal via `ruff check app tests scripts --select F401 --fix`.
2. **E402 Module Import Order (414):** Semi-automated; requires manual review due to context sensitivity.
3. **E701/E702 Multi-statement lines (232):** Automated splitting, but verify readability.
4. **F841 Unused local variables (33):** Case-by-case review; some may be intentional test setup.
5. **F811 Redefined names (30):** Review for true conflicts vs. intentional overrides.
6. **E741/E712/E711 (15 total):** Opportunistic fixes during other edits.

### CI Enforcement Strategy

- **Immediate (v1.0-rc phase):** Block only on `E9,F63,F7,F82,F821` (current).
- **Beta phase:** Consider adding `F401` and `F841` to the blocking gate.
- **Post-launch:** Progressively add E402, E701, E702 to CI gates as debt is paid down.

### Evidence

- **Baseline:** `ruff check app tests scripts --output-format=json` captured 2026-06-09.
- **CI gate:** Verified passing in GitHub Actions.
- **Automation:** Ruff supports `--fix` for many categories; automated runs can be added to CI or pre-commit hooks.

---

## File-by-File Hotspots (Top 20)

Run this command to identify files with highest debt concentration:

```bash
ruff check app tests scripts --output-format=json | \
  python3 -c "import json,sys; d=json.load(sys.stdin); \
  files={}; \
  [(files.setdefault(r['filename'], []).append(r['code'])) for r in d]; \
  print('\n'.join(f\"{f}: {len(files[f])} findings\" for f in sorted(files, key=lambda x: len(files[x]), reverse=True)[:20]))"
```

---

## References

- Ruff documentation: https://docs.astral.sh/ruff/rules/
- Phase 11 (Technical Debt Burn-Down) in RoadMap.md
- CI gate: `.github/workflows/ci-cd.yml`
