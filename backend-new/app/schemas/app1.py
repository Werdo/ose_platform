"""
OSE Platform - App 1 Schemas
Schemas para App 1: Notificación de Series a Clientes
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class NotificarSeriesRequest(BaseModel):
    """
    Schema para notificar series a un cliente
    Endpoint principal de App 1
    """
    cliente_id: str = Field(
        ...,
        description="ID del cliente (ObjectId como string)"
    )
    series: List[str] = Field(
        ...,
        description="Lista de IMEIs a notificar",
        min_items=1
    )
    ubicacion: Optional[str] = Field(
        None,
        description="Ubicación de los dispositivos"
    )
    enviar_email: bool = Field(
        default=True,
        description="Si enviar email de notificación"
    )
    operador: Optional[str] = Field(
        None,
        description="ID del operador que realiza la notificación"
    )

    @validator('series')
    def validate_series(cls, v):
        """Valida que todos los IMEIs sean válidos"""
        for imei in v:
            if not imei or len(imei.strip()) != 15:
                raise ValueError(f'IMEI inválido: {imei}. Debe tener 15 dígitos')
            if not imei.strip().isdigit():
                raise ValueError(f'IMEI inválido: {imei}. Debe contener solo dígitos')
        return [imei.strip() for imei in v]

    class Config:
        json_schema_extra = {
            "example": {
                "cliente_id": "507f1f77bcf86cd799439011",
                "series": [
                    "123456789012345",
                    "123456789012346"
                ],
                "ubicacion": "Almacén Central - Madrid",
                "enviar_email": True,
                "operador": "EMP001"
            }
        }


class NotificarSeriesResponse(BaseModel):
    """Schema para respuesta de notificación de series"""
    success: bool = Field(..., description="Si la operación fue exitosa")
    notificados: int = Field(..., description="Cantidad de dispositivos notificados")
    errores: List[str] = Field(default_factory=list, description="Lista de errores")
    detalles: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Detalles de cada dispositivo"
    )
    email_enviado: bool = Field(default=False, description="Si se envió el email")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "notificados": 2,
                "errores": [],
                "detalles": [
                    {
                        "imei": "123456789012345",
                        "status": "notificado",
                        "device_id": "507f1f77bcf86cd799439012"
                    },
                    {
                        "imei": "123456789012346",
                        "status": "notificado",
                        "device_id": "507f1f77bcf86cd799439013"
                    }
                ],
                "email_enviado": True
            }
        }


class BuscarDispositivosRequest(BaseModel):
    """Schema para buscar dispositivos disponibles para notificar"""
    cliente_id: Optional[str] = Field(None, description="Filtrar por cliente")
    nro_orden: Optional[str] = Field(None, description="Filtrar por orden de producción")
    estado: Optional[str] = Field(None, description="Filtrar por estado")
    notificado: Optional[bool] = Field(None, description="Filtrar por notificado/no notificado")
    limit: int = Field(default=100, ge=1, le=1000, description="Límite de resultados")
    skip: int = Field(default=0, ge=0, description="Saltar resultados")

    class Config:
        json_schema_extra = {
            "example": {
                "estado": "aprobado",
                "notificado": False,
                "limit": 50
            }
        }


class DispositivoResponse(BaseModel):
    """Schema para respuesta de dispositivo"""
    id: str = Field(..., description="ID del dispositivo")
    imei: str = Field(..., description="IMEI")
    ccid: Optional[str] = Field(None, description="CCID")
    marca: Optional[str] = Field(None, description="Marca")
    nro_referencia: Optional[str] = Field(None, description="Referencia")
    estado: str = Field(..., description="Estado")
    notificado: bool = Field(..., description="Si fue notificado")
    cliente: Optional[str] = Field(None, description="ID del cliente")
    cliente_nombre: Optional[str] = Field(None, description="Nombre del cliente")
    nro_orden: Optional[str] = Field(None, description="Orden de producción")
    lote: Optional[int] = Field(None, description="Lote")
    fecha_creacion: datetime = Field(..., description="Fecha de creación")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439012",
                "imei": "123456789012345",
                "ccid": "89340123456789012345",
                "marca": "OversunTrack",
                "nro_referencia": "OST-GPS-001",
                "estado": "aprobado",
                "notificado": False,
                "cliente": None,
                "cliente_nombre": None,
                "nro_orden": "ORD-2025-001",
                "lote": 1,
                "fecha_creacion": "2025-01-15T10:30:00"
            }
        }


class HistorialDispositivoResponse(BaseModel):
    """Schema para historial de un dispositivo"""
    device_id: str = Field(..., description="ID del dispositivo")
    imei: str = Field(..., description="IMEI")
    eventos: List[Dict[str, Any]] = Field(..., description="Lista de eventos")
    movimientos: List[Dict[str, Any]] = Field(..., description="Lista de movimientos")

    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "507f1f77bcf86cd799439012",
                "imei": "123456789012345",
                "eventos": [
                    {
                        "event_type": "created",
                        "timestamp": "2025-01-15T08:00:00",
                        "descripcion": "Dispositivo creado"
                    },
                    {
                        "event_type": "notified_to_client",
                        "timestamp": "2025-01-15T10:30:00",
                        "cliente": "507f1f77bcf86cd799439011"
                    }
                ],
                "movimientos": [
                    {
                        "tipo": "envio",
                        "fecha": "2025-01-15T10:30:00",
                        "cliente_nombre": "Cliente XYZ"
                    }
                ]
            }
        }


class EstadisticasClienteResponse(BaseModel):
    """Schema para estadísticas de un cliente"""
    cliente_id: str = Field(..., description="ID del cliente")
    cliente_nombre: str = Field(..., description="Nombre del cliente")
    total_dispositivos: int = Field(..., description="Total de dispositivos")
    dispositivos_activos: int = Field(..., description="Dispositivos activos")
    dispositivos_notificados: int = Field(..., description="Dispositivos notificados")
    ultima_notificacion: Optional[datetime] = Field(None, description="Última notificación")

    class Config:
        json_schema_extra = {
            "example": {
                "cliente_id": "507f1f77bcf86cd799439011",
                "cliente_nombre": "Cliente XYZ S.L.",
                "total_dispositivos": 150,
                "dispositivos_activos": 145,
                "dispositivos_notificados": 150,
                "ultima_notificacion": "2025-01-15T10:30:00"
            }
        }


class ClienteSimpleResponse(BaseModel):
    """Schema simplificado de cliente para listados"""
    id: str = Field(..., description="ID del cliente")
    customer_code: str = Field(..., description="Código del cliente")
    full_name: str = Field(..., description="Nombre completo")
    email: str = Field(..., description="Email")
    status: str = Field(..., description="Estado")
    devices_count: int = Field(default=0, description="Total de dispositivos")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "customer_code": "CLI001",
                "full_name": "Cliente XYZ S.L.",
                "email": "contacto@clientexyz.com",
                "status": "active",
                "devices_count": 150
            }
        }


class ValidateBulkRequest(BaseModel):
    """Schema para validación de múltiples IMEIs antes de notificar"""
    series: List[str] = Field(
        ...,
        description="Lista de IMEIs a validar",
        min_items=1
    )

    class Config:
        json_schema_extra = {
            "example": {
                "series": [
                    "123456789012345",
                    "123456789012346",
                    "123456789012347"
                ]
            }
        }


class ValidateBulkResponse(BaseModel):
    """Schema para respuesta de validación de IMEIs"""
    success: bool = Field(..., description="Si la validación fue exitosa")
    total: int = Field(..., description="Total de series validadas")
    validos: int = Field(..., description="Total de series válidas")
    invalidos: int = Field(..., description="Total de series inválidas")
    resultados: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Detalles de cada IMEI validado"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total": 3,
                "validos": 2,
                "invalidos": 1,
                "resultados": [
                    {
                        "imei": "123456789012345",
                        "valido": True,
                        "existe": True,
                        "notificado": False,
                        "message": "Disponible para notificar"
                    },
                    {
                        "imei": "123456789012346",
                        "valido": True,
                        "existe": True,
                        "notificado": True,
                        "message": "Ya fue notificado"
                    },
                    {
                        "imei": "123456789012347",
                        "valido": False,
                        "existe": False,
                        "notificado": False,
                        "message": "No encontrado en el sistema"
                    }
                ]
            }
        }


class DeviceSerialInput(BaseModel):
    """Schema para entrada de dispositivo con IMEI/ICCID"""
    imei: str = Field(..., description="IMEI del dispositivo")
    iccid: Optional[str] = Field(None, description="ICCID del dispositivo")
    package_no: Optional[str] = Field(None, description="Número de paquete")


class SendNotificationRequest(BaseModel):
    """Schema para envío completo de notificación con CSV"""
    serials: List[DeviceSerialInput] = Field(
        ...,
        description="Lista de dispositivos a notificar",
        min_items=1
    )
    customer_id: Optional[str] = Field(None, description="ID del cliente (opcional)")
    customer_name: Optional[str] = Field(None, description="Nombre del cliente (opcional)")
    location: str = Field(..., description="Número de LOTE o Albarán")
    csv_format: str = Field(..., description="Formato del CSV (separated, unified, detailed, compact)")
    email_to: str = Field(..., description="Email destinatario")
    email_cc: Optional[List[str]] = Field(None, description="Emails en copia")
    notes: Optional[str] = Field(None, description="Notas adicionales")

    class Config:
        json_schema_extra = {
            "example": {
                "serials": [
                    {"imei": "123456789012345", "iccid": "89344060000000000001"},
                    {"imei": "123456789012346", "iccid": "89344060000000000002"}
                ],
                "customer_id": "507f1f77bcf86cd799439011",
                "customer_name": "Cliente XYZ S.L.",
                "location": "LOTE-2025-001",
                "csv_format": "separated",
                "email_to": "cliente@example.com",
                "email_cc": ["supervisor@example.com"],
                "notes": "Envío urgente"
            }
        }


class SendNotificationResponse(BaseModel):
    """Schema para respuesta de envío de notificación"""
    success: bool = Field(..., description="Si la operación fue exitosa")
    notified_count: int = Field(..., description="Cantidad de dispositivos notificados")
    csv_content: str = Field(..., description="Contenido del archivo CSV generado")
    csv_filename: str = Field(..., description="Nombre del archivo CSV")
    email_sent: bool = Field(..., description="Si el email fue enviado")
    failed_serials: List[str] = Field(default_factory=list, description="IMEIs que fallaron")
    errors: Optional[List[str]] = Field(None, description="Lista de errores")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "notified_count": 2,
                "csv_content": "IMEI,ICCID\n123456789012345,89344060000000000001\n",
                "csv_filename": "series_20250114_143022.csv",
                "email_sent": True,
                "failed_serials": [],
                "errors": None
            }
        }
