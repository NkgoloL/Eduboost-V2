# PRD-0.9 — Repository hygiene and generated/local artifact audit

**Status:** Authority pending evidence capture  
**Stream:** PRD-PRODUCTION-READINESS  
**Depends on:** PRD-0.8 Branch/release naming reconciliation

## Objective

Record a controlled repository hygiene inventory after PRD-0.8 so that generated, cached, local, backup, and command-output artifacts cannot be mistaken for source authority, release evidence, or production readiness.

This slice is deliberately audit-first. It creates the policy, verifier, inventory, and evidence path needed to make later cleanup safe, but it does not remove files from the repository snapshot.

## In scope

- Add the canonical repository hygiene policy document.
- Inventory generated/local artifact candidates such as coverage files, logs, temp output, caches, package metadata, local backups, and generated reports.
- Inventory suspicious top-level command-output artifacts.
- Record `.gitignore` coverage for generated/local artifact candidates.
- Record counts and paths needed for later remediation planning.
- Preserve PRD-0 authority boundaries and advance the stream to PRD-0.10 after evidence capture.

## Out of scope

- No file deletion.
- No repository history rewrite.
- No generated artifact cleanup.
- No branch rename.
- No release tag creation.
- No deployment authority.
- No public beta/live learner traffic authority.
- No billing/live payment authority.
- No PRD-1 implementation.
- No new KG implementation slice.

## Closure evidence

PRD-0.9 closes only when:

- PRD-0.8 verifier remains valid.
- The repository hygiene policy document is present.
- The generated/local artifact inventory is captured.
- Suspicious top-level artifact candidates are recorded.
- The production-readiness register advances to PRD-0.10.
- Cleanup/deletion/rewrite authority remains false.
- All release/deployment/beta/billing boundaries remain false.
