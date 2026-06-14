# Phase 11 Route Comment Audit

**Audit date:** 2026-06-14
**Status:** Complete for stale authorization comments; two operational TODOs remain intentional

## Reviewed Scope

Route comments and docstrings were reviewed in the active `app/api_v2_routers/`
package, focusing on references to legacy dependency injection, trust-based
lesson access, and stale router ownership.

## Fix Applied

- Removed the stale `lessons.py` comment that said the route trusted `lesson_id`
  knowledge. The route now calls `require_lesson_read_access_for_current_user`
  before loading the lesson.

## Remaining Comments

The remaining route TODO comments in `auth_extended.py` describe asynchronous
job enqueueing for privacy export/deletion requests. They are not stale
authorization comments and remain as operational follow-up markers.

## Verification

```bash
grep -R "trust the lesson_id" -n app/api_v2_routers
# no matches
```
