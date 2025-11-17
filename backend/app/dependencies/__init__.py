"""
OSE Platform - Dependencies
Dependencias de FastAPI para inyección en endpoints
"""

from .auth import (
    get_current_user,
    get_current_active_user,
    get_current_user_optional,
    require_role,
    require_admin,
    require_supervisor,
    require_quality_inspector,
    require_permission,
    require_production_access,
    require_quality_access,
    require_warehouse_access,
    require_tickets_access,
    require_rma_access,
    require_customer_access,
    verify_production_line_access,
    verify_station_access,
    is_admin,
    is_supervisor,
    has_permission,
    can_access_production_line,
)

__all__ = [
    # Usuario actual
    "get_current_user",
    "get_current_active_user",
    "get_current_user_optional",

    # Roles
    "require_role",
    "require_admin",
    "require_supervisor",
    "require_quality_inspector",

    # Permisos
    "require_permission",
    "require_production_access",
    "require_quality_access",
    "require_warehouse_access",
    "require_tickets_access",
    "require_rma_access",
    "require_customer_access",

    # Verificaciones específicas
    "verify_production_line_access",
    "verify_station_access",

    # Helpers
    "is_admin",
    "is_supervisor",
    "has_permission",
    "can_access_production_line",
]
