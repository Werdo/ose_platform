"""
OSE Platform - Transform Template Model
Modelo para plantillas de transformación de documentos
"""

from beanie import Document
from pydantic import Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum


class DestinationType(str, Enum):
    """Tipos de destino de importación"""
    DEVICES = "devices"
    INVENTORY = "inventory"
    SERVICE_TICKETS = "service_tickets"
    DEPOSITOS = "depositos"
    CUSTOMERS = "customers"


class FieldType(str, Enum):
    """Tipos de datos para validación"""
    TEXT = "texto"
    NUMBER = "numero"
    BOOLEAN = "booleano"
    DATE = "fecha"
    EMAIL = "email"


class TransformTemplate(Document):
    """
    Plantilla de transformación de documentos
    Define cómo mapear y validar datos de archivos externos
    """

    # ════════════════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ════════════════════════════════════════════════════════════════════

    name: str = Field(
        ...,
        description="Nombre único de la plantilla",
        index=True
    )

    description: Optional[str] = Field(
        default=None,
        description="Descripción de la plantilla"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN
    # ════════════════════════════════════════════════════════════════════

    destination: DestinationType = Field(
        ...,
        description="Colección MongoDB destino",
        index=True
    )

    file_types: List[str] = Field(
        default_factory=lambda: ["csv", "xlsx"],
        description="Tipos de archivo soportados"
    )

    # ════════════════════════════════════════════════════════════════════
    # MAPEO DE CAMPOS
    # ════════════════════════════════════════════════════════════════════

    mapping: Dict[str, str] = Field(
        ...,
        description="Mapeo de columnas origen -> campo destino"
    )
    # Ejemplo: {"Producto": "nombre", "Cantidad": "stock"}

    # ════════════════════════════════════════════════════════════════════
    # VALIDACIÓN
    # ════════════════════════════════════════════════════════════════════

    validation: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Reglas de validación por campo"
    )
    # Ejemplo: {"stock": {"tipo": "numero", "min": 0}}

    # ════════════════════════════════════════════════════════════════════
    # TRANSFORMACIONES
    # ════════════════════════════════════════════════════════════════════

    transformations: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Transformaciones especiales (conversión de formatos, etc.)"
    )
    # Ejemplo: {"fecha": {"formato_origen": "DD/MM/YYYY", "formato_destino": "ISO"}}

    default_values: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Valores por defecto para campos no mapeados"
    )

    required_fields: List[str] = Field(
        default_factory=list,
        description="Campos requeridos en el documento fuente"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN AVANZADA
    # ════════════════════════════════════════════════════════════════════

    skip_rows: int = Field(
        default=0,
        description="Número de filas a saltar al inicio del archivo"
    )

    encoding: str = Field(
        default="utf-8",
        description="Codificación del archivo"
    )

    delimiter: Optional[str] = Field(
        default=",",
        description="Delimitador para archivos CSV"
    )

    sheet_name: Optional[str] = Field(
        default=None,
        description="Nombre de la hoja para archivos Excel (None = primera hoja)"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA
    # ════════════════════════════════════════════════════════════════════

    is_active: bool = Field(
        default=True,
        description="Si la plantilla está activa",
        index=True
    )

    created_by: str = Field(
        ...,
        description="ID del empleado que creó la plantilla"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación",
        index=True
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )

    last_used_at: Optional[datetime] = Field(
        default=None,
        description="Última vez que se usó la plantilla"
    )

    usage_count: int = Field(
        default=0,
        description="Número de veces que se ha usado"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "transform_templates"
        indexes = [
            "name",
            "destination",
            "is_active",
            "created_at"
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ════════════════════════════════════════════════════════════════════

    async def increment_usage(self):
        """Incrementa el contador de uso"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        await self.save()

    @staticmethod
    async def find_by_name(name: str) -> Optional["TransformTemplate"]:
        """Busca una plantilla por nombre"""
        return await TransformTemplate.find_one(
            TransformTemplate.name == name,
            TransformTemplate.is_active == True
        )

    @staticmethod
    async def find_by_destination(destination: DestinationType):
        """Encuentra todas las plantillas para un destino específico"""
        return await TransformTemplate.find(
            TransformTemplate.destination == destination,
            TransformTemplate.is_active == True
        ).sort("-usage_count").to_list()

    @staticmethod
    async def get_active_templates():
        """Obtiene todas las plantillas activas"""
        return await TransformTemplate.find(
            TransformTemplate.is_active == True
        ).sort("-created_at").to_list()
