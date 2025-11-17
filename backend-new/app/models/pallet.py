"""
OSE Platform - Modelo Pallet
Modelo para gestión de palets en picking logístico
JERARQUÍA: PALLET → CARTON → DEVICE
"""

from beanie import Document
from pydantic import Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId


class Pallet(Document):
    """
    Modelo para gestión de palets de producción

    Representa un palet físico con su contenido jerárquico.
    PALLET contiene CARTONS, CARTONS contienen DEVICES
    """

    # ════════════════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ════════════════════════════════════════════════════════════════════

    pallet_id: str = Field(
        ...,
        description="ID único del pallet (ej: T9121800079317017)",
        index=True
    )

    qr_code: Optional[str] = Field(
        None,
        description="Código QR generado para el pallet"
    )

    # ════════════════════════════════════════════════════════════════════
    # PRODUCCIÓN
    # ════════════════════════════════════════════════════════════════════

    order_number: str = Field(
        ...,
        description="Número de orden de producción (ej: WL00079317)",
        index=True
    )

    factory_id: Optional[int] = Field(
        None,
        description="ID de la fábrica de producción"
    )

    product_model: Optional[str] = Field(
        None,
        description="Modelo del producto (ej: CARLITE)"
    )

    product_reference: Optional[str] = Field(
        None,
        description="Referencia del producto (ej: 55296)"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONTENIDO JERÁRQUICO
    # ════════════════════════════════════════════════════════════════════

    carton_ids: List[str] = Field(
        default_factory=list,
        description="Lista de IDs de cartones que pertenecen a este pallet",
        index=True
    )

    carton_count: int = Field(
        default=0,
        description="Cantidad de cartones en el pallet"
    )

    device_count: int = Field(
        default=0,
        description="Cantidad total de dispositivos en todos los cartones"
    )

    devices_per_carton: Optional[int] = Field(
        None,
        description="Cantidad de dispositivos por cartón (constante si aplica)"
    )

    # ════════════════════════════════════════════════════════════════════
    # INFORMACIÓN LOGÍSTICA
    # ════════════════════════════════════════════════════════════════════

    peso_kg: Optional[float] = Field(
        None,
        description="Peso aproximado en kg"
    )

    volumen_m3: Optional[float] = Field(
        None,
        description="Volumen aproximado en m³"
    )

    ubicacion: Optional[str] = Field(
        None,
        description="Ubicación en almacén"
    )

    # ════════════════════════════════════════════════════════════════════
    # ENVÍO Y CLIENTE (OPCIONAL)
    # ════════════════════════════════════════════════════════════════════

    cliente_id: Optional[str] = Field(
        None,
        description="ID del cliente asignado",
        index=True
    )

    cliente_nombre: Optional[str] = Field(
        None,
        description="Nombre del cliente"
    )

    # ════════════════════════════════════════════════════════════════════
    # ESTADO Y AUDITORÍA
    # ════════════════════════════════════════════════════════════════════

    estado: str = Field(
        default="preparado",
        description="preparado, en_picking, verificado, enviado, entregado",
        index=True
    )

    fecha_creacion: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación del registro",
        index=True
    )

    fecha_modificacion: Optional[datetime] = Field(
        None,
        description="Última modificación"
    )

    creado_por: Optional[str] = Field(
        None,
        description="Usuario que creó el pallet"
    )

    notas: Optional[str] = Field(
        None,
        description="Observaciones adicionales"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "pallets"
        indexes = [
            "pallet_id",
            "order_number",
            "carton_ids",
            "cliente_id",
            "estado",
            "fecha_creacion",
            [("order_number", 1), ("pallet_id", 1)],
            [("estado", 1), ("fecha_creacion", -1)]
        ]

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "pallet_id": "T9121800079317017",
                "order_number": "WL00079317",
                "factory_id": 1,
                "product_model": "CARLITE",
                "product_reference": "55296",
                "carton_ids": [
                    "9912182510100007931700674",
                    "9912182510100007931700675"
                ],
                "carton_count": 48,
                "device_count": 2304,
                "devices_per_carton": 48,
                "estado": "preparado",
                "creado_por": "operario@ose.com"
            }
        }

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ════════════════════════════════════════════════════════════════════

    async def actualizar_contadores(self):
        """
        Actualiza los contadores de cartones y dispositivos
        consultando los datos reales de la BD
        """
        from app.models.device import Device

        # Contar cartones únicos
        devices = await Device.find(Device.pallet_id == self.pallet_id).to_list()
        unique_cartons = set()
        device_count = 0

        for device in devices:
            if device.package_no:  # package_no = carton_id
                unique_cartons.add(device.package_no)
            device_count += 1

        self.carton_count = len(unique_cartons)
        self.device_count = device_count
        self.carton_ids = list(unique_cartons)
        self.fecha_modificacion = datetime.utcnow()

        await self.save()

    async def marcar_como_verificado(self, operador: Optional[str] = None):
        """Marca el pallet como verificado"""
        self.estado = "verificado"
        self.fecha_modificacion = datetime.utcnow()
        if operador:
            self.creado_por = operador
        await self.save()

    async def marcar_como_enviado(self):
        """Marca el pallet como enviado"""
        self.estado = "enviado"
        self.fecha_modificacion = datetime.utcnow()
        await self.save()
