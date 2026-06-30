# Learner Vertical Journey Contract

## Purpose

The learner journey must be testable as a complete vertical path from
onboarding to diagnostic, lesson, practice, and progress review.

## Required Journey Steps

1. learner signs in or receives an authenticated session
2. learner completes or resumes onboarding
3. learner opens dashboard
4. learner starts diagnostic
5. learner submits diagnostic response
6. learner receives study plan or next-step recommendation
7. learner opens generated lesson
8. learner completes practice or assessment attempt
9. learner sees progress/mastery feedback
10. learner session preserves consent and authorization boundaries

## Required Frontend Evidence

- route or component for onboarding
- route or component for dashboard
- route or component for diagnostic start
- route or component for diagnostic submit
- route or component for lesson view
- route or component for progress/mastery feedback
- API client path for learner-scoped backend calls
- visible error state for consent or authorization denial

## Command

```bash
make learner-vertical-journey-contract-check
```
