"""
OSE Platform - SeriesNotification Model
Modelo para el historial de notificaciones de series (App 1)
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SeriesNotification(Document):
    """
    Registro de notificación de series a clientes
    Historial completo de notificaciones enviadas
    """

    # ════════════════════════════════════════════════════════════════════
    # INFORMACIÓN BÁSICA
    # ════════════════════════════════════════════════════════════════════

    fecha: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de la notificación",
        index=True
    )

    # ════════════════════════════════════════════════════════════════════
    # CLIENTE
    # ════════════════════════════════════════════════════════════════════

    customer_id: Optional[str] = Field(
        None,
        description="ID del cliente",
        index=True
    )

    customer_name: Optional[str] = Field(
        None,
        description="Nombre del cliente"
    )

    customer_code: Optional[str] = Field(
        None,
        description="Código del cliente"
    )

    # ════════════════════════════════════════════════════════════════════
    # UBICACIÓN Y LOTE
    # ════════════════════════════════════════════════════════════════════

    location: str = Field(
        ...,
        description="Número de LOTE o Albarán",
        index=True
    )

    # ════════════════════════════════════════════════════════════════════
    # DISPOSITIVOS
    # ════════════════════════════════════════════════════════════════════

    serials: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de dispositivos notificados (IMEI, ICCID, etc.)"
    )

    device_count: int = Field(
        ...,
        description="Cantidad de dispositivos notificados"
    )

    notified_count: int = Field(
        default=0,
        description="Cantidad de dispositivos marcados como notificados en BD"
    )

    failed_serials: List[str] = Field(
        default_factory=list,
        description="IMEIs que fallaron al notificar"
    )

    # ════════════════════════════════════════════════════════════════════
    # CSV Y EMAIL
    # ════════════════════════════════════════════════════════════════════

    csv_format: str = Field(
        ...,
        description="Formato del CSV (separated, unified, detailed, compact)"
    )

    csv_filename: str = Field(
        ...,
        description="Nombre del archivo CSV generado"
    )

    csv_content: Optional[str] = Field(
        None,
        description="Contenido del CSV (opcional, puede ser muy grande)"
    )

    email_to: str = Field(
        ...,
        description="Email destinatario",
        index=True
    )

    email_cc: Optional[List[str]] = Field(
        None,
        description="Emails en copia"
    )

    email_sent: bool = Field(
        default=False,
        description="Si el email fue enviado exitosamente"
    )

    # ════════════════════════════════════════════════════════════════════
    # OPERADOR
    # ════════════════════════════════════════════════════════════════════

    operator_id: str = Field(
        ...,
        description="ID del operador que envió la notificación",
        index=True
    )

    operator_name: str = Field(
        ...,
        description="Nombre del operador"
    )

    operator_email: str = Field(
        ...,
        description="Email del operador"
    )

    # ════════════════════════════════════════════════════════════════════
    # NOTAS Y ERRORES
    # ════════════════════════════════════════════════════════════════════

    notes: Optional[str] = Field(
        None,
        description="Notas adicionales"
    )

    errors: Optional[List[str]] = Field(
        None,
        description="Lista de errores ocurridos"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE MONGODB
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "series_notifications"
        indexes = [
            "fecha",
            "customer_id",
            "location",
            "email_to",
            "operator_id"
        ]
