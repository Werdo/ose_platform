"""
OSE Platform - Authentication Dependencies
Dependencies de FastAPI para autenticación y autorización
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from app.auth.jwt_handler import jwt_handler
from app.models.employee import Employee, EmployeeRole


# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Employee:
    """
    Dependency que obtiene el usuario actual desde el token JWT

    Args:
        credentials: Credenciales HTTP Bearer (token)

    Returns:
        Employee: Usuario autenticado

    Raises:
        HTTPException: Si el token no es válido o el usuario no existe
    """
    token = credentials.credentials

    # Verificar token
    payload = jwt_handler.verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtener ID del usuario
    user_id = payload.get("sub")
    employee_id = payload.get("employee_id")

    if not user_id or not employee_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Buscar usuario en la base de datos
    employee = await Employee.find_by_employee_id(employee_id)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que el usuario esté activo
    if not employee.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )

    return employee


async def get_current_active_user(
    current_user: Employee = Depends(get_current_user)
) -> Employee:
    """
    Dependency que verifica que el usuario esté activo

    Args:
        current_user: Usuario actual

    Returns:
        Employee: Usuario activo

    Raises:
        HTTPException: Si el usuario no está activo
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )

    return current_user


async def require_admin(
    current_user: Employee = Depends(get_current_active_user)
) -> Employee:
    """
    Dependency que requiere que el usuario sea admin

    Args:
        current_user: Usuario actual

    Returns:
        Employee: Usuario admin

    Raises:
        HTTPException: Si el usuario no es admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador"
        )

    return current_user


async def require_super_admin(
    current_user: Employee = Depends(get_current_active_user)
) -> Employee:
    """
    Dependency que requiere que el usuario sea super admin

    Args:
        current_user: Usuario actual

    Returns:
        Employee: Usuario super admin

    Raises:
        HTTPException: Si el usuario no es super admin
    """
    if current_user.role != EmployeeRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de super administrador"
        )

    return current_user


def require_permission(permission: str):
    """
    Factory que crea una dependency que requiere un permiso específico

    Args:
        permission: Nombre del permiso requerido

    Returns:
        Dependency function
    """
    async def permission_dependency(
        current_user: Employee = Depends(get_current_active_user)
    ) -> Employee:
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene permiso: {permission}"
            )
        return current_user

    return permission_dependency


def require_any_permission(*permissions: str):
    """
    Factory que crea una dependency que requiere AL MENOS uno de los permisos

    Args:
        *permissions: Lista de permisos (requiere tener al menos uno)

    Returns:
        Dependency function
    """
    async def permission_dependency(
        current_user: Employee = Depends(get_current_active_user)
    ) -> Employee:
        has_permission = any(
            current_user.has_permission(perm) for perm in permissions
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No tiene ninguno de los permisos requeridos: {', '.join(permissions)}"
            )

        return current_user

    return permission_dependency


def require_all_permissions(*permissions: str):
    """
    Factory que crea una dependency que requiere TODOS los permisos

    Args:
        *permissions: Lista de permisos (requiere tenerlos todos)

    Returns:
        Dependency function
    """
    async def permission_dependency(
        current_user: Employee = Depends(get_current_active_user)
    ) -> Employee:
        missing_permissions = [
            perm for perm in permissions
            if not current_user.has_permission(perm)
        ]

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Faltan permisos: {', '.join(missing_permissions)}"
            )

        return current_user

    return permission_dependency


def require_role(*roles: EmployeeRole):
    """
    Factory que crea una dependency que requiere uno de los roles especificados

    Args:
        *roles: Lista de roles permitidos

    Returns:
        Dependency function
    """
    async def role_dependency(
        current_user: Employee = Depends(get_current_active_user)
    ) -> Employee:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Rol no autorizado. Se requiere: {', '.join([r.value for r in roles])}"
            )

        return current_user

    return role_dependency


# Dependency opcional (no lanza error si no hay token)
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[Employee]:
    """
    Dependency opcional que obtiene el usuario si hay token, None si no

    Args:
        credentials: Credenciales HTTP Bearer (opcional)

    Returns:
        Employee o None
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
