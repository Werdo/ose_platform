"""
OSE Platform - Configuration Management
Sistema de configuración híbrido: .env + MongoDB
"""

from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
import os


class Settings(BaseSettings):
    """
    Configuración de la aplicación
    Lee desde .env y permite override desde MongoDB
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # ════════════════════════════════════════════════════════════════════
    # APLICACIÓN
    # ════════════════════════════════════════════════════════════════════

    APP_NAME: str = "OSE Platform"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Sistema de Gestión, Trazabilidad y Post-Venta - Oversun Energy"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    API_PREFIX: str = Field(default="/api/v1")

    # ════════════════════════════════════════════════════════════════════
    # SERVIDOR
    # ════════════════════════════════════════════════════════════════════

    BACKEND_HOST: str = Field(default="0.0.0.0")
    BACKEND_PORT: int = Field(default=8000)
    EXTERNAL_PORT: int = Field(default=8000)

    # ════════════════════════════════════════════════════════════════════
    # MONGODB
    # ════════════════════════════════════════════════════════════════════

    MONGODB_URI: str = Field(
        default="mongodb://localhost:27017",
        description="URI de conexión a MongoDB"
    )
    MONGODB_DB_NAME: str = Field(default="oversun_production")
    MONGODB_TIMEOUT: int = Field(default=5000)

    # Usuarios MongoDB (para el script de inicialización)
    MONGODB_ROOT_USER: str = Field(default="admin")
    MONGODB_ROOT_PASSWORD: str = Field(default="admin123")
    MONGODB_APP_USER: str = Field(default="ose_api")
    MONGODB_APP_PASSWORD: str = Field(default="ose_api_password")
    MONGODB_READONLY_USER: str = Field(default="ose_readonly")
    MONGODB_READONLY_PASSWORD: str = Field(default="ose_readonly_password")
    MONGODB_PORT: int = Field(default=27017)

    # ════════════════════════════════════════════════════════════════════
    # JWT - AUTENTICACIÓN
    # ════════════════════════════════════════════════════════════════════

    JWT_SECRET_KEY: str = Field(
        default="CHANGE_THIS_SECRET_KEY_IN_PRODUCTION",
        description="Clave secreta para firmar JWT tokens"
    )
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    JWT_ISSUER: str = Field(default="oversun-platform")

    # ════════════════════════════════════════════════════════════════════
    # SEGURIDAD
    # ════════════════════════════════════════════════════════════════════

    ENCRYPTION_SECRET_KEY: str = Field(
        default="CHANGE_THIS_ENCRYPTION_KEY_IN_PRODUCTION",
        description="Clave para encriptar datos sensibles"
    )
    PASSWORD_HASH_ROUNDS: int = Field(default=10)
    PASSWORD_MIN_LENGTH: int = Field(default=8)

    # ════════════════════════════════════════════════════════════════════
    # CORS
    # ════════════════════════════════════════════════════════════════════

    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173,http://localhost:8080"
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: str = Field(default="GET,POST,PUT,PATCH,DELETE,OPTIONS")
    CORS_ALLOW_HEADERS: str = Field(default="*")

    @property
    def cors_origins_list(self) -> List[str]:
        """Convierte string de orígenes a lista"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # ════════════════════════════════════════════════════════════════════
    # EMAIL / SMTP
    # ════════════════════════════════════════════════════════════════════

    EMAIL_ENABLED: bool = Field(default=True)
    SMTP_HOST: Optional[str] = Field(default=None)
    SMTP_PORT: Optional[int] = Field(default=587)
    SMTP_TLS: bool = Field(default=True)
    SMTP_SSL: bool = Field(default=False)
    SMTP_USER: Optional[str] = Field(default=None)
    SMTP_PASSWORD: Optional[str] = Field(default=None)
    SMTP_TIMEOUT: int = Field(default=10)

    EMAIL_FROM: Optional[str] = Field(default=None)
    EMAIL_REPLY_TO: Optional[str] = Field(default=None)
    EMAIL_ADMIN_COPY: Optional[str] = Field(default=None)

    @property
    def email_admin_copy_list(self) -> List[str]:
        """Convierte string de emails admin a lista"""
        if not self.EMAIL_ADMIN_COPY:
            return []
        return [email.strip() for email in self.EMAIL_ADMIN_COPY.split(",")]

    # ════════════════════════════════════════════════════════════════════
    # RATE LIMITING
    # ════════════════════════════════════════════════════════════════════

    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_REQUESTS_PER_SECOND: int = Field(default=10)
    RATE_LIMIT_BURST_SIZE: int = Field(default=20)
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)
    RATE_LIMIT_PER_HOUR: int = Field(default=1000)

    # ════════════════════════════════════════════════════════════════════
    # ARCHIVOS
    # ════════════════════════════════════════════════════════════════════

    MAX_FILE_SIZE_MB: int = Field(default=10)
    ALLOWED_FILE_TYPES: str = Field(default=".xlsx,.xls,.csv")
    TEMP_UPLOAD_PATH: str = Field(default="/tmp/ose_uploads")

    @property
    def allowed_file_types_list(self) -> List[str]:
        """Convierte string de tipos de archivo a lista"""
        return [ext.strip() for ext in self.ALLOWED_FILE_TYPES.split(",")]

    # ════════════════════════════════════════════════════════════════════
    # LOGGING
    # ════════════════════════════════════════════════════════════════════

    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")
    LOG_TO_FILE: bool = Field(default=True)
    LOG_FILE_PATH: str = Field(default="/var/log/ose/app.log")

    # ════════════════════════════════════════════════════════════════════
    # APLICACIONES ESPECÍFICAS
    # ════════════════════════════════════════════════════════════════════

    # App 1 - Notificación de Series
    APP1_ENABLED: bool = Field(default=True)
    APP1_CSV_FORMAT_DEFAULT: str = Field(default="unified")

    # App 2 - Importación de Datos
    APP2_ENABLED: bool = Field(default=True)
    APP2_AUTO_VALIDATE: bool = Field(default=True)
    APP2_ALLOW_DUPLICATES: bool = Field(default=False)

    # App 3 - RMA & Tickets
    APP3_ENABLED: bool = Field(default=True)
    APP3_AUTO_ASSIGN_TECHNICIAN: bool = Field(default=False)
    APP3_SLA_HOURS_CRITICAL: int = Field(default=4)
    APP3_SLA_HOURS_HIGH: int = Field(default=24)
    APP3_SLA_HOURS_MEDIUM: int = Field(default=72)
    APP3_SLA_HOURS_LOW: int = Field(default=168)

    # App 4 - Import Transform
    APP4_ENABLED: bool = Field(default=True)

    # App 5 - Factura Ticket
    APP5_ENABLED: bool = Field(default=True)

    # App 6 - Picking Palets
    APP6_ENABLED: bool = Field(default=True)

    # ════════════════════════════════════════════════════════════════════
    # INTEGRACIONES EXTERNAS
    # ════════════════════════════════════════════════════════════════════

    SEUR_API_KEY: Optional[str] = Field(default=None)
    SEUR_API_URL: str = Field(default="https://api.seur.com/v1")

    CORREOS_API_KEY: Optional[str] = Field(default=None)
    CORREOS_API_URL: str = Field(default="https://api.correos.es/v1")

    # ════════════════════════════════════════════════════════════════════
    # DESARROLLO
    # ════════════════════════════════════════════════════════════════════

    AUTO_RELOAD: bool = Field(default=True)
    SHOW_QUERIES: bool = Field(default=False)
    SEED_DATABASE: bool = Field(default=False)

    # ════════════════════════════════════════════════════════════════════
    # VALIDADORES
    # ════════════════════════════════════════════════════════════════════

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Valida que el entorno sea válido"""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENVIRONMENT debe ser uno de: {allowed}")
        return v

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Valida el nivel de logging"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL debe ser uno de: {allowed}")
        return v.upper()

    @validator("SMTP_PORT")
    def validate_smtp_port(cls, v):
        """Valida que el puerto SMTP sea válido"""
        if v and not (1 <= v <= 65535):
            raise ValueError("SMTP_PORT debe estar entre 1 y 65535")
        return v

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ÚTILES
    # ════════════════════════════════════════════════════════════════════

    @property
    def is_production(self) -> bool:
        """Verifica si estamos en producción"""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Verifica si estamos en desarrollo"""
        return self.ENVIRONMENT == "development"

    def get_database_url(self) -> str:
        """Retorna la URL de la base de datos"""
        return self.MONGODB_URI


