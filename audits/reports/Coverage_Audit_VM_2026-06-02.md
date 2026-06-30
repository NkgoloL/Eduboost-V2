# Coverage Audit VM 2026-06-02

Date: 2026-06-02
Repository: /home/azureuser/Dev/Eduboost-V2
Branch: remediation/phase0-phase1
Scope: release infrastructure and coverage measurement baseline

## Baseline Source

- Source file: coverage.xml
- Source timestamp (UTC): 2026-06-01T22:13:06.572Z
- Coverage.py version: 7.13.5

## Baseline Metrics

- Line coverage: 31.89 percent
- Branch coverage: 4.487 percent
- Lines covered: 7,235 of 22,690
- Branches covered: 237 of 5,282

## Interpretation

- CI floor is currently 67 percent, so this baseline is below gate requirements.
- Branch coverage is now measured (non-zero), which satisfies instrumentation visibility but remains low.
- Additional Phase 2 coverage work is still required before ratcheting above 67 percent.

## Infrastructure Changes Completed With This Baseline

- Backend coverage job now uploads coverage.xml as a workflow artifact.
- Nightly backend workflow scaffold added for full coverage plus governance evidence collection.
- Coverage ratchet schedule documented in docs/engineering/coverage_debt.md.

## Next Measurement Actions

1. Run nightly workflow and capture first artifact set.
2. Triage and fix the known fast-gate failures centered on tests/unit/test_json_completion.py.
3. Re-run baseline after cleanup and compare against this report.
