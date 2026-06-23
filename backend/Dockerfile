# ─────────────────────────────────────────────
# Backend - FastAPI + Uvicorn (Python 3.12)
# ─────────────────────────────────────────────
FROM python:3.12-slim

# Prevent Python from writing .pyc files & enable real-time stdout/stderr logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install minimal system dependencies (curl is used for healthcheck)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first so this layer is cached unless deps change
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Create a non-root user and switch to it for better security
RUN groupadd --system appgroup \
    && useradd --system --no-create-home --gid appgroup appuser \
    && chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

# Healthcheck hits the FastAPI /api/project/health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8000/api/project/health || exit 1

# Run FastAPI via Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
