import pytest
from unittest.mock import MagicMock, patch

from geoscore.utils.web_presence import check_web_presence


def test_check_web_presence_google_api_success(mock_google_search_response):
    """Test successful web presence check using Google API."""
    with patch("googleapiclient.discovery.build") as mock_build:
        # Mock Google API response
        mock_service = MagicMock()
        mock_cse = MagicMock()
        mock_list = MagicMock()
        
        mock_build.return_value = mock_service
        mock_service.cse.return_value = mock_cse
        mock_cse.list.return_value = mock_list
        mock_list.execute.return_value = mock_google_search_response
        
        result = check_web_presence("Test Brand")
    
    assert result["score"] > 0
    assert result["result_count"] == 42
    assert "google" in result["source"]
    assert "error" not in result


def test_check_web_presence_fallback_success(mock_requests_get):
    """Test fallback to web scraping when API fails."""
    # Mock Google API failure
    with patch("googleapiclient.discovery.build") as mock_build:
        mock_build.side_effect = Exception("API Error")
        
        # Mock successful web scraping response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <div id="result-stats">About 1,230 results</div>
        </html>
        """
        mock_requests_get.return_value = mock_response
        
        result = check_web_presence("Test Brand")
    
    assert result["score"] > 0
    assert result["result_count"] == 1230
    assert "scraping" in result["source"]
    assert "error" not in result


def test_check_web_presence_api_failure():
    """Test handling of complete API and scraping failure."""
    with patch("googleapiclient.discovery.build") as mock_build, \
         patch("requests.get") as mock_get:
        # Mock both API and scraping failures
        mock_build.side_effect = Exception("API Error")
        mock_get.side_effect = Exception("Scraping Error")
        
        result = check_web_presence("Test Brand")
    
    assert result["score"] == 0
    assert "error" in result
    assert "Failed to check web presence" in result["error"]


def test_web_presence_scoring():
    """Test the scoring logic for web presence."""
    with patch("googleapiclient.discovery.build") as mock_build:
        mock_service = MagicMock()
        mock_cse = MagicMock()
        mock_list = MagicMock()
        
        mock_build.return_value = mock_service
        mock_service.cse.return_value = mock_cse
        
        # Test with low result count
        mock_list.execute.return_value = {
            "searchInformation": {"totalResults": "5"},
            "items": [{"title": "Test"} for _ in range(5)]
        }
        mock_cse.list.return_value = mock_list
        low_score = check_web_presence("Test Brand")["score"]
        
        # Test with high result count
        mock_list.execute.return_value = {
            "searchInformation": {"totalResults": "100000"},
            "items": [{"title": "Test"} for _ in range(10)]
        }
        high_score = check_web_presence("Test Brand")["score"]
    
    assert 0 < low_score < high_score <= 100


def test_check_web_presence_invalid_response():
    """Test handling of invalid API response."""
    with patch("googleapiclient.discovery.build") as mock_build:
        mock_service = MagicMock()
        mock_cse = MagicMock()
        mock_list = MagicMock()
        
        mock_build.return_value = mock_service
        mock_service.cse.return_value = mock_cse
        mock_cse.list.return_value = mock_list
        mock_list.execute.return_value = {"invalid": "response"}  # Missing required fields
        
        result = check_web_presence("Test Brand")
    
    assert result["score"] == 0
    assert "error" in result
    assert "Invalid API response" in result["error"]
