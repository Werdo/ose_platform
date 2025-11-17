"""
OSE Platform - System Log Model
Modelo para almacenar logs del sistema en MongoDB
"""

from datetime import datetime
from typing import Optional, Dict, Any
from beanie import Document
from pydantic import Field
from enum import Enum


class LogLevel(str, Enum):
    """Niveles de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(str, Enum):
    """Categorías de log"""
    SYSTEM = "system"
    AUTH = "auth"
    API = "api"
    DATABASE = "database"
    IMPORT = "import"
    EXPORT = "export"
    EMAIL = "email"
    RMA = "rma"
    PICKING = "picking"
    INVOICE = "invoice"
    NOTIFICATION = "notification"
    SECURITY = "security"
    ERROR = "error"


class SystemLog(Document):
    """
    Modelo de Log del Sistema

    Almacena todos los eventos importantes del sistema para auditoría y debugging
    """

    # Información básica del log
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    level: LogLevel = Field(default=LogLevel.INFO)
    category: LogCategory = Field(default=LogCategory.SYSTEM)

    # Mensaje del log
    message: str = Field(..., min_length=1, max_length=2000)

    # Contexto adicional
    module: Optional[str] = Field(None, description="Módulo que generó el log")
    function: Optional[str] = Field(None, description="Función que generó el log")

    # Usuario relacionado
    user_id: Optional[str] = Field(None, description="ID del usuario relacionado")
    user_email: Optional[str] = Field(None, description="Email del usuario")

    # Request info
    endpoint: Optional[str] = Field(None, description="Endpoint API llamado")
    method: Optional[str] = Field(None, description="Método HTTP (GET, POST, etc)")
    ip_address: Optional[str] = Field(None, description="IP del cliente")
    user_agent: Optional[str] = Field(None, description="User agent del navegador")

    # Datos adicionales
    data: Optional[Dict[str, Any]] = Field(None, description="Datos adicionales en formato JSON")

    # Error info (si aplica)
    error_type: Optional[str] = Field(None, description="Tipo de error")
    error_message: Optional[str] = Field(None, description="Mensaje de error")
    stack_trace: Optional[str] = Field(None, description="Stack trace del error")

    # Performance
    duration_ms: Optional[float] = Field(None, description="Duración de la operación en ms")

    # Metadata
    environment: str = Field(default="production", description="Entorno: development, staging, production")
    server_hostname: Optional[str] = Field(None, description="Nombre del servidor")

    class Settings:
        name = "system_logs"
        indexes = [
            "timestamp",
            "level",
            "category",
            "user_email",
            "endpoint",
            [("timestamp", -1)],  # Índice descendente por timestamp
            [("level", 1), ("timestamp", -1)],
            [("category", 1), ("timestamp", -1)],
        ]

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2025-11-15T10:30:00",
                "level": "INFO",
                "category": "import",
                "message": "Importación de 1000 dispositivos completada exitosamente",
                "module": "app.routers.app2_import",
                "function": "upload_file",
                "user_email": "admin@ose.com",
                "endpoint": "/api/v1/app2/upload",
                "method": "POST",
                "data": {
                    "total_rows": 1000,
                    "success": 1000,
                    "errors": 0
                },
                "duration_ms": 2350.5
            }
        }

    def __repr__(self) -> str:
        return f"<SystemLog {self.level} [{self.category}] {self.message[:50]}>"

    def __str__(self) -> str:
        return f"[{self.timestamp}] {self.level} - {self.category}: {self.message}"
