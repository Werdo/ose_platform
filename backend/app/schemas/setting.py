"""
OSE Platform - Settings Schemas
Schemas para configuración del sistema
"""

from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field, EmailStr

from app.models.setting import SettingCategory


# ════════════════════════════════════════════════════════════════════════
# SETTING CRUD
# ════════════════════════════════════════════════════════════════════════

class SettingCreate(BaseModel):
    """Request para crear setting"""
    category: SettingCategory
    key: str = Field(..., min_length=1, max_length=100)
    value: Any
    encrypted: bool = False
    ui_visible: bool = True
    ui_order: int = 0
    ui_label: Optional[str] = None
    ui_help_text: Optional[str] = None
    ui_input_type: Optional[str] = "text"
    validation: Optional[Dict[str, Any]] = None


class SettingUpdate(BaseModel):
    """Request para actualizar setting"""
    value: Any
    ui_visible: Optional[bool] = None
    ui_order: Optional[int] = None
    ui_label: Optional[str] = None
    ui_help_text: Optional[str] = None


class SettingResponse(BaseModel):
    """Response de setting"""
    id: str
    category: SettingCategory
    key: str
    value: Any
    encrypted: bool
    ui_visible: bool
    ui_order: int
    ui_label: Optional[str]
    ui_help_text: Optional[str]
    ui_input_type: Optional[str]
    validation: Optional[Dict[str, Any]]
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True


# ════════════════════════════════════════════════════════════════════════
# EMAIL CONFIGURATION
# ════════════════════════════════════════════════════════════════════════

class EmailConfig(BaseModel):
    """
    Configuración de email (frontend UI)

    Example:
        {
            "enabled": true,
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_tls": true,
            "smtp_user": "noreply@oversun.com",
            "smtp_password": "***",
            "email_from": "OSE Platform <noreply@oversun.com>"
        }
    """
    enabled: bool = True
    smtp_host: str
    smtp_port: int = Field(..., ge=1, le=65535)
    smtp_tls: bool = True
    smtp_ssl: bool = False
    smtp_user: str
    smtp_password: str
    smtp_timeout: int = Field(default=30, ge=5, le=300)
    email_from: str
    email_reply_to: Optional[str] = None


class EmailConfigResponse(BaseModel):
    """Response de configuración de email (con password oculto)"""
    enabled: bool
    smtp_host: str
    smtp_port: int
    smtp_tls: bool
    smtp_ssl: bool
    smtp_user: str
    smtp_password: str = "********"  # Oculto
    smtp_timeout: int
    email_from: str
    email_reply_to: Optional[str]


class EmailTestRequest(BaseModel):
    """
    Request para probar conexión SMTP

    Example:
        {
            "test_connection_only": true
        }

    O enviar email de prueba:
        {
            "test_connection_only": false,
            "recipient": "test@example.com"
        }
    """
    test_connection_only: bool = True
    recipient: Optional[EmailStr] = None


class EmailTestResponse(BaseModel):
    """Response de prueba de email"""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None


# ════════════════════════════════════════════════════════════════════════
# SYSTEM CONFIGURATION
# ════════════════════════════════════════════════════════════════════════

class SystemConfigResponse(BaseModel):
    """
    Configuración general del sistema

    Example:
        {
            "app_name": "OSE Platform",
            "version": "1.0.0",
            "environment": "production",
            "features": {...}
        }
    """
    app_name: str
    version: str
    environment: str
    features: Dict[str, bool]
    limits: Dict[str, int]


class FeatureToggle(BaseModel):
    """Request para habilitar/deshabilitar feature"""
    feature: str
    enabled: bool


# ════════════════════════════════════════════════════════════════════════
# BULK SETTINGS
# ════════════════════════════════════════════════════════════════════════

class SettingsByCategoryResponse(BaseModel):
    """Response de settings agrupados por categoría"""
    category: SettingCategory
    settings: List[SettingResponse]


class BulkSettingsUpdate(BaseModel):
    """Request para actualizar múltiples settings"""
    updates: List[Dict[str, Any]] = Field(
        ...,
        description="Lista de {key: str, value: Any}"
    )
