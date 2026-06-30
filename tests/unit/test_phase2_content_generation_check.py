from scripts.curriculum.check_phase2_content_generation import check_phase2_content_generation


def test_phase2_content_generation_check_passes_with_restored_artifacts():
    result = check_phase2_content_generation()

    assert result.failures == []
    assert result.facts["generated_file_count"] >= 400
    assert result.facts["lesson_quality"]["lesson_files_present"] == 51
    assert result.facts["lesson_quality"]["failed_lessons"] == 0
    assert result.facts["review_scope_import_plan"]["production_unlocked"] == 0
    assert result.facts["promotion_readiness"]["review_blocked"] == 50
