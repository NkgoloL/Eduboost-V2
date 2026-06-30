# Technical Audit Remediation Phase 03 — Frontend & Tooling Authority

**Status:** implementation-ready  
**Authority boundary:** this slice establishes the frontend/tooling authority gate; it does not declare frontend readiness until the authority commands pass and verified evidence is recorded.  
**Backend-fast dependency:** TA-BACKEND-FAST-001 must remain closed with valid `make test-fast` evidence.  
**KG boundary:** no runtime knowledge-graph implementation is introduced. Future KG hooks remain architectural context only.

## Purpose

Phase 03 turns the frontend remediation stream into the same kind of controlled evidence workflow used for backend-fast restoration.

The authority gate is intentionally narrow:

1. Use `pnpm`, not `npm`, for frontend tooling.
2. Install from the frontend lockfile with `pnpm install --frozen-lockfile`.
3. Run the browser-exposure environment contract.
4. Run TypeScript type-checking.
5. Run frontend lint.
6. Run Vitest unit tests.
7. Preserve raw command output and machine-readable results.
8. Accept passing evidence only when every authority command exits `0`.

## Authority commands

The default authority command is:

```bash
python3 scripts/audit_remediation/run_frontend_tooling_authority.py \
  --output-dir docs/release-evidence/technical-audit/frontend-tooling-authority/raw \
  --json
```

The runner executes, in order:

```text
pnpm --version
pnpm --dir app/frontend install --frozen-lockfile
pnpm --dir app/frontend run env-check
pnpm --dir app/frontend run type-check
pnpm --dir app/frontend run lint
pnpm --dir app/frontend run test
```

A diagnostic-only `--skip-install` flag exists for local investigation, but passing authority evidence must use the default install-inclusive command.

## Evidence policy

Passing evidence requires:

- `frontend_tooling_authority_result.json` is valid JSON.
- `valid: true`.
- every expected authority step is present.
- every expected authority step has `returncode: 0`.
- `SHA256SUMS.txt` matches the captured raw artifacts.
- `evidence_index.md` exists.

Failed frontend/tooling runs may be preserved as diagnostics, but must not close TA-FRONTEND-001.

## Exit criteria

TA-FRONTEND-001 can move to `evidence_recorded` only after:

1. `collect_frontend_tooling_authority_evidence.sh` completes successfully.
2. `verify_frontend_tooling_evidence.py --evidence-dir docs/release-evidence/technical-audit/frontend-tooling-authority --json` returns `valid: true`.
3. evidence is committed separately from implementation.
4. `blocker_register.json` points at the valid frontend/tooling evidence commit.

## Out of scope

- Playwright/E2E authority closure. That remains TA-E2E-001.
- Dependency scan enforcement. That remains TA-SECURITY-001.
- Backend-fast gate changes.
- Phase 02R governance changes.
- Runtime knowledge-graph implementation.
