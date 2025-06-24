#!/bin/bash

# Exit on any error
set -e

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Create data directory if it doesn't exist
mkdir -p data

# Run the FastAPI application with Uvicorn
echo "Starting GeoScore API..."
uvicorn main:app \
    --host ${HOST:-0.0.0.0} \
    --port ${PORT:-8000} \
    --reload

echo "Server stopped."
