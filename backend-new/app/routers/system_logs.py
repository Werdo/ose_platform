"""
OSE Platform - System Logs Router
API para consultar y gestionar logs del sistema
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from beanie.operators import In

from app.models.system_log import SystemLog, LogLevel, LogCategory
from app.models.employee import Employee
from app.dependencies.auth import get_current_active_user

router = APIRouter(prefix="/logs", tags=["System Logs"])


@router.get("", response_model=dict)
async def get_logs(
    level: Optional[LogLevel] = Query(None, description="Filtrar por nivel de log"),
    category: Optional[LogCategory] = Query(None, description="Filtrar por categoría"),
    user_email: Optional[str] = Query(None, description="Filtrar por usuario"),
    endpoint: Optional[str] = Query(None, description="Filtrar por endpoint"),
    search: Optional[str] = Query(None, description="Buscar en mensaje"),
    start_date: Optional[datetime] = Query(None, description="Fecha inicio (ISO format)"),
    end_date: Optional[datetime] = Query(None, description="Fecha fin (ISO format)"),
    limit: int = Query(100, ge=1, le=1000, description="Cantidad de logs a retornar"),
    skip: int = Query(0, ge=0, description="Logs a saltar (paginación)"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Obtener logs del sistema con filtros

    Requiere permisos de administrador o supervisor
    """
    # Verificar permisos
    if current_user.role not in ["super_admin", "admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver los logs del sistema"
        )

    # Construir query
    query = {}

    if level:
        query["level"] = level

    if category:
        query["category"] = category

    if user_email:
        query["user_email"] = {"$regex": user_email, "$options": "i"}

    if endpoint:
        query["endpoint"] = {"$regex": endpoint, "$options": "i"}

    if search:
        query["message"] = {"$regex": search, "$options": "i"}

    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = start_date
        if end_date:
            query["timestamp"]["$lte"] = end_date

    # Obtener logs
    logs = await SystemLog.find(query)\
        .sort([("timestamp", -1)])\
        .skip(skip)\
        .limit(limit)\
        .to_list()

    # Obtener total
    total = await SystemLog.find(query).count()

    return {
        "logs": logs,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


@router.get("/stats", response_model=dict)
async def get_log_stats(
    hours: int = Query(24, ge=1, le=168, description="Horas a analizar (max 7 días)"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Obtener estadísticas de logs

    Requiere permisos de administrador
    """
    # Verificar permisos
    if current_user.role not in ["super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estadísticas de logs"
        )

    # Fecha de inicio
    start_date = datetime.utcnow() - timedelta(hours=hours)

    # Total de logs
    total_logs = await SystemLog.find(
        SystemLog.timestamp >= start_date
    ).count()

    # Logs por nivel
    logs_by_level = {}
    for level in LogLevel:
        count = await SystemLog.find(
            SystemLog.timestamp >= start_date,
            SystemLog.level == level
        ).count()
        logs_by_level[level.value] = count

    # Logs por categoría
    logs_by_category = {}
    for category in LogCategory:
        count = await SystemLog.find(
            SystemLog.timestamp >= start_date,
            SystemLog.category == category
        ).count()
        if count > 0:
            logs_by_category[category.value] = count

    # Errores recientes
    recent_errors = await SystemLog.find(
        SystemLog.timestamp >= start_date,
        In(SystemLog.level, [LogLevel.ERROR, LogLevel.CRITICAL])
    ).sort([("timestamp", -1)]).limit(10).to_list()

    # Endpoints más llamados
    pipeline = [
        {"$match": {
            "timestamp": {"$gte": start_date},
            "endpoint": {"$ne": None}
        }},
        {"$group": {
            "_id": "$endpoint",
            "count": {"$sum": 1},
            "avg_duration": {"$avg": "$duration_ms"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_endpoints = await SystemLog.aggregate(pipeline).to_list()

    return {
        "period_hours": hours,
        "start_date": start_date,
        "total_logs": total_logs,
        "logs_by_level": logs_by_level,
        "logs_by_category": logs_by_category,
        "recent_errors": recent_errors,
        "top_endpoints": top_endpoints
    }


@router.get("/{log_id}", response_model=SystemLog)
async def get_log_detail(
    log_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener detalles de un log específico"""
    # Verificar permisos
    if current_user.role not in ["super_admin", "admin", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver logs"
        )

    # Validar ObjectId
    if not ObjectId.is_valid(log_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID de log inválido"
        )

    # Buscar log
    log = await SystemLog.get(ObjectId(log_id))

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log no encontrado"
        )

    return log


@router.delete("/cleanup")
async def cleanup_old_logs(
    days: int = Query(30, ge=7, le=365, description="Eliminar logs más antiguos que X días"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Limpiar logs antiguos

    Solo administradores pueden ejecutar esta acción
    """
    # Verificar permisos (solo super_admin)
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo super administradores pueden limpiar logs"
        )

    # Fecha límite
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Contar logs a eliminar
    count = await SystemLog.find(
        SystemLog.timestamp < cutoff_date
    ).count()

    # Eliminar logs
    result = await SystemLog.find(
        SystemLog.timestamp < cutoff_date
    ).delete()

    return {
        "success": True,
        "deleted_count": count,
        "cutoff_date": cutoff_date,
        "message": f"Se eliminaron {count} logs anteriores a {cutoff_date}"
    }


@router.get("/export/csv")
async def export_logs_csv(
    level: Optional[LogLevel] = Query(None),
    category: Optional[LogCategory] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: int = Query(1000, le=10000),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Exportar logs a CSV

    Requiere permisos de administrador
    """
    from fastapi.responses import StreamingResponse
    import io
    import csv

    # Verificar permisos
    if current_user.role not in ["super_admin", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para exportar logs"
        )

    # Construir query
    query = {}
    if level:
        query["level"] = level
    if category:
        query["category"] = category
    if start_date or end_date:
        query["timestamp"] = {}
        if start_date:
            query["timestamp"]["$gte"] = start_date
        if end_date:
            query["timestamp"]["$lte"] = end_date

    # Obtener logs
    logs = await SystemLog.find(query)\
        .sort([("timestamp", -1)])\
        .limit(limit)\
        .to_list()

    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow([
        "Timestamp", "Level", "Category", "Message",
        "User", "Endpoint", "Method", "Duration (ms)",
        "Error Type", "Error Message"
    ])

    # Datos
    for log in logs:
        writer.writerow([
            log.timestamp.isoformat(),
            log.level.value,
            log.category.value,
            log.message,
            log.user_email or "",
            log.endpoint or "",
            log.method or "",
            log.duration_ms or "",
            log.error_type or "",
            log.error_message or ""
        ])

    # Retornar como archivo
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=system_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )
