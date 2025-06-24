"""
Utility for checking a brand's web presence using Google's Programmable Search Engine API.
"""
from typing import Dict, Any, Optional
import os
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_web_presence(brand_name: str) -> Dict[str, Any]:
    """
    Check a brand's web presence using Google's Programmable Search Engine API.
    
    Args:
        brand_name: The name of the brand to check
        
    Returns:
        Dictionary containing:
        - score: int (0-100)
        - results_count: Optional[int] - Number of search results
        - details: Dict with additional information
    """
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        cx = os.getenv('GOOGLE_CSE_ID')
        
        if not api_key or not cx:
            return _fallback_web_check(brand_name)
            
        # Make the API request
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': brand_name,
            'key': api_key,
            'cx': cx,
            'num': 1  # We only need the total results count
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Extract the total results count
        total_results = int(data.get('searchInformation', {}).get('totalResults', 0))
        
        # Calculate score based on result count
        if total_results > 1000000:
            score = 90
        elif total_results > 100000:
            score = 70
        elif total_results > 10000:
            score = 50
        elif total_results > 1000:
            score = 30
        else:
            score = 10
            
        return {
            'score': score,
            'results_count': total_results,
            'details': {
                'method': 'google_cse_api',
                'confidence': 'high',
                'search_term': brand_name
            }
        }
        
    except requests.RequestException as e:
        # Fallback to basic search if API fails
        return _fallback_web_check(brand_name)
    except Exception as e:
        return {
            'score': 0,
            'results_count': 0,
            'details': {
                'method': 'google_cse_api',
                'error': str(e),
                'confidence': 'low',
                'message': 'Error checking web presence'
            }
        }


def _fallback_web_check(brand_name: str) -> Dict[str, Any]:
    """
    Fallback method to check web presence using basic search.
    This is used when the Google CSE API is not available.
    """
    try:
        # This is a very basic check and may be blocked by Google
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        search_url = f"https://www.google.com/search?q={requests.utils.quote(brand_name)}"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Very basic check for result count in the page
        content = response.text.lower()
        if 'about' in content and 'results' in content:
            # This is a very rough estimate and may not be accurate
            return {
                'score': 50,  # Medium confidence score for fallback
                'results_count': None,
                'details': {
                    'method': 'fallback_search',
                    'confidence': 'medium',
                    'message': 'Used fallback search method',
                    'search_term': brand_name
                }
            }
            
        return {
            'score': 20,  # Low confidence score
            'results_count': None,
            'details': {
                'method': 'fallback_search',
                'confidence': 'low',
                'message': 'No clear result count found',
                'search_term': brand_name
            }
        }
        
    except Exception:
        return {
            'score': 0,
            'results_count': None,
            'details': {
                'method': 'fallback_search',
                'confidence': 'low',
                'message': 'Error in fallback search',
                'search_term': brand_name
            }
        }
