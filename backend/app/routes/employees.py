"""
OSE Platform - Employee Routes
Endpoints CRUD para empleados
"""

from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId

from app.schemas import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeResponse,
    EmployeeSummary,
    PaginatedResponse,
    PaginationParams,
    MessageResponse,
    SuccessResponse,
)
from app.models.employee import Employee
from app.dependencies import get_current_user, require_admin
from app.middleware import audit_logger

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("", response_model=SuccessResponse[EmployeeResponse], status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee_data: EmployeeCreate,
    current_user: Employee = Depends(require_admin)
):
    """Crea un nuevo empleado (solo admin)"""
    # Check if email or employee_id exists
    existing = await Employee.find_one(
        {"$or": [
            {"email": employee_data.email},
            {"employee_id": employee_data.employee_id}
        ]}
    )
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Employee already exists")

    # Create employee
    employee = Employee(**employee_data.model_dump(exclude={"password"}))
    await employee.set_password(employee_data.password)
    await employee.save()

    audit_logger.log_data_access(str(current_user.id), "employee", "create", str(employee.id))
    return SuccessResponse(data=EmployeeResponse(**employee.model_dump(), id=str(employee.id)))


@router.get("", response_model=PaginatedResponse[EmployeeSummary])
async def list_employees(
    pagination: PaginationParams = Depends(),
    current_user: Employee = Depends(get_current_user)
):
    """Lista empleados"""
    total = await Employee.find({}).count()
    employees = await Employee.find({}).skip(pagination.skip).limit(pagination.page_size).to_list()

    summaries = [EmployeeSummary(**e.model_dump(), id=str(e.id)) for e in employees]
    from app.schemas import PaginationMeta
    meta = PaginationMeta.create(total, pagination.page, pagination.page_size)

    return PaginatedResponse(data=summaries, meta=meta)


@router.get("/{employee_id}", response_model=SuccessResponse[EmployeeResponse])
async def get_employee(
    employee_id: str,
    current_user: Employee = Depends(get_current_user)
):
    """Obtiene un empleado por ID"""
    try:
        employee = await Employee.get(PydanticObjectId(employee_id))
    except:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")

    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")

    return SuccessResponse(data=EmployeeResponse(**employee.model_dump(), id=str(employee.id)))


@router.patch("/{employee_id}", response_model=SuccessResponse[EmployeeResponse])
async def update_employee(
    employee_id: str,
    employee_data: EmployeeUpdate,
    current_user: Employee = Depends(require_admin)
):
    """Actualiza un empleado"""
    try:
        employee = await Employee.get(PydanticObjectId(employee_id))
    except:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")

    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")

    update_data = employee_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)

    await employee.save()
    audit_logger.log_data_access(str(current_user.id), "employee", "update", employee_id)

    return SuccessResponse(data=EmployeeResponse(**employee.model_dump(), id=str(employee.id)))


@router.delete("/{employee_id}", response_model=MessageResponse)
async def delete_employee(
    employee_id: str,
    current_user: Employee = Depends(require_admin)
):
    """Elimina un empleado (solo admin)"""
    try:
        employee = await Employee.get(PydanticObjectId(employee_id))
    except:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")

    if not employee:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Employee not found")

    # Don't allow deleting yourself
    if str(employee.id) == str(current_user.id):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cannot delete yourself")

    await employee.delete()
    audit_logger.log_data_access(str(current_user.id), "employee", "delete", employee_id)

    return MessageResponse(message="Employee deleted successfully")
