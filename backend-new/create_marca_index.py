"""
Script para crear índice en el campo marca
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient


async def create_marca_index():
    # Conectar a MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27018")
    db = client["ose_platform"]

    print("[*] Creando indice para campo 'marca'...")

    # Crear índice
    result = await db.devices.create_index("marca")
    print(f"[+] Indice creado: {result}")

    # Verificar índices
    print(f"\n[*] Indices en coleccion devices:")
    indexes = await db.devices.list_indexes().to_list(None)
    for idx in indexes:
        print(f"   - {idx['name']}: {idx.get('key', {})}")

    # Estadísticas por marca
    print(f"\n[*] Estadisticas por marca:")
    pipeline = [
        {"$group": {"_id": "$marca", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]

    async for doc in db.devices.aggregate(pipeline):
        print(f"   {doc['_id']}: {doc['count']:,} dispositivos")

    print(f"\n[+] Proceso completado!")

    client.close()


if __name__ == "__main__":
    asyncio.run(create_marca_index())
