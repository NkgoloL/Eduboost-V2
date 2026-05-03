"""Repository abstractions for EduBoost V2."""

from app.repositories.assessment_repository import AssessmentRepository
from app.repositories.auth_repository import AuthRepository, GuardianRepository
from app.repositories.consent_repository import ConsentRepository
from app.repositories.diagnostic_repository import DiagnosticRepository
from app.repositories.gamification_repository import GamificationRepository
from app.repositories.learner_repository import LearnerRepository
from app.repositories.lesson_repository import LessonRepository

__all__ = [
    "AssessmentRepository",
    "AuthRepository",
    "ConsentRepository",
    "DiagnosticRepository",
    "GamificationRepository",
    "GuardianRepository",
    "LearnerRepository",
    "LessonRepository",
]
