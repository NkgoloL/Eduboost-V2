# RR-004 Workspace Hygiene Policy

## Authority

RR-004 exists to make workspace hygiene reproducible and auditable before further roadmap work proceeds.

## Safe cleanup target

The safe cleanup target is a **dry-run** target. It identifies ignored build/cache artifacts without deleting them:

```bash
make rr004-ignored-artifact-clean-dry-run
```

This delegates to:

```bash
python3 scripts/workspace_hygiene/safe_cleanup_ignored_artifacts.py --dry-run --json
```

Actual deletion is intentionally not part of the evidence capture path and requires an explicit confirmation flag outside this closure evidence.

## Tracked-file-only audit inventory

The canonical tracked-file inventory command is:

```bash
git ls-files
```

The scanner records tracked-file counts, top-level counts, extension counts, docs/scripts/tests counts, and ignored artifact candidates.

## Boundary

This policy does not authorise production release, deployment, release tagging, public beta, runtime KG implementation, or destructive cleanup.
