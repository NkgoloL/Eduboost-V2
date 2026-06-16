# Phase 2R Gate 2R.1 Closure Report

**Generated:** $timestamp
**Status:** $status
**Branch:** \`$branch\`
**evidence_run_source_sha:** \`$head_sha\`
**base_against_origin_master:** \`$base_sha\`
**initial_gate_report_commit_sha:** \`8d972b5f\`
**remediation_code_commit_sha:** pending until this remediation is committed
**evidence_commit_sha:** pending until this evidence pack is committed
**eventual_gate_approval_commit_sha:** not issued

## Result

Gate 2R.1 closure evidence was collected into a temporary directory before it
was copied into the repository.

## Source State

\`\`\`text
$status_porcelain
\`\`\`

## Evidence

See \`docs/release-evidence/atlas/phase-02r/gate-2r1/\`.

## Recommendation

$([[ "$overall_rc" -eq 0 ]] && echo "Gate 2R.1 implementation preflight and patch-application verification passed." || echo "Gate 2R.1 remains blocked. Remediate the failing raw commands before proceeding.")
