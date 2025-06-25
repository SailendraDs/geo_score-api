#!/bin/bash

# Exit on any error
set -e

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Create data directory if it doesn't exist
mkdir -p data

# Install the package in development mode
pip install -e .

# Install production dependencies
pip install -r requirements.txt

# Set Python path to include current directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run the FastAPI application with Uvicorn
echo "Starting GeoScore API..."
uvicorn main:app \
    --host ${HOST:-0.0.0.0} \
    --port ${PORT:-8000} \
    --reload
