"""
OSE Platform - Device Event Model
Modelo para trazabilidad completa del ciclo de vida de dispositivos
"""

from beanie import Document
from pydantic import Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Tipos de eventos en el ciclo de vida del dispositivo"""
    # Producción
    CREATED = "created"
    PRODUCTION_STARTED = "production_started"
    PRODUCTION_COMPLETED = "production_completed"

    # Control de Calidad
    QUALITY_CHECK_STARTED = "quality_check_started"
    QUALITY_CHECK_PASSED = "quality_check_passed"
    QUALITY_CHECK_FAILED = "quality_check_failed"

    # Empaquetado
    PACKED = "packed"
    LABELED = "labeled"

    # Logística
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"

    # Operación
    ACTIVATED = "activated"
    WARRANTY_STARTED = "warranty_started"
    DEACTIVATED = "deactivated"

    # Post-Venta
    SERVICE_REQUEST = "service_request"
    REPAIR_STARTED = "repair_started"
    REPAIR_COMPLETED = "repair_completed"
    REPLACEMENT_ISSUED = "replacement_issued"

    # RMA
    RMA_INITIATED = "rma_initiated"
    RMA_RECEIVED = "rma_received"
    RMA_INSPECTED = "rma_inspected"
    RMA_APPROVED = "rma_approved"
    RMA_REJECTED = "rma_rejected"
    RMA_COMPLETED = "rma_completed"

    # Cliente
    CUSTOMER_NOTIFIED = "customer_notified"
    CUSTOMER_ASSIGNED = "customer_assigned"

    # Estado
    STATUS_CHANGED = "status_changed"
    LOCATION_CHANGED = "location_changed"

    # Final
    RETURNED = "returned"
    RETIRED = "retired"
    DISPOSED = "disposed"

    # Otros
    COMMENT_ADDED = "comment_added"
    CUSTOM = "custom"


class DeviceEvent(Document):
    """
    Evento en el ciclo de vida de un dispositivo
    Proporciona trazabilidad completa desde producción hasta fin de vida
    """

    # ════════════════════════════════════════════════════════════════════
    # DISPOSITIVO
    # ════════════════════════════════════════════════════════════════════

    device_id: str = Field(
        ...,
        description="ID del dispositivo (ObjectId)",
        index=True
    )

    imei: str = Field(
        ...,
        description="IMEI del dispositivo (para búsquedas rápidas)",
        index=True
    )

    ccid: Optional[str] = Field(
        default=None,
        description="CCID del dispositivo"
    )

    # ════════════════════════════════════════════════════════════════════
    # EVENTO
    # ════════════════════════════════════════════════════════════════════

    event_type: str = Field(
        ...,
        description="Tipo de evento",
        index=True
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Momento en que ocurrió el evento",
        index=True
    )

    description: Optional[str] = Field(
        default=None,
        description="Descripción del evento"
    )

    # ════════════════════════════════════════════════════════════════════
    # OPERADOR / RESPONSABLE
    # ════════════════════════════════════════════════════════════════════

    operator: Optional[str] = Field(
        default=None,
        description="ID del empleado/operador que registró el evento",
        index=True
    )

    operator_name: Optional[str] = Field(
        default=None,
        description="Nombre del operador (cache)"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONTEXTO DE PRODUCCIÓN
    # ════════════════════════════════════════════════════════════════════

    production_order: Optional[str] = Field(
        default=None,
        description="Orden de producción relacionada"
    )

    batch: Optional[int] = Field(
        default=None,
        description="Lote relacionado"
    )

    production_line: Optional[int] = Field(
        default=None,
        description="Línea de producción"
    )

    workstation: Optional[int] = Field(
        default=None,
        description="Puesto de trabajo"
    )

    # ════════════════════════════════════════════════════════════════════
    # CAMBIOS DE ESTADO
    # ════════════════════════════════════════════════════════════════════

    old_status: Optional[str] = Field(
        default=None,
        description="Estado anterior (si aplica)"
    )

    new_status: Optional[str] = Field(
        default=None,
        description="Nuevo estado (si aplica)"
    )

    old_location: Optional[str] = Field(
        default=None,
        description="Ubicación anterior"
    )

    new_location: Optional[str] = Field(
        default=None,
        description="Nueva ubicación"
    )

    # ════════════════════════════════════════════════════════════════════
    # DATOS ADICIONALES
    # ════════════════════════════════════════════════════════════════════

    data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Datos adicionales específicos del evento"
    )
    # Ejemplos:
    # - quality_check: {"result": "passed", "inspector": "EMP001", "defects": []}
    # - shipping: {"carrier": "SEUR", "tracking": "ABC123", "recipient": "..."}
    # - repair: {"issue": "...", "solution": "...", "parts_used": [...]}

    # ════════════════════════════════════════════════════════════════════
    # METADATA
    # ════════════════════════════════════════════════════════════════════

    ip_address: Optional[str] = Field(
        default=None,
        description="IP desde donde se registró el evento"
    )

    user_agent: Optional[str] = Field(
        default=None,
        description="User agent del cliente"
    )

    source: Optional[str] = Field(
        default="manual",
        description="Origen del evento (manual, api, import, automated)"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "device_events"
        indexes = [
            "device_id",
            "imei",
            "event_type",
            "timestamp",
            "operator",
            [("device_id", 1), ("timestamp", -1)],
            [("imei", 1), ("timestamp", -1)],
            [("event_type", 1), ("timestamp", -1)],
            [("production_order", 1), ("timestamp", -1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # PROPIEDADES
    # ════════════════════════════════════════════════════════════════════

    @property
    def event_display_name(self) -> str:
        """Retorna un nombre legible del evento"""
        event_names = {
            "created": "Dispositivo Creado",
            "production_completed": "Producción Completada",
            "quality_check_passed": "Control de Calidad Aprobado",
            "quality_check_failed": "Control de Calidad Rechazado",
            "shipped": "Enviado",
            "delivered": "Entregado",
            "activated": "Activado",
            "service_request": "Solicitud de Servicio",
            "rma_initiated": "RMA Iniciado",
            "customer_notified": "Cliente Notificado",
            "status_changed": "Estado Cambiado",
            "retired": "Retirado"
        }
        return event_names.get(self.event_type, self.event_type.replace("_", " ").title())

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def get_device_history(device_id: str, limit: Optional[int] = None):
        """
        Obtiene el historial completo de un dispositivo
        Ordenado cronológicamente
        """
        query = DeviceEvent.find(
            DeviceEvent.device_id == device_id
        ).sort("+timestamp")

        if limit:
            return await query.limit(limit).to_list()

        return await query.to_list()

    @staticmethod
    async def get_device_history_by_imei(imei: str, limit: Optional[int] = None):
        """
        Obtiene el historial completo de un dispositivo por IMEI
        """
        query = DeviceEvent.find(
            DeviceEvent.imei == imei
        ).sort("+timestamp")

        if limit:
            return await query.limit(limit).to_list()

        return await query.to_list()

    @staticmethod
    async def get_recent_events(limit: int = 100):
        """Obtiene los eventos más recientes"""
        return await DeviceEvent.find().sort("-timestamp").limit(limit).to_list()

    @staticmethod
    async def get_events_by_type(event_type: str, limit: Optional[int] = None):
        """Obtiene eventos por tipo"""
        query = DeviceEvent.find(
            DeviceEvent.event_type == event_type
        ).sort("-timestamp")

        if limit:
            return await query.limit(limit).to_list()

        return await query.to_list()

    @staticmethod
    async def get_events_by_operator(operator: str, limit: Optional[int] = None):
        """Obtiene eventos registrados por un operador"""
        query = DeviceEvent.find(
            DeviceEvent.operator == operator
        ).sort("-timestamp")

        if limit:
            return await query.limit(limit).to_list()

        return await query.to_list()

    @staticmethod
    async def get_events_by_date_range(start_date: datetime, end_date: datetime):
        """Obtiene eventos en un rango de fechas"""
        return await DeviceEvent.find(
            DeviceEvent.timestamp >= start_date,
            DeviceEvent.timestamp <= end_date
        ).sort("-timestamp").to_list()

    @staticmethod
    async def get_production_events(production_order: str):
        """Obtiene todos los eventos de una orden de producción"""
        return await DeviceEvent.find(
            DeviceEvent.production_order == production_order
        ).sort("+timestamp").to_list()

    @staticmethod
    async def count_events_by_type(start_date: Optional[datetime] = None) -> dict:
        """
        Cuenta eventos por tipo
        Opcionalmente desde una fecha específica
        """
        query = {}
        if start_date:
            query["timestamp"] = {"$gte": start_date}

        # Esto debería hacerse con aggregation pipeline en producción
        # Por ahora una versión simplificada
        events = await DeviceEvent.find(query).to_list()

        counts = {}
        for event in events:
            event_type = event.event_type
            counts[event_type] = counts.get(event_type, 0) + 1

        return counts

    @staticmethod
    async def create_event(
        device_id: str,
        imei: str,
        event_type: str,
        operator: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> "DeviceEvent":
        """
        Helper para crear un evento de forma sencilla
        """
        event_data = {
            "device_id": device_id,
            "imei": imei,
            "event_type": event_type,
            "operator": operator,
            "description": description,
            **kwargs
        }

        event = DeviceEvent(**event_data)
        await event.insert()
        return event
