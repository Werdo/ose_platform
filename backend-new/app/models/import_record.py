"""
OSE Platform - Import Record Model
Modelo para registro de importaciones masivas de dispositivos
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ImportStatus(str, Enum):
    """Estados del proceso de importación"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"


class ImportError(Dict[str, Any]):
    """Estructura de un error de importación"""
    pass


class ImportRecord(Document):
    """
    Registro de importación de dispositivos
    Guarda el historial de todas las importaciones realizadas
    """

    # ════════════════════════════════════════════════════════════════════
    # INFORMACIÓN BÁSICA
    # ════════════════════════════════════════════════════════════════════

    filename: str = Field(
        ...,
        description="Nombre del archivo importado"
    )

    file_type: str = Field(
        ...,
        description="Tipo de archivo (xlsx, xls, csv)"
    )

    file_size: int = Field(
        ...,
        description="Tamaño del archivo en bytes"
    )

    # ════════════════════════════════════════════════════════════════════
    # RESULTADOS DE LA IMPORTACIÓN
    # ════════════════════════════════════════════════════════════════════

    status: ImportStatus = Field(
        default=ImportStatus.PROCESSING,
        description="Estado de la importación",
        index=True
    )

    total_rows: int = Field(
        default=0,
        description="Total de filas en el archivo"
    )

    success_count: int = Field(
        default=0,
        description="Cantidad de registros importados exitosamente"
    )

    error_count: int = Field(
        default=0,
        description="Cantidad de registros con errores"
    )

    duplicate_count: int = Field(
        default=0,
        description="Cantidad de registros duplicados"
    )

    # ════════════════════════════════════════════════════════════════════
    # ERRORES
    # ════════════════════════════════════════════════════════════════════

    errors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de errores encontrados"
    )

    warnings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de advertencias"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATOS
    # ════════════════════════════════════════════════════════════════════

    processing_time_seconds: Optional[float] = Field(
        default=None,
        description="Tiempo de procesamiento en segundos"
    )

    imported_by: Optional[str] = Field(
        default=None,
        description="ID del empleado que realizó la importación",
        index=True
    )

    imported_by_name: Optional[str] = Field(
        default=None,
        description="Nombre del empleado (denormalizado)"
    )

    ip_address: Optional[str] = Field(
        default=None,
        description="Dirección IP desde donde se realizó la importación"
    )

    notes: Optional[str] = Field(
        default=None,
        description="Notas adicionales sobre la importación"
    )

    # ════════════════════════════════════════════════════════════════════
    # RESUMEN DE DATOS IMPORTADOS
    # ════════════════════════════════════════════════════════════════════

    summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Resumen de los datos importados (órdenes, lotes, clientes, etc.)"
    )

    # ════════════════════════════════════════════════════════════════════
    # AUDITORÍA
    # ════════════════════════════════════════════════════════════════════

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de inicio de la importación",
        index=True
    )

    completed_at: Optional[datetime] = Field(
        default=None,
        description="Fecha de finalización de la importación"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "import_records"
        indexes = [
            "status",
            "imported_by",
            "created_at",
            [("created_at", -1)],
            [("imported_by", 1), ("created_at", -1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ════════════════════════════════════════════════════════════════════

    def add_error(self, row: int, field: str, message: str):
        """Añade un error a la lista de errores"""
        self.errors.append({
            "row": row,
            "field": field,
            "message": message
        })
        self.error_count += 1

    def add_warning(self, row: int, field: str, message: str):
        """Añade una advertencia a la lista"""
        self.warnings.append({
            "row": row,
            "field": field,
            "message": message
        })

    async def mark_completed(self, processing_time: float):
        """Marca la importación como completada"""
        self.processing_time_seconds = processing_time
        self.completed_at = datetime.utcnow()

        if self.error_count > 0:
            self.status = ImportStatus.COMPLETED_WITH_ERRORS
        else:
            self.status = ImportStatus.COMPLETED

        await self.save()

    async def mark_failed(self, error_message: str):
        """Marca la importación como fallida"""
        self.status = ImportStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.add_error(0, "general", error_message)
        await self.save()

    @property
    def success_rate(self) -> float:
        """Calcula el porcentaje de éxito"""
        if self.total_rows == 0:
            return 0.0
        return (self.success_count / self.total_rows) * 100

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def get_recent_imports(limit: int = 10):
        """Obtiene las importaciones más recientes"""
        return await ImportRecord.find_all().sort("-created_at").limit(limit).to_list()

    @staticmethod
    async def get_imports_by_user(employee_id: str, limit: int = 10):
        """Obtiene las importaciones de un empleado específico"""
        return await ImportRecord.find(
            ImportRecord.imported_by == employee_id
        ).sort("-created_at").limit(limit).to_list()
