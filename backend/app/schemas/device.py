"""
OSE Platform - Device Schemas
Schemas para gestión de dispositivos
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from datetime import datetime, date

from app.models.device import DeviceStatus
from app.utils.validators import validate_imei, validate_iccid


# ════════════════════════════════════════════════════════════════════════
# CREATE
# ════════════════════════════════════════════════════════════════════════

class DeviceCreate(BaseModel):
    """
    Request para crear dispositivo

    Example:
        {
            "imei": "123456789012345",
            "ccid": "8934071234567890123",
            "production_order": "OP-2025-00001",
            "batch": "BATCH-001",
            "production_line": "LINE-1",
            "sku": "OSE-GPS-4G-V2"
        }
    """
    imei: str = Field(..., min_length=15, max_length=15, description="IMEI de 15 dígitos")
    ccid: Optional[str] = Field(None, min_length=19, max_length=22, description="ICCID de 19-22 dígitos")
    production_order: str = Field(..., description="Número de orden de producción")
    batch: Optional[str] = Field(None, description="Lote de producción")
    production_line: Optional[str] = Field(None, description="Línea de producción")
    station: Optional[str] = Field(None, description="Estación actual")
    sku: Optional[str] = Field(None, description="SKU del producto")
    hardware_version: Optional[str] = None
    firmware_version: Optional[str] = None
    mac_address: Optional[str] = None

    @validator('imei')
    def validate_imei_format(cls, v):
        """Valida formato de IMEI"""
        is_valid, error = validate_imei(v)
        if not is_valid:
            raise ValueError(error)
        return v

    @validator('ccid')
    def validate_ccid_format(cls, v):
        """Valida formato de ICCID"""
        if v is None:
            return v
        is_valid, error = validate_iccid(v)
        if not is_valid:
            raise ValueError(error)
        return v


class DeviceBulkCreate(BaseModel):
    """
    Request para crear múltiples dispositivos

    Example:
        {
            "devices": [
                {"imei": "123456789012345", "ccid": "..."},
                {"imei": "123456789012346", "ccid": "..."}
            ],
            "production_order": "OP-2025-00001",
            "batch": "BATCH-001"
        }
    """
    devices: List[DeviceCreate]
    common_data: Optional[dict] = Field(
        None,
        description="Datos comunes a aplicar a todos los dispositivos"
    )


# ════════════════════════════════════════════════════════════════════════
# UPDATE
# ════════════════════════════════════════════════════════════════════════

class DeviceUpdate(BaseModel):
    """
    Request para actualizar dispositivo

    Todos los campos son opcionales
    """
    ccid: Optional[str] = Field(None, min_length=19, max_length=22)
    status: Optional[DeviceStatus] = None
    station: Optional[str] = None
    sku: Optional[str] = None
    hardware_version: Optional[str] = None
    firmware_version: Optional[str] = None
    mac_address: Optional[str] = None
    customer_id: Optional[str] = None
    notes: Optional[str] = None

    @validator('ccid')
    def validate_ccid_format(cls, v):
        """Valida formato de ICCID"""
        if v is None:
            return v
        is_valid, error = validate_iccid(v)
        if not is_valid:
            raise ValueError(error)
        return v


class DeviceStatusChange(BaseModel):
    """
    Request para cambiar status de dispositivo

    Example:
        {
            "new_status": "quality_control",
            "reason": "Device passed all production tests",
            "notes": "Ready for QC inspection"
        }
    """
    new_status: DeviceStatus
    reason: Optional[str] = Field(None, description="Razón del cambio")
    notes: Optional[str] = None


# ════════════════════════════════════════════════════════════════════════
# RESPONSE
# ════════════════════════════════════════════════════════════════════════

class DeviceResponse(BaseModel):
    """
    Response de dispositivo

    Example:
        {
            "id": "507f1f77bcf86cd799439011",
            "imei": "123456789012345",
            "ccid": "8934071234567890123",
            "status": "in_production",
            "production_order": "OP-2025-00001",
            ...
        }
    """
    id: str
    imei: str
    ccid: Optional[str]
    status: DeviceStatus
    production_order: str
    batch: Optional[str]
    production_line: Optional[str]
    station: Optional[str]
    sku: Optional[str]
    hardware_version: Optional[str]
    firmware_version: Optional[str]
    mac_address: Optional[str]

    # Producción
    produced_at: datetime
    operator_id: Optional[str]

    # QC
    qc_approved: bool
    qc_date: Optional[datetime]
    qc_inspector_id: Optional[str]

    # Warranty
    warranty_start: Optional[date]
    warranty_months: int
    warranty_active: bool

    # Shipping
    shipped_at: Optional[datetime]
    tracking_number: Optional[str]

    # Customer
    customer_id: Optional[str]
    assigned_at: Optional[datetime]

    # Metadata
    created_at: datetime
    updated_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True


class DeviceSummary(BaseModel):
    """
    Resumen de dispositivo (para listas)

    Versión ligera sin todos los detalles
    """
    id: str
    imei: str
    ccid: Optional[str]
    status: DeviceStatus
    sku: Optional[str]
    production_order: str
    produced_at: datetime

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════════════════
# FILTER
# ════════════════════════════════════════════════════════════════════════

class DeviceFilter(BaseModel):
    """
    Filtros para listado de dispositivos

    Example query params:
        ?status=in_production&production_line=LINE-1&sku=OSE-GPS-4G
    """
    status: Optional[DeviceStatus] = None
    production_order: Optional[str] = None
    batch: Optional[str] = None
    production_line: Optional[str] = None
    station: Optional[str] = None
    sku: Optional[str] = None
    customer_id: Optional[str] = None
    qc_approved: Optional[bool] = None
    warranty_active: Optional[bool] = None
    search: Optional[str] = Field(None, description="Búsqueda en IMEI, ICCID, tracking_number")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# ════════════════════════════════════════════════════════════════════════
# SHIPPING
# ════════════════════════════════════════════════════════════════════════

class DeviceShipping(BaseModel):
    """
    Request para marcar dispositivo como enviado

    Example:
        {
            "tracking_number": "TRK123456789",
            "carrier": "DHL",
            "shipped_to": "Customer Name",
            "notes": "Express shipping"
        }
    """
    tracking_number: str
    carrier: Optional[str] = None
    shipped_to: Optional[str] = None
    notes: Optional[str] = None


# ════════════════════════════════════════════════════════════════════════
# CUSTOMER ASSIGNMENT
# ════════════════════════════════════════════════════════════════════════

class DeviceAssignment(BaseModel):
    """
    Request para asignar dispositivo a cliente

    Example:
        {
            "customer_id": "507f1f77bcf86cd799439011",
            "activate_warranty": true,
            "send_notification": true
        }
    """
    customer_id: str
    activate_warranty: bool = True
    send_notification: bool = False
    notes: Optional[str] = None


# ════════════════════════════════════════════════════════════════════════
# STATISTICS
# ════════════════════════════════════════════════════════════════════════

class DeviceStatistics(BaseModel):
    """
    Estadísticas de dispositivos

    Example:
        {
            "total": 10000,
            "by_status": {
                "in_production": 500,
                "quality_control": 200,
                "approved": 1000,
                "shipped": 7000,
                "in_service": 1300
            },
            "produced_today": 150,
            "qc_pass_rate": 98.5
        }
    """
    total: int
    by_status: dict
    by_sku: dict
    produced_today: int
    produced_this_week: int
    produced_this_month: int
    qc_pass_rate: float
    devices_under_warranty: int


# ════════════════════════════════════════════════════════════════════════
# HISTORY
# ════════════════════════════════════════════════════════════════════════

class DeviceHistory(BaseModel):
    """
    Historial de eventos de un dispositivo

    Example:
        {
            "device_id": "507f1f77bcf86cd799439011",
            "imei": "123456789012345",
            "events": [...]
        }
    """
    device_id: str
    imei: str
    events: List[dict]  # Lista de DeviceEvent (se define en device_event schema)
