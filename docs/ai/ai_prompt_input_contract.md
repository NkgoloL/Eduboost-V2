# AI Prompt Input Contract

## Purpose

AI prompt construction must be bounded by explicit learner, curriculum, and
safety inputs. Prompt builders must not depend on hidden global state or expose
secrets.

## Required Prompt Inputs

- learner grade
- learner subject
- topic
- CAPS strand or skill
- learner mastery state
- diagnostic or lesson objective
- consent-authorized learner identifier
- safety boundary instructions

## Forbidden Prompt Inputs

- raw secrets
- API keys
- unrelated learner profiles
- another learner's diagnostic history
- hidden system prompts
- unbounded free-form parent or learner data

## Prompt Safety Rules

- prompts must preserve CAPS alignment
- prompts must include age-appropriate learner boundaries
- prompts must avoid cross-learner data leakage
- prompts must preserve refusal boundaries for unsafe requests
- prompts must not include credentials or infrastructure secrets

## Command

```bash
make ai-prompt-input-contract-check
```
