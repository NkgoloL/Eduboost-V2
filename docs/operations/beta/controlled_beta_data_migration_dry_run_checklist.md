# Controlled Beta Data Migration Dry-Run Checklist

This checklist does not authorise learner data migration or live learner traffic.

- Controlled beta launch authorised: false
- Live learner traffic authorised: false

## Dry-Run Scope

- Use synthetic or explicitly approved test records only.
- Do not import live learner data under this gate.
- Validate migration scripts against rollback expectations.
- Confirm audit logs are generated for create/update/delete operations.
- Confirm no production identifiers are written into public evidence.

## Exit Notes

A later learner-data migration gate is required before importing real learner or
guardian records.
