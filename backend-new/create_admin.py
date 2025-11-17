"""
OSE Platform - Create Admin User
Script para crear el primer usuario administrador
"""

import asyncio
from app.models.employee import Employee, EmployeeRole, EmployeeStatus
from app.utils.security import hash_password
from app.database import init_db, close_db


async def create_admin_user():
    """
    Crea el usuario administrador inicial
    """
    print("=" * 60)
    print("OSE Platform - Crear Usuario Administrador")
    print("=" * 60)
    print()

    # Conectar a la base de datos
    print("Conectando a MongoDB...")
    await init_db()
    print("[OK] Conectado\n")

    # Verificar si ya existe un admin
    existing_admin = await Employee.find_by_employee_id("ADMIN")

    if existing_admin:
        print("[AVISO] Ya existe un usuario ADMIN")
        print(f"   Email: {existing_admin.email}")
        print(f"   Nombre: {existing_admin.full_name}")
        print()

        overwrite = input("¿Deseas sobrescribir? (s/N): ").lower()

        if overwrite != 's':
            print("\nOperación cancelada")
            await close_db()
            return

        # Eliminar admin existente
        await existing_admin.delete()
        print("[OK] Usuario anterior eliminado\n")

    # Crear nuevo admin
    print("Creando usuario administrador...")
    print()

    # Solicitar datos
    employee_id = input("Employee ID [ADMIN]: ").strip() or "ADMIN"
    name = input("Nombre [Admin]: ").strip() or "Admin"
    surname = input("Apellidos [System]: ").strip() or "System"
    email = input("Email [admin@oversunenergy.com]: ").strip() or "admin@oversunenergy.com"
    password = input("Contraseña [admin123]: ").strip() or "admin123"

    print()
    print(f"Creando usuario:")
    print(f"  Employee ID: {employee_id}")
    print(f"  Nombre: {name} {surname}")
    print(f"  Email: {email}")
    print(f"  Rol: SUPER_ADMIN")
    print()

    # Crear usuario
    admin = Employee(
        employee_id=employee_id,
        name=name,
        surname=surname,
        email=email,
        password_hash=hash_password(password),
        role=EmployeeRole.SUPER_ADMIN,
        status=EmployeeStatus.ACTIVE,
        permissions={
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
        }
    )

    await admin.insert()

    print("=" * 60)
    print("[OK] Usuario administrador creado exitosamente!")
    print("=" * 60)
    print()
    print("Credenciales:")
    print(f"  Employee ID / Email: {employee_id} / {email}")
    print(f"  Contrasena: {password}")
    print()
    print("[IMPORTANTE] Cambia la contrasena despues del primer login")
    print("=" * 60)

    # Cerrar conexión
    await close_db()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
