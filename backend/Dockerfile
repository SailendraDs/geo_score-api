# Use official Python image as base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend:/app

# Create a non-root user and working directory
RUN useradd -m appuser && \
    mkdir -p /app/backend && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY --chown=appuser:appuser requirements.txt .
COPY --chown=appuser:appuser setup.py .

# Install system dependencies and Python packages
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Copy the rest of the application
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]