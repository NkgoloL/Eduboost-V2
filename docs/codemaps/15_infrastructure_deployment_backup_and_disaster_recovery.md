# EduBoost V2 Infrastructure, Deployment, Backup, and Disaster Recovery

Maps container images, Compose topology, reverse proxying, Kubernetes deployment, secrets, readiness, backups, restore drills, and operational recovery.

## Scope and ownership

This codemap is the primary architecture owner for:
- `docker`
- `docker-compose*.yml`
- `nginx`
- `k8s`
- `deployment`
- `scripts/*backup*`
- `app/modules/deployment`
- `app/modules/disaster_recovery`

It describes current implementation paths in repository-relative form. Related cross-cutting behaviour may be referenced from other codemaps, but every maintained source file has one primary owner in `codemap_coverage_manifest.json`.

## Architectural position

This area participates in the wider EduBoost request, data, evidence, and release architecture. Read it together with `00_application_bootstrap_and_request_lifecycle.md`, `17_testing_ci_coverage_security_and_quality_gates.md`, and `18_production_readiness_release_evidence_and_live_traffic.md` when changing runtime or release-critical behaviour.

## Trace ID: 1
**Title:** Container build, local/production topology, and reverse proxy

**Description:** Follows source and dependencies into backend, frontend, and inference images and the production service topology.

**Motivation:**
Reproducible images and explicit service wiring are the deployment unit for runtime evidence.

**Details:**

**Execution path**

1. Build pinned backend and frontend images.
2. Install runtime-only dependencies and non-root execution.
3. Compose API, frontend, database, Redis, proxy, and supporting services.
4. Inject environment and secret references.
5. Route public traffic through the reverse proxy.
6. Run container health and startup checks.

**State and ownership boundaries**

Images are immutable artefacts; environment configuration and secrets are deployment-time state.

**Failure, privacy, and control points**

Build contexts exclude secrets, containers run least-privileged, proxy limits are explicit, and production does not enable test stubs.

**Verification signals**

Build all production Dockerfiles, validate Compose config, and run disposable stack startup and smoke tests.

**Trace text diagram:**
```text
1. Build pinned backend and frontend images [1a]
   |
   v
2. Install runtime-only dependencies and non-root execution [1b]
   |
   v
3. Compose API, frontend, database, Redis, proxy, and supporting services [1c]
   |
   v
4. Inject environment and secret references [1d]
   |
   v
5. Route public traffic through the reverse proxy [1d]
   |
   v
6. Run container health and startup checks [1d]
```

**Location ID: 1a**
- **Title:** API image
- **Description:** Backend container build.
- **Path:LineNumber:** docker/Dockerfile.api:1

**Location ID: 1b**
- **Title:** Frontend image
- **Description:** Next.js container build.
- **Path:LineNumber:** docker/Dockerfile.frontend:2

**Location ID: 1c**
- **Title:** Production Compose
- **Description:** Service topology and dependencies.
- **Path:LineNumber:** docker-compose.prod.yml:5

**Location ID: 1d**
- **Title:** Production Nginx
- **Description:** External routing and proxy controls.
- **Path:LineNumber:** docker/nginx.prod.conf:38

### AI Guide: Container build, local/production topology, and reverse proxy

**Motivation:**
Reproducible images and explicit service wiring are the deployment unit for runtime evidence.

**Details:**

