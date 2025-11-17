"""
OSE Platform - Service Ticket Schemas
Schemas para tickets de soporte
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.service_ticket import TicketStatus, TicketPriority, TicketCategory


# ════════════════════════════════════════════════════════════════════════
# CREATE & UPDATE
# ════════════════════════════════════════════════════════════════════════

class TicketCreate(BaseModel):
    """Request para crear ticket"""
    customer_id: str
    device_id: Optional[str] = None
    imei: Optional[str] = None
    category: TicketCategory
    priority: TicketPriority = TicketPriority.MEDIUM
    subject: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class TicketUpdate(BaseModel):
    """Request para actualizar ticket"""
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to_id: Optional[str] = None
    resolution: Optional[str] = None
    customer_satisfaction: Optional[int] = Field(None, ge=1, le=5)


class TicketComment(BaseModel):
    """Request para añadir comentario"""
    comment: str = Field(..., min_length=1)
    internal: bool = False


# ════════════════════════════════════════════════════════════════════════
# RESPONSE
# ════════════════════════════════════════════════════════════════════════

class TicketResponse(BaseModel):
    """Response de ticket completo"""
    id: str
    ticket_number: str
    customer_id: str
    device_id: Optional[str]
    imei: Optional[str]
    category: TicketCategory
    status: TicketStatus
    priority: TicketPriority
    subject: str
    description: str
    contact_name: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    assigned_to_id: Optional[str]
    created_by_id: Optional[str]
    resolution: Optional[str]
    comments: List[dict]
    attachments: List[dict]
    sla_due_date: Optional[datetime]
    resolved_at: Optional[datetime]
    customer_satisfaction: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TicketSummary(BaseModel):
    """Resumen de ticket para listas"""
    id: str
    ticket_number: str
    customer_id: str
    category: TicketCategory
    status: TicketStatus
    priority: TicketPriority
    subject: str
    created_at: datetime

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════════════════
# FILTER
# ════════════════════════════════════════════════════════════════════════

class TicketFilter(BaseModel):
    """Filtros para tickets"""
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[TicketCategory] = None
    customer_id: Optional[str] = None
    assigned_to_id: Optional[str] = None
    overdue: Optional[bool] = None
    search: Optional[str] = None


# ════════════════════════════════════════════════════════════════════════
# STATISTICS
# ════════════════════════════════════════════════════════════════════════

class TicketStatistics(BaseModel):
    """Estadísticas de tickets"""
    total: int
    by_status: dict
    by_priority: dict
    by_category: dict
    open_tickets: int
    overdue_tickets: int
    avg_resolution_hours: float
    satisfaction_avg: Optional[float]
