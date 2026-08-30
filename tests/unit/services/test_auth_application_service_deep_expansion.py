"""Comprehensive unit tests for AuthApplicationService repository construction and symbol resolution."""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from app.services.auth_application_service import (
    import_symbol,
    construct_repository,
    AuthApplicationServiceError,
    REPOSITORY_CANDIDATES,
)


class TestAuthApplicationServiceHelpers:
    def test_import_symbol_valid_and_invalid(self):
        sym = import_symbol("app.services.auth_application_service.AuthApplicationServiceError")
        assert sym == AuthApplicationServiceError

        assert import_symbol("non_existent_module.FakeClass") is None
        assert import_symbol("invalid_path_without_dot") is None

    def test_construct_repository_signatures(self):
        mock_db = MagicMock()

        class RepoWithPositional:
            def __init__(self, db):
                self.db = db

        class RepoWithKeywordDb:
            def __init__(self, *, db):
                self.db = db

        class RepoWithKeywordSession:
            def __init__(self, *, session):
                self.db = session

        class RepoNoArgs:
            def __init__(self):
                pass

        r1 = construct_repository(RepoWithPositional, mock_db)
        assert r1.db == mock_db

        r2 = construct_repository(RepoWithKeywordDb, mock_db)
        assert r2.db == mock_db

        r3 = construct_repository(RepoWithKeywordSession, mock_db)
        assert r3.db == mock_db

        r4 = construct_repository(RepoNoArgs, mock_db)
        assert isinstance(r4, RepoNoArgs)

    def test_construct_repository_failure_raises(self):
        class IncompatibleRepo:
            def __init__(self, required_arg1, required_arg2):
                pass

        with pytest.raises(AuthApplicationServiceError):
            construct_repository(IncompatibleRepo, MagicMock())

    def test_repository_candidates_structure(self):
        assert "user_repo" in REPOSITORY_CANDIDATES
        assert "guardian_repo" in REPOSITORY_CANDIDATES
        assert "learner_repo" in REPOSITORY_CANDIDATES
        assert "consent_repo" in REPOSITORY_CANDIDATES
