"""
OSE Platform - Data Models
Modelos Beanie para MongoDB
"""

from .device import Device, DeviceStatus
from .production_order import ProductionOrder, ProductionOrderStatus
from .device_event import DeviceEvent, EventType
from .service_ticket import ServiceTicket, TicketStatus, TicketPriority
from .rma_case import RMACase, RMAStatus, RMAType
from .customer import Customer, CustomerType, CustomerStatus
from .employee import Employee, EmployeeRole, EmployeeStatus
from .quality_control import QualityControl, QCResult
from .inventory import InventoryItem, InventoryCategory, InventoryStatus
from .metric import Metric, MetricType, MetricPeriod
from .setting import SystemSetting, SettingCategory
from .series_notification import SeriesNotification, CSVFormat

__all__ = [
    # Models
    "Device",
    "ProductionOrder",
    "DeviceEvent",
    "ServiceTicket",
    "RMACase",
    "Customer",
    "Employee",
    "QualityControl",
    "InventoryItem",
    "Metric",
    "SystemSetting",
    "SeriesNotification",

    # Enums
    "DeviceStatus",
    "ProductionOrderStatus",
    "EventType",
    "TicketStatus",
    "TicketPriority",
    "RMAStatus",
    "RMAType",
    "CustomerType",
    "CustomerStatus",
    "EmployeeRole",
    "EmployeeStatus",
    "QCResult",
    "InventoryCategory",
    "InventoryStatus",
    "MetricType",
    "MetricPeriod",
    "SettingCategory",
    "CSVFormat",
]
