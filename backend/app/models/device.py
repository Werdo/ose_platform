"""
OSE Platform - Device Model
Modelo principal para gestión de dispositivos IoT/GPS
"""

from beanie import Document, Link
from pydantic import Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DeviceStatus(str, Enum):
    """Estados del ciclo de vida del dispositivo"""
    IN_PRODUCTION = "in_production"
    QUALITY_CONTROL = "quality_control"
    APPROVED = "approved"
    REJECTED = "rejected"
    PACKED = "packed"
    SHIPPED = "shipped"
    IN_SERVICE = "in_service"
    FAULTY = "faulty"
    RMA = "rma"
    REPLACED = "replaced"
    RETIRED = "retired"


class Device(Document):
    """
    Modelo principal de dispositivo
    Registro maestro de cada dispositivo único (IMEI/CCID)
    """

    # ════════════════════════════════════════════════════════════════════
    # IDENTIFICACIÓN ÚNICA
    # ════════════════════════════════════════════════════════════════════

    imei: str = Field(
        ...,
        description="IMEI del dispositivo (15 dígitos)",
        min_length=15,
        max_length=15,
        index=True
    )

    ccid: Optional[str] = Field(
        default=None,
        description="ICCID de la tarjeta SIM (19-22 dígitos)",
        min_length=19,
        max_length=22,
        index=True
    )

    # ════════════════════════════════════════════════════════════════════
    # PRODUCCIÓN
    # ════════════════════════════════════════════════════════════════════

    production_order: Optional[str] = Field(
        default=None,
        description="Número de orden de producción",
        index=True
    )

    batch: Optional[int] = Field(
        default=None,
        description="Número de lote dentro de la orden"
    )

    production_line: Optional[int] = Field(
        default=None,
        description="Línea de producción (1, 2, 3)",
        ge=1,
        le=3
    )

    workstation: Optional[int] = Field(
        default=None,
        description="Puesto de trabajo (1, 2)"
    )

    # ════════════════════════════════════════════════════════════════════
    # PRODUCTO
    # ════════════════════════════════════════════════════════════════════

    sku: Optional[str] = Field(
        default=None,
        description="SKU del producto"
    )

    reference_number: Optional[str] = Field(
        default=None,
        description="Número de referencia del modelo"
    )

    brand: Optional[str] = Field(
        default=None,
        description="Marca del dispositivo (Neoway, OversunTrack, etc.)"
    )

    model: Optional[str] = Field(
        default=None,
        description="Modelo del dispositivo"
    )

    # ════════════════════════════════════════════════════════════════════
    # ESTADO Y UBICACIÓN
    # ════════════════════════════════════════════════════════════════════

    status: DeviceStatus = Field(
        default=DeviceStatus.IN_PRODUCTION,
        description="Estado actual del dispositivo",
        index=True
    )

    current_location: Optional[str] = Field(
        default=None,
        description="Ubicación física actual"
    )

    # ════════════════════════════════════════════════════════════════════
    # EMPAQUETADO Y LOGÍSTICA
    # ════════════════════════════════════════════════════════════════════

    package_no: Optional[str] = Field(
        default=None,
        description="Número de caja/paquete",
        index=True
    )

    codigo_innerbox: Optional[str] = Field(
        default=None,
        description="Código de caja intermedia/expositora"
    )

    codigo_unitario: Optional[str] = Field(
        default=None,
        description="Código individual/QR del dispositivo"
    )

    num_palet: Optional[str] = Field(
        default=None,
        description="Número de palet"
    )

    num_deposito: Optional[str] = Field(
        default=None,
        description="Número de depósito"
    )

    # ════════════════════════════════════════════════════════════════════
    # CLIENTE
    # ════════════════════════════════════════════════════════════════════

    customer_id: Optional[str] = Field(
        default=None,
        description="ID del cliente asignado",
        index=True
    )

    customer_code: Optional[str] = Field(
        default=None,
        description="Código del cliente"
    )

    # ════════════════════════════════════════════════════════════════════
    # GARANTÍA
    # ════════════════════════════════════════════════════════════════════

    warranty: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "start_date": None,
            "end_date": None,
            "duration_months": 12,
            "type": "manufacturer",
            "active": False
        },
        description="Información de garantía"
    )

    # ════════════════════════════════════════════════════════════════════
    # ENVÍO
    # ════════════════════════════════════════════════════════════════════

    shipping_info: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Información de envío"
    )
    # Ejemplo:
    # {
    #     "carrier": "SEUR",
    #     "tracking_number": "ABC123456",
    #     "shipped_date": "2025-01-15",
    #     "delivered_date": "2025-01-16",
    #     "recipient": "...",
    #     "address": "..."
    # }

    # ════════════════════════════════════════════════════════════════════
    # NOTIFICACIÓN
    # ════════════════════════════════════════════════════════════════════

    notificado: bool = Field(
        default=False,
        description="Si se notificó al cliente (App 1)"
    )

    cliente_notificado: Optional[str] = Field(
        default=None,
        description="Cliente al que se notificó"
    )

    fecha_notificacion: Optional[datetime] = Field(
        default=None,
        description="Fecha de notificación al cliente"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA Y VALIDACIÓN
    # ════════════════════════════════════════════════════════════════════

    valid: bool = Field(
        default=True,
        description="Si el dispositivo pasó todas las validaciones"
    )

    errores: Optional[list] = Field(
        default_factory=list,
        description="Lista de errores de validación"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Campos adicionales personalizados"
    )

    # ════════════════════════════════════════════════════════════════════
    # AUDITORÍA
    # ════════════════════════════════════════════════════════════════════

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación/registro",
        index=True
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )

    created_by: Optional[str] = Field(
        default=None,
        description="Operador que creó el registro"
    )

    fecha_importacion: Optional[datetime] = Field(
        default=None,
        description="Fecha de importación (si fue importado)"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "devices"
        indexes = [
            "imei",  # Unique
            "ccid",
            "production_order",
            "status",
            "customer_id",
            "package_no",
            "created_at",
            [("imei", 1), ("status", 1)],
            [("production_order", 1), ("batch", 1)],
            [("customer_id", 1), ("status", 1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # VALIDADORES
    # ════════════════════════════════════════════════════════════════════

    @validator('imei')
    def validate_imei(cls, v):
        """Valida que el IMEI sea numérico de 15 dígitos"""
        v = v.strip()
        if not v.isdigit():
            raise ValueError('IMEI debe contener solo dígitos')
        if len(v) != 15:
            raise ValueError('IMEI debe tener exactamente 15 dígitos')
        return v

    @validator('ccid')
    def validate_ccid(cls, v):
        """Valida que el CCID sea numérico de 19-22 dígitos"""
        if v is None:
            return v
        v = v.strip()
        if not v.isdigit():
            raise ValueError('CCID debe contener solo dígitos')
        if not (19 <= len(v) <= 22):
            raise ValueError('CCID debe tener entre 19 y 22 dígitos')
        return v

    # ════════════════════════════════════════════════════════════════════
    # PROPIEDADES
    # ════════════════════════════════════════════════════════════════════

    @property
    def numero_serie(self) -> str:
        """Retorna el número de serie completo (IMEI + CCID)"""
        if self.ccid:
            return f"{self.imei} {self.ccid}"
        return self.imei

    @property
    def is_under_warranty(self) -> bool:
        """Verifica si el dispositivo está bajo garantía"""
        if not self.warranty or not self.warranty.get('active'):
            return False

        end_date = self.warranty.get('end_date')
        if not end_date:
            return False

        return datetime.utcnow() < end_date

    @property
    def warranty_days_remaining(self) -> Optional[int]:
        """Retorna los días restantes de garantía"""
        if not self.is_under_warranty:
            return 0

        end_date = self.warranty.get('end_date')
        if not end_date:
            return 0

        delta = end_date - datetime.utcnow()
        return max(0, delta.days)

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ════════════════════════════════════════════════════════════════════

    async def activate_warranty(self, months: int = 12):
        """Activa la garantía del dispositivo"""
        from datetime import timedelta

        self.warranty = {
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=months * 30),
            "duration_months": months,
            "type": "manufacturer",
            "active": True
        }
        self.updated_at = datetime.utcnow()
        await self.save()

    async def change_status(self, new_status: DeviceStatus, operator: Optional[str] = None):
        """
        Cambia el estado del dispositivo y crea un evento
        """
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()
        await self.save()

        # Crear evento en device_events
        from app.models.device_event import DeviceEvent, EventType

        event = DeviceEvent(
            device_id=str(self.id),
            imei=self.imei,
            event_type=f"status_changed_to_{new_status.value}",
            timestamp=datetime.utcnow(),
            operator=operator,
            old_status=old_status.value,
            new_status=new_status.value,
            production_order=self.production_order,
            batch=self.batch,
            production_line=self.production_line
        )
        await event.insert()

    async def mark_as_notified(self, customer: str, operator: Optional[str] = None):
        """Marca el dispositivo como notificado (App 1)"""
        self.notificado = True
        self.cliente_notificado = customer
        self.fecha_notificacion = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        await self.save()

        # Crear evento
        from app.models.device_event import DeviceEvent

        event = DeviceEvent(
            device_id=str(self.id),
            imei=self.imei,
            event_type="customer_notified",
            timestamp=datetime.utcnow(),
            operator=operator,
            data={
                "customer": customer,
                "notified_at": self.fecha_notificacion.isoformat()
            }
        )
        await event.insert()

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def find_by_imei(imei: str) -> Optional["Device"]:
        """Busca un dispositivo por IMEI"""
        return await Device.find_one(Device.imei == imei.strip())

    @staticmethod
    async def find_by_ccid(ccid: str) -> Optional["Device"]:
        """Busca un dispositivo por CCID"""
        return await Device.find_one(Device.ccid == ccid.strip())

    @staticmethod
    async def find_by_package(package_no: str):
        """Busca todos los dispositivos de un paquete"""
        return await Device.find(Device.package_no == package_no.strip()).to_list()

    @staticmethod
    async def find_by_order(order_number: str):
        """Busca todos los dispositivos de una orden de producción"""
        return await Device.find(Device.production_order == order_number.strip()).to_list()

    @staticmethod
    async def count_by_status(status: DeviceStatus) -> int:
        """Cuenta dispositivos por estado"""
        return await Device.find(Device.status == status).count()

    @staticmethod
    async def devices_under_warranty():
        """Retorna dispositivos bajo garantía activa"""
        return await Device.find(
            Device.warranty.active == True,
            Device.warranty.end_date > datetime.utcnow()
        ).to_list()
