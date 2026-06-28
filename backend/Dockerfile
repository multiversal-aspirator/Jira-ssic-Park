# ─────────────────────────────────────────────
# Backend - FastAPI + Uvicorn (Python 3.12)
# ─────────────────────────────────────────────
FROM python:3.12-slim

# Prevent Python from writing .pyc files & enable real-time stdout/stderr logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HOME=/tmp \
    XDG_CACHE_HOME=/tmp/.cache

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl gcc g++ make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create non-root user for security
RUN groupadd --system appgroup \
    && useradd --system --no-create-home --gid appgroup appuser \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

# Healthcheck for FastAPI
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl --fail http://localhost:8000/api/project/health || exit 1

# Run FastAPI via Uvicorn (single worker for now to avoid env var issues in multiprocessing)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
