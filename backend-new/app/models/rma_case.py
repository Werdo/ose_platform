"""
OSE Platform - RMA Case Model
Modelo para gestión de casos RMA (Return Merchandise Authorization)
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RMAStatus(str, Enum):
    """Estados de un caso RMA"""
    INITIATED = "initiated"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEVICE_RECEIVED = "device_received"
    UNDER_INSPECTION = "under_inspection"
    REPAIR_IN_PROGRESS = "repair_in_progress"
    REPLACEMENT_PREPARED = "replacement_prepared"
    SHIPPED_TO_CUSTOMER = "shipped_to_customer"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RMAType(str, Enum):
    """Tipos de RMA"""
    REPAIR = "repair"
    REPLACEMENT = "replacement"
    REFUND = "refund"
    EXCHANGE = "exchange"


class RMAReason(str, Enum):
    """Razones de RMA"""
    DEFECTIVE = "defective"
    DOA = "doa"  # Dead on Arrival
    WARRANTY_CLAIM = "warranty_claim"
    CUSTOMER_DISSATISFACTION = "customer_dissatisfaction"
    WRONG_PRODUCT = "wrong_product"
    DAMAGED_IN_TRANSIT = "damaged_in_transit"
    OTHER = "other"


class InspectionResult(str, Enum):
    """Resultados de inspección de RMA"""
    PASS = "pass"
    FAIL = "fail"
    NEEDS_REPAIR = "needs_repair"
    UNREPAIRABLE = "unrepairable"
    NOT_COVERED = "not_covered"
    PENDING = "pending"


class RMACase(Document):
    """
    Caso RMA (Return Merchandise Authorization)
    Gestiona devoluciones, reemplazos y reparaciones
    """

    # ════════════════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ════════════════════════════════════════════════════════════════════

    rma_number: str = Field(
        ...,
        description="Número único de RMA (ej: RMA-2025-00001)",
        index=True
    )

    # ════════════════════════════════════════════════════════════════════
    # DISPOSITIVO Y CLIENTE
    # ════════════════════════════════════════════════════════════════════

    device_id: str = Field(
        ...,
        description="ID del dispositivo original",
        index=True
    )

    imei: str = Field(
        ...,
        description="IMEI del dispositivo original",
        index=True
    )

    customer_id: str = Field(
        ...,
        description="ID del cliente",
        index=True
    )

    customer_name: Optional[str] = Field(
        default=None,
        description="Nombre del cliente (cache)"
    )

    # ════════════════════════════════════════════════════════════════════
    # TICKET RELACIONADO
    # ════════════════════════════════════════════════════════════════════

    service_ticket_id: Optional[str] = Field(
        default=None,
        description="ID del ticket de servicio que generó este RMA"
    )

    ticket_number: Optional[str] = Field(
        default=None,
        description="Número del ticket (cache)"
    )

    # ════════════════════════════════════════════════════════════════════
    # CLASIFICACIÓN
    # ════════════════════════════════════════════════════════════════════

    status: RMAStatus = Field(
        default=RMAStatus.INITIATED,
        description="Estado actual del RMA",
        index=True
    )

    rma_type: RMAType = Field(
        default=RMAType.REPAIR,
        description="Tipo de RMA"
    )

    reason: RMAReason = Field(
        default=RMAReason.DEFECTIVE,
        description="Razón de la devolución"
    )

    reason_detail: Optional[str] = Field(
        default=None,
        description="Descripción detallada de la razón"
    )

    # ════════════════════════════════════════════════════════════════════
    # REEMPLAZO (si aplica)
    # ════════════════════════════════════════════════════════════════════

    replacement_device_id: Optional[str] = Field(
        default=None,
        description="ID del dispositivo de reemplazo"
    )

    replacement_imei: Optional[str] = Field(
        default=None,
        description="IMEI del dispositivo de reemplazo"
    )

    # ════════════════════════════════════════════════════════════════════
    # INSPECCIÓN
    # ════════════════════════════════════════════════════════════════════

    inspection: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Resultados de la inspección del dispositivo devuelto"
    )
    # Ejemplo:
    # {
    #     "inspector": "EMP005",
    #     "date": "2025-01-15T10:00:00Z",
    #     "findings": "Pantalla rota, batería funcional",
    #     "physical_damage": True,
    #     "water_damage": False,
    #     "software_issue": False,
    #     "warranty_valid": True,
    #     "approved_for_warranty": True,
    #     "photos": [...]
    # }

    # ════════════════════════════════════════════════════════════════════
    # GARANTÍA
    # ════════════════════════════════════════════════════════════════════

    under_warranty: bool = Field(
        default=True,
        description="Si el dispositivo está bajo garantía"
    )

    warranty_void: bool = Field(
        default=False,
        description="Si la garantía se anuló (por daño físico, etc.)"
    )

    warranty_void_reason: Optional[str] = Field(
        default=None,
        description="Razón de anulación de garantía"
    )

    # ════════════════════════════════════════════════════════════════════
    # COSTOS
    # ════════════════════════════════════════════════════════════════════

    cost_estimate: Optional[float] = Field(
        default=None,
        description="Costo estimado de reparación (si aplica)"
    )

    cost_actual: Optional[float] = Field(
        default=None,
        description="Costo real de reparación"
    )

    charged_to_customer: bool = Field(
        default=False,
        description="Si se cobra al cliente"
    )

    amount_charged: Optional[float] = Field(
        default=None,
        description="Monto cobrado al cliente"
    )

    # ════════════════════════════════════════════════════════════════════
    # LOGÍSTICA
    # ════════════════════════════════════════════════════════════════════

    return_shipping: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Información de envío de devolución"
    )
    # {
    #     "carrier": "SEUR",
    #     "tracking_number": "ABC123",
    #     "shipped_date": "...",
    #     "received_date": "..."
    # }

    replacement_shipping: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Información de envío del reemplazo"
    )

    # ════════════════════════════════════════════════════════════════════
    # RESOLUCIÓN
    # ════════════════════════════════════════════════════════════════════

    resolution: Optional[str] = Field(
        default=None,
        description="Resolución final del RMA"
    )

    resolution_date: Optional[datetime] = Field(
        default=None,
        description="Fecha de resolución"
    )

    # ════════════════════════════════════════════════════════════════════
    # APROBACIÓN
    # ════════════════════════════════════════════════════════════════════

    approved_by: Optional[str] = Field(
        default=None,
        description="ID del empleado que aprobó el RMA"
    )

    approved_at: Optional[datetime] = Field(
        default=None,
        description="Fecha de aprobación"
    )

    rejection_reason: Optional[str] = Field(
        default=None,
        description="Razón de rechazo (si aplica)"
    )

    # ════════════════════════════════════════════════════════════════════
    # COMUNICACIÓN
    # ════════════════════════════════════════════════════════════════════

    notes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Notas y comentarios"
    )

    attachments: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Archivos adjuntos (fotos, documentos)"
    )

    # ════════════════════════════════════════════════════════════════════
    # FECHAS
    # ════════════════════════════════════════════════════════════════════

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación del RMA",
        index=True
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )

    completed_at: Optional[datetime] = Field(
        default=None,
        description="Fecha de completación"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA
    # ════════════════════════════════════════════════════════════════════

    created_by: Optional[str] = Field(
        default=None,
        description="ID del usuario que creó el RMA"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Datos adicionales"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "rma_cases"
        indexes = [
            "rma_number",  # Unique
            "device_id",
            "imei",
            "customer_id",
            "status",
            "created_at",
            [("status", 1), ("created_at", -1)],
            [("customer_id", 1), ("created_at", -1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # PROPIEDADES
    # ════════════════════════════════════════════════════════════════════

    @property
    def is_active(self) -> bool:
        """Verifica si el RMA está activo"""
        return self.status not in [
            RMAStatus.COMPLETED,
            RMAStatus.CANCELLED,
            RMAStatus.REJECTED
        ]

    @property
    def processing_time_days(self) -> Optional[int]:
        """Calcula el tiempo de procesamiento en días"""
        if self.completed_at:
            delta = self.completed_at - self.created_at
            return delta.days

        delta = datetime.utcnow() - self.created_at
        return delta.days

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ════════════════════════════════════════════════════════════════════

    async def approve(self, approved_by: str):
        """Aprueba el RMA"""
        self.status = RMAStatus.APPROVED
        self.approved_by = approved_by
        self.approved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        await self.save()

    async def reject(self, reason: str, rejected_by: str):
        """Rechaza el RMA"""
        self.status = RMAStatus.REJECTED
        self.rejection_reason = reason
        self.approved_by = rejected_by
        self.approved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        await self.save()

    async def add_note(self, author: str, text: str, author_name: Optional[str] = None):
        """Añade una nota al RMA"""
        note = {
            "author": author,
            "author_name": author_name,
            "text": text,
            "timestamp": datetime.utcnow()
        }
        self.notes.append(note)
        self.updated_at = datetime.utcnow()
        await self.save()

    async def complete(self, resolution: str):
        """Completa el RMA"""
        self.status = RMAStatus.COMPLETED
        self.resolution = resolution
        self.resolution_date = datetime.utcnow()
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        await self.save()

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def generate_rma_number() -> str:
        """Genera un número de RMA único"""
        year = datetime.utcnow().year
        prefix = f"RMA-{year}-"

        last_rma = await RMACase.find(
            RMACase.rma_number.regex(f"^{prefix}")
        ).sort("-rma_number").limit(1).to_list()

        if last_rma:
            last_number = int(last_rma[0].rma_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"{prefix}{new_number:05d}"

    @staticmethod
    async def find_by_rma_number(rma_number: str) -> Optional["RMACase"]:
        """Busca un RMA por su número"""
        return await RMACase.find_one(
            RMACase.rma_number == rma_number.strip().upper()
        )

    @staticmethod
    async def find_by_device(device_id: str):
        """Encuentra todos los RMAs de un dispositivo"""
        return await RMACase.find(
            RMACase.device_id == device_id
        ).sort("-created_at").to_list()

    @staticmethod
    async def find_active_rmas():
        """Encuentra todos los RMAs activos"""
        return await RMACase.find(
            RMACase.status.not_in([
                RMAStatus.COMPLETED,
                RMAStatus.CANCELLED,
                RMAStatus.REJECTED
            ])
        ).sort("-created_at").to_list()

    @staticmethod
    async def find_pending_approval():
        """Encuentra RMAs pendientes de aprobación"""
        return await RMACase.find(
            RMACase.status == RMAStatus.PENDING_APPROVAL
        ).sort("-created_at").to_list()
