import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from uuid import uuid4

from geoscore.main import app
from geoscore.models.schemas import ScoreRequest, ScoreResponse

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_check_score_endpoint_success():
    """Test successful score check through the API."""
    # Mock the calculate_geoscore function
    with patch("geoscore.services.scorer.calculate_geoscore") as mock_calculate:
        # Setup mock return value
        mock_result = {
            "score": 75,
            "score_breakdown": {
                "wikipedia_presence": 80,
                "llm_recall": 90,
                "platform_visibility": 70,
                "web_presence": 60
            },
            "scan_id": str(uuid4()),
            "timestamp": "2023-06-24T18:30:00.000Z",
            "metadata": {}
        }
        mock_calculate.return_value = mock_result
        
        # Make the request
        response = client.post(
            "/check-score",
            json={"brand_name": "Eiffel Tower", "url": "https://example.com"}
        )
        
        # Verify the response
        assert response.status_code == 200
        assert response.json() == mock_result
        mock_calculate.assert_called_once_with("Eiffel Tower", "https://example.com")


def test_check_score_missing_fields():
    """Test the score check endpoint with missing fields."""
    # Missing brand_name
    response = client.post("/check-score", json={"url": "https://example.com"})
    assert response.status_code == 422  # Validation error
    
    # Missing url
    response = client.post("/check-score", json={"brand_name": "Test"})
    assert response.status_code == 422  # Validation error


def test_get_result_endpoint():
    """Test retrieving a result by scan_id."""
    # First create a test result
    test_result = {
        "score": 75,
        "score_breakdown": {
            "wikipedia_presence": 80,
            "llm_recall": 90,
            "platform_visibility": 70,
            "web_presence": 60
        },
        "scan_id": str(uuid4()),
        "timestamp": "2023-06-24T18:30:00.000Z",
        "metadata": {}
    }
    
    # Store the test result
    with patch("geoscore.services.scorer.store_result") as mock_store, \
         patch("geoscore.services.scorer.get_result") as mock_get:
        mock_get.return_value = test_result
        
        # Try to retrieve the result
        response = client.get(f"/results/{test_result['scan_id']}")
        
        # Verify the response
        assert response.status_code == 200
        assert response.json() == test_result
        mock_get.assert_called_once_with(test_result["scan_id"])


def test_get_nonexistent_result():
    """Test retrieving a non-existent result."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    with patch("geoscore.services.scorer.get_result") as mock_get:
        mock_get.return_value = None
        
        response = client.get(f"/results/{non_existent_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


def test_check_score_error_handling():
    """Test error handling in the check-score endpoint."""
    with patch("geoscore.services.scorer.calculate_geoscore") as mock_calculate:
        # Simulate an error in the calculation
        mock_calculate.side_effect = Exception("Test error")
        
        response = client.post(
            "/check-score",
            json={"brand_name": "Test", "url": "https://example.com"}
        )
        
        assert response.status_code == 500
        assert "error" in response.json()
        assert "Test error" in response.json()["error"]


def test_cors_headers():
    """Test that CORS headers are properly set."""
    # Make a preflight request
    response = client.options(
        "/check-score",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    
    # Check CORS headers
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers
