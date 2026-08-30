import pytest

from app.services.content_review_governance import (
    _rubric_passed,
    _value,
    _env_bool,
    ReviewConflictError,
)
from app.models.content_factory import ContentReviewAction


def test_rubric_passed_coercions():
    assert _rubric_passed(True) is True
    assert _rubric_passed(False) is False
    assert _rubric_passed(0.85) is True
    assert _rubric_passed(0.75) is False
    assert _rubric_passed("PASSED") is True
    assert _rubric_passed("failed") is False
    assert _rubric_passed({"result": "passed"}) is True
    assert _rubric_passed({"passed": True}) is True
    assert _rubric_passed(None) is False


def test_value_and_env_bool(monkeypatch):
    assert _value(ContentReviewAction.APPROVE) == "approve"
    assert _value("plain") == "plain"

    monkeypatch.setenv("TEST_FLAG", "1")
    assert _env_bool("TEST_FLAG", False) is True
    monkeypatch.setenv("TEST_FLAG", "false")
    assert _env_bool("TEST_FLAG", True) is False
    assert _env_bool("UNSET_FLAG", True) is True


def test_review_conflict_error():
    err = ReviewConflictError("Version conflict")
    assert isinstance(err, ValueError)
    assert str(err) == "Version conflict"
