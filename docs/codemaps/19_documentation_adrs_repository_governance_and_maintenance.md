# EduBoost V2 Documentation, ADRs, Repository Governance, and Maintenance

Maps architecture authority, ADR lifecycle, documentation indexes, codemap governance, generated artefacts, housekeeping, repository hygiene, and contributor workflows.

## Scope and ownership

This codemap is the primary architecture owner for:
- `docs`
- `README.md`
- `CONTRIBUTING.md`
- `AGENT_INSTRUCTIONS_V2.md`
- `Makefile`
- `scripts/docs_inventory.py`
- `scripts/maintenance`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Architecture documentation index and ADR lifecycle

**Description:** Shows how architectural claims are proposed, decided, indexed, implemented, and verified against current code.

**Motivation:**
Architecture documents are useful only when readers can distinguish current authority, accepted decisions, superseded history, and future intent.

**Details:**

**Execution path**

1. Identify a material architecture decision or current-state change.
2. Create or update an ADR with status, context, decision, consequences, and scope.
3. Update the architecture documentation index and affected system documents.
4. Implement the decision in code and tests.
5. Add claim-to-source or verifier evidence.
6. Supersede stale documents without erasing history.

**State and ownership boundaries**

ADRs record decisions; current-state documents describe implemented architecture; roadmaps authorize future work.

**Failure, privacy, and control points**

Accepted decisions cannot remain contradicted by code, stale reports are quarantined, and proposed KG or production work is not presented as live prematurely.

**Verification signals**

Run ADR validation, documentation governance, current-state claim discipline, and stale-source quarantine checks.

**Trace text diagram:**
```text
1. Identify a material architecture decision or current-state change [1a]
   |
   v
2. Create or update an ADR with status, context, decision, consequences, and scope [1b]
   |
   v
3. Update the architecture documentation index and affected system documents [1c]
   |
   v
4. Implement the decision in code and tests [1d]
   |
   v
5. Add claim-to-source or verifier evidence [1d]
   |
   v
6. Supersede stale documents without erasing history [1d]
```

**Location ID: 1a**
- **Title:** Architecture index
- **Description:** Current architecture navigation authority.
- **Path:LineNumber:** docs/architecture/README.md:2

**Location ID: 1b**
- **Title:** ADR index
- **Description:** Architecture decision navigation.
- **Path:LineNumber:** docs/adr/README.md:2

**Location ID: 1c**
- **Title:** Claim discipline checker
- **Description:** Documentation-to-implementation validation.
- **Path:LineNumber:** scripts/check_documentation_adrs_claim_discipline_production_readiness.py:135

**Location ID: 1d**
- **Title:** Documentation governance workflow
- **Description:** Hosted documentation gate.
- **Path:LineNumber:** .github/workflows/documentation-governance.yml:1

### AI Guide: Architecture documentation index and ADR lifecycle

**Motivation:**
Architecture documents are useful only when readers can distinguish current authority, accepted decisions, superseded history, and future intent.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors architecture index. [1b] anchors adr index. [1c] anchors claim discipline checker. [1d] anchors documentation governance workflow.

**Safe change boundary.** ADRs record decisions; current-state documents describe implemented architecture; roadmaps authorize future work. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Accepted decisions cannot remain contradicted by code, stale reports are quarantined, and proposed KG or production work is not presented as live prematurely.

**How to verify the change.** Run ADR validation, documentation governance, current-state claim discipline, and stale-source quarantine checks. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Codemap suite, source coverage, and supersession

**Description:** Maps how application areas are assigned to canonical codemaps, how traces cite code, and how stale overlapping maps are retired.

**Motivation:**
Codemaps are operational architecture aids for humans and AI agents; duplication and stale absolute paths reduce trust.

**Details:**

**Execution path**

1. Inventory maintained application and operational files.
2. Assign each file to a primary canonical codemap owner.
3. Document source-backed execution traces with repository-relative line references.
4. Verify required sections, paths, line bounds, and zero unassigned files.
5. Publish a supersession map for legacy codemaps.
6. Update the suite whenever architecture ownership changes.

**State and ownership boundaries**

Codemaps are explanatory projections; source code, tests, ADRs, and release authority remain primary evidence.

**Failure, privacy, and control points**

References are repository-relative, each maintained file has one primary owner, overlap is declared, and generated manifests are reproducible.

**Verification signals**

Run `scripts/maintenance/verify_codemaps.py` and inspect the coverage report and supersession map.

