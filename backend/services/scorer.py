"""
Scoring service for geographical entities.
"""
import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from backend.data.db_utils import save_scan

from models.schemas import GeoEntity, ScoreRequest, ScoreResponse, ScoreBreakdown
from utils.wiki_check import WikipediaChecker
from utils.llm_check import LLMChecker
from utils.linkedin_check import check_linkedin_presence
from utils.web_presence import check_web_presence

class Scorer:
    """Handles scoring of geographical entities."""
    
    def __init__(self):
        self.wiki_checker = WikipediaChecker()
        self.llm_checker = LLMChecker()
        self.results: Dict[str, Any] = {}
        
        # Define weights for each scoring component
        self.weights = {
            'wikipedia': 0.3,  # 30% weight
            'llm': 0.3,        # 30% weight
            'linkedin': 0.2,   # 20% weight
            'web': 0.2         # 20% weight
        }
    
    async def calculate_score(self, brand_name: str, url: str) -> ScoreResponse:
        """
        Calculate a GEO score for the given brand using weighted scoring.
        
        Args:
            brand_name: Name of the brand to score
            url: URL of the brand's website
            
        Returns:
            ScoreResponse: The scoring result with weighted score
        """
        # Create a GeoEntity
        entity = GeoEntity(name=brand_name, location=None, metadata={'url': url})
        
        # Run all checks in parallel
        wiki_task = asyncio.create_task(self._check_wikipedia(entity))
        llm_task = asyncio.create_task(self.llm_checker.verify_entity(entity))
        
        # Run synchronous checks in thread pool
        loop = asyncio.get_running_loop()
        linkedin_task = loop.run_in_executor(None, check_linkedin_presence, brand_name)
        web_task = loop.run_in_executor(None, check_web_presence, brand_name)
        
        # Wait for all tasks to complete
        wiki_result, llm_result, linkedin_result, web_result = await asyncio.gather(
            wiki_task, llm_task, linkedin_task, web_task
        )
        
        # Calculate weighted score
        weighted_score = int(
            wiki_result['score'] * self.weights['wikipedia'] +
            llm_result['score'] * self.weights['llm'] +
            linkedin_result['score'] * self.weights['linkedin'] +
            web_result['score'] * self.weights['web']
        )
        
        # Create response with weighted score
        response = ScoreResponse(
            score=weighted_score,
            score_breakdown=ScoreBreakdown(
                llm_recall=llm_result['score'],
                wikipedia_presence=wiki_result['score'],
                platform_visibility=linkedin_result['score'],
                web_presence=web_result['score']
            ),
            scan_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            metadata={
                'checks': {
                    'wikipedia': wiki_result['details'],
                    'llm': llm_result['details'],
                    'linkedin': linkedin_result['details'],
                    'web': web_result['details']
                },
                'entity': entity.dict(),
                'weights': self.weights  # Include weights in metadata for reference
            }
        )
        
        # Store the result
        self._store_result(response)
        
        return response
    
    async def _check_wikipedia(self, entity: GeoEntity) -> Dict[str, Any]:
        """Check Wikipedia presence with error handling."""
        try:
            return self.wiki_checker.check_entity(entity.name)
        except Exception as e:
            return {
                'score': 0,
                'details': {
                    'error': str(e),
                    'confidence': 'low',
                    'message': 'Error checking Wikipedia',
                    'method': 'wikipedia_api'
                }
            }
    
    def get_result(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a stored result by scan ID."""
        return self.results.get(scan_id)
    
    def get_all_results(self) -> Dict[str, Any]:
        """Retrieve all stored results."""
        return self.results


# In the Scorer class, update the _store_result method:
async def _store_result(self, result: ScoreResponse) -> None:
    """
    Store the scan result in the database.
    
    Args:
        result: The ScoreResponse to store
    """
    scan_data = {
        'scan_id': result.scan_id,
        'brand_name': result.metadata['entity']['name'],
        'url': result.metadata['entity']['metadata'].get('url'),
        'score': result.score,
        'score_breakdown': result.score_breakdown.dict(),
        'timestamp': result.timestamp,
        'metadata': result.metadata
    }
    await save_scan(scan_data)