# Release Hygiene Checklist

Status: pending release-owner review

Before tagging a release candidate, confirm:

- [ ] `git status` has only intended release changes.
- [ ] No secrets or local-only credentials are staged.
- [ ] Generated docs are current or explicitly deferred.
- [ ] `TODO.md` statuses match readable evidence files.
- [ ] CI evidence links point to the current commit.
- [ ] Migration evidence includes upgrade output and rollback policy.
- [ ] Staging smoke evidence uses a real non-placeholder HTTPS URL.
- [ ] Known issues and beta limitations are non-empty.
- [ ] POPIA/legal/security approvals are linked or marked pending.
- [ ] Release bundle links resolve.

## Completion Rule

Every checked box needs a command, reviewer, or artifact reference.