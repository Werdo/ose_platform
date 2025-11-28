"""
OSE Platform - Database Connection
Gestión de conexión a MongoDB usando Motor (async) y Beanie (ODM)
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional, List
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """Singleton para gestionar la conexión a MongoDB"""

    client: Optional[AsyncIOMotorClient] = None
    database = None

    @classmethod
    async def connect(cls):
        """Establece la conexión a MongoDB e inicializa Beanie"""
        try:
            logger.info(f"Conectando a MongoDB: {settings.MONGODB_DB_NAME}")

            # Crear cliente MongoDB
            cls.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
                serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT
            )

            # Obtener base de datos
            cls.database = cls.client[settings.MONGODB_DB_NAME]

            # Inicializar Beanie con todos los modelos
            await init_beanie(
                database=cls.database,
                document_models=cls._get_document_models()
            )

            # Verificar conexión
            await cls.client.admin.command('ping')

            logger.info("✓ MongoDB conectado exitosamente")

        except Exception as e:
            logger.error(f"✗ Error conectando a MongoDB: {e}")
            raise

    @classmethod
    async def close(cls):
        """Cierra la conexión a MongoDB"""
        if cls.client:
            cls.client.close()
            logger.info("MongoDB connection closed")

    @classmethod
    def _get_document_models(cls) -> List:
        """
        Retorna lista de todos los modelos Beanie
        IMPORTANTE: Importar aquí para evitar importaciones circulares
        """
        from app.models.device import Device
        from app.models.device_event import DeviceEvent
        from app.models.production_order import ProductionOrder
        from app.models.employee import Employee
        from app.models.customer import Customer
        from app.models.movimiento import Movimiento
        from app.models.quality_control import QualityControl
        from app.models.service_ticket import ServiceTicket
        from app.models.rma_case import RMACase
        from app.models.inventory import InventoryItem
        from app.models.metric import Metric
        from app.models.setting import SystemSetting
        from app.models.import_record import ImportRecord
        from app.models.public_user import PublicUser
        from app.models.transform_template import TransformTemplate
        from app.models.import_job import ImportJob
        from app.models.sales_ticket import SalesTicket
        from app.models.invoice import Invoice
        from app.models.invoice_config import InvoiceConfig
        from app.models.pallet import Pallet
        from app.models.package import Package
        from app.models.system_log import SystemLog
        from app.models.iccid_generation import ICCIDGenerationBatch
        from app.models.iccid_batch import ICCIDBatch
        from app.models.client_user import ClientUser
        from app.models.series_notification import SeriesNotification
        from app.models.brand import Brand

        return [
            Device,
            DeviceEvent,
            ProductionOrder,
            Employee,
            Customer,
            Movimiento,  # Nueva colección crítica
            QualityControl,
            ServiceTicket,
            RMACase,
            InventoryItem,
            Metric,
            SystemSetting,
            ImportRecord,  # App 2: Registro de importaciones
            ICCIDGenerationBatch,  # App 2: Historial de generación de ICCID
            PublicUser,  # App 3: Usuarios del portal público
            TransformTemplate,  # App 4: Plantillas de transformación
            ImportJob,  # App 4: Jobs de importación
            SalesTicket,  # App 5: Tickets de venta
            Invoice,  # App 5: Facturas
            InvoiceConfig,  # App 5: Configuración de facturación
            Pallet,  # App 6: Palets de picking
            Package,  # App 6: Paquetería y tracking
            ICCIDBatch,  # App 8: Lotes de ICCID con análisis
            SystemLog,  # System: Logs del sistema
            ClientUser,  # System: Usuarios clientes externos
            SeriesNotification,  # App 1: Historial de notificaciones de series
            Brand,  # System: Marcas de dispositivos
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
