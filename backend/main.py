#!/usr/bin/env python3
"""
GeoScore - A FastAPI service for scoring geographical entities.
"""
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# Use absolute imports
from models.schemas import ScoreRequest, ScoreResponse
from services.scorer import Scorer

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
        "https://geoscore.in",        # Local development
        "http://localhost:8000",        # Local backend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the scorer
scorer = Scorer()

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "healthy"}


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
    result = scorer.get_result(scan_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No result found with ID: {scan_id}"
        )
    return result


if __name__ == "__main__":
    # Run the FastAPI application
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "true").lower() == "true"
    )
