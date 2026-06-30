# FE-PR-008 Audit — Parent Portal, Consent Flows, Info Officer Evidence

## Audit Scope
Guardian/parent portal routes, consent state/contracts, POPIA/data-rights endpoints, Info Officer display, evidence/audit hooks, report/export/erasure entrypoints, existing guardian tests.

## Audit Findings

### 1. Guardian/Parent Routes

| Route | Path | Type | Notes |
| --- | --- | --- | --- |
| Parent dashboard (parent group) | `/app/(parent)/parent-dashboard/page.tsx` | Client component | Uses `RouteGuard` with `required="parent"`, renders `ParentDashboard`. |
| Parent portal (legacy) | `/app/parent-portal/page.tsx` | Client component | Renders `ParentDashboard` directly, no route guard. |
| Learner-facing parent portal | `/app/(learner)/parent/page.tsx` | Client component | Shows learner ID and POPIA info, uses `LearnerContext`. |
| Privacy settings | `/app/settings/privacy/page.tsx` | Client component | Comprehensive privacy controls (analytics, AI improvement, marketing, leaderboard, retention, export, erasure). |

**Observations:**
- Two parent dashboard entry points exist: `/parent-dashboard` (guarded) and `/parent-portal` (unguarded). This is inconsistent.
- The learner-facing parent portal (`/parent`) is not a guardian-managed route—it’s a learner-facing view showing their ID for sharing with guardians.
- Privacy settings page is a standalone route with POPIA controls but not integrated into the guardian portal shell.

### 2. Consent Contracts

| Service | Methods | Types | Notes |
| --- | --- | --- | --- |
| `ConsentService` | `grant`, `revoke`, `status` | `ConsentGrantResponse`, `ConsentStatusResponse` | Calls `/consent/grant`, `/consent/revoke`, `/consent/status/{learnerId}`. |

**Observations:**
- Consent service exists but is not wired into any guardian-facing UI.
- No consent gate UI exists for guardians to grant/revoke consent for their learners.
- Consent is referenced in learner onboarding and registration flows, but there is no guardian-managed consent management flow.

### 3. POPIA/Data-Rights Endpoints

| Service | Methods | Types | Endpoints |
| --- | --- | --- | --- |
| `DataRightsService` | `exportLearner`, `requestErasure`, `cancelErasure`, `restrictProcessing`, `deletionStatus` | `DataRightsStatus`, `DataExportBundle` | `/popia/data-export`, `/popia/deletion-request`, `/popia/deletion-cancel`, `/popia/restriction-request`, `/popia/deletion-status` |

**Observations:**
- Data rights service is fully implemented and used in `ParentDashboard` and privacy settings page.
- Export, restrict, and erasure actions are surfaced in `ParentDashboard` with status messages.
- Privacy settings page provides a more comprehensive UI for the same actions plus retention and analytics toggles.

### 4. Info Officer Display

**Observations:**
- No dedicated Info Officer display component or route exists.
- POPIA documentation references Info Officer responsibilities, but there is no UI surface for guardians to contact the Info Officer or view their contact details.
- This is a gap for RC3 scope.

### 5. Evidence/Audit Hooks

**Observations:**
- Backend POPIA consent and audit evidence is documented in `docs/security/POPIA_CONSENT_GATE_CLOSURE.md` and `docs/security/POPIA_CONSENT_AUDIT_BASELINE.md`.
- Frontend does not currently expose audit event IDs or evidence hooks to guardians.
- `DataRightsStatus` type includes an `audit_event` field, but it is not displayed in the UI.
- Privacy settings page does not surface audit evidence for export/erasure requests.

### 6. Report/Export/Erasure Entrypoints

| Location | Actions | Notes |
| --- | --- | --- |
| `ParentDashboard` | Export, restrict processing, erasure | Buttons per learner, status messages, error handling. |
| Privacy settings page | Export, erasure, retention, analytics toggles | More comprehensive UI, modal for erasure confirmation. |

**Observations:**
- Two separate UIs provide overlapping POPIA rights functionality: `ParentDashboard` and privacy settings page.
- This is inconsistent and should be consolidated under a guardian portal shell.

### 7. Existing Guardian Tests

| Test File | Coverage | Notes |
| --- | --- | --- |
| `ParentDashboard.test.tsx` | Empty state, export, restrict, erasure, error handling | Mocks `ParentService` and `DataRightsService`. |
| `EntryAndPortal.test.tsx` | Parent dashboard rendering in portal smoke test | Mocks `ParentService.getTrustDashboard` and `getExportBundle`. |
| `RouteGuard.test.tsx` | Parent route guard behavior | Tests session check and redirect to `/login`. |

**Observations:**
- Tests cover basic dashboard functionality but not consent flows or Info Officer display (since they don’t exist).
- No tests for privacy settings page.
- No Playwright/Vitest guardian journey tests for end-to-end consent management.

## RC3 Slice Boundary Recommendation

Based on the audit, the RC3 slice should include:

1. **Consolidate guardian portal shell:**
   - Create a single guardian portal entry route with `RouteGuard` and server shell loader.
   - Deprecate or redirect `/parent-portal` to the guarded route.
   - Move privacy settings into the guardian portal shell as a sub-route.

2. **Consent gate UI:**
   - Add consent management UI for guardians to grant/revoke consent for their learners.
   - Wire `ConsentService` into the guardian portal shell.
   - Add consent status display per learner.

3. **Info Officer display:**
   - Add Info Officer contact details and responsibilities display in the guardian portal.
   - Provide a contact form or email link for guardians to reach the Info Officer.

4. **Audit evidence hooks:**
   - Surface `audit_event` IDs from `DataRightsStatus` in the UI.
   - Add a history view for data rights requests with audit evidence.
   - Consider adding a downloadable audit log for guardians.

5. **Guardian journey tests:**
   - Add Playwright/Vitest tests for consent grant/revoke flows.
   - Add tests for Info Officer display and contact.
   - Add tests for audit evidence display.

6. **Deprecate learner-facing parent portal:**
   - The `/parent` route under `(learner)` is a learner-facing view, not a guardian-managed route.
   - Clarify its purpose or move it to a learner settings section.

## Out of Scope for RC3

- PWA/offline sync.
- Analytics implementation (only UI toggles exist).
- AI tutor, voice input, WhatsApp sharing.
- Grade R phonics/earcons.
- Advanced gamification or leaderboards.
- RC5 visual/interaction extras.

## Next Steps

1. Confirm RC3 slice boundary with the user.
2. Begin implementation starting with the consolidated guardian portal shell.
3. Add consent gate UI and Info Officer display.
4. Add audit evidence hooks and guardian journey tests.
5. Document FE-PR-008 handover evidence.
