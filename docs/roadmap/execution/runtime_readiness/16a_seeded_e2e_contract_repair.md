# Phase 16A — Seeded E2E Route and Contract Repair

Status: repair slice. This does not claim Phase 16 evidence.

Repairs targeted by this slice:

- restore seeded learner state from `eb_active_learner`;
- forward the dev bearer token through the frontend client and Next proxy;
- expose seeded `/learners/:learnerId/*` and `/parent/learners/:learnerId/*` routes;
- align direct Playwright API assertions with the V2 async job contract;
- align parent consent API usage with `/api/v2/consent/status/{learner_id}`;
- provide stable UI markers for seeded study-plan, lesson, parent report, consent and data-export paths.

Boundary: no production release, deployment, release tag, live learner traffic, full production E2E certification, or runtime KG implementation is authorised.
