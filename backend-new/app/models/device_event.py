"""
OSE Platform - Device Event Model
Modelo para trazabilidad completa del ciclo de vida de dispositivos
CORREGIDO según documentación oficial
"""

from beanie import Document
from pydantic import Field
from typing import Optional, Dict, Any
from datetime import datetime


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
        description="ID del dispositivo (ObjectId como string)",
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
    # Tipos según documentación:
    # - created
    # - production_started
    # - production_completed
    # - quality_check_started
    # - quality_check_passed
    # - quality_check_failed
    # - packed
    # - shipped
    # - in_transit
    # - delivered
    # - activated
    # - warranty_started
    # - deactivated
    # - service_request
    # - repair_started
    # - repair_completed
    # - replacement_issued
    # - rma_initiated
    # - rma_received
    # - rma_inspected
    # - rma_approved
    # - rma_rejected
    # - rma_completed
    # - notified_to_client  # APP 1
    # - customer_assigned
    # - status_changed
    # - location_changed
    # - returned
    # - retired
    # - disposed
    # - comment_added
    # - custom

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Momento en que ocurrió el evento",
        index=True
    )

    descripcion: Optional[str] = Field(
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

    nro_orden: Optional[str] = Field(
        default=None,
        description="Orden de producción relacionada"
    )

    lote: Optional[int] = Field(
        default=None,
        description="Lote relacionado"
    )

    linea: Optional[int] = Field(
        default=None,
        description="Línea de producción"
    )

    puesto: Optional[int] = Field(
        default=None,
        description="Puesto de trabajo"
    )

    # ════════════════════════════════════════════════════════════════════
    # CLIENTE (para eventos de notificación)
    # ════════════════════════════════════════════════════════════════════

    cliente: Optional[str] = Field(
        default=None,
        description="ID del cliente (ObjectId como string) - para App 1",
        index=True
    )

    # ════════════════════════════════════════════════════════════════════
    # CAMBIOS DE ESTADO
    # ════════════════════════════════════════════════════════════════════

    estado_anterior: Optional[str] = Field(
        default=None,
        description="Estado anterior (si aplica)"
    )

    estado_nuevo: Optional[str] = Field(
        default=None,
        description="Nuevo estado (si aplica)"
    )

    ubicacion_anterior: Optional[str] = Field(
        default=None,
        description="Ubicación anterior"
    )

    ubicacion_nueva: Optional[str] = Field(
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

    origen: Optional[str] = Field(
        default="manual",
        description="Origen del evento (manual, api, import, automated, app1, app2, etc.)"
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
            "cliente",
            [("device_id", 1), ("timestamp", -1)],
            [("imei", 1), ("timestamp", -1)],
            [("event_type", 1), ("timestamp", -1)],
            [("nro_orden", 1), ("timestamp", -1)],
            [("cliente", 1), ("timestamp", -1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def obtener_historial_dispositivo(device_id: str, limit: Optional[int] = None):
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
    async def obtener_historial_por_imei(imei: str, limit: Optional[int] = None):
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
    async def obtener_eventos_recientes(limit: int = 100):
        """Obtiene los eventos más recientes"""
        return await DeviceEvent.find().sort("-timestamp").limit(limit).to_list()

    @staticmethod
    async def obtener_por_tipo(event_type: str, limit: Optional[int] = None):
        """Obtiene eventos por tipo"""
        query = DeviceEvent.find(
            DeviceEvent.event_type == event_type
        ).sort("-timestamp")

        if limit:
            return await query.limit(limit).to_list()

        return await query.to_list()

    @staticmethod
    async def crear_evento(
        device_id: str,
        imei: str,
        event_type: str,
        operator: Optional[str] = None,
        descripcion: Optional[str] = None,
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
            "descripcion": descripcion,
            **kwargs
        }

        event = DeviceEvent(**event_data)
        await event.insert()
        return event
