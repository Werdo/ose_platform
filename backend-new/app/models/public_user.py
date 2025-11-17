"""
OSE Platform - Public User Model
Modelo para usuarios externos del portal público de RMA/Tickets
"""

from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field, EmailStr
from enum import Enum


class PublicUserStatus(str, Enum):
    """Estados de usuario público"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"


class PublicUser(Document):
    """
    Usuario del portal público (clientes externos)
    Acceso limitado a crear y consultar tickets propios
    """

    # Información básica
    email: EmailStr
    password_hash: str

    # Datos personales
    nombre: str
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    empresa: Optional[str] = None

    # Estado y control
    status: PublicUserStatus = Field(default=PublicUserStatus.ACTIVE)
    is_verified: bool = Field(default=False)
    verification_token: Optional[str] = None

    # Metadatos
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    # Información adicional
    notes: Optional[str] = None  # Notas administrativas
    created_by: Optional[str] = None  # ID del empleado que lo creó

    class Settings:
        name = "public_users"
        indexes = [
            "email",
            "status",
            "created_at"
        ]

    @classmethod
    async def buscar_por_email(cls, email: str) -> Optional["PublicUser"]:
        """Busca un usuario público por email"""
        return await cls.find_one(cls.email == email)

    def dict_safe(self) -> dict:
        """Retorna diccionario sin información sensible"""
        return {
            "id": str(self.id),
            "email": self.email,
            "nombre": self.nombre,
            "apellidos": self.apellidos,
            "telefono": self.telefono,
            "empresa": self.empresa,
            "status": self.status,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
