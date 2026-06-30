# PR-004 Lesson Route Inventory

**Date:** 2026-06-01
**Phase:** Phase 2 - Lesson Object-Level Authorization

---

## Lesson Routes

### Location
**File:** `app/api_v2_routers/lessons.py`

### Route Definitions

#### 1. Generate Lesson
```python
@router.post("/generate")
async def generate_lesson(
    body: LessonGenerationRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LessonService = Depends(get_lesson_service),
)
```
**Authorization:**
- `require_learner_write_for_current_user(current_user, str(body.learner_id))`
- `require_active_consent_for_current_user(db, current_user, str(body.learner_id))`
**Status:** ✅ Has learner authorization and consent check

#### 2. Get Lesson
```python
@router.get("/{lesson_id}")
async def get_lesson(
    lesson_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LessonService = Depends(get_lesson_service),
)
```
**Authorization:**
- `require_lesson_read_access_for_current_user(db, current_user, lesson_id)`
**Status:** ✅ Has lesson authorization (but see note below)
**Note:** Comment says "In a real app, we'd check if current_user has access to this learner's lessons"

#### 3. Complete Lesson
```python
@router.post("/{lesson_id}/complete")
async def complete_lesson(
    lesson_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LessonService = Depends(get_lesson_service),
)
```
**Authorization:**
- `require_lesson_write_access_for_current_user(db, current_user, lesson_id)`
**Status:** ✅ Has lesson authorization

#### 4. Sync Lessons
```python
@router.post("/sync")
async def sync_lessons(
    body: LessonSyncRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    service: LessonService = Depends(get_lesson_service),
)
```
**Authorization:**
- Loops over lesson IDs and calls `require_lesson_write_access_for_current_user` for each
**Status:** ✅ Has lesson authorization per lesson

---

## Lesson Authorization Functions

### Location
**File:** `app/services/lesson_authorization.py`

### Functions

#### `require_lesson_read_access_for_current_user`
```python
async def require_lesson_read_access_for_current_user(
    db: Any, 
    current_user: Any, 
    lesson_id: Any
) -> Any
```
**Implementation:** Calls authorization function with current_user and lesson owner

#### `require_lesson_write_access_for_current_user`
```python
async def require_lesson_write_access_for_current_user(
    db: Any, 
    current_user: Any, 
    lesson_id: Any
) -> Any
```
**Implementation:** Calls authorization function with current_user and lesson owner

### Authorization Logic
The authorization functions use `_call_authz` which:
1. Loads lesson to get owner (learner_id)
2. Calls authorization function with current_user and owner
3. Raises HTTP 403 if authorization fails

---

## Lesson Service

### Location
**File:** `app/modules/lessons/service.py`

### Methods

#### `get_lesson_by_id(lesson_id: str)`
- Returns lesson by ID
- **Issue:** Does not verify learner ownership before returning
- **Risk:** Any user with lesson ID can access any lesson

#### `complete_lesson(lesson_id: str)`
- Marks lesson as completed
- **Issue:** Does not verify learner ownership before mutating
- **Risk:** Any user with lesson ID can complete any lesson

#### `record_feedback(lesson_id: str, score: int)`
- Records feedback for lesson
- **Issue:** Does not verify learner ownership before mutating
- **Risk:** Any user with lesson ID can add feedback to any lesson

---

## Issues Identified

### 1. Service Methods Lack Authorization
- `get_lesson_by_id` trusts caller to have valid lesson ID
- `complete_lesson` trusts caller to have valid lesson ID
- `record_feedback` trusts caller to have valid lesson ID
- **Risk:** Lesson ID guessing allows unauthorized access

### 2. Authorization Only at Router Level
- Authorization checks exist in routers
- Service methods have no ownership verification
- If service is called directly (bypassing router), no authorization
- **Risk:** Service re-use without authorization

### 3. Sync Route Authorization
- Sync route loops over lesson IDs
- Each lesson is authorized individually
- **Issue:** No check that all lessons belong to same learner
- **Risk:** Mixed-learner payloads could be processed

### 4. No Guardian Relationship Check
- Authorization uses `can_access_learner` which checks:
  - Admin role
  - Guardian relationship
- **Issue:** Guardian relationship check may not be enforced consistently
- **Risk:** Guardians could access unrelated learners

---

## Recommended Authorization Policy

```python
from app.api_v2_deps.auth import AuthContext
from app.domain.lesson import Lesson

def can_access_lesson(
    auth: AuthContext,
    lesson: Lesson,
) -> bool:
    """
    Check if authenticated user can access a lesson.
    
    Rules:
    - Admin can access any lesson
    - Learner can access their own lessons
    - Guardian can access their linked learner's lessons
    - Teacher can access their assigned learner's lessons
    """
    if auth.is_admin:
        return True
    
    # Direct learner access
    if auth.learner_id and auth.learner_id == lesson.learner_id:
        return True
    
    # Guardian access
    if auth.is_parent and auth.guardian_id:
        # Check guardian-learner relationship
        # This requires repository call
        return guardian_has_learner_relationship(auth.guardian_id, lesson.learner_id)
    
    # Teacher access
    if auth.is_teacher:
        # Check teacher assignment
        # This requires repository call
        return teacher_has_learner_assignment(auth.user_id, lesson.learner_id)
    
    return False
```

---

## Migration Strategy

1. Add ownership verification to service methods:
   - `get_lesson_by_id` should require auth context and verify ownership
   - `complete_lesson` should require auth context and verify ownership
   - `record_feedback` should require auth context and verify ownership

2. Add mixed-learner check to sync route:
   - Verify all lesson IDs belong to same learner
   - Reject mixed-learner payloads

3. Strengthen guardian relationship check:
   - Ensure guardian-learner relationship is verified at database level
   - Add caching for relationship checks

4. Add tests:
   - Learner can access own lesson
   - Learner cannot access another learner's lesson
   - Guardian can access linked learner's lesson
   - Guardian cannot access unrelated learner's lesson
   - Admin can access any lesson
   - Teacher can access assigned learner's lesson
   - Sync route rejects mixed-learner payloads

---

## Test Cases Required

### Unit Tests
1. `test_learner_can_access_own_lesson`
2. `test_learner_cannot_access_other_lesson`
3. `test_guardian_can_access_linked_learner_lesson`
4. `test_guardian_cannot_access_unlinked_learner_lesson`
5. `test_admin_can_access_any_lesson`
6. `test_teacher_can_access_assigned_lesson`
7. `test_sync_rejects_mixed_learner_payload`

### Integration Tests
1. `test_get_lesson_requires_authorization`
2. `test_complete_lesson_requires_authorization`
3. `test_sync_lessons_requires_authorization`
4. `test_service_methods_enforce_ownership`

---

**Created:** 2026-06-01
**Status:** Inventory complete
