---
title: "Git History & Packfile Remediation Runbook"
status: "active"
owner: "devops"
reviewers: ["platform", "engineering", "release-management"]
audience: "operator"
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: "2026-09-22"
review_interval_days: 90
evidence_command: "git count-objects -vH"
code_anchors: ["scripts/generate_release_notes.py", "docs/release/production_release_notes_v1.0.0-rc1.md"]
---

# Git History & Packfile Remediation Runbook

## Executive Summary

During prior automated release-note generation runs, `scripts/generate_release_notes.py` contained an unconstrained `SCAN_ROOTS` configuration that recursively ingested the output directory `docs/release/`. This caused `docs/release/production_release_notes_v1.0.0-rc1.md` to self-replicate exponentially across several commits, expanding the file to over 122MB in the working tree and embedding oversized blobs across git history.

While the working tree file has been sanitized and truncated to its canonical content (~197KB / 1,350 lines), the historical git packfile (`.git/objects/pack/`) retains the uncompressed and delta objects totaling ~250MB.

Because rewriting git history invalidates commit SHAs, disrupts open pull requests, and requires coordinated force-pushes across remote mirrors and developer checkouts, **this maintenance action must be executed under a strict, human-authorized maintenance window**.

---

## 1. Governance & Authorization (HALT Gate)

> [!CAUTION]
> **ANTI-THEATRE MANDATE**: Do NOT execute git history rewrites autonomously.
> This runbook is an operational procedure for the human Lead DevOps / Release Engineer.
> Execution alters all subsequent commit SHAs and requires a coordinated team re-clone.

### Required Approvals
- [ ] Lead Software Architect approval
- [ ] DevOps / SRE Lead authorization
- [ ] 24-hour advance developer announcement of maintenance window
- [ ] Active CI/CD deployments locked / frozen

---

## 2. Pre-Maintenance Preparation

### Step 2.1: Establish Maintenance Freeze
Notify the team and merge or close pending pull requests. Ensure no CI builds are running.

```bash
# Verify no active pushes or running workflows
gh workflow list
```

### Step 2.2: Create Full Mirror Backup
Before modifying any ref or object, create a pristine bare mirror of the repository.

```bash
# From an independent maintenance directory
cd /tmp
git clone --mirror git@github.com:NkgoloL/Eduboost-V2.git eduboost-v2-pre-remediation-backup.git
tar -czvf eduboost-v2-pre-remediation-backup-$(date +%Y%m%d).tar.gz eduboost-v2-pre-remediation-backup.git/
```

### Step 2.3: Create Pre-Remediation Tag in Workspace
Create an immutable reference tag in the active workspace.

```bash
git tag -a "archive/pre-packfile-remediation-$(date +%Y%m%d)" -m "Pre-packfile remediation historical snapshot"
git push origin "archive/pre-packfile-remediation-$(date +%Y%m%d)"
```

---

## 3. History Rewrite Procedure

The tool of choice is [`git-filter-repo`](https://github.com/newren/git-filter-repo) (modern replacement for deprecated `git filter-branch`).

### Step 3.1: Install `git-filter-repo`
```bash
python3 -m pip install git-filter-repo
# Verify installation
git filter-repo --version
```

### Step 3.2: Analyze Large Blobs
Verify that the target blob is indeed the root bloat driver:

```bash
git rev-list --objects --all \
| git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
| sed -n 's/^blob //p' \
| sort --numeric-sort --key=2 --reverse \
| head -n 10
```
Expected output: The top blob will correspond to `docs/release/production_release_notes_v1.0.0-rc1.md` (>100MB).

### Step 3.3: Execute Blob Stripping
To replace oversized historical snapshots of the release notes file while preserving the commit tree, run `git filter-repo` to strip objects exceeding 10MB in history:

```bash
# Strip blobs over 10MB across history
git filter-repo --strip-blobs-bigger-than 10M --force
```

Alternatively, to surgically rewrite only the history of `docs/release/production_release_notes_v1.0.0-rc1.md` while preserving the file at its current clean state:

```bash
# Replace target paths if needed
git filter-repo --path docs/release/production_release_notes_v1.0.0-rc1.md --invert-paths --force
# Note: Re-add the sanitized 197KB file immediately as the root release notes if stripped completely.
```

---

## 4. Packfile Expiration & Aggressive Garbage Collection

Once history has been rewritten, purge all reflogs and run aggressive packfile compaction:

```bash
# 1. Expire all unreachable reflog entries immediately
git reflog expire --expire=now --expire-unreachable=now --all

# 2. Aggressively repack objects and drop loose objects
git repack -a -d -f --depth=250 --window=250

# 3. Prune all unreferenced objects
git prune --expire=now

# 4. Run aggressive garbage collection
git gc --prune=now --aggressive
```

---

## 5. Verification & Integrity Checks

Verify the repository health, size reduction, and object tree integrity.

```bash
# Step 5.1: Verify object counts and packfile size
git count-objects -vH
```
*Expected Result:*
- `size-pack`: Reduced from ~250MB to < 40MB.
- `prune-packable`: 0
- `garbage`: 0

```bash
# Step 5.2: Verify full repository integrity
git fsck --full --strict
```
*Expected Result:* Exit code 0, no broken links, no dangling commits (or only acceptable dangling objects prior to pruning).

```bash
# Step 5.3: Verify essential operational test passes
pytest tests/unit/test_generate_release_notes.py
make docs-housekeeping-check
```

---

## 6. Coordinated Force-Push & Team Onboarding

> [!WARNING]
> Coordinated force-pushes overwrite remote branches. Ensure all team members have committed and pushed local work prior to this step.

### Step 6.1: Force-Push to Remote
```bash
# Re-add remote if git-filter-repo stripped it (git-filter-repo removes remotes as a safety feature)
git remote add origin git@github.com:NkgoloL/Eduboost-V2.git

# Push rewritten master and active branches
git push origin master --force
git push origin --force --tags
```

### Step 6.2: Team Member Recovery Instructions
Send this announcement to all developers with active checkouts:

```markdown
Subject: ACTION REQUIRED: Coordinated Git Repository Compaction Complete

The Git repository history maintenance has completed. All bloated objects have been pruned.
Because commit SHAs have changed, DO NOT PULL directly into existing branches.

Recommended Developer Action:
1. Back up any uncommitted work:
   git stash
2. Re-clone a fresh copy of the repository:
   cd ..
   git clone git@github.com:NkgoloL/Eduboost-V2.git Eduboost-V2-fresh
3. Apply any stashed or branch work via cherry-pick or format-patch.
```

---

## 7. Rollback & Disaster Recovery Procedure

If the history rewrite damages commit integrity or omits critical revisions:

1. Cease all work and halt pushing.
2. Restore the remote repository from the bare mirror backup:
   ```bash
   cd /tmp/eduboost-v2-pre-remediation-backup.git
   git push --mirror git@github.com:NkgoloL/Eduboost-V2.git
   ```
3. Have developers reset to the pre-remediation tag:
   ```bash
   git fetch origin
   git reset --hard archive/pre-packfile-remediation-$(date +%Y%m%d)
   ```
4. Verify repository returns to the pre-maintenance state.
