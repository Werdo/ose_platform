"""
OSE Platform - Authentication Dependencies
Dependencias para inyección en endpoints protegidos
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError

from app.models.employee import Employee, EmployeeRole, EmployeeStatus
from app.utils.security import verify_token
import logging

logger = logging.getLogger(__name__)

# Bearer token scheme
security = HTTPBearer()


# ════════════════════════════════════════════════════════════════════════
# DEPENDENCIAS DE AUTENTICACIÓN
# ════════════════════════════════════════════════════════════════════════

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Employee:
    """
    Obtiene el usuario actual desde el token JWT

    Args:
        credentials: Token Bearer automáticamente extraído del header

    Returns:
        Employee: Usuario autenticado

    Raises:
        HTTPException 401: Si el token es inválido o el usuario no existe
    """
    token = credentials.credentials

    # Verificar token
    payload = verify_token(token, token_type="access")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtener user_id del token
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buscar usuario en BD
    try:
        from beanie import PydanticObjectId
        user = await Employee.get(PydanticObjectId(user_id))
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que el usuario esté activo
    if user.status != EmployeeStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.status.value}"
        )

    return user


async def get_current_active_user(
    current_user: Employee = Depends(get_current_user)
) -> Employee:
    """
    Verifica que el usuario esté activo
    (Redundante con get_current_user pero útil para claridad)
    """
    return current_user


# ════════════════════════════════════════════════════════════════════════
# DEPENDENCIAS DE ROLES
# ════════════════════════════════════════════════════════════════════════

def require_role(*required_roles: EmployeeRole):
    """
    Factory para crear dependencias que requieren roles específicos

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: Employee = Depends(require_role(EmployeeRole.ADMIN))):
            ...
    """
    async def role_checker(current_user: Employee = Depends(get_current_user)) -> Employee:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[r.value for r in required_roles]}"
            )
        return current_user

    return role_checker


# Atajos para roles comunes
require_admin = require_role(EmployeeRole.ADMIN)
require_supervisor = require_role(EmployeeRole.ADMIN, EmployeeRole.SUPERVISOR)
require_quality_inspector = require_role(
    EmployeeRole.ADMIN,
    EmployeeRole.SUPERVISOR,
    EmployeeRole.QUALITY_INSPECTOR
)


# ════════════════════════════════════════════════════════════════════════
# DEPENDENCIAS DE PERMISOS GRANULARES
# ════════════════════════════════════════════════════════════════════════

def require_permission(permission_key: str):
    """
    Factory para crear dependencias que requieren permisos específicos

    Args:
        permission_key: Clave del permiso en el dict permissions del Employee

    Usage:
        @router.post("/production")
        async def create_order(
            user: Employee = Depends(require_permission("production_lines"))
        ):
            ...
    """
    async def permission_checker(
        current_user: Employee = Depends(get_current_user)
    ) -> Employee:
        # Admin siempre tiene todos los permisos
        if current_user.role == EmployeeRole.ADMIN:
            return current_user

        # Verificar permiso específico
        if not current_user.permissions.get(permission_key, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission_key}"
            )

        return current_user

    return permission_checker


# Atajos para permisos comunes
require_production_access = require_permission("production_lines")
require_quality_access = require_permission("quality_control")
require_warehouse_access = require_permission("warehouse")
require_tickets_access = require_permission("support_tickets")
require_rma_access = require_permission("rma_cases")
require_customer_access = require_permission("customer_management")


# ════════════════════════════════════════════════════════════════════════
# DEPENDENCIAS DE ACCESO A LÍNEAS/ESTACIONES
# ════════════════════════════════════════════════════════════════════════

async def verify_production_line_access(
    production_line: str,
    current_user: Employee = Depends(get_current_user)
) -> Employee:
    """
    Verifica que el usuario tenga acceso a una línea de producción específica

    Args:
        production_line: ID o nombre de la línea de producción
        current_user: Usuario actual

    Returns:
        Employee si tiene acceso

    Raises:
        HTTPException 403: Si no tiene acceso
    """
    # Admin siempre tiene acceso
    if current_user.role == EmployeeRole.ADMIN:
        return current_user

    # Verificar permiso general
    if not current_user.permissions.get("production_lines", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to production lines"
        )

    # Verificar línea específica (si aplica)
    allowed_lines = current_user.permissions.get("allowed_production_lines", [])
    if allowed_lines and production_line not in allowed_lines:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No access to production line: {production_line}"
        )

    return current_user


async def verify_station_access(
    station: str,
    current_user: Employee = Depends(get_current_user)
) -> Employee:
    """
    Verifica que el usuario tenga acceso a una estación específica

    Args:
        station: ID o nombre de la estación
        current_user: Usuario actual

    Returns:
        Employee si tiene acceso

    Raises:
        HTTPException 403: Si no tiene acceso
    """
    # Admin siempre tiene acceso
    if current_user.role == EmployeeRole.ADMIN:
        return current_user

    # Verificar permiso general
    if not current_user.permissions.get("stations", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to stations"
        )

    # Verificar estación específica (si aplica)
    allowed_stations = current_user.permissions.get("allowed_stations", [])
    if allowed_stations and station not in allowed_stations:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No access to station: {station}"
        )

    return current_user


# ════════════════════════════════════════════════════════════════════════
# DEPENDENCIAS OPCIONALES
# ════════════════════════════════════════════════════════════════════════

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Employee]:
    """
    Obtiene el usuario actual si hay token, None si no
    Útil para endpoints públicos que cambian comportamiento si hay auth
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


# ════════════════════════════════════════════════════════════════════════
# HELPERS DE VERIFICACIÓN
# ════════════════════════════════════════════════════════════════════════

def is_admin(user: Employee) -> bool:
    """Verifica si el usuario es administrador"""
    return user.role == EmployeeRole.ADMIN


def is_supervisor(user: Employee) -> bool:
    """Verifica si el usuario es supervisor o admin"""
    return user.role in [EmployeeRole.ADMIN, EmployeeRole.SUPERVISOR]


def has_permission(user: Employee, permission_key: str) -> bool:
    """Verifica si el usuario tiene un permiso específico"""
    if user.role == EmployeeRole.ADMIN:
        return True
    return user.permissions.get(permission_key, False)


def can_access_production_line(user: Employee, production_line: str) -> bool:
    """Verifica si el usuario puede acceder a una línea de producción"""
    if user.role == EmployeeRole.ADMIN:
        return True

    if not user.permissions.get("production_lines", False):
        return False

    allowed_lines = user.permissions.get("allowed_production_lines", [])
    if not allowed_lines:
        return True  # Sin restricciones específicas

    return production_line in allowed_lines
