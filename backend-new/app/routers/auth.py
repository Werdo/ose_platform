"""
OSE Platform - Authentication Router
Rutas para autenticación (login, logout, refresh, etc.)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    ChangePasswordRequest
)
from app.models.employee import Employee
from app.auth.jwt_handler import jwt_handler
from app.dependencies.auth import get_current_active_user
from app.utils.security import verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Login - Autentica un usuario y retorna tokens JWT + información del usuario

    - **identifier**: Employee ID o email
    - **password**: Contraseña

    Returns:
        LoginResponse: Access token, refresh token e información del usuario
    """
    # Autenticar usuario
    employee = await Employee.authenticate(
        identifier=credentials.identifier,
        password=credentials.password
    )

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Registrar login exitoso
    await employee.record_login(success=True)

    # Crear tokens
    tokens = jwt_handler.create_tokens_for_user(
        user_id=str(employee.id),
        employee_id=employee.employee_id,
        role=employee.role.value,
        permissions=employee.permissions
    )

    # Guardar refresh token en la BD
    from datetime import timedelta
    refresh_expires = datetime.utcnow() + timedelta(days=7)
    await employee.set_refresh_token(
        token=tokens["refresh_token"],
        expires=refresh_expires
    )

    # Crear respuesta con tokens y usuario
    return LoginResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        expires_in=tokens["expires_in"],
        user=UserResponse(
            id=str(employee.id),
            employee_id=employee.employee_id,
            name=employee.name,
            surname=employee.surname,
            email=employee.email,
            role=employee.role.value,
            permissions=employee.permissions,
            last_login=employee.last_login
        )
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh Token - Genera un nuevo access token usando un refresh token válido

    - **refresh_token**: Refresh token válido

    Returns:
        TokenResponse: Nuevo access token
    """
    # Verificar refresh token
    new_tokens = jwt_handler.refresh_access_token(request.refresh_token)

    if not new_tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar que el refresh token coincida con el almacenado
    payload = jwt_handler.verify_token(request.refresh_token)
    employee_id = payload.get("employee_id")

    employee = await Employee.find_by_employee_id(employee_id)

    if not employee or employee.refresh_token != request.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verificar expiración del refresh token almacenado
    if employee.refresh_token_expires and datetime.utcnow() > employee.refresh_token_expires:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Crear nuevos tokens completos (con permisos actualizados)
    tokens = jwt_handler.create_tokens_for_user(
        user_id=str(employee.id),
        employee_id=employee.employee_id,
        role=employee.role.value,
        permissions=employee.permissions
    )

    # Actualizar refresh token en la BD
    from datetime import timedelta
    refresh_expires = datetime.utcnow() + timedelta(days=7)
    await employee.set_refresh_token(
        token=tokens["refresh_token"],
        expires=refresh_expires
    )

    return tokens


@router.post("/logout")
async def logout(current_user: Employee = Depends(get_current_active_user)):
    """
    Logout - Invalida el refresh token del usuario

    Requiere autenticación.
    """
    # Limpiar refresh token
    await current_user.clear_refresh_token()

    return {"message": "Logout exitoso"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Obtiene información del usuario autenticado

    Requiere autenticación.

    Returns:
        UserResponse: Información del usuario
    """
    return UserResponse(
        id=str(current_user.id),
        employee_id=current_user.employee_id,
        name=current_user.name,
        surname=current_user.surname,
        email=current_user.email,
        role=current_user.role.value,
        permissions=current_user.permissions,
        last_login=current_user.last_login
    )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Cambia la contraseña del usuario autenticado

    - **current_password**: Contraseña actual
    - **new_password**: Nueva contraseña
    - **confirm_password**: Confirmación de nueva contraseña

    Requiere autenticación.
    """
    # Verificar contraseña actual
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )

    # Validar fortaleza de nueva contraseña
    from app.utils.security import validate_password_strength
    is_valid, message = validate_password_strength(request.new_password)

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )

    # Cambiar contraseña
    current_user.set_password(request.new_password)
    current_user.updated_at = datetime.utcnow()
    await current_user.save()

    # Limpiar refresh token (forzar re-login)
    await current_user.clear_refresh_token()

    return {"message": "Contraseña cambiada exitosamente. Por favor inicie sesión nuevamente."}


@router.get("/verify-token")
async def verify_token_endpoint(
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Verifica si el token es válido

    Requiere autenticación.

    Returns:
        dict: Información básica si el token es válido
    """
    return {
        "valid": True,
        "employee_id": current_user.employee_id,
        "role": current_user.role.value
    }


