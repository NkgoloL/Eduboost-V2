"""
EduBoost V2 — Authorization Policies

Canonical authorization policy functions for object-level access control.
These policies enforce that users can only access resources they are authorized to see or modify.
"""
from __future__ import annotations


from fastapi import HTTPException, status

from app.api_v2_deps.auth import AuthContext
from app.domain.lesson import Lesson
from app.domain.learner import Learner


def can_access_lesson(
    auth: AuthContext,
    lesson: Lesson,
) -> bool:
    """
    Check if authenticated user can access a lesson.
    
    Authorization rules:
    - Admin can access any lesson
    - Learner can access their own lessons
    - Guardian can access their linked learner's lessons
    - Teacher can access their assigned learner's lessons
    
    Args:
        auth: The authenticated user context
        lesson: The lesson being accessed
        
    Returns:
        True if access is allowed, False otherwise
    """
    # Admin bypass
    if auth.is_admin:
        return True

    # Direct learner access
    if auth.learner_id and auth.learner_id == lesson.learner_id:
        return True

    # Guardian access (requires relationship check)
    if auth.is_parent and auth.guardian_id:
        # Check if guardian is linked to the lesson's learner
        # This requires repository call - handled by caller
        return _guardian_has_learner_relationship(auth.guardian_id, lesson.learner_id)

    # Teacher access (requires assignment check)
    if auth.is_teacher:
        # Check if teacher is assigned to the lesson's learner
        # This requires repository call - handled by caller
        return _teacher_has_learner_assignment(auth.user_id, lesson.learner_id)

    return False


def can_write_lesson(
    auth: AuthContext,
    lesson: Lesson,
) -> bool:
    """
    Check if authenticated user can write to a lesson (complete, add feedback).
    
    Write access is more restrictive than read access:
    - Admin can write to any lesson
    - Learner can write to their own lessons
    - Guardian cannot write to lessons (read-only)
    - Teacher cannot write to lessons (read-only)
    
    Args:
        auth: The authenticated user context
        lesson: The lesson being written to
        
    Returns:
        True if write access is allowed, False otherwise
    """
    # Admin bypass
    if auth.is_admin:
        return True

    # Only the learner who owns the lesson can write to it
    if auth.learner_id and auth.learner_id == lesson.learner_id:
        return True

    # Guardians and teachers have read-only access
    return False


def can_access_learner(
    auth: AuthContext,
    learner: Learner,
) -> bool:
    """
    Check if authenticated user can access a learner's data.
    
    Authorization rules:
    - Admin can access any learner
    - Learner can access their own data
    - Guardian can access their linked learner's data
    - Teacher can access their assigned learner's data
    
    Args:
        auth: The authenticated user context
        learner: The learner being accessed
        
    Returns:
        True if access is allowed, False otherwise
    """
    # Admin bypass
    if auth.is_admin:
        return True

    # Direct learner access
    if auth.learner_id and auth.learner_id == str(learner.id):
        return True

    # Guardian access
    if auth.is_parent and auth.guardian_id:
        return str(learner.guardian_id) == auth.guardian_id

    # Teacher access (requires assignment check)
    if auth.is_teacher:
        # This requires repository call - handled by caller
        return _teacher_has_learner_assignment(auth.user_id, str(learner.id))

    return False


def can_write_learner(
    auth: AuthContext,
    learner: Learner,
) -> bool:
    """
    Check if authenticated user can write to a learner's data.
    
    Write access rules:
    - Admin can write to any learner
    - Guardian can write to their linked learner's data
    - Learner cannot write to their own learner record (read-only)
    - Teacher cannot write to learner records (read-only)
    
    Args:
        auth: The authenticated user context
        learner: The learner being written to
        
    Returns:
        True if write access is allowed, False otherwise
    """
    # Admin bypass
    if auth.is_admin:
        return True

    # Only guardian can write to learner record
    if auth.is_parent and auth.guardian_id:
        return str(learner.guardian_id) == auth.guardian_id

    return False


def require_lesson_access(auth: AuthContext, lesson: Lesson) -> None:
    """
    Raise HTTP 403 if user cannot access the lesson.
    
    This is a convenience wrapper for use in route handlers.
    
    Args:
        auth: The authenticated user context
        lesson: The lesson being accessed
        
    Raises:
        HTTPException 403: If access is denied
    """
    if not can_access_lesson(auth, lesson):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this lesson",
        )


def require_lesson_write(auth: AuthContext, lesson: Lesson) -> None:
    """
    Raise HTTP 403 if user cannot write to the lesson.
    
    This is a convenience wrapper for use in route handlers.
    
    Args:
        auth: The authenticated user context
        lesson: The lesson being written to
        
    Raises:
        HTTPException 403: If write access is denied
    """
    if not can_write_lesson(auth, lesson):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this lesson",
        )


def require_learner_access(auth: AuthContext, learner: Learner) -> None:
    """
    Raise HTTP 403 if user cannot access the learner.
    
    This is a convenience wrapper for use in route handlers.
    
    Args:
        auth: The authenticated user context
        learner: The learner being accessed
        
    Raises:
        HTTPException 403: If access is denied
    """
    if not can_access_learner(auth, learner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this learner",
        )


def require_learner_write(auth: AuthContext, learner: Learner) -> None:
    """
    Raise HTTP 403 if user cannot write to the learner.
    
    This is a convenience wrapper for use in route handlers.
    
    Args:
        auth: The authenticated user context
        learner: The learner being written to
        
    Raises:
        HTTPException 403: If write access is denied
    """
    if not can_write_learner(auth, learner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this learner",
        )


# ── Repository-level checks (to be implemented by caller) ───────────────────────

def _guardian_has_learner_relationship(guardian_id: str, learner_id: str) -> bool:
    """
    Check if guardian has a relationship with the learner.
    
    This is a placeholder for the actual repository check.
    The caller should implement this using the appropriate repository.
    
    Args:
        guardian_id: The guardian's user ID
        learner_id: The learner's ID
        
    Returns:
        True if guardian is linked to learner, False otherwise
    """
    # TODO: Implement repository check
    # This should query the guardians table to verify the relationship
    return False


def _teacher_has_learner_assignment(teacher_id: str, learner_id: str) -> bool:
    """
    Check if teacher has an assignment with the learner.
    
    This is a placeholder for the actual repository check.
    The caller should implement this using the appropriate repository.
    
    Args:
        teacher_id: The teacher's user ID
        learner_id: The learner's ID
        
    Returns:
        True if teacher is assigned to learner, False otherwise
    """
    # TODO: Implement repository check
    # This should query the teacher-learner assignment table
    return False


__all__ = [
    "can_access_lesson",
    "can_write_lesson",
    "can_access_learner",
    "can_write_learner",
    "require_lesson_access",
    "require_lesson_write",
    "require_learner_access",
    "require_learner_write",
]
