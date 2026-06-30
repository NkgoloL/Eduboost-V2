# FE-PR-013-E — Guardian-triggered WhatsApp sharing boundary

## Status
Planning-only PR. No implementation in this PR. This document defines the hard boundary, verification criteria, and acceptance checklist for any future work that adds a guardian-triggered WhatsApp share feature.

## Goal
Allow guardians to share a short, redacted, guardian-reviewed summary derived from parent-review assets via WhatsApp as a client-side share action only — subject to strict consent, redaction, and audit controls. This feature must not expose child PII, raw tutor transcripts, or persist message bodies or recipient phone numbers on our servers.

## Allowed scope
- UI and UX patterns that are guardian-triggered only (explicit "Share via WhatsApp" control visible only to guardians after review).
- Client-side share intent only (e.g., building a `wa.me` link or invoking the browser/native share sheet) with the message composed and edited by the guardian before sharing.
- Use of existing redaction utilities to generate the initial shareable summary; guardians may edit the text locally before calling the share intent.
- Audit metadata recording (only non-sensitive metadata described below) that a share action was approved or cancelled.
- UX warnings and copy that clearly instruct guardians to remove PII before sharing.

## Blocked scope
- No learner-triggered or automatic sharing flows.
- No background or automatic opening of WhatsApp or share intents without explicit guardian interaction.
- No server-side WhatsApp API integration (no third-party WhatsApp Business API calls from our servers in this PR).
- No collection or persistence of recipient phone numbers, message body, or transcripts in server-side storage.
- No analytics capturing message content. Only very coarse usage counters without content are allowed.

## Consent and POPIA §69 controls
- Lawful basis: explicit guardian consent for sharing; the guardian must actively review and approve the exact message to be shared. Consent is recorded in ephemeral audit metadata (audit record includes guardian pseudonymous id and action metadata but not the message body nor recipient).
- POPIA §69 risk mitigation:
  - No child-sensitive personal data is shared by default; the initial message must be redacted using the parent-review redaction utilities.
  - Guardians receive a prominent, editable preview and must confirm they have removed any PII before sending.
  - The system will not persist recipient identifiers or message bodies. Audit metadata must not include PII.
  - Retention: audit metadata retention limited to the minimal administrative period required by policy (documented separately), and subject to deletion requests.

## Data boundary
- Input: a redacted summary derived from the `ParentReviewRecord.redactedSummary` (or an editable variant prepared client-side by the guardian). Only redacted text should be used as the initial content.
- Output: the share intent invocation (wa.me URL or navigator.share payload) created on the client and handed to the platform. No message body or recipient phone number is stored on the server.
- Storage: No long-term storage of message text or recipient identifiers. Audit logs record only metadata (see below).

## Audit metadata
Record the following audit metadata when a guardian either approves or cancels a share action:
- `event`: `whatsapp_share_attempt` | `whatsapp_share_cancelled` | `whatsapp_share_approved`
- `timestamp`: ISO 8601
- `actor`: guardian pseudonymous id (no real name/email)
- `learnerId`: pseudonymous learner id
- `lessonId`: lesson id (if applicable)
- `messageLength`: integer character count of the final message at time of share invocation
- `outcome`: `approved` | `cancelled` | `failed`
Do NOT store: message body, recipient phoneNumber, wa.me URL containing phone, or full transcript.

## Proposed implementation files (for a later PR, NOT in this planning PR)
- `app/frontend/src/components/guardian/WhatsAppShareShell.tsx` (guardian review UI + editable composer + approve/cancel)
- `app/frontend/src/utils/share/whatsapp.ts` (client-only helper to build safe wa.me link or platform share object)
- `src/__tests__/guardian/whatsapp-share.*` (unit and integration tests for redaction+share intent+audit)

## Required tests (for implementation PR)
- Unit tests: verify `sanitizeForShare()` removes PII using redaction utilities.
- Integration tests: simulate guardian review flow, ensure audit metadata recorded, ensure wa.me link or navigator.share payload contains only sanitized text and is not sent to server.
- Forbidden-scope grep in CI to ensure no server-side WhatsApp API or phone storage code was added.

## Forbidden-scope grep (CI requirement)
Before merging any implementation PR, run:

```
grep -RInE "wa\.me|WhatsApp|whatsapp|navigator\.share|shareAction|recipientPhone|phoneNumber|messageBody" \
  app/frontend/src docs/frontend \
  --exclude-dir=node_modules --exclude-dir=.next
```

Expected: matches only in docs or tests; no new `app/frontend/src` implementation of server-side WhatsApp integration or phone storage.

## Rollback plan
- If a later implementation PR introduces accidental PII persistence or a server-side WhatsApp API, revert the PR and remove persisted artifacts within 24 hours.
- Notify security/privacy owners and perform a data inventory to identify and securely delete any retained PII.

## Acceptance checklist (for the planning PR)
- [x] Document exists and is committed to `docs/frontend/FE-PR-013-E-whatsapp-sharing-boundary.md`.
- [x] No implementation files added in `app/frontend/src` in this PR.
- [x] CI checklist for forbidden-scope grep added to the implementation PR checklist (above).
- [x] Privacy and POPIA §69 controls documented.

