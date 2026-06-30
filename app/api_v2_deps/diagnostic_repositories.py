from __future__ import annotations

from importlib import import_module
from typing import Any


class DiagnosticRepositoryBoundaryError(RuntimeError):
    """Raised when a diagnostics repository cannot be resolved."""


# Dynamic resolution is allowed here because this module is the explicit
# repository-boundary adapter for diagnostics. Routers must not perform this
# resolution themselves.
_REPOSITORY_TARGETS: dict[str, tuple[str, ...]] = {
    "learner": (
        "app.repositories.repositories.LearnerRepository",
        "app.repositories.learner_repository.LearnerRepository",
        "app.repositories.learners.LearnerRepository",
    ),
    "guardian": (
        "app.repositories.repositories.GuardianRepository",
        "app.repositories.guardian_repository.GuardianRepository",
        "app.repositories.guardians.GuardianRepository",
    ),
    "irt": (
        "app.repositories.repositories.IRTRepository",
        "app.repositories.irt_repository.IRTRepository",
    ),
    "diagnostic": (
        "app.repositories.repositories.DiagnosticRepository",
        "app.repositories.diagnostic_repository.DiagnosticRepository",
    ),
    "knowledge_gap": (
        "app.repositories.repositories.KnowledgeGapRepository",
        "app.repositories.knowledge_gap_repository.KnowledgeGapRepository",
    ),
    "item_bank": (
        "app.repositories.item_bank_repository.ItemBankRepository",
        "app.repositories.repositories.ItemBankRepository",
    ),
    "diagnostic_session": (
        "app.repositories.diagnostic_session_repository.DiagnosticSessionRepository",
        "app.repositories.repositories.DiagnosticSessionRepository",
    ),
    "mastery": (
        "app.repositories.mastery_repository.MasteryRepository",
        "app.repositories.repositories.MasteryRepository",
    ),
}


_CLASS_CACHE: dict[str, type[Any]] = {}


def _split_dotted_path(path: str) -> tuple[str, str]:
    module_name, sep, attr = path.rpartition(".")
    if not sep or not module_name or not attr:
        raise DiagnosticRepositoryBoundaryError(f"Invalid repository path: {path!r}")
    return module_name, attr


def resolve_repository_class(name: str) -> type[Any]:
    if name in _CLASS_CACHE:
        return _CLASS_CACHE[name]

    candidates = _REPOSITORY_TARGETS.get(name)
    if not candidates:
        raise DiagnosticRepositoryBoundaryError(f"Unknown diagnostics repository boundary name: {name!r}")

    failures: list[str] = []
    for dotted_path in candidates:
        module_name, attr = _split_dotted_path(dotted_path)
        try:
            module = import_module(module_name)
            cls = getattr(module, attr)
        except Exception as exc:  # expected while supporting known repo family variants
            failures.append(f"{dotted_path}: {type(exc).__name__}: {exc}")
            continue
        _CLASS_CACHE[name] = cls
        return cls

    raise DiagnosticRepositoryBoundaryError(
        f"Could not resolve diagnostics repository {name!r}. Tried: " + "; ".join(failures)
    )


def repository(name: str, db: Any) -> Any:
    cls = resolve_repository_class(name)
    return cls(db)


def learner(db: Any) -> Any:
    return repository("learner", db)


def guardian(db: Any) -> Any:
    return repository("guardian", db)


def irt(db: Any) -> Any:
    return repository("irt", db)


def diagnostic(db: Any) -> Any:
    return repository("diagnostic", db)


def knowledge_gap(db: Any) -> Any:
    return repository("knowledge_gap", db)


def item_bank(db: Any) -> Any:
    return repository("item_bank", db)


def diagnostic_session(db: Any) -> Any:
    return repository("diagnostic_session", db)


def mastery(db: Any) -> Any:
    return repository("mastery", db)


__all__ = [
    "DiagnosticRepositoryBoundaryError",
    "diagnostic",
    "diagnostic_session",
    "guardian",
    "irt",
    "item_bank",
    "knowledge_gap",
    "learner",
    "mastery",
    "repository",
    "resolve_repository_class",
]
