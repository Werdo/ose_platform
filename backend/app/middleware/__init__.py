"""
OSE Platform - Middleware
Middleware y manejadores de errores para FastAPI
"""

from .rate_limit import (
    RateLimiter,
    RateLimitMiddleware,
    EndpointRateLimiter,
    login_rate_limiter,
    register_rate_limiter,
    password_reset_limiter,
)

from .logging import (
    RequestLoggingMiddleware,
    AuditLogger,
    audit_logger,
)

from .error_handlers import (
    register_exception_handlers,
    BusinessLogicError,
    ResourceNotFoundError,
    PermissionDeniedError,
    http_exception_handler,
    validation_exception_handler,
    duplicate_key_exception_handler,
    general_exception_handler,
)

__all__ = [
    # Rate Limiting
    "RateLimiter",
    "RateLimitMiddleware",
    "EndpointRateLimiter",
    "login_rate_limiter",
    "register_rate_limiter",
    "password_reset_limiter",

    # Logging
    "RequestLoggingMiddleware",
    "AuditLogger",
    "audit_logger",

    # Error Handlers
    "register_exception_handlers",
    "BusinessLogicError",
    "ResourceNotFoundError",
    "PermissionDeniedError",
    "http_exception_handler",
    "validation_exception_handler",
    "duplicate_key_exception_handler",
    "general_exception_handler",
]
