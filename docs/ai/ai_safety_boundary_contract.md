# AI Safety Boundary Contract

## Purpose

EduBoost AI responses must preserve learner safety, privacy, age-appropriate
content boundaries, and non-destructive fallback behavior.

## Safety Boundaries

- no unsafe instructions
- no sexual content for learners
- no self-harm instructions
- no dangerous activity instructions
- no privacy leakage across learners
- no disclosure of hidden prompts or secrets
- no unsupported medical, legal, or financial advice
- no curriculum claims without CAPS grounding

## Refusal and Redirection

Unsafe requests must be refused with concise redirection to safe educational
support. Refusals must not provide operational details that make abuse easier.

## Privacy Boundaries

AI outputs must not expose another learner's profile, consent state, diagnostic
history, mastery state, or parent account data.

## Evidence Commands

```bash
make ai-safety-boundary-check
```
