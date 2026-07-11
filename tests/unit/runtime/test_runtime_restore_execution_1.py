from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_runtime_collector_uses_current_interpreter_for_python_gates():
    text = (ROOT / "scripts/production_readiness/collect_prd1100r_true_state_runtime_baseline.py").read_text()
    assert "import sys" in text
    assert '[sys.executable, "scripts/generate_openapi.py", "--check"]' in text
    assert '[sys.executable, "scripts/generate_route_inventory.py", "--check"]' in text
    assert '[sys.executable, "-m", "pytest", "tests/unit"' in text
    assert '[sys.executable, "-m", "pytest", "tests/integration"' in text
    assert '[sys.executable, "-m", "pip_audit"' in text


def test_runtime_stack_verifier_uses_current_interpreter_for_py_compile():
    text = (ROOT / "scripts/runtime/verify_runtime_stack_readiness.py").read_text()
    assert "import sys" in text
    assert "sys.executable" in text


def test_learner_layout_hook_order_is_not_conditional():
    text = (ROOT / "app/frontend/src/app/(learner)/layout.tsx").read_text()
    assert "const isParentRoute = pathname.startsWith" in text
    assert "if (!learner && !isParentRoute)" in text
    assert text.index("useEffect(() =>") < text.index("if (isParentRoute)")
