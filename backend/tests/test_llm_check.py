import json
import pytest
from unittest.mock import patch

from geoscore.utils.llm_check import verify_with_llm


def test_verify_with_llm_success(mock_openai_chat_completion):
    """Test successful LLM verification."""
    result = verify_with_llm("Eiffel Tower")
    
    assert result["score"] == 90  # 0.9 * 100
    assert result["is_geographical"] is True
    assert result["confidence"] == 0.9
    assert result["reasoning"] == "Test reason"
    assert "error" not in result


def test_verify_with_llm_invalid_json():
    """Test handling of invalid JSON response from LLM."""
    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.return_value = {
            "choices": [{"message": {"content": "invalid json"}}]
        }
        result = verify_with_llm("Test Entity")
    
    assert result["score"] == 0
    assert "error" in result
    assert "Failed to parse LLM response" in result["error"]


def test_verify_with_llm_api_error():
    """Test handling of API errors from OpenAI."""
    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.side_effect = Exception("API Error")
        result = verify_with_llm("Test Entity")
    
    assert result["score"] == 0
    assert "error" in result
    assert "API Error" in result["error"]


def test_verify_with_llm_low_confidence():
    """Test scoring with low confidence from LLM."""
    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "is_geographical": True,
                            "confidence": 0.3,
                            "reasoning": "Low confidence reason"
                        })
                    }
                }
            ]
        }
        result = verify_with_llm("Borderline Entity")
    
    assert result["score"] == 30  # 0.3 * 100
    assert result["is_geographical"] is True
    assert result["confidence"] == 0.3
    assert result["reasoning"] == "Low confidence reason"


def test_verify_with_llm_not_geographical():
    """Test with entity that is not geographical."""
    with patch("openai.ChatCompletion.create") as mock_create:
        mock_create.return_value = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps({
                            "is_geographical": False,
                            "confidence": 0.95,
                            "reasoning": "Not a geographical entity"
                        })
                    }
                }
            ]
        }
        result = verify_with_llm("Test Company")
    
    assert result["score"] == 0  # Score should be 0 when not geographical
    assert result["is_geographical"] is False
    assert result["confidence"] == 0.95
