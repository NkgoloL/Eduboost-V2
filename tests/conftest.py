import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

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
