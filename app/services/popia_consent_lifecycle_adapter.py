from __future__ import annotations

import inspect
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.domain.consent import ConsentRecord, ConsentState


async def _maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        return await value
    return value


def _value(kwargs: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if kwargs.get(name) is not None:
            return kwargs[name]
    return default


def _coerce_uuid(value: Any, *, salt: str) -> uuid.UUID:
    if isinstance(value, uuid.UUID):
        return value
    if value is None:
        return uuid.uuid5(uuid.NAMESPACE_URL, f"eduboost-popia-missing-{salt}")
    text = str(value)
    try:
        return uuid.UUID(text)
    except (TypeError, ValueError):
        return uuid.uuid5(uuid.NAMESPACE_URL, f"eduboost-popia-{salt}-{text}")


def _coerce_datetime(value: Any, *, fallback: datetime) -> datetime:
    if isinstance(value, datetime):
        return value
    return fallback


def _state_from(value: Any, *, fallback: ConsentState) -> ConsentState:
    if isinstance(value, ConsentState):
        return value
    if value is None:
        return fallback
    text = str(value).lower()
    aliases = {
        "active": ConsentState.GRANTED,
        "approved": ConsentState.GRANTED,
        "granted": ConsentState.GRANTED,
        "denied": ConsentState.DENIED,
        "declined": ConsentState.DENIED,
        "rejected": ConsentState.DENIED,
        "withdrawn": ConsentState.WITHDRAWN,
        "revoked": ConsentState.WITHDRAWN,
        "renewal_required": ConsentState.RENEWAL_REQUIRED,
        "expired": ConsentState.EXPIRED,
        "pending": ConsentState.PENDING,
    }
    return aliases.get(text, fallback)


def _dump_candidate(result: Any) -> dict[str, Any]:
    if result is None or isinstance(result, (int, float, bool, str)):
        return {}
    if isinstance(result, ConsentRecord):
        return result.model_dump()
    if isinstance(result, dict):
        return dict(result)
    if hasattr(result, "model_dump"):
        try:
            value = result.model_dump()
            if isinstance(value, dict):
                return value
        except Exception:
            pass

    data: dict[str, Any] = {}
    for name in (
        "id",
        "learner_id",
        "guardian_id",
        "privacy_notice_version",
        "policy_version",
        "consent_version",
        "state",
        "status",
        "granted_at",
        "expires_at",
        "withdrawn_at",
        "revoked_at",
        "denial_reason",
        "reason",
        "created_at",
        "updated_at",
    ):
        if hasattr(result, name):
            data[name] = getattr(result, name)
    return data


def _coerce_consent_record(result: Any, kwargs: dict[str, Any], *, fallback_state: ConsentState) -> ConsentRecord:
    """Normalize canonical/legacy service output to the router response contract.

    Legacy revoke-style methods can return an integer rowcount. POPIA routes,
    however, declare response_model=ConsentRecord. This adapter is the contract
    boundary that prevents int-like service results from escaping to FastAPI
    response validation.
    """
    if isinstance(result, ConsentRecord):
        return result

    data = _dump_candidate(result)
    now = datetime.now(timezone.utc)

    state = _state_from(_value(data, "state", "status"), fallback=fallback_state)
    learner_id = _coerce_uuid(_value(data, "learner_id", default=_value(kwargs, "learner_id")), salt="learner")
    guardian_id = _coerce_uuid(
        _value(data, "guardian_id", default=_value(kwargs, "guardian_id", "parent_id", "actor_id")),
        salt="guardian",
    )
    privacy_notice_version = str(
        _value(
            data,
            "privacy_notice_version",
            "policy_version",
            "consent_version",
            default=_value(kwargs, "privacy_notice_version", "consent_version", default="unknown"),
        )
    )

    granted_at = _coerce_datetime(_value(data, "granted_at"), fallback=now if state == ConsentState.GRANTED else None)  # type: ignore[arg-type]
    withdrawn_at = _coerce_datetime(
        _value(data, "withdrawn_at", "revoked_at"),
        fallback=now if state == ConsentState.WITHDRAWN else None,
    )  # type: ignore[arg-type]

    return ConsentRecord(
        id=_coerce_uuid(_value(data, "id"), salt=f"consent-{learner_id}-{state.value}"),
        learner_id=learner_id,
        guardian_id=guardian_id,
        privacy_notice_version=privacy_notice_version,
        state=state,
        granted_at=granted_at,
        expires_at=_coerce_datetime(_value(data, "expires_at"), fallback=None),  # type: ignore[arg-type]
        withdrawn_at=withdrawn_at,
        denial_reason=_value(data, "denial_reason", "reason", default=kwargs.get("reason")),
        created_at=_coerce_datetime(_value(data, "created_at"), fallback=now),
        updated_at=_coerce_datetime(_value(data, "updated_at"), fallback=now),
    )


@dataclass
class POPIAConsentLifecycleAdapter:
    service: Any

    async def _call(self, method_names: tuple[str, ...], **kwargs: Any) -> Any:
        if "consent_version" not in kwargs and "privacy_notice_version" in kwargs:
            kwargs["consent_version"] = kwargs["privacy_notice_version"]
        if "privacy_notice_version" not in kwargs and "consent_version" in kwargs:
            kwargs["privacy_notice_version"] = kwargs["consent_version"]

        missing: list[str] = []
        for method_name in method_names:
            method = getattr(self.service, method_name, None)
            if method is None:
                missing.append(method_name)
                continue

            signature = inspect.signature(method)
            params = signature.parameters
            if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in params.values()):
                return await _maybe_await(method(**kwargs))

            filtered = {key: value for key, value in kwargs.items() if key in params}
            required = [
                name
                for name, param in params.items()
                if name != "self"
                and param.default is inspect.Parameter.empty
                and param.kind in {inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY}
                and name not in filtered
            ]

            positional: list[Any] = []
            for name in required:
                if name in {"guardian_id", "parent_id"}:
                    positional.append(_value(kwargs, "guardian_id", "parent_id", "actor_id"))
                elif name == "learner_id":
                    positional.append(kwargs.get("learner_id"))
                elif name in {"consent_version", "version"}:
                    positional.append(_value(kwargs, "consent_version", "privacy_notice_version"))
                elif name in {"actor_id", "user_id"}:
                    positional.append(_value(kwargs, "actor_id", "guardian_id"))
                else:
                    positional = []
                    break

            if required and positional and len(positional) == len(required):
                return await _maybe_await(method(*positional, **filtered))
            return await _maybe_await(method(**filtered))

        raise AttributeError(f"Canonical consent service lacks methods: {', '.join(missing)}")

    @staticmethod
    def _merge_positional(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
        names = ("guardian_id", "learner_id", "consent_version")
        merged = dict(kwargs)
        for name, value in zip(names, args):
            merged.setdefault(name, value)
        return merged

    async def grant(self, *args: Any, **kwargs: Any) -> ConsentRecord:
        merged = self._merge_positional(args, kwargs)
        result = await self._call(("grant", "grant_consent", "create_consent"), **merged)
        return _coerce_consent_record(result, merged, fallback_state=ConsentState.GRANTED)

    async def deny(self, *args: Any, **kwargs: Any) -> ConsentRecord:
        merged = self._merge_positional(args, kwargs)
        if any(hasattr(self.service, name) for name in ("deny", "deny_consent")):
            result = await self._call(("deny", "deny_consent"), **merged)
        else:
            merged.setdefault("reason", "denied")
            result = await self._call(("revoke", "revoke_consent", "withdraw", "withdraw_consent"), **merged)
        return _coerce_consent_record(result, merged, fallback_state=ConsentState.DENIED)

    async def withdraw(self, *args: Any, **kwargs: Any) -> ConsentRecord:
        merged = self._merge_positional(args, kwargs)
        result = await self._call(("withdraw", "withdraw_consent", "revoke", "revoke_consent"), **merged)
        return _coerce_consent_record(result, merged, fallback_state=ConsentState.WITHDRAWN)

    async def revoke(self, *args: Any, **kwargs: Any) -> ConsentRecord:
        merged = self._merge_positional(args, kwargs)
        result = await self._call(("revoke", "revoke_consent", "withdraw", "withdraw_consent"), **merged)
        return _coerce_consent_record(result, merged, fallback_state=ConsentState.WITHDRAWN)

    async def renew(self, *args: Any, **kwargs: Any) -> ConsentRecord:
        merged = self._merge_positional(args, kwargs)
        if any(hasattr(self.service, name) for name in ("renew", "renew_consent")):
            result = await self._call(("renew", "renew_consent"), **merged)
        else:
            result = await self._call(("grant", "grant_consent"), **merged)
        return _coerce_consent_record(result, merged, fallback_state=ConsentState.GRANTED)

    async def erase(self, *args: Any, **kwargs: Any) -> Any:
        return await self._call(("erase", "erase_consent", "request_erasure", "delete_consent"), **self._merge_positional(args, kwargs))

    async def restrict_processing(self, *args: Any, **kwargs: Any) -> Any:
        return await self._call(("restrict_processing", "restrict", "request_restriction"), **self._merge_positional(args, kwargs))

    def __getattr__(self, name: str) -> Any:
        return getattr(self.service, name)


__all__ = ["POPIAConsentLifecycleAdapter", "_coerce_consent_record"]
