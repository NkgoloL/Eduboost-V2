    # Domain 07: Diagnostics & Assessment execution report

    Source roadmap: `temp/roadmaps/Domain_07_Diagnostics_Assessment.docx`  
    Branch: `domain/07-diagnostics-assessment`  
    Base: `origin/master`

    ## Roadmap size

    | Metric | Count |
    |---|---:|
    | Domain Total Tasks | 26 |
| P0 Blockers | 10 |
| P1 Gates | 10 |
| P2 Hardening | 4 |
| P3 Optimisation | 2 |

    ## Task identifiers captured from the roadmap

    DIAG-01, DIAG-02, DIAG-05, DIAG-03, DIAG-04, DIAG-06, DIAG-07, DIAG-08, DIAG-09, DIAG-10, DIAG-11, DIAG-12, DIAG-13, FE-11

    ## Repository-side evidence gate

    This branch adds an executable evidence gate for the domain and records the
    repo-verifiable artifacts that map to the roadmap. Run:

    ```bash
    python scripts/check_domain_07_diagnostics_assessment_evidence.py
    ```

    Evidence artifacts checked by the gate:

    - `app/modules/diagnostics`
- `app/modules/progress`
- `app/modules/practice`
- `scripts/ci/check_diagnostics_assessment.py`
- `scripts/check_learning_evidence.py`
- `scripts/check_caps_learning_proof.py`
- `docs/caps`
- `tests/unit/modules/diagnostics`
- `tests/unit/modules/progress`
- `tests/unit/modules/practice`
- `.github/workflows/ci_diagnostics_assessment.yml`

    ## Repo-side gaps still tracked from roadmap scope

    - None detected by this branch checker.

    ## External or human gates not claimable from git

    - GitHub branch-protection / required-check UI settings require repository-admin access.
- Green GitHub Actions status must be verified on GitHub after push.
- Human owner, legal/privacy, security, curriculum, and release approvals cannot be supplied by an agent.
- Psychometric/curriculum review of diagnostics and item bias requires educator/human review.

    ## Claim discipline

    This branch verifies repository artifacts only. Full roadmap completion still
    requires green CI for the branch and closure of the external/human gates above.
    Do not mark this domain production-ready from this branch alone.
