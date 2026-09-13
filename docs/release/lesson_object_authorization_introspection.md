---
title: "Release — Lesson Object Authorization Introspection"
status: "active"
owner: "release"
reviewers: ['release', 'engineering']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
# Lesson Object Authorization Introspection

Generated at: `2026-05-17T20:18:03Z`

| Check | Value |
|---|---|
| Router exists | True |
| Helper import present | True |
| Read helper calls | 2 |
| Write helper calls | 3 |
| Sync extractor calls | 2 |

## Router functions

- `get_lesson_service` args=['db']
- `generate_lesson` args=['request', 'body', 'background_tasks', 'current_user', 'db', 'service']
- `_run` args=[]
- `generate_lesson_stream` args=['body', 'current_user', 'db', 'service']
- `_events` args=[]
- `get_lesson` args=['lesson_id', 'current_user', 'service', 'db']
- `complete_lesson` args=['lesson_id', 'current_user', 'service', 'db']
- `sync_lessons` args=['body', 'current_user', 'service', 'db']
