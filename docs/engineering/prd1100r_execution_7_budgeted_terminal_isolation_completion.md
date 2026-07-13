# PRD-11.0R Execution-7 Budgeted Terminal Isolation Completion

This remediation makes the coverage diagnostic bounded and resumable. It does not
relax the 70% threshold, capture green evidence, close Execution-7, or authorise
Execution-8.

## Execution model

- The advisory wrapper allows 4,200 seconds.
- The coverage runner uses a 3,900-second inner budget and reserves 300 seconds for
  summary, checkpoint, archive, and checksum generation.
- Multi-file timeout leaves continue adaptive bisection until file-level isolation,
  subject to depth 8 and 256 generated leaves.
- Terminal collection compares collected nodes with terminal statuses already
  observed in the timed-out leaf and probes only unresolved nodes.
- Progress and resume manifests are written atomically after every collect or node
  attempt.
- Attempt reuse requires matching revision, command, timeout, marker expression,
  runtime versions, and test-file content hashes.

## Partial diagnostic semantics

Budget exhaustion is not a test timeout. A budget-limited run writes a structurally
valid, non-green partial summary with pending work, a resume manifest, a terminal
archive, and SHA-256 checksum. A later run can reuse compatible completed terminal
attempts.

Coverage from timed-out or interrupted attempts is not used as authoritative
coverage. After all execution blockers are resolved, the final percentage must be
produced by a fresh complete run.
