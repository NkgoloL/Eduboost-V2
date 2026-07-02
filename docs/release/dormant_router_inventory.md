# Dormant Router Inventory

**RR item:** RR-003  
**Status:** inventory baseline

This inventory records router modules that need explicit review before retirement, archival, or route consolidation work. This document does not remove routes.

| Router | Current classification | Required next action |
|---|---|---|
| `app/modules/diagnostics/bias_review_router.py` | specialist diagnostic governance route | confirm active use or archive under RR-005 |
| `app/modules/lessons/lesson_coverage_router.py` | specialist lesson coverage route | confirm active use or archive under RR-005 |
| `app/modules/lessons/lesson_review_router.py` | specialist lesson review route | confirm active use or archive under RR-005 |
| `app/modules/practice/router.py` | practice module route | confirm active use or archive under RR-005 |

## Boundary

Dormant router retirement is deferred to RR-005 technical debt burn-down unless a route is proven unsafe.
