"""EduBoost Test System Taxonomy and Classification Registry.

Implements TSR-5.1: Enforce test taxonomy across product, runtime, governance, and release gates.
"""
from __future__ import annotations

import enum
from typing import NamedTuple


class TestClass(str, enum.Enum):
    PRODUCT_UNIT = "product_unit"
    PRODUCT_INTEGRATION = "product_integration"
    RUNTIME_STACK = "runtime_stack"
    GOVERNANCE_CONTRACT = "governance_contract"
    RELEASE_EVIDENCE = "release_evidence"


class TestModuleMetadata(NamedTuple):
    path: str
    classification: TestClass
    description: str
    target_gate: str
    max_duration_seconds: float


TEST_TAXONOMY_MAP: dict[str, TestClass] = {
    "tests/unit": TestClass.PRODUCT_UNIT,
    "tests/integration": TestClass.PRODUCT_INTEGRATION,
    "tests/runtime": TestClass.RUNTIME_STACK,
    "tests/governance": TestClass.GOVERNANCE_CONTRACT,
    "tests/release": TestClass.RELEASE_EVIDENCE,
}


def classify_test_path(path: str) -> TestClass:
    for prefix, cls in TEST_TAXONOMY_MAP.items():
        if path.startswith(prefix):
            return cls
    if "governance" in path or "audit" in path or "contract" in path:
        return TestClass.GOVERNANCE_CONTRACT
    if "integration" in path:
        return TestClass.PRODUCT_INTEGRATION
    return TestClass.PRODUCT_UNIT
