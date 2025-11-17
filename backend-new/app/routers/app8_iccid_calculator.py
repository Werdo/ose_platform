"""
OSE Platform - App 8: ICCID Calculator Router
Router para calculadora de ICCID con historial y análisis completo
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from io import StringIO
import csv

from app.models.employee import Employee
from app.models.iccid_batch import ICCIDBatch
from app.dependencies.auth import get_current_active_user
from app.utils.iccid_analyzer import analyze_iccid, get_available_iin_profiles
from app.utils.iccid_utils import generate_iccid_with_checksum


router = APIRouter(
    prefix="/app8/iccid-calculator",
    tags=["App 8 - ICCID Calculator"]
)


# ═══════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class GenerateICCIDBatchRequest(BaseModel):
    """Request para generar un lote de ICCIDs"""
    batch_name: str = Field(..., description="Nombre del lote")
    description: Optional[str] = Field(None, description="Descripción")
    base_iccid: str = Field(..., description="ICCID base (sin checksum)")
    start_number: int = Field(..., description="Número inicial", ge=0)
    end_number: int = Field(..., description="Número final", ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "batch_name": "Lote IoT Enero 2025",
                "description": "ICCIDs para dispositivos IoT",
                "base_iccid": "89882260",
                "start_number": 1000000,
                "end_number": 1001000
            }
        }


class AnalyzeICCIDRequest(BaseModel):
    """Request para analizar un ICCID individual"""
    iccid: str = Field(..., description="ICCID a analizar")


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS - GENERACIÓN Y ANÁLISIS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/batches/generate")
async def generate_iccid_batch(
    request: GenerateICCIDBatchRequest,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Genera un lote de ICCIDs con análisis completo.

    - Genera ICCIDs secuenciales con checksum Luhn
    - Analiza cada ICCID (país, operador, validación)
    - Almacena en BD para historial
    - Calcula estadísticas del lote
    """

    # Validar rangos
    if request.end_number < request.start_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El número final debe ser mayor o igual al inicial"
        )

    total_count = request.end_number - request.start_number + 1

    if total_count > 100000:  # Límite de 100k ICCIDs por lote
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Máximo 100,000 ICCIDs por lote"
        )

    # Generar ICCIDs con análisis
    iccids_list = []
    analyses_list = []

    # Contadores para estadísticas
    operators_count: Dict[str, int] = {}
    countries_count: Dict[str, int] = {}
    valid_count = 0
    invalid_count = 0

    for i in range(request.start_number, request.end_number + 1):
        # Generar ICCID con checksum
        iccid = generate_iccid_with_checksum(request.base_iccid, i)
        iccids_list.append(iccid)

        # Analizar ICCID
        analysis = analyze_iccid(iccid)
        analyses_list.append(analysis)

        # Actualizar estadísticas
        if analysis.get("luhn_valid"):
            valid_count += 1
        else:
            invalid_count += 1

        # Contar operadores
        iin_profile = analysis.get("iin_profile")
        if iin_profile:
            operator = iin_profile.get("operator", "Desconocido")
            operators_count[operator] = operators_count.get(operator, 0) + 1

        # Contar países
        country = analysis.get("country_name_guess") or "Desconocido"
        countries_count[country] = countries_count.get(country, 0) + 1

    # Preparar estadísticas
    stats = {
        "total_count": total_count,
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "operators": operators_count,
        "countries": countries_count,
    }

    # Crear lote en BD
    batch = ICCIDBatch(
        batch_name=request.batch_name,
        description=request.description,
        base_iccid=request.base_iccid,
        start_number=request.start_number,
        end_number=request.end_number,
        total_count=total_count,
        iccids=iccids_list,
        analyses=analyses_list,
        stats=stats,
        created_by=current_user.employee_id
    )

    await batch.insert()

    return {
        "success": True,
        "message": f"Lote generado correctamente: {total_count} ICCIDs",
        "batch_id": str(batch.id),
        "batch_name": batch.batch_name,
        "total_count": total_count,
        "stats": stats
    }


