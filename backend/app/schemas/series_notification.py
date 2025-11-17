"""
OSE Platform - Series Notification Schemas
Schemas para API de notificación de series (App 1)
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CSVFormatEnum(str, Enum):
    """Formatos de CSV"""
    SEPARATED = "separated"  # IMEI,ICCID (dos columnas)
    UNIFIED = "unified"       # "IMEI ICCID" (una columna)


# ════════════════════════════════════════════════════════════════════════
# REQUEST SCHEMAS
# ════════════════════════════════════════════════════════════════════════

class DeviceSerialInput(BaseModel):
    """Serial de dispositivo (IMEI/ICCID)"""
    imei: str = Field(..., min_length=15, max_length=15, description="IMEI del dispositivo")
    iccid: Optional[str] = Field(None, min_length=19, max_length=22, description="ICCID de la SIM")
    package_no: Optional[str] = Field(None, description="Número de paquete (si aplica)")

    @validator('imei')
    def validate_imei(cls, v):
        if not v.isdigit():
            raise ValueError('IMEI debe contener solo dígitos')
        return v

    @validator('iccid')
    def validate_iccid(cls, v):
        if v and not v.isdigit():
            raise ValueError('ICCID debe contener solo dígitos')
        return v


class ParseInputRequest(BaseModel):
    """Request para parsear input de texto"""
    input_text: str = Field(..., description="Texto con IMEI/ICCID para parsear")


class ValidateSerialRequest(BaseModel):
    """Request para validar un serial"""
    serial: DeviceSerialInput = Field(..., description="Serial a validar")


class ValidateBulkRequest(BaseModel):
    """Request para validar múltiples seriales"""
    serials: List[DeviceSerialInput] = Field(..., description="Lista de seriales a validar")


class SendNotificationRequest(BaseModel):
    """Request para enviar notificación"""
    serials: List[DeviceSerialInput] = Field(
        ...,
        description="Lista de seriales a notificar",
        min_items=1
    )
    customer_id: str = Field(..., description="ID del cliente")
    customer_name: str = Field(..., description="Nombre del cliente")
    location: Optional[str] = Field(None, description="Ubicación/almacén de destino")
    csv_format: CSVFormatEnum = Field(..., description="Formato del CSV")
    email_to: EmailStr = Field(..., description="Email destinatario")
    email_cc: Optional[List[EmailStr]] = Field(None, description="Emails en CC")
    notes: Optional[str] = Field(None, description="Notas adicionales")


# ════════════════════════════════════════════════════════════════════════
# RESPONSE SCHEMAS
# ════════════════════════════════════════════════════════════════════════

class DeviceSerialOutput(BaseModel):
    """Serial de dispositivo con información adicional"""
    imei: str
    iccid: Optional[str] = None
    package_no: Optional[str] = None
    device_id: Optional[str] = None
    exists: Optional[bool] = None
    already_notified: Optional[bool] = None
    error: Optional[str] = None


class ParseResult(BaseModel):
    """Resultado del parseo de input"""
    valid: List[DeviceSerialOutput] = Field(default_factory=list)
    invalid: List[Dict[str, str]] = Field(default_factory=list)
    total: int = Field(default=0)


class ValidationResult(BaseModel):
    """Resultado de validación de un serial"""
    serial: DeviceSerialOutput
    valid: bool
    exists: bool
    already_notified: bool
    error: Optional[str] = None
    device_id: Optional[str] = None


class BulkValidationResult(BaseModel):
    """Resultado de validación masiva"""
    total: int
    valid: int
    invalid: int
    already_notified: int
    results: List[ValidationResult]


class NotificationResponse(BaseModel):
    """Respuesta de envío de notificación"""
    success: bool
    message: str
    notification_id: Optional[str] = None
    notified_count: int
    csv_content: Optional[str] = None
    csv_filename: str
    email_sent: bool
    failed_serials: List[str] = Field(default_factory=list)
    errors: Optional[List[str]] = None


class CustomerOutput(BaseModel):
    """Información de cliente"""
    id: str
    name: str
    email: str
    code: Optional[str] = None
    active: bool
    customer_type: Optional[str] = None


class NotificationHistoryItem(BaseModel):
    """Item del historial de notificaciones"""
    id: str
    notification_date: datetime
    customer_id: str
    customer_name: str
    customer_email: str
    device_count: int
    csv_format: str
    csv_filename: str
    email_to: str
    email_cc: List[str] = Field(default_factory=list)
    email_sent: bool
    location: Optional[str] = None
    notes: Optional[str] = None
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    operator_email: Optional[str] = None
    serials: List[Dict[str, str]] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationHistoryResponse(BaseModel):
    """Respuesta con historial de notificaciones"""
    items: List[NotificationHistoryItem]
    total: int
    page: int
    limit: int
    pages: int


class NotificationDetailsResponse(BaseModel):
    """Detalles completos de una notificación"""
    notification: NotificationHistoryItem
    devices: Optional[List[Dict[str, Any]]] = None


# ════════════════════════════════════════════════════════════════════════
# UTILITY SCHEMAS
# ════════════════════════════════════════════════════════════════════════

class OptionsResponse(BaseModel):
    """Opciones para la aplicación (clientes, formatos, etc.)"""
    customers: List[CustomerOutput]
    csv_formats: List[Dict[str, str]] = [
        {"value": "separated", "label": "Separado (IMEI,ICCID)"},
        {"value": "unified", "label": "Unificado (IMEI ICCID)"}
    ]
