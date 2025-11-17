"""
OSE Platform - App 5: Schemas
Pydantic schemas para el sistema de facturación
"""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class TicketItemCreate(BaseModel):
    """Schema para línea de ticket"""
    description: str = Field(..., min_length=1, description="Descripción del producto")
    quantity: float = Field(..., gt=0, description="Cantidad")
    unit_price: float = Field(..., ge=0, description="Precio unitario")
    total: float = Field(..., ge=0, description="Total de la línea")


class TicketCreate(BaseModel):
    """Schema para crear un ticket"""
    email: EmailStr = Field(..., description="Email del cliente")
    ticket_number: str = Field(..., min_length=1, description="Número del ticket")
    date: str = Field(..., description="Fecha del ticket (ISO format)")
    total: float = Field(..., gt=0, description="Total del ticket")
    items: List[TicketItemCreate] = Field(..., min_items=1, description="Líneas del ticket")
    billing_name: Optional[str] = Field(None, description="Nombre de facturación")
    billing_nif: Optional[str] = Field(None, description="NIF/CIF")
    billing_address: Optional[str] = Field(None, description="Dirección de facturación")


class TicketResponse(BaseModel):
    """Schema de respuesta de ticket"""
    id: int
    email: str
    ticket_number: str
    date: str
    total: float
    image_url: Optional[str] = None
    status: str
    items: List[dict]
    billing_name: Optional[str] = None
    billing_nif: Optional[str] = None
    billing_address: Optional[str] = None
    created_at: str
