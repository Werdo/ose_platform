"""
OSE Platform - Employee Schemas
Schemas para gestión de empleados
"""

from typing import Optional, Dict, List
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime

from app.models.employee import EmployeeRole, EmployeeStatus


# ════════════════════════════════════════════════════════════════════════
# CREATE
# ════════════════════════════════════════════════════════════════════════

class EmployeeCreate(BaseModel):
    """
    Request para crear empleado

    Example:
        {
            "employee_id": "EMP-001",
            "name": "John",
            "surname": "Doe",
            "email": "john@oversun.com",
            "password": "SecurePass123",
            "role": "operator",
            "permissions": {...}
        }
    """
    employee_id: str = Field(..., min_length=3, max_length=50, description="ID único del empleado")
    name: str = Field(..., min_length=1, max_length=100)
    surname: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, description="Contraseña (será hasheada)")
    phone: Optional[str] = None
    role: EmployeeRole
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[datetime] = None
    permissions: Dict[str, bool] = Field(
        default_factory=lambda: {
            "production_lines": False,
            "stations": False,
            "quality_control": False,
            "warehouse": False,
            "support_tickets": False,
            "rma_cases": False,
            "customer_management": False,
            "reports": False,
            "admin_panel": False,
        }
    )

    @validator('password')
    def validate_password(cls, v):
        """Valida fortaleza de contraseña"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


# ════════════════════════════════════════════════════════════════════════
# UPDATE
# ════════════════════════════════════════════════════════════════════════

class EmployeeUpdate(BaseModel):
    """
    Request para actualizar empleado

    Todos los campos son opcionales
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    surname: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[EmployeeRole] = None
    status: Optional[EmployeeStatus] = None
    department: Optional[str] = None
    position: Optional[str] = None
    permissions: Optional[Dict[str, bool]] = None


# ════════════════════════════════════════════════════════════════════════
# RESPONSE
# ════════════════════════════════════════════════════════════════════════

class EmployeeResponse(BaseModel):
    """
    Response de empleado (sin contraseña)

    Example:
        {
            "id": "507f1f77bcf86cd799439011",
            "employee_id": "EMP-001",
            "name": "John",
            "surname": "Doe",
            "email": "john@oversun.com",
            "role": "operator",
            "status": "active",
            "permissions": {...},
            "created_at": "2025-01-01T10:00:00Z",
            "last_login": "2025-01-15T09:30:00Z"
        }
    """
    id: str
    employee_id: str
    name: str
    surname: str
    email: EmailStr
    phone: Optional[str] = None
    role: EmployeeRole
    status: EmployeeStatus
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[datetime] = None
    permissions: Dict[str, bool]
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════════════════
# LIST/FILTER
# ════════════════════════════════════════════════════════════════════════

class EmployeeFilter(BaseModel):
    """
    Filtros para listado de empleados

    Example query params:
        ?role=operator&status=active&department=Production
    """
    role: Optional[EmployeeRole] = None
    status: Optional[EmployeeStatus] = None
    department: Optional[str] = None
    search: Optional[str] = Field(None, description="Búsqueda en name, surname, email, employee_id")


class EmployeeSummary(BaseModel):
    """
    Resumen de empleado (para listas)

    Versión más ligera sin todos los detalles
    """
    id: str
    employee_id: str
    name: str
    surname: str
    email: EmailStr
    role: EmployeeRole
    status: EmployeeStatus

    @property
    def full_name(self) -> str:
        return f"{self.name} {self.surname}"

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════════════════
# STATISTICS
# ════════════════════════════════════════════════════════════════════════

class EmployeeStatistics(BaseModel):
    """
    Estadísticas de empleados

    Example:
        {
            "total": 50,
            "by_role": {
                "operator": 30,
                "supervisor": 10,
                "admin": 5,
                "quality_inspector": 5
            },
            "by_status": {
                "active": 45,
                "inactive": 3,
                "suspended": 2
            }
        }
    """
    total: int
    by_role: Dict[str, int]
    by_status: Dict[str, int]
    active_today: int = Field(..., description="Empleados que han hecho login hoy")
