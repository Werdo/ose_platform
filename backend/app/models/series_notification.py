"""
OSE Platform - Series Notification Model
Modelo para el historial de notificaciones de series a clientes (App 1)
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CSVFormat(str, Enum):
    """Formatos de CSV para notificación"""
    SEPARATED = "separated"  # IMEI,ICCID (dos columnas)
    UNIFIED = "unified"       # "IMEI ICCID" (una columna)


class SeriesNotification(Document):
    """
    Registro de notificación de series a clientes
    Almacena el historial completo de envíos desde App 1
    """

    # ════════════════════════════════════════════════════════════════════
    # INFORMACIÓN BÁSICA
    # ════════════════════════════════════════════════════════════════════

    notification_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de la notificación",
        index=True
    )

    # ════════════════════════════════════════════════════════════════════
    # CLIENTE
    # ════════════════════════════════════════════════════════════════════

    customer_id: str = Field(
        ...,
        description="ID del cliente (ObjectId)",
        index=True
    )

    customer_name: str = Field(
        ...,
        description="Nombre del cliente (cache)"
    )

    customer_code: Optional[str] = Field(
        default=None,
        description="Código del cliente"
    )

    customer_email: str = Field(
        ...,
        description="Email del cliente al que se envió"
    )

    # ════════════════════════════════════════════════════════════════════
    # DISPOSITIVOS
    # ════════════════════════════════════════════════════════════════════

    device_count: int = Field(
        ...,
        description="Cantidad de dispositivos notificados"
    )

    device_ids: List[str] = Field(
        default_factory=list,
        description="IDs de los dispositivos notificados"
    )

    serials: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Lista de seriales (IMEI/ICCID)"
    )
    # Ejemplo: [{"imei": "861888...", "iccid": "89882390..."}]

    # ════════════════════════════════════════════════════════════════════
    # CSV Y EMAIL
    # ════════════════════════════════════════════════════════════════════

    csv_format: CSVFormat = Field(
        ...,
        description="Formato del CSV generado"
    )

    csv_filename: str = Field(
        ...,
        description="Nombre del archivo CSV generado"
    )

    csv_content: Optional[str] = Field(
        default=None,
        description="Contenido del CSV (opcional, puede ser muy grande)"
    )

    email_to: str = Field(
        ...,
        description="Destinatario principal del email"
    )

    email_cc: List[str] = Field(
        default_factory=list,
        description="Destinatarios en CC"
    )

    email_subject: Optional[str] = Field(
        default=None,
        description="Asunto del email enviado"
    )

    email_sent: bool = Field(
        default=False,
        description="Si el email fue enviado exitosamente"
    )

    # ════════════════════════════════════════════════════════════════════
    # UBICACIÓN Y DETALLES
    # ════════════════════════════════════════════════════════════════════

    location: Optional[str] = Field(
        default=None,
        description="Ubicación/almacén de destino"
    )

    notes: Optional[str] = Field(
        default=None,
        description="Notas adicionales de la notificación"
    )

    # ════════════════════════════════════════════════════════════════════
    # OPERADOR
    # ════════════════════════════════════════════════════════════════════

    operator_id: Optional[str] = Field(
        default=None,
        description="ID del empleado que realizó la notificación",
        index=True
    )

    operator_name: Optional[str] = Field(
        default=None,
        description="Nombre del operador (cache)"
    )

    operator_email: Optional[str] = Field(
        default=None,
        description="Email del operador (cache)"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA
    # ════════════════════════════════════════════════════════════════════

    source: str = Field(
        default="app1",
        description="Origen de la notificación"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Datos adicionales"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación del registro"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "series_notifications"
        indexes = [
            "notification_date",
            "customer_id",
            "operator_id",
            [("customer_id", 1), ("notification_date", -1)],
            [("operator_id", 1), ("notification_date", -1)],
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def get_history(
        page: int = 1,
        limit: int = 20,
        customer_id: Optional[str] = None,
        operator_id: Optional[str] = None
    ):
        """
        Obtiene el historial de notificaciones con paginación
        """
        query = SeriesNotification.find()

        if customer_id:
            query = query.find(SeriesNotification.customer_id == customer_id)

        if operator_id:
            query = query.find(SeriesNotification.operator_id == operator_id)

        # Contar total
        total = await query.count()

        # Paginar
        skip = (page - 1) * limit
        items = await query.sort("-notification_date").skip(skip).limit(limit).to_list()

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }

    @staticmethod
    async def get_by_customer(customer_id: str, limit: int = 10):
        """Obtiene notificaciones de un cliente específico"""
        return await SeriesNotification.find(
            SeriesNotification.customer_id == customer_id
        ).sort("-notification_date").limit(limit).to_list()

    @staticmethod
    async def get_by_operator(operator_id: str, limit: int = 10):
        """Obtiene notificaciones realizadas por un operador"""
        return await SeriesNotification.find(
            SeriesNotification.operator_id == operator_id
        ).sort("-notification_date").limit(limit).to_list()

    @staticmethod
    async def count_by_date_range(start_date: datetime, end_date: datetime) -> int:
        """Cuenta notificaciones en un rango de fechas"""
        return await SeriesNotification.find(
            SeriesNotification.notification_date >= start_date,
            SeriesNotification.notification_date <= end_date
        ).count()
