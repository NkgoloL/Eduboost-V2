from scripts.curriculum.check_topic_map_review_framework import check_framework


def test_topic_map_review_framework_is_complete():
    result = check_framework()

    assert result.failures == []
    assert result.facts["topic_map_file_count"] >= 50
    assert result.facts["scope_status_counts"]["review"] == 50
    assert result.facts["scope_status_counts"]["active"] == 1
    assert result.facts["source_manifest_passed"] is True
    assert result.facts["generation_ready_scope_count"] >= 50
