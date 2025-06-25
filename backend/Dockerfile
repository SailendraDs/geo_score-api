FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir uvicorn

# Copy application code
COPY . .

<<<<<<< HEAD
# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app:$PYTHONPATH

=======
>>>>>>> a7333b61e6e22ec36d093c23e0574730aa8db091
# Install the package in development mode
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/data

# Use a non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
