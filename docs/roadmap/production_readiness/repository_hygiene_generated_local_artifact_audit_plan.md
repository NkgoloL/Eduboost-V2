# Repository hygiene and generated/local artifact audit plan

## Canonical decision

PRD-0.9 records repository hygiene truth. It does not clean the repository.

The correct sequence is:

1. establish a repository hygiene policy;
2. inventory generated/local artifact candidates;
3. inventory suspicious command-output artifacts;
4. record evidence from clean `master` after authority lands;
5. hand off to PRD-0.10 for PRD-0 closure evidence and PRD-1 readiness gating.

## Evidence inventory

The PRD-0.9 capture step records:

- configured generated/local artifact candidates;
- candidates currently present in the repository snapshot;
- `.gitignore` coverage for candidates;
- suspicious top-level entries;
- terminal/pager-output artifact indicators;
- file counts and total byte estimates for configured paths;
- authority boundary flags.

## Deferred work

Physical cleanup, deletion, git history rewrite, large-file migration, generated-artifact movement, and branch/default-branch changes are deferred to later explicitly authorised slices. PRD-0.9 only creates the audit baseline.
