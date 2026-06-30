# FE-PR-013 Safety and Compliance Boundary

## Purpose

Define the hard boundary for FE-PR-013 so the implementation remains safe, compliant, and clearly scoped. This document is the single source of truth for what may be built and what must be blocked in the AI tutor, voice input, and WhatsApp sharing tracks.

## Core boundary principles

- No new production code is introduced in this planning batch.
- All implementation decisions are deferred until the plan is approved.
- The plan must explicitly name allowed behaviors, blocked behaviors, consent rules, and audit requirements.
- Safety and privacy must be enforced before any AI tutor or voice features reach learners.

## AI tutor boundary

### Allowed
- Server-only proxy route for tutor requests.
- Provider keys stored exclusively on the server.
- Lesson-scoped queries with explicit boundaries.
- Input/output filtering and safe refusal modes.
- Guardian consent gating.
- Rate limiting and audit event recording.

### Blocked
- Client-side open API calls to model providers.
- Unlimited free chat or general Q&A.
- Child PII or sensitive content sent to the provider.
- Persistent tutor history without an approved retention and review schema.
- Unapproved direct access to `/api/tutor` from the client.

## Voice input boundary

### Allowed
- Progressive enhancement to existing lesson input.
- Consent-gated access and explicit user enablement.
- Text fallback always available.
- No storage of raw audio or transcripts.
- No requirement that learners must speak to complete a lesson.

### Blocked
- Automatic microphone permission prompts.
- Background listening or always-on capture.
- Offline-only voice UX without device verification.
- Any voice-first or voice-only lesson flow.

## WhatsApp sharing boundary

### Allowed
- Guardian-triggered share intent only.
- Explicit confirmation before sending.
- Minimal, reviewable message content.
- No learner PII, profile, or tutor transcript sharing.
- POPIA §69 direct-marketing risk acknowledgement.

### Blocked
- Learner-initiated WhatsApp share actions.
- Automatic or silent sharing.
- Sharing without guardian confirmation.
- Sharing private tutor or educational content that is not minimal.

## Compliance requirements

- All AI tutor and voice features must include audit hooks before implementation.
- Parent review and retention policy must be defined before tutor history is stored.
- Guardian consent must be documented and revocable.
- Any share feature must avoid POPIA direct-marketing exposure.

## Non-goals for this batch

- No AI tutor implementation code.
- No voice input feature code.
- No WhatsApp share implementation code.
- No direct provider integrations.
- No microphone or audio capture code.
- No client-side data leakage.
