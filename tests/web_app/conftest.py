"""Test configuration specific to web_app backend."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch


@pytest.fixture
def test_client():
    """Create a test client for FastAPI app."""
    with patch.dict('os.environ', {
        'AZURE_STORAGE_CONNECTION_STRING': 'DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test',
        'AZURE_CONTAINER_NAME': 'test-container',
        'CHROMA_HOST': 'localhost',
        'CHROMA_PORT': '8000',
        'CHROMA_USE_SSL': 'false',
        'REDIS_HOST': 'localhost',
        'REDIS_PORT': '6379'
    }):
        # Import here to ensure environment variables are set
        from web_app.backend.main import app
        return TestClient(app)


@pytest.fixture
def mock_azure_storage():
    """Mock Azure storage client."""
    mock_client = Mock()
    mock_client.get_blob_client.return_value.download_blob.return_value.readall.return_value = b"Mock CV content"
    return mock_client


@pytest.fixture
def mock_redis_client():
    """Mock Redis client."""
    mock_client = Mock()
    mock_client.get.return_value = None  # No cached data by default
    mock_client.setex.return_value = True
    return mock_client


@pytest.fixture
def mock_chroma_client():
    """Mock ChromaDB client."""
    mock_client = Mock()
    mock_collection = Mock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_collection.query.return_value = {
        'ids': [['job_1', 'job_2']],
        'metadatas': [[
            {'title': 'Data Scientist', 'company': 'TechCorp'},
            {'title': 'ML Engineer', 'company': 'DataCorp'}
        ]],
        'distances': [[0.1, 0.3]]
    }
    return mock_client