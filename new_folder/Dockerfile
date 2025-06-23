   # TradeMasterX 2.0 Production Dockerfile
# Multi-stage build for optimized production image

# ============================================================================
# BUILD STAGE - Development dependencies and compilation
# ============================================================================
FROM python:3.11-slim as builder

# Set build arguments
ARG BUILD_DATE
ARG VERSION=2.0.0
ARG VCS_REF

# Add labels for image metadata
LABEL maintainer="TradeMasterX Team <dev@trademasterx.com>" \
      version="${VERSION}" \
      description="Advanced AI-Powered Trading System" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}"

# Set environment variables for build
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ============================================================================
# PRODUCTION STAGE - Minimal runtime image
# ============================================================================
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000

# Create non-root user for security
RUN groupadd -r trademasterx && \
    useradd -r -g trademasterx -s /bin/bash trademasterx

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create application directory structure
WORKDIR /app

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/config /app/backups && \
    chown -R trademasterx:trademasterx /app

# Copy application code
COPY --chown=trademasterx:trademasterx trademasterx/ ./trademasterx/
COPY --chown=trademasterx:trademasterx config/ ./config/
COPY --chown=trademasterx:trademasterx setup.py ./
COPY --chown=trademasterx:trademasterx README.md ./
COPY --chown=trademasterx:trademasterx .env.example ./.env

# Install the application
RUN pip install -e .

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Initialize configuration if not exists\n\
if [ ! -f "/app/config/system.yaml" ]; then\n\
    echo "Initializing configuration..."\n\
    tmx config init\n\
fi\n\
\n\
# Create data directories\n\
mkdir -p /app/data /app/logs\n\
\n\
# Run database migrations if needed\n\
tmx validate system\n\
\n\
# Start the application based on command\n\
case "$1" in\n\
    "web")\n\
        echo "Starting TradeMasterX Web Interface..."\n\
        exec tmx-web --host $FLASK_HOST --port $FLASK_PORT\n\
        ;;\n\
    "master")\n\
        echo "Starting TradeMasterX Master Bot..."\n\
        exec tmx-master start\n\
        ;;\n\
    "all")\n\
        echo "Starting TradeMasterX Complete System..."\n\
        exec tmx start --all\n\
        ;;\n\
    *)\n\
        echo "Usage: $0 {web|master|all}"\n\
        echo "  web    - Start web interface only"\n\
        echo "  master - Start master bot only"\n\
        echo "  all    - Start complete system"\n\
        exit 1\n\
        ;;\n\
esac\n\
' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Switch to non-root user
USER trademasterx

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${FLASK_PORT}/api/status || exit 1

# Expose ports
EXPOSE 5000

# Volume for persistent data
VOLUME ["/app/data", "/app/logs", "/app/backups"]

# Use tini as init system
ENTRYPOINT ["/usr/bin/tini", "--"]

# Default command
CMD ["/app/entrypoint.sh", "all"]

# ============================================================================
# DEVELOPMENT VARIANT
# ============================================================================
FROM production as development

# Switch back to root for development packages
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    htop \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install \
    pytest>=6.0.0 \
    pytest-cov>=2.12.0 \
    black>=21.0.0 \
    flake8>=4.0.0 \
    mypy>=0.910 \
    ipython>=8.0.0 \
    jupyter>=1.0.0

# Development environment variables
ENV ENVIRONMENT=development \
    DEBUG=true \
    FLASK_DEBUG=true

# Switch back to application user
USER trademasterx

# Development command
CMD ["/app/entrypoint.sh", "web"]
