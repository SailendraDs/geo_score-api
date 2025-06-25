import pytest
from unittest.mock import MagicMock

from geoscore.utils.wiki_check import check_wikipedia_presence


def test_check_wikipedia_presence_success(mock_wikipedia_page):
    """Test successful Wikipedia page check."""
    result = check_wikipedia_presence("Test Page")
    assert result["score"] > 0
    assert result["page_url"] is not None
    assert result["summary"] == "Test summary"


def test_check_wikipedia_presence_nonexistent_page():
    """Test Wikipedia check with non-existent page."""
    mock_page = MagicMock()
    mock_page.exists.return_value = False
    
    with patch("wikipediaapi.Wikipedia") as mock_wiki:
        mock_wiki.return_value.page.return_value = mock_page
        result = check_wikipedia_presence("Nonexistent Page")
    
    assert result["score"] == 0
    assert result["page_url"] is None
    assert "No Wikipedia page found" in result["summary"]


def test_check_wikipedia_presence_error_handling():
    """Test error handling in Wikipedia check."""
    with patch("wikipediaapi.Wikipedia") as mock_wiki:
        mock_wiki.side_effect = Exception("API Error")
        result = check_wikipedia_presence("Test Page")
    
    assert result["score"] == 0
    assert result["page_url"] is None
    assert "Error checking Wikipedia" in result["summary"]


def test_wikipedia_scoring_quality(mock_wikipedia_page):
    """Test the quality scoring of Wikipedia pages."""
    # Test with minimal content
    mock_wikipedia_page.text = "Short content"
    result = check_wikipedia_presence("Test Page")
    low_score = result["score"]
    
    # Test with more substantial content
    mock_wikipedia_page.text = "Longer content with more details and information. " * 50
    result = check_wikipedia_presence("Test Page")
    high_score = result["score"]
    
    assert high_score > low_score
    assert 0 <= low_score <= 100
    assert 0 <= high_score <= 100
