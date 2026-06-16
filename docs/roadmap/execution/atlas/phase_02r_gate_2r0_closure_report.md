# Phase 2R Gate 2R.0 Closure Report

**Generated:** 2026-06-16T11:15:32Z
**Status:** Failed / remediation required
**Branch:** `feature/atlas-phase-02r-authoritative-caps-corpus`
**baseline_capture_sha:** `b238d8911a78deb351611ee82276dbfdf53651dc`
**base_against_origin_master:** `4b3805b700869aaeacce4141bb565e1963777163`
**gate_report_commit_sha:** pending until this report is committed
**eventual_gate_approval_commit_sha:** not issued

## Result

Gate 2R.0 closure evidence was collected. The approval flag must remain
`PHASE_02R_START_APPROVED=false` unless every raw command exits zero and the
worktree is clean.

## Source State

```text

```

## Evidence

See `docs/release-evidence/atlas/phase-02r/gate-2r0/`.

## Recommendation

Gate 2R.1 remains blocked. Remediate the failing raw commands before approval.
