from __future__ import annotations

import dataclasses
from datetime import date
import importlib
import inspect
from collections.abc import Iterable
from enum import Enum
from typing import Any

import pytest


READINESS_MODULES = (
    "app.modules.beta_launch.production_readiness_contracts",
    "app.modules.billing.production_readiness_contracts",
    "app.modules.deployment.production_readiness_contracts",
    "app.modules.disaster_recovery.production_readiness_contracts",
    "app.modules.documentation_governance.production_readiness_contracts",
    "app.modules.final_release_blockers.production_readiness_contracts",
    "app.modules.notifications.production_readiness_contracts",
    "app.modules.observability.production_readiness_contracts",
    "app.modules.operations_support.production_readiness_contracts",
    "app.modules.quality_gates.production_readiness_contracts",
    "app.modules.roadmap.production_readiness_contracts",
    "app.modules.security_posture.production_readiness_contracts",
)

FIXED_TODAY = date(2026, 6, 1)


def _iter_default_contracts(module: Any) -> Iterable[Any]:
    for name in dir(module):
        if not name.startswith("DEFAULT_"):
            continue
        value = getattr(module, name)
        if dataclasses.is_dataclass(value) and hasattr(value, "validate"):
            yield value
        elif isinstance(value, tuple):
            for item in value:
                if dataclasses.is_dataclass(item) and hasattr(item, "validate"):
                    yield item


def _negative_values(value: Any) -> list[Any]:
    if isinstance(value, bool):
        return [False] if value else []
    if isinstance(value, int) and not isinstance(value, bool):
        return [0] if value > 0 else []
    if isinstance(value, str):
        return [""] if value else []
    if isinstance(value, tuple):
        return [()] if value else []
    if isinstance(value, Enum):
        return [candidate for candidate in type(value) if candidate != value]
    return []


def _invalid_variants(contract: Any) -> Iterable[Any]:
    for field in dataclasses.fields(contract):
        for replacement in _negative_values(getattr(contract, field.name)):
            yield dataclasses.replace(contract, **{field.name: replacement})


def _validate(contract: Any) -> list[str]:
    validate = contract.validate
    signature = inspect.signature(validate)
    if "today" in signature.parameters:
        return validate(today=FIXED_TODAY)
    return validate()


@pytest.mark.unit
@pytest.mark.parametrize("module_name", READINESS_MODULES)
def test_default_readiness_reports_remain_release_clean(module_name: str) -> None:
    module = importlib.import_module(module_name)
    report_names = [
        name
        for name in dir(module)
        if name.startswith("default_") and name.endswith("_readiness_report")
    ]

    assert report_names, f"{module_name} must expose a default readiness report"
    for report_name in report_names:
        report = getattr(module, report_name)()
        issue_fields = {
            key: value
            for key, value in report.items()
            if key.endswith("_issues") or key.endswith("_errors")
        }
        assert issue_fields, f"{module_name}.{report_name} must expose issue fields"
        assert {
            key: value
            for key, value in issue_fields.items()
            if value
        } == {}


@pytest.mark.unit
@pytest.mark.parametrize("module_name", READINESS_MODULES)
def test_readiness_contracts_fail_closed_for_malformed_evidence(module_name: str) -> None:
    module = importlib.import_module(module_name)
    contracts = list(_iter_default_contracts(module))

    assert contracts, f"{module_name} must expose default contract records"
    for contract in contracts:
        assert _validate(contract) == []
        variants = list(_invalid_variants(contract))
        assert variants, f"{contract.__class__.__name__} must have mutable release gates"
        variant_issues = [_validate(variant) for variant in variants]
        assert any(variant_issues), (
            f"{contract.__class__.__name__} must reject at least one malformed "
            "release-readiness evidence variant"
        )
