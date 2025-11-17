"""
OSE Platform - System Settings Model
Modelo para configuración dinámica del sistema
"""

from beanie import Document
from pydantic import Field
from typing import Optional, Any, Dict
from datetime import datetime
from enum import Enum


class SettingCategory(str, Enum):
    """Categorías de configuración"""
    EMAIL = "email"
    SMTP = "smtp"
    JWT = "jwt"
    SECURITY = "security"
    CORS = "cors"
    APP = "app"
    INTEGRATIONS = "integrations"
    RATE_LIMIT = "rate_limit"
    FILES = "files"
    LOGGING = "logging"
    CUSTOM = "custom"


class SystemSetting(Document):
    """
    Configuración del sistema almacenada en MongoDB
    Permite override de configuraciones desde la interfaz de administración
    """

    # ════════════════════════════════════════════════════════════════════
    # CAMPOS PRINCIPALES
    # ════════════════════════════════════════════════════════════════════

    category: SettingCategory = Field(
        description="Categoría de la configuración"
    )

    key: str = Field(
        ...,
        description="Clave única de la configuración (ej: smtp_host)",
        index=True
    )

    value: Any = Field(
        ...,
        description="Valor de la configuración (puede ser cualquier tipo)"
    )

    # ════════════════════════════════════════════════════════════════════
    # METADATA
    # ════════════════════════════════════════════════════════════════════

    description: Optional[str] = Field(
        default=None,
        description="Descripción de qué hace esta configuración"
    )

    encrypted: bool = Field(
        default=False,
        description="Si el valor está encriptado (para contraseñas, API keys, etc.)"
    )

    required: bool = Field(
        default=False,
        description="Si esta configuración es requerida para el funcionamiento"
    )

    active: bool = Field(
        default=True,
        description="Si esta configuración está activa"
    )

    # ════════════════════════════════════════════════════════════════════
    # UI - INTERFAZ DE ADMINISTRACIÓN
    # ════════════════════════════════════════════════════════════════════

    ui_visible: bool = Field(
        default=True,
        description="Si debe mostrarse en la interfaz de administración"
    )

    ui_order: int = Field(
        default=0,
        description="Orden en que se muestra en la UI"
    )

    ui_input_type: Optional[str] = Field(
        default="text",
        description="Tipo de input en la UI (text, password, number, select, checkbox, etc.)"
    )

    ui_placeholder: Optional[str] = Field(
        default=None,
        description="Placeholder para el campo en la UI"
    )

    ui_help_text: Optional[str] = Field(
        default=None,
        description="Texto de ayuda que se muestra en la UI"
    )

    # ════════════════════════════════════════════════════════════════════
    # VALIDACIÓN
    # ════════════════════════════════════════════════════════════════════

    validation: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Reglas de validación (type, pattern, min, max, etc.)"
    )

    # Ejemplos de validation:
    # {
    #     "type": "string",
    #     "pattern": "^smtp\\.",
    #     "min_length": 5,
    #     "max_length": 100
    # }
    # {
    #     "type": "number",
    #     "min": 1,
    #     "max": 65535
    # }
    # {
    #     "type": "enum",
    #     "values": ["option1", "option2", "option3"]
    # }

    # ════════════════════════════════════════════════════════════════════
    # AUDITORÍA
    # ════════════════════════════════════════════════════════════════════

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )

    updated_by: Optional[str] = Field(
        default=None,
        description="ID del usuario que actualizó por última vez"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "settings"
        indexes = [
            "key",
            "category",
            "active",
            [("category", 1), ("key", 1)]  # Índice compuesto
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ════════════════════════════════════════════════════════════════════

    def get_decrypted_value(self) -> Any:
        """
        Retorna el valor desencriptado si está encriptado
        Si no está encriptado, retorna el valor tal cual
        """
        if not self.encrypted:
            return self.value

        # Importar aquí para evitar importaciones circulares
        from app.utils.security import decrypt_value

        try:
            return decrypt_value(self.value)
        except Exception as e:
            # Si falla la desencriptación, retornar el valor original
            return self.value

    def set_encrypted_value(self, value: Any):
        """
        Encripta y establece el valor
        """
        from app.utils.security import encrypt_value

        self.value = encrypt_value(value)
        self.encrypted = True

    async def save_with_audit(self, updated_by: str):
        """
        Guarda el setting actualizando metadata de auditoría
        """
        self.updated_at = datetime.utcnow()
        self.updated_by = updated_by
        await self.save()

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS - HELPERS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def get_value(key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración por su clave
        Retorna el valor desencriptado si existe, sino el default
        """
        setting = await SystemSetting.find_one(
            SystemSetting.key == key,
            SystemSetting.active == True
        )

        if setting:
            return setting.get_decrypted_value()

        return default

    @staticmethod
    async def set_value(
        key: str,
        value: Any,
        category: SettingCategory = SettingCategory.CUSTOM,
        encrypted: bool = False,
        updated_by: Optional[str] = None,
        **kwargs
    ) -> "SystemSetting":
        """
        Establece un valor de configuración
        Si ya existe, lo actualiza. Si no, lo crea.
        """
        setting = await SystemSetting.find_one(SystemSetting.key == key)

        if setting:
            # Actualizar existente
            if encrypted:
                setting.set_encrypted_value(value)
            else:
                setting.value = value

            setting.updated_at = datetime.utcnow()
            if updated_by:
                setting.updated_by = updated_by

            # Actualizar otros campos si se proporcionan
            for k, v in kwargs.items():
                if hasattr(setting, k):
                    setattr(setting, k, v)

            await setting.save()
        else:
            # Crear nuevo
            setting_data = {
                "category": category,
                "key": key,
                "value": value,
                "encrypted": encrypted,
                "updated_by": updated_by,
                **kwargs
            }

            setting = SystemSetting(**setting_data)

            if encrypted:
                setting.set_encrypted_value(value)

            await setting.insert()

        return setting

    @staticmethod
    async def get_by_category(category: SettingCategory, active_only: bool = True):
        """
        Obtiene todas las configuraciones de una categoría
        """
        query = SystemSetting.find(SystemSetting.category == category)

        if active_only:
            query = query.find(SystemSetting.active == True)

        return await query.to_list()

    @staticmethod
    async def delete_setting(key: str, hard_delete: bool = False):
        """
        Elimina una configuración
        Por defecto hace soft delete (active = False)
        Si hard_delete = True, elimina permanentemente
        """
        setting = await SystemSetting.find_one(SystemSetting.key == key)

        if not setting:
            return False

        if hard_delete:
            await setting.delete()
        else:
            setting.active = False
            setting.updated_at = datetime.utcnow()
            await setting.save()

        return True


# ════════════════════════════════════════════════════════════════════════
# CONFIGURACIONES PREDEFINIDAS
# ════════════════════════════════════════════════════════════════════════

DEFAULT_SETTINGS = [
    # ──────────────────────────────────────────────────────────────────
    # EMAIL / SMTP
    # ──────────────────────────────────────────────────────────────────
    {
        "category": SettingCategory.EMAIL,
        "key": "email_enabled",
        "value": False,
        "description": "Habilitar o deshabilitar el envío de emails",
        "ui_visible": True,
        "ui_order": 1,
        "ui_input_type": "checkbox",
        "validation": {"type": "boolean"}
    },
    {
        "category": SettingCategory.SMTP,
        "key": "smtp_host",
        "value": None,
        "description": "Servidor SMTP (ej: smtp.gmail.com)",
        "ui_visible": True,
        "ui_order": 2,
        "ui_input_type": "text",
        "ui_placeholder": "smtp.gmail.com",
        "ui_help_text": "Servidor SMTP para envío de emails",
        "validation": {"type": "string", "min_length": 3}
    },
    {
        "category": SettingCategory.SMTP,
        "key": "smtp_port",
        "value": 587,
        "description": "Puerto SMTP (587 para TLS, 465 para SSL)",
        "ui_visible": True,
        "ui_order": 3,
        "ui_input_type": "number",
        "validation": {"type": "number", "min": 1, "max": 65535}
    },
    {
        "category": SettingCategory.SMTP,
        "key": "smtp_user",
        "value": None,
        "description": "Usuario SMTP (email completo)",
        "ui_visible": True,
        "ui_order": 4,
        "ui_input_type": "email",
        "ui_placeholder": "notificaciones@empresa.com"
    },
    {
        "category": SettingCategory.SMTP,
        "key": "smtp_password",
        "value": None,
        "description": "Contraseña SMTP o App Password",
        "encrypted": True,
        "ui_visible": True,
        "ui_order": 5,
        "ui_input_type": "password",
        "ui_help_text": "Para Gmail usar App Password"
    },
    {
        "category": SettingCategory.EMAIL,
        "key": "email_from",
        "value": None,
        "description": "Email remitente (FROM)",
        "ui_visible": True,
        "ui_order": 6,
        "ui_input_type": "text",
        "ui_placeholder": "\"OSE Platform <notificaciones@empresa.com>\""
    },
]


async def seed_default_settings():
    """
    Crea las configuraciones predefinidas si no existen
    Útil para inicialización de la BD
    """
    for setting_data in DEFAULT_SETTINGS:
        existing = await SystemSetting.find_one(
            SystemSetting.key == setting_data["key"]
        )

        if not existing:
            setting = SystemSetting(**setting_data)
            await setting.insert()
