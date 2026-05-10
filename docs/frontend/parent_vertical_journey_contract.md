# Parent Vertical Journey Contract

## Purpose

The parent journey must be testable as a complete vertical path from
authenticated parent session to learner progress, trust, consent, export, and
support actions.

## Required Journey Steps

1. parent signs in or receives an authenticated session
2. parent opens parent dashboard
3. parent selects linked learner
4. parent views learner progress/mastery
5. parent views consent status and trust dashboard
6. parent can grant or revoke consent where authorized
7. parent can request learner data export where authorized
8. parent can start data-rights request where authorized
9. parent sees clear error state for authorization denial
10. parent session does not expose unrelated learner data

## Required Frontend Evidence

- route or component for parent dashboard
- route or component for linked learner selector
- route or component for learner progress/mastery
- route or component for consent status
- route or component for trust dashboard
- route or component for data export/data-rights request
- API client path for parent-scoped backend calls
- visible error state for authorization denial
- visible error state for consent denial or expired consent

## Command

```bash
make parent-vertical-journey-contract-check
```
