"""
Script para verificar si los dispositivos tienen marca asociada
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient


async def check_devices():
    # Conectar a MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27018")
    db = client["ose_platform"]

    # Contar total de dispositivos
    total = await db.devices.count_documents({})
    print(f"[+] Total de dispositivos: {total:,}")

    # Contar dispositivos CON marca
    with_marca = await db.devices.count_documents({"marca": {"$ne": None, "$exists": True}})
    print(f"[+] Dispositivos CON marca: {with_marca:,}")

    # Contar dispositivos SIN marca
    without_marca = await db.devices.count_documents({
        "$or": [
            {"marca": None},
            {"marca": {"$exists": False}}
        ]
    })
    print(f"[-] Dispositivos SIN marca: {without_marca:,}")

    # Obtener marcas únicas
    marcas = await db.devices.distinct("marca", {"marca": {"$ne": None}})
    print(f"\n[*] Marcas encontradas: {marcas}")

    # Contar dispositivos por marca
    print(f"\n[*] Dispositivos por marca:")
    pipeline = [
        {"$match": {"marca": {"$ne": None}}},
        {"$group": {"_id": "$marca", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]

    async for doc in db.devices.aggregate(pipeline):
        print(f"   {doc['_id']}: {doc['count']:,} dispositivos")

    # Verificar algunos ejemplos específicos
    print(f"\n[*] Ejemplos de dispositivos:")
    cursor = db.devices.find(
        {"imei": {"$in": ["861888086768500", "867572080141013", "867572080439417"]}},
        {"imei": 1, "ccid": 1, "marca": 1, "nro_referencia": 1, "sku": 1, "_id": 0}
    ).limit(5)

    async for device in cursor:
        print(f"   IMEI: {device.get('imei')}")
        print(f"   ICCID: {device.get('ccid', 'N/A')}")
        print(f"   Marca: {device.get('marca', 'SIN MARCA')}")
        print(f"   Ref: {device.get('nro_referencia', 'N/A')}")
        print(f"   SKU: {device.get('sku', 'N/A')}")
        print()

    # Verificar índices
    print(f"\n[*] Indices en coleccion devices:")
    indexes = await db.devices.list_indexes().to_list(None)
    for idx in indexes:
        print(f"   - {idx['name']}: {idx.get('key', {})}")

    client.close()


if __name__ == "__main__":
    asyncio.run(check_devices())
