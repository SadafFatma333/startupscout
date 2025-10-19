# tests/conftest.py
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

# Set test environment variables
os.environ["TESTING"] = "true"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_NAME"] = "test_startupscout"
os.environ["DB_USER"] = "test_user"
os.environ["DB_PASSWORD"] = "test_password"
os.environ["OPENAI_API_KEY"] = "test_openai_key"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"
os.environ["JWT_SECRET"] = "test_jwt_secret"
os.environ["ADMIN_API_KEY"] = "test_admin_key"


@pytest.fixture(scope="session")
def test_db():
    """Create a temporary test database."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing."""
    with patch('openai.OpenAI') as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        
        # Mock embedding response
        mock_embed_response = Mock()
        mock_embed_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_embed_response
        
        # Mock completion response
        mock_completion_response = Mock()
        mock_completion_response.choices = [Mock()]
        mock_completion_response.choices[0].message.content = "Test answer"
        mock_completion_response.usage = Mock()
        mock_completion_response.usage.prompt_tokens = 100
        mock_completion_response.usage.completion_tokens = 50
        mock_client.chat.completions.create.return_value = mock_completion_response
        
        yield mock_client


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    with patch('redis.Redis') as mock:
        mock_client = Mock()
        mock.return_value = mock_client
        
        mock_client.get.return_value = None
        mock_client.set.return_value = True
        mock_client.delete.return_value = 1
        mock_client.flushall.return_value = True
        
        yield mock_client


@pytest.fixture
def mock_database():
    """Mock database connection for testing."""
    with patch('psycopg_pool.ConnectionPool') as mock:
        mock_pool = Mock()
        mock.return_value = mock_pool
        
        mock_conn = Mock()
        mock_cursor = Mock()
        
        mock_pool.connection.return_value.__enter__.return_value = mock_conn
        mock_pool.connection.return_value.__exit__.return_value = None
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.cursor.return_value.__exit__.return_value = None
        
        # Default mock data
        mock_cursor.fetchall.return_value = [
            (1, "Test Title", "https://example.com", "test_source", 0.9, "Test content")
        ]
        mock_cursor.fetchone.return_value = (1,)
        mock_cursor.rowcount = 1
        
        yield mock_pool, mock_conn, mock_cursor


@pytest.fixture
def sample_startup_data():
    """Sample startup data for testing."""
    return [
        {
            "id": 1,
            "title": "How to Raise Series A Funding",
            "url": "https://example.com/series-a",
            "source": "yc",
            "content": "Series A funding is crucial for scaling your startup...",
            "created_at": "2024-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "title": "Startup Metrics That Matter",
            "url": "https://example.com/metrics",
            "source": "medium",
            "content": "Key metrics include CAC, LTV, MRR, and churn rate...",
            "created_at": "2024-01-02T00:00:00Z"
        },
        {
            "id": 3,
            "title": "Product-Market Fit Guide",
            "url": "https://example.com/pmf",
            "source": "reddit",
            "content": "Product-market fit is achieved when customers buy faster than you can make...",
            "created_at": "2024-01-03T00:00:00Z"
        }
    ]


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True,
        "is_admin": False,
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": "2024-01-01T12:00:00Z",
        "login_count": 5
    }


@pytest.fixture
def sample_jwt_token():
    """Sample JWT token for testing."""
    from utils.auth import create_jwt
    payload = {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "username": "testuser",
        "email": "test@example.com",
        "is_admin": False
    }
    return create_jwt(payload)


@pytest.fixture
def test_client(mock_openai, mock_redis, mock_database):
    """Create test client with mocked services."""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def authenticated_headers(sample_jwt_token):
    """Headers with authentication token."""
    return {"Authorization": f"Bearer {sample_jwt_token}"}


@pytest.fixture
def admin_headers():
    """Headers with admin API key."""
    return {"x-api-key": "test_admin_key"}


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add slow marker to tests that take more than 1 second
        if "test_e2e" in item.nodeid or "test_performance" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # Add integration marker to integration tests
        if "test_api_endpoints" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add e2e marker to end-to-end tests
        if "test_e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)