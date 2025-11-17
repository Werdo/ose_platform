"""
Script para poblar la base de datos con datos de prueba para App 1
Crea clientes y dispositivos de prueba
"""

import asyncio
from datetime import datetime
import sys
import os

# Añadir el directorio padre al path para poder importar app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.mongodb import Database
from app.models import Customer, CustomerType, CustomerStatus, Device, DeviceStatus


async def create_test_customers():
    """Crea clientes de prueba"""
    print("📦 Creando clientes de prueba...")

    customers_data = [
        {
            "customer_code": "ACME",
            "company_name": "ACME Corporation",
            "email": "contact@acme.com",
            "phone": "+34 91 123 4567",
            "customer_type": CustomerType.DISTRIBUTOR,
            "status": CustomerStatus.ACTIVE,
            "address": {
                "street": "Calle Principal 123",
                "city": "Madrid",
                "state": "Madrid",
                "postal_code": "28001",
                "country": "España"
            }
        },
        {
            "customer_code": "TECH",
            "company_name": "TechCorp Solutions",
            "email": "info@techcorp.com",
            "phone": "+34 93 456 7890",
            "customer_type": CustomerType.ENTERPRISE,
            "status": CustomerStatus.ACTIVE,
            "address": {
                "street": "Avenida Tecnológica 456",
                "city": "Barcelona",
                "state": "Cataluña",
                "postal_code": "08001",
                "country": "España"
            }
        },
        {
            "customer_code": "GLOB",
            "company_name": "Global Logistics SA",
            "email": "global@logistics.com",
            "phone": "+34 96 789 0123",
            "customer_type": CustomerType.DISTRIBUTOR,
            "status": CustomerStatus.ACTIVE,
            "address": {
                "street": "Puerto Industrial 789",
                "city": "Valencia",
                "state": "Valencia",
                "postal_code": "46001",
                "country": "España"
            }
        },
        {
            "customer_code": "COES",
            "company_name": "Correos España",
            "email": "operaciones@correos.es",
            "phone": "+34 91 987 6543",
            "customer_type": CustomerType.GOVERNMENT,
            "status": CustomerStatus.ACTIVE,
            "address": {
                "street": "Plaza de Cibeles 1",
                "city": "Madrid",
                "state": "Madrid",
                "postal_code": "28014",
                "country": "España"
            }
        }
    ]

    created_customers = []
    for customer_data in customers_data:
        # Verificar si ya existe
        existing = await Customer.find_by_code(customer_data["customer_code"])
        if existing:
            print(f"  ⏭ Cliente {customer_data['customer_code']} ya existe")
            created_customers.append(existing)
            continue

        customer = Customer(**customer_data)
        await customer.insert()
        created_customers.append(customer)
        print(f"  ✓ Cliente creado: {customer.customer_code} - {customer.full_name}")

    return created_customers


async def create_test_devices():
    """Crea dispositivos de prueba"""
    print("\n📱 Creando dispositivos de prueba...")

    # Dispositivos sin notificar (para probar App 1)
    devices_data = [
        # Lote 1 - ACME Corporation
        {"imei": "861888082667623", "ccid": "89882390001210884632", "package_no": "9912182508200007739500205"},
        {"imei": "861888082667624", "ccid": "89882390001210884633", "package_no": "9912182508200007739500205"},
        {"imei": "861888082667625", "ccid": "89882390001210884634", "package_no": "9912182508200007739500205"},
        {"imei": "861888082667626", "ccid": "89882390001210884635", "package_no": "9912182508200007739500205"},
        {"imei": "861888082667627", "ccid": "89882390001210884636", "package_no": "9912182508200007739500205"},

        # Lote 2 - TechCorp
        {"imei": "861888082667628", "ccid": "89882390001210884637", "package_no": "9912182508200007739500206"},
        {"imei": "861888082667629", "ccid": "89882390001210884638", "package_no": "9912182508200007739500206"},
        {"imei": "861888082667630", "ccid": "89882390001210884639", "package_no": "9912182508200007739500206"},

        # Lote 3 - Global Logistics
        {"imei": "861888082667631", "ccid": "89882390001210884640", "package_no": "9912182508200007739500207"},
        {"imei": "861888082667632", "ccid": "89882390001210884641", "package_no": "9912182508200007739500207"},
        {"imei": "861888082667633", "ccid": "89882390001210884642", "package_no": "9912182508200007739500207"},
        {"imei": "861888082667634", "ccid": "89882390001210884643", "package_no": "9912182508200007739500207"},

        # Dispositivos individuales sin paquete
        {"imei": "861888082667635", "ccid": "89882390001210884644"},
        {"imei": "861888082667636", "ccid": "89882390001210884645"},
        {"imei": "861888082667637", "ccid": "89882390001210884646"},
    ]

    created_count = 0
    for device_data in devices_data:
        # Verificar si ya existe
        existing = await Device.find_by_imei(device_data["imei"])
        if existing:
            print(f"  ⏭ Dispositivo {device_data['imei']} ya existe")
            continue

        device = Device(
            imei=device_data["imei"],
            ccid=device_data.get("ccid"),
            package_no=device_data.get("package_no"),
            status=DeviceStatus.APPROVED,
            current_location="ALMACEN-PRINCIPAL",
            brand="OversunTrack",
            model="GT06N",
            notificado=False,
            valid=True,
            created_by="system_seed"
        )
        await device.insert()
        created_count += 1
        print(f"  ✓ Dispositivo creado: {device.imei}")

    print(f"\n✓ Total dispositivos creados: {created_count}")


async def create_already_notified_devices():
    """Crea algunos dispositivos ya notificados para probar validaciones"""
    print("\n📱 Creando dispositivos ya notificados (para pruebas)...")

    notified_devices = [
        {"imei": "861888082667700", "ccid": "89882390001210884700", "customer": "ACME Corporation"},
        {"imei": "861888082667701", "ccid": "89882390001210884701", "customer": "TechCorp Solutions"},
    ]

    for device_data in notified_devices:
        existing = await Device.find_by_imei(device_data["imei"])
        if existing:
            print(f"  ⏭ Dispositivo {device_data['imei']} ya existe")
            continue

        device = Device(
            imei=device_data["imei"],
            ccid=device_data["ccid"],
            status=DeviceStatus.IN_SERVICE,
            current_location="CLIENTE",
            brand="OversunTrack",
            model="GT06N",
            notificado=True,
            cliente_notificado=device_data["customer"],
            fecha_notificacion=datetime.utcnow(),
            valid=True,
            created_by="system_seed"
        )
        await device.insert()
        print(f"  ✓ Dispositivo notificado creado: {device.imei} -> {device_data['customer']}")


async def main():
    """Función principal"""
    print("🚀 Iniciando seed de datos para App 1...\n")

    try:
        # Conectar a MongoDB
        await Database.connect()
        print("✓ Conectado a MongoDB\n")

        # Crear datos de prueba
        await create_test_customers()
        await create_test_devices()
        await create_already_notified_devices()

        print("\n✅ Seed completado exitosamente!")
        print("\n📊 Resumen:")
        customers_count = await Customer.find().count()
        devices_count = await Device.find().count()
        notified_count = await Device.find(Device.notificado == True).count()
        print(f"  • Clientes: {customers_count}")
        print(f"  • Dispositivos: {devices_count}")
        print(f"  • Dispositivos notificados: {notified_count}")
        print(f"  • Dispositivos sin notificar: {devices_count - notified_count}")

    except Exception as e:
        print(f"\n❌ Error durante el seed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await Database.close()
        print("\n✓ Conexión cerrada")


if __name__ == "__main__":
    asyncio.run(main())
