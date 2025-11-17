"""
Script para actualizar permisos del usuario ADMIN
Otorga acceso a todas las aplicaciones
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Configuración de MongoDB
MONGODB_URI = "mongodb://localhost:27018"
MONGODB_DB_NAME = "ose_platform"


async def update_admin_permissions():
    """Actualiza los permisos del usuario ADMIN para que tenga acceso a todas las apps"""

    print("Conectando a MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DB_NAME]

    try:
        # Buscar al usuario ADMIN
        admin_user = await db.employees.find_one({"employee_id": "ADMIN"})

        if not admin_user:
            print("ERROR: Usuario ADMIN no encontrado")
            return

        print(f"Usuario encontrado: {admin_user.get('name')} {admin_user.get('surname')}")
        print(f"  Role: {admin_user.get('role')}")

        # Permisos completos para todas las apps
        all_permissions = {
            # Aplicaciones
            "app1_access": True,  # Notificación de Series
            "app2_access": True,  # Importación de Datos
            "app3_access": True,  # RMA & Tickets
            "app4_access": True,  # Transform Data
            "app5_access": True,  # Facturas
            "app6_access": True,  # Picking & Etiquetado
            # Estaciones de producción
            "production_line1_station1": True,
            "production_line1_station2": True,
            "production_line2_station1": True,
            "production_line2_station2": True,
            "production_line3_station1": True,
            "production_line3_station2": True,
            # Permisos generales
            "quality_control": True,
            "admin_access": True,
            "manage_users": True,
            "manage_settings": True,
            "view_reports": True,
            "manage_tickets": True,
            "manage_rma": True,
            "manage_customers": True,
            "manage_inventory": True,
        }

        # Actualizar permisos
        result = await db.employees.update_one(
            {"employee_id": "ADMIN"},
            {
                "$set": {
                    "permissions": all_permissions,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        if result.modified_count > 0:
            print("OK - Permisos actualizados correctamente")
            print("\nPermisos habilitados:")
            print("  [OK] App 1: Notificacion de Series")
            print("  [OK] App 2: Importacion de Datos")
            print("  [OK] App 3: RMA & Tickets")
            print("  [OK] App 4: Transform Data")
            print("  [OK] App 5: Facturas")
            print("  [OK] App 6: Picking & Etiquetado")
            print("  [OK] Todos los permisos administrativos")
        else:
            print("INFO: No se modifico ningun registro (puede que ya tuviera los permisos)")

    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        client.close()
        print("\nConexion cerrada")


if __name__ == "__main__":
    print("=" * 60)
    print("ACTUALIZACIÓN DE PERMISOS - USUARIO ADMIN")
    print("=" * 60)
    asyncio.run(update_admin_permissions())
    print("=" * 60)
