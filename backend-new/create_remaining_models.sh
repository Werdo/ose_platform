#!/bin/bash
# Script para crear los modelos restantes del backend

cd "C:\Users\pedro\claude-code-workspace\OSE-Platform\backend-new\platform\models"

# Crear __init__.py
cat > __init__.py << 'PYEOF'
"""
OSE Platform - Data Models
Modelos Beanie para MongoDB
"""

from .device import Device, EstadoDispositivo
from .device_event import DeviceEvent
from .movimiento import Movimiento, TipoMovimiento
from .production_order import ProductionOrder, ProductionOrderStatus
from .employee import Employee, EmployeeRole, EmployeeStatus
from .customer import Customer, CustomerType, CustomerStatus
from .quality_control import QualityControl, QCResult
from .service_ticket import ServiceTicket, TicketStatus, TicketPriority
from .rma_case import RMACase, RMAStatus, RMAType
from .inventory import InventoryItem, InventoryCategory, InventoryStatus
from .metric import Metric, MetricType, MetricPeriod
from .setting import SystemSetting, SettingCategory

__all__ = [
    # Models
    "Device",
    "DeviceEvent",
    "Movimiento",
    "ProductionOrder",
    "Employee",
    "Customer",
    "QualityControl",
    "ServiceTicket",
    "RMACase",
    "InventoryItem",
    "Metric",
    "SystemSetting",
    
    # Enums
    "EstadoDispositivo",
    "TipoMovimiento",
    "ProductionOrderStatus",
    "EmployeeRole",
    "EmployeeStatus",
    "CustomerType",
    "CustomerStatus",
    "QCResult",
    "TicketStatus",
    "TicketPriority",
    "RMAStatus",
    "RMAType",
    "InventoryCategory",
    "InventoryStatus",
    "MetricType",
    "MetricPeriod",
    "SettingCategory",
]
PYEOF

echo "Modelos base creados"
