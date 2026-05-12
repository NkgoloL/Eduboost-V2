    # Domain 06: AI / LLM Pipeline execution report

    Source roadmap: `temp/roadmaps/Domain_06_AI_LLM_Pipeline.docx`  
    Branch: `domain/06-ai-llm-pipeline`  
    Base: `origin/master`

    ## Roadmap size

    | Metric | Count |
    |---|---:|
    | Domain Total Tasks | 37 |
| P0 Blockers | 16 |
| P1 Gates | 12 |
| P2 Hardening | 6 |
| P3 Optimisation | 3 |

    ## Task identifiers captured from the roadmap

    AI-01, AI-02, AI-03, AI-06, AI-07, AI-08, AI-10, AI-11, AI-12, AI-13, AI-14, AI-18, AI-19, AI-20, AI-23, AI-04, AI-05, AI-09, AI-15, AI-16, AI-17, AI-21, AI-22, AI-24

    ## Repository-side evidence gate

    This branch adds an executable evidence gate for the domain and records the
    repo-verifiable artifacts that map to the roadmap. Run:

    ```bash
    python scripts/check_domain_06_ai_llm_pipeline_evidence.py
    ```

    Evidence artifacts checked by the gate:

    - `scripts/popia_sweep.py`
- `scripts/check_ai_safety_boundary_contract.py`
- `scripts/check_ai_output_schema_contract.py`
- `scripts/validate_ai_output_fixtures.py`
- `docs/ai`
- `docs/llm`
- `.github/workflows/cluster-f-ai-safety.yml`

    ## Repo-side gaps still tracked from roadmap scope

    - `app/services/llm`
- `app/services/content_safety`

    ## External or human gates not claimable from git

    - GitHub branch-protection / required-check UI settings require repository-admin access.
- Green GitHub Actions status must be verified on GitHub after push.
- Human owner, legal/privacy, security, curriculum, and release approvals cannot be supplied by an agent.
- GPU provisioning/model registry/fine-tuning completion require cloud/model-registry access and human AI-safety review.

    ## Claim discipline

    This branch verifies repository artifacts only. Full roadmap completion still
    requires green CI for the branch and closure of the external/human gates above.
    Do not mark this domain production-ready from this branch alone.
