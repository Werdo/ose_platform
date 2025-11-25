"""
OSE Platform - ICCID Batch Model
Modelo para almacenar lotes de ICCIDs generados con análisis completo
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from beanie import Document
from pydantic import Field


class ICCIDAnalysis(Document):
    """Análisis individual de un ICCID"""

    iccid: str = Field(..., description="ICCID completo")
    iccid_raw: Optional[str] = Field(None, description="ICCID original sin sanitizar")

    # Información básica
    length: int = Field(..., description="Longitud del ICCID")
    valid_length: bool = Field(..., description="¿Longitud válida? (18-22)")

    # MII (Major Industry Identifier)
    mii: Optional[str] = Field(None, description="MII (normalmente 89)")
    mii_meaning: Optional[str] = Field(None, description="Significado del MII")

    # País
    country_code: Optional[str] = Field(None, description="Código de país")
    country_name: Optional[str] = Field(None, description="Nombre del país")

    # IIN (Issuer Identification Number)
    iin_prefix: Optional[str] = Field(None, description="Prefijo IIN")

    # Perfil del operador
    brand: Optional[str] = Field(None, description="Marca comercial")
    operator: Optional[str] = Field(None, description="Operador/plataforma")
    region: Optional[str] = Field(None, description="Región")
    use_case: Optional[str] = Field(None, description="Caso de uso")
    core_network: Optional[str] = Field(None, description="Tipo de red")
    notes: Optional[str] = Field(None, description="Notas adicionales")
    confidence: Optional[str] = Field(None, description="Nivel de confianza")

    # Número de cuenta y checksum
    account_number: Optional[str] = Field(None, description="Número de cuenta")
    checksum: Optional[str] = Field(None, description="Dígito de control")

    # Validación
    luhn_valid: bool = Field(..., description="¿Checksum Luhn válido?")
    warnings: List[str] = Field(default_factory=list, description="Advertencias")

    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "iccid_analyses"
        indexes = [
            "iccid",
            "iin_prefix",
            "operator",
            "country_code",
            "generated_at",
        ]


class ICCIDBatch(Document):
    """Lote de ICCIDs generados"""

    # Información del lote
    batch_name: str = Field(..., description="Nombre del lote")
    description: Optional[str] = Field(None, description="Descripción del lote")

    # Parámetros de generación
    iccid_start: str = Field(..., description="ICCID inicial del rango (completo)")
    iccid_end: str = Field(..., description="ICCID final del rango (completo)")
    total_count: int = Field(..., description="Cantidad total de ICCIDs")

    # ICCIDs generados con análisis
    iccids: List[str] = Field(default_factory=list, description="Lista de ICCIDs")
    analyses: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Análisis de cada ICCID"
    )

    # Estadísticas del lote
    stats: Dict[str, Any] = Field(
        default_factory=dict,
        description="Estadísticas del lote (operadores, países, etc.)"
    )

    # Metadata
    created_by: str = Field(..., description="Usuario que creó el lote")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # CSV generado
    csv_generated: bool = Field(default=False, description="¿CSV generado?")
    csv_generated_at: Optional[datetime] = Field(None, description="Fecha generación CSV")
    csv_download_count: int = Field(default=0, description="Veces descargado")

    class Settings:
        name = "iccid_batches"
        indexes = [
            "batch_name",
            "created_by",
            "created_at",
            "iccid_start",
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "batch_name": "Lote IoT Enero 2025",
                "description": "ICCIDs para dispositivos IoT desplegados en enero",
                "iccid_start": "89882260100000000001",
                "iccid_end": "89882260100099900008",
                "total_count": 1000,
                "created_by": "ADMIN"
            }
        }
