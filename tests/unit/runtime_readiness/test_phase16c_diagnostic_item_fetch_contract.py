from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_dev_session_seeds_real_irt_items_for_backend_backed_e2e() -> None:
    source = read("app/services/auth_lifecycle_impl.py")
    seed_source = read("app/services/dev_diagnostic_seed.py")

    assert "ensure_dev_diagnostic_items" in source
    assert "seeded_diagnostic_item_ids = await ensure_dev_diagnostic_items" in source
    assert "diagnostic_seed" in source
    assert "IRTItem(" in seed_source
    assert "dev-diagnostic-g{grade}-math-001" in seed_source
    assert "subject=seed.subject" in seed_source
    assert "review_status=ItemReviewStatus.AI_GENERATED" in seed_source


def test_diagnostic_items_route_serialises_backend_options_and_subject_codes() -> None:
    source = read("app/api_v2_routers/diagnostics.py")

    assert "def _normalise_option_labels" in source
    assert "def _subject_code" in source
    assert '"Mathematics": "MATH"' in source
    assert "_serialise_canonical_item" in source
    assert "_serialise_irt_item" in source
    assert '"options": _normalise_option_labels(item.options)' in source
    assert '"item_id": item.id' in source


def test_frontend_diagnostic_service_accepts_legacy_and_record_option_shapes() -> None:
    source = read("app/frontend/src/lib/api/services.ts")

    assert "type DiagnosticOptionPayload" in source
    assert "function normalizeDiagnosticOptions" in source
    assert 'return ["A", "B", "C", "D"]' in source
    assert "options: normalizeDiagnosticOptions(item.options)" in source


def test_interactive_diagnostic_submits_answer_keys_not_display_labels() -> None:
    source = read("app/frontend/src/components/eduboost/InteractiveDiagnostic.tsx")

    assert "const optionKey = String.fromCharCode(65 + index);" in source
    assert "onClick={() => void handleAnswer(optionKey)}" in source
    assert "{optionKey}" in source
    assert "{option}" in source
