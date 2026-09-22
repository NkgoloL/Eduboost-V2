import json
from pathlib import Path
import pytest
from scripts.educational_validation.generate_synthetic_validation_cohort import generate_cohort


def test_synthetic_cohort_generation():
    data = generate_cohort(learner_count=50, seed=123)
    assert data["evidence_type"] == "synthetic_fixture"
    assert data["learner_count"] == 50
    assert len(data["learners"]) == 50
    assert len(data["events"]) == 50 * 20  # 5 concepts * 4 items
    assert len(data["impact_records"]) == 50
    assert len(data["retention_records"]) == 50 * 4  # 4 spaced intervals
    assert len(data["transfer_records"]) == 50 * 2  # near + far transfer


def test_synthetic_cohort_event_schema():
    import jsonschema  # type: ignore

    repo_root = Path(__file__).resolve().parents[3]
    schema_path = repo_root / "docs/roadmap/production_readiness/lev/schemas/interaction_event.schema.json"
    assert schema_path.exists(), f"Schema not found: {schema_path}"

    schema = json.loads(schema_path.read_text())
    data = generate_cohort(learner_count=10, seed=999)

    for event in data["events"]:
        jsonschema.validate(instance=event, schema=schema)
