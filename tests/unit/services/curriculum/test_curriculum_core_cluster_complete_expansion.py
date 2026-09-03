from pathlib import Path
import pytest

from app.services.curriculum.answer_verification import (
    AnswerVerificationError,
    AnswerVerificationOutcome,
    DeterministicMathAnswerVerifier,
    _eval_arithmetic,
)
from app.services.curriculum.claim_validation import (
    Claim,
    ClaimValidationOutcome,
    ClaimValidator,
)
from app.services.curriculum.legacy_migration import (
    LegacyArtifactView,
    LegacyDispositionDecision,
    LegacyDispositionError,
    LegacyMigrationClassifier,
    build_gate2r8_legacy_fixture_artifacts,
    build_gate2r8_legacy_migration_manifest,
)
from app.services.curriculum.object_storage import (
    LocalImmutableObjectStore,
    ObjectStorageRejectedError,
    StoredObject,
)


def test_claim_validation_complete():
    validator = ClaimValidator(maximum_overlap_ratio=0.20)

    # 1. Valid claims
    claims = [
        Claim(claim_type="curriculum_requirement", text="Valid text", supporting_chunk_ids=["chk_1"], overlap_ratio=0.1),
        Claim(claim_type="pedagogical_guidance", text="Guidance text", overlap_ratio=0.0),
    ]
    res = validator.validate(claims)
    assert res.status == "passed"
    assert res.errors == []

    # 2. Unsupported claim type
    bad_type = [Claim(claim_type="unknown_claim_type", text="Text")]
    res_bad = validator.validate(bad_type)
    assert res_bad.status == "failed"
    assert any("unsupported claim_type" in e for e in res_bad.errors)

    # 3. Missing supporting chunks for curriculum requirement
    no_chunks = [Claim(claim_type="curriculum_requirement", text="Text", supporting_chunk_ids=[])]
    res_chunks = validator.validate(no_chunks)
    assert any("requires supporting source chunks" in e for e in res_chunks.errors)

    # 4. Overlap ratio exceeded
    high_overlap = [Claim(claim_type="pedagogical_guidance", text="Text", overlap_ratio=0.5)]
    res_overlap = validator.validate(high_overlap)
    assert any("exceeds permitted textual overlap" in e for e in res_overlap.errors)

    # 5. Enrichment promoted to CAPS requires
    fake_caps = [Claim(claim_type="enrichment", text="Because CAPS requires this step.")]
    res_enrich = validator.validate(fake_caps)
    assert any("cannot be promoted to a CAPS requirement" in e for e in res_enrich.errors)


def test_answer_verification_complete():
    verifier = DeterministicMathAnswerVerifier()

    # Valid arithmetic evaluation
    res_pass = verifier.verify_arithmetic_expression(question_expression="2 + 3 * 4", proposed_answer="14")
    assert res_pass.status == "passed"
    assert res_pass.expected_answer == "14"

    # Float division
    res_div = verifier.verify_arithmetic_expression(question_expression="7 / 2", proposed_answer="3.5")
    assert res_div.status == "passed"
    assert res_div.expected_answer == "3.5"

    # Floor div and modulo and unary minus
    assert _eval_arithmetic("10 // 3") == 3.0
    assert _eval_arithmetic("10 % 3") == 1.0
    assert _eval_arithmetic("-5 + 2") == -3.0

    # Failed check
    res_fail = verifier.verify_arithmetic_expression(question_expression="5 + 5", proposed_answer="12")
    assert res_fail.status == "failed"

    # Unsupported expression raises AnswerVerificationError
    with pytest.raises(AnswerVerificationError, match="unsupported arithmetic"):
        _eval_arithmetic("len([1, 2])")



def test_object_storage_complete(tmp_path):
    store = LocalImmutableObjectStore(root=tmp_path)

    # Valid file storage
    src_file = tmp_path / "source.txt"
    content = b"Hello CAPS Object Storage"
    src_file.write_bytes(content)
    import hashlib
    sha = hashlib.sha256(content).hexdigest()

    stored = store.put_file(src_file, expected_sha256=sha, suffix=".txt")
    assert stored.sha256 == sha
    assert stored.size_bytes == len(content)
    assert stored.path.exists()

    # Re-put existing file with matching hash
    re_stored = store.put_file(src_file, expected_sha256=sha, suffix=".txt")
    assert re_stored.sha256 == sha

    # Nonexistent source file
    with pytest.raises(ObjectStorageRejectedError, match="does not exist"):
        store.put_file(tmp_path / "missing.txt", expected_sha256=sha, suffix=".txt")

    # Invalid sha256
    with pytest.raises(ObjectStorageRejectedError, match="64 lowercase hexadecimal"):
        store.put_file(src_file, expected_sha256="bad_sha", suffix=".txt")

    # Unsupported suffix
    with pytest.raises(ObjectStorageRejectedError, match="unsupported object suffix"):
        store.put_file(src_file, expected_sha256=sha, suffix=".exe")

    # Empty source file
    empty_file = tmp_path / "empty.txt"
    empty_file.write_bytes(b"")
    empty_sha = hashlib.sha256(b"").hexdigest()
    with pytest.raises(ObjectStorageRejectedError, match="source object is empty"):
        store.put_file(empty_file, expected_sha256=empty_sha, suffix=".txt")

    # Checksum mismatch
    with pytest.raises(ObjectStorageRejectedError, match="checksum mismatch"):
        store.put_file(src_file, expected_sha256="0" * 64, suffix=".txt")

    # Exceeds max bytes
    with pytest.raises(ObjectStorageRejectedError, match="exceeds maximum allowed size"):
        store.put_file(src_file, expected_sha256=sha, suffix=".txt", max_bytes=5)


def test_legacy_migration_complete():
    classifier = LegacyMigrationClassifier()

    manifest = build_gate2r8_legacy_migration_manifest()
    assert manifest["gate"] == "2R.8"
    assert manifest["artifact_count"] >= 5
    assert "manifest_sha256" in manifest

    # Empty artifacts list error
    with pytest.raises(LegacyDispositionError, match="at least one artifact"):
        classifier.build_manifest([])

    # Empty artifact id or type
    with pytest.raises(LegacyDispositionError, match="required"):
        LegacyArtifactView(artifact_id="", artifact_type="lesson", published=False, source_snapshot_hash=None).normalized()