# ════════════════════════════════════════════════════════════════════════
# GESTIÓN DE EMPLEADOS (solo para super_admin)
# ════════════════════════════════════════════════════════════════════════

print("DEBUG: Loading employee management endpoints...")

@router.get("/employees")
async def list_employees(
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Lista todos los empleados del sistema

    Requiere rol super_admin
    """
    # Verificar permisos
    if current_user.role.value != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver la lista de empleados"
        )

    # Obtener todos los empleados
    employees = await Employee.find_all().to_list()

    # Convertir a dict para retornar
    return [
        {
            "_id": str(emp.id),
            "employee_id": emp.employee_id,
            "name": emp.name,
            "surname": emp.surname,
            "email": emp.email,
            "role": emp.role.value,
            "status": emp.status.value,
            "permissions": emp.permissions,
            "last_login": emp.last_login
        }
        for emp in employees
    ]


@router.put("/employees/{employee_id}")
async def update_employee(
    employee_id: str,
    data: dict,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Actualiza un empleado existente

    Requiere rol super_admin
    """
    # Verificar permisos
    if current_user.role.value != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar empleados"
        )

    # Buscar empleado
    employee = await Employee.find_one(Employee.employee_id == employee_id)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Empleado {employee_id} no encontrado"
        )

    # Actualizar campos
    if "name" in data:
        employee.name = data["name"]
    if "surname" in data:
        employee.surname = data["surname"]
    if "email" in data:
        employee.email = data["email"]
    if "role" in data:
        from app.models.employee import EmployeeRole
        employee.role = EmployeeRole(data["role"])
    if "status" in data:
        from app.models.employee import EmployeeStatus
        employee.status = EmployeeStatus(data["status"])
    if "permissions" in data:
        employee.permissions = data["permissions"]
    if "password" in data and data["password"]:
        employee.set_password(data["password"])

    employee.updated_at = datetime.utcnow()
    await employee.save()

    return {
        "success": True,
        "message": f"Empleado {employee_id} actualizado correctamente",
        "employee": {
            "_id": str(employee.id),
            "employee_id": employee.employee_id,
            "name": employee.name,
            "surname": employee.surname,
            "email": employee.email,
            "role": employee.role.value,
            "status": employee.status.value,
            "permissions": employee.permissions
        }
    }


@router.post("/employees")
async def create_employee(
    data: dict,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Crea un nuevo empleado

    Requiere rol super_admin
    """
    # Verificar permisos
    if current_user.role.value != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear empleados"
        )

    # Validar campos requeridos
    required_fields = ["employee_id", "name", "surname", "password", "role"]
    for field in required_fields:
        if field not in data or not data[field]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El campo {field} es requerido"
            )

    # Verificar que el employee_id no exista
    existing = await Employee.find_one(Employee.employee_id == data["employee_id"])
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El empleado {data['employee_id']} ya existe"
        )

    # Crear nuevo empleado
    from app.models.employee import EmployeeRole, EmployeeStatus

    new_employee = Employee(
        employee_id=data["employee_id"],
        name=data["name"],
        surname=data["surname"],
        email=data.get("email"),
        role=EmployeeRole(data["role"]),
        status=EmployeeStatus(data.get("status", "active")),
        permissions=data.get("permissions", {}),
        password_hash="",  # Será reemplazado por set_password
        created_by=current_user.employee_id
    )

    # Establecer contraseña
    new_employee.set_password(data["password"])

    # Guardar
    await new_employee.insert()

    return {
        "success": True,
        "message": f"Empleado {data['employee_id']} creado correctamente",
        "employee": {
            "_id": str(new_employee.id),
            "employee_id": new_employee.employee_id,
            "name": new_employee.name,
            "surname": new_employee.surname,
            "email": new_employee.email,
            "role": new_employee.role.value,
            "status": new_employee.status.value
        }
    }


@router.delete("/employees/{employee_id}")
async def delete_employee(
    employee_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Elimina un empleado

    Requiere rol super_admin
    No permite eliminar el propio usuario ni otros super_admin
    """
    # Verificar permisos
    if current_user.role.value != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar empleados"
        )

    # Buscar empleado
    employee = await Employee.find_one(Employee.employee_id == employee_id)

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Empleado {employee_id} no encontrado"
        )

    # No permitir eliminar super_admin
    if employee.role.value == "super_admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede eliminar usuarios Super Admin"
        )

    # No permitir eliminar el propio usuario
    if employee.employee_id == current_user.employee_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propio usuario"
        )

    # Eliminar
    await employee.delete()

    return {
        "success": True,
        "message": f"Empleado {employee_id} eliminado correctamente"
    }

# End of file
