"""
EduBoost V2 — Structured JSON Logging
Configures stdlib logging with structlog for JSON output in production.
"""
from __future__ import annotations

import logging
import sys

import structlog
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.core.config import settings


def configure_logging() -> None:
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    renderer = (
        structlog.processors.JSONRenderer()
        if settings.is_production()
        else structlog.dev.ConsoleRenderer(colors=True)
    )
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
        ],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    structlog.configure(
        processors=shared_processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        level=log_level,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        app_env=settings.APP_ENV,
        app_version=settings.APP_VERSION,
    )

    # ── Sentry ───────────────────────────────────────────────────────────────
    if settings.is_production() and hasattr(settings, "SENTRY_DSN") and settings.SENTRY_DSN:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.APP_ENV,
            release=f"eduboost@{settings.APP_VERSION}",
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
                sentry_logging,
            ],
            traces_sample_rate=0.1,  # 10% sampling for performance tracing
            profiles_sample_rate=0.1,
        )


def get_logger(name: str) -> structlog.BoundLogger:
    return structlog.get_logger(name)
