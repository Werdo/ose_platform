"""
OSE Platform - Customer Model
Modelo para gestión de clientes (distribuidores y usuarios finales)
"""

from beanie import Document
from pydantic import Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CustomerType(str, Enum):
    """Tipos de clientes"""
    END_USER = "end_user"
    DISTRIBUTOR = "distributor"
    RESELLER = "reseller"
    ENTERPRISE = "enterprise"
    GOVERNMENT = "government"


class CustomerStatus(str, Enum):
    """Estados de clientes"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    BLACKLISTED = "blacklisted"


class Customer(Document):
    """
    Cliente (distribuidor, usuario final, enterprise)
    """

    # ════════════════════════════════════════════════════════════════════
    # IDENTIFICACIÓN
    # ════════════════════════════════════════════════════════════════════

    customer_code: str = Field(
        ...,
        description="Código único del cliente",
        index=True
    )

    customer_type: CustomerType = Field(
        default=CustomerType.END_USER,
        description="Tipo de cliente"
    )

    status: CustomerStatus = Field(
        default=CustomerStatus.ACTIVE,
        description="Estado del cliente",
        index=True
    )

    # ════════════════════════════════════════════════════════════════════
    # INFORMACIÓN BÁSICA
    # ════════════════════════════════════════════════════════════════════

    company_name: Optional[str] = Field(
        default=None,
        description="Nombre de la empresa (para distribuidores/enterprise)"
    )

    first_name: Optional[str] = Field(
        default=None,
        description="Nombre (para usuarios finales)"
    )

    last_name: Optional[str] = Field(
        default=None,
        description="Apellidos (para usuarios finales)"
    )

    tax_id: Optional[str] = Field(
        default=None,
        description="NIF/CIF/Tax ID"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONTACTO
    # ════════════════════════════════════════════════════════════════════

    email: EmailStr = Field(
        ...,
        description="Email principal",
        index=True
    )

    phone: Optional[str] = Field(
        default=None,
        description="Teléfono principal"
    )

    mobile: Optional[str] = Field(
        default=None,
        description="Teléfono móvil"
    )

    website: Optional[str] = Field(
        default=None,
        description="Sitio web (para empresas)"
    )

    # ════════════════════════════════════════════════════════════════════
    # DIRECCIÓN
    # ════════════════════════════════════════════════════════════════════

    address: Optional[Dict[str, str]] = Field(
        default=None,
        description="Dirección del cliente"
    )
    # {
    #     "street": "Calle Principal 123",
    #     "city": "Madrid",
    #     "state": "Madrid",
    #     "postal_code": "28001",
    #     "country": "España"
    # }

    billing_address: Optional[Dict[str, str]] = Field(
        default=None,
        description="Dirección de facturación (si es diferente)"
    )

    # ════════════════════════════════════════════════════════════════════
    # DISPOSITIVOS Y SERVICIOS
    # ════════════════════════════════════════════════════════════════════

    devices_count: int = Field(
        default=0,
        description="Total de dispositivos del cliente"
    )

    active_devices_count: int = Field(
        default=0,
        description="Dispositivos activos del cliente"
    )

    tickets_count: int = Field(
        default=0,
        description="Total de tickets generados"
    )

    rma_count: int = Field(
        default=0,
        description="Total de RMAs generados"
    )

    # ════════════════════════════════════════════════════════════════════
    # RELACIÓN COMERCIAL
    # ════════════════════════════════════════════════════════════════════

    discount_rate: Optional[float] = Field(
        default=0.0,
        description="Porcentaje de descuento",
        ge=0,
        le=100
    )

    payment_terms: Optional[str] = Field(
        default="30_days",
        description="Términos de pago"
    )

    credit_limit: Optional[float] = Field(
        default=None,
        description="Límite de crédito"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONTACTOS ADICIONALES
    # ════════════════════════════════════════════════════════════════════

    contacts: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Contactos adicionales del cliente"
    )
    # [
    #     {
    #         "name": "Juan Pérez",
    #         "role": "Gerente Técnico",
    #         "email": "juan@empresa.com",
    #         "phone": "+34 600 123 456"
    #     }
    # ]

    # ════════════════════════════════════════════════════════════════════
    # NOTAS Y PREFERENCIAS
    # ════════════════════════════════════════════════════════════════════

    notes: Optional[str] = Field(
        default=None,
        description="Notas internas sobre el cliente"
    )

    preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Preferencias del cliente"
    )

    tags: List[str] = Field(
        default_factory=list,
        description="Etiquetas para clasificación"
    )

    # ════════════════════════════════════════════════════════════════════
    # FECHAS
    # ════════════════════════════════════════════════════════════════════

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de registro",
        index=True
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )

    last_purchase_date: Optional[datetime] = Field(
        default=None,
        description="Última fecha de compra"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA
    # ════════════════════════════════════════════════════════════════════

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Datos adicionales"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "customers"
        indexes = [
            "customer_code",  # Unique
            "email",
            "status",
            "customer_type",
            [("customer_type", 1), ("status", 1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # VALIDADORES
    # ════════════════════════════════════════════════════════════════════

    @validator('customer_code')
    def validate_customer_code(cls, v):
        """Valida el código de cliente"""
        return v.strip().upper()

    @validator('email')
    def validate_email(cls, v):
        """Normaliza el email"""
        return v.lower()

    # ════════════════════════════════════════════════════════════════════
    # PROPIEDADES
    # ════════════════════════════════════════════════════════════════════

    @property
    def full_name(self) -> str:
        """Retorna el nombre completo o nombre de empresa"""
        if self.company_name:
            return self.company_name
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.customer_code

    @property
    def is_active(self) -> bool:
        """Verifica si el cliente está activo"""
        return self.status == CustomerStatus.ACTIVE

    @property
    def is_enterprise(self) -> bool:
        """Verifica si es cliente enterprise"""
        return self.customer_type in [
            CustomerType.DISTRIBUTOR,
            CustomerType.ENTERPRISE,
            CustomerType.RESELLER
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ════════════════════════════════════════════════════════════════════

    async def increment_devices_count(self, quantity: int = 1):
        """Incrementa el contador de dispositivos"""
        self.devices_count += quantity
        self.active_devices_count += quantity
        self.updated_at = datetime.utcnow()
        await self.save()

    async def increment_tickets_count(self):
        """Incrementa el contador de tickets"""
        self.tickets_count += 1
        self.updated_at = datetime.utcnow()
        await self.save()

    async def increment_rma_count(self):
        """Incrementa el contador de RMAs"""
        self.rma_count += 1
        self.updated_at = datetime.utcnow()
        await self.save()

    async def add_contact(self, name: str, role: str, email: str, phone: Optional[str] = None):
        """Añade un contacto adicional"""
        contact = {
            "name": name,
            "role": role,
            "email": email,
            "phone": phone,
            "added_at": datetime.utcnow()
        }
        self.contacts.append(contact)
        self.updated_at = datetime.utcnow()
        await self.save()

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def find_by_code(customer_code: str) -> Optional["Customer"]:
        """Busca un cliente por su código"""
        return await Customer.find_one(
            Customer.customer_code == customer_code.strip().upper()
        )

    @staticmethod
    async def find_by_email(email: str) -> Optional["Customer"]:
        """Busca un cliente por email"""
        return await Customer.find_one(Customer.email == email.lower())

    @staticmethod
    async def find_active_customers():
        """Retorna todos los clientes activos"""
        return await Customer.find(
            Customer.status == CustomerStatus.ACTIVE
        ).sort("-created_at").to_list()

    @staticmethod
    async def find_by_type(customer_type: CustomerType):
        """Busca clientes por tipo"""
        return await Customer.find(
            Customer.customer_type == customer_type,
            Customer.status == CustomerStatus.ACTIVE
        ).to_list()
