import pytest

from app.services.diagnostic import DiagnosticEngine, p_correct, update_theta_mle
from app.services.ether import EtherService
from app.services.executive import ExecutiveService
from app.services.fourth_estate import FourthEstateService
from app.services.judiciary import ConstitutionalViolation, JudiciaryService, LessonPayload
from app.services.lesson_generator import LessonGenerator, QuotaExceededError


def test_service_compatibility_shims():
    # Diagnostic shim
    assert DiagnosticEngine is not None
    assert callable(p_correct)
    assert callable(update_theta_mle)

    # Ether shim
    assert EtherService is not None

    # Executive shim
    assert ExecutiveService is not None

    # Fourth Estate shim
    assert FourthEstateService is not None

    # Judiciary shim
    assert ConstitutionalViolation is not None
    assert JudiciaryService is not None
    assert LessonPayload is not None

    # Lesson generator shim
    assert LessonGenerator is not None
    assert QuotaExceededError is not None
