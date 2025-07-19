FROM python:3.12-slim

WORKDIR /app

# Set environment variables for Phase 1 AI Integration
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies for AI services
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Debug: List contents to verify all files are present in the image
RUN ls -l /app && ls -l /app/auth && ls -l /app/api
RUN echo "=== Checking for password_utils.py ===" && ls -la /app/auth/password_utils.py || echo "password_utils.py NOT FOUND"

# Create directories for AI file processing
RUN mkdir -p temp_uploads temp_audio

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Production command - Use PORT environment variable for Railway
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
