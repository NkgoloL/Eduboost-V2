---
title: Technical Audit Remediation Phase 02I — Backend Fast Topic-Map Provenance
status: active-control
owner: roadmap-governance
reviewers: [roadmap-governance, release-management, documentation-governance]
audience: roadmap-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-06
review_interval_days: 30
evidence_command: make docs-housekeeping-stage7-check
code_anchors: [docs/roadmap, docs/documentation/stage_7_release_archive_backlog_codemaps_governance.md]
---

# Technical Audit Remediation Phase 02I — Backend Fast Topic-Map Provenance

**Status:** Implementation ready  
**Authority gate:** `make test-fast` remains the only backend-fast passing authority.  
**Scope:** Final observed backend-fast failure: `tests/unit/test_topic_map_worklist.py::test_topic_map_worklist_preserves_source_hashes_for_scope`.

## Problem

After Phase 02H, the backend-fast authority gate had one remaining failing test. The Grade 7 Mathematics topic-map worklist preserved the Senior Phase Mathematics PDF source hash, but did not preserve the reviewed text-extract provenance hash expected by the topic-map worklist contract.

The missing contract is not a runtime tutor/KG change. It is static provenance metadata for the Content Factory topic-map worklist.

## Remediation

- Track `data/content_factory/source_text_extracts_manifest.json` with the reviewed Senior Phase Mathematics text-extract provenance record.
- Bind `caps_senior_mathematics_en` to:
  - immutable PDF source SHA-256 `64dcd19ee1d67109ff4172d9b098259954a2e77a55aeae0d11ee7ec033b0d8f8`
  - reviewed text-extract SHA-256 `881f88f60186856703767333a0c3f2331b8aeebb52dd11fcf46c2f25c90d3c33`
  - stable clean-checkout metadata path `data/caps/source_documents/text/caps_senior_mathematics_en.txt`
- Add Phase 02I verifier and focused tests.

## Evidence policy

Phase 02I evidence may be recorded separately, but backend-fast candidate evidence remains blocked until `make test-fast` exits 0 through `scripts/audit_remediation/collect_backend_fast_evidence.sh`.

## Boundaries

- No backend-fast pass is claimed by this focused evidence.
- No Phase 02R governance is changed.
- No production release-readiness claim is made.
- No live DB migration is executed.
- No runtime KG implementation is added.

KG remains a future architecture north star only.
