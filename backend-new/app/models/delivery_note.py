"""
OSE Platform - Modelo Albarán/Delivery Note
Modelo para gestión de albaranes con códigos de palet EST912
"""

from beanie import Document
from pydantic import Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId


class DeliveryNoteSequence(Document):
    """
    Contador de secuencia para códigos EST912
    Solo existirá un documento en la colección para mantener el contador global
    """
    sequence_name: str = Field(
        default="EST912",
        description="Nombre de la secuencia"
    )

    current_value: int = Field(
        default=0,
        description="Valor actual del contador (incrementa con cada nuevo código)"
    )

    last_updated: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización del contador"
    )

    class Settings:
        name = "delivery_note_sequences"
        indexes = ["sequence_name"]

    @classmethod
    async def get_next_value(cls) -> int:
        """
        Obtiene y incrementa el siguiente valor de la secuencia
        Retorna el valor para usar en el código EST912
        """
        sequence = await cls.find_one(cls.sequence_name == "EST912")

        if not sequence:
            # Crear secuencia inicial
            sequence = cls(
                sequence_name="EST912",
                current_value=1,
                last_updated=datetime.utcnow()
            )
            await sequence.insert()
            return 1

        # Incrementar y guardar
        sequence.current_value += 1
        sequence.last_updated = datetime.utcnow()
        await sequence.save()

        return sequence.current_value


class DeliveryNote(Document):
    """
    Modelo para albaranes/delivery notes con código de palet EST912
    """

    # ════════════════════════════════════════════════════════════════════
    # CÓDIGO DE PALET EST912
    # ════════════════════════════════════════════════════════════════════

    pallet_code: str = Field(
        ...,
        description="Código de palet formato EST912XXXXXXXXXX",
        index=True,
        unique=True
    )

    # ════════════════════════════════════════════════════════════════════
    # INFORMACIÓN DEL ALBARÁN
    # ════════════════════════════════════════════════════════════════════

    delivery_note_number: str = Field(
        ...,
        description="Número de albarán",
        index=True
    )

    order_number: Optional[str] = Field(
        None,
        description="Número de pedido asociado",
        index=True
    )

    customer_name: str = Field(
        ...,
        description="Nombre del cliente"
    )

    customer_code: Optional[str] = Field(
        None,
        description="Código de cliente"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONTENIDO DEL PALET
    # ════════════════════════════════════════════════════════════════════

    total_boxes: int = Field(
        ...,
        ge=1,
        description="Cantidad total de cajas en el palet"
    )

    box_configuration: Optional[str] = Field(
        None,
        description="Configuración de cajas (ej: 48 unidades/caja)"
    )

    total_units: Optional[int] = Field(
        None,
        description="Total de unidades en el palet"
    )

    product_description: Optional[str] = Field(
        None,
        description="Descripción del producto"
    )

    # ════════════════════════════════════════════════════════════════════
    # INFORMACIÓN DEL ENVÍO
    # ════════════════════════════════════════════════════════════════════

    sender_name: str = Field(
        default="Oversun Energy SL",
        description="Nombre del remitente"
    )

    sender_address: Optional[str] = Field(
        None,
        description="Dirección del remitente"
    )

    destination_address: Optional[str] = Field(
        None,
        description="Dirección de destino"
    )

    # ════════════════════════════════════════════════════════════════════
    # ETIQUETAS
    # ════════════════════════════════════════════════════════════════════

    total_pallets_in_order: int = Field(
        default=1,
        ge=1,
        description="Total de palets en este pedido (para etiqueta X/N)"
    )

    pallet_number_in_order: int = Field(
        default=1,
        ge=1,
        description="Número de este palet en el pedido (para etiqueta X/N)"
    )

    labels_to_print: int = Field(
        default=1,
        ge=1,
        description="Cantidad de etiquetas a imprimir"
    )

    # ════════════════════════════════════════════════════════════════════
    # ESTADO Y AUDITORÍA
    # ════════════════════════════════════════════════════════════════════

    status: str = Field(
        default="preparado",
        description="preparado, enviado, entregado, cancelado"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación",
        index=True
    )

    updated_at: Optional[datetime] = Field(
        None,
        description="Última actualización"
    )

    created_by: Optional[str] = Field(
        None,
        description="Usuario que creó el albarán"
    )

    notes: Optional[str] = Field(
        None,
        description="Notas adicionales"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "delivery_notes"
        indexes = [
            "pallet_code",
            "delivery_note_number",
            "order_number",
            "customer_name",
            "status",
            "created_at",
            [("order_number", 1), ("pallet_number_in_order", 1)],
            [("status", 1), ("created_at", -1)]
        ]

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "pallet_code": "EST9120000000001",
                "delivery_note_number": "ALB-2024-001",
                "order_number": "PED-2024-0015",
                "customer_name": "Cliente Ejemplo SA",
                "customer_code": "CLI001",
                "total_boxes": 48,
                "box_configuration": "48 unidades/caja",
                "total_units": 2304,
                "product_description": "Baliza V16 Carlite-C",
                "sender_name": "Oversun Energy SL",
                "total_pallets_in_order": 3,
                "pallet_number_in_order": 1,
                "labels_to_print": 4,
                "status": "preparado",
                "created_by": "operario@ose.com"
            }
        }

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def generate_pallet_code() -> str:
        """
        Genera un nuevo código de palet en formato EST912XXXXXXXXXX

        - EST: Código de país (España)
        - 912: Código fijo
        - XXXXXXXXXX: Número secuencial de 10 dígitos (con ceros a la izquierda)

        Returns:
            str: Código de palet único (ej: EST9120000000001)
        """
        next_value = await DeliveryNoteSequence.get_next_value()

        # Formatear a 10 dígitos con ceros a la izquierda
        sequence_str = str(next_value).zfill(10)

        return f"EST912{sequence_str}"

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS DE INSTANCIA
    # ════════════════════════════════════════════════════════════════════

    async def mark_as_sent(self):
        """Marca el albarán como enviado"""
        self.status = "enviado"
        self.updated_at = datetime.utcnow()
        await self.save()

    async def mark_as_delivered(self):
        """Marca el albarán como entregado"""
        self.status = "entregado"
        self.updated_at = datetime.utcnow()
        await self.save()

    async def cancel(self):
        """Cancela el albarán"""
        self.status = "cancelado"
        self.updated_at = datetime.utcnow()
        await self.save()

    def to_dict(self) -> dict:
        """Convierte el albarán a diccionario para API responses"""
        return {
            "id": str(self.id) if self.id else None,
            "pallet_code": self.pallet_code,
            "delivery_note_number": self.delivery_note_number,
            "order_number": self.order_number,
            "customer_name": self.customer_name,
            "customer_code": self.customer_code,
            "total_boxes": self.total_boxes,
            "box_configuration": self.box_configuration,
            "total_units": self.total_units,
            "product_description": self.product_description,
            "sender_name": self.sender_name,
            "sender_address": self.sender_address,
            "destination_address": self.destination_address,
            "total_pallets_in_order": self.total_pallets_in_order,
            "pallet_number_in_order": self.pallet_number_in_order,
            "labels_to_print": self.labels_to_print,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
            "notes": self.notes
        }
