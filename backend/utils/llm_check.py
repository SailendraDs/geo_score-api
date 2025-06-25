"""
Utility for verifying geographical entities using LLM.
"""
import os
import openai
import logging
from typing import Dict, Any, Optional
from models.schemas import GeoEntity
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

class LLMChecker:
    """Handles verification of geographical entities using LLM."""
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the LLM checker.
        
        Args:
            model: The model to use (default: 'gpt-4')
        """
        self.model = model
        self.max_retries = 3
    
    async def verify_entity(self, entity: GeoEntity) -> Dict[str, Any]:
        """
        Verify a geographical entity using LLM.
        
        Args:
            entity: The geographical entity to verify
            
        Returns:
            Dict containing:
            - score: int (0-100)
            - confidence: float (0-1)
            - details: Dict with additional information
        """
        if not openai.api_key:
            logger.warning("OpenAI API key not found. Skipping LLM check.")
            return self._create_error_response("OpenAI API key not configured")
        
        prompt = self._create_prompt(entity)
        
        for attempt in range(self.max_retries):
            try:
                response = await openai.ChatCompletion.acreate(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that verifies geographical entities."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                return self._parse_response(response, entity.name)
                
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"LLM verification failed after {self.max_retries} attempts: {str(e)}")
                    return self._create_error_response(f"LLM verification failed: {str(e)}")
                continue
    
    def _create_prompt(self, entity: GeoEntity) -> str:
        """Create a prompt for the LLM to verify the entity."""
        return f"""Please analyze the geographical entity: {entity.name}
        
Provide a verification with the following:
1. Existence: Does this appear to be a valid geographical location? (Yes/No)
2. Type: What type of location is it? (e.g., city, country, landmark, etc.)
3. Confidence: On a scale of 0-100, how confident are you in your assessment?
4. Details: A brief explanation of your assessment.

Format your response as a JSON object with the following keys:
{{
  "exists": boolean,
  "type": string,
  "confidence": number (0-100),
  "details": string
}}"""
    
    def _parse_response(self, response: Any, entity_name: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured format."""
        try:
            content = response.choices[0].message.content
            
            # Try to parse the JSON response
            import json
            result = json.loads(content.strip())
            
            # Calculate score based on existence and confidence
            if result.get('exists', False):
                score = int(result.get('confidence', 50))  # Use LLM's confidence as score
            else:
                score = 0
            
            return {
                'score': score,
                'confidence': result.get('confidence', 0) / 100.0,  # Convert to 0-1 range
                'details': {
                    'type': result.get('type', 'unknown'),
                    'explanation': result.get('details', ''),
                    'model': self.model,
                    'method': 'llm_verification'
                }
            }
            
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            return self._create_error_response(f"Invalid response format from LLM: {str(e)}")
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create an error response with score 0 and error details."""
        return {
            'score': 0,
            'confidence': 0.0,
            'details': {
                'error': error_msg,
                'confidence': 'low',
                'method': 'llm_verification',
                'model': self.model
            }
        }
