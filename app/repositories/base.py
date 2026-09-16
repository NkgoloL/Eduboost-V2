"""Shared repository contracts for EduBoost V2."""

from __future__ import annotations

from typing import Protocol, TypeVar

T_co = TypeVar("T_co", covariant=True)


class Repository(Protocol[T_co]):
    async def get_by_id(self, entity_id: str) -> T_co | None: ...
