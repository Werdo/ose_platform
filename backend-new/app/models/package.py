"""
OSE Platform - Modelo Package
Modelo para gestión de paquetería pequeña con tracking
"""

from beanie import Document
from pydantic import Field, EmailStr
from typing import List, Optional
from datetime import datetime
from bson import ObjectId


class Package(Document):
    """
    Modelo para gestión de paquetes pequeños

    Representa un envío de paquetería con tracking,
    integración con transportistas y notificación al cliente
    """

    # Identificación y tracking
    tracking_number: str = Field(..., description="Número de seguimiento del transportista")
    transportista: str = Field(..., description="Nombre del transportista (Seur, Correos, etc.)")

    # Asociación con pedido
    order_code: str = Field(..., description="Código del pedido web")
    order_ref: Optional[ObjectId] = Field(None, description="Referencia ObjectId al pedido")

    # Cliente
    cliente_id: Optional[ObjectId] = Field(None, description="Referencia al cliente")
    cliente_email: EmailStr = Field(..., description="Email del cliente para notificación")
    cliente_nombre: Optional[str] = Field(None, description="Nombre del cliente")
    cliente_telefono: Optional[str] = Field(None, description="Teléfono del cliente")

    # Dirección de envío
    direccion_envio: Optional[str] = Field(None, description="Dirección completa de envío")
    ciudad: Optional[str] = Field(None, description="Ciudad")
    codigo_postal: Optional[str] = Field(None, description="Código postal")
    pais: str = Field(default="ES", description="País (código ISO)")

    # Contenido
    dispositivos: List[ObjectId] = Field(default_factory=list, description="Referencias a devices incluidos")
    dispositivos_info: List[dict] = Field(
        default_factory=list,
        description="Información denormalizada de dispositivos (IMEI, modelo, etc.)"
    )

    # Información del paquete
    peso_kg: Optional[float] = Field(None, description="Peso en kg")
    dimensiones: Optional[str] = Field(None, description="Dimensiones (ej: 30x20x10 cm)")
    numero_bultos: int = Field(default=1, description="Número de bultos")

    # Tracking y estado
    tipo: str = Field(default="paqueteria", description="Tipo de envío")
    estado: str = Field(default="preparado", description="preparado, enviado, en_transito, entregado, incidencia")
    fecha_envio: Optional[datetime] = None
    fecha_entrega_estimada: Optional[datetime] = None
    fecha_entrega_real: Optional[datetime] = None

    # Notificaciones
    email_enviado: bool = Field(default=False, description="Si se envió el email de notificación")
    fecha_email: Optional[datetime] = None
    enlace_seguimiento: Optional[str] = Field(None, description="URL de seguimiento del transportista")

    # Metadata
    creado_por: str = Field(..., description="Usuario que creó el paquete")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_modificacion: Optional[datetime] = None
    notas: Optional[str] = Field(None, description="Observaciones adicionales")

    class Settings:
        name = "packages"
        indexes = [
            "tracking_number",
            "order_code",
            "transportista",
            "estado",
            "cliente_email",
            "fecha_creacion"
        ]

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "tracking_number": "CX123456789ES",
                "transportista": "Seur",
                "order_code": "PEDWEB-20251111-0021",
                "cliente_email": "cliente@example.com",
                "cliente_nombre": "Juan Pérez",
                "direccion_envio": "Calle Principal 123",
                "ciudad": "Madrid",
                "codigo_postal": "28001",
                "dispositivos_info": [
                    {"imei": "123456789012345", "modelo": "Tracker GPS", "descripcion": "Rastreador vehicular"}
                ],
                "peso_kg": 0.5,
                "estado": "preparado",
                "creado_por": "operario@ose.com"
            }
        }

    async def marcar_como_enviado(self):
        """Marca el paquete como enviado y registra la fecha"""
        self.estado = "enviado"
        self.fecha_envio = datetime.utcnow()
        self.fecha_modificacion = datetime.utcnow()
        await self.save()

    async def marcar_email_enviado(self):
        """Marca que se envió el email de notificación"""
        self.email_enviado = True
        self.fecha_email = datetime.utcnow()
        self.fecha_modificacion = datetime.utcnow()
        await self.save()

    async def actualizar_estado(self, nuevo_estado: str):
        """Actualiza el estado del paquete"""
        self.estado = nuevo_estado
        self.fecha_modificacion = datetime.utcnow()

        if nuevo_estado == "entregado":
            self.fecha_entrega_real = datetime.utcnow()

        await self.save()
