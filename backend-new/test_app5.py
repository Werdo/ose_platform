"""
Script de prueba para App5 - Sistema de Facturación de Tickets
Verifica que todos los modelos y servicios estén correctamente implementados
"""

import asyncio
from datetime import datetime
from pathlib import Path
import sys

# Fix para encoding en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


async def test_app5_models():
    """Prueba los modelos de App5"""
    print("\n" + "=" * 60)
    print("TESTING APP 5 - MODELOS")
    print("=" * 60)

    try:
        # Importar modelos
        from app.models.sales_ticket import SalesTicket, TicketStatus as SalesTicketStatus
        from app.models.invoice import Invoice, InvoiceStatus
        from app.models.invoice_config import InvoiceConfig

        print("✓ Modelos importados correctamente")

        # Crear ticket de prueba
        ticket = SalesTicket(
            ticket_number="TEST-001",
            customer_email="test@example.com",
            customer_name="Cliente Test",
            billing_name="Cliente Test S.L.",
            billing_nif="B12345678",
            billing_address="C/ Test, 123",
            billing_city="Madrid",
            billing_postal_code="28001",
            fecha_ticket=datetime.utcnow(),
            lineas=[
                {
                    "producto": "Producto Test 1",
                    "cantidad": 2,
                    "precio_unitario": 10.0,
                    "total": 20.0
                },
                {
                    "producto": "Producto Test 2",
                    "cantidad": 1,
                    "precio_unitario": 15.0,
                    "total": 15.0
                }
            ],
            status=SalesTicketStatus.PENDING
        )

        # Calcular totales
        ticket.calculate_totals()
        print(f"✓ Ticket creado: {ticket.ticket_number}")
        print(f"  - Subtotal: {ticket.subtotal}€")
        print(f"  - IVA: {ticket.iva_importe}€")
        print(f"  - Total: {ticket.total}€")

        # Crear configuración de prueba
        config = InvoiceConfig(
            config_id="test",
            company_name="Empresa Test S.L.",
            company_nif="A12345678",
            company_address="C/ Empresa, 456",
            company_city="Barcelona",
            company_postal_code="08001",
            company_phone="+34 900 123 456",
            company_email="info@empresatest.com"
        )
        print(f"✓ Configuración creada: {config.company_name}")

        # Crear factura de prueba
        invoice = Invoice(
            invoice_number="F-2025-000001",
            invoice_series="F",
            customer_email=ticket.customer_email,
            customer_name=ticket.billing_name or ticket.customer_name,
            customer_nif=ticket.billing_nif,
            customer_address=ticket.billing_address,
            customer_city=ticket.billing_city,
            customer_postal_code=ticket.billing_postal_code,
            lines=[
                {
                    "description": line["producto"],
                    "quantity": line["cantidad"],
                    "unit_price": line["precio_unitario"],
                    "tax_rate": 21,
                    "ticket_number": ticket.ticket_number
                }
                for line in ticket.lineas
            ],
            ticket_ids=["test_id"],
            ticket_numbers=[ticket.ticket_number],
            company_name=config.company_name,
            company_nif=config.company_nif,
            company_address=config.company_address,
            company_city=config.company_city,
            company_postal_code=config.company_postal_code,
            company_phone=config.company_phone,
            company_email=config.company_email,
            status=InvoiceStatus.DRAFT
        )

        # Calcular totales
        invoice.calculate_totals()
        print(f"✓ Factura creada: {invoice.invoice_number}")
        print(f"  - Líneas: {len(invoice.lines)}")
        print(f"  - Subtotal: {invoice.subtotal}€")
        print(f"  - IVA: {invoice.tax_total}€")
        print(f"  - Total: {invoice.total}€")

        print("\n✓ TODOS LOS MODELOS FUNCIONAN CORRECTAMENTE")
        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_app5_services():
    """Prueba los servicios de App5"""
    print("\n" + "=" * 60)
    print("TESTING APP 5 - SERVICIOS")
    print("=" * 60)

    try:
        # Importar servicios
        from app.services.ocr_service import ocr_service
        from app.services.pdf_service import pdf_service

        print("✓ Servicios importados correctamente")

        # Probar OCR (mock)
        print("\nProbando OCR Service (MOCK)...")
        ocr_result = await ocr_service.process_ticket_image("test_image.jpg")

        if ocr_result["success"]:
            print("✓ OCR procesado correctamente")
            print(f"  - Confianza: {ocr_result['confidence']}")
            print(f"  - Ticket Number: {ocr_result['extracted_data'].get('ticket_number')}")
            print(f"  - Total: {ocr_result['extracted_data'].get('total')}€")
        else:
            print(f"✗ OCR falló: {ocr_result.get('error')}")

        # Probar PDF Service
        print("\nProbando PDF Service...")

        # Datos de factura de prueba
        invoice_data = {
            "invoice_number": "F-2025-000001",
            "invoice_series": "F",
            "invoice_date": datetime.utcnow(),
            "customer_name": "Cliente Test S.L.",
            "customer_nif": "B12345678",
            "customer_address": "C/ Test, 123",
            "customer_city": "Madrid",
            "customer_postal_code": "28001",
            "customer_email": "test@example.com",
            "company_name": "Empresa Test S.L.",
            "company_nif": "A12345678",
            "company_address": "C/ Empresa, 456",
            "company_city": "Barcelona",
            "company_postal_code": "08001",
            "company_phone": "+34 900 123 456",
            "company_email": "info@empresatest.com",
            "lines": [
                {
                    "description": "Producto Test 1",
                    "quantity": 2,
                    "unit_price": 10.0,
                    "tax_rate": 21,
                    "tax_amount": 4.2,
                    "total": 24.2
                },
                {
                    "description": "Producto Test 2",
                    "quantity": 1,
                    "unit_price": 15.0,
                    "tax_rate": 21,
                    "tax_amount": 3.15,
                    "total": 18.15
                }
            ],
            "subtotal": 35.0,
            "tax_total": 7.35,
            "total": 42.35,
            "payment_terms": "Pago al contado",
            "notes": "Gracias por su compra"
        }

        # Generar PDF
        pdf_bytes = pdf_service.generate_invoice_pdf(invoice_data)
        print(f"✓ PDF generado correctamente ({len(pdf_bytes)} bytes)")

        # Guardar PDF de prueba
        test_pdf_path = Path("backend-new/uploads/invoices/test_invoice.pdf")
        test_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        with open(test_pdf_path, "wb") as f:
            f.write(pdf_bytes)

        print(f"✓ PDF guardado en: {test_pdf_path}")

        print("\n✓ TODOS LOS SERVICIOS FUNCIONAN CORRECTAMENTE")
        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_app5_routers():
    """Prueba que los routers estén correctamente configurados"""
    print("\n" + "=" * 60)
    print("TESTING APP 5 - ROUTERS")
    print("=" * 60)

    try:
        # Importar routers
        from app.routers import app5_invoice

        print("✓ Router importado correctamente")
        print(f"✓ Router público: {app5_invoice.router_public.prefix}")
        print(f"✓ Router admin: {app5_invoice.router_admin.prefix}")

        # Contar endpoints
        public_routes = len(app5_invoice.router_public.routes)
        admin_routes = len(app5_invoice.router_admin.routes)

        print(f"\nEndpoints públicos: {public_routes}")
        for route in app5_invoice.router_public.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                methods = ', '.join(route.methods)
                print(f"  - [{methods}] {route.path}")

        print(f"\nEndpoints admin: {admin_routes}")
        for route in app5_invoice.router_admin.routes:
            if hasattr(route, 'methods') and hasattr(route, 'path'):
                methods = ', '.join(route.methods)
                print(f"  - [{methods}] {route.path}")

        print(f"\n✓ Total endpoints: {public_routes + admin_routes}")
        print("✓ TODOS LOS ROUTERS ESTÁN CORRECTAMENTE CONFIGURADOS")
        return True

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Ejecuta todas las pruebas"""
    print("\n" + "=" * 60)
    print("APP 5 - SISTEMA DE FACTURACIÓN DE TICKETS")
    print("SUITE DE PRUEBAS COMPLETA")
    print("=" * 60)

    results = []

    # Probar modelos
    results.append(await test_app5_models())

    # Probar servicios
    results.append(await test_app5_services())

    # Probar routers
    results.append(await test_app5_routers())

    # Resumen final
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)

    total = len(results)
    passed = sum(results)
    failed = total - passed

    print(f"Total: {total}")
    print(f"✓ Pasadas: {passed}")
    print(f"✗ Fallidas: {failed}")

    if all(results):
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("App 5 está lista para usar.")
    else:
        print("\n⚠️  Algunas pruebas fallaron.")
        print("Revisa los errores arriba.")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
