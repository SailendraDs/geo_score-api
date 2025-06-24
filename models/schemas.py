"""
Data models and schemas for the GeoScore application.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class GeoEntity(BaseModel):
    """Represents a geographical entity with its properties."""
    name: str
    location: Optional[str] = None
    coordinates: Optional[tuple[float, float]] = None
    score: Optional[float] = None
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = {}


class ScoreRequest(BaseModel):
    """Request model for the /check-score endpoint."""
    brand_name: str = Field(..., description="The name of the brand to score")
    url: str = Field(..., description="The URL of the brand's website")


class ScoreBreakdown(BaseModel):
    """Breakdown of the GEO score components."""
    llm_recall: int = Field(..., ge=0, le=100, description="Score based on LLM knowledge")
    wikipedia_presence: int = Field(..., ge=0, le=100, description="Score based on Wikipedia presence")
    platform_visibility: int = Field(..., ge=0, le=100, description="Score based on LinkedIn presence")
    web_presence: int = Field(..., ge=0, le=100, description="Score based on web search results")


class ScoreResponse(BaseModel):
    """Response model for the /check-score endpoint."""
    score: int = Field(..., ge=0, le=100, description="Overall GEO score (0-100)")
    score_breakdown: ScoreBreakdown = Field(..., description="Detailed score breakdown")
    scan_id: str = Field(..., description="Unique identifier for this scan")
    timestamp: str = Field(..., description="ISO 8601 timestamp of when the scan was performed")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata about the scan"
    )


class ScoringResult(BaseModel):
    """Represents the result of a scoring operation."""
    entity: str
    score: float
    confidence: float
    details: Optional[Dict[str, Any]] = {}
    timestamp: Optional[str] = None
