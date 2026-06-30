# PR-004 Auth Usage Inventory

**Date:** 2026-06-01
**Phase:** Phase 1 - Auth Claim Normalization

---

## JWT Implementation Locations

### Core JWT Modules
- `app/core/security.py` - Main JWT create/verify dependency, uses jwt_keyring
- `app/core/token_config.py` - Alternative JWT subsystem with CURRENT_KEY/PREVIOUS_KEY logic
- `app/services/jwt_keyring.py` - Keyring parsing, key rotation, environment validation

### JWT Functions
**From `app/core/security.py`:**
- `create_access_token(payload, extra=None)` - Creates access tokens
- `create_refresh_token()` - Creates refresh tokens
- `decode_token(token)` - Decodes tokens using keyring

**From `app/core/token_config.py`:**
- `create_access_token(user_id, role)` - Alternative access token creation
- `create_refresh_token()` - Alternative refresh token creation (opaque bytes)
- `verify_access_token(token)` - Verifies access tokens

**From `app/services/jwt_keyring.py`:**
- `parse_jwt_keyring(raw=None)` - Parses JWT keyring from environment
- `current_jwt_key(keys=None)` - Gets current signing key
- `current_jwt_signing_key()` - Returns current signing key secret
- `current_jwt_algorithm(default="HS256")` - Returns algorithm
- `current_jwt_headers()` - Returns headers with kid
- `validate_jwt_keyring_environment()` - Validates environment
- `encode_jwt_with_keyring(payload)` - Encodes JWT with keyring
- `decode_jwt_with_keyring(token, options=None)` - Decodes JWT with keyring

### JWT Configuration
- `app/core/config.py` - JWT_SECRET default, validation
- `app/api_v2.py` - Validates JWT keyring environment on startup

---

## current_user Usage Inventory

### Dependency Definition
**Location:** `app/core/security.py`
```python
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
```

### Router Usage (30+ occurrences)

**Routers using `get_current_user`:**
1. `app/api_v2_routers/auth.py` - me, list_sessions, logout, revoke_all
2. `app/api_v2_routers/lessons.py` - generate_lesson, get_lesson, complete_lesson, sync_lessons
3. `app/api_v2_routers/learners.py` - create_learner, get_learner, update_learner, delete_learner
4. `app/api_v2_routers/consent.py` - grant_consent, revoke_consent, get_consent_status
5. `app/api_v2_routers/onboarding.py` - get_onboarding_questions, submit_onboarding_answers
6. `app/api_v2_routers/ether.py` - get_questions
7. `app/api_v2_routers/jobs.py` - job status
8. `app/api_v2_routers/learner_content.py` - get_lessons, get_lessons_by_caps_ref

### Claim Access Patterns

**Common claim accesses:**
- `current_user["sub"]` - User ID (subject)
- `current_user["role"]` - User role
- `current_user.get("role", "")` - Role with default
- `current_user.get("sub") or ""` - Sub with default

**Inconsistent patterns:**
- Some routes use `current_user["sub"]` directly
- Some use `current_user.get("sub")` with default
- Some use `str(current_user["sub"])` for type conversion
- Some use `UUID(str(current_user["sub"]))` for UUID conversion

### Authorization Dependencies

**Additional auth dependencies used:**
- `require_parent_or_admin` - From `app/core.security`
- `require_learner_write_for_current_user` - From `app/security/dependencies`
- `require_learner_read_for_current_user` - From `app/security/dependencies`
- `require_active_consent_for_current_user` - From `app/security/dependencies`
- `require_lesson_read_access_for_current_user` - From `app/services/lesson_authorization`
- `require_lesson_write_access_for_current_user` - From `app/services/lesson_authorization`

---

## Token Usage Inventory

### Token Types
- Access tokens (JWT)
- Refresh tokens (JWT or opaque bytes depending on subsystem)
- Email verification tokens
- Password reset tokens

### Token Storage
- Redis-backed token revocation
- Database fallback for revocation persistence
- Refresh token families with reuse detection

### Token Operations
**From `app/services/auth_service.py`:**
- `verify_email(token)` - Email verification
- `initiate_password_reset(email)` - Password reset initiation
- `complete_password_reset(token, new_password)` - Password reset completion
- `emergency_revoke_all_tokens(initiated_by)` - Global revoke
- `_issue_token_pair(user, family_id=None)` - Token pair issuance

---

## Issues Identified

### 1. Two Competing JWT Subsystems
- `app/core/security.py` uses jwt_keyring
- `app/core/token_config.py` uses CURRENT_KEY/PREVIOUS_KEY
- Both create/verify tokens independently
- Risk: Inconsistent token formats and key resolution

### 2. Inconsistent Claim Access
- No normalized claim structure
- Direct dict access with inconsistent defaults
- Type conversion scattered across routers
- No centralized claim validation

### 3. Missing iss/aud Claims
- Access tokens lack issuer (iss) claim
- Access tokens lack audience (aud) claim
- Risk: Token replay across environments

### 4. Auth Logic in Routers
- `app/api_v2_routers/auth.py` contains registration/login logic inline
- Email encryption handled incorrectly (raw email stored in encrypted field)
- Inconsistent token claims between register, login, dev-session, refresh

### 5. No Minimum Key Length Enforcement
- Placeholder guard catches obvious placeholders
- No enforcement of minimum key length (≥32 chars for HS256)

---

## Recommended AuthContext Structure

```python
from pydantic import BaseModel
from typing import Any, Optional
from enum import Enum

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class UserRole(str, Enum):
    PARENT = "parent"
    TEACHER = "teacher"
    ADMIN = "admin"
    STUDENT = "student"

class AuthContext(BaseModel):
    """Normalized authentication context from JWT claims."""
    
    user_id: str
    guardian_id: Optional[str] = None
    learner_id: Optional[str] = None
    roles: list[UserRole] = []
    token_type: TokenType
    raw_claims: dict[str, Any]
    
    # Convenience accessors
    @property
    def is_admin(self) -> bool:
        return UserRole.ADMIN in self.roles
    
    @property
    def is_parent(self) -> bool:
        return UserRole.PARENT in self.roles
    
    @property
    def is_teacher(self) -> bool:
        return UserRole.TEACHER in self.roles
    
    @property
    def is_student(self) -> bool:
        return UserRole.STUDENT in self.roles
```

---

## Migration Strategy

1. Create `app/api_v2_deps/auth.py` with `AuthContext` and dependency
2. Update `get_current_user` to return `AuthContext` instead of dict
3. Add backward compatibility layer for existing dict access
4. Migrate routers incrementally to use typed `AuthContext`
5. Remove dict compatibility layer after migration complete

---

**Created:** 2026-06-01
**Status:** Inventory complete
