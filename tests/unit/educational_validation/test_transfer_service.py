import numpy as np
import pytest

from app.services.educational_validation.transfer import (
    TransferType,
    compute_transfer_matrix,
    evaluate_transfer_validity,
)


def test_evaluate_transfer_validity_near_valid():
    np.random.seed(42)
    source = np.random.uniform(0.4, 0.9, 50)
    # High correlation near transfer
    target = source * 0.9 + np.random.normal(0, 0.05, 50)
    res = evaluate_transfer_validity(
        source, target, "math.add", "math.sub", TransferType.NEAR, min_correlation=0.30
    )
    assert res.is_transfer_valid
    assert res.pearson_r > 0.50
    assert res.unsupported_warning is None


def test_evaluate_transfer_validity_unsupported():
    np.random.seed(42)
    source = np.random.uniform(0.4, 0.9, 50)
    # Zero correlation
    target = np.random.uniform(0.1, 0.9, 50)
    res = evaluate_transfer_validity(
        source, target, "math.add", "science.plants", TransferType.NEAR, min_correlation=0.30
    )
    assert not res.is_transfer_valid
    assert res.unsupported_warning is not None


def test_compute_transfer_matrix():
    records = [
        {"source_concept_id": "c1", "target_concept_id": "c2", "transfer_type": "near", "source_score": 0.8, "target_score": 0.75},
        {"source_concept_id": "c1", "target_concept_id": "c2", "transfer_type": "near", "source_score": 0.6, "target_score": 0.62},
        {"source_concept_id": "c1", "target_concept_id": "c2", "transfer_type": "near", "source_score": 0.7, "target_score": 0.68},
        {"source_concept_id": "c1", "target_concept_id": "c2", "transfer_type": "near", "source_score": 0.9, "target_score": 0.85},
        {"source_concept_id": "c1", "target_concept_id": "c2", "transfer_type": "near", "source_score": 0.5, "target_score": 0.52},
    ]
    matrix = compute_transfer_matrix(records)
    assert matrix["total_pairs_evaluated"] == 1
    assert len(matrix["transfer_evaluations"]) == 1


def test_evaluate_transfer_validity_validation_errors_and_to_dict():
    # Fewer than 5 observations
    with pytest.raises(ValueError, match="At least 5 paired observations"):
        evaluate_transfer_validity([0.5, 0.6], [0.5, 0.6], "c1", "c2")

    # Mismatched lengths
    with pytest.raises(ValueError, match="matching lengths"):
        evaluate_transfer_validity([0.5] * 6, [0.5] * 5, "c1", "c2")

    # to_dict verification
    res = evaluate_transfer_validity(
        [0.5, 0.6, 0.7, 0.8, 0.9],
        [0.55, 0.65, 0.75, 0.85, 0.95],
        "c1",
        "c2",
        TransferType.FAR,
    )
    d = res.to_dict()
    assert d["transfer_type"] == "far"
    assert "pearson_r" in d
    assert d["evidence_type"] == "synthetic_fixture"