**Reasoning through the execution path.** Start at [1a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [1a] anchors api image. [1b] anchors frontend image. [1c] anchors production compose. [1d] anchors production nginx.

**Safe change boundary.** Images are immutable artefacts; environment configuration and secrets are deployment-time state. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Build contexts exclude secrets, containers run least-privileged, proxy limits are explicit, and production does not enable test stubs.

**How to verify the change.** Build all production Dockerfiles, validate Compose config, and run disposable stack startup and smoke tests. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 2
**Title:** Kubernetes rollout, readiness, staging, and secret controls

**Description:** Maps deployment specifications through rollout, probe evaluation, monitoring, and staging acceptance.

**Motivation:**
Orchestration must route traffic only after schema, dependency, and application readiness are truthful.

**Details:**

**Execution path**

1. Apply deployment, service, config, and secret references.
2. Start pods with resource and security contexts.
3. Run liveness and readiness probes.
4. Scrape metrics and evaluate alerts.
5. Perform staging smoke and acceptance checks.
6. Promote, pause, or roll back the rollout.

**State and ownership boundaries**

Deployment manifests describe desired state; release evidence records the observed rollout and checks.

**Failure, privacy, and control points**

Secrets are referenced rather than committed, probes match runtime contracts, rollouts are bounded, and rollback remains available.

**Verification signals**

Validate manifests, run ready-probe contracts, staging smoke, secret placeholder, and deployment readiness checks.

**Trace text diagram:**
```text
1. Apply deployment, service, config, and secret references [2a]
   |
   v
2. Start pods with resource and security contexts [2b]
   |
   v
3. Run liveness and readiness probes [2c]
   |
   v
4. Scrape metrics and evaluate alerts [2d]
   |
   v
5. Perform staging smoke and acceptance checks [2d]
   |
   v
6. Promote, pause, or roll back the rollout [2d]
```

**Location ID: 2a**
- **Title:** API deployment
- **Description:** Kubernetes workload definition.
- **Path:LineNumber:** k8s/api-deployment.yml:4

**Location ID: 2b**
- **Title:** Readiness probe
- **Description:** Traffic eligibility configuration.
- **Path:LineNumber:** deployment/k8s/ready_probe.yaml:2

**Location ID: 2c**
- **Title:** Secret rotation
- **Description:** Runtime secret lifecycle.
- **Path:LineNumber:** app/core/secret_rotation.py:12

**Location ID: 2d**
- **Title:** Staging smoke workflow
- **Description:** Post-deploy validation.
- **Path:LineNumber:** .github/workflows/staging-smoke.yml:1

### AI Guide: Kubernetes rollout, readiness, staging, and secret controls

**Motivation:**
Orchestration must route traffic only after schema, dependency, and application readiness are truthful.

**Details:**

**Reasoning through the execution path.** Start at [2a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [2a] anchors api deployment. [2b] anchors readiness probe. [2c] anchors secret rotation. [2d] anchors staging smoke workflow.

**Safe change boundary.** Deployment manifests describe desired state; release evidence records the observed rollout and checks. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Secrets are referenced rather than committed, probes match runtime contracts, rollouts are bounded, and rollback remains available.

**How to verify the change.** Validate manifests, run ready-probe contracts, staging smoke, secret placeholder, and deployment readiness checks. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Trace ID: 3
**Title:** Database backup, restore, rollback, and disaster recovery

**Description:** Shows scheduled backups, integrity manifests, restore exercises, rollback evidence, and recovery readiness.

**Motivation:**
Backups count only when they are complete, protected, and proven restorable within recovery objectives.

**Details:**

**Execution path**

1. Trigger scheduled or operator backup.
2. Create database dump and metadata manifest.
3. Encrypt or protect the artefact and enforce retention.
4. Verify checksum and backup completeness.
5. Restore into an isolated environment.
6. Run schema and application checks and record recovery evidence.

**State and ownership boundaries**

Backup artefacts, manifests, restore logs, and production data have separate access and retention rules.

**Failure, privacy, and control points**

Backups do not expose secrets, restore never targets production by default, failure alerts are actionable, and recovery evidence records RPO/RTO.

**Verification signals**

Run backup dry-run/matrix workflows, restore rollback evidence, disaster recovery contracts, and systemd timer validation.

**Trace text diagram:**
```text
1. Trigger scheduled or operator backup [3a]
   |
   v
2. Create database dump and metadata manifest [3b]
   |
   v
3. Encrypt or protect the artefact and enforce retention [3c]
   |
   v
4. Verify checksum and backup completeness [3d]
   |
   v
5. Restore into an isolated environment [3d]
   |
   v
6. Run schema and application checks and record recovery evidence [3d]
```

**Location ID: 3a**
- **Title:** Postgres backup
- **Description:** Database backup implementation.
- **Path:LineNumber:** scripts/backup_postgres.sh:5

**Location ID: 3b**
- **Title:** Backup schedule
- **Description:** Host-level backup timer.
- **Path:LineNumber:** deployment/systemd/db-backup.timer:5

**Location ID: 3c**
- **Title:** DR contracts
- **Description:** Recovery readiness requirements.
- **Path:LineNumber:** app/modules/disaster_recovery/production_readiness_contracts.py:17

**Location ID: 3d**
- **Title:** Restore evidence workflow
- **Description:** Hosted backup and rollback proof.
- **Path:LineNumber:** .github/workflows/db-backup-restore-rollback-evidence.yml:1

### AI Guide: Database backup, restore, rollback, and disaster recovery

**Motivation:**
Backups count only when they are complete, protected, and proven restorable within recovery objectives.

**Details:**

**Reasoning through the execution path.** Start at [3a] and follow the ordered state transition rather than jumping directly to a downstream repository or generated artefact. The trace is designed to show which layer owns transport, orchestration, persistence, and evidence. [3a] anchors postgres backup. [3b] anchors backup schedule. [3c] anchors dr contracts. [3d] anchors restore evidence workflow.

**Safe change boundary.** Backup artefacts, manifests, restore logs, and production data have separate access and retention rules. A change that moves responsibility across these boundaries should update the owning codemap, tests, and any affected ADR or release verifier in the same change.

**Controls to preserve.** Backups do not expose secrets, restore never targets production by default, failure alerts are actionable, and recovery evidence records RPO/RTO.

**How to verify the change.** Run backup dry-run/matrix workflows, restore rollback evidence, disaster recovery contracts, and systemd timer validation. Use the cited locations as navigation anchors, then inspect call sites and tests before modifying behaviour.

## Change checklist

- Update this codemap when an entry point, major dependency, persistence owner, or control flow changes.
- Keep all `Path:LineNumber` references repository-relative and line-valid.
- Update `codemap_coverage_manifest.json` when files move between architecture owners.
- Run `python scripts/maintenance/verify_codemaps.py --repo-root .` before merging.
