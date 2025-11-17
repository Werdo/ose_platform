"""
OSE Platform - MongoDB Connection
Gestión de conexión a MongoDB usando Motor (async) y Beanie (ODM)
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional
import logging

from app.config import settings, dynamic_config

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════
# CLIENTE MONGODB GLOBAL
# ════════════════════════════════════════════════════════════════════════

class Database:
    """Singleton para gestionar la conexión a MongoDB"""

    client: Optional[AsyncIOMotorClient] = None
    database = None

    @classmethod
    async def connect(cls):
        """Establece la conexión a MongoDB"""
        try:
            logger.info(f"Connecting to MongoDB: {settings.MONGODB_DB_NAME}")

            # Crear cliente MongoDB
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT
            )

            # Obtener base de datos
            cls.database = cls.client[settings.MONGODB_DB_NAME]

            # Inicializar Beanie con los modelos
            await init_beanie(
                database=cls.database,
                document_models=cls._get_document_models()
            )

            # Configurar dynamic_config con la BD
            dynamic_config.set_database(cls.database)

            # Verificar conexión
            await cls.client.admin.command('ping')

            logger.info("✓ MongoDB connected successfully")

        except Exception as e:
            logger.error(f"✗ Error connecting to MongoDB: {e}")
            raise

    @classmethod
    async def close(cls):
        """Cierra la conexión a MongoDB"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    def _get_document_models(cls):
        """
        Retorna lista de todos los modelos Beanie
        IMPORTANTE: Importar aquí para evitar importaciones circulares
        """
        from app.models.device import Device
        from app.models.production_order import ProductionOrder
        from app.models.device_event import DeviceEvent
        from app.models.service_ticket import ServiceTicket
        from app.models.rma_case import RMACase
        from app.models.customer import Customer
        from app.models.employee import Employee
        from app.models.quality_control import QualityControl
        from app.models.inventory import InventoryItem
        from app.models.metric import Metric
        from app.models.setting import SystemSetting
        from app.models.series_notification import SeriesNotification

        return [
            Device,
            ProductionOrder,
            DeviceEvent,
            ServiceTicket,
            RMACase,
            Customer,
            Employee,
            QualityControl,
            InventoryItem,
            Metric,
            SystemSetting,  # Nueva colección para configuración dinámica
            SeriesNotification  # App 1: Notificación de series
        ]

    @classmethod
    def get_database(cls):
        """Retorna la instancia de la base de datos"""
        if not cls.database:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return cls.database


# ════════════════════════════════════════════════════════════════════════
# FUNCIONES DE CONVENIENCIA
# ════════════════════════════════════════════════════════════════════════

async def init_db():
    """Inicializa la conexión a la base de datos"""
    await Database.connect()


async def close_db():
    """Cierra la conexión a la base de datos"""
    await Database.close()


def get_db():
    """
    Dependency para FastAPI
    Retorna la instancia de la base de datos
    """
    return Database.get_database()


# Alias para importación más sencilla
db = Database


# ════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ════════════════════════════════════════════════════════════════════════

async def check_database_health() -> dict:
    """
    Verifica el estado de la conexión a MongoDB
    Retorna información sobre la salud de la BD
    """
    try:
        if not Database.client:
            return {
                "status": "disconnected",
                "message": "No database connection"
            }

        # Ping a la base de datos
        await Database.client.admin.command('ping')

        # Obtener stats de la BD
        stats = await Database.database.command("dbStats")

        return {
            "status": "healthy",
            "database": settings.MONGODB_DB_NAME,
            "collections": stats.get("collections", 0),
            "dataSize": f"{stats.get('dataSize', 0) / 1024 / 1024:.2f} MB",
            "indexSize": f"{stats.get('indexSize', 0) / 1024 / 1024:.2f} MB"
        }

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
