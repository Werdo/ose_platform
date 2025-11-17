"""
OSE Platform - Production Schemas
Schemas para órdenes de producción y operaciones
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime

from app.models.production_order import ProductionOrderStatus


# ════════════════════════════════════════════════════════════════════════
# PRODUCTION ORDER - CREATE
# ════════════════════════════════════════════════════════════════════════

class ProductionOrderCreate(BaseModel):
    """
    Request para crear orden de producción

    Example:
        {
            "order_number": "OP-2025-00001",
            "sku": "OSE-GPS-4G-V2",
            "quantity": 1000,
            "customer_id": "507f...",
            "priority": "high",
            "due_date": "2025-02-01"
        }
    """
    order_number: str = Field(..., pattern=r'^OP-\d{4}-\d{5,}$', description="Formato: OP-YYYY-NNNNN")
    sku: str
    quantity: int = Field(..., gt=0, description="Cantidad a producir")
    customer_id: Optional[str] = None
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    due_date: Optional[datetime] = None
    labels_required: bool = False
    notes: Optional[str] = None

    @validator('due_date')
    def validate_due_date(cls, v):
        """Valida que due_date sea futura"""
        if v and v < datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v


# ════════════════════════════════════════════════════════════════════════
# PRODUCTION ORDER - UPDATE
# ════════════════════════════════════════════════════════════════════════

class ProductionOrderUpdate(BaseModel):
    """Request para actualizar orden de producción"""
    status: Optional[ProductionOrderStatus] = None
    priority: Optional[str] = Field(None, pattern="^(low|normal|high|urgent)$")
    due_date: Optional[datetime] = None
    notes: Optional[str] = None


# ════════════════════════════════════════════════════════════════════════
# PRODUCTION ORDER - RESPONSE
# ════════════════════════════════════════════════════════════════════════

class ProductionOrderResponse(BaseModel):
    """
    Response de orden de producción

    Example:
        {
            "id": "507f...",
            "order_number": "OP-2025-00001",
            "sku": "OSE-GPS-4G-V2",
            "quantity": 1000,
            "produced": 750,
            "approved": 735,
            "rejected": 15,
            "status": "in_progress",
            "completion_percentage": 75.0,
            ...
        }
    """
    id: str
    order_number: str
    sku: str
    quantity: int
    produced: int
    approved: int
    rejected: int
    status: ProductionOrderStatus
    customer_id: Optional[str]
    priority: str
    due_date: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    labels_required: bool
    batches: List[dict]  # BatchInfo
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    # Calculated fields
    completion_percentage: float
    quality_rate: float
    rejection_rate: float

    class Config:
        from_attributes = True


class ProductionOrderSummary(BaseModel):
    """Resumen de orden (para listas)"""
    id: str
    order_number: str
    sku: str
    quantity: int
    produced: int
    status: ProductionOrderStatus
    completion_percentage: float
    created_at: datetime

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════════════════
# BATCH MANAGEMENT
# ════════════════════════════════════════════════════════════════════════

class BatchCreate(BaseModel):
    """
    Request para crear lote dentro de orden

    Example:
        {
            "batch_number": "BATCH-001",
            "quantity": 100,
            "production_line": "LINE-1"
        }
    """
    batch_number: str
    quantity: int = Field(..., gt=0)
    production_line: Optional[str] = None
    shift: Optional[str] = None


class BatchUpdate(BaseModel):
    """Request para actualizar lote"""
    produced: Optional[int] = Field(None, ge=0)
    defective: Optional[int] = Field(None, ge=0)
    completed: Optional[bool] = None


# ════════════════════════════════════════════════════════════════════════
# PRODUCTION OPERATIONS
# ════════════════════════════════════════════════════════════════════════

class ProductionStart(BaseModel):
    """
    Request para iniciar producción

    Example:
        {
            "production_line": "LINE-1",
            "operator_id": "EMP-001",
            "shift": "morning"
        }
    """
    production_line: str
    operator_id: Optional[str] = None
    shift: Optional[str] = None
    notes: Optional[str] = None


class ProductionIncrement(BaseModel):
    """
    Request para incrementar contador de producción

    Example:
        {
            "batch_number": "BATCH-001",
            "quantity": 10,
            "operator_id": "EMP-001"
        }
    """
    batch_number: Optional[str] = None
    quantity: int = Field(..., gt=0, description="Cantidad producida")
    operator_id: Optional[str] = None


# ════════════════════════════════════════════════════════════════════════
# FILTER
# ════════════════════════════════════════════════════════════════════════

class ProductionOrderFilter(BaseModel):
    """
    Filtros para listado de órdenes

    Example query params:
        ?status=in_progress&sku=OSE-GPS-4G&priority=high
    """
    status: Optional[ProductionOrderStatus] = None
    sku: Optional[str] = None
    customer_id: Optional[str] = None
    priority: Optional[str] = None
    search: Optional[str] = Field(None, description="Búsqueda en order_number, SKU")
    overdue: Optional[bool] = Field(None, description="Solo órdenes atrasadas")


# ════════════════════════════════════════════════════════════════════════
# STATISTICS
# ════════════════════════════════════════════════════════════════════════

class ProductionStatistics(BaseModel):
    """
    Estadísticas de producción

    Example:
        {
            "total_orders": 50,
            "active_orders": 15,
            "produced_today": 500,
            "produced_this_week": 3000,
            "produced_this_month": 12000,
            "average_quality_rate": 98.5,
            "by_status": {...},
            "by_line": {...}
        }
    """
    total_orders: int
    active_orders: int
    completed_orders: int
    produced_today: int
    produced_this_week: int
    produced_this_month: int
    average_quality_rate: float
    by_status: dict
    by_sku: dict
    by_line: Optional[dict] = None
