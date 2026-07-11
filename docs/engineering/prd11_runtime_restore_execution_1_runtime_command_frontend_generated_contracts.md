# PRD-11.0R.RUNTIME-RESTORE.EXECUTION-1 — Runtime Command Execution, Frontend Hook Repair, and Generated Contract Gate Activation

**Status:** Authority recorded  
**Owner:** Nkgolo Lebelo  
**Scope:** Start clearing real blockers instead of adding more meta-contracts.

## Purpose

This execution slice begins the blocker-clearing phase after PRD-11.0R.RUNTIME-RESTORE-6. It targets concrete failures that prevent independent runtime/product/advisory proof:

1. Python child commands in runtime collectors used `python3`, which can escape the repo virtual environment even when the top-level verifier is executed with `.venv/bin/python`.
2. The frontend learner layout had a conditional early return before `useEffect`, which is a real React hook-order lint blocker.
3. Generated-contract checks must run with the same interpreter and dependencies as the caller, otherwise they can fail because the app dependencies are unavailable to system Python.

## Boundary

This slice does not claim the runtime baseline is green. It keeps controlled-beta activation on operational hold and keeps production release, deployment, release tags, public beta, billing launch, and live payment processing locked.

## Evidence rule

The slice is valid when the source fixes are installed and evidence is captured. The actual runtime baseline remains red until the independent command gates are executed and pass.
