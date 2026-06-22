# Gate 2R.1 Current Evidence State

Gate 2R.1 has candidate evidence collected and committed. Gate 2R.1 is not
closed. Independent approvals and a separate Gate 2R.2 authorisation commit
remain required.

Current candidate evidence was regenerated from source commit
`e893cd876e650f4d996876cfedeb203243c5f1e1`.

Candidate handoff metadata is recorded in
`docs/release-evidence/atlas/phase-02r/gate-2r1/evidence_handoff_metadata.json`.
That metadata stamps the source commit, evidence commit, current branch tip,
remote branch SHA at handoff, and evidence-index SHA-256. It does not close
Gate 2R.1 or authorise Gate 2R.2.

If candidate evidence must be regenerated from a newer source commit, ensure
the worktree is clean and run:

```bash
bash scripts/collect_phase02r_evidence.sh --gate 2R.1
```

The collector creates a candidate evidence pack. It does not approve or close
the gate.

Independent approvals remain pending after candidate evidence collection; Gate
2R.2 remains blocked until a later approval and transition commit.
