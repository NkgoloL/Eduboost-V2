# Phase 0 — Domain E — Hardening Intake & Repository Hygiene Evidence

**Branch:** `remediation/phase0-phase1`
**Date:** 2026-05-27
**Scope:** T040, T041, T042, T050, T060, T061, T070, T071

---

## T040 — Triage all untracked hardening assets

**Status:** Done by exclusion. See `audits/production_hardening/intake_triage_20260527.md`.

Working tree on `origin/master` is clean with respect to hardening
surfaces. Audit's "untracked hardening assets" do not exist on master and
are classified `discard` by default. Detailed reasoning in the linked
triage document.

## T041 — Commit validated intake evidence

**Status:** Not applicable (no `stage-now` assets — see T040).

## T042 — Stage or defer hardening assets by class

**Status:** Done. `git status --short` after Phase 0 commits shows only
Phase 0 remediation work being staged through normal PR review; no
unclassified hardening artifacts remain.

---

## T050 — Content filter safety decision

**Status:** ⚠️ **OPEN** — awaiting Security/Safety owner sign-off.

Important finding during this work: the audit's premise that
`app/core/content_filter.py` exists locally is **false** for
`origin/master`. There is no content filter implementation in version
control:

```text
$ find . -path ./node_modules -prune -o -path ./.venv -prune \
       -o -name "content_filter*" -print
(no output)
$ grep -rln "content_filter_middleware" app/ --include="*.py"
(no output)
```

A decision document with three options (A: implement under review, B:
formally defer with signed risk acceptance, C: block release until
decided) has been drafted at
`audits/risk_acceptances/content_filter_deferral.md`.

Engineering's recommendation is documented in that file: Option A.

The decision is owned by the Security/Safety reviewer per the TODO
T050 directive. Phase 0 records this decision per the TODO instructions;
Phase 1 T100 (wire the filter) is blocked until the decision is signed.

---

## T060 — Python runtime ADR

**Status:** Done. See `docs/adr/ADR-001-python-runtime-version.md`.

Decision: **Python 3.12.3** is the single supported runtime.

Rationale, rejected alternatives, and consequences are documented in the
ADR. Briefly: 3.12.3 matches the local `.venv`, matches half of CI
already, and is Render-supported; 3.11 would have required a wider
downgrade with no compensating benefit; system Python (3.14.5) is
explicitly out of scope.

## T061 — Apply Python runtime decision consistently

**Status:** Done.

Updates applied:

| File | Pre-fix | Post-fix |
|---|---|---|
| `.python-version` | `3.11.10` | `3.12.3` |
| `render.yaml` (PYTHON_VERSION envVar) | `3.11.9` | `3.12.3` |
| `README.md` ("Prerequisites" section) | "Python 3.11+" | "Python 3.12.3 (managed via `.python-version`; see ADR-001)" |
| `.github/workflows/*.yml` (32 workflow files) | mix of `"3.11"`, `"3.11.10"`, `"3.12"`, `'3.12'` | uniformly `"3.12.3"` (or `'3.12.3'`, or via `env.PYTHON_VERSION = "3.12.3"`) |

Validation:

```text
$ cat .python-version
3.12.3
$ grep -A1 'PYTHON_VERSION' render.yaml | head -4
      # ADR-001 declares Python 3.12.3 as the supported runtime.
      - key: PYTHON_VERSION
        value: "3.12.3"
$ grep -hE "^\s+python-version:|^\s*PYTHON_VERSION:" .github/workflows/*.yml | sort -u
          python-version: "3.12.3"
          python-version: ${{ env.PYTHON_VERSION }}
          python-version: '3.12.3'
  PYTHON_VERSION: "3.12.3"
```

All workflow YAMLs validated via `yaml.safe_load`: **36 of 36 OK**.

**AC met:** all deployment, CI, and developer-onboarding declarations
agree on Python 3.12.3.

**Developer follow-up (documented in ADR):** any contributor with an
older `.venv` must recreate it. The local `.venv` on the original tree
already matched 3.12.3 — no rebuild was required during this remediation.

---

## T070 — Freeze documentation generation

**Status:** Done. See `docs/README.md`.

The freeze and expected lift date are documented in the new
`docs/README.md`. No automated doc-generation workflows were found
running in `.github/workflows/`; the only doc-related script is
`scripts/check_docs_intelligence.py`, which is a validator (not a
generator). The freeze is therefore enforced socially via the rules
listed in `docs/README.md` rather than by a code change.

## T071 — Update `.gitignore` for generated artifacts

**Status:** Done by inspection — `.gitignore` already covers every
pattern the TODO listed.

Pattern audit:

```text
coverage_html/            PRESENT
site/                     PRESENT
temp/                     PRESENT
__pycache__/              PRESENT
*.pyc                     (covered by *.py[cod])
.pytest_cache/            PRESENT
.mypy_cache/              PRESENT
.ruff_cache/              PRESENT
htmlcov/                  PRESENT
coverage.xml              PRESENT
```

Validation:

```text
$ git status --short
 M .github/workflows/...           (Phase 0 T061 changes)
 M render.yaml                     (Phase 0 T010 + T061)
 M .python-version                 (Phase 0 T061)
... (Phase 0 remediation only)
```

None of the listed cache or coverage directories appear in `git status`.
**AC met.**

---

## Outcome

- T040–T042: triage closed by exclusion (clean tree) ✅
- T050: decision memo drafted; **awaiting Security/Safety sign-off** ⚠️
- T060: ADR committed declaring Python 3.12.3 ✅
- T061: every Python version declaration aligned to 3.12.3; 36/36 workflow
  YAMLs validated ✅
- T070: docs freeze documented in `docs/README.md` ✅
- T071: `.gitignore` already covers all required patterns; verified clean ✅

Phase 0 Domain E is closed with one explicitly open gate (T050) requiring
human reviewer sign-off.
