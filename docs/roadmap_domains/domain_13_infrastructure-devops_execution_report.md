    # Domain 13: Infrastructure & DevOps execution report

    Source roadmap: `temp/md/06_infrastructure_devops_roadmap.md`  
    Roadmap label: Domain 13 of 14  
    Branch: `roadmap/domain-13-infrastructure-devops`  
    Base: `origin/master`

    ## Roadmap size

    - Total tasks: 24
    - Priority breakdown: 8 P0 · 8 P1 · 6 P2 · 2 P3

    ## Task identifiers captured from the roadmap

    INF-01, INF-04, OBS-13, QA-09, QA-06, INF-05, INF-02, INF-03, INF-06, INF-07, INF-08, INF-09, OBS-04, INF-10, INF-11, INF-12, INF-13, LEGAL-08

    ## Repository-side evidence gate

    This branch follows the same processing logic used for the previous domain
    roadmaps: it adds a domain execution report, a repo-side evidence checker,
    and a Makefile target. The checker verifies repository artifacts that can be
    validated from git and lists remaining repo or external gates separately.

    Run:

    ```bash
    python scripts/check_domain_13_infrastructure_devops_evidence.py
    ```

    Evidence artifacts checked by the gate:

    - `bicep`
- `k8s`
- `docker`
- `docker-compose.prod.yml`
- `deployment`
- `scripts/staging_smoke.py`
- `scripts/validate_ops_assets.py`
- `scripts/build_release_evidence.py`
- `scripts/check_staging_release_gate.py`
- `scripts/check_release_evidence_artifacts.py`
- `docs/operations`
- `docs/release`
- `.github/workflows/cluster-d-ci.yml`
- `.github/workflows/release.yml`
- `Makefile`

    ## Repo-side gaps still tracked from roadmap scope

    - `Dockerfile`
- `docs/staging`

    ## External or human gates not claimable from git

    - Green GitHub Actions status must be verified on GitHub after push.
- Production/staging/cloud evidence cannot be produced from repository files alone.
- Human owner, legal/privacy, security, curriculum, accessibility, and release approvals cannot be supplied by an agent.
- Azure resources, Key Vault secrets, staging smoke evidence, backup/restore drills, and image scans require cloud access.

    ## Claim discipline

    This branch verifies repository artifacts only. Full roadmap completion still
    requires green CI for the branch and closure of external/human gates. Do not
    mark this domain production-ready from this branch alone.
