"""
OSE Platform - Employee Management Router
Endpoints for CRUD operations on employees (super_admin only)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from app.models.employee import Employee, EmployeeRole, EmployeeStatus
from app.dependencies.auth import get_current_active_user

router = APIRouter(prefix="/auth/employees", tags=["Employee Management"])


@router.get("")
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


@router.put("/{employee_id}")
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
        employee.role = EmployeeRole(data["role"])
    if "status" in data:
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


@router.post("")
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


@router.delete("/{employee_id}")
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
