"""
OSE Platform - Main Application
FastAPI application principal
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db, close_db, check_database_health
from app.routers import auth, app1_notify, app2_import, app3_rma, app4_transform, public_auth, public_tickets
from app.routers import app5_invoice, app6_picking, system_logs, brand_update, employees

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events (startup/shutdown)
    """
    # Startup
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)

    try:
        # Conectar a MongoDB
        logger.info("Connecting to MongoDB...")
        await init_db()
        logger.info("✓ MongoDB connected successfully")

        # Verificar salud de la BD
        health = await check_database_health()
        logger.info(f"✓ Database: {health.get('database')}")
        logger.info(f"✓ Collections: {health.get('collections')}")

    except Exception as e:
        logger.error(f"✗ Error during startup: {e}")
        raise

    logger.info("=" * 60)
    logger.info(f"Server ready on {settings.HOST}:{settings.PORT}")
    logger.info(f"API Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    logger.info("✓ Database connections closed")


# Crear aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema de gestión integral para dispositivos IoT/GPS",
    lifespan=lifespan,
    redirect_slashes=False  # Deshabilitar redirects automáticos de slashes
)


# ════════════════════════════════════════════════════════════════════════
# MIDDLEWARE
# ════════════════════════════════════════════════════════════════════════

# CORS - Configuración para desarrollo
# NOTA: No se puede usar allow_origins=["*"] con allow_credentials=True
# Debe usar orígenes explícitos cuando credentials están habilitadas
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Orígenes explícitos (requerido con credentials)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los headers
    expose_headers=["*"],  # Exponer todos los headers en la respuesta
    max_age=3600,  # Cache preflight requests for 1 hour
)


# ════════════════════════════════════════════════════════════════════════
# ROUTERS
# ════════════════════════════════════════════════════════════════════════

# Autenticación
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)

# Employee Management (super_admin only)
app.include_router(employees.router, prefix=settings.API_V1_PREFIX)

# App 1: Notificación de Series
if settings.FEATURE_APP1_ENABLED:
    app.include_router(app1_notify.router, prefix=settings.API_V1_PREFIX)
    logger.info("✓ App 1 (Notificación de Series) enabled")

# App 2: Importación de Datos
if settings.FEATURE_APP2_ENABLED:
    app.include_router(app2_import.router, prefix="/api")
    logger.info("✓ App 2 (Importación de Datos) enabled")

# App 3: RMA & Tickets
if settings.FEATURE_APP3_ENABLED:
    app.include_router(app3_rma.router, prefix=settings.API_V1_PREFIX)
    logger.info("✓ App 3 (RMA & Tickets) enabled")

# App 4: Transform & Import
if settings.FEATURE_APP4_ENABLED:
    app.include_router(app4_transform.router, prefix=settings.API_V1_PREFIX)
    logger.info("✓ App 4 (Transform & Import) enabled")

# App 5: Sistema de Facturación de Tickets
if settings.FEATURE_APP5_ENABLED:
    app.include_router(app5_invoice.router_public)  # No API prefix for public routes
    app.include_router(app5_invoice.router_admin, prefix=settings.API_V1_PREFIX)
    logger.info("✓ App 5 (Facturación de Tickets) enabled")

# App 6: Sistema de Picking y Etiquetado
if settings.FEATURE_APP6_ENABLED:
    app.include_router(app6_picking.router, prefix=settings.API_V1_PREFIX)
    logger.info("✓ App 6 (Picking & Etiquetado) enabled")

# Portal Público - Autenticación y Tickets
app.include_router(public_auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(public_tickets.router, prefix=settings.API_V1_PREFIX)
logger.info("✓ Portal Público (RMA/Tickets) enabled")

# System Logs - Monitoreo y Auditoría
app.include_router(system_logs.router, prefix=settings.API_V1_PREFIX)
logger.info("✓ System Logs (Monitoreo) enabled")

# Brand Update - Actualización masiva de marcas
app.include_router(brand_update.router, prefix=settings.API_V1_PREFIX, tags=["Brand Update"])
logger.info("✓ Brand Update (Actualización de Marcas) enabled")


# ════════════════════════════════════════════════════════════════════════
# ENDPOINTS BÁSICOS
# ════════════════════════════════════════════════════════════════════════
# NOTA: CORSMiddleware maneja automáticamente las peticiones OPTIONS (preflight)
# No es necesario un handler manual

@app.get("/")
async def root():
    """
    Root endpoint - Información básica de la API
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": f"{settings.API_V1_PREFIX}/docs",
        "company": settings.COMPANY_NAME
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint - Verifica el estado del servidor y la BD
    """
    try:
        db_health = await check_database_health()

        return {
            "status": "healthy",
            "api": "online",
            "database": db_health.get("status"),
            "version": settings.APP_VERSION
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "api": "online",
                "database": "error",
                "error": str(e)
            }
        )


@app.get(f"{settings.API_V1_PREFIX}/info")
async def api_info():
    """
    API Information - Información detallada de la API
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "company": settings.COMPANY_NAME,
        "features": {
            "app1_notify": settings.FEATURE_APP1_ENABLED,
            "app2_import": settings.FEATURE_APP2_ENABLED,
            "app3_tickets": settings.FEATURE_APP3_ENABLED,
            "app4_rma": settings.FEATURE_APP4_ENABLED,
            "app5_production": settings.FEATURE_APP5_ENABLED,
            "app6_reports": settings.FEATURE_APP6_ENABLED,
        },
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/health"
        }
    }


# ════════════════════════════════════════════════════════════════════════
# ERROR HANDLERS
# ════════════════════════════════════════════════════════════════════════

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handler para 404 Not Found"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint no encontrado",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handler para 500 Internal Server Error"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Error interno del servidor",
            "message": "Por favor contacte al administrador"
        }
    )


# ════════════════════════════════════════════════════════════════════════
# PUNTO DE ENTRADA
# ════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # Solo en desarrollo
        log_level="info",
        timeout_keep_alive=300,  # 5 minutos para archivos grandes
        limit_concurrency=1000,
        limit_max_requests=10000
    )


