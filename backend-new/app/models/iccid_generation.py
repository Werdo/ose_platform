"""
OSE Platform - ICCID Generation Batch Model
Modelo para registro de generaciones de ICCIDs
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class BatchInfo(Dict[str, Any]):
    """Estructura de información de un lote"""
    pass


class ICCIDGenerationBatch(Document):
    """
    Registro de generación de ICCIDs
    Guarda el historial de todos los lotes de ICCIDs generados
    """

    # ════════════════════════════════════════════════════════════════════
    # INFORMACIÓN BÁSICA
    # ════════════════════════════════════════════════════════════════════

    name: str = Field(
        ...,
        description="Nombre descriptivo de la generación"
    )

    total_iccids: int = Field(
        ...,
        description="Cantidad total de ICCIDs generados"
    )

    total_batches: int = Field(
        ...,
        description="Cantidad de lotes procesados"
    )

    # ════════════════════════════════════════════════════════════════════
    # DETALLES DE LOS LOTES
    # ════════════════════════════════════════════════════════════════════

    batches: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Información de cada lote generado"
    )
    # Estructura de cada lote:
    # {
    #     "name": str,
    #     "iccid_start": str,
    #     "iccid_end": str,
    #     "count": int
    # }

    # ════════════════════════════════════════════════════════════════════
    # ARCHIVO CSV
    # ════════════════════════════════════════════════════════════════════

    csv_filename: Optional[str] = Field(
        default=None,
        description="Nombre del archivo CSV generado"
    )

    csv_size_bytes: Optional[int] = Field(
        default=None,
        description="Tamaño del CSV en bytes"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATOS
    # ════════════════════════════════════════════════════════════════════

    generated_by: Optional[str] = Field(
        default=None,
        description="ID del empleado que generó los ICCIDs",
        index=True
    )

    generated_by_name: Optional[str] = Field(
        default=None,
        description="Nombre del empleado (denormalizado)"
    )

    generated_by_email: Optional[str] = Field(
        default=None,
        description="Email del empleado"
    )

    ip_address: Optional[str] = Field(
        default=None,
        description="Dirección IP desde donde se generó"
    )

    notes: Optional[str] = Field(
        default=None,
        description="Notas adicionales sobre la generación"
    )

    # ════════════════════════════════════════════════════════════════════
    # AUDITORÍA
    # ════════════════════════════════════════════════════════════════════

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de generación",
        index=True
    )

    processing_time_seconds: Optional[float] = Field(
        default=None,
        description="Tiempo de procesamiento en segundos"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "iccid_generations"
        indexes = [
            "generated_by",
            "created_at",
            [("created_at", -1)],
            [("generated_by", 1), ("created_at", -1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def get_recent_generations(limit: int = 20):
        """Obtiene las generaciones más recientes"""
        return await ICCIDGenerationBatch.find_all().sort("-created_at").limit(limit).to_list()

    @staticmethod
    async def get_generations_by_user(employee_id: str, limit: int = 20):
        """Obtiene las generaciones de un empleado específico"""
        return await ICCIDGenerationBatch.find(
            ICCIDGenerationBatch.generated_by == employee_id
        ).sort("-created_at").limit(limit).to_list()

    @staticmethod
    async def get_total_iccids_generated():
        """Obtiene el total de ICCIDs generados"""
        result = await ICCIDGenerationBatch.aggregate([
            {"$group": {
                "_id": None,
                "total": {"$sum": "$total_iccids"}
            }}
        ]).to_list()

        return result[0]["total"] if result else 0
