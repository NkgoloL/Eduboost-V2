"""
EduBoost SA — Global Exception Handlers
Consistent canonical V2 JSON error responses across all modules.
"""
from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from jose import JWTError
from sqlalchemy.exc import IntegrityError
from slowapi.errors import RateLimitExceeded

from app.domain.api_v2_models import FieldError, envelope_content, fail

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
    error_code = "unauthorized"


class AuthorisationError(EduBoostError):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "forbidden"


class DuplicateError(EduBoostError):
    status_code = status.HTTP_409_CONFLICT
    error_code = "conflict"


class LLMError(EduBoostError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "dependency_unavailable"


class POPIAViolationError(EduBoostError):
    """Raised when an operation would violate POPIA compliance rules."""

    status_code = status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS
    error_code = "popia_violation"


_STATUS_ERROR_CODES: dict[int, str] = {
    status.HTTP_400_BAD_REQUEST: "bad_request",
    status.HTTP_401_UNAUTHORIZED: "unauthorized",
    status.HTTP_403_FORBIDDEN: "forbidden",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_409_CONFLICT: "conflict",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "validation_error",
    status.HTTP_429_TOO_MANY_REQUESTS: "rate_limited",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "internal_error",
    status.HTTP_503_SERVICE_UNAVAILABLE: "dependency_unavailable",
}


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _http_error_code(status_code: int) -> str:
    return _STATUS_ERROR_CODES.get(status_code, "http_error")


def _http_message_and_details(detail: Any) -> tuple[str, dict[str, Any]]:
    if isinstance(detail, str):
        return detail, {}
    if isinstance(detail, dict):
        message = str(detail.get("message") or detail.get("detail") or "HTTP error")
        details = {key: value for key, value in detail.items() if key not in {"message", "detail"}}
        return message, details
    return str(detail), {"detail": detail}


def _validation_field_errors(exc: RequestValidationError) -> list[FieldError]:
    field_errors: list[FieldError] = []
    for error in exc.errors():
        loc = error.get("loc", ())
        field = ".".join(str(part) for part in loc if part not in {"body", "query", "path", "header"})
        field_errors.append(
            FieldError(
                field=field or "request",
                message=str(error.get("msg", "Invalid value")),
                code=str(error.get("type", "invalid")),
            )
        )
    return field_errors


def _error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
    *,
    field_errors: list[FieldError] | None = None,
    remediation: str | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=envelope_content(
            fail(
                code=error_code,
                message=message,
                request_id=request_id,
                field_errors=field_errors,
                remediation=remediation,
                details=details,
            )
        ),
        headers=headers,
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
            _request_id(request),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        message, details = _http_message_and_details(exc.detail)
        return _error_response(
            exc.status_code,
            _http_error_code(exc.status_code),
            message,
            details=details,
            request_id=_request_id(request),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "validation_error",
            "Request validation failed",
            {"errors": jsonable_encoder(exc.errors())},
            _request_id(request),
            field_errors=_validation_field_errors(exc),
        )

    @app.exception_handler(JWTError)
    async def handle_jwt_error(request: Request, exc: JWTError) -> JSONResponse:
        return _error_response(
            status.HTTP_401_UNAUTHORIZED,
            "unauthorized",
            "Invalid or expired token",
            request_id=_request_id(request),
        )

    @app.exception_handler(IntegrityError)
    async def handle_integrity_error(request: Request, exc: IntegrityError) -> JSONResponse:
        logger.warning("DB integrity error: %s", exc)
        return _error_response(
            status.HTTP_409_CONFLICT,
            "conflict",
            "Resource already exists",
            request_id=_request_id(request),
        )

    @app.exception_handler(RateLimitExceeded)
    async def handle_rate_limit(request: Request, exc: RateLimitExceeded) -> JSONResponse:
        return _error_response(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "rate_limited",
            "Rate limit exceeded. Please upgrade to Premium for higher limits.",
            request_id=_request_id(request),
            remediation="Try again later or reduce request frequency.",
        )

    @app.exception_handler(Exception)
    async def handle_unhandled(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "internal_error",
            "An unexpected error occurred",
            request_id=_request_id(request),
        )