# ════════════════════════════════════════════════════════════════════════
# INSTANCIA GLOBAL DE CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════════════

settings = Settings()


# ════════════════════════════════════════════════════════════════════════
# SISTEMA DE CONFIGURACIÓN DINÁMICA (MongoDB override)
# ════════════════════════════════════════════════════════════════════════

class DynamicConfig:
    """
    Sistema de configuración dinámica que permite
    override de valores desde MongoDB
    """

    def __init__(self):
        self._cache = {}
        self._db = None

    def set_database(self, db):
        """Establece la referencia a la base de datos"""
        self._db = db

    async def get(self, key: str, default=None):
        """
        Obtiene un valor de configuración con el siguiente orden de prioridad:
        1. MongoDB (settings collection)
        2. .env (Settings class)
        3. Default value
        """
        # 1. Intentar desde caché
        if key in self._cache:
            return self._cache[key]

        # 2. Intentar desde MongoDB
        if self._db:
            try:
                from app.models.setting import SystemSetting
                setting = await SystemSetting.find_one(
                    SystemSetting.key == key,
                    SystemSetting.active == True
                )
                if setting:
                    value = setting.get_decrypted_value()
                    self._cache[key] = value
                    return value
            except Exception as e:
                # Si falla, continuar con .env
                pass

        # 3. Desde settings (.env)
        env_value = getattr(settings, key.upper(), None)
        if env_value is not None:
            return env_value

        # 4. Default
        return default

    async def set(self, key: str, value, encrypted: bool = False, updated_by: str = None):
        """
        Guarda un valor de configuración en MongoDB
        """
        if not self._db:
            raise RuntimeError("Database not initialized")

        from app.models.setting import SystemSetting

        setting = await SystemSetting.find_one(SystemSetting.key == key)

        if setting:
            # Actualizar existente
            setting.value = value
            setting.encrypted = encrypted
            if updated_by:
                setting.updated_by = updated_by
            await setting.save()
        else:
            # Crear nuevo
            setting = SystemSetting(
                key=key,
                value=value,
                encrypted=encrypted,
                updated_by=updated_by
            )
            await setting.insert()

        # Actualizar caché
        self._cache[key] = value

        return setting

    def clear_cache(self):
        """Limpia el caché de configuración"""
        self._cache.clear()

    async def reload(self):
        """Recarga toda la configuración desde MongoDB"""
        self.clear_cache()

        if not self._db:
            return

        try:
            from app.models.setting import SystemSetting
            settings_list = await SystemSetting.find(
                SystemSetting.active == True
            ).to_list()

            for setting in settings_list:
                self._cache[setting.key] = setting.get_decrypted_value()
        except Exception as e:
            # Si falla, usar valores de .env
            pass


# Instancia global de configuración dinámica
dynamic_config = DynamicConfig()