**Trace text diagram:**
```text
1. Inventory maintained application and operational files [2a]
   |
   v
2. Assign each file to a primary canonical codemap owner [2b]
   |
   v
3. Document source-backed execution traces with repository-relative line references [2c]
   |
   v
4. Verify required sections, paths, line bounds, and zero unassigned files [2d]
   |
   v
5. Publish a supersession map for legacy codemaps [2d]
   |
   v
6. Update the suite whenever architecture ownership changes [2d]
```

**Location ID: 2a**
- **Title:** Codemap index
- **Description:** Canonical suite navigation and rules.
- **Path:LineNumber:** docs/codemaps/README.md:1

**Location ID: 2b**
- **Title:** Documentation inventory
- **Description:** Repository documentation discovery.
- **Path:LineNumber:** scripts/docs_inventory.py:422

**Location ID: 2c**
- **Title:** Docs housekeeping
- **Description:** Maintenance command integration.
- **Path:LineNumber:** scripts/maintenance/patch_makefile_docs_housekeeping.py:35

**Location ID: 2d**
- **Title:** Documentation targets
- **Description:** Contributor-facing documentation commands.
- **Path:LineNumber:** Makefile:6

### AI Guide: Codemap suite, source coverage, and supersession

**Motivation:**
Codemaps are operational architecture aids for humans and AI agents; duplication and stale absolute paths reduce trust.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors codemap index. [2b] anchors documentation inventory. [2c] anchors docs housekeeping. [2d] anchors documentation targets.

**Safe change boundary.** Codemaps are explanatory projections; source code, tests, ADRs, and release authority remain primary evidence. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** References are repository-relative, each maintained file has one primary owner, overlap is declared, and generated manifests are reproducible.

**How to verify the change.** Run `scripts/maintenance/verify_codemaps.py` and inspect the coverage report and supersession map. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Repository hygiene, generated artefacts, contribution, and maintenance

**Description:** Shows how contributors and automation keep source, generated files, local artefacts, branches, commands, and documentation consistent.

**Motivation:**
Repository quality depends on repeatable maintenance controls, especially in a large evidence-heavy codebase.

**Details:**

**Execution path**

1. Follow contributor and agent instructions from a clean branch.
2. Run canonical format, test, docs, generation, and verification commands.
3. Regenerate committed artefacts through their owning scripts.
4. Detect local, secret, archive, and stale generated files.
5. Review branch, release, and naming authority.
6. Commit bounded changes with evidence and keep master clean.

**State and ownership boundaries**

Generated artefacts have named producers; local caches, evidence scratch space, and secrets are not source authority.

**Failure, privacy, and control points**

Maintenance scripts are idempotent, generated drift fails checks, archives are deliberate, and no workflow command points to missing files.

**Verification signals**

Run repository hygiene, workflow command inventory, generated artefact canonicalization, docs housekeeping, and secret scans.

**Trace text diagram:**
```text
1. Follow contributor and agent instructions from a clean branch [3a]
   |
   v
2. Run canonical format, test, docs, generation, and verification commands [3b]
   |
   v
3. Regenerate committed artefacts through their owning scripts [3c]
   |
   v
4. Detect local, secret, archive, and stale generated files [3d]
   |
   v
5. Review branch, release, and naming authority [3d]
   |
   v
6. Commit bounded changes with evidence and keep master clean [3d]
```

**Location ID: 3a**
- **Title:** Contribution guide
- **Description:** Human development workflow.
- **Path:LineNumber:** CONTRIBUTING.md:1

**Location ID: 3b**
- **Title:** Agent instructions
- **Description:** Repository automation guardrails.
- **Path:LineNumber:** AGENT_INSTRUCTIONS_V2.md:1

**Location ID: 3c**
- **Title:** Workflow hygiene verifier
- **Description:** CI command consistency.
- **Path:LineNumber:** scripts/production_readiness/audit_prd006_workflow_command_hygiene_ci_inventory.py:199

**Location ID: 3d**
- **Title:** Repository hygiene verifier
- **Description:** Generated and local artefact control.
- **Path:LineNumber:** scripts/production_readiness/audit_prd009_repository_hygiene_generated_local_artifact_audit.py:357

### AI Guide: Repository hygiene, generated artefacts, contribution, and maintenance

**Motivation:**
Repository quality depends on repeatable maintenance controls, especially in a large evidence-heavy codebase.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors contribution guide. [3b] anchors agent instructions. [3c] anchors workflow hygiene verifier. [3d] anchors repository hygiene verifier.

**Safe change boundary.** Generated artefacts have named producers; local caches, evidence scratch space, and secrets are not source authority. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Maintenance scripts are idempotent, generated drift fails checks, archives are deliberate, and no workflow command points to missing files.

**How to verify the change.** Run repository hygiene, workflow command inventory, generated artefact canonicalization, docs housekeeping, and secret scans. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
