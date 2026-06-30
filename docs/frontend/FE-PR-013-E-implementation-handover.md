# FE-PR-013-E Implementation Handover — Guardian WhatsApp Share (client-only)

Scope: implement a client-only guardian-triggered WhatsApp share intent that allows a guardian to edit a redacted summary before invoking the native share or opening a `wa.me` link. Strict non-goals and constraints are listed below.

Files added in this PR:

- `app/frontend/src/components/guardian/WhatsAppShareShell.tsx` — Client component, editable composer, guardian-triggered only. Does not auto-open, does not persist message body or recipient.
- `app/frontend/src/lib/share/whatsapp.ts` — Client helper: `buildWaMeUrl`, `shareViaNavigator`, `emitShareAudit`. Audit is metadata-only and never includes message content.
- `app/frontend/src/lib/share/types.ts` — Types for metadata.
- `app/frontend/src/__tests__/guardian/whatsapp-share-helper.test.ts` — Unit test for `buildWaMeUrl`.
- `app/frontend/src/__tests__/guardian/whatsapp-share-shell.test.tsx` — Component test ensuring no auto-share and metadata-only audit.

Hard blocks (enforced):

- No server-side WhatsApp API integration.
- No recipient phone-number persisted by the app or server.
- No message-body persistence or analytics that contain message content.
- No raw tutor transcripts or PII in the shared payload.
- No learner-triggered share controls; UI should be rendered only for guardians in the app flow.
- No auto-open on component render.

Verification steps run locally (required):

1. Type-check: `pnpm run type-check`  
2. Lint: `pnpm run lint --no-cache`  
3. Tests: `pnpm run test --silent`  
4. Build: `pnpm run build`  
5. Analyze: `ANALYZE=true pnpm run build`  
6. Forbidden-scope grep (expected only matches in docs/tests/components):

```
grep -RInE \
  "recipientPhone|phoneNumber|messageBody|server.*whatsapp|WhatsApp Business|rawTranscript|fullTranscript|rawPrompt|rawResponse|autoShare|learner.*share" \
  app/frontend/src docs/frontend \
  --exclude-dir=node_modules --exclude-dir=.next
```

If CI or reviewers spot accidental persistence of message bodies or phone numbers, revert and remove persisted artifacts immediately and notify the compliance owner.

Next steps for reviewers:

- Confirm the implementation renders only within guardian flows.
- Run the verification steps above.
- If accepted, open a follow-up PR to wire the guard that conditionally shows the UI in the guardian-only experience (not included here).
