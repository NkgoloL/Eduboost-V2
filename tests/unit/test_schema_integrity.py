from scripts.validate_schema_integrity import main as validate_schema_integrity


def test_schema_integrity_baseline() -> None:
    assert validate_schema_integrity() == 0
