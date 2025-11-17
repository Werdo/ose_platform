"""
OSE Platform - Inventory Model
Modelo para gestión de inventario (componentes y productos terminados)
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class InventoryCategory(str, Enum):
    """Categorías de inventario"""
    FINISHED_PRODUCT = "finished_product"
    COMPONENT = "component"
    RAW_MATERIAL = "raw_material"
    PACKAGING = "packaging"
    TOOL = "tool"
    CONSUMABLE = "consumable"
    SIM_CARD = "sim_card"
    BATTERY = "battery"
    PCB = "pcb"
    ANTENNA = "antenna"
    CASING = "casing"
    OTHER = "other"


class InventoryStatus(str, Enum):
    """Estados de items de inventario"""
    AVAILABLE = "available"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    RESERVED = "reserved"
    DISCONTINUED = "discontinued"


class InventoryItem(Document):
    """
    Item de inventario
    Gestiona stock de componentes, productos terminados, etc.
    """

    # ════════════════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ════════════════════════════════════════════════════════════════════

    part_number: str = Field(
        ...,
        description="Número de parte único",
        index=True
    )

    category: InventoryCategory = Field(
        default=InventoryCategory.COMPONENT,
        description="Categoría del item"
    )

    # ════════════════════════════════════════════════════════════════════
    # DESCRIPCIÓN
    # ════════════════════════════════════════════════════════════════════

    name: str = Field(
        ...,
        description="Nombre del item"
    )

    description: Optional[str] = Field(
        default=None,
        description="Descripción detallada"
    )

    manufacturer: Optional[str] = Field(
        default=None,
        description="Fabricante"
    )

    model: Optional[str] = Field(
        default=None,
        description="Modelo"
    )

    # ════════════════════════════════════════════════════════════════════
    # STOCK
    # ════════════════════════════════════════════════════════════════════

    quantity: int = Field(
        default=0,
        description="Cantidad actual en stock",
        ge=0
    )

    reserved_quantity: int = Field(
        default=0,
        description="Cantidad reservada",
        ge=0
    )

    available_quantity: int = Field(
        default=0,
        description="Cantidad disponible (quantity - reserved)"
    )

    min_stock: int = Field(
        default=0,
        description="Stock mínimo (alerta de reorden)",
        ge=0
    )

    max_stock: Optional[int] = Field(
        default=None,
        description="Stock máximo"
    )

    reorder_point: int = Field(
        default=0,
        description="Punto de reorden",
        ge=0
    )

    reorder_quantity: int = Field(
        default=0,
        description="Cantidad a reordenar",
        ge=0
    )

    # ════════════════════════════════════════════════════════════════════
    # UBICACIÓN
    # ════════════════════════════════════════════════════════════════════

    location: Optional[str] = Field(
        default=None,
        description="Ubicación física en almacén"
    )

    warehouse: Optional[str] = Field(
        default=None,
        description="Almacén"
    )

    # ════════════════════════════════════════════════════════════════════
    # COSTOS
    # ════════════════════════════════════════════════════════════════════

    unit_cost: Optional[float] = Field(
        default=None,
        description="Costo unitario"
    )

    unit_price: Optional[float] = Field(
        default=None,
        description="Precio de venta unitario"
    )

    currency: str = Field(
        default="EUR",
        description="Moneda"
    )

    # ════════════════════════════════════════════════════════════════════
    # PROVEEDOR
    # ════════════════════════════════════════════════════════════════════

    supplier: Optional[str] = Field(
        default=None,
        description="Proveedor principal"
    )

    supplier_part_number: Optional[str] = Field(
        default=None,
        description="Número de parte del proveedor"
    )

    lead_time_days: Optional[int] = Field(
        default=None,
        description="Tiempo de entrega en días"
    )

    # ════════════════════════════════════════════════════════════════════
    # ESTADO
    # ════════════════════════════════════════════════════════════════════

    status: InventoryStatus = Field(
        default=InventoryStatus.AVAILABLE,
        description="Estado del item",
        index=True
    )

    active: bool = Field(
        default=True,
        description="Si el item está activo"
    )

    # ════════════════════════════════════════════════════════════════════
    # FECHAS
    # ════════════════════════════════════════════════════════════════════

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )

    last_restocked: Optional[datetime] = Field(
        default=None,
        description="Última vez que se reabastecióel stock"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA
    # ════════════════════════════════════════════════════════════════════

    tags: List[str] = Field(
        default_factory=list,
        description="Etiquetas para clasificación"
    )

    notes: Optional[str] = Field(
        default=None,
        description="Notas adicionales"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Datos adicionales"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "inventory"
        indexes = [
            "part_number",  # Unique
            "category",
            "status",
            [("category", 1), ("status", 1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ════════════════════════════════════════════════════════════════════

    async def add_stock(self, quantity: int):
        """Añade stock"""
        self.quantity += quantity
        self.available_quantity = self.quantity - self.reserved_quantity
        self.last_restocked = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        await self.update_status()
        await self.save()

    async def remove_stock(self, quantity: int):
        """Remueve stock"""
        if quantity > self.available_quantity:
            raise ValueError("Insufficient stock")
        self.quantity -= quantity
        self.available_quantity = self.quantity - self.reserved_quantity
        self.updated_at = datetime.utcnow()
        await self.update_status()
        await self.save()

    async def reserve_stock(self, quantity: int):
        """Reserva stock"""
        if quantity > self.available_quantity:
            raise ValueError("Insufficient available stock")
        self.reserved_quantity += quantity
        self.available_quantity = self.quantity - self.reserved_quantity
        self.updated_at = datetime.utcnow()
        await self.save()

    async def update_status(self):
        """Actualiza el estado basado en la cantidad"""
        if self.quantity == 0:
            self.status = InventoryStatus.OUT_OF_STOCK
        elif self.quantity <= self.min_stock:
            self.status = InventoryStatus.LOW_STOCK
        else:
            self.status = InventoryStatus.AVAILABLE

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def find_by_part_number(part_number: str) -> Optional["InventoryItem"]:
        """Busca un item por número de parte"""
        return await InventoryItem.find_one(
            InventoryItem.part_number == part_number.strip().upper()
        )

    @staticmethod
    async def find_low_stock():
        """Encuentra items con stock bajo"""
        return await InventoryItem.find(
            InventoryItem.status == InventoryStatus.LOW_STOCK
        ).to_list()

    @staticmethod
    async def find_out_of_stock():
        """Encuentra items sin stock"""
        return await InventoryItem.find(
            InventoryItem.status == InventoryStatus.OUT_OF_STOCK
        ).to_list()
