import json
from pathlib import Path

from scripts.build_guardrails_dataset import build_records, run as run_guardrails
from scripts.sync_caps_r2 import iter_local_items


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def test_build_guardrails_records_include_pedagogical_safety_categories():
    records = build_records()

    categories = {record["category"] for record in records}
    assert "popia_safety" in categories
    assert "age_appropriate_language" in categories
    assert all(record["instruction"] and record["output"] for record in records)


def test_guardrails_can_be_combined_with_base_dataset(tmp_path: Path):
    base = tmp_path / "base.jsonl"
    output = tmp_path / "guardrails.jsonl"
    combined = tmp_path / "combined.jsonl"
    base.write_text(json.dumps({"instruction": "Base", "output": "Record"}) + "\n", encoding="utf-8")

    run_guardrails(Args(output=str(output), base_dataset=str(base), combined_output=str(combined), combine=True))

    lines = [json.loads(line) for line in combined.read_text(encoding="utf-8").splitlines()]
    assert lines[0]["instruction"] == "Base"
    assert any(line.get("source") == "pedagogical_guardrail" for line in lines)


def test_iter_local_items_builds_r2_keys(tmp_path: Path):
    local = tmp_path / "caps"
    (local / "nested").mkdir(parents=True)
    (local / "nested" / "training.jsonl").write_text("{}\n", encoding="utf-8")

    items = iter_local_items(local, "training-data/caps-curated")

    assert len(items) == 1
    assert items[0].key == "training-data/caps-curated/nested/training.jsonl"
