"""RLHF export service with pre-export PII minimisation gate."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from app.services.pii_sweep import assert_no_pii


class RLHFService:
    def export_openai_format(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        assert_no_pii(records)
        return {
            "id": str(uuid.uuid4()),
            "format": "openai",
            "record_count": len(records),
            "exported_at": datetime.now(UTC).isoformat(),
            "dataset_json": json.dumps(records),
        }

    def export_anthropic_format(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        assert_no_pii(records)
        return {
            "id": str(uuid.uuid4()),
            "format": "anthropic",
            "record_count": len(records),
            "exported_at": datetime.now(UTC).isoformat(),
            "dataset_json": json.dumps(records),
        }
