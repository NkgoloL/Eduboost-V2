# PR Checklist — FE-PR-001 through FE-PR-013

Use the matrix below to ensure every implementation slice ships with its required evidence. Attach this checklist (or a link) to each PR description.

| PR ID | Scope | Key Deliverables | Required Evidence |
| --- | --- | --- | --- |
| FE-PR-001 | ADRs, rollback plan, backlog metadata | ADR template + ADR-001..008 files, sign-off register, rollback plan, metadata/spike templates | Links to ADR markdown files, updated sign-off table, screenshot/CI log showing lint success |
| FE-PR-002 | Docker/runtime, pnpm discipline, env validation, monitoring, `.next` cleanup | Dockerfile runner target, pnpm lock, env schema, monitoring facade, cleanup script | `pnpm run build` log, `make clean-next`, `/api/health` output, screenshot of analyzer |
| FE-PR-003 | TypeScript strictness + lint | Strict tsconfig, lint rule, zero `any`, failing tests resolved | `pnpm run type-check` log, ESLint report, list of removed `any`s |
| FE-PR-004 | Design tokens + root layout | Tailwind tokens, earcon constants, layout shells | Screenshot of tokens, `pnpm run lint` focusing on CSS, accessibility notes |
| FE-PR-005 | Auth shell, protected routes | Session helpers, JWT verification, middleware, login/register forms | Playwright auth journey, cookie inspection screenshot |
| FE-PR-006 | Learner dashboard shell | Dashboard RSC, diagnostic entry, lesson loop shell | Playwright Journey 1–2 evidence, audit relay log |
| FE-PR-007 | RC2 gamification core | XP, badges, streak display, boundary docs | Bundle diff with analyzer, UX screenshots |
| FE-PR-008 | Guardian consent gate | Parent portal shell, consent FSM, Info Officer panel | Playwright guardian journey, consent log export |
| FE-PR-009 | Accessibility + mobile hardening | A11y fixes, SAST timestamps, POPIA evidence coupling | Lighthouse + axe reports, SAST timestamp proof |
| FE-PR-010 | PWA shell | Manifest, install prompts, low-data toggle | Lighthouse PWA score, offline screenshots |
| FE-PR-011 | Offline progress queue | Sync reconciliation, loadshedding UI | Offline Playwright log, Dexie schema dump |
| FE-PR-012 | Grade R mode + earcons | Pre-reader UI, phonics/karaoke renderer | Accessibility test results, earcon playback recordings (synthetic) |
| FE-PR-013 | AI tutor, voice input, WhatsApp sharing | Tutor proxy, voice hooks, sharing UI | FE-SPIKE-004/005 approvals, safety review, audit logs |

## How to Use

1. Copy relevant row(s) into the PR description and tick each evidence item with ✅ / ❌.
2. Link to supporting documents in `docs/frontend/*` and the spike reports.
3. Update the release evidence file once the PR merges.
