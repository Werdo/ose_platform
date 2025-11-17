"""
OSE Platform - Customer Schemas
Schemas para gestión de clientes
"""

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

from app.models.customer import CustomerType, CustomerStatus


# ════════════════════════════════════════════════════════════════════════
# CREATE & UPDATE
# ════════════════════════════════════════════════════════════════════════

class CustomerCreate(BaseModel):
    """Request para crear cliente"""
    customer_code: str = Field(..., min_length=3, max_length=20)
    customer_type: CustomerType
    company_name: str = Field(..., min_length=2, max_length=200)
    tax_id: Optional[str] = None
    contact_name: str
    contact_email: EmailStr
    contact_phone: str
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_country: Optional[str] = None
    address_postal_code: Optional[str] = None
    discount_percentage: float = Field(default=0, ge=0, le=100)
    payment_terms_days: int = Field(default=30, ge=0)
    credit_limit: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


class CustomerUpdate(BaseModel):
    """Request para actualizar cliente"""
    customer_type: Optional[CustomerType] = None
    status: Optional[CustomerStatus] = None
    company_name: Optional[str] = Field(None, min_length=2, max_length=200)
    tax_id: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_country: Optional[str] = None
    address_postal_code: Optional[str] = None
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    payment_terms_days: Optional[int] = Field(None, ge=0)
    credit_limit: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None


# ════════════════════════════════════════════════════════════════════════
# RESPONSE
# ════════════════════════════════════════════════════════════════════════

class CustomerResponse(BaseModel):
    """Response de cliente completo"""
    id: str
    customer_code: str
    customer_type: CustomerType
    status: CustomerStatus
    company_name: str
    tax_id: Optional[str]
    contact_name: str
    contact_email: EmailStr
    contact_phone: str
    address_street: Optional[str]
    address_city: Optional[str]
    address_state: Optional[str]
    address_country: Optional[str]
    address_postal_code: Optional[str]
    billing_address_street: Optional[str]
    billing_address_city: Optional[str]
    billing_address_state: Optional[str]
    billing_address_country: Optional[str]
    billing_address_postal_code: Optional[str]
    discount_percentage: float
    payment_terms_days: int
    credit_limit: Optional[float]
    devices_count: int
    tickets_count: int
    rma_count: int
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CustomerSummary(BaseModel):
    """Resumen de cliente para listas"""
    id: str
    customer_code: str
    company_name: str
    customer_type: CustomerType
    status: CustomerStatus
    devices_count: int

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════════════════
# FILTER & STATISTICS
# ════════════════════════════════════════════════════════════════════════

class CustomerFilter(BaseModel):
    """Filtros para clientes"""
    customer_type: Optional[CustomerType] = None
    status: Optional[CustomerStatus] = None
    country: Optional[str] = None
    search: Optional[str] = Field(None, description="Búsqueda en código, nombre, email")


class CustomerStatistics(BaseModel):
    """Estadísticas de clientes"""
    total: int
    by_type: dict
    by_status: dict
    by_country: dict
    total_devices: int
    active_customers: int
