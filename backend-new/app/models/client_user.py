"""
OSE Platform - Client User Model
Modelo para usuarios clientes externos con permisos granulares
"""

from datetime import datetime
from typing import Optional, List, Dict
from beanie import Document
from pydantic import Field, EmailStr
from enum import Enum


class ClientUserRole(str, Enum):
    """Roles de usuarios clientes"""
    CLIENT = "client"  # Cliente básico
    CLIENT_PREMIUM = "client_premium"  # Cliente con acceso extendido
    PARTNER = "partner"  # Partner/Distribuidor


class AppPermission(str, Enum):
    """Permisos por aplicación"""
    APP1_SERIES_NOTIFICATION = "app1"  # Notificación de Series
    APP2_DATA_IMPORT = "app2"  # Importación de Datos (solo admin/employee)
    APP3_RMA_TICKETS = "app3"  # RMA & Tickets
    APP4_TRANSFORM_DATA = "app4"  # Transform Data (solo admin/employee)
    APP5_INVOICING = "app5"  # Facturación (solo admin/employee)
    APP6_PICKING = "app6"  # Picking (solo admin/employee)
    APP7_ASSETFLOW = "app7"  # AssetFlow (enlace externo)
    APP8_ICCID_CALCULATOR = "app8"  # Calculadora ICCID
    APP9_SEARCH_DEVICES = "app9"  # Búsqueda IMEI/ICCID


class ClientUser(Document):
    """Usuario cliente externo"""

    # Información básica
    email: EmailStr = Field(..., description="Email del cliente (único)", index=True)
    company_name: str = Field(..., description="Nombre de la empresa/cliente")
    contact_name: str = Field(..., description="Nombre de contacto")
    phone: Optional[str] = Field(None, description="Teléfono")

    # Autenticación
    hashed_password: str = Field(..., description="Password hasheado")

    # Rol y permisos
    role: ClientUserRole = Field(
        default=ClientUserRole.CLIENT,
        description="Rol del cliente"
    )
    permissions: List[AppPermission] = Field(
        default_factory=list,
        description="Permisos de acceso a apps"
    )

    # Estado de la cuenta
    is_active: bool = Field(default=True, description="Usuario activo")
    is_verified: bool = Field(default=False, description="Email verificado")

    # Información adicional
    notes: Optional[str] = Field(None, description="Notas internas sobre el cliente")
    client_code: Optional[str] = Field(None, description="Código de cliente", index=True)

    # Restricciones de datos
    allowed_imei_prefixes: List[str] = Field(
        default_factory=list,
        description="Prefijos de IMEI permitidos para búsqueda"
    )
    allowed_iccid_prefixes: List[str] = Field(
        default_factory=list,
        description="Prefijos de ICCID permitidos para búsqueda"
    )

    # Metadata de gestión
    created_by: str = Field(..., description="Admin que creó el usuario")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(None, description="Último login")

    # Configuración de AssetFlow (si tiene acceso)
    assetflow_url: Optional[str] = Field(
        default="https://assetflow.oversunenergy.com",
        description="URL de AssetFlow"
    )
    assetflow_username: Optional[str] = Field(
        None,
        description="Usuario de AssetFlow (si es diferente)"
    )

    class Settings:
        name = "client_users"
        indexes = [
            "email",
            "company_name",
            "client_code",
            "is_active",
            "role",
            "created_at",
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "email": "contacto@clienteejemplo.com",
                "company_name": "Cliente Ejemplo S.L.",
                "contact_name": "Juan Pérez",
                "phone": "+34 666 777 888",
                "role": "client",
                "permissions": ["app1", "app3", "app9"],
                "is_active": True,
                "client_code": "CLI001",
                "notes": "Cliente desde 2025",
                "created_by": "ADMIN"
            }
        }

    async def update_last_login(self):
        """Actualiza el último login"""
        self.last_login = datetime.utcnow()
        await self.save()

    def has_permission(self, app: AppPermission) -> bool:
        """Verifica si el usuario tiene permiso para una app"""
        return app in self.permissions

    def get_accessible_apps(self) -> List[Dict[str, str]]:
        """Retorna lista de apps accesibles con metadatos"""
        app_metadata = {
            AppPermission.APP1_SERIES_NOTIFICATION: {
                "name": "Notificación de Series",
                "icon": "bi-send",
                "path": "/app1",
                "external": False
            },
            AppPermission.APP2_DATA_IMPORT: {
                "name": "Importación de Datos",
                "icon": "bi-upload",
                "path": "/app2",
                "external": False
            },
            AppPermission.APP3_RMA_TICKETS: {
                "name": "RMA & Tickets",
                "icon": "bi-ticket",
                "path": "/app3",
                "external": False
            },
            AppPermission.APP4_TRANSFORM_DATA: {
                "name": "Transform Data",
                "icon": "bi-arrow-repeat",
                "path": "/app4",
                "external": False
            },
            AppPermission.APP5_INVOICING: {
                "name": "Generación de Facturas",
                "icon": "bi-receipt",
                "path": "/app5",
                "external": False
            },
            AppPermission.APP6_PICKING: {
                "name": "Picking Lists",
                "icon": "bi-box-seam",
                "path": "/app6",
                "external": False
            },
            AppPermission.APP7_ASSETFLOW: {
                "name": "AssetFlow",
                "icon": "bi-layers",
                "path": self.assetflow_url or "https://assetflow.oversunenergy.com",
                "external": True
            },
            AppPermission.APP8_ICCID_CALCULATOR: {
                "name": "Calculadora ICCID",
                "icon": "bi-calculator",
                "path": "/app8",
                "external": False
            },
            AppPermission.APP9_SEARCH_DEVICES: {
                "name": "Búsqueda IMEI/ICCID",
                "icon": "bi-search",
                "path": "/app9",
                "external": False
            },
        }

        accessible = []
        for perm in self.permissions:
            if perm in app_metadata:
                accessible.append({
                    "id": perm.value,
                    **app_metadata[perm]
                })

        return accessible
