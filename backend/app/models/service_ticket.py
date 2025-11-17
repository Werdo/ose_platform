"""
OSE Platform - Service Ticket Model
Modelo para gestión de tickets de soporte técnico y post-venta
"""

from beanie import Document
from pydantic import Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum


class TicketStatus(str, Enum):
    """Estados de un ticket de servicio"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    PENDING_CUSTOMER = "pending_customer"
    PENDING_PARTS = "pending_parts"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TicketPriority(str, Enum):
    """Prioridades de tickets"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCategory(str, Enum):
    """Categorías de tickets"""
    HARDWARE_ISSUE = "hardware_issue"
    SOFTWARE_ISSUE = "software_issue"
    CONNECTIVITY = "connectivity"
    BATTERY = "battery"
    GPS_TRACKING = "gps_tracking"
    SIM_CARD = "sim_card"
    WARRANTY_CLAIM = "warranty_claim"
    CONSULTATION = "consultation"
    OTHER = "other"


class ServiceTicket(Document):
    """
    Ticket de servicio post-venta
    Gestiona incidencias, soporte técnico y reparaciones
    """

    # ════════════════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ════════════════════════════════════════════════════════════════════

    ticket_number: str = Field(
        ...,
        description="Número único del ticket (ej: TKT-2025-00001)",
        index=True
    )

    # ════════════════════════════════════════════════════════════════════
    # DISPOSITIVO Y CLIENTE
    # ════════════════════════════════════════════════════════════════════

    device_id: str = Field(
        ...,
        description="ID del dispositivo afectado",
        index=True
    )

    imei: str = Field(
        ...,
        description="IMEI del dispositivo (cache)",
        index=True
    )

    customer_id: str = Field(
        ...,
        description="ID del cliente que reporta",
        index=True
    )

    customer_name: Optional[str] = Field(
        default=None,
        description="Nombre del cliente (cache)"
    )

    customer_email: Optional[str] = Field(
        default=None,
        description="Email del cliente"
    )

    customer_phone: Optional[str] = Field(
        default=None,
        description="Teléfono del cliente"
    )

    # ════════════════════════════════════════════════════════════════════
    # CLASIFICACIÓN
    # ════════════════════════════════════════════════════════════════════

    status: TicketStatus = Field(
        default=TicketStatus.OPEN,
        description="Estado actual del ticket",
        index=True
    )

    priority: TicketPriority = Field(
        default=TicketPriority.MEDIUM,
        description="Prioridad del ticket",
        index=True
    )

    category: TicketCategory = Field(
        default=TicketCategory.OTHER,
        description="Categoría del problema"
    )

    # ════════════════════════════════════════════════════════════════════
    # DESCRIPCIÓN DEL PROBLEMA
    # ════════════════════════════════════════════════════════════════════

    subject: str = Field(
        ...,
        description="Asunto/título del ticket",
        max_length=200
    )

    description: str = Field(
        ...,
        description="Descripción detallada del problema"
    )

    symptoms: Optional[List[str]] = Field(
        default_factory=list,
        description="Síntomas reportados"
    )

    # ════════════════════════════════════════════════════════════════════
    # ASIGNACIÓN
    # ════════════════════════════════════════════════════════════════════

    assigned_to: Optional[str] = Field(
        default=None,
        description="ID del técnico asignado",
        index=True
    )

    assigned_to_name: Optional[str] = Field(
        default=None,
        description="Nombre del técnico (cache)"
    )

    assigned_at: Optional[datetime] = Field(
        default=None,
        description="Fecha de asignación"
    )

    # ════════════════════════════════════════════════════════════════════
    # RESOLUCIÓN
    # ════════════════════════════════════════════════════════════════════

    diagnosis: Optional[str] = Field(
        default=None,
        description="Diagnóstico del técnico"
    )

    resolution: Optional[str] = Field(
        default=None,
        description="Solución aplicada"
    )

    resolution_date: Optional[datetime] = Field(
        default=None,
        description="Fecha de resolución"
    )

    requires_rma: bool = Field(
        default=False,
        description="Si requiere proceso RMA"
    )

    rma_case_id: Optional[str] = Field(
        default=None,
        description="ID del caso RMA asociado"
    )

    # ════════════════════════════════════════════════════════════════════
    # SLA (Service Level Agreement)
    # ════════════════════════════════════════════════════════════════════

    sla_due_date: Optional[datetime] = Field(
        default=None,
        description="Fecha límite según SLA"
    )

    sla_breached: bool = Field(
        default=False,
        description="Si se incumplió el SLA"
    )

    # ════════════════════════════════════════════════════════════════════
    # COMUNICACIÓN
    # ════════════════════════════════════════════════════════════════════

    comments: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Comentarios y actualizaciones"
    )
    # Ejemplo:
    # [
    #     {
    #         "author": "tech_001",
    #         "author_name": "Juan Pérez",
    #         "text": "Revisado el dispositivo...",
    #         "timestamp": "2025-01-15T10:00:00Z",
    #         "internal": False
    #     }
    # ]

    attachments: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Archivos adjuntos (fotos, logs, etc.)"
    )

    # ════════════════════════════════════════════════════════════════════
    # SATISFACCIÓN DEL CLIENTE
    # ════════════════════════════════════════════════════════════════════

    customer_satisfaction: Optional[int] = Field(
        default=None,
        description="Calificación del cliente (1-5)",
        ge=1,
        le=5
    )

    customer_feedback: Optional[str] = Field(
        default=None,
        description="Comentarios del cliente sobre el servicio"
    )

    # ════════════════════════════════════════════════════════════════════
    # FECHAS
    # ════════════════════════════════════════════════════════════════════

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación del ticket",
        index=True
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )

    closed_at: Optional[datetime] = Field(
        default=None,
        description="Fecha de cierre"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA
    # ════════════════════════════════════════════════════════════════════

    created_by: Optional[str] = Field(
        default=None,
        description="ID del usuario que creó el ticket"
    )

    source: Optional[str] = Field(
        default="manual",
        description="Origen del ticket (email, phone, web, portal, api)"
    )

    tags: List[str] = Field(
        default_factory=list,
        description="Etiquetas para clasificación"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Datos adicionales"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "service_tickets"
        indexes = [
            "ticket_number",  # Unique
            "device_id",
            "imei",
            "customer_id",
            "status",
            "priority",
            "assigned_to",
            "created_at",
            [("status", 1), ("priority", 1)],
            [("assigned_to", 1), ("status", 1)],
            [("customer_id", 1), ("created_at", -1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # VALIDADORES
    # ════════════════════════════════════════════════════════════════════

    @validator('ticket_number')
    def validate_ticket_number(cls, v):
        """Valida el formato del número de ticket"""
        return v.strip().upper()

    # ════════════════════════════════════════════════════════════════════
    # PROPIEDADES
    # ════════════════════════════════════════════════════════════════════

    @property
    def is_open(self) -> bool:
        """Verifica si el ticket está abierto"""
        return self.status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS]

    @property
    def is_resolved(self) -> bool:
        """Verifica si el ticket está resuelto"""
        return self.status in [TicketStatus.RESOLVED, TicketStatus.CLOSED]

    @property
    def resolution_time_hours(self) -> Optional[float]:
        """Calcula el tiempo de resolución en horas"""
        if not self.resolution_date:
            return None

        delta = self.resolution_date - self.created_at
        return delta.total_seconds() / 3600

    @property
    def age_hours(self) -> float:
        """Calcula la antigüedad del ticket en horas"""
        delta = datetime.utcnow() - self.created_at
        return delta.total_seconds() / 3600

    @property
    def is_overdue(self) -> bool:
        """Verifica si el ticket está vencido según SLA"""
        if not self.sla_due_date:
            return False

        return datetime.utcnow() > self.sla_due_date and not self.is_resolved

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ════════════════════════════════════════════════════════════════════

    async def assign_to(self, technician_id: str, technician_name: Optional[str] = None):
        """Asigna el ticket a un técnico"""
        self.assigned_to = technician_id
        self.assigned_to_name = technician_name
        self.assigned_at = datetime.utcnow()
        self.status = TicketStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow()
        await self.save()

    async def add_comment(
        self,
        author: str,
        text: str,
        author_name: Optional[str] = None,
        internal: bool = False
    ):
        """Añade un comentario al ticket"""
        comment = {
            "author": author,
            "author_name": author_name,
            "text": text,
            "timestamp": datetime.utcnow(),
            "internal": internal
        }

        self.comments.append(comment)
        self.updated_at = datetime.utcnow()
        await self.save()

    async def resolve(
        self,
        resolution: str,
        diagnosis: Optional[str] = None,
        technician: Optional[str] = None
    ):
        """Marca el ticket como resuelto"""
        self.status = TicketStatus.RESOLVED
        self.resolution = resolution
        if diagnosis:
            self.diagnosis = diagnosis
        self.resolution_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        await self.save()

    async def close(self, feedback: Optional[str] = None, rating: Optional[int] = None):
        """Cierra el ticket"""
        self.status = TicketStatus.CLOSED
        self.closed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        if feedback:
            self.customer_feedback = feedback
        if rating:
            self.customer_satisfaction = rating

        await self.save()

    async def escalate(self, new_priority: TicketPriority):
        """Escala la prioridad del ticket"""
        self.priority = new_priority
        self.updated_at = datetime.utcnow()
        await self.save()

    async def calculate_sla_due_date(self):
        """
        Calcula la fecha límite según SLA basado en la prioridad
        """
        from app.config import settings

        sla_hours = {
            TicketPriority.CRITICAL: settings.APP3_SLA_HOURS_CRITICAL,
            TicketPriority.HIGH: settings.APP3_SLA_HOURS_HIGH,
            TicketPriority.MEDIUM: settings.APP3_SLA_HOURS_MEDIUM,
            TicketPriority.LOW: settings.APP3_SLA_HOURS_LOW
        }

        hours = sla_hours.get(self.priority, 72)
        self.sla_due_date = self.created_at + timedelta(hours=hours)
        await self.save()

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def generate_ticket_number() -> str:
        """Genera un número de ticket único"""
        # Obtener el último ticket del año actual
        year = datetime.utcnow().year
        prefix = f"TKT-{year}-"

        last_ticket = await ServiceTicket.find(
            ServiceTicket.ticket_number.regex(f"^{prefix}")
        ).sort("-ticket_number").limit(1).to_list()

        if last_ticket:
            last_number = int(last_ticket[0].ticket_number.split("-")[-1])
            new_number = last_number + 1
        else:
            new_number = 1

        return f"{prefix}{new_number:05d}"

    @staticmethod
    async def find_by_ticket_number(ticket_number: str) -> Optional["ServiceTicket"]:
        """Busca un ticket por su número"""
        return await ServiceTicket.find_one(
            ServiceTicket.ticket_number == ticket_number.strip().upper()
        )

    @staticmethod
    async def find_by_device(device_id: str):
        """Encuentra todos los tickets de un dispositivo"""
        return await ServiceTicket.find(
            ServiceTicket.device_id == device_id
        ).sort("-created_at").to_list()

    @staticmethod
    async def find_open_tickets():
        """Encuentra todos los tickets abiertos"""
        return await ServiceTicket.find(
            ServiceTicket.status.in_([
                TicketStatus.OPEN,
                TicketStatus.IN_PROGRESS,
                TicketStatus.PENDING_CUSTOMER,
                TicketStatus.PENDING_PARTS
            ])
        ).sort("-priority", "-created_at").to_list()

    @staticmethod
    async def find_by_technician(technician_id: str):
        """Encuentra tickets asignados a un técnico"""
        return await ServiceTicket.find(
            ServiceTicket.assigned_to == technician_id,
            ServiceTicket.status.in_([
                TicketStatus.IN_PROGRESS,
                TicketStatus.PENDING_PARTS
            ])
        ).sort("-priority", "-created_at").to_list()

    @staticmethod
    async def get_overdue_tickets():
        """Encuentra tickets vencidos según SLA"""
        now = datetime.utcnow()
        return await ServiceTicket.find(
            ServiceTicket.sla_due_date < now,
            ServiceTicket.status.in_([
                TicketStatus.OPEN,
                TicketStatus.IN_PROGRESS
            ])
        ).to_list()
