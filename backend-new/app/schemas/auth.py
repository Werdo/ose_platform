"""
OSE Platform - Authentication Schemas
Schemas Pydantic para autenticación
"""

from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict
from datetime import datetime


class LoginRequest(BaseModel):
    """Schema para login"""
    identifier: str = Field(
        ...,
        description="Employee ID o email",
        min_length=3
    )
    password: str = Field(
        ...,
        description="Contraseña",
        min_length=4
    )

    class Config:
        json_schema_extra = {
            "example": {
                "identifier": "EMP001",
                "password": "mypassword"
            }
        }


class TokenResponse(BaseModel):
    """Schema para respuesta de tokens"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Segundos hasta expiración")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class RefreshTokenRequest(BaseModel):
    """Schema para refresh token"""
    refresh_token: str = Field(..., description="Refresh token válido")


class UserResponse(BaseModel):
    """Schema para datos del usuario autenticado"""
    id: str = Field(..., description="ID del usuario")
    employee_id: str = Field(..., description="ID del empleado")
    name: str = Field(..., description="Nombre")
    surname: str = Field(..., description="Apellidos")
    email: Optional[str] = Field(None, description="Email")
    role: str = Field(..., description="Rol")
    permissions: Dict[str, bool] = Field(..., description="Permisos")
    last_login: Optional[datetime] = Field(None, description="Último login")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "employee_id": "EMP001",
                "name": "Juan",
                "surname": "Pérez",
                "email": "juan@empresa.com",
                "role": "operator",
                "permissions": {
                    "production_line1_station1": True,
                    "quality_control": False
                },
                "last_login": "2025-01-15T10:30:00"
            }
        }


class LoginResponse(BaseModel):
    """Schema para respuesta de login con tokens y usuario"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Tipo de token")
    expires_in: int = Field(..., description="Segundos hasta expiración")
    user: UserResponse = Field(..., description="Información del usuario")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": "507f1f77bcf86cd799439011",
                    "employee_id": "EMP001",
                    "name": "Juan",
                    "surname": "Pérez",
                    "email": "juan@empresa.com",
                    "role": "operator",
                    "permissions": {
                        "production_line1_station1": True
                    }
                }
            }
        }


class ChangePasswordRequest(BaseModel):
    """Schema para cambiar contraseña"""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., description="Nueva contraseña", min_length=8)
    confirm_password: str = Field(..., description="Confirmar nueva contraseña")

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Las contraseñas no coinciden')
        return v


class CreateUserRequest(BaseModel):
    """Schema para crear nuevo usuario/empleado"""
    employee_id: str = Field(..., description="ID del empleado", min_length=3, max_length=20)
    name: str = Field(..., description="Nombre", min_length=2, max_length=50)
    surname: str = Field(..., description="Apellidos", min_length=2, max_length=100)
    email: Optional[EmailStr] = Field(None, description="Email")
    phone: Optional[str] = Field(None, description="Teléfono")
    password: str = Field(..., description="Contraseña", min_length=8)
    role: str = Field(default="operator", description="Rol")
    permissions: Optional[Dict[str, bool]] = Field(None, description="Permisos específicos")

    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP002",
                "name": "María",
                "surname": "García",
                "email": "maria@empresa.com",
                "phone": "+34 600 123 456",
                "password": "SecurePass123",
                "role": "operator",
                "permissions": {
                    "production_line1_station1": True
                }
            }
        }


class UpdateUserRequest(BaseModel):
    """Schema para actualizar usuario"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    surname: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[Dict[str, bool]] = None
    status: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "+34 600 999 888",
                "role": "supervisor"
            }
        }
