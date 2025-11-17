"""
OSE Platform - Metric Model
Modelo para almacenar métricas y KPIs agregados
"""

from beanie import Document
from pydantic import Field
from typing import Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


class MetricType(str, Enum):
    """Tipos de métricas"""
    # Producción
    PRODUCTION_DAILY = "production_daily"
    PRODUCTION_WEEKLY = "production_weekly"
    PRODUCTION_MONTHLY = "production_monthly"
    PRODUCTION_PER_LINE = "production_per_line"
    PRODUCTION_PER_OPERATOR = "production_per_operator"
    PRODUCTION_TIME_AVG = "production_time_avg"

    # Calidad
    QUALITY_RATE = "quality_rate"
    REJECTION_RATE = "rejection_rate"
    FIRST_PASS_YIELD = "first_pass_yield"
    DEFECT_RATE = "defect_rate"
    REWORK_RATE = "rework_rate"

    # Post-Venta
    TICKET_COUNT = "ticket_count"
    TICKET_RESOLUTION_TIME_AVG = "ticket_resolution_time_avg"
    TICKET_OPEN = "ticket_open"
    TICKET_CLOSED = "ticket_closed"
    RMA_RATE = "rma_rate"
    RMA_COUNT = "rma_count"

    # Satisfacción
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    NPS_SCORE = "nps_score"

    # Garantía
    WARRANTY_CLAIMS = "warranty_claims"
    WARRANTY_COST_AVG = "warranty_cost_avg"

    # Inventario
    STOCK_LEVEL = "stock_level"
    STOCK_TURNOVER = "stock_turnover"

    # Otros
    CUSTOM = "custom"


class MetricPeriod(str, Enum):
    """Períodos de métricas"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class Metric(Document):
    """
    Métrica/KPI
    Almacena valores agregados para análisis y reportes
    """

    # ════════════════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ════════════════════════════════════════════════════════════════════

    metric_type: MetricType = Field(description="Tipo de métrica")

    metric_name: Optional[str] = Field(
        default=None,
        description="Nombre personalizado de la métrica"
    )

    # ════════════════════════════════════════════════════════════════════
    # PERÍODO
    # ════════════════════════════════════════════════════════════════════

    period: MetricPeriod = Field(
        default=MetricPeriod.DAILY,
        description="Período de la métrica"
    )

    metric_date: date = Field(description="Fecha de la métrica")

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp exacto"
    )

    # ════════════════════════════════════════════════════════════════════
    # VALOR
    # ════════════════════════════════════════════════════════════════════

    value: float = Field(description="Valor de la métrica")

    unit: Optional[str] = Field(
        default=None,
        description="Unidad de medida (unidades, %, horas, etc.)"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONTEXTO
    # ════════════════════════════════════════════════════════════════════

    production_order: Optional[str] = Field(
        default=None,
        description="Orden de producción relacionada"
    )

    production_line: Optional[str] = Field(
        default=None,
        description="Línea de producción relacionada"
    )

    operator: Optional[str] = Field(
        default=None,
        description="Operador relacionado"
    )

    customer_id: Optional[str] = Field(
        default=None,
        description="Cliente relacionado"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA
    # ════════════════════════════════════════════════════════════════════

    dimensions: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Dimensiones adicionales para filtrado"
    )
    # Ejemplo:
    # {
    #     "shift": "morning",
    #     "sku": "1001",
    #     "region": "EU"
    # }

    data: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Datos adicionales de la métrica"
    )
    # Ejemplo para quality_rate:
    # {
    #     "total_inspections": 100,
    #     "passed": 95,
    #     "failed": 5,
    #     "pass_rate": 95.0
    # }

    # ════════════════════════════════════════════════════════════════════
    # AUDITORÍA
    # ════════════════════════════════════════════════════════════════════

    calculated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Cuándo se calculó la métrica"
    )

    calculated_by: Optional[str] = Field(
        default="system",
        description="Quién/qué calculó la métrica (system, job_id, user_id)"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "metrics"
        indexes = [
            "metric_type",
            "period",
            "metric_date",
            "production_order",
            "production_line",
            [("metric_type", 1), ("period", 1), ("metric_date", -1)],
            [("metric_type", 1), ("metric_date", -1)],
            [("production_line", 1), ("metric_date", -1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def get_metric(
        metric_type: MetricType,
        date_value: date,
        period: MetricPeriod = MetricPeriod.DAILY,
        **filters
    ) -> Optional["Metric"]:
        """Obtiene una métrica específica"""
        query = {
            "metric_type": metric_type,
            "period": period,
            "metric_date": date_value
        }
        query.update(filters)

        return await Metric.find_one(query)

    @staticmethod
    async def get_time_series(
        metric_type: MetricType,
        start_date: date,
        end_date: date,
        period: MetricPeriod = MetricPeriod.DAILY,
        **filters
    ):
        """Obtiene una serie temporal de métricas"""
        query = {
            "metric_type": metric_type,
            "period": period,
            "metric_date": {"$gte": start_date, "$lte": end_date}
        }
        query.update(filters)

        return await Metric.find(query).sort("+metric_date").to_list()

    @staticmethod
    async def record_metric(
        metric_type: MetricType,
        value: float,
        date_value: date,
        period: MetricPeriod = MetricPeriod.DAILY,
        unit: Optional[str] = None,
        **kwargs
    ) -> "Metric":
        """Registra o actualiza una métrica"""
        # Buscar si ya existe
        existing = await Metric.get_metric(
            metric_type=metric_type,
            date_value=date_value,
            period=period,
            **{k: v for k, v in kwargs.items() if k in ["production_order", "production_line", "operator", "customer_id"]}
        )

        if existing:
            # Actualizar
            existing.value = value
            existing.calculated_at = datetime.utcnow()
            if unit:
                existing.unit = unit
            for key, val in kwargs.items():
                if hasattr(existing, key):
                    setattr(existing, key, val)
            await existing.save()
            return existing
        else:
            # Crear nuevo
            metric_data = {
                "metric_type": metric_type,
                "period": period,
                "metric_date": date_value,
                "value": value,
                "unit": unit,
                **kwargs
            }
            metric = Metric(**metric_data)
            await metric.insert()
            return metric
