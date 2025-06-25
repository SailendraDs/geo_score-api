"""
Utility for checking if a company has a LinkedIn presence.
"""
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import re
from fake_useragent import UserAgent


def check_google_search(company_name: str) -> Optional[Dict[str, Any]]:
    """Check LinkedIn presence using Google search."""
    try:
        query = f"{company_name} site:linkedin.com/company"
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&hl=en"
        
        ua = UserAgent()
        headers = {
            "User-Agent": ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        linkedin_urls = []
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'linkedin.com/company/' in href and 'google.com' not in href:
                match = re.search(r'url\?q=([^&]+)', href)
                if match:
                    url = match.group(1)
                    if url not in linkedin_urls:
                        linkedin_urls.append(url)
        
        if linkedin_urls:
            return {
                'score': 100,
                'url': linkedin_urls[0].split('&')[0],
                'details': {
                    'method': 'google_search',
                    'matches_found': len(linkedin_urls),
                    'confidence': 'high'
                }
            }
    except Exception as e:
        print(f"Google search failed: {e}")
    return None

def check_bing_search(company_name: str) -> Optional[Dict[str, Any]]:
    """Check LinkedIn presence using Bing search."""
    try:
        query = f'site:linkedin.com/company "{company_name}"'
        search_url = f"https://www.bing.com/search?q={quote_plus(query)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        for a_tag in soup.select('li.b_algo h2 a'):
            href = a_tag.get('href', '')
            if 'linkedin.com/company/' in href.lower():
                clean_url = href.split('?')[0]
                if clean_url not in links:
                    links.append(clean_url)
        
        if links:
            return {
                'score': 100,
                'url': links[0],
                'details': {
                    'method': 'bing_search',
                    'matches_found': len(links),
                    'confidence': 'high'
                }
            }
    except Exception as e:
        print(f"Bing search failed: {e}")
    return None

def check_linkedin_presence(company_name: str) -> Dict[str, Any]:
    """
    Check if a company has a LinkedIn presence by searching Google first, then Bing.
    
    Args:
        company_name: Name of the company to check
        
    Returns:
        Dictionary containing:
        - score: int (0-100)
        - url: Optional[str] - LinkedIn URL if found
        - details: Dict with additional information
    """
    # Try Google first
    result = check_google_search(company_name)
    
    # If Google fails, try Bing
    if not result:
        result = check_bing_search(company_name)
    
    # If both fail, return not found
    if not result:
        return {
            'score': 0,
            'url': None,
            'details': {
                'method': 'search',
                'message': 'No LinkedIn company page found',
                'confidence': 'medium'
            }
        }
    
    return result
