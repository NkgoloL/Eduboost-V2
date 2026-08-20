# Diagnostic Item-Bank Policy Status

Generated at: `2026-08-19T19:13:29Z`
Commit: `d5ae429bdec24b4d0123ea3362323fa3e4f25e4b`

**Status:** `diagnostic-item-bank-policy-accepted`
**Policy:** `docs/architecture/diagnostic_item_bank_canonicality.yml`
**Decision:** `diagnostic_items-runtime-required`
**Canonical table:** `diagnostic_items`
**Supporting table:** `irt_items`
**Unresolved blocker:** `DIAG-SCORE-001`

## Policy markers

| Marker | Present |
|---|---:|
| `decision: diagnostic_items-runtime-required` | True |
| `canonical_item_bank: diagnostic_items` | True |
| `supporting_item_bank: irt_items` | True |
| `classification: runtime-required` | True |
| `expected_min_rows: 1` | True |
| `beta_blocking_when_empty: true` | True |
| `migration_action: seed-required` | True |
| `unresolved_blocker: DIAG-SCORE-001` | True |

## Runtime diagnostic_items references

| Path | Line | Excerpt |
|---|---:|---|
| `app/api_v2_routers/content_factory.py` | 1077 | `diagnostic_items = await service.get_diagnostic_items(session, scope_id=scope_id, caps_ref=caps_ref)` |
| `app/api_v2_routers/content_factory.py` | 1079 | `return {"diagnostic_items": diagnostic_items, "lessons": lessons}` |
| `app/api_v2_routers/content_factory.py` | 1100 | `run_metadata={"layers": ["diagnostic_items", "lessons", "assessment_blueprints", "study_plan_templates"]},` |
| `app/core/runtime_readiness.py` | 23 | `"diagnostic_items",` |
| `app/core/runtime_readiness.py` | 37 | `"diagnostic_items": (` |
| `app/domain/content_coverage.py` | 11 | `DIAGNOSTIC_ITEMS = "diagnostic_items"` |
| `app/domain/curriculum_expansion_schemas.py` | 17 | `layers: list[str] = Field(default_factory=lambda: ["diagnostic_items", "lessons"], min_length=1, max_length=8)` |
| `app/models/content_factory.py` | 59 | `DIAGNOSTIC_ITEMS = "diagnostic_items"` |
| `app/models/diagnostic_item.py` | 111 | `ORM representation of the diagnostic_items table.` |
| `app/models/diagnostic_item.py` | 117 | `__tablename__ = "diagnostic_items"` |
| `app/models/irt_quality.py` | 48 | `ForeignKey("diagnostic_items.item_id", ondelete="RESTRICT"), nullable=False` |
| `app/models/item_exposure.py` | 58 | `ForeignKey("diagnostic_items.item_id", ondelete="RESTRICT"),` |
| `app/services/content_answer_key_verification.py` | 112 | `if layer != "diagnostic_items" and artifact_type != "diagnostic_item":` |
| `app/services/content_file_artifact_import.py` | 29 | `"diagnostic_items": (ContentLayer.DIAGNOSTIC_ITEMS, ContentArtifactType.DIAGNOSTIC_ITEM, "items"),` |
| `app/services/content_file_promotion_readiness.py` | 22 | `"diagnostic_items": "diagnostic_items",` |
| `app/services/content_file_promotion_readiness.py` | 252 | `if layer == "diagnostic_items":` |
| `app/services/content_generation/providers/llm.py` | 169 | `values = payload.get("diagnostic_items")` |
| `app/services/content_generation/scope_blueprint_generator.py` | 80 | `"source_item_bank": "diagnostic_items",` |
| `app/services/content_review_governance.py` | 355 | `if _value(artifact.artifact_type) == "diagnostic_item" or _value(artifact.content_layer) == "diagnostic_items":` |
| `app/services/content_review_governance.py` | 545 | `or _value(artifact.content_layer) == "diagnostic_items"` |
| `app/services/curriculum/coverage.py` | 24 | `def detect_gaps(self, *, lessons: Iterable[Mapping[str, Any]], diagnostic_items: Iterable[Mapping[str, Any]]) -> list[CurriculumGap]:` |
| `app/services/curriculum/coverage.py` | 27 | `item_refs = {row.get("caps_reference") for row in diagnostic_items if row.get("caps_reference")}` |
| `app/services/curriculum_expansion.py` | 177 | `if _enum_value(artifact.content_layer) == "diagnostic_items" and not artifact.answer_key_verified:` |
| `app/services/launch_content_seed.py` | 48 | `item_bank_path = _artifact_path(scope, "diagnostic_items", "data/generated/items/grade4_maths_launch_item_bank.json")` |
| `app/services/launch_content_seed.py` | 66 | `item_target = _target_for(scope, "diagnostic_items.approved", DEFAULT_ITEM_TARGET, registry=registry)` |

## Blockers

- None

## No false-closure rules

- This policy does not close DIAG-SCORE-001.
- Empty `diagnostic_items` remains beta-blocking under DIAG-SCORE-001.
- This policy does not seed `diagnostic_items`.
- This policy does not prove scoring quality, item exposure correctness, or adaptive recommendation behavior.
- This policy supersedes the earlier attempted `irt_items`-canonical-only classification.
