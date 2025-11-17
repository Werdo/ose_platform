"""
OSE Platform - Main Application
Punto de entrada de la aplicación FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database.mongodb import Database
from app.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    register_exception_handlers,
)
from app.routes import routers

# ════════════════════════════════════════════════════════════════════════
# LOGGING CONFIGURATION
# ════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════
# LIFESPAN EVENTS
# ════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager para startup y shutdown events

    Startup:
    - Conecta a MongoDB
    - Inicializa Beanie con los modelos
    - Crea índices y settings por defecto

    Shutdown:
    - Cierra conexión a MongoDB
    """
    # Startup
    logger.info("🚀 Starting OSE Platform API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Version: {settings.APP_VERSION}")

    try:
        # Connect to MongoDB
        logger.info("Connecting to MongoDB...")
        await Database.connect()
        logger.info("✓ MongoDB connected successfully")

        # Initialize default settings (TODO: implement init_default_settings method)
        # logger.info("Initializing system settings...")
        # from app.models.setting import SystemSetting
        # await SystemSetting.init_default_settings()
        # logger.info("✓ System settings initialized")

        logger.info("✓ Application startup complete")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}", exc_info=True)
        raise

    yield  # Application is running

    # Shutdown
    logger.info("Shutting down OSE Platform API...")
    try:
        await Database.close()
        logger.info("✓ MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)

    logger.info("✓ Shutdown complete")


# ════════════════════════════════════════════════════════════════════════
# APPLICATION INSTANCE
# ════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="OSE Platform API",
    description="""
    **OSE Platform** - Sistema de gestión, trazabilidad y post-venta para Oversun Energy

    ## Características

    - 🔐 **Autenticación JWT** - Sistema seguro de tokens con refresh
    - 📦 **Gestión de Dispositivos** - Trazabilidad completa de dispositivos IoT/GPS
    - 🏭 **Control de Producción** - Órdenes, lotes, líneas y estaciones
    - 🎫 **Tickets de Soporte** - Sistema completo de helpdesk
    - 🔄 **Gestión de RMA** - Reparaciones y reemplazos
    - 👥 **Gestión de Clientes** - CRM integrado
    - ⚙️ **Configuración Dinámica** - Settings en MongoDB con interfaz web
    - 📊 **Reportes y Métricas** - KPIs y estadísticas en tiempo real

    ## Autenticación

    La API usa autenticación JWT. Para obtener un token:

    1. POST `/auth/login` con email y password
    2. Usar el `access_token` en el header: `Authorization: Bearer <token>`
    3. Refrescar el token con `/auth/refresh` usando el `refresh_token`

    ## Rate Limiting

    - Requests generales: 600 por minuto por IP
    - Login: 5 por minuto
    - Password reset: 3 por minuto
    """,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan,
)


# ════════════════════════════════════════════════════════════════════════
# MIDDLEWARE
# ════════════════════════════════════════════════════════════════════════

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS.split(","),
    allow_headers=settings.CORS_ALLOW_HEADERS.split(","),
)

# Request Logging
app.add_middleware(RequestLoggingMiddleware)

# Rate Limiting
app.add_middleware(RateLimitMiddleware)

logger.info("✓ Middleware registered")


# ════════════════════════════════════════════════════════════════════════
# EXCEPTION HANDLERS
# ════════════════════════════════════════════════════════════════════════

register_exception_handlers(app)


# ════════════════════════════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════════════════════════════

# Register all routers
for router in routers:
    app.include_router(router, prefix="/api/v1")

logger.info(f"✓ Registered {len(routers)} routers")


# ════════════════════════════════════════════════════════════════════════
# ROOT ENDPOINT
# ════════════════════════════════════════════════════════════════════════

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API info
    """
    return {
        "name": "OSE Platform API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
        "docs": "/docs" if settings.ENVIRONMENT != "production" else "disabled",
        "health": "/api/v1/health",
    }


# ════════════════════════════════════════════════════════════════════════
# APPLICATION INFO
# ════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting development server...")
    logger.info(f"API will be available at: http://0.0.0.0:{settings.PORT}")
    logger.info(f"API Docs at: http://0.0.0.0:{settings.PORT}/docs")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
