"""
OSE Platform - Services
Servicios de negocio y utilidades
"""

from .email_service import (
    EmailService,
    send_email,
    send_template_email,
    test_smtp_connection
)

__all__ = [
    "EmailService",
    "send_email",
    "send_template_email",
    "test_smtp_connection",
]
