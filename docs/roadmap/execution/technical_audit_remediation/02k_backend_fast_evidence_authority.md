# Technical Audit Remediation Phase 02K — Backend Fast Evidence Authority Repair

**Status:** Implementation ready  
**Stream:** technical-audit-remediation  
**Authority command:** `make test-fast`

## Why this slice exists

The backend-fast retry reached the final failure edge and then the focused topic-map provenance contract was repaired. However, the uploaded branch snapshot still contains candidate backend-fast evidence whose raw authority artifacts disagree with the candidate-pass claim:

- `raw/backend_fast_gate_result.json` records `returncode: 2` and `valid: false`.
- `raw/backend_fast_failure_classification.json` records one failed test.
- `raw/backend_fast_evidence_check.json` records `valid: true` with no checked artifacts.
- Several JSON raw artifacts are prefixed with shell command banners, making them not machine-readable JSON for the verifier.

This means the backend-fast gate cannot be treated as passed from the recorded evidence, even if the current code path is likely fixed. The next safe step is to repair the evidence authority harness and recollect the backend-fast evidence from a clean commit.

## Scope

This slice repairs only the candidate evidence harness:

1. Candidate JSON evidence files are captured as pure JSON with no `$ command` banner.
2. `verify_backend_fast_evidence.py` fails closed when raw JSON is malformed.
3. The verifier requires:
   - `backend_fast_gate_result.json.valid == true`
   - `backend_fast_gate_result.json.returncode == 0`
   - `backend_fast_failure_classification.json.failure_count == 0`
   - no failed tests and no matched failure categories
   - no failed/error lines in `backend_fast_gate.txt`
4. `SHA256SUMS.txt` excludes itself and is verified against raw evidence files.
5. Synthetic evidence checks with empty checked lists cannot mask a failed authority result.

## Out of scope

- No application-code remediation.
- No Phase 02R governance change.
- No product release-readiness claim.
- No live database migration.
- No runtime knowledge-graph implementation.

## Exit criteria

- Phase 02K verifier passes.
- Focused evidence-authority tests pass.
- `collect_backend_fast_evidence.sh` is rerun from a clean commit.
- Backend-fast candidate evidence is committed only if `make test-fast` exits `0` and `verify_backend_fast_evidence.py` independently returns `valid: true`.
