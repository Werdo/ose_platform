"""
OSE Platform - Schemas
Pydantic schemas para request/response de la API
"""

# Common
from .common import (
    SuccessResponse,
    ErrorResponse,
    ErrorDetail,
    MessageResponse,
    PaginationParams,
    PaginationMeta,
    PaginatedResponse,
    SortParams,
    DateRangeFilter,
    FileInfo,
    FileUploadResponse,
    BulkOperationResult,
    HealthStatus,
    StatisticsResponse,
)

# Auth
from .auth import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    EmployeePublic,
    EmployeeProfile,
    CurrentUserResponse,
    LogoutRequest,
    TokenValidationResponse,
)

# Employee
from .employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeSummary,
    EmployeeFilter,
    EmployeeStatistics,
)

# Device
from .device import (
    DeviceCreate,
    DeviceBulkCreate,
    DeviceUpdate,
    DeviceStatusChange,
    DeviceResponse,
    DeviceSummary,
    DeviceFilter,
    DeviceShipping,
    DeviceAssignment,
    DeviceStatistics,
    DeviceHistory,
)

# Production
from .production import (
    ProductionOrderCreate,
    ProductionOrderUpdate,
    ProductionOrderResponse,
    ProductionOrderSummary,
    BatchCreate,
    BatchUpdate,
    ProductionStart,
    ProductionIncrement,
    ProductionOrderFilter,
    ProductionStatistics,
)

# Ticket
from .ticket import (
    TicketCreate,
    TicketUpdate,
    TicketComment,
    TicketResponse,
    TicketSummary,
    TicketFilter,
    TicketStatistics,
)

# RMA
from .rma import (
    RMACreate,
    RMAUpdate,
    RMAInspection,
    RMAResponse,
    RMASummary,
    RMAFilter,
    RMAStatistics,
)

# Customer
from .customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerSummary,
    CustomerFilter,
    CustomerStatistics,
)

# Setting
from .setting import (
    SettingCreate,
    SettingUpdate,
    SettingResponse,
    EmailConfig,
    EmailConfigResponse,
    EmailTestRequest,
    EmailTestResponse,
    SystemConfigResponse,
    FeatureToggle,
    SettingsByCategoryResponse,
    BulkSettingsUpdate,
)

__all__ = [
    # Common
    "SuccessResponse",
    "ErrorResponse",
    "ErrorDetail",
    "MessageResponse",
    "PaginationParams",
    "PaginationMeta",
    "PaginatedResponse",
    "SortParams",
    "DateRangeFilter",
    "FileInfo",
    "FileUploadResponse",
    "BulkOperationResult",
    "HealthStatus",
    "StatisticsResponse",

    # Auth
    "LoginRequest",
    "LoginResponse",
    "TokenResponse",
    "RefreshTokenRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "PasswordChangeRequest",
    "EmployeePublic",
    "EmployeeProfile",
    "CurrentUserResponse",
    "LogoutRequest",
    "TokenValidationResponse",

    # Employee
    "EmployeeCreate",
    "EmployeeUpdate",
    "EmployeeResponse",
    "EmployeeSummary",
    "EmployeeFilter",
    "EmployeeStatistics",

    # Device
    "DeviceCreate",
    "DeviceBulkCreate",
    "DeviceUpdate",
    "DeviceStatusChange",
    "DeviceResponse",
    "DeviceSummary",
    "DeviceFilter",
    "DeviceShipping",
    "DeviceAssignment",
    "DeviceStatistics",
    "DeviceHistory",

    # Production
    "ProductionOrderCreate",
    "ProductionOrderUpdate",
    "ProductionOrderResponse",
    "ProductionOrderSummary",
    "BatchCreate",
    "BatchUpdate",
    "ProductionStart",
    "ProductionIncrement",
    "ProductionOrderFilter",
    "ProductionStatistics",

    # Ticket
    "TicketCreate",
    "TicketUpdate",
    "TicketComment",
    "TicketResponse",
    "TicketSummary",
    "TicketFilter",
    "TicketStatistics",

    # RMA
    "RMACreate",
    "RMAUpdate",
    "RMAInspection",
    "RMAResponse",
    "RMASummary",
    "RMAFilter",
    "RMAStatistics",

    # Customer
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse",
    "CustomerSummary",
    "CustomerFilter",
    "CustomerStatistics",

    # Setting
    "SettingCreate",
    "SettingUpdate",
    "SettingResponse",
    "EmailConfig",
    "EmailConfigResponse",
    "EmailTestRequest",
    "EmailTestResponse",
    "SystemConfigResponse",
    "FeatureToggle",
    "SettingsByCategoryResponse",
    "BulkSettingsUpdate",
]
