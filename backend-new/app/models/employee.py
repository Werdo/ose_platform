"""
OSE Platform - Employee Model
Modelo para gestión de personal y autenticación
"""

from beanie import Document
from pydantic import Field, EmailStr, validator
from typing import Optional, Dict
from datetime import datetime
from enum import Enum


class EmployeeRole(str, Enum):
    """Roles de empleados"""
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    QUALITY_INSPECTOR = "quality_inspector"
    TECHNICIAN = "technician"
    MANAGER = "manager"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class EmployeeStatus(str, Enum):
    """Estados de empleados"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ON_LEAVE = "on_leave"


class Employee(Document):
    """
    Modelo de empleado/usuario del sistema
    Gestiona autenticación, permisos y trazabilidad de operaciones
    """

    # ════════════════════════════════════════════════════════════════════
    # INFORMACIÓN PERSONAL
    # ════════════════════════════════════════════════════════════════════

    employee_id: str = Field(
        ...,
        description="ID único del empleado",
        min_length=3,
        max_length=20,
        index=True
    )

    name: str = Field(
        ...,
        description="Nombre del empleado",
        min_length=2,
        max_length=50
    )

    surname: str = Field(
        ...,
        description="Apellidos del empleado",
        min_length=2,
        max_length=100
    )

    email: Optional[EmailStr] = Field(
        default=None,
        description="Email del empleado",
        index=True
    )

    phone: Optional[str] = Field(
        default=None,
        description="Teléfono de contacto"
    )

    # ════════════════════════════════════════════════════════════════════
    # AUTENTICACIÓN
    # ════════════════════════════════════════════════════════════════════

    password_hash: str = Field(
        ...,
        description="Hash de la contraseña (bcrypt)"
    )

    role: EmployeeRole = Field(
        default=EmployeeRole.OPERATOR,
        description="Rol principal del empleado"
    )

    status: EmployeeStatus = Field(
        default=EmployeeStatus.ACTIVE,
        description="Estado del empleado"
    )

    # ════════════════════════════════════════════════════════════════════
    # PERMISOS GRANULARES (heredados de PostgreSQL)
    # ════════════════════════════════════════════════════════════════════

    permissions: Dict[str, bool] = Field(
        default_factory=lambda: {
            # Aplicaciones
            "app1_access": False,  # Notificación de Series
            "app2_access": False,  # Importación de Datos
            "app3_access": False,  # RMA & Tickets
            "app4_access": False,  # Transform Data
            "app5_access": False,  # Facturas
            "app6_access": False,  # Picking & Etiquetado
            # Estaciones de producción
            "production_line1_station1": False,
            "production_line1_station2": False,
            "production_line2_station1": False,
            "production_line2_station2": False,
            "production_line3_station1": False,
            "production_line3_station2": False,
            # Permisos generales
            "quality_control": False,
            "admin_access": False,
            "manage_users": False,
            "manage_settings": False,
            "view_reports": False,
            "manage_tickets": False,
            "manage_rma": False,
            "manage_customers": False,
            "manage_inventory": False,
        },
        description="Permisos específicos del empleado"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA DE SESIÓN
    # ════════════════════════════════════════════════════════════════════

    last_login: Optional[datetime] = Field(
        default=None,
        description="Último inicio de sesión"
    )

    last_login_ip: Optional[str] = Field(
        default=None,
        description="IP del último login"
    )

    failed_login_attempts: int = Field(
        default=0,
        description="Intentos fallidos de login"
    )

    locked_until: Optional[datetime] = Field(
        default=None,
        description="Bloqueado hasta (por intentos fallidos)"
    )

    # ════════════════════════════════════════════════════════════════════
    # REFRESH TOKEN (para JWT)
    # ════════════════════════════════════════════════════════════════════

    refresh_token: Optional[str] = Field(
        default=None,
        description="Token de refresh actual"
    )

    refresh_token_expires: Optional[datetime] = Field(
        default=None,
        description="Expiración del refresh token"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA
    # ════════════════════════════════════════════════════════════════════

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )

    created_by: Optional[str] = Field(
        default=None,
        description="ID del usuario que creó este registro"
    )

    notes: Optional[str] = Field(
        default=None,
        description="Notas adicionales sobre el empleado"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "employees"
        indexes = [
            "employee_id",
            "email",
            "role",
            "status",
            [("employee_id", 1), ("status", 1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # VALIDADORES
    # ════════════════════════════════════════════════════════════════════

    @validator('employee_id')
    def validate_employee_id(cls, v):
        """Valida el formato del employee_id"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('employee_id debe contener solo letras, números, guiones y guiones bajos')
        return v.strip().upper()

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ════════════════════════════════════════════════════════════════════

    @property
    def full_name(self) -> str:
        """Retorna el nombre completo"""
        return f"{self.name} {self.surname}"

    @property
    def is_active(self) -> bool:
        """Verifica si el empleado está activo"""
        return self.status == EmployeeStatus.ACTIVE

    @property
    def is_admin(self) -> bool:
        """Verifica si el empleado es admin"""
        return self.role in [EmployeeRole.ADMIN, EmployeeRole.SUPER_ADMIN]

    @property
    def is_locked(self) -> bool:
        """Verifica si la cuenta está bloqueada"""
        if not self.locked_until:
            return False
        return datetime.utcnow() < self.locked_until

    def has_permission(self, permission: str) -> bool:
        """Verifica si el empleado tiene un permiso específico"""
        # Super admin tiene todos los permisos
        if self.role == EmployeeRole.SUPER_ADMIN:
            return True

        # Admin tiene casi todos los permisos
        if self.role == EmployeeRole.ADMIN and permission != "manage_settings":
            return True

        # Verificar permiso específico
        return self.permissions.get(permission, False)

    def verify_password(self, password: str) -> bool:
        """
        Verifica si la contraseña es correcta
        """
        from app.utils.security import verify_password
        return verify_password(password, self.password_hash)

    def set_password(self, password: str):
        """
        Establece una nueva contraseña (hash)
        """
        from app.utils.security import hash_password
        self.password_hash = hash_password(password)

    async def record_login(self, ip: Optional[str] = None, success: bool = True):
        """
        Registra un intento de login
        """
        if success:
            self.last_login = datetime.utcnow()
            if ip:
                self.last_login_ip = ip
            self.failed_login_attempts = 0
            self.locked_until = None
        else:
            self.failed_login_attempts += 1

            # Bloquear cuenta después de 5 intentos fallidos
            if self.failed_login_attempts >= 5:
                from datetime import timedelta
                self.locked_until = datetime.utcnow() + timedelta(minutes=30)

        self.updated_at = datetime.utcnow()
        await self.save()

    async def set_refresh_token(self, token: str, expires: datetime):
        """
        Establece un nuevo refresh token
        """
        self.refresh_token = token
        self.refresh_token_expires = expires
        await self.save()

    async def clear_refresh_token(self):
        """
        Limpia el refresh token (logout)
        """
        self.refresh_token = None
        self.refresh_token_expires = None
        await self.save()

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def find_by_employee_id(employee_id: str) -> Optional["Employee"]:
        """Busca un empleado por su employee_id"""
        return await Employee.find_one(
            Employee.employee_id == employee_id.strip().upper()
        )

    @staticmethod
    async def find_by_email(email: str) -> Optional["Employee"]:
        """Busca un empleado por su email"""
        return await Employee.find_one(Employee.email == email.lower())

    @staticmethod
    async def authenticate(identifier: str, password: str) -> Optional["Employee"]:
        """
        Autentica un empleado por employee_id o email
        Retorna el empleado si las credenciales son correctas, None si no
        """
        # Intentar buscar por employee_id o email
        employee = await Employee.find_by_employee_id(identifier)
        if not employee:
            employee = await Employee.find_by_email(identifier)

        if not employee:
            return None

        # Verificar que esté activo
        if not employee.is_active:
            return None

        # Verificar que no esté bloqueado
        if employee.is_locked:
            return None

        # Verificar contraseña
        if not employee.verify_password(password):
            await employee.record_login(success=False)
            return None

        return employee
