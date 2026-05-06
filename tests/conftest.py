import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.api_v2 import app as fastapi_app
from app.core import providers
from app.core.database import get_db


@pytest.fixture
def mock_db_session():
    """Fixture for a mocked SQLAlchemy AsyncSession."""
    session = AsyncMock()
    return session


@pytest.fixture
def db_session(mock_db_session):
    """Alias for mock_db_session for compatibility with legacy tests."""
    return mock_db_session


@pytest.fixture
def mock_llm_service():
    """Fixture for a mocked LLM service."""
    service = AsyncMock()
    service.generate_lesson.return_value = (MagicMock(), False)
    return service


@pytest.fixture
def mock_user_id():
    """Fixture for a consistent test user ID."""
    return uuid4()


@pytest.fixture
def mock_learner_id():
    """Fixture for a consistent test learner ID."""
    return uuid4()


@pytest.fixture(autouse=True)
def dependency_overrides(mock_db_session):
    """Install common FastAPI dependency overrides for tests.

    Overrides the DB provider and common service providers so tests don't
    accidentally hit real infrastructure. This fixture is autouse so it
    applies to all tests unless explicitly disabled.
    """
    # Save existing overrides to restore later
    original = dict(fastapi_app.dependency_overrides)

    fastapi_app.dependency_overrides[get_db] = lambda: mock_db_session
    # Provide lightweight async mocks for commonly-injected services
    fastapi_app.dependency_overrides[providers.get_lesson_service] = lambda: AsyncMock()
    fastapi_app.dependency_overrides[providers.get_audit_service] = lambda: AsyncMock()

    yield

    # Restore original overrides
    fastapi_app.dependency_overrides.clear()
    fastapi_app.dependency_overrides.update(original)
