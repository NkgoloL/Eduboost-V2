---
title: "Pull Request Template — Documentation Change"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'architecture']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
## Documentation change checklist

- [ ] I checked `docs/documentation/source_of_truth.yml`.
- [ ] I marked new/changed docs with front matter metadata.
- [ ] I did not create a second canonical document for an existing topic.
- [ ] I used bounded language for readiness/security/compliance/release claims.
- [ ] I linked claims to commands, code anchors, or evidence records.
- [ ] I archived or superseded stale documents instead of leaving duplicates current-looking.
- [ ] I ran `make docs-housekeeping-check` or the relevant documentation check scripts.
