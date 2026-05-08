# Secrets Management (starter guidance)

Owner: `NkgoloL` (update when team members assigned).

Goals:
- Keep production secrets out of source control.
- Provide a clear rotation and emergency revoke procedure.

Recommended practices:
- Store secrets in a secret store (Azure Key Vault, HashiCorp Vault, or similar).
- Use short-lived credentials for CI where possible.
- Never commit secrets or credentials into the repo; enable secret scanning.
- Use environment-specific secret scopes: local, test, staging, production.

Rotation and emergency revoke (minimal process):
1. Identify secret owner and list affected systems.
2. Rotate secret in vault and update dependent deployments.
3. Revoke old secret where supported.
4. Run smoke tests and monitor for failures.
5. Notify stakeholders and document incident in `audits/`.

CI integration:
- Use CI secret variables or vault integrations (do not echo secrets in logs).

Next steps (fill in org-specific details):
- Add a mapping of secret names to vault paths and owner contact details.
- Add rotation schedule (e.g., quarterly) and emergency contact list.
