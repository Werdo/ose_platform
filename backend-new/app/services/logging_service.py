"""
OSE Platform - Logging Service
Servicio centralizado para logging con almacenamiento en MongoDB
"""

import logging
import traceback
import socket
from datetime import datetime
from typing import Optional, Dict, Any
from app.models.system_log import SystemLog, LogLevel, LogCategory


class MongoDBHandler(logging.Handler):
    """Handler personalizado para guardar logs en MongoDB"""

    def __init__(self):
        super().__init__()
        self.hostname = socket.gethostname()

    def emit(self, record: logging.LogRecord):
        """Guarda el log en MongoDB"""
        try:
            # Mapear nivel de logging a LogLevel
            level_mapping = {
                logging.DEBUG: LogLevel.DEBUG,
                logging.INFO: LogLevel.INFO,
                logging.WARNING: LogLevel.WARNING,
                logging.ERROR: LogLevel.ERROR,
                logging.CRITICAL: LogLevel.CRITICAL,
            }

            # Extraer información del record
            log_data = {
                "timestamp": datetime.fromtimestamp(record.created),
                "level": level_mapping.get(record.levelno, LogLevel.INFO),
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "server_hostname": self.hostname,
            }

            # Agregar categoría si está disponible
            if hasattr(record, 'category'):
                log_data["category"] = record.category
            else:
                # Inferir categoría del módulo
                log_data["category"] = self._infer_category(record.module)

            # Agregar información de usuario si está disponible
            if hasattr(record, 'user_email'):
                log_data["user_email"] = record.user_email
            if hasattr(record, 'user_id'):
                log_data["user_id"] = record.user_id

            # Agregar información de request si está disponible
            if hasattr(record, 'endpoint'):
                log_data["endpoint"] = record.endpoint
            if hasattr(record, 'method'):
                log_data["method"] = record.method
            if hasattr(record, 'ip_address'):
                log_data["ip_address"] = record.ip_address

            # Agregar datos adicionales
            if hasattr(record, 'data'):
                log_data["data"] = record.data

            # Agregar duración si está disponible
            if hasattr(record, 'duration_ms'):
                log_data["duration_ms"] = record.duration_ms

            # Si es un error, agregar información del error
            if record.exc_info:
                log_data["error_type"] = record.exc_info[0].__name__ if record.exc_info[0] else None
                log_data["error_message"] = str(record.exc_info[1]) if record.exc_info[1] else None
                log_data["stack_trace"] = ''.join(traceback.format_exception(*record.exc_info))

            # Crear y guardar el log (de forma asíncrona)
            # Nota: Beanie requiere contexto async, así que usamos create_sync
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Si hay un loop corriendo, crear tarea
                    loop.create_task(SystemLog(**log_data).insert())
                else:
                    # Si no hay loop, usar run_until_complete
                    loop.run_until_complete(SystemLog(**log_data).insert())
            except RuntimeError:
                # Si falla, simplemente no guardamos en DB (evitar que crashee)
                pass

        except Exception as e:
            # No queremos que un error en el logging crashee la aplicación
            print(f"Error guardando log en MongoDB: {e}")

    def _infer_category(self, module: str) -> LogCategory:
        """Infiere la categoría del log basándose en el módulo"""
        if 'auth' in module.lower():
            return LogCategory.AUTH
        elif 'app2' in module or 'import' in module.lower():
            return LogCategory.IMPORT
        elif 'app3' in module or 'rma' in module.lower():
            return LogCategory.RMA
        elif 'app5' in module or 'invoice' in module.lower():
            return LogCategory.INVOICE
        elif 'app6' in module or 'picking' in module.lower():
            return LogCategory.PICKING
        elif 'app1' in module or 'notif' in module.lower():
            return LogCategory.NOTIFICATION
        elif 'database' in module.lower():
            return LogCategory.DATABASE
        elif 'email' in module.lower() or 'mail' in module.lower():
            return LogCategory.EMAIL
        else:
            return LogCategory.SYSTEM


class LoggingService:
    """Servicio centralizado de logging"""

    @staticmethod
    def setup_logging(level: str = "INFO"):
        """
        Configura el sistema de logging

        Args:
            level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        # Configurar nivel de logging
        log_level = getattr(logging, level.upper(), logging.INFO)

        # Obtener el logger raíz
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Limpiar handlers existentes
        root_logger.handlers.clear()

        # Formato de logging para consola
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

        # Handler para MongoDB
        mongodb_handler = MongoDBHandler()
        mongodb_handler.setLevel(logging.INFO)  # Solo INFO y superior a MongoDB
        root_logger.addHandler(mongodb_handler)

        logging.info("Sistema de logging configurado correctamente")

    @staticmethod
    async def log(
        level: LogLevel,
        message: str,
        category: LogCategory = LogCategory.SYSTEM,
        user_email: Optional[str] = None,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        ip_address: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
        error_type: Optional[str] = None,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
    ) -> SystemLog:
        """
        Crea un log directamente en la base de datos

        Args:
            level: Nivel del log
            message: Mensaje del log
            category: Categoría del log
            user_email: Email del usuario
            user_id: ID del usuario
            endpoint: Endpoint API
            method: Método HTTP
            ip_address: IP del cliente
            data: Datos adicionales
            duration_ms: Duración de la operación
            error_type: Tipo de error
            error_message: Mensaje de error
            stack_trace: Stack trace del error

        Returns:
            SystemLog creado
        """
        log = SystemLog(
            level=level,
            message=message,
            category=category,
            user_email=user_email,
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            ip_address=ip_address,
            data=data,
            duration_ms=duration_ms,
            error_type=error_type,
            error_message=error_message,
            stack_trace=stack_trace,
            server_hostname=socket.gethostname(),
        )

        await log.insert()
        return log

    @staticmethod
    async def log_request(
        endpoint: str,
        method: str,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        duration_ms: Optional[float] = None,
        status_code: int = 200,
    ):
        """Log de requests HTTP"""
        level = LogLevel.INFO if status_code < 400 else LogLevel.ERROR
        message = f"{method} {endpoint} - {status_code}"

        await LoggingService.log(
            level=level,
            message=message,
            category=LogCategory.API,
            user_email=user_email,
            endpoint=endpoint,
            method=method,
            ip_address=ip_address,
            duration_ms=duration_ms,
            data={"status_code": status_code}
        )

    @staticmethod
    async def log_import(
        total: int,
        success: int,
        failed: int,
        user_email: str,
        duration_ms: float,
        errors: Optional[list] = None,
    ):
        """Log específico para importaciones"""
        message = f"Importación: {success}/{total} exitosos, {failed} fallidos"

        await LoggingService.log(
            level=LogLevel.INFO,
            message=message,
            category=LogCategory.IMPORT,
            user_email=user_email,
            duration_ms=duration_ms,
            data={
                "total": total,
                "success": success,
                "failed": failed,
                "errors": errors[:10] if errors else []  # Solo primeros 10 errores
            }
        )

    @staticmethod
    async def log_error(
        message: str,
        category: LogCategory = LogCategory.ERROR,
        user_email: Optional[str] = None,
        endpoint: Optional[str] = None,
        exception: Optional[Exception] = None,
    ):
        """Log de errores"""
        error_data = {}
        if exception:
            error_data = {
                "error_type": type(exception).__name__,
                "error_message": str(exception),
                "stack_trace": ''.join(traceback.format_tb(exception.__traceback__))
            }

        await LoggingService.log(
            level=LogLevel.ERROR,
            message=message,
            category=category,
            user_email=user_email,
            endpoint=endpoint,
            **error_data
        )


# Instancia global del servicio
logging_service = LoggingService()
