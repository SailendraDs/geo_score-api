import pytest
from unittest.mock import MagicMock, patch

from geoscore.utils.linkedin_check import check_linkedin_presence


def test_check_linkedin_presence_success(mock_requests_get):
    """Test successful LinkedIn presence check."""
    # Mock successful Google search response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <div class="g">
            <div class="r">
                <a href="https://www.linkedin.com/company/test-company/">Test Company | LinkedIn</a>
            </div>
        </div>
    </html>
    """
    mock_requests_get.return_value = mock_response
    
    result = check_linkedin_presence("Test Company")
    
    assert result["score"] == 100
    assert "linkedin.com/company/test-company" in result["linkedin_url"]
    assert "error" not in result


def test_check_linkedin_presence_not_found(mock_requests_get):
    """Test when no LinkedIn page is found."""
    # Mock empty Google search results
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>No results found</body></html>"
    mock_requests_get.return_value = mock_response
    
    result = check_linkedin_presence("Nonexistent Company")
    
    assert result["score"] == 0
    assert result["linkedin_url"] is None
    assert "No LinkedIn page found" in result["error"]


def test_check_linkedin_presence_http_error(mock_requests_get):
    """Test handling of HTTP errors."""
    # Mock HTTP error
    mock_requests_get.side_effect = Exception("HTTP Error")
    
    result = check_linkedin_presence("Test Company")
    
    assert result["score"] == 0
    assert result["linkedin_url"] is None
    assert "Error checking LinkedIn presence" in result["error"]


def test_check_linkedin_presence_multiple_results(mock_requests_get):
    """Test handling of multiple search results."""
    # Mock multiple search results
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <div class="g">
            <div class="r">
                <a href="https://www.linkedin.com/company/company1/">Company 1 | LinkedIn</a>
            </div>
        </div>
        <div class="g">
            <div class="r">
                <a href="https://www.linkedin.com/company/company2/">Company 2 | LinkedIn</a>
            </div>
        </div>
    </html>
    """
    mock_requests_get.return_value = mock_response
    
    result = check_linkedin_presence("Test Company")
    
    # Should return the first result
    assert result["score"] == 100
    assert "linkedin.com/company/company1" in result["linkedin_url"]


def test_check_linkedin_presence_invalid_url(mock_requests_get):
    """Test handling of invalid LinkedIn URLs in search results."""
    # Mock search results with invalid LinkedIn URL
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <html>
        <div class="g">
            <div class="r">
                <a href="https://www.notlinkedin.com/company/test/">Not LinkedIn | Test</a>
            </div>
        </div>
    </html>
    """
    mock_requests_get.return_value = mock_response
    
    result = check_linkedin_presence("Test Company")
    
    assert result["score"] == 0
    assert result["linkedin_url"] is None
    assert "No valid LinkedIn URL found" in result["error"]
