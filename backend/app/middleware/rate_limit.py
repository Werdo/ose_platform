"""
OSE Platform - Rate Limiting Middleware
Middleware para limitar requests por IP y usuario
"""

import time
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.config import settings

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════
# RATE LIMITER
# ════════════════════════════════════════════════════════════════════════

class RateLimiter:
    """
    Token Bucket Rate Limiter

    Permite un número de requests por segundo con burst capacity
    """

    def __init__(self, requests_per_second: int = 10, burst_size: int = 20):
        """
        Args:
            requests_per_second: Requests permitidos por segundo
            burst_size: Máximo de requests acumulados (burst capacity)
        """
        self.rate = requests_per_second
        self.burst_size = burst_size
        self.buckets: Dict[str, Tuple[float, int]] = {}  # {key: (last_update, tokens)}

    def is_allowed(self, key: str) -> bool:
        """
        Verifica si una request está permitida

        Args:
            key: Identificador único (IP, user_id, etc.)

        Returns:
            True si la request está permitida, False si excede el rate limit
        """
        now = time.time()

        if key not in self.buckets:
            # Primera request de esta key
            self.buckets[key] = (now, self.burst_size - 1)
            return True

        last_update, tokens = self.buckets[key]

        # Calcular tokens acumulados desde última request
        time_passed = now - last_update
        new_tokens = time_passed * self.rate
        tokens = min(self.burst_size, tokens + new_tokens)

        if tokens < 1:
            # No hay tokens disponibles - rate limit exceeded
            return False

        # Consumir un token
        self.buckets[key] = (now, tokens - 1)
        return True

    def get_retry_after(self, key: str) -> int:
        """
        Obtiene el tiempo en segundos hasta que la key pueda hacer otra request

        Args:
            key: Identificador único

        Returns:
            Segundos hasta próxima request permitida
        """
        if key not in self.buckets:
            return 0

        now = time.time()
        last_update, tokens = self.buckets[key]

        if tokens >= 1:
            return 0

        # Calcular cuánto tiempo hasta tener 1 token
        tokens_needed = 1 - tokens
        seconds_needed = tokens_needed / self.rate

        return int(seconds_needed) + 1

    def cleanup_old_entries(self, max_age: int = 3600):
        """
        Limpia entradas antiguas para evitar memory leak

        Args:
            max_age: Edad máxima en segundos para mantener entradas
        """
        now = time.time()
        keys_to_delete = [
            key for key, (last_update, _) in self.buckets.items()
            if now - last_update > max_age
        ]
        for key in keys_to_delete:
            del self.buckets[key]


# ════════════════════════════════════════════════════════════════════════
# MIDDLEWARE
# ════════════════════════════════════════════════════════════════════════

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware de rate limiting basado en IP

    Configurable desde settings:
    - RATE_LIMIT_ENABLED
    - RATE_LIMIT_REQUESTS_PER_SECOND
    - RATE_LIMIT_BURST_SIZE
    """

    def __init__(self, app, limiter: RateLimiter = None):
        super().__init__(app)
        self.limiter = limiter or RateLimiter(
            requests_per_second=settings.RATE_LIMIT_REQUESTS_PER_SECOND,
            burst_size=settings.RATE_LIMIT_BURST_SIZE
        )
        self.enabled = settings.RATE_LIMIT_ENABLED
        self.last_cleanup = time.time()

    async def dispatch(self, request: Request, call_next):
        """
        Procesa la request y aplica rate limiting
        """
        # Si está deshabilitado, pasar directo
        if not self.enabled:
            return await call_next(request)

        # Paths excluidos (health checks, docs)
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)

        # Obtener identificador (IP)
        client_ip = self._get_client_ip(request)

        # Cleanup periódico (cada 5 minutos)
        now = time.time()
        if now - self.last_cleanup > 300:
            self.limiter.cleanup_old_entries()
            self.last_cleanup = now

        # Verificar rate limit
        if not self.limiter.is_allowed(client_ip):
            retry_after = self.limiter.get_retry_after(client_ip)
            logger.warning(f"Rate limit exceeded for IP {client_ip}")

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": str(retry_after)}
            )

        # Procesar request
        response = await call_next(request)
        return response

    def _get_client_ip(self, request: Request) -> str:
        """
        Obtiene la IP del cliente considerando proxies

        Busca en orden:
        1. X-Forwarded-For (si hay proxy/load balancer)
        2. X-Real-IP
        3. request.client.host (directo)
        """
        # Check X-Forwarded-For (puede tener múltiples IPs)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Tomar la primera IP (cliente real)
            return forwarded_for.split(",")[0].strip()

        # Check X-Real-IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback a IP directa
        return request.client.host if request.client else "unknown"


# ════════════════════════════════════════════════════════════════════════
# RATE LIMITER POR ENDPOINT
# ════════════════════════════════════════════════════════════════════════

class EndpointRateLimiter:
    """
    Rate limiter específico para endpoints críticos

    Usage:
        endpoint_limiter = EndpointRateLimiter(requests_per_minute=5)

        @router.post("/sensitive-endpoint")
        async def sensitive(request: Request):
            endpoint_limiter.check(request)
            ...
    """

    def __init__(self, requests_per_minute: int = 60):
        self.limiter = RateLimiter(
            requests_per_second=requests_per_minute / 60,
            burst_size=requests_per_minute
        )

    def check(self, request: Request):
        """
        Verifica el rate limit para una request

        Raises:
            HTTPException 429: Si excede el rate limit
        """
        client_ip = self._get_client_ip(request)

        if not self.limiter.is_allowed(client_ip):
            retry_after = self.limiter.get_retry_after(client_ip)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests to this endpoint",
                headers={"Retry-After": str(retry_after)}
            )

    def _get_client_ip(self, request: Request) -> str:
        """Obtiene IP del cliente"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"


# ════════════════════════════════════════════════════════════════════════
# INSTANCIAS GLOBALES PARA ENDPOINTS CRÍTICOS
# ════════════════════════════════════════════════════════════════════════

# Rate limiter para login (60 intentos por minuto en desarrollo, 5 en producción)
from app.config import settings
login_rate_limiter = EndpointRateLimiter(
    requests_per_minute=60 if settings.ENVIRONMENT == "development" else 5
)

# Rate limiter para registro (30 por minuto en desarrollo, 3 en producción)
register_rate_limiter = EndpointRateLimiter(
    requests_per_minute=30 if settings.ENVIRONMENT == "development" else 3
)

# Rate limiter para password reset (30 por minuto en desarrollo, 3 en producción)
password_reset_limiter = EndpointRateLimiter(
    requests_per_minute=30 if settings.ENVIRONMENT == "development" else 3
)
