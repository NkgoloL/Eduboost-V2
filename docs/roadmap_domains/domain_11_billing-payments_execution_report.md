    # Domain 11: Billing & Payments execution report

    Source roadmap: `temp/md/04_billing_payments_roadmap.md`  
    Roadmap label: Domain 11 of 14  
    Branch: `roadmap/domain-11-billing-payments`  
    Base: `origin/master`

    ## Roadmap size

    - Total tasks: 22
    - Priority breakdown: 6 P0 · 10 P1 · 4 P2 · 2 P3

    ## Task identifiers captured from the roadmap

    BILL-01, BILL-02, BILL-03, BILL-04, BILL-05, BILL-06, BILL-07, BILL-02a, BILL-02b, BILL-02c, BILL-03a, BILL-03b, BILL-03c, BILL-03d, BILL-04a, BILL-04b, BILL-04c, BILL-04d, BILL-04e, BILL-06a, BILL-06b, BILL-06c, BILL-07a, FE-14, BILL-07b, BILL-07c, BILL-07d, BILL-07e

    ## Repository-side evidence gate

    This branch follows the same processing logic used for the previous domain
    roadmaps: it adds a domain execution report, a repo-side evidence checker,
    and a Makefile target. The checker verifies repository artifacts that can be
    validated from git and lists remaining repo or external gates separately.

    Run:

    ```bash
    python scripts/check_domain_11_billing_payments_evidence.py
    ```

    Evidence artifacts checked by the gate:

    - `app/api_v2_routers/billing.py`
- `docs/adr`
- `Makefile`

    ## Repo-side gaps still tracked from roadmap scope

    - `app/modules/billing`
- `app/services/billing`
- `docs/billing_policy.md`
- `app/frontend/src/app/billing`
- `tests/unit/modules/billing`
- `tests/integration/test_billing_webhooks.py`
- `scripts/check_billing_evidence.py`

    ## External or human gates not claimable from git

    - Green GitHub Actions status must be verified on GitHub after push.
- Production/staging/cloud evidence cannot be produced from repository files alone.
- Human owner, legal/privacy, security, curriculum, accessibility, and release approvals cannot be supplied by an agent.
- Billing provider selection, sandbox credentials, webhook secrets, and payment-provider dashboard validation require human/provider access.

    ## Claim discipline

    This branch verifies repository artifacts only. Full roadmap completion still
    requires green CI for the branch and closure of external/human gates. Do not
    mark this domain production-ready from this branch alone.
