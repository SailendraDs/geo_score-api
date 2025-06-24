"""
Utility for checking geographical entities against Wikipedia.
"""
import wikipediaapi
from typing import Dict, Any, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WikipediaChecker:
    """Handles Wikipedia lookups for geographical entities."""
    
    def __init__(self, language: str = 'en'):
        """
        Initialize the Wikipedia checker.
        
        Args:
            language: Language code for Wikipedia (default: 'en')
        """
        self.wiki = wikipediaapi.Wikipedia(
            language=language,
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='GeoScore/1.0 (your-email@example.com)'
        )
    
    def check_entity(self, entity_name: str) -> Dict[str, Any]:
        """
        Check if an entity exists on Wikipedia and get a score based on content quality.
        
        Args:
            entity_name: Name of the entity to look up
            
        Returns:
            Dictionary containing:
            - score: int (0-100)
            - url: Optional[str] - Wikipedia URL if found
            - details: Dict with additional information
        """
        try:
            page = self.wiki.page(entity_name)
            
            if not page.exists():
                return {
                    'score': 0,
                    'url': None,
                    'details': {
                        'exists': False,
                        'confidence': 'high',
                        'message': 'No Wikipedia page found'
                    }
                }
            
            # Calculate score based on page content
            score = self._calculate_wiki_score(page)
            
            return {
                'score': score,
                'url': page.fullurl,
                'details': {
                    'exists': True,
                    'title': page.title,
                    'summary_length': len(page.summary) if page.summary else 0,
                    'confidence': 'high',
                    'method': 'wikipedia_api'
                }
            }
            
        except Exception as e:
            logger.error(f"Error checking Wikipedia for {entity_name}: {str(e)}")
            return {
                'score': 0,
                'url': None,
                'details': {
                    'error': str(e),
                    'confidence': 'low',
                    'message': 'Error checking Wikipedia'
                }
            }
    
    def _calculate_wiki_score(self, page) -> int:
        """
        Calculate a score based on Wikipedia page quality.
        
        Args:
            page: Wikipedia page object
            
        Returns:
            int: Score from 0-100
        """
        score = 0
        
        # Basic existence gives points
        if page.exists():
            score = 50
            
            # Add points for page content
            if page.summary:
                score += 20
                
                # More detailed content
                if len(page.summary) > 500:
                    score += 15
                elif len(page.summary) > 200:
                    score += 10
                    
            # Check for important sections
            if page.sections:
                score += 15
                
                # Check for specific important sections
                section_titles = [s.title.lower() for s in page.sections]
                important_sections = ['history', 'geography', 'location', 'description']
                
                for section in important_sections:
                    if any(section in title for title in section_titles):
                        score += 5
            
            # Cap the score at 100
            score = min(score, 100)
            
        return score
