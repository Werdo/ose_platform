"""
OSE Platform - Import Job Model
Modelo para tracking de trabajos de importación
"""

from beanie import Document
from pydantic import Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    """Estados de un job de importación"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"  # Completado con errores


class ImportJob(Document):
    """
    Job de importación de documentos
    Tracking de estado y resultados
    """

    # ════════════════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ════════════════════════════════════════════════════════════════════

    job_number: str = Field(
        ...,
        description="Número único del job (ej: IMP-2025-00001)",
        index=True
    )

    # ════════════════════════════════════════════════════════════════════
    # USUARIO Y PLANTILLA
    # ════════════════════════════════════════════════════════════════════

    employee_id: str = Field(
        ...,
        description="ID del empleado que ejecutó la importación",
        index=True
    )

    employee_name: Optional[str] = Field(
        default=None,
        description="Nombre del empleado (cache)"
    )

    template_id: Optional[str] = Field(
        default=None,
        description="ID de la plantilla utilizada"
    )

    template_name: Optional[str] = Field(
        default=None,
        description="Nombre de la plantilla (cache)"
    )

    # ════════════════════════════════════════════════════════════════════
    # ARCHIVO
    # ════════════════════════════════════════════════════════════════════

    filename: str = Field(
        ...,
        description="Nombre del archivo importado"
    )

    file_type: str = Field(
        ...,
        description="Tipo de archivo (csv, xlsx, pdf)"
    )

    file_size: int = Field(
        ...,
        description="Tamaño del archivo en bytes"
    )

    file_path: Optional[str] = Field(
        default=None,
        description="Ruta donde se guardó el archivo"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN
    # ════════════════════════════════════════════════════════════════════

    destination: str = Field(
        ...,
        description="Colección destino (devices, inventory, etc.)",
        index=True
    )

    operation_mode: str = Field(
        default="insert",
        description="Modo de operación (insert, update, upsert)"
    )

    # ════════════════════════════════════════════════════════════════════
    # ESTADO Y PROGRESO
    # ════════════════════════════════════════════════════════════════════

    status: JobStatus = Field(
        default=JobStatus.PENDING,
        description="Estado actual del job",
        index=True
    )

    progress: int = Field(
        default=0,
        description="Progreso en porcentaje (0-100)"
    )

    # ════════════════════════════════════════════════════════════════════
    # RESULTADOS
    # ════════════════════════════════════════════════════════════════════

    total_rows: int = Field(
        default=0,
        description="Total de filas en el archivo"
    )

    processed_rows: int = Field(
        default=0,
        description="Filas procesadas"
    )

    successful_rows: int = Field(
        default=0,
        description="Filas insertadas/actualizadas exitosamente"
    )

    failed_rows: int = Field(
        default=0,
        description="Filas con errores"
    )

    skipped_rows: int = Field(
        default=0,
        description="Filas saltadas (duplicados, vacías, etc.)"
    )

    # ════════════════════════════════════════════════════════════════════
    # ERRORES Y LOGS
    # ════════════════════════════════════════════════════════════════════

    errors: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de errores encontrados"
    )
    # Ejemplo: [{"row": 5, "field": "stock", "error": "Valor negativo no permitido"}]

    warnings: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de advertencias"
    )

    log_messages: List[str] = Field(
        default_factory=list,
        description="Mensajes de log del proceso"
    )

    # ════════════════════════════════════════════════════════════════════
    # DATOS TRANSFORMADOS
    # ════════════════════════════════════════════════════════════════════

    preview_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Vista previa de los primeros registros transformados"
    )

    mapping_used: Optional[Dict[str, str]] = Field(
        default=None,
        description="Mapeo utilizado (cache)"
    )

    # ════════════════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ════════════════════════════════════════════════════════════════════

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación del job",
        index=True
    )

    started_at: Optional[datetime] = Field(
        default=None,
        description="Fecha de inicio del procesamiento"
    )

    completed_at: Optional[datetime] = Field(
        default=None,
        description="Fecha de finalización"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA
    # ════════════════════════════════════════════════════════════════════

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Metadata adicional"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "import_jobs"
        indexes = [
            "job_number",
            "employee_id",
            "destination",
            "status",
            "created_at",
            [("status", 1), ("created_at", -1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # PROPIEDADES
    # ════════════════════════════════════════════════════════════════════

    @property
    def duration_seconds(self) -> Optional[int]:
        """Calcula la duración del job en segundos"""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds())
        elif self.started_at:
            delta = datetime.utcnow() - self.started_at
            return int(delta.total_seconds())
        return None

    @property
    def success_rate(self) -> float:
        """Calcula el porcentaje de éxito"""
        if self.total_rows == 0:
            return 0.0
        return (self.successful_rows / self.total_rows) * 100

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ════════════════════════════════════════════════════════════════════

    async def start_processing(self):
        """Marca el job como en procesamiento"""
        self.status = JobStatus.PROCESSING
        self.started_at = datetime.utcnow()
        await self.save()

    async def complete(self, success: bool = True):
        """Marca el job como completado"""
        if success and self.failed_rows == 0:
            self.status = JobStatus.COMPLETED
        elif success and self.failed_rows > 0:
            self.status = JobStatus.PARTIAL
        else:
            self.status = JobStatus.FAILED

        self.completed_at = datetime.utcnow()
        self.progress = 100
        await self.save()

    async def add_error(self, row: int, field: str, error: str):
        """Añade un error a la lista"""
        self.errors.append({
            "row": row,
            "field": field,
            "error": error,
            "timestamp": datetime.utcnow()
        })
        self.failed_rows += 1
        await self.save()

    async def add_warning(self, row: int, message: str):
        """Añade una advertencia"""
        self.warnings.append({
            "row": row,
            "message": message,
            "timestamp": datetime.utcnow()
        })
        await self.save()

    async def update_progress(self, processed: int, total: int):
        """Actualiza el progreso"""
        self.processed_rows = processed
        self.total_rows = total
        self.progress = int((processed / total) * 100) if total > 0 else 0
        await self.save()

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def generate_job_number() -> str:
        """Genera un número de job único"""
        year = datetime.utcnow().year
        prefix = f"IMP-{year}-"

        last_job = await ImportJob.find(
            ImportJob.job_number.regex(f"^{prefix}")
        ).sort("-job_number").limit(1).to_list()

        if last_job:
            last_number = int(last_job[0].job_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"{prefix}{new_number:05d}"

    @staticmethod
    async def find_by_employee(employee_id: str):
        """Encuentra todos los jobs de un empleado"""
        return await ImportJob.find(
            ImportJob.employee_id == employee_id
        ).sort("-created_at").to_list()

    @staticmethod
    async def find_recent(limit: int = 20):
        """Encuentra los jobs más recientes"""
        return await ImportJob.find_all().sort("-created_at").limit(limit).to_list()
