"""V2 Judiciary service for schema enforcement and content screening."""

from __future__ import annotations

import json
from typing import Any, Type, TypeVar

from pydantic import BaseModel, TypeAdapter

from app.services.audit_service import AuditService

T = TypeVar("T", bound=BaseModel)


class JudiciaryViolationError(RuntimeError):
    pass


class JudiciaryServiceV2:
    """Enforces constitutional rules on AI outputs and inputs."""

    def __init__(self) -> None:
        self.audit = AuditService()

    async def screen_content(self, text: str, learner_id: str | None = None) -> bool:
        """Simple content screening for inappropriate keywords (V2 baseline)."""
        forbidden = {"inappropriate", "harmful", "illegal"}  # Simplified for V2
        violations = [word for word in forbidden if word in text.lower()]
        
        if violations:
            await self.audit.log_event(
                event_type="JUDICIARY_VIOLATION",
                learner_id=learner_id,
                payload={"violations": violations, "text_snippet": text[:100]},
            )
            return False
        return True

    def validate_schema(self, data: Any, schema_class: Type[T]) -> T:
        """Strictly validate and cast data to a Pydantic model using TypeAdapter."""
        try:
            adapter = TypeAdapter(schema_class)
            return adapter.validate_python(data)
        except Exception as e:
            # Log as a judiciary failure if the AI failed to follow instructions
            raise JudiciaryViolationError(f"Schema validation failed: {str(e)}") from e

    async def stamp_and_validate(self, raw_json: str, schema_class: Type[T], learner_id: str | None = None) -> T:
        """Parses, screens, and validates raw LLM output."""
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as e:
            raise JudiciaryViolationError("Invalid JSON output from LLM") from e

        # Screen the raw data if it's a string or has string values
        if not await self.screen_content(str(data), learner_id):
            raise JudiciaryViolationError("Content screening failed")

        validated = self.validate_schema(data, schema_class)
        
        await self.audit.log_event(
            event_type="JUDICIARY_STAMP_GRANTED",
            learner_id=learner_id,
            payload={"schema": schema_class.__name__},
        )
        return validated
