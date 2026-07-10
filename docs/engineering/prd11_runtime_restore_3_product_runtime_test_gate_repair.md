# PRD-11.0R.RUNTIME-RESTORE-3 — Product and Runtime Test Gate Repair

This slice installs the behavioural product/runtime gate contract needed after
the test-suite, script-suite and coverage taxonomy work.

It preserves the operational hold:

```json
{
  "controlled_beta_activation_operational_hold": true,
  "live_learner_traffic_operationally_safe": false,
  "production_release_authorised": false,
  "deployment_authorised": false,
  "release_tag_authorised": false
}
```

## Controls installed

- Product/runtime domains are release-blocking.
- Every product/runtime domain requires independent command output.
- Positive and negative paths are required.
- Presence-only checks are forbidden as release evidence.
- Governance/evidence records cannot substitute for product/runtime proof.
- Product/runtime gate evidence is captured separately from PRD status records.

## Handoff

After evidence capture, the next authorised item is `PRD-11.0R.RUNTIME-RESTORE-4`. The runtime
baseline remains red until the actual stack and product/runtime command outputs
prove otherwise.
