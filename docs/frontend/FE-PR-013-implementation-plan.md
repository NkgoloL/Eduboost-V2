# FE-PR-013 Implementation Plan

## Summary

This document defines the FE-PR-013 planning boundary for AI tutor streaming, voice input, and WhatsApp sharing. It separates the three tracks into independent design and gating requirements so implementation only begins after the plan is approved.

## Tracks

### 1. AI tutor streaming

#### Allowed scope
- Server-proxied tutor route only (e.g. Next.js `/api/tutor` or approved backend proxy).
- Provider API keys stored and used only on the server.
- Lesson-bounded help: tutor access is tied to the current lesson context.
- Strict input filtering before proxying prompts.
- Output filtering before UI rendering.
- Rate limits on learner turns and session volume.
- Audit events for tutor session lifecycle and safety triggers.
- Safe refusal states when prompts are off-topic, unsafe, or rate-limited.

#### Blocked scope
- Direct client calls to third-party model providers.
- Unrestricted free chat or open-ended AI usage.
- Sending child PII to the tutor provider.
- Persistent tutor history without an approved parent-review schema.
- Tutor history retained without a documented retention policy.
- Any client-side provider key handling or storage.

#### Consent requirements
- Guardian consent must be obtained before enabling tutor access for learners.
- Consent should be explicit, recorded, and reviewable.
- Tutor usage should include an explanatory UX state when consent is required or denied.

#### Audit events
At minimum, emit:
- `tutor.session_started`
- `tutor.turn_submitted`
- `tutor.turn_completed`
- `tutor.rate_limit_exceeded`
- `tutor.safety_filter_triggered`
- `tutor.session_ended`

#### Failure states
- `Tutor unavailable`: when the server proxy is down.
- `Rate limit reached`: learner has hit the permitted turn count.
- `Input blocked`: prompt rejected due to disallowed content or PII.
- `Content refused`: tutor refuses off-topic or unsafe requests.
- `Guardian consent required`: tutor cannot activate without consent.

#### Tests
- Unit tests for API proxy filtering and rate-limit logic.
- Contract tests validating `/api/tutor` request/response shape.
- UI tests confirming tutor activation only after consent.
- Safety tests for refusal states and output sanitization.
- Audit tests asserting required events are emitted.

#### Rollback plan
- Disable the tutor route at the server layer.
- Revert feature flag or UI entry point.
- Retain audit logs for post-mortem analysis.
- Remove any partially stored tutor session history until the approved schema is in place.

### 2. Voice input

#### Allowed scope
- Progressive enhancement only.
- Guardian consent gate required before any voice input UI is enabled.
- Mandatory text fallback for all voice-enabled flows.
- No audio recording storage on device or server.
- No lesson completion dependency on voice input.
- Voice input should be optional and clearly labelled.

#### Blocked scope
- Automatic microphone prompts on page load.
- Background listening or continuous capture.
- Offline voice claims without explicit device compatibility testing.
- Voice-only UX or gating lesson progress behind voice.

#### Consent requirements
- Guardians must explicitly opt into voice input feature.
- The app should explain what voice input will do and what is not stored.
- Consent should be cancellable at any time.

#### Audit events
- `voice.input_enabled`
- `voice.input_submitted`
- `voice.input_rejected`
- `voice.consent_revoked`

#### Failure states
- `Microphone unavailable`: device permission denied or hardware absent.
- `Voice input blocked`: consent not granted.
- `Voice input unsupported`: browser does not support `getUserMedia` for audio.
- `Fallback enforced`: user must use text input.

#### Tests
- UI tests for voice enablement gating and consent flows.
- Negative tests for blocked microphone permission.
- Accessibility tests ensuring text fallback is present.
- Functional tests confirming no voice prompt appears without consent.

#### Rollback plan
- Hide or disable voice input controls in the UI.
- Remove any runtime media access requests.
- Preserve fallback text input as the canonical path.

### 3. WhatsApp sharing

#### Allowed scope
- Guardian-triggered sharing only.
- Consent-aware sharing flow with explicit confirmation.
- Minimal reviewed content before send.
- No child PII or learner profile data in WhatsApp messages.
- POPIA §69 direct-marketing risk explicitly addressed in documentation.

#### Blocked scope
- Learner-triggered WhatsApp sharing.
- Auto-sharing or pre-populated send without guardian review.
- Sharing learner profile data.
- Sharing tutor transcripts or sensitive conversation content.
- Sharing without guardian confirmation.

#### Consent requirements
- Guardians must review and confirm each WhatsApp share.
- The content should be editable or reviewable before opening WhatsApp.
- The share flow should clearly describe what will be sent.

#### Audit events
- `whatsapp.share_requested`
- `whatsapp.share_confirmed`
- `whatsapp.share_cancelled`
- `whatsapp.share_blocked`

#### Failure states
- `Sharing blocked`: guardian did not confirm.
- `PII blocked`: message contains disallowed sensitive data.
- `WhatsApp unsupported`: device/browser does not support the share target.

#### Tests
- UX tests verifying guardian confirmation step.
- Content tests ensuring shared messages are minimal and non-PII.
- Audit tests validating share events.
- Negative tests preventing learner-initiated share actions.

#### Rollback plan
- Remove WhatsApp share controls from the UI.
- Disable the share intent feature entirely.
- Keep the flow documented for future approval.
