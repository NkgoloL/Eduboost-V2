# IRT Diagnostic Model

EduBoost diagnostics use a three-parameter logistic model for approved CAPS diagnostic items:

`P(correct | theta, a, b, c) = c + (1 - c) / (1 + exp(-a(theta - b)))`

Live-session parameter ranges are enforced before scoring:

- `theta`: finite and clamped to `[-4, 4]`
- `a` discrimination: `[0.5, 2.5]`
- `b` difficulty: `[-3.0, 3.0]`
- `c` guessing: `[0.0, 0.35]`

Item selection uses Maximum Fisher Information at the learner current theta. Sessions terminate when SE is at or below `0.40`, `15` items have been served, or fewer than `3` eligible items remain.

Session snapshots are persisted through `SessionRecoveryService` with a two-hour TTL so a learner can reconnect without losing theta, SE, served-item, or response state.

Calibration is conservative: after at least 100 responses, observed accuracy is used to propose updated IRT parameters and large difficulty shifts are flagged for human review.
