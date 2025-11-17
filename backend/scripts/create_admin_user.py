"""
Script para crear usuario administrador
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_admin_user():
    """Crea un usuario administrador en MongoDB"""

    # Conectar a MongoDB
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://ose_user:ose_password_2024@localhost:27018/ose_platform?authSource=ose_platform")

    print(f"🔌 Conectando a MongoDB...")
    client = AsyncIOMotorClient(mongodb_uri)
    db = client.ose_platform

    try:
        # Verificar conexión
        await db.command('ping')
        print("✅ Conectado a MongoDB")

        # Datos del usuario
        email = "ppelaez@oversunenergy.com"
        password = "bb474edf"

        # Verificar si el usuario ya existe
        existing_user = await db.employees.find_one({"email": email})
        if existing_user:
            print(f"⚠️  Usuario {email} ya existe")

            # Actualizar contraseña
            password_hash = pwd_context.hash(password)
            await db.employees.update_one(
                {"email": email},
                {"$set": {
                    "password_hash": password_hash,
                    "updated_at": datetime.utcnow()
                }}
            )
            print(f"✅ Contraseña actualizada para {email}")
            return

        # Hashear contraseña
        password_hash = pwd_context.hash(password)
        print(f"🔐 Contraseña hasheada correctamente")

        # Crear documento del empleado
        employee_doc = {
            "employee_id": "PPELAEZ",
            "name": "Pedro",
            "surname": "Peláez",
            "email": email,
            "phone": None,
            "password_hash": password_hash,
            "role": "admin",
            "status": "active",
            "permissions": {
                "production_line1_station1": True,
                "production_line1_station2": True,
                "production_line2_station1": True,
                "production_line2_station2": True,
                "production_line3_station1": True,
                "production_line3_station2": True,
                "quality_control": True,
                "admin_access": True,
                "manage_users": True,
                "manage_settings": True,
                "view_reports": True,
                "manage_tickets": True,
                "manage_rma": True,
                "manage_customers": True,
                "manage_inventory": True,
            },
            "last_login": None,
            "last_login_ip": None,
            "failed_login_attempts": 0,
            "locked_until": None,
            "refresh_token": None,
            "refresh_token_expires": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "created_by": None,
            "notes": "Usuario administrador creado por script"
        }

        # Insertar en MongoDB
        result = await db.employees.insert_one(employee_doc)

        print(f"✅ Usuario creado exitosamente")
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print(f"👤 Employee ID: PPELAEZ")
        print(f"🎭 Role: admin")
        print(f"🆔 MongoDB ID: {result.inserted_id}")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        client.close()
        print("🔌 Conexión cerrada")


if __name__ == "__main__":
    asyncio.run(create_admin_user())
