---
title: "Import-Linter Contract Run"
status: active
owner: architecture
reviewers: [architecture, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/architecture/README.md]
---

# Import-Linter Contract Run

Generated at: `2026-06-12T17:31:10Z`

**Status:** pass

```text

╔══╗─────────▶╔╗ ╔╗      ╔╗◀───┐
╚╣╠╝◀─────┐  ╔╝╚╗║║────▶╔╝╚╗   │
 ║║   ╔══╦══╦╩╗╔╝║║  ╔╦═╩╗╔╝╔═╦══╗
 ║║╔══╣╔╗║╔╗║╔╣║ ║║ ╔╬╣╔╗║║ ║│║╔═╝
╔╣╠╣║║║╚╝║╚╝║║║╚╗║╚═╝║║║║║╚╗║═╣║
╚══╩╩╩╣╔═╩══╩╝╚═╝╚═══╩╩╝╚╩═╩╩═╩╝
  └──▶║║                    ▲ 
      ╚╝────────────────────┘


---------
Contracts
---------

Analyzed 390 files, 1907 dependencies.
--------------------------------------

FastAPI v2 routers should not import repositories directly KEPT
POPIA router uses dependency layer rather than repository construction KEPT
Lessons router uses authorization service layer rather than repositories KEPT

Contracts: 3 kept, 0 broken.
```
