# Gate 2R.1 Current Evidence State

Gate 2R.1 has candidate evidence collected and committed. Gate 2R.1 is not
closed. Independent approvals and a separate Gate 2R.2 authorisation commit
remain required.

Candidate evidence was collected from source commit
`c5a8cd829e8d5707e0f98f909b105af9b99ca903` and committed separately at
`4325a68f85597800b9741344a4a72c68f8830a73`.

If candidate evidence must be regenerated from a newer source commit, ensure
the worktree is clean and run:

```bash
bash scripts/collect_phase02r_evidence.sh --gate 2R.1
```

The collector creates a candidate evidence pack. It does not approve or close
the gate.

Independent approvals remain pending after candidate evidence collection; Gate
2R.2 remains blocked until a later approval and transition commit.
