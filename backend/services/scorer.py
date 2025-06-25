"""
Scoring service for geographical entities.
"""
import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Use absolute imports without the 'backend.' prefix
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
    
    async def calculate_score(self, brand_name: str, url: str) -> ScoreResponse:
        """
        Calculate a GEO score for the given brand.
        
        Args:
            brand_name: Name of the brand to score
            url: URL of the brand's website
            
        Returns:
            ScoreResponse: The scoring result
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
        
        # Calculate final score (simple average for now)
        scores = [
            wiki_result['score'],
            llm_result['score'],
            linkedin_result['score'],
            web_result['score']
        ]
        final_score = int(sum(scores) / len(scores))
        
        # Create response
        response = ScoreResponse(
            score=final_score,
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
                'entity': entity.dict()
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
    
    def _store_result(self, result: ScoreResponse) -> None:
        """Store the scoring result."""
        self.results[result.scan_id] = result.dict()
        
        # Also save to file (in production, consider using a database)
        try:
            import os
            os.makedirs('data', exist_ok=True)
            with open('data/temp_results.json', 'w') as f:
                json.dump(self.results, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save results: {str(e)}")
    
    def get_result(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a stored result by scan ID."""
        return self.results.get(scan_id)
    
    def get_all_results(self) -> Dict[str, Any]:
        """Retrieve all stored results."""
        return self.results
