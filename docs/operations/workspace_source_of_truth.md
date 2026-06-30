# Workspace Source Of Truth

Updated: 2026-06-13

## Decision

The local WSL checkout is the main working directory and current source-of-truth workspace for EduBoost V2 work:

```text
/home/nkgolol/Dev/Development/Eduboost-V2
```

The Windows path exposed to desktop tooling is:

```text
\\wsl.localhost\Ubuntu\home\nkgolol\Dev\Development\Eduboost-V2
```

## Remote VM Status

The previously referenced remote VM is inaccessible and is not canonical for current development, audit, or release evidence. Recent SSH attempts to the old host timed out. Do not rely on that VM for file state, test evidence, or deployment identity unless access is restored and AR-010 records fresh environment identity evidence.

## Operating Rule

- Run repository commands from the local WSL checkout.
- Treat `origin` as the Git synchronization point.
- Tie release evidence to an exact local WSL commit, CI run, and deployed image digest.
- If a remote or staging environment is reintroduced, it must prove commit SHA, image digest, migration head, OpenAPI hash, Content Factory registry hashes, and sanitized configuration fingerprint before it can become canonical.
