# FE-SPIKE-004: Web Speech API & South African Accent Reliability

## 1. Browser Support Matrix
- **Chrome / Edge (Android, Desktop):** Excellent support via `webkitSpeechRecognition`. Chrome for Android natively supports offline recognition packets.
- **Safari (iOS, macOS):** Supported since iOS 14.5 via `SpeechRecognition`, but known to be flaky compared to Chromium's engine.
- **Firefox:** Minimal/no built-in support for the standard Web Speech API without experimental flags.
- **Conclusion:** Safe to implement as an enhancement, but **MUST** have a seamless text-input fallback.

## 2. Microphone Permission Behavior
- Requires explicit user interaction (e.g., tap on mic button) to request `microphone` permissions.
- In `https` environments, permissions persist; otherwise, they are requested on every session.
- Pre-reader mode must visually guide the child to grant permission if the browser prompts.

## 3. SA Accent Reliability Findings
- Specifying `lang='en-ZA'` greatly improves detection accuracy for South African English varieties compared to the default `en-US` or `en-GB`.
- Accents heavily influenced by isiZulu, isiXhosa, and Afrikaans show moderate error rates, especially for phonemes not standard in native English.
- Grade R learners (children's voices) already have higher failure rates; combined with SA accents, the recognition confidence may drop significantly.

## 4. Offline / Failure Fallback
- `SpeechRecognition` fails instantly when offline unless the device has downloaded language packs (common on modern Android, rare on iOS).
- **Fallback:** Silent degradation. The microphone button should either be hidden when `!navigator.onLine` or clearly indicate "Offline" with an earcon.

## 5. Privacy & Consent Requirements (POPIA §69)
- **Constraint:** Voice data must not be recorded, persisted, or transmitted to third parties without explicit guardian consent.
- Using the browser's native API is compliant if the text output is processed locally and discarded or anonymized before sending to the AI Tutor.
- Must ensure we are not creating PII risk by accidentally capturing background conversations in households.

## 6. Verdict
**PROCEED WITH CAUTION — pending reviewer acceptance**

## Hard Constraints
- Voice is progressive enhancement only.
- Text input remains the default fallback.
- Guardian consent is required before microphone use.
- No audio recording.
- No audio storage.
- No voice feature when offline unless tested on target devices.
- SA accent reliability remains unverified until representative testing exists.
- Grade R voice UX must not become required for lesson completion.

*Implementation is approved strictly as a progressive enhancement. It must default to disabled if consent is absent, fail silently offline, and fall back gracefully to text interactions.*
