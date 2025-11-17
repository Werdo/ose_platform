"""
OSE Platform - Production Order Model
Modelo para gestión de órdenes de producción
"""

from beanie import Document
from pydantic import Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProductionOrderStatus(str, Enum):
    """Estados de una orden de producción"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    ON_HOLD = "on_hold"
    PACKING = "packing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProductionOrder(Document):
    """
    Orden de producción
    Gestiona lotes de fabricación de dispositivos
    """

    # ════════════════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ════════════════════════════════════════════════════════════════════

    order_number: str = Field(
        ...,
        description="Número único de la orden de producción",
        index=True
    )

    reference_number: Optional[str] = Field(
        default=None,
        description="Número de referencia del producto"
    )

    # ════════════════════════════════════════════════════════════════════
    # PRODUCTO
    # ════════════════════════════════════════════════════════════════════

    sku: Optional[int] = Field(
        default=None,
        description="SKU del producto a fabricar"
    )

    product_name: Optional[str] = Field(
        default=None,
        description="Nombre del producto"
    )

    brand: Optional[str] = Field(
        default=None,
        description="Marca del producto"
    )

    # ════════════════════════════════════════════════════════════════════
    # CANTIDADES
    # ════════════════════════════════════════════════════════════════════

    quantity: int = Field(
        ...,
        description="Cantidad total a producir",
        ge=1
    )

    produced: int = Field(
        default=0,
        description="Cantidad producida",
        ge=0
    )

    approved: int = Field(
        default=0,
        description="Cantidad aprobada en control de calidad",
        ge=0
    )

    rejected: int = Field(
        default=0,
        description="Cantidad rechazada en control de calidad",
        ge=0
    )

    # ════════════════════════════════════════════════════════════════════
    # ESTADO Y LÍNEA
    # ════════════════════════════════════════════════════════════════════

    status: ProductionOrderStatus = Field(
        default=ProductionOrderStatus.PENDING,
        description="Estado actual de la orden",
        index=True
    )

    production_line: Optional[int] = Field(
        default=None,
        description="Línea de producción asignada (1, 2, 3)",
        ge=1,
        le=3
    )

    # ════════════════════════════════════════════════════════════════════
    # RESPONSABLE
    # ════════════════════════════════════════════════════════════════════

    responsible: Optional[str] = Field(
        default=None,
        description="ID del empleado responsable"
    )

    # ════════════════════════════════════════════════════════════════════
    # FECHAS
    # ════════════════════════════════════════════════════════════════════

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación de la orden",
        index=True
    )

    start_date: Optional[datetime] = Field(
        default=None,
        description="Fecha de inicio de producción"
    )

    end_date: Optional[datetime] = Field(
        default=None,
        description="Fecha de finalización"
    )

    estimated_completion: Optional[datetime] = Field(
        default=None,
        description="Fecha estimada de finalización"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )

    # ════════════════════════════════════════════════════════════════════
    # LOTES (BATCHES)
    # ════════════════════════════════════════════════════════════════════

    batches: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lotes de producción (cupones de trabajo)"
    )
    # Ejemplo:
    # [
    #     {
    #         "batch_number": 1,
    #         "quantity": 250,
    #         "workstation": 1,
    #         "operator": "EMP001",
    #         "start_date": "2025-01-15T08:00:00Z",
    #         "end_date": "2025-01-15T12:00:00Z",
    #         "produced": 250,
    #         "status": "completed"
    #     }
    # ]

    total_batches: int = Field(
        default=0,
        description="Total de lotes planificados"
    )

    # ════════════════════════════════════════════════════════════════════
    # ETIQUETAS
    # ════════════════════════════════════════════════════════════════════

    labels_required: Optional[Dict[str, int]] = Field(
        default_factory=dict,
        description="Etiquetas necesarias por tipo"
    )
    # Ejemplo:
    # {
    #     "label_24": 1000,
    #     "label_48": 500,
    #     "label_80": 1000,
    #     "label_96": 500
    # }

    # ════════════════════════════════════════════════════════════════════
    # DETALLES Y NOTAS
    # ════════════════════════════════════════════════════════════════════

    notes: Optional[str] = Field(
        default=None,
        description="Notas y detalles adicionales de la orden",
        max_length=500
    )

    priority: Optional[str] = Field(
        default="normal",
        description="Prioridad de la orden (low, normal, high, critical)"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA
    # ════════════════════════════════════════════════════════════════════

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Campos adicionales personalizados"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "production_orders"
        indexes = [
            "order_number",  # Unique
            "status",
            "production_line",
            "created_at",
            [("status", 1), ("production_line", 1)],
            [("created_at", -1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # VALIDADORES
    # ════════════════════════════════════════════════════════════════════

    @validator('order_number')
    def validate_order_number(cls, v):
        """Valida el formato del número de orden"""
        return v.strip().upper()

    @validator('priority')
    def validate_priority(cls, v):
        """Valida la prioridad"""
        allowed = ["low", "normal", "high", "critical"]
        if v and v.lower() not in allowed:
            raise ValueError(f"Priority must be one of: {allowed}")
        return v.lower() if v else "normal"

    # ════════════════════════════════════════════════════════════════════
    # PROPIEDADES
    # ════════════════════════════════════════════════════════════════════

    @property
    def completion_percentage(self) -> float:
        """Retorna el porcentaje de completitud"""
        if self.quantity == 0:
            return 0.0
        return (self.produced / self.quantity) * 100

    @property
    def quality_rate(self) -> float:
        """Retorna la tasa de calidad (aprobados/producidos)"""
        if self.produced == 0:
            return 0.0
        return (self.approved / self.produced) * 100

    @property
    def rejection_rate(self) -> float:
        """Retorna la tasa de rechazo"""
        if self.produced == 0:
            return 0.0
        return (self.rejected / self.produced) * 100

    @property
    def is_completed(self) -> bool:
        """Verifica si la orden está completada"""
        return self.status == ProductionOrderStatus.COMPLETED

    @property
    def is_active(self) -> bool:
        """Verifica si la orden está activa"""
        return self.status in [
            ProductionOrderStatus.PENDING,
            ProductionOrderStatus.IN_PROGRESS,
            ProductionOrderStatus.PAUSED
        ]

    @property
    def pending_quantity(self) -> int:
        """Retorna la cantidad pendiente de producir"""
        return max(0, self.quantity - self.produced)

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ════════════════════════════════════════════════════════════════════

    async def start_production(self, operator: Optional[str] = None):
        """Inicia la producción de la orden"""
        self.status = ProductionOrderStatus.IN_PROGRESS
        self.start_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        await self.save()

    async def complete_production(self, operator: Optional[str] = None):
        """Marca la orden como completada"""
        self.status = ProductionOrderStatus.COMPLETED
        self.end_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        await self.save()

    async def add_batch(
        self,
        batch_number: int,
        quantity: int,
        workstation: int,
        operator: Optional[str] = None
    ):
        """Añade un nuevo lote a la orden"""
        batch = {
            "batch_number": batch_number,
            "quantity": quantity,
            "workstation": workstation,
            "operator": operator,
            "start_date": datetime.utcnow(),
            "end_date": None,
            "produced": 0,
            "status": "in_progress"
        }

        self.batches.append(batch)
        self.total_batches = len(self.batches)
        self.updated_at = datetime.utcnow()
        await self.save()

    async def update_production_count(self, produced: int, approved: int, rejected: int):
        """Actualiza los contadores de producción"""
        self.produced = produced
        self.approved = approved
        self.rejected = rejected
        self.updated_at = datetime.utcnow()
        await self.save()

    async def increment_produced(self, quantity: int = 1):
        """Incrementa el contador de producidos"""
        self.produced += quantity
        self.updated_at = datetime.utcnow()
        await self.save()

    async def increment_approved(self, quantity: int = 1):
        """Incrementa el contador de aprobados"""
        self.approved += quantity
        self.updated_at = datetime.utcnow()
        await self.save()

    async def increment_rejected(self, quantity: int = 1):
        """Incrementa el contador de rechazados"""
        self.rejected += quantity
        self.updated_at = datetime.utcnow()
        await self.save()

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def find_by_order_number(order_number: str) -> Optional["ProductionOrder"]:
        """Busca una orden por su número"""
        return await ProductionOrder.find_one(
            ProductionOrder.order_number == order_number.strip().upper()
        )

    @staticmethod
    async def find_active_orders():
        """Retorna todas las órdenes activas"""
        return await ProductionOrder.find(
            ProductionOrder.status.in_([
                ProductionOrderStatus.PENDING,
                ProductionOrderStatus.IN_PROGRESS,
                ProductionOrderStatus.PAUSED
            ])
        ).to_list()

    @staticmethod
    async def find_by_line(production_line: int):
        """Retorna órdenes de una línea específica"""
        return await ProductionOrder.find(
            ProductionOrder.production_line == production_line
        ).sort("-created_at").to_list()

    @staticmethod
    async def get_production_stats(start_date: datetime, end_date: datetime) -> dict:
        """
        Retorna estadísticas de producción en un rango de fechas
        """
        orders = await ProductionOrder.find(
            ProductionOrder.created_at >= start_date,
            ProductionOrder.created_at <= end_date
        ).to_list()

        total_orders = len(orders)
        total_quantity = sum(o.quantity for o in orders)
        total_produced = sum(o.produced for o in orders)
        total_approved = sum(o.approved for o in orders)
        total_rejected = sum(o.rejected for o in orders)

        return {
            "total_orders": total_orders,
            "total_quantity": total_quantity,
            "total_produced": total_produced,
            "total_approved": total_approved,
            "total_rejected": total_rejected,
            "completion_rate": (total_produced / total_quantity * 100) if total_quantity > 0 else 0,
            "quality_rate": (total_approved / total_produced * 100) if total_produced > 0 else 0,
            "rejection_rate": (total_rejected / total_produced * 100) if total_produced > 0 else 0
        }
