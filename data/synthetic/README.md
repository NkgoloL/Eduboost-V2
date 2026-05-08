# Synthetic local seed data

This directory is reserved for local-only, non-PII seed data.

Rules:

1. Never copy production learner, guardian, consent, billing, or audit records into fixtures.
2. Use pseudonymous emails, learner names, and deterministic IDs.
3. Keep datasets small enough for local development unless a specific performance test requires volume.
4. Mark all synthetic records clearly in payload fields where possible.

Use this data only for development and migration smoke tests.
