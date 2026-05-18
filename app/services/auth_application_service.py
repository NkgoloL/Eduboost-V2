from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from typing import Any


REPOSITORY_CANDIDATES: dict[str, tuple[str, ...]] = {
    "user_repo": (
        "app.repositories.user_repository.UserRepository",
        "app.repositories.repositories.UserRepository",
    ),
    "guardian_repo": (
        "app.repositories.guardian_repository.GuardianRepository",
        "app.repositories.repositories.GuardianRepository",
    ),
    "learner_repo": (
        "app.repositories.learner_repository.LearnerRepository",
        "app.repositories.repositories.LearnerRepository",
    ),
    "consent_repo": (
        "app.repositories.consent_repository.ConsentRepository",
        "app.repositories.repositories.ConsentRepository",
    ),
    "audit_repo": (
        "app.repositories.audit_repository.AuditRepository",
        "app.repositories.repositories.AuditRepository",
    ),
    "refresh_token_repo": (
        "app.repositories.refresh_token_repository.RefreshTokenRepository",
        "app.repositories.repositories.RefreshTokenRepository",
    ),
    "password_reset_repo": (
        "app.repositories.password_reset_repository.PasswordResetRepository",
        "app.repositories.repositories.PasswordResetRepository",
    ),
}


class AuthApplicationServiceError(RuntimeError):
    """Raised when the auth application boundary cannot construct a dependency."""


def import_symbol(path: str) -> Any | None:
    module_name, _, attr = path.rpartition(".")
    if not module_name or not attr:
        return None
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return None
    return getattr(module, attr, None)


def construct_repository(repository_cls: Any, db: Any) -> Any:
    for args, kwargs in (
        ((db,), {}),
        ((), {"db": db}),
        ((), {"session": db}),
        ((), {"database": db}),
        ((), {}),
    ):
        try:
            return repository_cls(*args, **kwargs)
        except TypeError:
            continue
    raise AuthApplicationServiceError(f"Cannot construct repository {repository_cls!r}")


@dataclass
class AuthRepositoryBundle:
    """Lazy repository bundle owned by AuthApplicationService.

    Routers depend on AuthApplicationService instead of importing repository
    classes directly. The bundle keeps the current repository APIs intact while
    closing the router import boundary.
    """

    db: Any
    _cache: dict[str, Any] = field(default_factory=dict)

    def _repo(self, name: str) -> Any:
        if name in self._cache:
            return self._cache[name]

        for candidate in REPOSITORY_CANDIDATES.get(name, ()):  # pragma: no branch - simple fallback loop
            cls = import_symbol(candidate)
            if cls is None:
                continue
            repo = construct_repository(cls, self.db)
            self._cache[name] = repo
            return repo

        raise AuthApplicationServiceError(f"No repository implementation found for {name}")

    @property
    def user_repo(self) -> Any:
        return self._repo("user_repo")

    @property
    def guardian_repo(self) -> Any:
        return self._repo("guardian_repo")

    @property
    def learner_repo(self) -> Any:
        return self._repo("learner_repo")

    @property
    def consent_repo(self) -> Any:
        return self._repo("consent_repo")

    @property
    def audit_repo(self) -> Any:
        return self._repo("audit_repo")

    @property
    def refresh_token_repo(self) -> Any:
        return self._repo("refresh_token_repo")

    @property
    def password_reset_repo(self) -> Any:
        return self._repo("password_reset_repo")


@dataclass
class AuthApplicationService:
    db: Any
    repositories: AuthRepositoryBundle | None = None

    def __post_init__(self) -> None:
        if self.repositories is None:
            self.repositories = AuthRepositoryBundle(self.db)

    @property
    def user_repo(self) -> Any:
        return self.repositories.user_repo

    @property
    def guardian_repo(self) -> Any:
        return self.repositories.guardian_repo

    @property
    def learner_repo(self) -> Any:
        return self.repositories.learner_repo

    @property
    def consent_repo(self) -> Any:
        return self.repositories.consent_repo

    @property
    def audit_repo(self) -> Any:
        return self.repositories.audit_repo

    @property
    def refresh_token_repo(self) -> Any:
        return self.repositories.refresh_token_repo

    @property
    def password_reset_repo(self) -> Any:
        return self.repositories.password_reset_repo

    async def guardian_learner_ids(self, guardian_id: Any) -> list[Any]:
        repo = self.learner_repo
        for method_name in ("get_by_guardian", "list_by_guardian", "get_for_guardian", "find_by_guardian"):
            method = getattr(repo, method_name, None)
            if method is None:
                continue
            for args, kwargs in (
                ((guardian_id,), {}),
                ((), {"guardian_id": guardian_id}),
                ((), {"parent_id": guardian_id}),
            ):
                try:
                    result = method(*args, **kwargs)
                    if hasattr(result, "__await__"):
                        result = await result
                    return [extract_identifier(item) for item in (result or []) if extract_identifier(item) is not None]
                except TypeError:
                    continue
        return []


def extract_identifier(value: Any) -> Any | None:
    if value is None:
        return None
    if isinstance(value, dict):
        for key in ("id", "learner_id", "user_id"):
            if value.get(key) is not None:
                return value[key]
    for attr in ("id", "learner_id", "user_id"):
        item = getattr(value, attr, None)
        if item is not None:
            return item
    return value


def build_auth_application_service(db: Any) -> AuthApplicationService:
    return AuthApplicationService(db=db)


__all__ = [
    "AuthApplicationService",
    "AuthApplicationServiceError",
    "AuthRepositoryBundle",
    "build_auth_application_service",
    "construct_repository",
    "extract_identifier",
    "import_symbol",
]

# code_911_950_auth_lifecycle_methods
async def _auth_lifecycle_call_legacy(self, legacy_impl, **kwargs):
    """Execute a preserved auth lifecycle implementation through the service boundary."""
    if legacy_impl is None:
        raise AuthApplicationServiceError("legacy_impl is required for transitional lifecycle extraction")
    result = legacy_impl(**kwargs)
    if hasattr(result, "__await__"):
        return await result
    return result


async def _auth_lifecycle_register(self, *, legacy_impl=None, **kwargs):
    return await self._auth_lifecycle_call_legacy(legacy_impl, **kwargs)


async def _auth_lifecycle_login(self, *, legacy_impl=None, **kwargs):
    return await self._auth_lifecycle_call_legacy(legacy_impl, **kwargs)


async def _auth_lifecycle_refresh(self, *, legacy_impl=None, **kwargs):
    return await self._auth_lifecycle_call_legacy(legacy_impl, **kwargs)


async def _auth_lifecycle_create_dev_session(self, *, legacy_impl=None, **kwargs):
    return await self._auth_lifecycle_call_legacy(legacy_impl, **kwargs)


AuthApplicationService._auth_lifecycle_call_legacy = _auth_lifecycle_call_legacy
AuthApplicationService.register = _auth_lifecycle_register
AuthApplicationService.login = _auth_lifecycle_login
AuthApplicationService.refresh = _auth_lifecycle_refresh
AuthApplicationService.create_dev_session = _auth_lifecycle_create_dev_session
