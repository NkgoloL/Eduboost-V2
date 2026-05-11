# Pull Request

## Summary

Describe the change and why it is needed.

## Scope

- [ ] Backend
- [ ] Frontend
- [ ] Security
- [ ] POPIA/compliance
- [ ] AI/CAPS
- [ ] DevOps/CI
- [ ] Documentation
- [ ] Tests only

## Evidence

Add evidence paths and commands here.

```text
Implementation:
Tests:
Docs:
CI:
Staging:
Release evidence:
```

## Runtime/API Contract Checklist

Complete this section when the PR changes backend runtime, routers, request/response models, error handling, OpenAPI output, or API client contracts.

- [ ] I confirmed the canonical runtime remains `app.api_v2:app`.
- [ ] I ran `make runtime-check`.
- [ ] I ran `make openapi-check`.
- [ ] I ran `make route-inventory-check`.
- [ ] I regenerated `docs/openapi.json` if API contracts changed.
- [ ] I regenerated `docs/route_inventory.md` if routes changed.
- [ ] I updated or added tests for request/response model changes.
- [ ] I updated or added tests for error-envelope behavior.
- [ ] I verified legacy routes are not exposed by `app.api_v2:app`.
- [ ] I documented any breaking API change and added the required PR label.
- [ ] I updated relevant API docs or evidence docs.

## Security and POPIA Checklist

Complete this section when the PR touches auth, authorization, consent, learner data, guardian data, audit, exports, erasure, logs, prompts, billing, or operational secrets.

- [ ] Object-level authorization was considered and tested where relevant.
- [ ] Consent gates were considered and tested where relevant.
- [ ] No unnecessary learner/guardian PII is exposed.
- [ ] Logs, prompts, and error responses do not expose secrets or sensitive PII.
- [ ] Audit events were added or updated where required.
- [ ] Compliance docs were updated where required.

## Verification Commands

Paste the exact commands run.

```bash
# example; replace with exact targeted commands for this PR
pytest -c pytest.ini tests/path/to/relevant_test.py -q --no-cov
```

## Release Evidence Impact

- [ ] No release-evidence impact.
- [ ] Release evidence updated.
- [ ] Release evidence update deferred with issue link.

## Notes for Reviewer

List risk areas, known limitations, follow-up tasks, or rollback notes.
