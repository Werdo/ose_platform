"""
OSE Platform - RMA Schemas
Schemas para casos RMA
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.rma_case import RMAStatus, RMAType, InspectionResult


# ════════════════════════════════════════════════════════════════════════
# CREATE & UPDATE
# ════════════════════════════════════════════════════════════════════════

class RMACreate(BaseModel):
    """Request para crear RMA"""
    customer_id: str
    device_id: str
    imei: str
    ticket_id: Optional[str] = None
    rma_type: RMAType
    reason: str = Field(..., min_length=10, description="Razón del RMA")
    problem_description: str = Field(..., min_length=20)
    customer_contact: Optional[str] = None


class RMAUpdate(BaseModel):
    """Request para actualizar RMA"""
    status: Optional[RMAStatus] = None
    assigned_to_id: Optional[str] = None
    resolution_notes: Optional[str] = None
    estimated_cost: Optional[float] = Field(None, ge=0)


class RMAInspection(BaseModel):
    """Request para registrar inspección"""
    result: InspectionResult
    findings: str
    warranty_valid: bool
    estimated_cost: Optional[float] = Field(None, ge=0)
    repair_notes: Optional[str] = None


# ════════════════════════════════════════════════════════════════════════
# RESPONSE
# ════════════════════════════════════════════════════════════════════════

class RMAResponse(BaseModel):
    """Response de RMA completo"""
    id: str
    rma_number: str
    customer_id: str
    device_id: str
    imei: str
    ticket_id: Optional[str]
    rma_type: RMAType
    status: RMAStatus
    reason: str
    problem_description: str
    customer_contact: Optional[str]
    assigned_to_id: Optional[str]
    inspection_result: Optional[InspectionResult]
    inspection_findings: Optional[str]
    inspection_date: Optional[datetime]
    warranty_valid: Optional[bool]
    estimated_cost: Optional[float]
    actual_cost: Optional[float]
    resolution_notes: Optional[str]
    approved_at: Optional[datetime]
    approved_by_id: Optional[str]
    completed_at: Optional[datetime]
    tracking_to_warehouse: Optional[str]
    tracking_to_customer: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RMASummary(BaseModel):
    """Resumen de RMA para listas"""
    id: str
    rma_number: str
    customer_id: str
    imei: str
    rma_type: RMAType
    status: RMAStatus
    created_at: datetime

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════════════════
# FILTER & STATISTICS
# ════════════════════════════════════════════════════════════════════════

class RMAFilter(BaseModel):
    """Filtros para RMAs"""
    status: Optional[RMAStatus] = None
    rma_type: Optional[RMAType] = None
    customer_id: Optional[str] = None
    assigned_to_id: Optional[str] = None
    warranty_valid: Optional[bool] = None
    search: Optional[str] = None


class RMAStatistics(BaseModel):
    """Estadísticas de RMAs"""
    total: int
    by_status: dict
    by_type: dict
    open_cases: int
    pending_inspection: int
    avg_resolution_days: float
    warranty_valid_rate: float
