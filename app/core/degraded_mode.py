"""Graceful degraded-mode capability registry.

The registry separates critical runtime dependencies from optional product
capabilities. Optional integrations may be disabled without making `/ready`
fail, provided the product exposes a clear fallback state to API and frontend
callers.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

from app.core.config import settings

CapabilityStatus = Literal["available", "degraded", "disabled"]
CapabilityCriticality = Literal["critical", "optional"]


@dataclass(frozen=True, slots=True)
class RuntimeCapability:
    name: str
    status: CapabilityStatus
    criticality: CapabilityCriticality
    fallback: str
    reason: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def _has_llm_provider() -> bool:
    return bool(
        settings.GOOGLE_API_KEY
        or settings.GROQ_API_KEY
        or settings.ANTHROPIC_API_KEY
        or settings.LLM_PROVIDER in {"mock", "local_hf"}
    )


def _has_billing_provider() -> bool:
    return bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_WEBHOOK_SECRET and settings.STRIPE_PRICE_ID_PREMIUM)


def _has_email_provider() -> bool:
    return bool(settings.SENDGRID_API_KEY and settings.SENDGRID_FROM_EMAIL)


def _has_analytics_provider() -> bool:
    return bool(settings.POSTHOG_API_KEY)


def get_runtime_capabilities() -> dict[str, RuntimeCapability]:
    llm_available = _has_llm_provider()
    billing_available = _has_billing_provider()
    email_available = _has_email_provider()
    analytics_available = _has_analytics_provider()
    return {
        "llm_generation": RuntimeCapability(
            name="llm_generation",
            status="available" if llm_available else "degraded",
            criticality="optional",
            fallback="Use deterministic/static CAPS-aligned lesson templates and cached approved content.",
            reason="No LLM provider configured" if not llm_available else "",
        ),
        "billing": RuntimeCapability(
            name="billing",
            status="available" if billing_available else "disabled",
            criticality="optional",
            fallback="Keep users on the free tier and hide/disable checkout actions.",
            reason="Stripe keys/price are not configured" if not billing_available else "",
        ),
        "email": RuntimeCapability(
            name="email",
            status="available" if email_available else "degraded",
            criticality="optional",
            fallback="Show in-app notices and queue operational email intents for later replay.",
            reason="SendGrid sender/API key not configured" if not email_available else "",
        ),
        "analytics": RuntimeCapability(
            name="analytics",
            status="available" if analytics_available else "disabled",
            criticality="optional",
            fallback="Log POPIA-safe pseudonymous events locally without third-party dispatch.",
            reason="PostHog API key not configured" if not analytics_available else "",
        ),
    }


def capabilities_payload() -> dict[str, object]:
    capabilities = get_runtime_capabilities()
    degraded = [name for name, item in capabilities.items() if item.status != "available"]
    return {
        "status": "degraded" if degraded else "ok",
        "degraded_capabilities": degraded,
        "capabilities": {name: item.to_dict() for name, item in capabilities.items()},
    }


def require_optional_capability(name: str) -> RuntimeCapability:
    capability = get_runtime_capabilities()[name]
    if capability.status != "available":
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "code": "capability_unavailable",
                "capability": name,
                "status": capability.status,
                "fallback": capability.fallback,
                "reason": capability.reason,
            },
        )
    return capability
