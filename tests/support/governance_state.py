"""State-aware assertions for governance tests that survive roadmap progression."""
from scripts.testing.targeted_baseline_reconciliation import (
    assert_archival_or_current_valid,
    assert_release_boundaries_closed,
)

__all__ = ["assert_archival_or_current_valid", "assert_release_boundaries_closed"]
