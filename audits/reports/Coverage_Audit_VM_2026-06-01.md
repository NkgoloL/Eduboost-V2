# Coverage and Readiness Audit (VM Repo)

Date: 2026-06-01
Repo: /home/azureuser/Dev/Eduboost-V2
Branch state: dirty (165 modified files)

## Snapshot

- Measured backend line coverage from coverage.xml: 67.02% (15298/22827)
- Measured branch coverage from coverage.xml: 0.00% (0/0)
- Pytest local gate in pytest.ini: --cov-fail-under=80
- CI workflow gate in .github/workflows/ci-cd.yml: COVERAGE_THRESHOLD=60

## High-Confidence Findings

1. Coverage improved versus older baseline docs, but still below production target.
- Current measured line coverage is 67.02%.
- This is below the 80% production-grade target.

2. Coverage governance is inconsistent.
- pytest.ini enforces 80%.
- ci-cd workflow still enforces 60%.
- This creates policy drift and false confidence risk.

3. Branch coverage is effectively not being measured.
- coverage.xml reports branches-valid=0.
- This means decision-path risk is unquantified.

4. Worktree is dominated by generated release/audit docs.
- 165 modified files, most under docs/release and docs/architecture.
- High noise can mask true code/test changes and make review reliability lower.

5. Large untested zones remain despite active coverage work.
- Several substantial modules are at 0% (examples from coverage.xml extraction):
  - services/etl/etl_pipeline.py
  - services/etl/etl_pipeline_v2.py
  - services/etl/etl_pipeline_v3_additions.py
  - modules/lessons/llm_gateway_v2.py
  - api_v2_routers/test_services.py and other legacy/slice files

## Key Risks

- Release risk: CI can pass at 60% while local policy expects 80%.
- Regression risk: branch behavior is not covered by branch metrics.
- Traceability risk: high documentation churn obscures true engineering progress.

## Recommended Sprint Priorities

1. Unify coverage policy now.
- Set one threshold target across pytest.ini and CI workflow.
- If 80% is immediate target, update ci-cd COVERAGE_THRESHOLD from 60 to 80.

2. Turn on meaningful branch coverage reporting.
- Ensure branch tracking is enabled and consumed in CI artifacts.
- Block on non-zero branch metrics for core packages.

3. Focus test investment on highest-yield low-coverage modules.
- Start with ETL pipelines, LLM gateway v2, and POPIA/security-adjacent services.
- Add module-level minimum gates for critical packages.

4. Reduce evidence noise in commits.
- Separate generated docs/evidence commits from code/test commits.
- Add clear ownership and generation cadence for docs/release artifacts.

5. Produce a truthful coverage trajectory.
- Weekly report: current %, delta, top 20 uncovered files, and planned additions.

## Conclusion

This repo shows significant effort and real progress on coverage infrastructure and evidence generation. It is not yet production-grade against an 80% backend coverage bar. Primary blockers are threshold inconsistency (60 vs 80), absent branch coverage signal, and remaining large 0%-covered modules.
