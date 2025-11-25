"""
OSE Platform - Migration Script
Actualiza todos los dispositivos existentes con información de operador desde ICCID

Uso:
    python scripts/migrate_add_operator_fields.py
"""

import asyncio
import sys
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
from app.models.device import Device
from app.database import Database
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def migrate_devices():
    """Migra todos los dispositivos agregando información de operador"""

    logger.info("=" * 70)
    logger.info("MIGRACIÓN: Agregar información de operador a dispositivos")
    logger.info("=" * 70)

    try:
        # Conectar a la base de datos
        logger.info("Conectando a MongoDB...")
        await Database.connect()
        logger.info("✓ Conectado a MongoDB")

        # Obtener todos los dispositivos con ICCID
        logger.info("Buscando dispositivos con ICCID...")
        devices_with_iccid = await Device.find(
            Device.ccid != None
        ).to_list()

        total = len(devices_with_iccid)
        logger.info(f"✓ Encontrados {total} dispositivos con ICCID")

        if total == 0:
            logger.warning("No hay dispositivos con ICCID para migrar")
            return

        # Procesar cada dispositivo
        actualizados = 0
        errores = 0
        sin_operador = 0

        logger.info("\nIniciando actualización...")
        logger.info("-" * 70)

        for idx, device in enumerate(devices_with_iccid, 1):
            try:
                # Actualizar información del operador
                result = await device.actualizar_operador_desde_iccid()

                if result:
                    actualizados += 1
                    logger.info(
                        f"[{idx}/{total}] ✓ {device.imei[:8]}... - "
                        f"ICCID: {device.ccid[:10]}... - "
                        f"Operador: {device.operador or 'N/A'}"
                    )
                else:
                    sin_operador += 1
                    logger.warning(
                        f"[{idx}/{total}] ⚠ {device.imei[:8]}... - "
                        f"ICCID: {device.ccid[:10]}... - "
                        f"IIN no encontrado en tabla"
                    )

            except Exception as e:
                errores += 1
                logger.error(
                    f"[{idx}/{total}] ✗ Error en {device.imei}: {e}"
                )

        # Resumen
        logger.info("-" * 70)
        logger.info("\n" + "=" * 70)
        logger.info("RESUMEN DE MIGRACIÓN")
        logger.info("=" * 70)
        logger.info(f"Total procesados:        {total}")
        logger.info(f"✓ Actualizados:          {actualizados}")
        logger.info(f"⚠ Sin IIN encontrado:    {sin_operador}")
        logger.info(f"✗ Errores:               {errores}")
        logger.info("=" * 70)

        # Estadísticas de operadores
        if actualizados > 0:
            logger.info("\nEstadísticas de operadores:")
            logger.info("-" * 70)

            # Contar por operador
            devices_updated = await Device.find(
                Device.operador != None
            ).to_list()

            operador_counts = {}
            for dev in devices_updated:
                op = dev.operador or "Desconocido"
                operador_counts[op] = operador_counts.get(op, 0) + 1

            for operador, count in sorted(
                operador_counts.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                logger.info(f"  {operador}: {count} dispositivos")

        logger.info("\n✓ Migración completada exitosamente")

    except Exception as e:
        logger.error(f"✗ Error durante la migración: {e}")
        raise

    finally:
        # Cerrar conexión
        await Database.close()
        logger.info("Conexión cerrada")


async def main():
    """Función principal"""
    await migrate_devices()


if __name__ == "__main__":
    asyncio.run(main())
