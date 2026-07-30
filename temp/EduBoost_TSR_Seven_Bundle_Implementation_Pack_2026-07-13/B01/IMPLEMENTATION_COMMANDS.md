# B01 implementation commands — TSR-0 + TSR-1

## Purpose

Release Gate Recovery. This bundle is sequential and requires the preceding bundle marker to be valid. It prepares its own evidence directory, records every command result, times out hung processes, and restores changed files after a failed run unless `--keep-failed-changes` is explicitly supplied.

## Required manual/external controls

- `TSR-0.7`
- `TSR-1.11`

These controls require real review artifacts. The script will not invent approvals or mark them green.

## Standard execution

```bash
export REPO=/absolute/path/to/Eduboost-V2
cd "$(dirname "$REPO")"
python -m venv "$REPO/.venv"  # only when no managed environment already exists
source "$REPO/.venv/bin/activate"
python -m pip install --upgrade pip
python "B01/apply_bundle.py" --repo "$REPO" --phase all
```

When running from this bundle directory directly, use:

```bash
python apply_bundle.py --repo "$REPO" --phase all
```

## Safe smoke run

A smoke run validates payload integrity and structural preconditions but can never close the bundle:

```bash
python apply_bundle.py --repo "$REPO" --phase all --skip-heavy --keep-failed-changes
```

## Resume after a controlled failure

1. Read `docs/release-evidence/true-state-remediation/b01/implementation_state.json` and command logs.
2. Correct the reported blocker in the retained worktree.
3. Record required reviewed artifacts:

```bash
python "$REPO/scripts/true_state_remediation/record_manual_evidence.py"   --repo "$REPO" --bundle B01 --control <TSR-X.Y>   --reviewer "<name>" --reviewer-role "<role>"   --decision approved --artifact "<path-inside-or-outside-repo>"   --notes "<what was reviewed>"
```

4. Re-run verification:

```bash
python verify_bundle.py --repo "$REPO"
```

## Commit and handoff to the next bundle

After verification is green, review the diff and commit the implementation plus generated evidence before starting the next bundle:

```bash
cd "$REPO"
git status --short
git add -A
git commit -m "control(tsr): close b01 TSR-0 and TSR-1"
git status --short --branch
```

The next bundle intentionally refuses an uncommitted worktree. Push the branch and obtain hosted-CI evidence wherever that bundle lists it as a manual control.

## Failure and rollback behavior

- Dirty Git worktrees are refused unless `--allow-dirty` is explicitly supplied.
- Bundle payload hashes are validated before any repository modification.
- Files are backed up under `.tsr/backups/b01/<UTC timestamp>/`.
- Failed changes are restored by default.
- `--keep-failed-changes` retains the partial implementation for deliberate remediation.
- `--skip-heavy` never writes a valid completion marker.
- The next stage is `B02` and will refuse to run until this bundle marker is valid.

