"""
OSE Platform - App 5: Sistema de Facturación de Tickets
Router para gestión de tickets de venta y generación de facturas
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Body
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import logging
import os
import shutil
import base64

from app.models.sales_ticket import SalesTicket, TicketStatus as SalesTicketStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.invoice_config import InvoiceConfig
from app.models.employee import Employee
from app.dependencies.auth import get_current_active_user
from app.services.ocr_service import ocr_service
from app.services.pdf_service import pdf_service
from app.config import settings
from app.schemas.app5 import TicketCreate, TicketResponse

logger = logging.getLogger(__name__)

# Crear dos routers: uno público y uno admin
router_public = APIRouter(prefix="/public", tags=["App 5: Facturación (Público)"])
router_admin = APIRouter(prefix="/app5", tags=["App 5: Facturación (Admin)"])


# ════════════════════════════════════════════════════════════════════════
# ENDPOINTS PÚBLICOS (Sin autenticación)
# ════════════════════════════════════════════════════════════════════════

@router_public.post("/tickets/scan")
async def scan_ticket_image(
    file: UploadFile = File(...),
    email: str = Query(..., description="Email del cliente")
):
    """
    **[PÚBLICO] Escanear imagen de ticket con OCR**

    Sube una imagen de ticket de venta para su procesamiento OCR.
    No requiere autenticación.

    - **file**: Imagen del ticket (JPG, PNG)
    - **email**: Email del cliente

    Retorna:
    - ticket_id: ID del ticket creado
    - image_url: URL de la imagen subida
    - ocr_result: Resultado del procesamiento OCR (si está habilitado)
    """
    try:
        # Validar tipo de archivo
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser una imagen (JPG, PNG)"
            )

        # Crear directorio de uploads si no existe
        upload_dir = Path("uploads/tickets")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generar nombre único para el archivo
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix if file.filename else ".jpg"
        filename = f"ticket_{email}_{timestamp}{file_extension}"
        file_path = upload_dir / filename

        # Guardar archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Ticket image uploaded: {file_path}")

        # Obtener configuración
        config = await InvoiceConfig.get_config()

        # Procesar OCR si está habilitado
        ocr_result = None
        extracted_data = {}

        if config.ocr_enabled:
            ocr_result = await ocr_service.process_ticket_image(str(file_path))
            extracted_data = ocr_result.get("extracted_data", {})

        # Crear ticket con estado PROCESSING
        ticket = SalesTicket(
            ticket_number=extracted_data.get("ticket_number", f"TEMP-{timestamp}"),
            image_url=f"/uploads/tickets/{filename}",
            image_filename=filename,
            customer_email=email,
            status=SalesTicketStatus.PROCESSING if config.ocr_enabled else SalesTicketStatus.PENDING,
            ocr_confidence=ocr_result.get("confidence", 0.0) if ocr_result else None,
            ocr_raw_text=ocr_result.get("raw_text", "") if ocr_result else None,
            manual_entry=not config.ocr_enabled
        )

        # Si hay datos extraídos, añadirlos
        if extracted_data:
            ticket.fecha_ticket = extracted_data.get("fecha_ticket")
            ticket.establecimiento = extracted_data.get("establecimiento")
            ticket.lineas = extracted_data.get("lineas", [])
            ticket.subtotal = extracted_data.get("subtotal", 0.0)
            ticket.iva_porcentaje = extracted_data.get("iva_porcentaje", 21.0)
            ticket.iva_importe = extracted_data.get("iva_importe", 0.0)
            ticket.total = extracted_data.get("total", 0.0)
            ticket.forma_pago = extracted_data.get("forma_pago")

        # Verificar duplicados si está habilitado
        if config.auto_reject_duplicates and not config.allow_duplicate_tickets:
            existing = await SalesTicket.check_duplicate(ticket.ticket_number)
            if existing:
                ticket.mark_as_duplicate(str(existing.id))

        await ticket.save()

        return {
            "success": True,
            "ticket_id": str(ticket.id),
            "ticket_number": ticket.ticket_number,
            "image_url": ticket.image_url,
            "status": ticket.status,
            "ocr_processed": config.ocr_enabled,
            "ocr_confidence": ticket.ocr_confidence,
            "extracted_data": extracted_data if config.ocr_enabled else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir el ticket: {str(e)}"
        )


@router_public.post("/tickets")
async def submit_ticket_data(ticket_data: TicketCreate = Body(...)):
    """
    **[PÚBLICO] Crear ticket con datos manuales**

    Crea un ticket proporcionando los datos manualmente (sin imagen).
    No requiere autenticación.

    - **email**: Email del cliente
    - **ticket_number**: Número del ticket
    - **date**: Fecha del ticket
    - **items**: Array de líneas de productos
    - **total**: Total del ticket
    - **billing_***: Datos de facturación opcionales
    """
    try:
        # Verificar duplicados
        config = await InvoiceConfig.get_config()

        if config.auto_reject_duplicates and not config.allow_duplicate_tickets:
            existing = await SalesTicket.check_duplicate(ticket_data.ticket_number)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un ticket con el número {ticket_data.ticket_number}"
                )

        # Convertir items a formato del modelo
        lineas = [
            {
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "total": item.total
            }
            for item in ticket_data.items
        ]

        # Parsear fecha
        try:
            fecha_ticket = datetime.fromisoformat(ticket_data.date.replace('Z', '+00:00'))
        except:
            fecha_ticket = datetime.utcnow()

        # Crear ticket
        ticket = SalesTicket(
            ticket_number=ticket_data.ticket_number,
            customer_email=ticket_data.email,
            billing_name=ticket_data.billing_name,
            billing_nif=ticket_data.billing_nif,
            billing_address=ticket_data.billing_address,
            fecha_ticket=fecha_ticket,
            lineas=lineas,
            total=ticket_data.total,
            manual_entry=True,
            status=SalesTicketStatus.PENDING
        )

        # Calcular totales
        ticket.calculate_totals()

        await ticket.save()

        return {
            "id": str(ticket.id),
            "email": ticket.customer_email,
            "ticket_number": ticket.ticket_number,
            "date": ticket.fecha_ticket.isoformat() if ticket.fecha_ticket else None,
            "total": ticket.total,
            "status": ticket.status,
            "items": ticket.lineas,
            "billing_name": ticket.billing_name,
            "billing_nif": ticket.billing_nif,
            "billing_address": ticket.billing_address,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el ticket: {str(e)}"
        )


@router_public.get("/tickets")
async def get_tickets(
    email: str = Query(..., description="Email del cliente")
):
    """
    **[PÚBLICO] Obtener tickets por email**

    Obtiene todos los tickets de un cliente por email.
    No requiere autenticación.
    """
    try:
        tickets = await SalesTicket.get_by_customer_email(email)

        return {
            "success": True,
            "count": len(tickets),
            "tickets": [
                {
                    "id": str(t.id),
                    "ticket_number": t.ticket_number,
                    "fecha_ticket": t.fecha_ticket,
                    "total": t.total,
                    "status": t.status,
                    "invoice_number": t.invoice_number,
                    "created_at": t.created_at
                }
                for t in tickets
            ]
        }

    except Exception as e:
        logger.error(f"Error getting tickets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tickets: {str(e)}"
        )


@router_public.post("/tickets/generate")
async def generate_invoice_from_tickets(
    email: str = Query(..., description="Email del cliente"),
    ticket_ids: Optional[List[str]] = None
):
    """
    **[PÚBLICO] Generar factura de tickets pendientes**

    Genera una factura consolidando todos los tickets pendientes de un cliente.
    Si se proporcionan ticket_ids, solo se facturan esos tickets.

    - **email**: Email del cliente
    - **ticket_ids**: IDs de tickets específicos (opcional)
    """
    try:
        # Obtener configuración
        config = await InvoiceConfig.get_config()

        # Obtener tickets pendientes
        if ticket_ids:
            tickets = await SalesTicket.find(
                SalesTicket.id.in_([t for t in ticket_ids]),  # type: ignore
                SalesTicket.customer_email == email,
                SalesTicket.status == SalesTicketStatus.PENDING
            ).to_list()
        else:
            tickets = await SalesTicket.get_pending_for_invoice(email)

        if not tickets:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No hay tickets pendientes para facturar"
            )

        # Validar que todos los tickets tengan datos de facturación
        first_ticket = tickets[0]
        if not first_ticket.billing_name or not first_ticket.billing_nif:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los tickets deben tener datos de facturación completos"
            )

        # Generar número de factura
        invoice_number = await Invoice.generate_next_invoice_number(
            series=config.invoice_series
        )

        # Consolidar líneas de todos los tickets
        all_lines = []
        total_subtotal = 0.0
        total_tax = 0.0
        ticket_ids_list = []
        ticket_numbers_list = []

        for ticket in tickets:
            ticket_ids_list.append(str(ticket.id))
            ticket_numbers_list.append(ticket.ticket_number)

            # Convertir líneas del ticket a líneas de factura
            for line in ticket.lineas:
                invoice_line = {
                    "description": line.get("producto", "Producto"),
                    "quantity": line.get("cantidad", 1),
                    "unit_price": line.get("precio_unitario", 0.0),
                    "tax_rate": ticket.iva_porcentaje,
                    "ticket_number": ticket.ticket_number
                }
                all_lines.append(invoice_line)

            total_subtotal += ticket.subtotal
            total_tax += ticket.iva_importe

        # Crear factura
        invoice = Invoice(
            invoice_number=invoice_number,
            invoice_series=config.invoice_series,
            invoice_date=datetime.utcnow(),
            customer_email=email,
            customer_name=first_ticket.billing_name or first_ticket.customer_name or email,
            customer_nif=first_ticket.billing_nif,
            customer_address=first_ticket.billing_address,
            customer_city=first_ticket.billing_city,
            customer_postal_code=first_ticket.billing_postal_code,
            lines=all_lines,
            ticket_ids=ticket_ids_list,
            ticket_numbers=ticket_numbers_list,
            company_name=config.company_name,
            company_nif=config.company_nif,
            company_address=config.company_address,
            company_city=config.company_city,
            company_postal_code=config.company_postal_code,
            company_phone=config.company_phone,
            company_email=config.company_email,
            company_logo_url=config.company_logo_url,
            payment_terms=config.payment_terms,
            footer_text=config.invoice_footer_text,
            status=InvoiceStatus.DRAFT
        )

        # Calcular totales
        invoice.calculate_totals()

        await invoice.save()

        # Generar PDF
        invoice_data = invoice.dict()
        pdf_bytes = pdf_service.generate_invoice_pdf(invoice_data)

        # Guardar PDF
        pdf_dir = Path("uploads/invoices")
        pdf_dir.mkdir(parents=True, exist_ok=True)
        pdf_filename = f"invoice_{invoice_number}.pdf"
        pdf_path = pdf_dir / pdf_filename

        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        # Actualizar factura con PDF
        invoice.mark_as_generated(
            pdf_url=f"/uploads/invoices/{pdf_filename}",
            pdf_filename=pdf_filename
        )
        await invoice.save()

        # Marcar tickets como facturados
        for ticket in tickets:
            ticket.mark_as_invoiced(str(invoice.id), invoice_number)
            await ticket.save()

        return {
            "success": True,
            "invoice_id": str(invoice.id),
            "invoice_number": invoice.invoice_number,
            "pdf_url": invoice.pdf_url,
            "total": invoice.total,
            "tickets_count": len(tickets)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar la factura: {str(e)}"
        )


@router_public.get("/tickets/{ticket_id}")
async def get_ticket_by_id(ticket_id: str):
    """
    **[PÚBLICO] Obtener ticket por ID**

    Obtiene un ticket específico por su ID.
    No requiere autenticación.
    """
    try:
        ticket = await SalesTicket.get(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )

        return {
            "success": True,
            "ticket": {
                "id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "fecha_ticket": ticket.fecha_ticket,
                "establecimiento": ticket.establecimiento,
                "lineas": ticket.lineas,
                "subtotal": ticket.subtotal,
                "iva_porcentaje": ticket.iva_porcentaje,
                "iva_importe": ticket.iva_importe,
                "total": ticket.total,
                "forma_pago": ticket.forma_pago,
                "customer_email": ticket.customer_email,
                "status": ticket.status,
                "image_url": ticket.image_url,
                "invoice_number": ticket.invoice_number,
                "created_at": ticket.created_at
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener ticket: {str(e)}"
        )


@router_public.post("/tickets/{ticket_id}/upload")
async def upload_image_to_ticket(
    ticket_id: str,
    file: UploadFile = File(...)
):
    """
    **[PÚBLICO] Subir imagen a un ticket existente**

    Sube una imagen a un ticket que ya fue creado.
    No requiere autenticación.
    """
    try:
        # Buscar ticket
        ticket = await SalesTicket.get(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )

        # Validar tipo de archivo
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser una imagen (JPG, PNG)"
            )

        # Crear directorio de uploads si no existe
        upload_dir = Path("uploads/tickets")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Generar nombre único para el archivo
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix if file.filename else ".jpg"
        filename = f"ticket_{ticket.customer_email}_{timestamp}{file_extension}"
        file_path = upload_dir / filename

        # Guardar archivo
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Actualizar ticket con la imagen
        ticket.image_url = f"/uploads/tickets/{filename}"
        ticket.image_filename = filename
        await ticket.save()

        logger.info(f"Image uploaded to ticket {ticket_id}: {file_path}")

        return {
            "success": True,
            "image_url": ticket.image_url
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image to ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir la imagen: {str(e)}"
        )


@router_public.get("/tickets/download/{invoice_id}")
async def download_invoice_pdf(invoice_id: str):
    """
    **[PÚBLICO] Descargar PDF de factura**

    Descarga el PDF de una factura.
    No requiere autenticación (la seguridad es por oscuridad del ID).
    """
    try:
        # Buscar factura
        invoice = await Invoice.get(invoice_id)

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Factura no encontrada"
            )

        if not invoice.pdf_filename:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="PDF no disponible"
            )

        # Ruta del PDF
        pdf_path = Path("uploads/invoices") / invoice.pdf_filename

        if not pdf_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Archivo PDF no encontrado"
            )

        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename=invoice.pdf_filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al descargar la factura: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# ENDPOINTS ADMIN (Con autenticación)
# ════════════════════════════════════════════════════════════════════════

@router_admin.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {"test": "working"}

@router_admin.get("/stats", response_model=dict)
async def get_dashboard_stats(current_user: Employee = Depends(get_current_active_user)):
    """[ADMIN] Obtener estadísticas del dashboard de App5"""
    try:
        from datetime import datetime

        # Ticket stats
        total_tickets = await SalesTicket.count()
        pending_tickets = await SalesTicket.find({"status": SalesTicketStatus.PENDING}).count()
        processing_tickets = await SalesTicket.find({"status": SalesTicketStatus.PROCESSING}).count()
        invoiced_tickets = await SalesTicket.find({"status": SalesTicketStatus.INVOICED}).count()
        processed_tickets = processing_tickets + invoiced_tickets  # Tickets procesados = en proceso + facturados

        # Invoice counts
        total_invoices = await Invoice.count()
        draft_invoices = await Invoice.find({"status": InvoiceStatus.DRAFT}).count()
        sent_invoices = await Invoice.find({"status": InvoiceStatus.SENT}).count()
        paid_invoices = await Invoice.find({"status": InvoiceStatus.PAID}).count()
        issued_invoices = sent_invoices + paid_invoices  # Facturas emitidas = enviadas + pagadas

        # Calculate total amount from all invoices
        all_invoices = await Invoice.find_all().to_list()
        total_amount = sum(inv.total_amount for inv in all_invoices) if all_invoices else 0.0

        # Calculate month amount (current month)
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)
        month_invoices = await Invoice.find({"invoice_date": {"$gte": start_of_month}}).to_list()
        month_amount = sum(inv.total_amount for inv in month_invoices) if month_invoices else 0.0

        return {
            "success": True,
            "stats": {
                "total_tickets": total_tickets,
                "pending_tickets": pending_tickets,
                "processed_tickets": processed_tickets,
                "total_invoices": total_invoices,
                "draft_invoices": draft_invoices,
                "issued_invoices": issued_invoices,
                "sent_invoices": sent_invoices,
                "paid_invoices": paid_invoices,
                "total_amount": total_amount,
                "month_amount": month_amount
            }
        }
    except Exception as e:
        logger.error(f"Error in stats endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router_admin.get("/tickets")
async def list_all_tickets(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[SalesTicketStatus] = None,
    email: Optional[str] = None,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **[ADMIN] Listar todos los tickets**

    Requiere autenticación.
    """
    try:
        # Construir query
        query = {}
        if status:
            query["status"] = status
        if email:
            query["customer_email"] = email

        # Paginación
        skip = (page - 1) * limit

        # Buscar tickets
        tickets_query = SalesTicket.find(query)
        total = await tickets_query.count()
        tickets = await tickets_query.skip(skip).limit(limit).sort("-created_at").to_list()

        return {
            "success": True,
            "total": total,
            "page": page,
            "limit": limit,
            "tickets": [
                {
                    "id": str(t.id),
                    "ticket_number": t.ticket_number,
                    "customer_email": t.customer_email,
                    "fecha_ticket": t.fecha_ticket,
                    "total": t.total,
                    "status": t.status,
                    "invoice_number": t.invoice_number,
                    "is_duplicate": t.is_duplicate,
                    "manual_entry": t.manual_entry,
                    "created_at": t.created_at
                }
                for t in tickets
            ]
        }

    except Exception as e:
        logger.error(f"Error listing tickets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar tickets: {str(e)}"
        )


