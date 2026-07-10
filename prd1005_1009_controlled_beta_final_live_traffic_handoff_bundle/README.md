# PRD-10.5-10.9 controlled beta final live-traffic handoff bundle

This bundle closes PRD-10 after the PRD-10.0-10.4 preflight foundation is merged and evidenced.
It records the limited controlled-beta live learner traffic authorisation decision while keeping public beta,
production release, deployment, billing launch, and live payment processing locked.

Apply:

```bash
bash prd1005_1009_controlled_beta_final_live_traffic_handoff_bundle/apply_prd1005_1009_controlled_beta_final_live_traffic_handoff.sh .
```

Authority verification:

```bash
PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd1005_1009_controlled_beta_final_live_traffic_handoff.py --authority-only --json
```

Evidence capture after authority PR lands:

```bash
PYTHONPATH=. python3 scripts/roadmap_reconciliation/capture_prd1005_1009_controlled_beta_final_live_traffic_handoff_evidence.py   --claim-prd1005-1009-controlled-beta-final-live-traffic-handoff   --prd-owner "Nkgolo Lebelo"   --target-branch master   --require-valid   --json
```
