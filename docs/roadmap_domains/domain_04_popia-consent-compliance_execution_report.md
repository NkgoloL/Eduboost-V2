    # Domain 04: POPIA, Consent & Compliance execution report

    Source roadmap: `temp/roadmaps/Domain_04_POPIA_Consent_Compliance.docx`  
    Branch: `domain/04-popia-consent-compliance`  
    Base: `origin/master`

    ## Roadmap size

    | Metric | Count |
    |---|---:|
    | Domain Total Tasks | 40 |
| P0 Blockers | 20 |
| P1 Gates | 14 |
| P2 Hardening | 4 |
| P3 Optimisation | 2 |

    ## Task identifiers captured from the roadmap

    POP-01, POP-09, POP-02, POP-04, POP-05, POP-06, POP-07, POP-08, POP-10, POP-13, POP-11, POP-12, POP-17, POP-21, POP-18, POP-19, POP-20, LEGAL-01, LEGAL-05, LEGAL-02, LEGAL-03, LEGAL-04, POP-03, POP-14, POP-15, POP-16, LEGAL-06, LEGAL-07, LEGAL-08, CI-06

    ## Repository-side evidence gate

    This branch adds an executable evidence gate for the domain and records the
    repo-verifiable artifacts that map to the roadmap. Run:

    ```bash
    python scripts/check_domain_04_popia_consent_compliance_evidence.py
    ```

    Evidence artifacts checked by the gate:

    - `docs/security/popia_consent_boundary_matrix.md`
- `scripts/popia_sweep.py`
- `scripts/check_popia_legal_evidence.py`
- `.github/workflows/popia-consent-audit.yml`
- `docs/POPIA_COMPLIANCE.md`
- `docs/data_inventory.md`

    ## Repo-side gaps still tracked from roadmap scope

    - `app/modules/popia`
- `app/services/popia`
- `docs/security/popia_consent_audit_evidence.md`
- `docs/security/popia_legal_evidence.md`

    ## External or human gates not claimable from git

    - GitHub branch-protection / required-check UI settings require repository-admin access.
- Green GitHub Actions status must be verified on GitHub after push.
- Human owner, legal/privacy, security, curriculum, and release approvals cannot be supplied by an agent.
- POPIA legal review and guardian-facing notice approval require human legal authority.

    ## Claim discipline

    This branch verifies repository artifacts only. Full roadmap completion still
    requires green CI for the branch and closure of the external/human gates above.
    Do not mark this domain production-ready from this branch alone.
