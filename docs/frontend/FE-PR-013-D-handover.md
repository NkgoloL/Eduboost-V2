# FE-PR-013-D Handover — Voice progressive enhancement boundary

This PR adds a consent-gated, progressive enhancement voice input shell.

Included:

- `app/frontend/src/lib/voice/types.ts`
- `app/frontend/src/lib/voice/capability.ts`
- `app/frontend/src/lib/voice/consent.ts`
- `app/frontend/src/lib/voice/guardrails.ts`
- `app/frontend/src/components/voice/VoiceInputShell.tsx`
- `app/frontend/src/components/voice/VoiceFallbackTextInput.tsx`
- Tests under `app/frontend/src/__tests__/voice`

Key constraints:
- No automatic microphone prompts; permission requested only on explicit user action.
- No audio recording or storage persisted.
- Text fallback always present.
- Guardian consent stored locally via `localStorage` (client-side). Integrate with server-side consent in future phases.
