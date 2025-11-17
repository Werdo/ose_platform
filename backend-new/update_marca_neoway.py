"""
Script para actualizar todos los dispositivos sin marca a Neoway
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime


async def update_marca_neoway():
    # Conectar a MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27018")
    db = client["ose_platform"]

    print("[*] Iniciando actualizacion de marca a Neoway...")
    print("=" * 60)

    # Contar dispositivos sin marca
    count_without_marca = await db.devices.count_documents({
        "$or": [
            {"marca": None},
            {"marca": {"$exists": False}}
        ]
    })

    print(f"[+] Dispositivos sin marca: {count_without_marca:,}")

    if count_without_marca == 0:
        print("[!] No hay dispositivos sin marca para actualizar")
        client.close()
        return

    # Confirmar actualización
    print(f"\n[!] Se van a actualizar {count_without_marca:,} dispositivos a marca 'Neoway'")
    print("[*] Procesando actualizacion...")

    # Actualizar todos los dispositivos sin marca
    result = await db.devices.update_many(
        {
            "$or": [
                {"marca": None},
                {"marca": {"$exists": False}}
            ]
        },
        {
            "$set": {
                "marca": "Neoway",
                "fecha_actualizacion": datetime.utcnow()
            }
        }
    )

    print(f"\n[+] Actualizacion completada!")
    print(f"    - Documentos encontrados: {result.matched_count:,}")
    print(f"    - Documentos actualizados: {result.modified_count:,}")

    # Verificar resultado
    print(f"\n[*] Verificando resultado...")

    total_devices = await db.devices.count_documents({})
    neoway_devices = await db.devices.count_documents({"marca": "Neoway"})
    carlite_devices = await db.devices.count_documents({"marca": "CARLITE"})
    still_without = await db.devices.count_documents({
        "$or": [
            {"marca": None},
            {"marca": {"$exists": False}}
        ]
    })

    print(f"\n[+] Resultado final:")
    print(f"    - Total dispositivos: {total_devices:,}")
    print(f"    - Marca Neoway: {neoway_devices:,}")
    print(f"    - Marca CARLITE: {carlite_devices:,}")
    print(f"    - Sin marca: {still_without:,}")

    print("\n" + "=" * 60)
    print("[+] Actualizacion completada exitosamente!")

    client.close()


if __name__ == "__main__":
    asyncio.run(update_marca_neoway())