@router.post("/analyze")
async def analyze_single_iccid(
    request: AnalyzeICCIDRequest,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Analiza un ICCID individual y devuelve toda la información.

    - Validación Luhn
    - Identificación de operador
    - País y región
    - Advertencias
    """
    analysis = analyze_iccid(request.iccid)

    return {
        "success": True,
        "analysis": analysis
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS - HISTORIAL Y GESTIÓN
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/batches")
async def list_iccid_batches(
    skip: int = 0,
    limit: int = 50,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Lista todos los lotes de ICCID generados.

    - Ordenados por fecha de creación (más recientes primero)
    - Paginación
    - Incluye estadísticas básicas
    """
    batches = await ICCIDBatch.find_all()\
        .sort(-ICCIDBatch.created_at)\
        .skip(skip)\
        .limit(limit)\
        .to_list()

    total = await ICCIDBatch.count()

    return {
        "success": True,
        "total": total,
        "skip": skip,
        "limit": limit,
        "batches": [
            {
                "_id": str(batch.id),
                "batch_name": batch.batch_name,
                "description": batch.description,
                "base_iccid": batch.base_iccid,
                "total_count": batch.total_count,
                "stats": batch.stats,
                "created_by": batch.created_by,
                "created_at": batch.created_at,
                "csv_download_count": batch.csv_download_count
            }
            for batch in batches
        ]
    }


@router.get("/batches/{batch_id}")
async def get_iccid_batch_details(
    batch_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Obtiene los detalles completos de un lote específico.

    - Lista completa de ICCIDs
    - Análisis de cada ICCID
    - Estadísticas detalladas
    """
    batch = await ICCIDBatch.get(batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote no encontrado"
        )

    return {
        "success": True,
        "batch": {
            "_id": str(batch.id),
            "batch_name": batch.batch_name,
            "description": batch.description,
            "base_iccid": batch.base_iccid,
            "start_number": batch.start_number,
            "end_number": batch.end_number,
            "total_count": batch.total_count,
            "iccids": batch.iccids,
            "analyses": batch.analyses,
            "stats": batch.stats,
            "created_by": batch.created_by,
            "created_at": batch.created_at,
            "csv_download_count": batch.csv_download_count
        }
    }


@router.get("/batches/{batch_id}/csv")
async def download_iccid_batch_csv(
    batch_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Descarga un lote de ICCIDs como CSV.

    - Incluye ICCID y análisis completo
    - Columnas: ICCID, Operador, País, Región, Válido, etc.
    - Incrementa contador de descargas
    """
    batch = await ICCIDBatch.get(batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote no encontrado"
        )

    # Crear CSV en memoria
    output = StringIO()
    writer = csv.writer(output)

    # Headers
    writer.writerow([
        "ICCID",
        "Válido",
        "Operador",
        "Marca",
        "País",
        "Región",
        "Caso de Uso",
        "Red",
        "IIN Prefix",
        "Account Number",
        "Checksum",
        "Advertencias"
    ])

    # Datos
    for analysis in batch.analyses:
        iin_profile = analysis.get("iin_profile") or {}

        writer.writerow([
            analysis.get("iccid", ""),
            "Sí" if analysis.get("luhn_valid") else "No",
            iin_profile.get("operator", "Desconocido"),
            iin_profile.get("brand", ""),
            analysis.get("country_name_guess", ""),
            iin_profile.get("region", ""),
            iin_profile.get("use_case", ""),
            iin_profile.get("core_network", ""),
            analysis.get("iin_prefix", ""),
            analysis.get("account_number", ""),
            analysis.get("checksum", ""),
            "; ".join(analysis.get("warnings", []))
        ])

    # Actualizar estadísticas de descarga
    batch.csv_download_count += 1
    batch.csv_generated = True
    batch.csv_generated_at = datetime.utcnow()
    await batch.save()

    # Preparar respuesta
    output.seek(0)
    filename = f"iccids_{batch.batch_name.replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.delete("/batches/{batch_id}")
async def delete_iccid_batch(
    batch_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Elimina un lote de ICCID.

    Requiere permisos de administrador.
    """
    # Solo super_admin puede eliminar
    if current_user.role.value != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo super_admin puede eliminar lotes"
        )

    batch = await ICCIDBatch.get(batch_id)

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lote no encontrado"
        )

    await batch.delete()

    return {
        "success": True,
        "message": f"Lote '{batch.batch_name}' eliminado correctamente"
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS - UTILIDADES
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/iin-profiles")
async def get_iin_profiles(
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Obtiene la lista de perfiles IIN disponibles en la tabla.

    Útil para mostrar operadores soportados en el frontend.
    """
    profiles = get_available_iin_profiles()

    return {
        "success": True,
        "total": len(profiles),
        "profiles": profiles
    }


@router.get("/stats/global")
async def get_global_stats(
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Obtiene estadísticas globales de todos los lotes.

    - Total de lotes generados
    - Total de ICCIDs generados
    - Operadores más usados
    - Países más frecuentes
    """
    all_batches = await ICCIDBatch.find_all().to_list()

    total_batches = len(all_batches)
    total_iccids = sum(batch.total_count for batch in all_batches)

    # Agregar operadores y países
    all_operators: Dict[str, int] = {}
    all_countries: Dict[str, int] = {}

    for batch in all_batches:
        stats = batch.stats or {}

        # Operadores
        for op, count in stats.get("operators", {}).items():
            all_operators[op] = all_operators.get(op, 0) + count

        # Países
        for country, count in stats.get("countries", {}).items():
            all_countries[country] = all_countries.get(country, 0) + count

    # Top 10 operadores
    top_operators = sorted(
        all_operators.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    # Top 10 países
    top_countries = sorted(
        all_countries.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    return {
        "success": True,
        "stats": {
            "total_batches": total_batches,
            "total_iccids": total_iccids,
            "top_operators": [
                {"operator": op, "count": count}
                for op, count in top_operators
            ],
            "top_countries": [
                {"country": country, "count": count}
                for country, count in top_countries
            ]
        }
    }
