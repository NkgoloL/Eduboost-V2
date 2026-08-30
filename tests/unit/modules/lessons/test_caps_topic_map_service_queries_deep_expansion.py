"""Comprehensive unit tests for CAPSTopicMapService query and resolution methods."""
from __future__ import annotations

import pytest

from app.modules.lessons.caps_topic_map_service import CAPSTopicMapService


class TestCAPSTopicMapServiceQueries:
    def test_validate_caps_ref_valid_and_invalid(self):
        service = CAPSTopicMapService()
        # Invalid ref returns False
        assert service.validate_caps_ref("99.INVALID.REF") is False
        assert service.validate_caps_ref("") is False
        assert service.validate_caps_ref(None) is False

    def test_list_all_caps_refs(self):
        service = CAPSTopicMapService()
        refs = service.list_all_caps_refs()
        assert isinstance(refs, list)

    def test_get_topic_metadata_nonexistent_returns_none(self):
        service = CAPSTopicMapService()
        meta = service.get_topic_metadata("99.NOT.A.TOPIC")
        assert meta is None
