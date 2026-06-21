# Gate 2R.1 Current Evidence State

Gate 2R.1 has candidate evidence collected and committed. Gate 2R.1 is not
closed. Independent approvals and a separate Gate 2R.2 authorisation commit
remain required.

Current candidate evidence was collected from source commit
`d3298ed7184b695127cc539e46482a8b16362d37` and committed separately at
`ffb8a0d99dcdcb88f60b8eb876ae87162358673f`.

If candidate evidence must be regenerated from a newer source commit, ensure
the worktree is clean and run:

```bash
bash scripts/collect_phase02r_evidence.sh --gate 2R.1
```

The collector creates a candidate evidence pack. It does not approve or close
the gate.

Independent approvals remain pending after candidate evidence collection; Gate
2R.2 remains blocked until a later approval and transition commit.
