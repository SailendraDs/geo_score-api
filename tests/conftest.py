import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app  # noqa: E402


@pytest.fixture(scope="module")
def test_client():
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test_openai_key",
            "GOOGLE_API_KEY": "test_google_key",
            "GOOGLE_CSE_ID": "test_cse_id",
        },
    ):
        yield


@pytest.fixture
def mock_requests_get():
    """Mock requests.get for testing HTTP requests."""
    with patch("requests.get") as mock_get:
        yield mock_get


@pytest.fixture
def mock_wikipedia_page():
    """Mock Wikipedia page object for testing."""
    mock_page = MagicMock()
    mock_page.exists.return_value = True
    mock_page.summary = "Test summary"
    mock_page.text = "Test page content"
    return mock_page


@pytest.fixture
def mock_wikipedia_api(mock_wikipedia_page):
    """Mock Wikipedia API for testing."""
    with patch("wikipediaapi.Wikipedia") as mock_wiki:
        mock_wiki.return_value.page.return_value = mock_wikipedia_page
        yield mock_wiki


@pytest.fixture
def mock_openai_chat_completion():
    """Mock OpenAI chat completion for testing."""
    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"is_geographical": true, "confidence": 0.9, "reasoning": "Test reason"}'
                    }
                }
            ]
        }
        yield mock_create


@pytest.fixture
def score_request_data():
    """Sample score request data for testing."""
    return {"brand_name": "Test Brand", "url": "https://example.com"}


@pytest.fixture
def mock_google_search_response():
    """Mock Google Custom Search API response."""
    return {
        "items": [
            {"title": "Test Result 1", "link": "https://example.com/1"},
            {"title": "Test Result 2", "link": "https://example.com/2"},
        ],
        "searchInformation": {"totalResults": "42"},
    }
