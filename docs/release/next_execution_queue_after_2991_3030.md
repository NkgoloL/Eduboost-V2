# Next Execution Queue After AUDIT-BASELINE-REFRESH / code_2991_3030

## Recommended next batch

Choose the next batch based on the refreshed blocker list:

1. `APPROVALS-001R / code_3031_3070` — attach Legal/POPIA, Security, Curriculum/Content, and staging acceptance approval metadata.
2. `JWT-001R / code_3031_3070` — attach production/staging secret provisioning, fallback-disabled proof, rotation notes, and verifier metadata.
3. `ARQ-001R / code_3031_3070` — run live Redis worker enqueue/dequeue staging proof.
4. `DIAG-SCORE-001R / code_3031_3070` — resolve diagnostic item-bank/scoring audit proof.
5. `FRONTEND-RUNTIME-001R / code_3031_3070` — fix frontend type-check/build and deploy browser smoke proof.

## Required discipline

Do not close any remaining blocker from the baseline refresh alone. Every blocker still requires its own evidence gate.
