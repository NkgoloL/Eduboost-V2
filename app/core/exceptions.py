"""
EduBoost SA — Global Exception Handlers
Consistent JSON error responses across all modules.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jose import JWTError
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)


class EduBoostError(Exception):
    """Base exception for all EduBoost domain errors."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)


class NotFoundError(EduBoostError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"


class ConsentRequiredError(EduBoostError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "consent_required"


class ConsentExpiredError(EduBoostError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "consent_expired"


class AuthenticationError(EduBoostError):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "authentication_failed"


class AuthorisationError(EduBoostError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "authorisation_failed"


class DuplicateError(EduBoostError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "duplicate"


class LLMError(EduBoostError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "llm_unavailable"


class POPIAViolationError(EduBoostError):
    """Raised when an operation would violate POPIA compliance rules."""
    status_code = status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS
    error_code = "popia_violation"


def _error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_code,
            "message": message,
            "detail": message,
            "details": details or {},
            "request_id": request_id,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all global exception handlers on the FastAPI app."""

    @app.exception_handler(EduBoostError)
    async def handle_eduboost_error(request: Request, exc: EduBoostError) -> JSONResponse:
        return _error_response(
            exc.status_code,
            exc.error_code,
            exc.message,
            exc.details,
            getattr(request.state, "request_id", None),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        return _error_response(
            exc.status_code,
            "http_error",
            str(exc.detail),
            request_id=getattr(request.state, "request_id", None),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "validation_error",
            "Request validation failed",
            {"errors": exc.errors()},
            getattr(request.state, "request_id", None),
        )

    @app.exception_handler(JWTError)
    async def handle_jwt_error(request: Request, exc: JWTError) -> JSONResponse:
        return _error_response(
            status.HTTP_401_UNAUTHORIZED,
            "invalid_token",
            "Invalid or expired token",
            request_id=getattr(request.state, "request_id", None),
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("DB integrity error: %s", exc)
        return _error_response(
            status.HTTP_409_CONFLICT,
            "duplicate",
            "Resource already exists",
            request_id=getattr(request.state, "request_id", None),
        )

    @app.exception_handler(Exception)
    async def handle_unhandled(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "internal_error",
            "An unexpected error occurred",
            request_id=getattr(request.state, "request_id", None),
        )
