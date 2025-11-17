"""
OSE Platform - Quality Control Model
Modelo para registro de inspecciones de control de calidad
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class QCResult(str, Enum):
    """Resultados de control de calidad"""
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONAL = "conditional"
    PENDING = "pending"


class DefectSeverity(str, Enum):
    """Severidad de defectos"""
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class QualityControl(Document):
    """
    Registro de control de calidad
    Inspecciones detalladas de dispositivos
    """

    # ════════════════════════════════════════════════════════════════════
    # DISPOSITIVO
    # ════════════════════════════════════════════════════════════════════

    device_id: str = Field(
        ...,
        description="ID del dispositivo inspeccionado",
        index=True
    )

    imei: str = Field(
        ...,
        description="IMEI del dispositivo",
        index=True
    )

    ccid: Optional[str] = Field(
        default=None,
        description="CCID del dispositivo"
    )

    # ════════════════════════════════════════════════════════════════════
    # PRODUCCIÓN
    # ════════════════════════════════════════════════════════════════════

    production_order: Optional[str] = Field(
        default=None,
        description="Orden de producción"
    )

    batch: Optional[int] = Field(
        default=None,
        description="Lote"
    )

    production_line: Optional[int] = Field(
        default=None,
        description="Línea de producción",
        index=True,
        ge=1,
        le=3
    )

    # ════════════════════════════════════════════════════════════════════
    # INSPECCIÓN
    # ════════════════════════════════════════════════════════════════════

    inspection_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de inspección",
        index=True
    )

    inspector: Optional[str] = Field(
        default=None,
        description="ID del inspector",
        index=True
    )

    inspector_name: Optional[str] = Field(
        default=None,
        description="Nombre del inspector (cache)"
    )

    # ════════════════════════════════════════════════════════════════════
    # RESULTADO
    # ════════════════════════════════════════════════════════════════════

    result: QCResult = Field(
        default=QCResult.PENDING,
        description="Resultado de la inspección",
        index=True
    )

    score: Optional[float] = Field(
        default=None,
        description="Puntuación (0-100)",
        ge=0,
        le=100
    )

    # ════════════════════════════════════════════════════════════════════
    # CHECKLIST
    # ════════════════════════════════════════════════════════════════════

    checklist: Optional[Dict[str, bool]] = Field(
        default_factory=lambda: {
            "physical_appearance": None,
            "screen_condition": None,
            "buttons_functional": None,
            "battery_ok": None,
            "charging_ok": None,
            "gps_signal": None,
            "gsm_signal": None,
            "sim_detected": None,
            "firmware_ok": None,
            "imei_valid": None,
            "iccid_valid": None,
            "no_physical_damage": None
        },
        description="Lista de verificación"
    )

    # ════════════════════════════════════════════════════════════════════
    # DEFECTOS
    # ════════════════════════════════════════════════════════════════════

    defects_found: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Defectos encontrados"
    )
    # [
    #     {
    #         "category": "hardware",
    #         "description": "Botón power suelto",
    #         "severity": "minor",
    #         "action": "replace_button"
    #     }
    # ]

    # ════════════════════════════════════════════════════════════════════
    # ACCIÓN CORRECTIVA
    # ════════════════════════════════════════════════════════════════════

    corrective_action: Optional[str] = Field(
        default=None,
        description="Acción correctiva tomada"
    )

    rework: bool = Field(
        default=False,
        description="Si requirió retrabajo"
    )

    scrap: bool = Field(
        default=False,
        description="Si se desechó"
    )

    # ════════════════════════════════════════════════════════════════════
    # NOTAS
    # ════════════════════════════════════════════════════════════════════

    notes: Optional[str] = Field(
        default=None,
        description="Observaciones del inspector"
    )

    photos: List[str] = Field(
        default_factory=list,
        description="URLs de fotos de la inspección"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA
    # ════════════════════════════════════════════════════════════════════

    duration_seconds: Optional[int] = Field(
        default=None,
        description="Duración de la inspección en segundos"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Datos adicionales"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "quality_control"
        indexes = [
            "device_id",
            "imei",
            "result",
            "production_line",
            "inspection_date",
            "inspector",
            [("production_line", 1), ("inspection_date", -1)],
            [("result", 1), ("inspection_date", -1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def get_quality_rate_by_line(production_line: int, start_date: datetime, end_date: datetime) -> dict:
        """Calcula la tasa de calidad por línea en un rango de fechas"""
        inspections = await QualityControl.find(
            QualityControl.production_line == production_line,
            QualityControl.inspection_date >= start_date,
            QualityControl.inspection_date <= end_date
        ).to_list()

        total = len(inspections)
        passed = sum(1 for i in inspections if i.result == QCResult.PASSED)
        failed = sum(1 for i in inspections if i.result == QCResult.FAILED)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0,
            "fail_rate": (failed / total * 100) if total > 0 else 0
        }
