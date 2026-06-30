# FE-PR-013-D Voice Consent Evidence

- Guardian consent stored in `localStorage` via `app/frontend/src/lib/voice/consent.ts`.
- Consent is required for voice usage; guardrails implemented in `guardrails.ts`.
- No microphone permission is requested on component mount; permission flows must be user-initiated in the UI.
- Tests cover consent get/set, guardrails logic, capability detection, and component render.
