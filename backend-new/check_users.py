"""
Script para verificar y crear usuario de prueba
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def check_and_create_user():
    # Conectar a MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27018")
    db = client["ose_platform"]

    # Verificar si hay usuarios
    count = await db.employees.count_documents({})
    print(f"Total de empleados en BD: {count}")

    # Listar usuarios existentes
    async for emp in db.employees.find({}, {"employee_id": 1, "email": 1, "name": 1, "surname": 1}):
        print(f"  - {emp.get('employee_id')} | {emp.get('email')} | {emp.get('name')} {emp.get('surname')}")

    # Verificar si existe el usuario de prueba ppelaez
    test_user_exists = await db.employees.find_one({"email": "ppelaez@oversunenergy.com"})

    if not test_user_exists:
        print("\nCreando usuario de prueba (ppelaez@oversunenergy.com)...")

        test_user = {
            "employee_id": "EMP001",
            "email": "ppelaez@oversunenergy.com",
            "name": "Pedro",
            "surname": "Peláez",
            "password_hash": pwd_context.hash("bb474edf"),
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
                "manage_inventory": True
            }
        }

        result = await db.employees.insert_one(test_user)
        print(f"[OK] Usuario creado con ID: {result.inserted_id}")
        print(f"[OK] Credenciales: {test_user['email']} / bb474edf")
    else:
        print(f"\n[OK] Usuario de prueba ya existe: {test_user_exists.get('email')}")

    client.close()

if __name__ == "__main__":
    asyncio.run(check_and_create_user())
