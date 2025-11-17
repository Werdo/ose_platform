# ════════════════════════════════════════════════════════════════════════════
# OSE PLATFORM - Backend Dockerfile
# ════════════════════════════════════════════════════════════════════════════
#
# Multi-stage build para optimizar el tamaño de la imagen
#
# ════════════════════════════════════════════════════════════════════════════

# ──────────────────────────────────────────────────────────────────────────
# STAGE 1: Base
# ──────────────────────────────────────────────────────────────────────────
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim as base

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Metadatos
LABEL maintainer="Oversun Energy <dev@oversun.com>" \
      description="OSE Platform Backend API" \
      version="1.0.0"

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 oseuser && \
    mkdir -p /app /var/log/ose /tmp/ose_uploads && \
    chown -R oseuser:oseuser /app /var/log/ose /tmp/ose_uploads

# ──────────────────────────────────────────────────────────────────────────
# STAGE 2: Dependencies
# ──────────────────────────────────────────────────────────────────────────
FROM base as dependencies

WORKDIR /app

# Copiar solo requirements para aprovechar cache de Docker
COPY --chown=oseuser:oseuser requirements.txt .

# Instalar dependencias de Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# ──────────────────────────────────────────────────────────────────────────
# STAGE 3: Production
# ──────────────────────────────────────────────────────────────────────────
FROM dependencies as production

WORKDIR /app

# Copiar el código de la aplicación
COPY --chown=oseuser:oseuser ./app ./app
COPY --chown=oseuser:oseuser ./scripts ./scripts

# Cambiar a usuario no-root
USER oseuser

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Comando por defecto (puede ser sobrescrito en docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ──────────────────────────────────────────────────────────────────────────
# STAGE 4: Development (opcional)
# ──────────────────────────────────────────────────────────────────────────
FROM dependencies as development

WORKDIR /app

# Instalar dependencias de desarrollo
RUN pip install \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    flake8 \
    mypy \
    ipython

# Copiar código
COPY --chown=oseuser:oseuser . .

USER oseuser

EXPOSE 8000

# Hot reload para desarrollo
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
