"""
OSE Platform - Logging Middleware
Middleware para logging de requests y auditoría
"""

import time
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers
import logging

from app.config import settings

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════
# REQUEST LOGGING MIDDLEWARE
# ════════════════════════════════════════════════════════════════════════

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging detallado de requests y responses

    Registra:
    - Método HTTP y path
    - IP del cliente
    - User-Agent
    - Tiempo de procesamiento
    - Status code
    - Usuario autenticado (si aplica)
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Procesa y registra cada request
        """
        # Info de la request
        method = request.method
        path = request.url.path
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "unknown")

        # Timestamp de inicio
        start_time = time.time()

        # ID único para la request (para tracing)
        request_id = self._generate_request_id()
        request.state.request_id = request_id

        # Log de request entrante (solo en debug)
        if settings.LOG_LEVEL == "DEBUG":
            logger.debug(
                f"[{request_id}] {method} {path} - IP: {client_ip} - UA: {user_agent[:50]}"
            )

        # Procesar request
        try:
            response = await call_next(request)

            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time

            # Añadir headers personalizados
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.3f}s"

            # Log de response
            self._log_response(
                request_id=request_id,
                method=method,
                path=path,
                status_code=response.status_code,
                process_time=process_time,
                client_ip=client_ip
            )

            return response

        except Exception as e:
            # Log de error
            process_time = time.time() - start_time
            logger.error(
                f"[{request_id}] {method} {path} - ERROR after {process_time:.3f}s: {str(e)}",
                exc_info=True
            )
            raise

    def _log_response(
        self,
        request_id: str,
        method: str,
        path: str,
        status_code: int,
        process_time: float,
        client_ip: str
    ):
        """
        Registra la response

        Nivel de log según status code:
        - 2xx: INFO
        - 3xx: INFO
        - 4xx: WARNING
        - 5xx: ERROR
        """
        log_msg = f"[{request_id}] {method} {path} - {status_code} - {process_time:.3f}s - {client_ip}"

        if status_code < 400:
            logger.info(log_msg)
        elif status_code < 500:
            logger.warning(log_msg)
        else:
            logger.error(log_msg)

    def _get_client_ip(self, request: Request) -> str:
        """Obtiene la IP del cliente"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _generate_request_id(self) -> str:
        """Genera un ID único para la request"""
        import uuid
        return str(uuid.uuid4())[:8]


# ════════════════════════════════════════════════════════════════════════
# AUDIT LOGGING
# ════════════════════════════════════════════════════════════════════════

class AuditLogger:
    """
    Logger especializado para acciones críticas de auditoría

    Uso:
        audit_logger.log_login(user_id, ip, success=True)
        audit_logger.log_data_access(user_id, resource, action)
    """

    def __init__(self):
        self.logger = logging.getLogger("audit")

    def log_login(
        self,
        user_id: str,
        username: str,
        ip: str,
        success: bool,
        reason: str = None
    ):
        """Registra intento de login"""
        self.logger.info(
            f"LOGIN - User: {username} ({user_id}) - IP: {ip} - "
            f"Success: {success}" + (f" - Reason: {reason}" if reason else "")
        )

    def log_logout(self, user_id: str, username: str, ip: str):
        """Registra logout"""
        self.logger.info(f"LOGOUT - User: {username} ({user_id}) - IP: {ip}")

    def log_data_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        resource_id: str = None,
        ip: str = None
    ):
        """
        Registra acceso a datos

        Args:
            user_id: ID del usuario
            resource: Tipo de recurso (device, customer, ticket, etc.)
            action: Acción realizada (read, create, update, delete)
            resource_id: ID específico del recurso
            ip: IP del cliente
        """
        self.logger.info(
            f"DATA_ACCESS - User: {user_id} - Action: {action} - "
            f"Resource: {resource}" +
            (f" - ID: {resource_id}" if resource_id else "") +
            (f" - IP: {ip}" if ip else "")
        )

    def log_configuration_change(
        self,
        user_id: str,
        setting_key: str,
        old_value: str,
        new_value: str,
        ip: str = None
    ):
        """Registra cambios en configuración del sistema"""
        self.logger.warning(
            f"CONFIG_CHANGE - User: {user_id} - Setting: {setting_key} - "
            f"Old: {old_value} - New: {new_value}" +
            (f" - IP: {ip}" if ip else "")
        )

    def log_permission_denied(
        self,
        user_id: str,
        resource: str,
        action: str,
        reason: str,
        ip: str = None
    ):
        """Registra intento de acceso denegado"""
        self.logger.warning(
            f"PERMISSION_DENIED - User: {user_id} - Action: {action} - "
            f"Resource: {resource} - Reason: {reason}" +
            (f" - IP: {ip}" if ip else "")
        )

    def log_data_export(
        self,
        user_id: str,
        resource: str,
        count: int,
        format: str,
        ip: str = None
    ):
        """Registra exportación de datos"""
        self.logger.info(
            f"DATA_EXPORT - User: {user_id} - Resource: {resource} - "
            f"Count: {count} - Format: {format}" +
            (f" - IP: {ip}" if ip else "")
        )

    def log_bulk_operation(
        self,
        user_id: str,
        operation: str,
        resource: str,
        count: int,
        ip: str = None
    ):
        """Registra operaciones masivas"""
        self.logger.warning(
            f"BULK_OPERATION - User: {user_id} - Operation: {operation} - "
            f"Resource: {resource} - Count: {count}" +
            (f" - IP: {ip}" if ip else "")
        )

    def log_security_event(
        self,
        event_type: str,
        user_id: str = None,
        ip: str = None,
        details: str = None
    ):
        """Registra eventos de seguridad"""
        self.logger.error(
            f"SECURITY_EVENT - Type: {event_type}" +
            (f" - User: {user_id}" if user_id else "") +
            (f" - IP: {ip}" if ip else "") +
            (f" - Details: {details}" if details else "")
        )


# ════════════════════════════════════════════════════════════════════════
# INSTANCIA GLOBAL
# ════════════════════════════════════════════════════════════════════════

audit_logger = AuditLogger()
