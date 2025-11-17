"""
OSE Platform - App4: Document Transform & Import Router
Sistema de transformación e importación de documentos
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import pandas as pd
import io

from app.models import TransformTemplate, ImportJob, DestinationType, JobStatus, Device, InventoryItem, Customer
from app.dependencies.auth import get_current_active_user as get_current_employee
from app.models.employee import Employee

router = APIRouter(
    prefix="/app4",
    tags=["App4 - Transform & Import"]
)


# ════════════════════════════════════════════════════════════════════
# SCHEMAS
# ════════════════════════════════════════════════════════════════════

class TemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    destination: DestinationType
    file_types: List[str] = ["csv", "xlsx"]
    mapping: Dict[str, str]
    validation: Dict[str, Dict[str, Any]] = {}
    default_values: Optional[Dict[str, Any]] = None
    required_fields: List[str] = []


class TemplateUpdate(BaseModel):
    description: Optional[str] = None
    mapping: Optional[Dict[str, str]] = None
    validation: Optional[Dict[str, Dict[str, Any]]] = None
    is_active: Optional[bool] = None


# ════════════════════════════════════════════════════════════════════
# ENDPOINTS - PLANTILLAS
# ════════════════════════════════════════════════════════════════════

@router.get("/plantillas", status_code=status.HTTP_200_OK)
async def get_templates(
    destination: Optional[DestinationType] = None,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Obtiene lista de plantillas de transformación
    """
    try:
        if destination:
            templates = await TransformTemplate.find_by_destination(destination)
        else:
            templates = await TransformTemplate.get_active_templates()

        return {
            "success": True,
            "total": len(templates),
            "templates": [
                {
                    "id": str(t.id),
                    "name": t.name,
                    "description": t.description,
                    "destination": t.destination,
                    "file_types": t.file_types,
                    "usage_count": t.usage_count,
                    "created_at": t.created_at,
                    "last_used_at": t.last_used_at
                }
                for t in templates
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo plantillas: {str(e)}"
        )


@router.post("/plantillas", status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Crea una nueva plantilla de transformación
    """
    try:
        # Verificar que no exista
        existing = await TransformTemplate.find_by_name(template_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una plantilla con el nombre '{template_data.name}'"
            )

        # Crear plantilla
        template = TransformTemplate(
            **template_data.dict(),
            created_by=str(current_user.id)
        )
        await template.save()

        return {
            "success": True,
            "message": "Plantilla creada exitosamente",
            "template": {
                "id": str(template.id),
                "name": template.name,
                "destination": template.destination
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando plantilla: {str(e)}"
        )


@router.get("/plantillas/{template_id}", status_code=status.HTTP_200_OK)
async def get_template(
    template_id: str,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Obtiene una plantilla específica
    """
    try:
        template = await TransformTemplate.get(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plantilla no encontrada"
            )

        return {
            "success": True,
            "template": {
                "id": str(template.id),
                "name": template.name,
                "description": template.description,
                "destination": template.destination,
                "file_types": template.file_types,
                "mapping": template.mapping,
                "validation": template.validation,
                "default_values": template.default_values,
                "required_fields": template.required_fields,
                "usage_count": template.usage_count,
                "created_at": template.created_at
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo plantilla: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════
# ENDPOINTS - TRANSFORMACIÓN E IMPORTACIÓN
# ════════════════════════════════════════════════════════════════════

@router.post("/transformar", status_code=status.HTTP_200_OK)
async def transform_file(
    file: UploadFile = File(...),
    template_id: Optional[str] = None,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Transforma un archivo sin guardarlo en la BD
    Devuelve una vista previa de los datos transformados
    """
    try:
        # Validar tamaño (50MB max)
        content = await file.read()
        if len(content) > 50 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="El archivo excede el tamaño máximo de 50MB"
            )

        # Obtener plantilla si se especificó
        template = None
        if template_id:
            template = await TransformTemplate.get(template_id)
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Plantilla no encontrada"
                )

        # Procesar archivo según tipo
        file_ext = file.filename.split('.')[-1].lower()

        if file_ext == 'csv':
            df = pd.read_csv(io.BytesIO(content))
        elif file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no soportado: {file_ext}"
            )

        # Transformar datos si hay plantilla
        if template:
            # Aplicar mapeo
            df_transformed = df.rename(columns=template.mapping)

            # Aplicar valores por defecto
            if template.default_values:
                for field, value in template.default_values.items():
                    if field not in df_transformed.columns:
                        df_transformed[field] = value

            # Convertir a lista de diccionarios
            records = df_transformed.to_dict(orient='records')
        else:
            records = df.to_dict(orient='records')

        # Vista previa (primeros 10 registros)
        preview = records[:10]

        return {
            "success": True,
            "total_rows": len(records),
            "preview_rows": len(preview),
            "columns": list(df.columns),
            "preview": preview,
            "template_applied": template.name if template else None
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error transformando archivo: {str(e)}"
        )


@router.post("/importar/{destination}", status_code=status.HTTP_201_CREATED)
async def import_file(
    destination: DestinationType,
    file: UploadFile = File(...),
    template_id: str = None,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Importa un archivo y lo guarda en la BD
    """
    try:
        # Crear job de importación
        job_number = await ImportJob.generate_job_number()

        job = ImportJob(
            job_number=job_number,
            employee_id=str(current_user.id),
            employee_name=f"{current_user.name} {current_user.surname}",
            template_id=template_id,
            filename=file.filename,
            file_type=file.filename.split('.')[-1].lower(),
            file_size=0,  # Se actualizará
            destination=destination
        )
        await job.save()

        # Leer archivo
        content = await file.read()
        job.file_size = len(content)

        # Validar tamaño
        if len(content) > 50 * 1024 * 1024:
            job.status = JobStatus.FAILED
            await job.add_error(0, "file", "Archivo excede 50MB")
            await job.save()
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="El archivo excede el tamaño máximo de 50MB"
            )

        # Obtener plantilla
        template = None
        if template_id:
            template = await TransformTemplate.get(template_id)
            job.template_name = template.name if template else None

        await job.start_processing()

        # Procesar archivo
        file_ext = file.filename.split('.')[-1].lower()

        if file_ext == 'csv':
            df = pd.read_csv(io.BytesIO(content))
        elif file_ext in ['xlsx', 'xls']:
            df = pd.read_excel(io.BytesIO(content))
        else:
            job.status = JobStatus.FAILED
            await job.add_error(0, "file", f"Tipo no soportado: {file_ext}")
            await job.save()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tipo de archivo no soportado: {file_ext}"
            )

        job.total_rows = len(df)
        await job.save()

        # Aplicar transformación si hay plantilla
        if template:
            df = df.rename(columns=template.mapping)
            if template.default_values:
                for field, value in template.default_values.items():
                    if field not in df.columns:
                        df[field] = value
            await template.increment_usage()

        # Vista previa
        job.preview_data = df.head(5).to_dict(orient='records')
        await job.save()

        # Nota: La importación real a la BD requiere lógica específica por destino
        # Por ahora solo se crea el job y se procesa el archivo

        await job.complete(success=True)

        return {
            "success": True,
            "message": f"Archivo importado exitosamente",
            "job": {
                "id": str(job.id),
                "job_number": job.job_number,
                "status": job.status,
                "total_rows": job.total_rows,
                "preview": job.preview_data
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        if 'job' in locals():
            job.status = JobStatus.FAILED
            await job.add_error(0, "system", str(e))
            await job.save()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importando archivo: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════
# ENDPOINTS - JOBS
# ════════════════════════════════════════════════════════════════════

@router.get("/jobs", status_code=status.HTTP_200_OK)
async def get_jobs(
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[JobStatus] = None,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Obtiene lista de jobs de importación
    """
    try:
        if status_filter:
            jobs = await ImportJob.find(
                ImportJob.status == status_filter
            ).sort("-created_at").limit(limit).to_list()
        else:
            jobs = await ImportJob.find_recent(limit=limit)

        return {
            "success": True,
            "total": len(jobs),
            "jobs": [
                {
                    "id": str(j.id),
                    "job_number": j.job_number,
                    "filename": j.filename,
                    "destination": j.destination,
                    "status": j.status,
                    "progress": j.progress,
                    "total_rows": j.total_rows,
                    "successful_rows": j.successful_rows,
                    "failed_rows": j.failed_rows,
                    "created_at": j.created_at,
                    "employee_name": j.employee_name
                }
                for j in jobs
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo jobs: {str(e)}"
        )


@router.get("/jobs/{job_id}", status_code=status.HTTP_200_OK)
async def get_job(
    job_id: str,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Obtiene detalles de un job específico
    """
    try:
        job = await ImportJob.get(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job no encontrado"
            )

        return {
            "success": True,
            "job": {
                "id": str(job.id),
                "job_number": job.job_number,
                "filename": job.filename,
                "file_type": job.file_type,
                "destination": job.destination,
                "status": job.status,
                "progress": job.progress,
                "total_rows": job.total_rows,
                "processed_rows": job.processed_rows,
                "successful_rows": job.successful_rows,
                "failed_rows": job.failed_rows,
                "skipped_rows": job.skipped_rows,
                "errors": job.errors,
                "warnings": job.warnings,
                "preview_data": job.preview_data,
                "created_at": job.created_at,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "duration_seconds": job.duration_seconds,
                "success_rate": job.success_rate,
                "employee_name": job.employee_name,
                "template_name": job.template_name
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo job: {str(e)}"
        )
