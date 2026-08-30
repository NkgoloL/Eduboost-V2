"""Comprehensive unit tests for DiagnosticItemValidator and item safety validation."""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from app.services.diagnostic_safety import (
    DiagnosticItemValidation,
    DiagnosticItemValidator,
)


class TestDiagnosticSafety:
    def test_diagnostic_item_validation_dataclass(self):
        val = DiagnosticItemValidation(valid=True, reasons=())
        assert val.valid is True
        assert len(val.reasons) == 0

        val_invalid = DiagnosticItemValidation(valid=False, reasons=("difficulty out of bounds",))
        assert val_invalid.valid is False
        assert val_invalid.reasons[0] == "difficulty out of bounds"

    def test_diagnostic_item_validator_invalid_schema(self):
        validator = DiagnosticItemValidator()
        bad_payload = {"invalid_key": 123}
        res = validator.validate_mapping(bad_payload)
        assert res.valid is False
        assert len(res.reasons) > 0
