#!/usr/bin/env python3
"""
GeoScore - A FastAPI service for scoring geographical entities.
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from datetime import datetime

# Use relative imports
from .models.schemas import ScoreRequest, ScoreResponse
from .services.scorer import Scorer
from .data.db_utils import save_scan, get_scan, get_all_scans

# Initialize FastAPI app
app = FastAPI(
    title="GeoScore API",
    description="API for scoring geographical entities based on various factors",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://geoscore.vercel.app",  # Production frontend
        "https://geoscore.in",        # Production
        "http://localhost:8000",        # Local backend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the scorer
scorer = Scorer()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    from .data.db_utils import setup_db
    await setup_db()
    print("Database initialized")

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/check-score", response_model=ScoreResponse, status_code=status.HTTP_200_OK)
async def check_score(payload: ScoreRequest) -> ScoreResponse:
    """
    Calculate a GEO score for the given brand.
    
    Args:
        payload: ScoreRequest containing brand_name and url
        
    Returns:
        ScoreResponse with the calculated score and breakdown
    """
    try:
        # Calculate the score asynchronously
        result = await scorer.calculate_score(
            brand_name=payload.brand_name,
            url=payload.url
        )
        
        # Save the scan result to the database
        scan_data = {
            'scan_id': result.scan_id,
            'brand_name': payload.brand_name,
            'url': payload.url,
            'score': result.score,
            'score_breakdown': result.score_breakdown.dict(),
            'timestamp': result.timestamp,
            'metadata': result.metadata
        }
        await save_scan(scan_data)
        
        return result
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@app.get("/results/{scan_id}", response_model=ScoreResponse)
async def get_result(scan_id: str):
    """
    Retrieve a previously calculated score by scan ID.
    
    Args:
        scan_id: The ID of the scan to retrieve
        
    Returns:
        The stored ScoreResponse or 404 if not found
    """
    result = await get_scan(scan_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No result found with ID: {scan_id}"
        )
    return result

@app.get("/history", response_model=List[Dict[str, Any]])
async def get_history(limit: int = Query(10, ge=1, le=100, description="Number of results to return")):
    """
    Get scan history.
    
    Args:
        limit: Maximum number of results to return (1-100)
        
    Returns:
        List of recent scan results
    """
    try:
        return await get_all_scans(limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving scan history: {str(e)}"
        )

@app.get("/suggestions/{scan_id}", response_model=Dict[str, Any])
async def get_suggestions(scan_id: str):
    """
    Get improvement suggestions for a scan.
    
    Args:
        scan_id: The ID of the scan to get suggestions for
        
    Returns:
        Dictionary containing suggestions for improvement
    """
    try:
        # Get the scan result
        scan = await get_scan(scan_id)
        if not scan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No scan found with ID: {scan_id}"
            )
        
        # Generate suggestions based on the score breakdown
        breakdown = scan.get('score_breakdown', {})
        suggestions = []
        
        if breakdown.get('wikipedia_presence', 0) < 50:
            suggestions.append("Consider creating or improving your Wikipedia page.")
        
        if breakdown.get('llm_recall', 0) < 50:
            suggestions.append("Improve your online mentions and media coverage for better LLM recall.")
        
        if breakdown.get('platform_visibility', 0) < 50:
            suggestions.append("Strengthen your LinkedIn and developer profiles.")
        
        if breakdown.get('web_presence', 0) < 50:
            suggestions.append("Increase website SEO and digital PR efforts.")
        
        return {
            "scan_id": scan_id,
            "suggestions": suggestions,
            "score": scan.get('score', 0),
            "brand_name": scan.get('brand_name', 'Unknown')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating suggestions: {str(e)}"
        )

if __name__ == "__main__":
    # Run the FastAPI application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
