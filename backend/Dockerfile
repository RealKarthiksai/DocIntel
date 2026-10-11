FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for build tools and curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for rapid and reliable Python package management
RUN pip install --no-cache-dir uv

# Copy requirements
COPY requirements.txt .

# Install dependencies using CPU torch to keep image slim and fast
RUN uv pip install --no-cache --system -r requirements.txt

# Copy application source
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI server
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
