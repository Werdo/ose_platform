"""
OSE Platform - Health Routes
Endpoints para health checks y status del sistema
"""

from fastapi import APIRouter, status
from datetime import datetime

from app.schemas import HealthStatus
from app.database.mongodb import check_database_health
from app.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthStatus,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Verifica el estado del sistema y sus dependencias"
)
async def health_check():
    """
    Health check endpoint

    Retorna:
    - Status del sistema (healthy, degraded, unhealthy)
    - Versión de la API
    - Estado de la base de datos
    - Estado de servicios externos
    """
    # Check database
    try:
        db_health = await check_database_health()
        db_status = "healthy"
    except Exception as e:
        db_health = {"status": "unhealthy", "error": str(e)}
        db_status = "unhealthy"

    # Overall status
    overall_status = "healthy" if db_status == "healthy" else "unhealthy"

    return HealthStatus(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
        database=db_health,
        services={
            "email": {"status": "not_checked"}  # Se puede extender
        }
    )


@router.get(
    "/ping",
    status_code=status.HTTP_200_OK,
    summary="Ping",
    description="Endpoint simple para verificar que la API responde"
)
async def ping():
    """Simple ping endpoint"""
    return {"ping": "pong", "timestamp": datetime.utcnow()}
