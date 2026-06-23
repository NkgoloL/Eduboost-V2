---
title: "ADR-008 — Voice Input (Web Speech API en-ZA)"
status: active
owner: frontend
reviewers: [frontend, architecture]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 180
evidence_command: make docs-housekeeping-stage3-check
code_anchors: []
---
# ADR-008 — Voice Input (Web Speech API en-ZA)

```text
Status: Draft (RC5 gate)
Date: 2026-05-28
Owner: Frontend Tech Lead
RC Gate: RC5
Blocks: FE-P2-082..085 · FE-PR-013 voice scope
Reviewers: POPIA Compliance Officer, Information Officer, Safety Lead
Evidence: FE-SPIKE-004 (pending), Phase 2 RC5 backlog items
```

## Context

RC5 differentiators include Grade R phonics with optional voice input. Learner privacy and accuracy for South African accents demand a conservative approach until FE-SPIKE-004 proves reliability on low-end Android devices.

## Decision

- Leverage the browser Web Speech API (`SpeechRecognition`) configured for `lang: 'en-ZA'`. No audio is sent to third-party services.
- Voice input is supplementary. The UI always offers tactile alternatives and never blocks lesson progression if the microphone is unavailable.
- Audio data is ephemeral: transcripts stay in-memory and are never stored in IndexedDB or sent to the backend without explicit guardian consent.
- Microphone permission prompts include POPIA disclaimers and link to guardian consent settings.

## Consequences

### Positive

- Avoids integrating third-party voice SDKs that may violate POPIA data locality requirements.
- Keeps the code path optional so RC2 learners are unaffected if RC5 slips.

### Negative

- Browser API accuracy may be insufficient in noisy classrooms; fallback UX must be stellar.
- Compatibility limited on iOS Safari; requires progressive enhancement checks.

## Implementation Notes

1. FE-SPIKE-004 must gather accuracy metrics across devices and accents.
2. Implement `useVoiceInput` hook with feature detection and `requestPermission()` flows.
3. Add automated accessibility tests to ensure microphone prompts have ARIA instructions.

## Compliance & Evidence

- Approval from POPIA officers needed before enabling by default.
- Synthetic data only in demos; no real learner audio captured during testing.
