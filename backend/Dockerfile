# ==============================================================================
# Multi-Stage Production Dockerfile for AstroMind AI Backend
# Pinned Base Image: Python 3.11 Slim Bookworm
# Enforces Least Privilege: Non-Root 'appuser' (UID 10001)
# ==============================================================================

# --- Stage 1: Build & Dependencies ---
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for ultra-fast, deterministic dependency resolution
COPY --from=ghcr.io/astral-sh/uv:0.5.21 /uv /bin/uv

# Copy project manifests
COPY backend/pyproject.toml ./backend/
COPY backend/app ./backend/app

# Install dependencies into virtualenv
RUN uv venv /opt/venv && \
    uv pip install --python /opt/venv/bin/python --no-cache -e "./backend"

# --- Stage 2: Minimal Runtime Image ---
FROM python:3.11-slim-bookworm AS runner

# Security: Set safe environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    APP_ENV=staging \
    PORT=8000

WORKDIR /app

# Install runtime library dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged system user and group
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /sbin/nologin -M appuser

# Copy virtualenv and application code from builder
COPY --from=builder --chown=appuser:appgroup /opt/venv /opt/venv
COPY --chown=appuser:appgroup backend /app/backend
COPY --chown=appuser:appgroup scripts /app/scripts

# Create storage directory with appropriate permissions
RUN mkdir -p /app/backend/storage/reports /app/backend/backups && \
    chown -R appuser:appgroup /app/backend/storage /app/backend/backups

USER 10001:10001

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://127.0.0.1:8000/health/live || exit 1

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers"]
