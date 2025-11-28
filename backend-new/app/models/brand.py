"""
Modelo de Marca (Brand)
Gestión de marcas de dispositivos en el sistema
"""

from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime


class Brand(Document):
    """
    Modelo para gestionar marcas de dispositivos
    """

    name: str = Field(..., description="Nombre de la marca")
    code: Optional[str] = Field(None, description="Código o abreviatura de la marca")
    description: Optional[str] = Field(None, description="Descripción de la marca")
    is_active: bool = Field(default=True, description="Indica si la marca está activa")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="ID del usuario que creó la marca")

    class Settings:
        name = "brands"
        indexes = [
            "name",
            "code",
            "is_active"
        ]

    @classmethod
    async def get_active_brands(cls):
        """Obtiene todas las marcas activas ordenadas por nombre"""
        return await cls.find(cls.is_active == True).sort("name").to_list()

    @classmethod
    async def find_by_name(cls, name: str):
        """Busca una marca por nombre (case-insensitive)"""
        return await cls.find_one({"name": {"$regex": f"^{name}$", "$options": "i"}})

    @classmethod
    async def find_by_code(cls, code: str):
        """Busca una marca por código"""
        if not code:
            return None
        return await cls.find_one({"code": {"$regex": f"^{code}$", "$options": "i"}})

    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
