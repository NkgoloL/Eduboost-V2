---
title: Git LFS Large Files
status: release-record
owner: release-management
reviewers: [release-management, evidence-custodian, documentation-governance]
audience: release-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 180
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/release, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Git LFS Large Files

The following files in this directory are tracked using Git LFS:
- `backend_deletion_candidate_inventory.md` (~96 MB)

## How to Access LFS Files

To download the actual files instead of the Git LFS pointers:
1. Ensure Git LFS is installed on your local machine:
   - **Debian/Ubuntu**: `sudo apt-get install git-lfs`
   - **macOS**: `brew install git-lfs`
   - **Windows**: Download installer from https://git-lfs.github.com
2. Initialize Git LFS:
   ```bash
   git lfs install
   ```
3. Fetch/pull the large files:
   ```bash
   git lfs pull
   ```