@router_admin.get("/tickets/{ticket_id}")
async def get_ticket_detail(
    ticket_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **[ADMIN] Ver detalle de ticket**

    Requiere autenticación.
    """
    try:
        ticket = await SalesTicket.get(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )

        return {
            "success": True,
            "ticket": ticket.dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el ticket: {str(e)}"
        )


@router_admin.put("/tickets/{ticket_id}")
async def update_ticket(
    ticket_id: str,
    ticket_data: dict,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **[ADMIN] Editar ticket**

    Permite editar manualmente los datos de un ticket.
    Requiere autenticación.
    """
    try:
        ticket = await SalesTicket.get(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )

        # Actualizar campos permitidos
        allowed_fields = [
            "ticket_number", "fecha_ticket", "establecimiento",
            "lineas", "subtotal", "iva_porcentaje", "iva_importe", "total",
            "forma_pago", "billing_name", "billing_nif", "billing_address",
            "billing_city", "billing_postal_code", "notes"
        ]

        for field in allowed_fields:
            if field in ticket_data:
                setattr(ticket, field, ticket_data[field])

        ticket.manual_entry = True
        ticket.updated_at = datetime.utcnow()

        await ticket.save()

        return {
            "success": True,
            "ticket": ticket.dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el ticket: {str(e)}"
        )


@router_admin.delete("/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **[ADMIN] Eliminar ticket**

    Requiere autenticación.
    """
    try:
        ticket = await SalesTicket.get(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )

        if ticket.status == SalesTicketStatus.INVOICED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar un ticket ya facturado"
            )

        await ticket.delete()

        return {
            "success": True,
            "message": "Ticket eliminado correctamente"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting ticket: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el ticket: {str(e)}"
        )


@router_admin.post("/tickets/{ticket_id}/process-ocr")
async def process_ticket_ocr(
    ticket_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **[ADMIN] Procesar OCR manualmente**

    Procesa o reprocesa el OCR de un ticket.
    Requiere autenticación.
    """
    try:
        ticket = await SalesTicket.get(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )

        if not ticket.image_filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El ticket no tiene imagen asociada"
            )

        # Procesar OCR
        image_path = Path("uploads/tickets") / ticket.image_filename

        if not image_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Imagen no encontrada"
            )

        ocr_result = await ocr_service.process_ticket_image(str(image_path))
        extracted_data = ocr_result.get("extracted_data", {})

        # Actualizar ticket
        ticket.ocr_confidence = ocr_result.get("confidence", 0.0)
        ticket.ocr_raw_text = ocr_result.get("raw_text", "")

        if extracted_data:
            ticket.ticket_number = extracted_data.get("ticket_number", ticket.ticket_number)
            ticket.fecha_ticket = extracted_data.get("fecha_ticket")
            ticket.establecimiento = extracted_data.get("establecimiento")
            ticket.lineas = extracted_data.get("lineas", [])
            ticket.subtotal = extracted_data.get("subtotal", 0.0)
            ticket.iva_porcentaje = extracted_data.get("iva_porcentaje", 21.0)
            ticket.iva_importe = extracted_data.get("iva_importe", 0.0)
            ticket.total = extracted_data.get("total", 0.0)
            ticket.forma_pago = extracted_data.get("forma_pago")

        ticket.status = SalesTicketStatus.PENDING
        ticket.updated_at = datetime.utcnow()

        await ticket.save()

        return {
            "success": True,
            "ticket": ticket.dict(),
            "ocr_result": ocr_result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing OCR: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar OCR: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# ENDPOINTS ADMIN - FACTURAS
# ════════════════════════════════════════════════════════════════════════

@router_admin.get("/invoices")
async def list_invoices(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[InvoiceStatus] = None,
    email: Optional[str] = None,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **[ADMIN] Listar facturas**

    Requiere autenticación.
    """
    try:
        query = {}
        if status:
            query["status"] = status
        if email:
            query["customer_email"] = email

        skip = (page - 1) * limit

        invoices_query = Invoice.find(query)
        total = await invoices_query.count()
        invoices = await invoices_query.skip(skip).limit(limit).sort("-invoice_date").to_list()

        return {
            "success": True,
            "total": total,
            "page": page,
            "limit": limit,
            "invoices": [
                {
                    "id": str(inv.id),
                    "invoice_number": inv.invoice_number,
                    "customer_email": inv.customer_email,
                    "customer_name": inv.customer_name,
                    "invoice_date": inv.invoice_date,
                    "total": inv.total,
                    "status": inv.status,
                    "tickets_count": len(inv.ticket_ids),
                    "created_at": inv.created_at
                }
                for inv in invoices
            ]
        }

    except Exception as e:
        logger.error(f"Error listing invoices: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar facturas: {str(e)}"
        )


@router_admin.get("/invoices/{invoice_id}")
async def get_invoice_detail(
    invoice_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **[ADMIN] Ver detalle de factura**

    Requiere autenticación.
    """
    try:
        invoice = await Invoice.get(invoice_id)

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Factura no encontrada"
            )

        return {
            "success": True,
            "invoice": invoice.dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la factura: {str(e)}"
        )


@router_admin.post("/invoices/{invoice_id}/regenerate")
async def regenerate_invoice_pdf(
    invoice_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **[ADMIN] Regenerar PDF de factura**

    Requiere autenticación.
    """
    try:
        invoice = await Invoice.get(invoice_id)

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Factura no encontrada"
            )

        # Generar nuevo PDF
        invoice_data = invoice.dict()
        pdf_bytes = pdf_service.generate_invoice_pdf(invoice_data)

        # Guardar PDF
        pdf_dir = Path("uploads/invoices")
        pdf_dir.mkdir(parents=True, exist_ok=True)
        pdf_filename = f"invoice_{invoice.invoice_number}.pdf"
        pdf_path = pdf_dir / pdf_filename

        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)

        # Actualizar factura
        invoice.pdf_url = f"/uploads/invoices/{pdf_filename}"
        invoice.pdf_filename = pdf_filename
        invoice.updated_at = datetime.utcnow()

        await invoice.save()

        return {
            "success": True,
            "pdf_url": invoice.pdf_url
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al regenerar la factura: {str(e)}"
        )


@router_admin.post("/invoices/{invoice_id}/send-email")
async def send_invoice_email(
    invoice_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **[ADMIN] Enviar factura por email**

    Requiere autenticación.
    """
    try:
        invoice = await Invoice.get(invoice_id)

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Factura no encontrada"
            )

        # TODO: Implementar envío de email usando mail_service
        # from app.services.mail_service import mail_service
        # await mail_service.send_invoice_email(invoice)

        invoice.mark_as_sent()
        await invoice.save()

        return {
            "success": True,
            "message": "Email enviado correctamente (MOCK)"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending invoice email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar el email: {str(e)}"
        )


@router_admin.delete("/invoices/{invoice_id}")
async def cancel_invoice(
    invoice_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **[ADMIN] Cancelar factura**

    Cancela una factura y libera los tickets asociados.
    Requiere autenticación.
    """
    try:
        invoice = await Invoice.get(invoice_id)

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Factura no encontrada"
            )

        # Cancelar factura
        invoice.cancel()
        await invoice.save()

        # Liberar tickets
        for ticket_id in invoice.ticket_ids:
            ticket = await SalesTicket.get(ticket_id)
            if ticket:
                ticket.status = SalesTicketStatus.PENDING
                ticket.invoice_id = None
                ticket.invoice_number = None
                ticket.processed_at = None
                await ticket.save()

        return {
            "success": True,
            "message": "Factura cancelada correctamente"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cancelar la factura: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# ENDPOINTS ADMIN - CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════════════

@router_admin.get("/config")
async def get_invoice_config(
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **[ADMIN] Obtener configuración de facturación**

    Requiere autenticación.
    """
    try:
        config = await InvoiceConfig.get_config()

        return {
            "success": True,
            "config": config.dict()
        }

    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener la configuración: {str(e)}"
        )


@router_admin.put("/config")
async def update_invoice_config(
    config_data: dict,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **[ADMIN] Actualizar configuración de facturación**

    Requiere autenticación.
    """
    try:
        config = await InvoiceConfig.get_config()

        await config.update_company_info(config_data)

        return {
            "success": True,
            "config": config.dict()
        }

    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar la configuración: {str(e)}"
        )


@router_admin.post("/config/upload-logo")
async def upload_company_logo(
    file: UploadFile = File(...),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **[ADMIN] Subir logo de la empresa**

    Requiere autenticación.
    """
    try:
        # Validar tipo de archivo
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser una imagen"
            )

        # Crear directorio
        upload_dir = Path("uploads/logos")
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Guardar archivo
        filename = f"company_logo{Path(file.filename).suffix if file.filename else '.png'}"
        file_path = upload_dir / filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Actualizar configuración
        config = await InvoiceConfig.get_config()
        config.company_logo_url = f"/uploads/logos/{filename}"
        config.company_logo_filename = filename
        await config.save()

        return {
            "success": True,
            "logo_url": config.company_logo_url
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading logo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir el logo: {str(e)}"
        )
