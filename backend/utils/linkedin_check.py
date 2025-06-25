"""
Utility for checking if a company has a LinkedIn presence.
"""
from typing import Optional, Dict, Any
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re
from fake_useragent import UserAgent


def check_linkedin_presence(company_name: str) -> Dict[str, Any]:
    """
    Check if a company has a LinkedIn presence by searching Google.
    
    Args:
        company_name: Name of the company to check
        
    Returns:
        Dictionary containing:
        - score: int (0-100)
        - url: Optional[str] - LinkedIn URL if found
        - details: Dict with additional information
    """
    try:
        # Create search query
        query = f"{company_name} site:linkedin.com/company"
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&hl=en"
        
        # Use a random user agent to avoid bot detection
        ua = UserAgent()
        headers = {
            "User-Agent": ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
        }
        
        # Make the request
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse the response
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for LinkedIn URLs in the search results
        linkedin_urls = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'linkedin.com/company/' in href and 'google.com' not in href:
                # Extract the actual LinkedIn URL from Google's redirect
                match = re.search(r'url\?q=([^&]+)', href)
                if match:
                    url = match.group(1)
                    linkedin_urls.append(url)
        
        if linkedin_urls:
            # Get the first unique LinkedIn URL
            linkedin_url = linkedin_urls[0].split('&')[0]  # Remove any tracking parameters
            return {
                'score': 100,
                'url': linkedin_url,
                'details': {
                    'method': 'google_search',
                    'confidence': 'high',
                    'matches_found': len(linkedin_urls)
                }
            }
        
        # If no LinkedIn URL found in search results
        return {
            'score': 0,
            'url': None,
            'details': {
                'method': 'google_search',
                'confidence': 'high',
                'message': 'No LinkedIn company page found'
            }
        }
        
    except requests.RequestException as e:
        return {
            'score': 0,
            'url': None,
            'details': {
                'method': 'google_search',
                'error': str(e),
                'confidence': 'low',
                'message': 'Error performing search'
            }
        }
    except Exception as e:
        return {
            'score': 0,
            'url': None,
            'details': {
                'method': 'google_search',
                'error': str(e),
                'confidence': 'low',
                'message': 'Unexpected error'
            }
        }
