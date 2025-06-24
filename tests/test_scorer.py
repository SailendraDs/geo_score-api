import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4

from geoscore.services.scorer import calculate_geoscore, get_result, store_result
from geoscore.models.schemas import ScoreBreakdown, GeoEntity, ScoringResult


@patch('geoscore.services.scorer.check_wikipedia_presence')
@patch('geoscore.services.scorer.verify_with_llm')
@patch('geoscore.services.scorer.check_linkedin_presence')
@patch('geoscore.services.scorer.check_web_presence')
def test_calculate_geoscore_success(
    mock_web, mock_linkedin, mock_llm, mock_wiki, mock_env_vars
):
    """Test successful calculation of geoscore with all components."""
    # Mock component responses
    mock_wiki.return_value = {"score": 80, "page_url": "https://en.wikipedia.org/wiki/Test"}
    mock_llm.return_value = {"score": 90, "is_geographical": True, "confidence": 0.9}
    mock_linkedin.return_value = {"score": 70, "linkedin_url": "https://linkedin.com/company/test"}
    mock_web.return_value = {"score": 60, "result_count": 1000}
    
    # Test with a brand name and URL
    result = calculate_geoscore("Eiffel Tower", "https://example.com")
    
    # Verify the result structure
    assert isinstance(result, dict)
    assert "score" in result
    assert "score_breakdown" in result
    assert "scan_id" in result
    assert "timestamp" in result
    assert "metadata" in result
    
    # Verify the score calculation (average of all components)
    expected_score = (80 + 90 + 70 + 60) // 4
    assert result["score"] == expected_score
    
    # Verify all components were called
    mock_wiki.assert_called_once_with("Eiffel Tower")
    mock_llm.assert_called_once_with("Eiffel Tower")
    mock_linkedin.assert_called_once_with("Eiffel Tower")
    mock_web.assert_called_once_with("Eiffel Tower")


def test_store_and_get_result():
    """Test storing and retrieving a result."""
    # Create a test result
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
        "metadata": {"test": "data"}
    }
    
    # Store the result
    store_result(test_result)
    
    # Retrieve the result
    retrieved = get_result(test_result["scan_id"])
    
    # Verify the retrieved result matches the stored one
    assert retrieved == test_result


def test_get_nonexistent_result():
    """Test retrieving a non-existent result."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    result = get_result(non_existent_id)
    assert result is None


@patch('geoscore.services.scorer.check_wikipedia_presence')
@patch('geoscore.services.scorer.verify_with_llm')
@patch('geoscore.services.scorer.check_linkedin_presence')
@patch('geoscore.services.scorer.check_web_presence')
def test_calculate_geoscore_partial_failure(
    mock_web, mock_linkedin, mock_llm, mock_wiki, mock_env_vars
):
    """Test geoscore calculation with some components failing."""
    # Mock some successful and some failed responses
    mock_wiki.return_value = {"score": 80, "page_url": "https://en.wikipedia.org/wiki/Test"}
    mock_llm.return_value = {"score": 0, "error": "API Error"}  # Failed
    mock_linkedin.return_value = {"score": 0, "error": "Not found"}  # Failed
    mock_web.return_value = {"score": 60, "result_count": 1000}  # Success
    
    result = calculate_geoscore("Test Brand", "https://example.com")
    
    # Verify the result only includes successful components
    assert result["score"] == (80 + 60) // 2  # Average of successful components
    assert "wikipedia_presence" in result["score_breakdown"]
    assert "web_presence" in result["score_breakdown"]
    assert "llm_recall" not in result["score_breakdown"]
    assert "platform_visibility" not in result["score_breakdown"]


def test_geoscore_edge_cases():
    """Test edge cases in geoscore calculation."""
    # Test with empty brand name
    with pytest.raises(ValueError):
        calculate_geoscore("", "https://example.com")
    
    # Test with None brand name
    with pytest.raises(ValueError):
        calculate_geoscore(None, "https://example.com")
    
    # Test with invalid URL
    with pytest.raises(ValueError):
        calculate_geoscore("Test Brand", "not-a-url")
