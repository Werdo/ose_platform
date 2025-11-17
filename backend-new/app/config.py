"""
OSE Platform - Configuration
Centralización de configuración y variables de entorno
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union
from functools import lru_cache


class Settings(BaseSettings):
    """
    Configuración global de la aplicación
    Carga desde variables de entorno o archivo .env
    """

    # ════════════════════════════════════════════════════════════════════
    # APLICACIÓN
    # ════════════════════════════════════════════════════════════════════
    APP_NAME: str = "OSE Platform API"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True

    # ════════════════════════════════════════════════════════════════════
    # API
    # ════════════════════════════════════════════════════════════════════
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",  # Public Portal
        "http://localhost:3004",  # Admin Portal (alternate port)
        "http://localhost:5173",
        "http://localhost:5006",  # Picking Portal
        "http://localhost:5007",  # Picking Portal (alternate)
        "http://localhost:5008",  # Picking Portal (alternate 2)
        "http://localhost:5009",  # Picking Portal (alternate 3)
        "http://localhost:5010",  # Picking Portal (alternate 4)
        "http://localhost:5011",  # Picking Portal (alternate 5)
        "http://localhost:5012",  # Picking Portal (alternate 6)
        "http://localhost:8080"
    ]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    # ════════════════════════════════════════════════════════════════════
    # MONGODB
    # ════════════════════════════════════════════════════════════════════
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "ose_platform"
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 50
    MONGODB_TIMEOUT: int = 5000

    # ════════════════════════════════════════════════════════════════════
    # AUTENTICACIÓN JWT
    # ════════════════════════════════════════════════════════════════════
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars-long"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Encryption (for sensitive data in DB like API keys, passwords)
    ENCRYPTION_KEY: Optional[str] = None

    # ════════════════════════════════════════════════════════════════════
    # SMTP / EMAIL
    # ════════════════════════════════════════════════════════════════════
    SMTP_ENABLED: bool = True
    SMTP_HOST: str = "smtp.dondominio.com"
    SMTP_PORT: int = 587
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_USER: str = "serviciorma@neowaybyose.com"
    SMTP_PASSWORD: str = "@S1i9m8o1n"
    SMTP_TIMEOUT: int = 30

    # Cuentas de correo configuradas:
    # - RMA y Notificaciones: serviciorma@neowaybyose.com (@S1i9m8o1n)
    # - Trazabilidad: trazabilidad@neowaybyose.com (@S1i9m8o1n)

    EMAIL_FROM: str = "serviciorma@neowaybyose.com"
    EMAIL_FROM_NAME: str = "OSE Platform - Servicio RMA"
    EMAIL_REPLY_TO: Optional[str] = "serviciorma@neowaybyose.com"
    EMAIL_SUPPORT: str = "serviciorma@neowaybyose.com"

    # Cuenta alternativa para trazabilidad (puede usarse en módulos específicos)
    EMAIL_TRACKING: str = "trazabilidad@neowaybyose.com"
    EMAIL_TRACKING_PASSWORD: str = "@S1i9m8o1n"

    # Frontend URL (for emails with links)
    FRONTEND_URL: str = "http://localhost:3000"

    # ════════════════════════════════════════════════════════════════════
    # PDF GENERATION
    # ════════════════════════════════════════════════════════════════════
    PDF_FONT_FAMILY: str = "Arial, sans-serif"
    PDF_PAGE_SIZE: str = "A4"
    PDF_MARGIN: str = "20mm"
    PDF_DPI: int = 96

    # ════════════════════════════════════════════════════════════════════
    # ARCHIVOS Y UPLOADS
    # ════════════════════════════════════════════════════════════════════
    UPLOAD_DIR: str = "/tmp/ose_uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: List[str] = [".csv", ".xlsx", ".xls", ".pdf", ".jpg", ".png"]

    # ════════════════════════════════════════════════════════════════════
    # TEMPLATES
    # ════════════════════════════════════════════════════════════════════
    TEMPLATES_DIR: str = "platform/templates"
    STATIC_DIR: str = "platform/static"

    # ════════════════════════════════════════════════════════════════════
    # LOGGING
    # ════════════════════════════════════════════════════════════════════
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE: str = "/var/log/ose/app.log"
    LOG_JSON: bool = True
    LOG_ROTATION: str = "1 day"
    LOG_RETENTION: str = "30 days"

    # ════════════════════════════════════════════════════════════════════
    # RATE LIMITING
    # ════════════════════════════════════════════════════════════════════
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # ════════════════════════════════════════════════════════════════════
    # EMPRESA / ORGANIZACIÓN
    # ════════════════════════════════════════════════════════════════════
    COMPANY_NAME: str = "Oversun Energy"
    COMPANY_EMAIL: str = "info@oversunenergy.com"
    COMPANY_WEBSITE: str = "https://oversunenergy.com"
    COMPANY_PHONE: str = "+34 XXX XXX XXX"
    COMPANY_ADDRESS: str = "C/ Dirección, CP, Ciudad, País"
    COMPANY_LOGO_URL: str = "/static/logo.png"

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN POR DEFECTO
    # ════════════════════════════════════════════════════════════════════
    DEFAULT_LANGUAGE: str = "es"
    DEFAULT_TIMEZONE: str = "Europe/Madrid"
    DEFAULT_CURRENCY: str = "EUR"

    # ════════════════════════════════════════════════════════════════════
    # CARACTERÍSTICAS / FEATURE FLAGS
    # ════════════════════════════════════════════════════════════════════
    FEATURE_APP1_ENABLED: bool = True  # Notificación series
    FEATURE_APP2_ENABLED: bool = True  # Importación datos
    FEATURE_APP3_ENABLED: bool = True  # RMA & Tickets
    FEATURE_APP4_ENABLED: bool = True  # Transform docs
    FEATURE_APP5_ENABLED: bool = True  # Facturas
    FEATURE_APP6_ENABLED: bool = True  # Picking

    # ════════════════════════════════════════════════════════════════════
    # VALIDACIÓN DE BUSINESS LOGIC
    # ════════════════════════════════════════════════════════════════════
    IMEI_LENGTH: int = 15
    ICCID_MIN_LENGTH: int = 19
    ICCID_MAX_LENGTH: int = 22
    PACKAGE_NO_LENGTH: int = 25
    PACKAGE_NO_PREFIX: str = "99"

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE PYDANTIC SETTINGS
    # ════════════════════════════════════════════════════════════════════
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna la configuración (cached)
    Use esta función para obtener settings en toda la aplicación
    """
    return Settings()


# Instancia global de settings
settings = get_settings()
