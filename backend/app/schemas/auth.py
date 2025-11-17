"""
OSE Platform - Auth Schemas
Schemas para autenticación y gestión de tokens
"""

from typing import Optional, Dict
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime

from app.models.employee import EmployeeRole, EmployeeStatus


# ════════════════════════════════════════════════════════════════════════
# LOGIN
# ════════════════════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    """
    Request de login

    Example:
        {
            "identifier": "admin@oversun.com",
            "password": "SecurePass123"
        }

    OR:
        {
            "identifier": "ADMIN",
            "password": "SecurePass123"
        }
    """
    identifier: str = Field(..., description="Email o Employee ID del usuario")
    password: str = Field(..., min_length=1, description="Contraseña")


class TokenResponse(BaseModel):
    """
    Response con tokens JWT

    Example:
        {
            "access_token": "eyJ...",
            "refresh_token": "eyJ...",
            "token_type": "bearer",
            "expires_in": 1800
        }
    """
    access_token: str = Field(..., description="Token de acceso JWT")
    refresh_token: str = Field(..., description="Token de refresh JWT")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Segundos hasta expiración")


class LoginResponse(BaseModel):
    """
    Response completa de login

    Example:
        {
            "success": true,
            "message": "Login successful",
            "user": {...},
            "tokens": {...}
        }
    """
    success: bool = True
    message: str = "Login successful"
    user: "EmployeePublic"
    tokens: TokenResponse


# ════════════════════════════════════════════════════════════════════════
# REFRESH TOKEN
# ════════════════════════════════════════════════════════════════════════

class RefreshTokenRequest(BaseModel):
    """
    Request para refresh de token

    Example:
        {
            "refresh_token": "eyJ..."
        }
    """
    refresh_token: str = Field(..., description="Refresh token JWT")


# ════════════════════════════════════════════════════════════════════════
# PASSWORD RESET
# ════════════════════════════════════════════════════════════════════════

class PasswordResetRequest(BaseModel):
    """
    Request para solicitar reset de contraseña

    Example:
        {
            "email": "user@example.com"
        }
    """
    email: EmailStr = Field(..., description="Email del usuario")


class PasswordResetConfirm(BaseModel):
    """
    Request para confirmar reset de contraseña con token

    Example:
        {
            "token": "eyJ...",
            "new_password": "NewSecurePass123"
        }
    """
    token: str = Field(..., description="Token de reset recibido por email")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")

    @validator('new_password')
    def validate_password(cls, v):
        """Valida fortaleza de contraseña"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v


class PasswordChangeRequest(BaseModel):
    """
    Request para cambiar contraseña (usuario autenticado)

    Example:
        {
            "current_password": "OldPass123",
            "new_password": "NewPass123"
        }
    """
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=8, description="Nueva contraseña")

    @validator('new_password')
    def validate_password(cls, v):
        """Valida fortaleza de contraseña"""
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

    @validator('new_password')
    def passwords_different(cls, v, values):
        """Verifica que la nueva contraseña sea diferente"""
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('New password must be different from current password')
        return v


# ════════════════════════════════════════════════════════════════════════
# USER INFO
# ════════════════════════════════════════════════════════════════════════

class EmployeePublic(BaseModel):
    """
    Información pública del usuario (sin contraseña ni datos sensibles)

    Example:
        {
            "id": "507f1f77bcf86cd799439011",
            "employee_id": "EMP-001",
            "name": "John",
            "surname": "Doe",
            "email": "john@oversun.com",
            "role": "admin",
            "status": "active",
            "permissions": {...}
        }
    """
    id: str = Field(..., description="ID de MongoDB")
    employee_id: str
    name: str
    surname: str
    email: EmailStr
    role: EmployeeRole
    status: EmployeeStatus
    permissions: Dict[str, bool]
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmployeeProfile(EmployeePublic):
    """
    Perfil completo del usuario (información adicional)

    Extiende EmployeePublic con información adicional que solo el usuario ve
    """
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[datetime] = None


class CurrentUserResponse(BaseModel):
    """
    Response de /auth/me

    Example:
        {
            "success": true,
            "user": {...}
        }
    """
    success: bool = True
    user: EmployeeProfile


# ════════════════════════════════════════════════════════════════════════
# LOGOUT
# ════════════════════════════════════════════════════════════════════════

class LogoutRequest(BaseModel):
    """
    Request de logout (opcional)

    Puede incluir refresh token para invalidar
    """
    refresh_token: Optional[str] = Field(None, description="Refresh token a invalidar")


# ════════════════════════════════════════════════════════════════════════
# TOKEN VALIDATION
# ════════════════════════════════════════════════════════════════════════

class TokenValidationResponse(BaseModel):
    """
    Response de validación de token

    Example:
        {
            "valid": true,
            "expires_at": "2025-01-15T10:30:00Z",
            "user_id": "507f1f77bcf86cd799439011"
        }
    """
    valid: bool
    expires_at: Optional[datetime] = None
    user_id: Optional[str] = None
    role: Optional[EmployeeRole] = None


# Forward reference resolution
LoginResponse.model_rebuild()
CurrentUserResponse.model_rebuild()
