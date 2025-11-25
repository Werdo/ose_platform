"""
Script para verificar campos de operador actualizados
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.device import Device
from app.database import Database
import json


async def verify():
    """Verifica los campos de operador"""

    await Database.connect()

    # Obtener un dispositivo con ICCID
    device = await Device.find_one(Device.ccid != None)

    if device:
        print("\n" + "="*70)
        print("EJEMPLO DE DISPOSITIVO CON OPERADOR ACTUALIZADO")
        print("="*70)
        print(f"\nIMEI: {device.imei}")
        print(f"CCID: {device.ccid}")
        print(f"\n--- INFORMACIÓN DEL OPERADOR ---")
        print(f"Operador: {device.operador}")
        print(f"Marca: {device.operador_marca}")
        print(f"País: {device.operador_pais}")
        print(f"Región: {device.operador_region}")
        print(f"IIN Prefix: {device.iin_prefix}")
        print(f"Uso: {device.operador_uso}")
        print(f"Red: {device.operador_red}")
        print(f"Actualizado: {device.operador_actualizado}")
        print("="*70)

    # Contar por operador
    print("\n--- ESTADÍSTICAS DE OPERADORES ---")
    devices = await Device.find(Device.operador != None).to_list()

    operadores = {}
    for dev in devices:
        op = dev.operador or "Desconocido"
        operadores[op] = operadores.get(op, 0) + 1

    for operador, count in operadores.items():
        print(f"  {operador}: {count} dispositivos")

    print(f"\nTotal dispositivos con operador: {len(devices)}")
    print("="*70 + "\n")

    await Database.close()


if __name__ == "__main__":
    asyncio.run(verify())
