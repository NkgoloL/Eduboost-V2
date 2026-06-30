"""tests/unit/test_content_factory_enums.py

Validates that the Python ORM enum definitions in app.models.content_factory
are in agreement with the canonical enum contracts declared in the centralized
schema contract module.

User rule: "Enum compatibility must account for string-backed enums... don't
fail merely because a column is stored as VARCHAR."

These tests are purely static (no DB required) and compare .value strings.
"""
from __future__ import annotations


from scripts.ci.content_factory_schema_contract import ENUM_CONTRACTS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _enum_values(enum_cls) -> set[str]:
    """Return the set of .value strings for any str-based Python Enum."""
    return {member.value for member in enum_cls}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestContentArtifactStatusEnum:
    """ContentArtifactStatus must match the contract exactly."""

    def test_all_contract_values_present_in_orm(self):
        from app.models.content_factory import ContentArtifactStatus

        contract_values = set(ENUM_CONTRACTS["content_artifact_status"])
        orm_values = _enum_values(ContentArtifactStatus)

        missing = contract_values - orm_values
        assert not missing, (
            f"ContentArtifactStatus is missing values declared in the schema contract: "
            f"{missing!r}. Update the ORM enum or the contract."
        )

    def test_no_undeclared_orm_values(self):
        from app.models.content_factory import ContentArtifactStatus

        contract_values = set(ENUM_CONTRACTS["content_artifact_status"])
        orm_values = _enum_values(ContentArtifactStatus)

        extra = orm_values - contract_values
        assert not extra, (
            f"ContentArtifactStatus has values not declared in the schema contract: "
            f"{extra!r}. Add them to the contract or remove from the ORM."
        )

    def test_enum_members_are_lowercase_strings(self):
        from app.models.content_factory import ContentArtifactStatus

        for member in ContentArtifactStatus:
            assert member.value == member.value.lower(), (
                f"ContentArtifactStatus.{member.name} value {member.value!r} "
                "is not lowercase. DB values should be lowercase strings."
            )

    def test_enum_is_str_backed(self):
        from app.models.content_factory import ContentArtifactStatus

        assert issubclass(ContentArtifactStatus, str), (
            "ContentArtifactStatus must be a str-backed enum (class … str, enum.Enum) "
            "so VARCHAR columns can store/compare values without casting."
        )


class TestContentLayerEnum:
    """ContentLayer must match the contract exactly."""

    def test_all_contract_values_present_in_orm(self):
        from app.models.content_factory import ContentLayer

        contract_values = set(ENUM_CONTRACTS["content_layer"])
        orm_values = _enum_values(ContentLayer)
        missing = contract_values - orm_values
        assert not missing, (
            f"ContentLayer is missing contract values: {missing!r}"
        )

    def test_no_undeclared_orm_values(self):
        from app.models.content_factory import ContentLayer

        contract_values = set(ENUM_CONTRACTS["content_layer"])
        orm_values = _enum_values(ContentLayer)
        extra = orm_values - contract_values
        assert not extra, (
            f"ContentLayer has undeclared values: {extra!r}"
        )

    def test_enum_is_str_backed(self):
        from app.models.content_factory import ContentLayer
        assert issubclass(ContentLayer, str)


class TestContentArtifactTypeEnum:
    """ContentArtifactType must match the contract exactly."""

    def test_all_contract_values_present_in_orm(self):
        from app.models.content_factory import ContentArtifactType

        contract_values = set(ENUM_CONTRACTS["content_artifact_type"])
        orm_values = _enum_values(ContentArtifactType)
        missing = contract_values - orm_values
        assert not missing, (
            f"ContentArtifactType is missing contract values: {missing!r}"
        )

    def test_no_undeclared_orm_values(self):
        from app.models.content_factory import ContentArtifactType

        contract_values = set(ENUM_CONTRACTS["content_artifact_type"])
        orm_values = _enum_values(ContentArtifactType)
        extra = orm_values - contract_values
        assert not extra, (
            f"ContentArtifactType has undeclared values: {extra!r}"
        )

    def test_enum_is_str_backed(self):
        from app.models.content_factory import ContentArtifactType
        assert issubclass(ContentArtifactType, str)


class TestContentReviewActionEnum:
    """ContentReviewAction must match the contract exactly."""

    def test_all_contract_values_present_in_orm(self):
        from app.models.content_factory import ContentReviewAction

        contract_values = set(ENUM_CONTRACTS["content_review_action"])
        orm_values = _enum_values(ContentReviewAction)
        missing = contract_values - orm_values
        assert not missing, (
            f"ContentReviewAction is missing contract values: {missing!r}"
        )

    def test_no_undeclared_orm_values(self):
        from app.models.content_factory import ContentReviewAction

        contract_values = set(ENUM_CONTRACTS["content_review_action"])
        orm_values = _enum_values(ContentReviewAction)
        extra = orm_values - contract_values
        assert not extra, (
            f"ContentReviewAction has undeclared values: {extra!r}"
        )

    def test_enum_is_str_backed(self):
        from app.models.content_factory import ContentReviewAction
        assert issubclass(ContentReviewAction, str)


class TestContentScopeStatusEnum:
    """ContentScopeStatus must match the contract exactly."""

    def test_all_contract_values_present_in_orm(self):
        from app.models.content_factory import ContentScopeStatus

        contract_values = set(ENUM_CONTRACTS["content_scope_status"])
        orm_values = _enum_values(ContentScopeStatus)
        missing = contract_values - orm_values
        assert not missing, (
            f"ContentScopeStatus is missing contract values: {missing!r}"
        )

    def test_no_undeclared_orm_values(self):
        from app.models.content_factory import ContentScopeStatus

        contract_values = set(ENUM_CONTRACTS["content_scope_status"])
        orm_values = _enum_values(ContentScopeStatus)
        extra = orm_values - contract_values
        assert not extra, (
            f"ContentScopeStatus has undeclared values: {extra!r}"
        )

    def test_enum_is_str_backed(self):
        from app.models.content_factory import ContentScopeStatus
        assert issubclass(ContentScopeStatus, str)


class TestEnumContractCoverage:
    """Meta-test: all enum contract keys must be tested above."""

    _TESTED_KEYS = {
        "content_artifact_status",
        "content_layer",
        "content_artifact_type",
        "content_review_action",
        "content_scope_status",
    }

    def test_all_contract_keys_are_tested(self):
        contract_keys = set(ENUM_CONTRACTS.keys())
        untested = contract_keys - self._TESTED_KEYS
        assert not untested, (
            f"These enum contract keys have no dedicated test class: {untested!r}. "
            "Add a test class above and include the key in _TESTED_KEYS."
        )
