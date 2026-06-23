---
title: Stage 2 Documentation Housekeeping
status: active
owner: documentation-governance
reviewers: [release-management, engineering]
audience: engineering
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-22
review_interval_days: 30
evidence_command: make docs-housekeeping-check
code_anchors: [scripts/maintenance, Makefile, docs/generated]
---

# Stage 2 Documentation Housekeeping

Stage 2 turns the Stage 1 documentation governance scaffolding into an executable ratchet.
The goal is not to pretend that the documentation corpus is already clean. The goal is to make the current debt measurable, reproducible, and unable to grow silently.

## What Stage 2 enforces

- Deterministic documentation inventory generation.
- Git LFS-aware Markdown inventory behavior so GitHub source ZIPs and git-lfs clones produce the same committed inventory outputs.
- Reproducibility checking for `docs/generated/documentation_inventory.json`, `docs/generated/documentation_inventory.csv`, and `docs/generated/documentation_findings.csv`.
- Ratchet baselines for total findings, broken local links, metadata coverage, ADR-number duplicates, and stale off-project terms.
- A strict housekeeping target that exposes remaining debt but is not the default adoption gate.
- Root README link cleanup away from archived `docs/todos` paths.

## Default gate

Run this before committing documentation changes:

```bash
make docs-housekeeping-check
```

The default gate is safe for the current repo. It checks canonical docs, changed links, deterministic inventory, and ratchet baselines.
It validates committed generated inventory outputs before running ratchets; it does not regenerate those outputs.

## Refresh target

Regenerate committed inventory outputs explicitly when the documentation tree intentionally changes:

```bash
make docs-housekeeping-refresh
```

## Strict gate

Run this during cleanup sprints:

```bash
make docs-housekeeping-strict-check
```

The strict gate is expected to fail until the documentation debt is burned down. Its purpose is to show the true remaining cleanup surface.

## Refreshing baselines

Only refresh baselines after an intentional cleanup improvement or after a controlled structural change.

```bash
make docs-housekeeping-baseline-refresh
make docs-housekeeping-check
```

Baseline refreshes must be reviewed carefully because they can hide regressions if used casually.

## LFS reproducibility rule

Markdown files declared as Git LFS tracked in `.gitattributes` are inventoried by stable object identity rather than by expanded text content. This avoids a known mismatch where GitHub ZIP downloads contain LFS pointer files while local clones may contain expanded content.

The current example is:

```text
docs/release/backend_deletion_candidate_inventory.md
```

The inventory records the stable SHA-256 identity and logical object size, then skips content-derived title, link, and stale-term checks for that LFS-tracked Markdown file.
