# Adverse Educational Consequence Monitoring & Mitigation Plan (LEV-WS11)

## 1. Scope & Objective
This plan establishes leading and lagging indicators, stop-work triggers, and teacher escalation pathways to detect and mitigate potential pedagogical and emotional harm in learners using EduBoost V2.

## 2. Leading Harm Indicators
1. **Rapid Guessing / Low Latency (< 1500ms)**: Indicates disengagement, frustration-driven clicking, or avoidance behaviour.
2. **Hint Exhaustion**: Repeatedly requesting all hints without successfully solving items signals instructional mismatch.
3. **Repeated Failure on Prerequisite Items**: Attempting advanced concepts while failing prerequisites triggers cognitive overload.
4. **Streak Breaking & Demotivation**: Severe drops in confidence following repeated unexpected incorrect answers.

## 3. Quantitative Thresholds & Stop-Work Triggers
- **Nominal State**: Frustration index $< 0.40$. Continue standard adaptive difficulty selection.
- **Elevated Warning**: Frustration index $\ge 0.40$ or 2 consecutive hint-exhaustion events. The system automatically reduces difficulty by 1 level and presents a worked example.
- **Critical Stop-Work**: $\ge 3$ consecutive struggle events or frustration index $\ge 0.75$.
  - Progression is locked immediately.
  - A friendly cooldown screen ("Time for a brain break!") is displayed.
  - A low-priority notification is dispatched to the educator portal for human teacher triage.

## 4. POPIA & Learner Well-Being Compliance
- Frustration telemetry is pseudonymized and stored in append-only tables (`lev_interaction_events`).
- No punitive tracking or negative reinforcement is ever presented to learners or guardians.
