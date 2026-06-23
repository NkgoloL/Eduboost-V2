# Technical Audit Remediation — Slice 01: OpenAPI Route Contract

**Status:** Implementation package ready  
**Stream:** Technical-audit remediation  
**Precondition:** Phase 02R terminally closed and baseline reset evidence recorded.

## Objective

Reconcile OpenAPI drift after POPIA route alignment and establish a static contract that prevents frontend/backend route drift from returning.

## Scope

This slice covers:

- regeneration of `docs/openapi.json` from the active FastAPI runtime;
- static verification that canonical POPIA and parent privacy routes are present in OpenAPI;
- static verification that stale POPIA frontend aliases are absent;
- static verification that parent export references use the canonical POPIA export endpoint;
- evidence capture for the audit-remediation stream.

## Non-scope

This slice does not:

- change Phase 02R governance;
- declare full product release readiness;
- run live database migrations;
- implement runtime knowledge-graph features;
- modify learner graph state;
- close the full technical-audit remediation stream.

## Canonical route contract

The following routes must appear in `docs/openapi.json` under both `/api/v2` and `/v2` where the backend exposes both prefixes:

- `POST /popia/exports`
- `POST /popia/erasure`
- `POST /popia/erasure/{learner_id}/cancel`
- `GET /popia/erasure/{learner_id}/status`
- `POST /popia/restriction`
- `GET /parents/{guardian_id}/export`

The frontend client must use canonical POPIA routes and must not reintroduce stale route aliases such as `/popia/data-export/{learnerId}` or `/popia/deletion-request/{learnerId}`.

## Knowledge-graph future constraint

The KG pivot remains a future architectural north star. This slice preserves that direction by keeping route contracts deterministic and provenance-friendly, while explicitly avoiding runtime KG implementation until the audit remediation stream has a green baseline.

## Evidence

Evidence should be recorded under:

```text
docs/release-evidence/technical-audit/openapi-route-contract/
```

Required raw artifacts:

- `raw/openapi_regeneration_check.txt`
- `raw/openapi_route_contract.json`
- `raw/popia_route_contract.json`
- `raw/baseline_reset_check.json`
- `raw/openapi_sha256.txt`
- `raw/unit_tests.txt`
- `raw/compileall.txt`
