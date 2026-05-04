"""Shared repository contracts for EduBoost V2."""

from __future__ import annotations

from typing import Protocol, TypeVar

T = TypeVar("T")


class Repository(Protocol[T]):
    async def get_by_id(self, entity_id: str) -> T | None: ...
