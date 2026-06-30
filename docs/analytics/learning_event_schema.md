# POPIA-safe learning event schema

Learning analytics must avoid direct identifiers and negative learner labels.

## Event fields

| Field | Required | Notes |
|---|---:|---|
| pseudonymous_learner_id | Yes | Stable pseudonymous ID, not email/name/phone |
| topic_ref | Yes | CAPS reference or reviewed internal topic ref |
| activity_type | Yes | diagnostic, lesson, practice, review |
| timestamp | Yes | Server timestamp |
| correctness | Conditional | Boolean or score where educationally relevant |
| attempt_number | Conditional | Positive integer |
| time_spent_seconds | Conditional | Bounded integer |
| hint_used | Conditional | Boolean |
| confidence | Optional | Learner self-rating; never used as a negative label |

## Label policy

Use constructive labels: `ready_to_strengthen`, `needs_another_example`, `almost_mastered`, `ready_for_challenge`. Do not use labels such as weak learner, poor performer, or failing child.
