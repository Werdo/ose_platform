"""
OSE Platform - Routes
API endpoints routers
"""

from .health import router as health_router
from .auth import router as auth_router
from .employees import router as employees_router
from .devices import router as devices_router
from .settings import router as settings_router
from .series_notifications import router as series_notifications_router

# Lista de todos los routers para registrar en main.py
routers = [
    health_router,
    auth_router,
    employees_router,
    devices_router,
    settings_router,
    series_notifications_router,
]

__all__ = [
    "health_router",
    "auth_router",
    "employees_router",
    "devices_router",
    "settings_router",
    "series_notifications_router",
    "routers",
]
