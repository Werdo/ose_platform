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
from .import_record import ImportRecord, ImportStatus
from .public_user import PublicUser, PublicUserStatus
from .transform_template import TransformTemplate, DestinationType, FieldType
from .import_job import ImportJob, JobStatus
from .sales_ticket import SalesTicket, TicketStatus as SalesTicketStatus
from .invoice import Invoice, InvoiceStatus
from .invoice_config import InvoiceConfig
from .series_notification import SeriesNotification
from .pallet import Pallet

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
    "ImportRecord",
    "PublicUser",
    "TransformTemplate",
    "ImportJob",
    "SalesTicket",
    "Invoice",
    "InvoiceConfig",
    "SeriesNotification",
    "Pallet",

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
    "ImportStatus",
    "PublicUserStatus",
    "DestinationType",
    "FieldType",
    "JobStatus",
    "SalesTicketStatus",
    "InvoiceStatus",
]
