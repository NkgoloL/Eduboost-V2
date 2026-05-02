from app.core.judiciary import ConstitutionalViolation, JudiciaryService, LessonPayload, StudyPlanPayload

JudiciaryValidationError = ConstitutionalViolation

__all__ = [
    "ConstitutionalViolation",
    "JudiciaryService",
    "JudiciaryValidationError",
    "LessonPayload",
    "StudyPlanPayload",
]
