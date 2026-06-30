"""
app/modules/diagnostics/item_bank_pipeline.py
=============================================
Item-bank pipeline for the EduBoost V2 diagnostics module.

Responsibilities
----------------
* Validate pipeline configuration at construction time (fail-fast).
* Fetch candidate items from ``ItemBankRepository`` – either all approved
  items or a topic-filtered subset.
* Apply client-side post-filters: difficulty range and max-items cap.
* Optionally shuffle the result set before returning.

Design notes
------------
* ``ItemBankRepository`` is imported at module level so that unit tests can
  patch ``app.modules.diagnostics.item_bank_pipeline.ItemBankRepository``
  and inject a mock repository without touching the constructor signature.
* The ``repository`` constructor kwarg lets integration and higher-level
  tests (or callers) supply a pre-built repository instance directly,
  bypassing the module-level import entirely.
* ``fetch_items`` is a coroutine so it composes cleanly with the async
  FastAPI / SQLAlchemy stack used in the rest of the V2 runtime.

Interface contract (derived from test_item_bank_pipeline.py)
------------------------------------------------------------
Construction:
    pipeline = ItemBankPipeline(config: dict)
    pipeline = ItemBankPipeline(config: dict, repository: ItemBankRepository)

    Raises ValueError at construction for:
        - config["max_items"] < 0
        - config["difficulty_range"] where low > high

Execution:
    items: list[dict] = await pipeline.fetch_items()

    Behaviour:
        - Delegates to repository.get_items_by_topic(topic) when
          config["topic_filter"] is set.
        - Delegates to repository.get_approved_items() otherwise.
        - Filters returned items to those whose "difficulty" value falls
          within [difficulty_low, difficulty_high] (inclusive bounds).
        - Truncates to config["max_items"] after filtering.
        - Returns [] (not raises) when the bank is empty.
        - Optionally shuffles when config["shuffle"] is True.
"""

from __future__ import annotations

import random
from typing import Any

# Module-level import so unit tests can patch
# "app.modules.diagnostics.item_bank_pipeline.ItemBankRepository".
from app.repositories.item_bank_repository import ItemBankRepository

__all__ = ["ItemBankPipeline"]


# ---------------------------------------------------------------------------
# Config schema
# ---------------------------------------------------------------------------

_DEFAULTS: dict[str, Any] = {
    "max_items": 10,
    "difficulty_range": (0.0, 1.0),
    "topic_filter": None,
    "shuffle": False,
}


def _validate_config(config: dict[str, Any]) -> None:
    """Raise ``ValueError`` for any invalid configuration values.

    Validation is intentionally strict and runs at construction time so
    that misconfigured pipelines surface immediately rather than at the
    first ``await fetch_items()`` call.
    """
    max_items = config.get("max_items", _DEFAULTS["max_items"])
    if not isinstance(max_items, int) or max_items < 0:
        raise ValueError(
            f"max_items must be a non-negative integer, got {max_items!r}."
        )

    difficulty_range = config.get("difficulty_range", _DEFAULTS["difficulty_range"])
    try:
        low, high = difficulty_range
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"difficulty_range must be a two-element sequence (low, high), "
            f"got {difficulty_range!r}."
        ) from exc

    if low > high:
        raise ValueError(
            f"difficulty_range low ({low}) must be ≤ high ({high}). "
            f"Got {difficulty_range!r}."
        )


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

class ItemBankPipeline:
    """Fetch, filter, and return a list of approved item-bank items.

    Parameters
    ----------
    config:
        Pipeline configuration dictionary.  Recognised keys:

        max_items (int, default 10):
            Maximum number of items to return.  Must be ≥ 0.
        difficulty_range (tuple[float, float], default (0.0, 1.0)):
            Inclusive (low, high) difficulty bounds.  Items whose
            ``difficulty`` value falls outside this range are discarded.
            ``low`` must be ≤ ``high``; both are floats in [0.0, 1.0].
        topic_filter (str | None, default None):
            When set, ``repository.get_items_by_topic(topic_filter)`` is
            called instead of ``repository.get_approved_items()``.
        shuffle (bool, default False):
            When True, shuffle the filtered result before truncation.

    repository:
        Optional pre-built ``ItemBankRepository`` instance.  When omitted,
        the pipeline constructs one from the module-level import.  Providing
        this kwarg is the recommended approach for integration tests that
        supply a session-scoped repository.
    """

    def __init__(
        self,
        config: dict[str, Any],
        repository: ItemBankRepository | None = None,
    ) -> None:
        # Validate before storing anything so construction is atomic.
        _validate_config(config)

        # Merge caller config over defaults so all keys are always present.
        self._config: dict[str, Any] = {**_DEFAULTS, **config}

        # Use the injected repository if provided; otherwise rely on the
        # module-level ``ItemBankRepository`` (patchable by unit tests).
        self._repository: ItemBankRepository = (
            repository if repository is not None else ItemBankRepository()
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def fetch_items(self) -> list[dict[str, Any]]:
        """Fetch, filter, and return candidate items.

        Returns
        -------
        list[dict]:
            Filtered items, each represented as a plain dictionary.
            Never raises for an empty bank – returns ``[]`` instead.
        """
        raw_items = await self._fetch_from_repository()
        filtered = self._apply_difficulty_filter(raw_items)

        if self._config["shuffle"]:
            random.shuffle(filtered)

        return filtered[: self._config["max_items"]]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _fetch_from_repository(self) -> list[dict[str, Any]]:
        """Delegate to the appropriate repository method."""
        topic: str | None = self._config["topic_filter"]
        if topic is not None:
            return await self._repository.get_items_by_topic(topic)
        return await self._repository.get_approved_items()

    def _apply_difficulty_filter(
        self, items: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Return only items whose difficulty falls within the configured range."""
        low, high = self._config["difficulty_range"]

        # Fast path: default full range – skip per-item checks.
        if low == 0.0 and high == 1.0:
            return list(items)

        return [
            item
            for item in items
            if low <= float(item.get("difficulty", 0.0)) <= high
        ]
