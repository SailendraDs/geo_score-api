FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy setup files first to leverage Docker cache
COPY setup.py .
COPY requirements.txt .

# Install Python dependencies and package in development mode
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Copy application code
COPY . .

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app

# Create necessary directories
RUN mkdir -p /app/data && \
    touch /app/data/__init__.py

# Use a non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
