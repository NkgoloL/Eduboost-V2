from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_dev_session_seeds_real_irt_items_for_backend_backed_e2e() -> None:
    source = read("app/services/auth_lifecycle_impl.py")
    seed_source = read("app/services/dev_diagnostic_seed.py")

    assert "seed_dev_diagnostic_items" in source
    assert "await seed_dev_diagnostic_items" in source
    assert "DEV_DIAGNOSTIC_ITEMS" in seed_source
    assert "00000000-0000-4000-8000-000000160301" in seed_source
    assert '"options": [{"key": key, "label": value}' in seed_source


def test_diagnostic_items_route_serialises_backend_options_and_subject_codes() -> None:
    source = read("app/api_v2_routers/diagnostics.py")

    assert "def _option_payload" in source
    assert '"options": options' in source
    assert '"option_keys": [option["key"] for option in options]' in source
    assert '"subject": _subject_code(item.subject)' in source
    assert '"item_id": str(item.item_id)' in source


def test_frontend_diagnostic_service_accepts_legacy_and_record_option_shapes() -> None:
    source = read("app/frontend/src/lib/api/services.ts")

    assert "const normalizeDiagnosticOptions" in source
    assert "labels: string[]" in source
    assert "keys: string[]" in source
    assert "option_keys: item.option_keys?.length ? item.option_keys : normalizedOptions.keys" in source


def test_interactive_diagnostic_submits_answer_keys_not_display_labels() -> None:
    source = read("app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx")

    assert "const optionKey = currentItem.option_keys?.[index] || String.fromCharCode(65 + index);" in source
    assert "selected_option: optionKey" in source
    assert "onClick={() => void handleAnswer(option, index)}" in source
    assert "{option}" in source
