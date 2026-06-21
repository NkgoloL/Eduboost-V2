# Gate 2R.1 Current Evidence State

Gate 2R.1 has candidate evidence collected and committed. Gate 2R.1 is not
closed. Independent approvals and a separate Gate 2R.2 authorisation commit
remain required.

Current candidate evidence was collected from source commit
`e6e43df45e4e990e9914a55134742b68c500ddd5` and committed separately at
`57f8a3c4ea51a19cd3601cdf5f3ae29753548644`.

If candidate evidence must be regenerated from a newer source commit, ensure
the worktree is clean and run:

```bash
bash scripts/collect_phase02r_evidence.sh --gate 2R.1
```

The collector creates a candidate evidence pack. It does not approve or close
the gate.

Independent approvals remain pending after candidate evidence collection; Gate
2R.2 remains blocked until a later approval and transition commit.
