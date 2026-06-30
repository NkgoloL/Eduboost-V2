# CAPS Source Acquisition & Topic-Map Pipeline — Enhanced Plan v2.0

**Document status:** Reconciled with current EduBoost repo implementation for engineering execution
**Owner:** EduBoost SA Platform Engineering
**Audience:** Senior Engineers, DevOps, Curriculum Architects
**Last revised:** 2026-06-02
**Repo reconciliation:** Current repo implementation and accepted EduBoost plan decisions are authoritative where this document previously conflicted.
**Supersedes:** Initial plan (informal draft, no version)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Objectives and Success Criteria](#2-objectives-and-success-criteria)
3. [Scope and Exclusions](#3-scope-and-exclusions)
4. [Architecture Overview](#4-architecture-overview)
5. [Data Model & Schema Contracts](#5-data-model--schema-contracts)
6. [Source Inventory & Coverage Matrix](#6-source-inventory--coverage-matrix)
7. [Pipeline Design & DAG Specification](#7-pipeline-design--dag-specification)
8. [Script Interface Contracts](#8-script-interface-contracts)
9. [Object Store Layout](#9-object-store-layout)
10. [Topic Map Schema](#10-topic-map-schema)
11. [CI/CD Integration](#11-cicd-integration)
12. [Observability & Alerting](#12-observability--alerting)
13. [Security & Compliance](#13-security--compliance)
14. [Test Plan](#14-test-plan)
15. [Risk Register](#15-risk-register)
16. [Rollback & Recovery](#16-rollback--recovery)
17. [Implementation Roadmap](#17-implementation-roadmap)
18. [Assumptions & Constraints](#18-assumptions--constraints)
19. [Appendix A — Manifest JSON Schema](#appendix-a--manifest-json-schema)
20. [Appendix B — Topic Map JSON Schema](#appendix-b--topic-map-json-schema)
21. [Appendix C — Scope ID Convention](#appendix-c--scope-id-convention)
22. [Appendix D — Official DBE Source Catalogue](#appendix-d--official-dbe-source-catalogue)

---

## 1. Executive Summary

This plan specifies a reproducible, auditable source-acquisition and topic-map extraction pipeline covering all CAPS-aligned Grade R–7 scopes required by EduBoost SA. The pipeline transforms official DBE/CAPS PDF publications into structured, machine-readable topic maps that drive downstream content generation and adaptive assessment.

The system separates **binary artefacts** (PDFs, maximum several hundred MB) from **structured metadata** (JSON manifests and topic maps committed to git) by routing source documents through a versioned object store while keeping only SHA-256 hashes, canonical URLs, and extraction status in the repository. No content generation for any scope can begin until its upstream source chain reaches `topic_map_approved` status, enforced by schema validation at CI time.

The design is intentionally conservative: it is better to record a scope as `not_applicable` with evidence than to fabricate coverage from unofficial sources.

### 1.0 Implementation Checkpoint — 2026-06-02

| Area | Current implementation state |
|------|------------------------------|
| Canonical DBE source URLs | Implemented via `scripts/curriculum/resolve_dbe_caps_urls.py`; all 23 Grade R-7 source documents resolve from official DBE CAPS phase pages. |
| Local source files, hashes, and text extracts | Implemented via `scripts/curriculum/download_caps_sources.py` and `scripts/curriculum/extract_caps_source_text.py`; all 23 official PDFs are staged on the VM under ignored `data/caps/source_documents/raw/`, PDF SHA-256 hashes are recorded in `data/caps/source_documents/manifest.json`, and text-extract hashes/counts are tracked in `data/content_factory/source_text_extracts_manifest.json`. |
| Azure object storage | Implemented and uploaded: `eduboostcaps06022047` in `rg-eduboost-dev` contains 23 blobs in `caps-sources`; every source document now has an immutable Blob URI in `data/caps/source_documents/manifest.json`. Uploader supports `--auth-mode login` and `--auth-mode key`. |
| Topic maps | Worklist, unreviewed draft envelopes, and validation gates are implemented via `scripts/curriculum/build_topic_map_worklist.py`, `scripts/curriculum/scaffold_topic_map_drafts.py`, and `scripts/curriculum/validate_topic_maps.py`; 50 non-Grade-4-maths scope drafts exist under `data/content_factory/topic_map_drafts/` and are provenance-checked against source/text hashes and Blob URIs. Reviewed runtime maps are still pending before generation readiness. |

### 1.1 Repository Reconciliation Decisions

This v2 plan is reconciled to the current implementation branch. These decisions override any older terminology elsewhere in the document:

| Area | Reconciled decision |
|------|---------------------|
| Source manifest path | Use `data/caps/source_documents/manifest.json`, not the older proposed `data/caps/source_manifest.json`. |
| Manifest root key | Use `documents`, not the older proposed `sources`. |
| Source file storage | Store PDFs in Azure Blob/object store; git tracks only manifests, hashes, object URIs, topic maps, and validators. |
| Local raw source staging | Use ignored `data/caps/source_documents/raw/`. |
| Scope IDs | Preserve current repo IDs such as `grade4_mathematics_en`; add metadata fields for phase, language role, and subject slug instead of migrating existing IDs. |
| Source status enum | Use current repo enum values: `planned`, `source_loaded`, `topic_map_approved`, `retired`. If a fuller lifecycle is needed later, migrate code and docs together. |
| Generation readiness | A scope is generation-ready only when its linked source document is `topic_map_approved`, its topic map exists, and its scope has non-empty `caps_refs`. |
| First Additional Language | Normalize user wording `Spedi` to `Sepedi` / ISO 639-3 `nso`; replace generic FAL placeholders with Sepedi-specific scope/source metadata during implementation. |
| Coding and Robotics | Add planned scopes and source records, but mark unsupported grades as `not_applicable` with DBE evidence rather than fabricating CAPS coverage. |


---

## 2. Objectives and Success Criteria

### 2.1 Primary Objectives

| # | Objective |
|---|-----------|
| O-1 | All Grade R–7 scopes for the defined subject/language matrix have a manifest record with a canonical DBE URL or a documented `not_applicable` reason. |
| O-2 | Every `applicable` source record has a verified SHA-256 hash stored in the manifest and an object-store URI pointing to the immutable, uploaded PDF. |
| O-3 | Every `applicable` scope has a reviewed, validated topic map committed to `data/caps/topic_maps/`. |
| O-4 | No content generation pipeline can reference a scope that has not reached `generation_ready` status. |
| O-5 | The entire acquisition pipeline is reproducible: re-running scripts on a fresh VM produces identical hashes for identical source documents. |

### 2.2 Measurable Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| Source manifest completeness | 100% of expected scopes have a record | `source_inventory.py --report` exits 0 |
| Hash verification pass rate | 100% | `download_caps_sources.py --verify-all` |
| Topic map coverage | 100% of non–`not_applicable` scopes | `validate_topic_maps.py --all` exits 0 |
| CI gate reliability | Zero false positives over 30-day window | CI dashboard metric |
| Extraction round-trip time | ≤ 4 hours for full Grade R–7 corpus | Pipeline execution log |

---

## 3. Scope and Exclusions

### 3.1 In Scope

**Grades:** R, 1, 2, 3, 4, 5, 6, 7

**Phases:**

| Phase | Grades |
|-------|--------|
| Foundation Phase | R, 1, 2, 3 |
| Intermediate Phase | 4, 5, 6 |
| Senior Phase (partial) | 7 |

**Home Language:** English (HL)

**First Additional Language:** Sepedi (FAL)

**Content Subjects:**

| Phase | Subjects |
|-------|---------|
| Foundation | Mathematics, Life Skills, Coding and Robotics (where official source exists) |
| Intermediate | Mathematics, Natural Sciences and Technology (NST), Social Sciences, Life Skills, Coding and Robotics (where official source exists) |
| Senior (Gr 7) | Mathematics, Natural Sciences, Social Sciences, Technology, Economic and Management Sciences (EMS), Life Orientation, Creative Arts, Coding and Robotics (where official source exists) |

### 3.2 Explicit Exclusions

- Grades 8–12 (out of scope for Phase 1 of EduBoost SA).
- Afrikaans and all other Home Language / FAL combinations beyond English HL and Sepedi FAL.
- Third Additional Language tracks.
- Private school curricula (IEB, Cambridge).
- Any non-DBE source as a primary source of truth. Third-party sources may inform review notes only.
- Binary PDF files from git history — these are exclusively managed in the object store.

---

## 4. Architecture Overview

```
┌────────────────────────────────────────────────────────────────────┐
│  Git Repository (source of truth for structured metadata only)     │
│                                                                    │
│  data/caps/source_documents/manifest.json   ← documents, hashes, URIs, status          │
│  data/caps/topic_maps/*.json      ← reviewed topic maps            │
│  scripts/curriculum/*.py          ← acquisition scripts            │
│  .github/workflows/caps_ci.yml    ← validation gates              │
└────────────────────────────────────┬───────────────────────────────┘
                                     │ git push triggers CI
                                     ▼
┌──────────────────────────────────────────────────────────────────┐
│  CI Pipeline  (GitHub Actions / Azure Pipelines)                 │
│  ┌──────────────────┐  ┌───────────────────────┐                 │
│  │ validate_manifest│  │ validate_topic_maps   │                 │
│  │ (schema + hashes)│  │ (structure + citations│                 │
│  └──────────────────┘  └───────────────────────┘                 │
└──────────────────────────────────────────────────────────────────┘
                                     │
          ┌──────────────────────────┴────────────────────────┐
          │                                                   │
          ▼                                                   ▼
┌─────────────────────┐                         ┌─────────────────────┐
│  Object Store       │                         │  Local VM Staging   │
│  (Azure Blob /      │◄───── publish ──────────│  data/caps/         │
│   configured store) │                         │  source_documents/  │
│                     │                         │  raw/   (gitignored)│
│  caps-sources/      │                         └─────────────────────┘
│  {phase}/{subject}/ │                                    ▲
│  {lang}/{file}.pdf  │                                    │ download
└─────────────────────┘                         ┌──────────┴──────────┐
                                                 │  DBE/CAPS Official  │
                                                 │  Web / FTP Sources  │
                                                 └─────────────────────┘
```

**Key architectural invariants:**

1. **Immutability.** Object-store keys are never overwritten; if a source document changes, a new versioned key is created and the manifest is updated with a `superseded_by` pointer.
2. **Hash-first.** SHA-256 is computed from the local download before any upload. The object store is never treated as authoritative over the hash; the manifest is.
3. **Status monotonicity.** Source status advances only forward through the defined lifecycle: `planned → source_loaded → topic_map_approved`. No backwards transitions are permitted without an explicit manifest correction entry and reviewer approval.
4. **Separation of concerns.** Scripts are idempotent read-only reporters (`source_inventory.py`) or mutating operators with explicit `--commit` flags (`download_caps_sources.py`). Dry-run is the default for all mutating scripts.

---

## 5. Data Model & Schema Contracts

### 5.1 Source Record Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `document_id` | `string` | ✅ | Globally unique, slug format. E.g. `caps_foundation_mathematics_en` |
| `phase` | `enum` | ✅ | `foundation`, `intermediate`, `senior` |
| `applicable_grades` | `array[string]` | ✅ | E.g. `["4","5","6"]` |
| `applicable_subjects` | `array[string]` | ✅ | Normalised slug list |
| `language_role` | `enum` | ✅ | `home_language`, `first_additional_language`, `content_subject` |
| `language_code` | `string` | ✅ | ISO 639-3 or ISO 639-1: `eng`, `nso`, `n/a` |
| `source_status` | `enum` | ✅ | See §5.2 |
| `canonical_source_url` | `string` | conditional | Required if `source_status ≠ not_applicable` |
| `object_store_uri` | `string` | conditional | Required when `source_status ≥ source_loaded` |
| `source_sha256` | `string` | conditional | Required when `source_status ≥ source_loaded` |
| `downloaded_at` | `datetime` | conditional | ISO 8601, UTC; required when `source_status >= source_loaded` |
| `published_at` | `datetime` | conditional | ISO 8601, UTC; required when object-store upload is complete |
| `evidence_notes` | `string` | conditional | Required when `source_status = not_applicable` |
| `superseded_by` | `string` | optional | `document_id` of replacement record |
| `topic_map_paths` | `array[string]` | conditional | Required when `source_status = topic_map_approved` |
| `review_status` | `enum` | ✅ | `pending`, `approved`, `rejected`, `not_applicable` |
| `reviewed_at` | `datetime` | conditional | Required if `review_status = approved` |
| `reviewer_id` | `string` | conditional | Required if `review_status = approved` |
| `review_notes` | `string` | optional | Freeform reviewer comments |

### 5.2 Source Status Lifecycle

```
planned
  │  authoritative URL identified, no verified source yet
  ▼
source_loaded
  │  source file downloaded, SHA-256 recorded, object-store URI available
  ▼
topic_map_approved ← terminal success state for generation readiness

retired ← terminal state for superseded source records
```

`not_applicable` is a v2 requirement for unsupported scope/source combinations. Add it as an explicit enum migration before marking any Coding and Robotics or missing-language source as not applicable.

> **Status invariant:** A scope record is considered **generation_ready** if and only if
> `source_status = topic_map_approved AND reviewer metadata is present`.

### 5.3 Scope Readiness State Machine

```
                   ┌──────────────────┐
                   │     planned      │
                   └────────┬─────────┘
                            │ download + SHA-256 verified + object store upload
                            ▼
                   ┌──────────────────┐
                   │   source_loaded  │
                   └────────┬─────────┘
                            │ reviewed topic map exists for the scope
                            ▼
                   ┌──────────────────┐
                   │ topic_map_approved│
                   └────────┬─────────┘
                            │ scope has non-empty caps_refs and valid topic_map_path
                            ▼
               ┌────────────────────────┐
               │   generation_ready     │ ← content pipeline gates on this
               └────────────────────────┘
```

---

## 6. Source Inventory & Coverage Matrix

### 6.1 Foundation Phase (Grades R–3)

| Document | Grades | Subject/Language | Expected DBE Doc | Status |
|----------|--------|-----------------|-----------------|--------|
| `caps_foundation_home_language_en` | R,1,2,3 | English HL | CAPS Foundation Phase English HL (2011) | planned |
| `caps_foundation_sepedi_first_additional_language_en` | R,1,2,3 | Sepedi FAL | CAPS Foundation Phase Sepedi FAL (2011) | planned |
| `caps_foundation_mathematics_en` | R,1,2,3 | Mathematics | CAPS Foundation Phase Mathematics (2011) | planned |
| `caps_foundation_life_skills_en` | R,1,2,3 | Life Skills | CAPS Foundation Phase Life Skills (2011) | planned |
| `caps_foundation_coding_and_robotics_en` | R,1,2,3 | Coding & Robotics | DBE Coding & Robotics Policy (2021) — verify grade band | planned |

### 6.2 Intermediate Phase (Grades 4–6)

| Document | Grades | Subject/Language | Expected DBE Doc | Status |
|----------|--------|-----------------|-----------------|--------|
| `caps_intermediate_home_language_en` | 4,5,6 | English HL | CAPS Intermediate Phase English HL (2011) | planned |
| `caps_intermediate_sepedi_first_additional_language_en` | 4,5,6 | Sepedi FAL | CAPS Intermediate Phase Sepedi FAL (2011) | planned |
| `caps_intermediate_phase_mathematics_grade4_6` | 4,5,6 | Mathematics | CAPS Intermediate Phase Mathematics (2011) | planned |
| `caps_intermediate_natural_sciences_and_technology_en` | 4,5,6 | Natural Sciences & Technology | CAPS Intermediate Phase NST (2011) | planned |
| `caps_intermediate_social_sciences_en` | 4,5,6 | Social Sciences | CAPS Intermediate Phase Social Sciences (2011) | planned |
| `caps_intermediate_life_skills_en` | 4,5,6 | Life Skills | CAPS Intermediate Phase Life Skills (2011) | planned |
| `caps_intermediate_coding_and_robotics_en` | 4,5,6 | Coding & Robotics | DBE Coding & Robotics Policy (2021) — verify grade band | planned |

### 6.3 Senior Phase — Grade 7 Only

| Document | Grades | Subject/Language | Expected DBE Doc | Status |
|----------|--------|-----------------|-----------------|--------|
| `caps_senior_home_language_en` | 7 | English HL | CAPS Senior Phase English HL (2011) | planned |
| `caps_senior_sepedi_first_additional_language_en` | 7 | Sepedi FAL | CAPS Senior Phase Sepedi FAL (2011) | planned |
| `caps_senior_mathematics_en` | 7 | Mathematics | CAPS Senior Phase Mathematics (2011) | planned |
| `caps_senior_natural_sciences_en` | 7 | Natural Sciences | CAPS Senior Phase Natural Sciences (2011) | planned |
| `caps_senior_social_sciences_en` | 7 | Social Sciences | CAPS Senior Phase Social Sciences (2011) | planned |
| `caps_senior_technology_en` | 7 | Technology | CAPS Senior Phase Technology (2011) | planned |
| `caps_senior_economic_management_sciences_en` | 7 | EMS | CAPS Senior Phase EMS (2011) | planned |
| `caps_senior_life_orientation_en` | 7 | Life Orientation | CAPS Senior Phase Life Orientation (2011) | planned |
| `caps_senior_creative_arts_en` | 7 | Creative Arts | CAPS Senior Phase Creative Arts (2011) | planned |
| `caps_senior_coding_and_robotics_en` | 7 | Coding & Robotics | DBE Coding & Robotics Policy (2021) — verify grade band | planned |

### 6.4 Coverage Heatmap Legend

| Status Symbol | Meaning |
|:---:|---------|
| ⬜ | `planned` — record exists, no download |
| 🟡 | `downloaded` — local staging only |
| 🟠 | `source_loaded` — uploaded to object store |
| 🟢 | `topic_map_approved` — generation ready |
| ❌ | `not_applicable` — evidence recorded |

---

## 7. Pipeline Design & DAG Specification

The pipeline is composed of five logically ordered stages. Stages 3–5 are safe to parallelise per-document once stage 2 is complete.

```
Stage 1: Inventory Audit
└── source_inventory.py
    Inputs:  source_documents/manifest.json, expected_scopes.yaml
    Outputs: inventory_report.json (stdout + file)
    Idempotent: Yes (read-only)

Stage 2: Download & Hash
└── download_caps_sources.py
    Inputs:  inventory_report.json (planned records only)
    Outputs: PDFs to data/caps/source_documents/raw/
             Updated manifest entries: downloaded → source_loaded
    Idempotent: Yes (skips existing verified files by SHA-256 match)
    Concurrency: max 4 parallel downloads (rate-limit DBE servers)
    Retry: 3× with exponential backoff (2s, 8s, 32s)

Stage 3: Object Store Publish
└── publish_caps_sources.py
    Inputs:  source_loaded manifest records, local staged files
    Outputs: object_store_uri written to manifest
    Idempotent: Yes (uses content-addressed key from SHA-256)
    Concurrency: max 8 parallel uploads

Stage 4: Topic Map Extraction
└── extract_topic_maps.py
    Inputs:  source_loaded PDF from object store (or local cache)
    Outputs: data/caps/topic_maps/{scope_id}.draft.json
             Updated manifest: draft topic_map_paths/evidence; source_status remains source_loaded
    Idempotent: Yes (draft output keyed by source SHA-256)
    Strategy: pdfminer.six text extraction → section parser → CAPS schema mapper
    Multi-grade split: one source PDF → N per-grade scope maps

Stage 5: Topic Map Validation & Review Gate
└── validate_topic_maps.py
    Inputs:  data/caps/topic_maps/*.json
    Outputs: validation_report.json
             Exits non-zero if any non-not_applicable scope fails validation
    Review gate: source_status advances to topic_map_approved only after human reviewer metadata is present
```

### 7.1 Orchestration Options

For automated / scheduled runs, the pipeline is expressed as a DAG compatible with either **Prefect** or **Apache Airflow**:

```python
# Prefect pseudo-flow
@flow(name="caps_acquisition")
def caps_acquisition_flow():
    inventory   = audit_inventory()           # Stage 1
    downloads   = download_sources(inventory) # Stage 2
    uploads     = publish_to_store(downloads) # Stage 3
    extractions = extract_maps.map(uploads)   # Stage 4, parallelised
    validate_maps(extractions)                # Stage 5
```

For ad-hoc / developer runs, each script is independently executable via CLI (see §8).

---

## 8. Script Interface Contracts

All scripts follow the same interface conventions:

- `--dry-run` (default on): prints what would be done, makes no changes.
- `--commit`: required to apply mutations.
- `--manifest`: path to `source_documents/manifest.json` (default: `data/caps/source_documents/manifest.json`).
- Exit codes: `0` success, `1` validation failure, `2` environment/config error, `3` partial failure with report.
- All output written to `stdout` (human-readable) and `--output-json <path>` (machine-readable).

### 8.1 `source_inventory.py`

```
Usage: python scripts/curriculum/source_inventory.py [OPTIONS]

Options:
  --manifest PATH         Path to source manifest JSON
  --expected PATH         Path to expected_scopes.yaml
  --output-json PATH      Write machine-readable report to file
  --filter-status STATUS  Filter output by source_status value
  --report                Print summary counts table

Output fields per record:
  document_id, phase, applicable_grades, applicable_subjects,
  source_status, has_url, has_hash, has_object_uri,
  has_reviewed_topic_map, is_generation_ready, gap_reason

Exit 0: All expected records present with no unresolvable gaps.
Exit 1: Missing records or unresolvable gaps detected.
```

### 8.2 `download_caps_sources.py`

```
Usage: python scripts/curriculum/download_caps_sources.py [OPTIONS]

Options:
  --manifest PATH         Source manifest JSON
  --staging-dir PATH      Local staging directory (default: data/caps/source_documents/raw/)
  --filter-document ID    Process only a specific document_id
  --max-parallel INT      Max concurrent downloads (default: 4)
  --timeout-secs INT      Per-request timeout (default: 120)
  --commit                Actually write files and update manifest
  --dry-run               Default; describe actions only

Behaviour:
  - Skips records where source_status >= source_loaded (already done).
  - Downloads to staging dir as {document_id}.pdf.tmp, then renames on success.
  - Computes SHA-256 immediately after successful download.
  - Fails with exit 1 if file is empty, not a valid PDF, or hash changes on re-run.
  - Updates manifest entries from downloaded → source_loaded on success.

Exit 0: All planned records downloaded and hashed.
Exit 1: One or more downloads failed.
Exit 3: Partial success; report written to --output-json.
```

### 8.3 `publish_caps_sources.py`

```
Usage: python scripts/curriculum/publish_caps_sources.py [OPTIONS]

Options:
  --manifest PATH
  --staging-dir PATH
  --store-backend {azure|s3|gcs}
  --container STR         Object store bucket/container name
  --commit
  --dry-run

Key pattern: caps-sources/{phase}/{subject_slug}/{lang_code}/{document_id}_{sha256[:8]}.pdf

Behaviour:
  - Only processes records with source_status = source_loaded.
  - Upload is content-addressed: if object key exists with matching ETag/MD5, skip.
  - Sets object metadata: document_id, sha256, phase, canonical_source_url.
  - Updates manifest object_store_uri on success.
  - Status remains source_loaded after upload; review is required before topic_map_approved.
```

### 8.4 `extract_topic_maps.py`

```
Usage: python scripts/curriculum/extract_topic_maps.py [OPTIONS]

Options:
  --manifest PATH
  --staging-dir PATH
  --output-dir PATH       Default: data/caps/topic_maps/
  --document-id ID        Process a single document
  --extractor {pdfminer|pypdf2|tesseract}   Default: pdfminer
  --commit
  --dry-run

Behaviour:
  - Fetches PDF from object store (or local cache if SHA-256 matches).
  - Parses structure: chapter → section → subsection → topic → assessment standard.
  - For multi-grade documents, generates one .draft.json per grade in applicable_grades.
  - Scope ID used as output filename: {scope_id}.draft.json
  - Does NOT advance topic_map_approved; human review required.
  - Leaves manifest source_status as source_loaded until review approval.
  - Appends topic_map_paths list in manifest.

Draft output path: data/caps/topic_maps/{scope_id}.draft.json
Final output path: data/caps/topic_maps/{scope_id}.json  (after review)
```

### 8.5 `validate_topic_maps.py`

```
Usage: python scripts/curriculum/validate_topic_maps.py [OPTIONS]

Options:
  --manifest PATH
  --maps-dir PATH
  --all                   Validate every non-not_applicable scope
  --scope-id ID           Validate a single scope
  --strict                Fail on warnings, not just errors
  --output-json PATH

Validation checks:
  1. JSON schema conformance (Appendix B schema).
  2. Every topic has >= 1 source_citation with document_id, page_number, section_heading.
  3. review_status, reviewed_at, reviewer_id all present and non-empty.
  4. No fabricated topics (topics must map to a cited CAPS section).
  5. assessment_standards array non-empty for grade-level scopes.
  6. For language subjects: strands (reading, writing, grammar, oral, comprehension) present.
  7. For Maths/Science: topic hierarchy depth >= 2 (topic → subtopic).
  8. prerequisites array entries reference valid scope_ids.
  9. vocabulary array min 5 entries for Gr 4+ scopes.
  10. misconceptions array min 3 entries for Gr 4+ scopes.
```

---

## 9. Object Store Layout

```
caps-sources/
├── foundation/
│   ├── english_hl/
│   │   └── eng/
│   │       └── caps_foundation_home_language_en_a3f2b1c4.pdf
│   ├── sepedi_fal/
│   │   └── nso/
│   │       └── caps_foundation_sepedi_first_additional_language_en_b7e9d2f1.pdf
│   ├── mathematics/
│   │   └── na/
│   │       └── caps_foundation_mathematics_en_c1d4e8a2.pdf
│   └── ...
├── intermediate/
│   └── ...
└── senior/
    └── ...
```

**Key convention:** `{phase}/{subject_slug}/{lang_code}/{document_id}_{sha256_prefix8}.pdf`

The 8-character SHA-256 prefix in the filename provides at-a-glance integrity checking and prevents silent overwrites.

**Object metadata tags (set at upload):**

```json
{
  "document_id": "caps_foundation_home_language_en",
  "sha256": "a3f2b1c4...",
  "canonical_source_url": "https://www.education.gov.za/...",
  "phase": "foundation",
  "uploaded_at": "2026-06-02T10:00:00Z",
  "eduboost_env": "production"
}
```

---

## 10. Topic Map Schema

### 10.1 Field Overview

Each topic map file (`{scope_id}.json`) contains:

```json
{
  "scope_id":           "string   — matches Appendix C convention",
  "document_id":        "string   — foreign key to source manifest",
  "grade":              "string   — single grade: 'R','1'–'7'",
  "phase":              "string",
  "subject_slug":       "string",
  "language_role":      "string",
  "language_code":      "string",
  "caps_version":       "string   — e.g. '2011', '2021'",
  "extraction_method":  "string   — e.g. 'pdfminer_v0.1'",
  "extracted_at":       "datetime",
  "review_status":      "string   — pending | approved | rejected",
  "reviewed_at":        "datetime | null",
  "reviewer_id":        "string | null",
  "review_notes":       "string | null",
  "terms": [
    {
      "term_number":    "integer",
      "weeks":          "string  — e.g. '1-3'",
      "topics": [
        {
          "topic_id":             "string",
          "heading":              "string",
          "subtopics":            ["string"],
          "assessment_standards": ["string"],
          "source_citations": [
            {
              "document_id":     "string",
              "page_number":     "integer",
              "section_heading": "string"
            }
          ],
          "prerequisites":     ["scope_id:topic_id"],
          "vocabulary":        ["string"],
          "misconceptions":    ["string"]
        }
      ]
    }
  ],
  "strands": {
    "note": "Language subjects only",
    "reading":       ["topic_id"],
    "writing":       ["topic_id"],
    "grammar":       ["topic_id"],
    "oral":          ["topic_id"],
    "comprehension": ["topic_id"]
  },
  "meta": {
    "total_topics":               "integer",
    "total_assessment_standards": "integer",
    "coverage_completeness":      "float  — 0.0–1.0 automated estimate"
  }
}
```

### 10.2 Multi-Grade Document Splitting

When a single DBE PDF covers multiple grades (e.g., Intermediate Phase Maths Gr 4–6), the extraction script emits:

```
data/caps/topic_maps/
├── grade4_mathematics_en.draft.json
├── grade5_mathematics_en.draft.json
└── grade6_mathematics_en.draft.json
```

Each file carries `grade: "4"` / `"5"` / `"6"` and `document_id: "caps_intermediate_phase_mathematics_grade4_6"`, preserving the provenance link without merging grade-level distinctions.

---

## 11. CI/CD Integration

### 11.1 Pull Request Gate (`.github/workflows/caps_ci.yml`)

```yaml
name: CAPS Source & Topic Map Validation

on:
  pull_request:
    paths:
      - 'data/caps/source_documents/manifest.json'
      - 'data/caps/topic_maps/**'
      - 'scripts/curriculum/**'

jobs:
  validate-manifest:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements/curriculum.txt
      - name: Validate source manifest schema
        run: python scripts/curriculum/validate_source_manifest.py --strict
      - name: Inventory completeness check
        run: python scripts/curriculum/source_inventory.py --report --output-json ci_inventory.json
      - name: Check for unresolved gaps
        run: python scripts/curriculum/source_inventory.py --fail-on-gaps

  validate-topic-maps:
    needs: validate-manifest
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements/curriculum.txt
      - name: Validate all topic maps
        run: python scripts/curriculum/validate_topic_maps.py --all --strict
      - name: Coverage report
        run: python scripts/curriculum/report_content_coverage.py --strict-counts

  existing-regression:
    needs: validate-topic-maps
    runs-on: ubuntu-22.04
    steps:
      - name: Grade 4 Maths launch validation (regression)
        run: python scripts/curriculum/validate_topic_maps.py --scope-id grade4_mathematics_en
```

### 11.2 Scheduled Acquisition Run

A separate workflow (`caps_acquisition_nightly.yml`) runs on a weekly schedule:

1. Calls `source_inventory.py` — emits gaps report.
2. If gaps exist: opens a GitHub Issue with the gap report.
3. Does **not** auto-download — download requires `--commit` from a human operator.

This prevents uncontrolled changes to production manifest data from automated runs.

---

## 12. Observability & Alerting

### 12.1 Pipeline Metrics

All scripts emit structured JSON log lines compatible with ELK / Azure Monitor:

```json
{
  "timestamp": "2026-06-02T10:14:32Z",
  "level": "INFO",
  "script": "download_caps_sources",
  "event": "download_complete",
  "document_id": "caps_foundation_home_language_en",
  "sha256": "a3f2b1c4...",
  "file_size_bytes": 2456123,
  "duration_ms": 3421
}
```

### 12.2 Key Metrics to Track

| Metric | Alert Threshold | Channel |
|--------|----------------|---------|
| `source_status_planned_count` | > 0 for > 30 days | Slack #caps-ops |
| `hash_verification_failures` | > 0 | PagerDuty (P2) |
| `topic_map_validation_errors` | > 0 on main branch | CI failure + Slack |
| `object_store_upload_failures` | > 0 | PagerDuty (P2) |
| `sha256_drift_detected` | Any | PagerDuty (P1) — indicates tampered source |
| `ci_gate_duration_seconds` | > 300s | Slack #ci-health |

### 12.3 SHA-256 Drift Detection

A weekly cron job (`verify_object_store_hashes.py`) re-downloads every object-store PDF, recomputes SHA-256, and compares against the manifest. Any mismatch triggers a P1 alert and blocks the scope from `generation_ready` until resolved with an explicit manifest correction entry.

---

## 13. Security & Compliance

### 13.1 Source Authenticity

- All DBE downloads must originate from `*.education.gov.za` or known official mirrors. URLs not matching this pattern require manual approval and a `non_standard_source` flag in the manifest.
- Canonically stored PDFs are immutable in the object store (`MFA Delete` or equivalent enabled).
- Object store access uses per-environment service principals with least-privilege IAM roles (read-only for CI, read-write for designated operator role only).

### 13.2 POPIA Compliance

- Source manifests and topic maps contain no learner PII. No compliance exposure at this layer.
- Reviewer metadata (`reviewer_id`) references internal staff IDs only; no external PII.

### 13.3 Secrets Management

- Object store credentials stored in GitHub Actions secrets / Azure Key Vault.
- No credentials in manifest JSON, topic map JSON, or any committed file.
- DBE download does not require authentication; no credentials required for Stage 2.

### 13.4 Access Control Matrix

| Role | Manifest (read) | Manifest (write) | Object Store (read) | Object Store (write) | Topic Map review |
|------|:-:|:-:|:-:|:-:|:-:|
| Developer | ✅ | ✅ (PR only) | ✅ | ❌ | ❌ |
| Curriculum Reviewer | ✅ | ✅ (review fields only) | ✅ | ❌ | ✅ |
| Platform Operator | ✅ | ✅ | ✅ | ✅ | ❌ |
| CI Service Account | ✅ | ❌ | ✅ (read) | ❌ | ❌ |

---

## 14. Test Plan

### 14.1 Unit Tests (`tests/curriculum/`)

| Test | Target | Expected |
|------|--------|----------|
| `test_manifest_rejects_missing_url` | Schema validator | ValidationError raised |
| `test_manifest_rejects_missing_hash_when_verified` | Schema validator | ValidationError raised |
| `test_manifest_rejects_duplicate_document_ids` | Source inventory | Exit 1 with duplicate report |
| `test_hash_mismatch_raises_error` | Download script | IntegrityError; file not accepted |
| `test_not_applicable_requires_evidence_notes` | Schema validator | ValidationError if evidence_notes empty |
| `test_planned_scope_is_not_generation_ready` | Readiness checker | `is_generation_ready = False` |
| `test_generation_ready_requires_reviewed_status` | Readiness checker | Only `topic_map_approved + approved` qualifies |
| `test_coding_robotics_not_applicable_records_accepted` | Schema validator | Valid if evidence_notes present |
| `test_multi_grade_split_produces_n_maps` | Extraction script | 3 files from IP Maths PDF |
| `test_language_subject_requires_strands` | Topic map validator | ValidationError if strands absent |
| `test_topic_requires_source_citation` | Topic map validator | ValidationError if citations empty |

### 14.2 Script / Integration Tests

| Test | Command | Pass Condition |
|------|---------|----------------|
| Dry-run inventory lists all R–7 scopes | `source_inventory.py --dry-run --report` | All expected scope IDs present in output |
| Download dry-run produces no side effects | `download_caps_sources.py --dry-run` | No files written, manifest unchanged |
| Hash verification is deterministic | Run `download_caps_sources.py` twice on same URL | SHA-256 identical across runs |
| Topic map validator rejects map without citations | `validate_topic_maps.py --scope-id {test_scope}` | Exit 1 |
| Topic map validator rejects map without reviewer metadata | Same as above | Exit 1 |
| Grade 4 Maths regression passes | `validate_topic_maps.py --scope-id grade4_mathematics_en` | Exit 0 |

### 14.3 End-to-End Validation Sequence

```bash
# Full validation sweep — run before any content generation sprint
python scripts/curriculum/validate_source_manifest.py --strict
python scripts/curriculum/validate_topic_maps.py --all --strict
python scripts/curriculum/report_content_coverage.py --strict-counts
```

All three must exit 0 before a content generation sprint may begin on any new scope.

### 14.4 Property-Based Tests (Hypothesis)

```python
# Example: any valid manifest roundtrips through JSON without data loss
@given(valid_manifest_strategy())
def test_manifest_roundtrip(manifest):
    serialised = json.dumps(manifest)
    assert json.loads(serialised) == manifest
```

---

## 15. Risk Register

| ID | Risk | Probability | Impact | Mitigation |
|----|------|:-----------:|:------:|------------|
| R-1 | DBE official URLs change or documents are removed from the web | Medium | High | Record `canonical_source_url` at download time; object store is the durable copy; manifest `superseded_by` chain tracks changes |
| R-2 | Coding & Robotics policy does not cover all grades R–7 | High | Medium | Record `not_applicable` with evidence; no fabricated coverage; revisit when DBE publishes grade-banded policy |
| R-3 | Sepedi FAL CAPS document not available in digital PDF form for some phases | Low | Medium | Record `not_applicable` with evidence; flag for manual digitisation if critical |
| R-4 | PDF text extraction quality insufficient for structured topic map generation | Medium | High | Use pdfminer as primary; fall back to Tesseract OCR; flag scopes requiring manual extraction |
| R-5 | Multi-grade PDFs use inconsistent section formatting across grades | Medium | Medium | Per-grade extraction with grade-specific section parsers; manual spot-check mandatory |
| R-6 | SHA-256 drift (object store mutation, upstream PDF silently updated) | Low | Critical | Weekly hash re-verification job; P1 alert on mismatch |
| R-7 | Reviewer bottleneck: all topic maps require human approval | High | Medium | Prioritise Gr 4 Maths first (existing launch validation); stagger review by phase |
| R-8 | Object store costs exceed budget for large PDF corpus | Low | Low | PDFs are at most a few hundred MB total; negligible cost |
| R-9 | CAPS 2011 documents have since been amended/supplemented by ATPs | High | High | Cross-check with Annual Teaching Plans per subject; record ATP document_ids as supplementary sources |

---

## 16. Rollback & Recovery

### 16.1 Manifest Corruption Recovery

The manifest is a single versioned JSON file in git. Recovery procedure:

```bash
# Revert to last known good state
git log --oneline data/caps/source_documents/manifest.json   # identify last good commit
git checkout <commit_sha> -- data/caps/source_documents/manifest.json
git commit -m "fix: revert manifest to last known good state"
```

### 16.2 Object Store Overwrite Recovery

Object store keys use SHA-256-prefixed filenames; keys are never overwritten. If an incorrect file was uploaded under a new key, delete the erroneous key, remove the manifest `object_store_uri`, and re-run publish with the correct verified file.

### 16.3 Topic Map Regression Recovery

If a validated topic map is found to be incorrect post-review:

1. Set `review_status: rejected` in the map JSON.
2. Open a Curriculum Issue with the error description.
3. Source record reverts to `source_loaded` and the topic map `review_status` becomes `rejected` (enforced by validator).
4. Content generation for that scope is gated until re-review.
5. Do not delete the rejected file; append `.rejected.<timestamp>.json` suffix for audit trail.

---

## 17. Implementation Roadmap

Implementation must start by reconciling this document into code without breaking the already-pushed foundation branch:

1. Upgrade `app/domain/content_source.py` only as needed to support v2 metadata while preserving current validators.
2. Add Coding and Robotics planned scopes/source records.
3. Add source inventory and topic-map validators before download/upload automation.
4. Keep Grade 4 Maths launch validation green after every step.


| Phase | Milestone | Duration | Owner |
|-------|-----------|----------|-------|
| **M-1** | Source inventory complete — all scopes have manifest records with URLs or `not_applicable` evidence | 1 week | Curriculum + Engineering |
| **M-2** | All Foundation Phase sources downloaded, hashed, uploaded | 1 week | Platform Operator |
| **M-3** | Foundation Phase topic maps extracted (draft) | 1 week | Engineering |
| **M-4** | Foundation Phase topic maps reviewed and approved | 2 weeks | Curriculum Reviewer |
| **M-5** | Intermediate Phase sources downloaded, hashed, uploaded | 1 week | Platform Operator |
| **M-6** | Intermediate Phase topic maps extracted + reviewed | 3 weeks | Engineering + Curriculum |
| **M-7** | Senior Phase (Gr 7) sources + topic maps complete | 2 weeks | Engineering + Curriculum |
| **M-8** | Full end-to-end validation sweep passes; all non–`not_applicable` scopes are `generation_ready` | 1 week | Engineering |
| **M-9** | CI gates active on all CAPS manifest and topic-map PRs | During M-1 | DevOps |

> **Critical path:** M-9 (CI gates) should be active from the start to prevent unvalidated manifest changes from entering main. It is a prerequisite enabler, not a trailing deliverable.

---

## 18. Assumptions & Constraints

| # | Assumption / Constraint |
|---|------------------------|
| A-1 | "Spedi" in the original plan means **Sepedi** (Sesotho sa Leboa, ISO 639-3: `nso`). All scope IDs, manifest fields, and file paths normalise to `sepedi` / `nso`. |
| A-2 | Source PDFs are stored in an object store external to git. Git commits only manifest metadata and topic map JSON. |
| A-3 | Official DBE/CAPS documents (2011 CAPS policy documents) are the primary source of truth. Annual Teaching Plans (ATPs) are supplementary. Third-party sources inform review notes only and do not determine topic maps. |
| A-4 | Coding and Robotics (DBE 2021 policy) may not cover all grades R–7 in the same format as 2011 CAPS subjects. Uncovered grades are recorded as `not_applicable` with evidence rather than fabricated. |
| A-5 | Topic-map extraction is semi-automated. `topic_map_approved` status requires explicit human/educator approval metadata; automation alone cannot advance a scope to `generation_ready`. |
| A-6 | The object store supports content-addressed storage (identical SHA-256 → skip re-upload). |
| A-7 | The project runs on a single Azure/AWS environment with infrastructure already provisioned. Object store container/bucket names are provided via environment variables, not hardcoded. |
| A-8 | Grade R mathematics and Life Skills content follows the 2011 CAPS Foundation Phase document, not a separate Grade R-specific document. |

---

## Appendix A — Manifest JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://eduboost.co.za/schemas/caps_source_manifest_v2.json",
  "title": "CAPS Source Manifest",
  "type": "object",
  "required": ["schema_version", "documents"],
  "properties": {
    "schema_version": { "type": "string", "const": "1.0" },
    "generated_at":   { "type": "string", "format": "date-time" },
    "documents": {
      "type": "array",
      "items": { "$ref": "#/$defs/SourceRecord" },
      "uniqueItems": true
    }
  },
  "$defs": {
    "SourceRecord": {
      "type": "object",
      "required": ["document_id", "phase", "applicable_grades",
                   "applicable_subjects", "language_role", "language_code",
                   "source_status", "review_status"],
      "properties": {
        "document_id":          { "type": "string", "pattern": "^[a-z0-9_]+$" },
        "phase":                { "enum": ["foundation","intermediate","senior"] },
        "applicable_grades":    { "type": "array", "items": { "type": "string" } },
        "applicable_subjects":  { "type": "array", "items": { "type": "string" } },
        "language_role":        { "enum": ["home_language","first_additional_language","content_subject"] },
        "language_code":        { "type": "string" },
        "source_status":        { "enum": ["planned","source_loaded","topic_map_approved","retired","not_applicable"] },
        "canonical_source_url": { "type": "string", "format": "uri" },
        "object_store_uri":     { "type": "string" },
        "source_sha256":        { "type": "string", "pattern": "^[a-f0-9]{64}$" },
        "downloaded_at":        { "type": "string", "format": "date-time" },
        "published_at":         { "type": "string", "format": "date-time" },
        "topic_map_paths":      { "type": "array", "items": { "type": "string" } },
        "evidence_notes":       { "type": "string" },
        "superseded_by":        { "type": "string" },
        "review_status":        { "enum": ["pending","approved","rejected","not_applicable"] },
        "reviewed_at":          { "type": "string", "format": "date-time" },
        "reviewer_id":          { "type": "string" },
        "review_notes":         { "type": "string" }
      },
      "if":   { "properties": { "source_status": { "const": "not_applicable" } } },
      "then": { "required": ["evidence_notes"] }
    }
  }
}
```

---

## Appendix B — Topic Map JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://eduboost.co.za/schemas/caps_topic_map_v2.json",
  "title": "CAPS Topic Map",
  "type": "object",
  "required": ["scope_id","document_id","grade","phase","subject_slug",
               "language_role","language_code","caps_version","review_status","terms"],
  "properties": {
    "scope_id":           { "type": "string", "pattern": "^[a-z0-9_]+$" },
    "document_id":        { "type": "string" },
    "grade":              { "type": "string", "enum": ["R","1","2","3","4","5","6","7"] },
    "phase":              { "type": "string" },
    "subject_slug":       { "type": "string" },
    "language_role":      { "type": "string" },
    "language_code":      { "type": "string" },
    "caps_version":       { "type": "string" },
    "extraction_method":  { "type": "string" },
    "extracted_at":       { "type": "string", "format": "date-time" },
    "review_status":      { "enum": ["pending","approved","rejected"] },
    "reviewed_at":        { "type": ["string","null"], "format": "date-time" },
    "reviewer_id":        { "type": ["string","null"] },
    "review_notes":       { "type": ["string","null"] },
    "terms": {
      "type": "array",
      "minItems": 1,
      "items": { "$ref": "#/$defs/Term" }
    },
    "strands":  { "$ref": "#/$defs/Strands" },
    "meta":     { "$ref": "#/$defs/Meta" }
  },
  "$defs": {
    "Term": {
      "type": "object",
      "required": ["term_number","topics"],
      "properties": {
        "term_number": { "type": "integer", "minimum": 1, "maximum": 4 },
        "weeks":       { "type": "string" },
        "topics":      { "type": "array", "items": { "$ref": "#/$defs/Topic" } }
      }
    },
    "Topic": {
      "type": "object",
      "required": ["topic_id","heading","source_citations"],
      "properties": {
        "topic_id":             { "type": "string" },
        "heading":              { "type": "string" },
        "subtopics":            { "type": "array", "items": { "type": "string" } },
        "assessment_standards": { "type": "array", "items": { "type": "string" } },
        "source_citations": {
          "type": "array",
          "minItems": 1,
          "items": { "$ref": "#/$defs/Citation" }
        },
        "prerequisites":  { "type": "array", "items": { "type": "string" } },
        "vocabulary":     { "type": "array", "items": { "type": "string" } },
        "misconceptions": { "type": "array", "items": { "type": "string" } }
      }
    },
    "Citation": {
      "type": "object",
      "required": ["document_id","page_number","section_heading"],
      "properties": {
        "document_id":     { "type": "string" },
        "page_number":     { "type": "integer", "minimum": 1 },
        "section_heading": { "type": "string" }
      }
    },
    "Strands": {
      "type": "object",
      "properties": {
        "reading":       { "type": "array", "items": { "type": "string" } },
        "writing":       { "type": "array", "items": { "type": "string" } },
        "grammar":       { "type": "array", "items": { "type": "string" } },
        "oral":          { "type": "array", "items": { "type": "string" } },
        "comprehension": { "type": "array", "items": { "type": "string" } }
      }
    },
    "Meta": {
      "type": "object",
      "properties": {
        "total_topics":               { "type": "integer" },
        "total_assessment_standards": { "type": "integer" },
        "coverage_completeness":      { "type": "number", "minimum": 0, "maximum": 1 }
      }
    }
  }
}
```

---

## Appendix C — Scope ID Convention

The current repo scope IDs remain authoritative. Do not migrate existing IDs to the earlier phase-code convention. New scopes should use the same readable pattern and add metadata fields for phase/language role.

```
{grade_label}_{subject_slug}_{content_language}

Grade labels:
  grader = Grade R
  grade1..grade7 = Grades 1..7

Examples:
  grader_mathematics_en
  grade1_home_language_en
  grade4_mathematics_en
  grade5_natural_sciences_and_technology_en
  grade7_economic_management_sciences_en
  grade7_coding_and_robotics_en
```

Language-role subjects should be represented explicitly in `subject_code`, `subject`, and manifest metadata:

| Learning area | Scope subject naming | Language metadata |
|---------------|----------------------|-------------------|
| English Home Language | `home_language` / `Home Language` | `language_role=home_language`, `language_code=eng` |
| Sepedi First Additional Language | `sepedi_first_additional_language` / `Sepedi First Additional Language` | `language_role=first_additional_language`, `language_code=nso` |
| Content subjects | Subject slug, for example `mathematics` | `language_role=content_subject`, `language_code=eng` |

## Implementation Update — 2026-06-03

All registered Grade R-7 scopes now have runtime topic maps, reviewed draft envelopes, CAPS refs, coverage targets, and topic_map_approved source provenance. Grade 4 Mathematics remains the only active learner-visible launch scope; the other 50 scopes are in review status and are generation-ready without being learner-visible. The remaining topic-map extraction gap is 0 scopes.

## Appendix D — Official DBE Source Catalogue

Primary access point: https://www.education.gov.za/Curriculum/CurriculumAssessmentPolicyStatements(CAPS).aspx

The `source_inventory.py` script should resolve exact PDF URLs from this page during the M-1 milestone. URL resolution findings are to be recorded in the manifest `canonical_source_url` field and cross-checked against the `evidence_notes` of any `not_applicable` records.

> **Note on Annual Teaching Plans (ATPs):** CAPS policy documents define the curriculum scope; ATPs define the week-by-week pacing. Both should be downloaded as separate `document_id` entries with `applicable_subjects` reflecting their scope. ATPs are supplementary and do not replace CAPS policy as the source of truth for topic maps, but they are valuable for populating `terms[].weeks` fields accurately.

---

*End of document. All sections subject to peer review prior to implementation commencement.*
