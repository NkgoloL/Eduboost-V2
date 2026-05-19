from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, AsyncContextManager, Callable


class POPIATransactionError(RuntimeError):
    """Raised when a POPIA lifecycle transaction cannot be completed."""


class _NullAsyncContext:
    async def __aenter__(self) -> None:
        return None

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> bool:
        return False


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


def _has_active_transaction(db: Any) -> bool:
    checker = getattr(db, "in_transaction", None)
    if callable(checker):
        try:
            return bool(checker())
        except Exception:
            return False
    return False


def _transaction_context(db: Any) -> AsyncContextManager[Any]:
    if db is None or not hasattr(db, "begin"):
        return _NullAsyncContext()
    if _has_active_transaction(db):
        return _NullAsyncContext()
    return db.begin()


def _filter_kwargs(method: Callable[..., Any], kwargs: dict[str, Any]) -> dict[str, Any]:
    try:
        signature = inspect.signature(method)
    except (TypeError, ValueError):
        return kwargs
    params = signature.parameters
    if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in params.values()):
        return kwargs
    return {key: value for key, value in kwargs.items() if key in params}


async def _call_flexible(target: Any, method_names: tuple[str, ...], **kwargs: Any) -> Any:
    missing: list[str] = []
    for method_name in method_names:
        method = getattr(target, method_name, None)
        if method is None:
            missing.append(method_name)
            continue
        return await _maybe_await(method(**_filter_kwargs(method, kwargs)))
    raise POPIATransactionError(f"Missing lifecycle method(s): {', '.join(missing)}")


@dataclass
class TransactionalPOPIAConsentLifecycleService:
    """Atomic POPIA consent transition + audit writer.

    This wrapper is intentionally small. Its only responsibility is to execute a
    consent lifecycle mutation and the corresponding audit write inside one
    transaction boundary when the provided DB/session supports transactions.
    """

    db: Any
    consent_service: Any
    audit_service: Any

    async def _audit(self, *, action: str, consent_record: Any, actor_id: Any = None, **kwargs: Any) -> None:
        await _call_flexible(
            self.audit_service,
            (
                "record_consent_lifecycle_event",
                "record_consent_event",
                "consent_lifecycle_event",
                "log_event",
                "audit_event",
            ),
            action=action,
            consent_record=consent_record,
            actor_id=actor_id,
            **kwargs,
        )

    async def _transition(self, *, action: str, methods: tuple[str, ...], **kwargs: Any) -> Any:
        async with _transaction_context(self.db):
            consent_record = await _call_flexible(self.consent_service, methods, **kwargs)
            await self._audit(action=action, consent_record=consent_record, actor_id=kwargs.get("actor_id"), **kwargs)
            return consent_record

    async def grant(self, **kwargs: Any) -> Any:
        return await self._transition(action="grant", methods=("grant", "grant_consent", "create_consent"), **kwargs)

    async def deny(self, **kwargs: Any) -> Any:
        return await self._transition(action="deny", methods=("deny", "deny_consent"), **kwargs)

    async def withdraw(self, **kwargs: Any) -> Any:
        return await self._transition(action="withdraw", methods=("withdraw", "withdraw_consent", "revoke", "revoke_consent"), **kwargs)

    async def renew(self, **kwargs: Any) -> Any:
        return await self._transition(action="renew", methods=("renew", "renew_consent"), **kwargs)


__all__ = [
    "POPIATransactionError",
    "TransactionalPOPIAConsentLifecycleService",
]
