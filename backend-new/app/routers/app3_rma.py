"""
OSE Platform - App3: RMA & Tickets Router
Sistema de gestión de incidencias y RMA multiusuario
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import csv
import io

from app.models import ServiceTicket, RMACase, Device, Customer
from app.models.service_ticket import TicketStatus, TicketPriority
from app.models.rma_case import RMAStatus, RMAType, RMAReason
from app.dependencies.auth import get_current_active_user as get_current_employee
from app.models.employee import Employee

router = APIRouter(
    prefix="/app3",
    tags=["App3 - RMA & Tickets"]
)


# ════════════════════════════════════════════════════════════════════
# SCHEMAS
# ════════════════════════════════════════════════════════════════════

class TicketCreate(BaseModel):
    device_imei: str
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    issue_type: str
    description: str
    priority: str = "medium"


class TicketMessage(BaseModel):
    message: str
    attachments: Optional[List[str]] = None


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class RMACreate(BaseModel):
    ticket_id: str
    rma_type: str
    reason: str
    return_address: Optional[str] = None


# ════════════════════════════════════════════════════════════════════
# ENDPOINTS - TICKETS
# ════════════════════════════════════════════════════════════════════

@router.post("/tickets", status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Crea un nuevo ticket de soporte

    **Parámetros:**
    - device_imei: IMEI del dispositivo
    - customer_email: Email del cliente (opcional)
    - customer_name: Nombre del cliente (opcional)
    - issue_type: Tipo de problema
    - description: Descripción del problema
    - priority: Prioridad (low, medium, high, critical)
    """
    try:
        # Buscar dispositivo
        device = await Device.buscar_por_imei(ticket_data.device_imei)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dispositivo con IMEI {ticket_data.device_imei} no encontrado"
            )

        # Generar número de ticket
        ticket_count = await ServiceTicket.find_all().count()
        ticket_number = f"TKT-{datetime.now().year}-{str(ticket_count + 1).zfill(5)}"

        # Crear ticket
        ticket = ServiceTicket(
            ticket_number=ticket_number,
            device_id=str(device.id),
            device_imei=device.imei,
            customer_name=ticket_data.customer_name,
            customer_email=ticket_data.customer_email,
            issue_type=ticket_data.issue_type,
            description=ticket_data.description,
            priority=TicketPriority(ticket_data.priority),
            status=TicketStatus.OPEN,
            reported_by=f"{current_user.nombre} {current_user.apellidos}",
            created_by=str(current_user.id)
        )

        await ticket.insert()

        return {
            "success": True,
            "message": "Ticket creado exitosamente",
            "ticket": {
                "id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "priority": ticket.priority,
                "device_imei": ticket.device_imei
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando ticket: {str(e)}"
        )


@router.get("/tickets", status_code=status.HTTP_200_OK)
async def get_tickets(
    status_filter: Optional[str] = Query(None, description="Filtrar por estado"),
    priority_filter: Optional[str] = Query(None, description="Filtrar por prioridad"),
    search: Optional[str] = Query(None, description="Buscar por IMEI o número de ticket"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Employee = Depends(get_current_employee)
):
    """
    Obtiene lista de tickets con filtros opcionales
    """
    try:
        # Construir query
        query = {}

        if status_filter:
            query["status"] = status_filter

        if priority_filter:
            query["priority"] = priority_filter

        if search:
            # Buscar por IMEI o número de ticket
            query["$or"] = [
                {"device_imei": {"$regex": search, "$options": "i"}},
                {"ticket_number": {"$regex": search, "$options": "i"}}
            ]

        # Obtener tickets
        tickets = await ServiceTicket.find(query).sort("-created_at").skip(offset).limit(limit).to_list()
        total = await ServiceTicket.find(query).count()

        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "tickets": [
                {
                    "id": str(ticket.id),
                    "ticket_number": ticket.ticket_number,
                    "device_imei": ticket.device_imei,
                    "customer_name": ticket.customer_name,
                    "customer_email": ticket.customer_email,
                    "issue_type": ticket.issue_type,
                    "description": ticket.description,
                    "status": ticket.status,
                    "priority": ticket.priority,
                    "created_at": ticket.created_at.isoformat(),
                    "updated_at": ticket.updated_at.isoformat(),
                    "reported_by": ticket.reported_by,
                    "assigned_to": ticket.assigned_to,
                    "messages_count": len(ticket.messages) if ticket.messages else 0
                }
                for ticket in tickets
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo tickets: {str(e)}"
        )


@router.get("/tickets/{ticket_id}", status_code=status.HTTP_200_OK)
async def get_ticket_details(
    ticket_id: str,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Obtiene detalles completos de un ticket incluyendo mensajes
    """
    try:
        ticket = await ServiceTicket.get(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )

        # Obtener dispositivo
        device = None
        if ticket.device_id:
            device = await Device.get(ticket.device_id)

        return {
            "success": True,
            "ticket": {
                "id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "device_imei": ticket.device_imei,
                "device": {
                    "id": str(device.id) if device else None,
                    "imei": device.imei if device else None,
                    "marca": device.marca if device else None,
                    "estado": device.estado if device else None
                } if device else None,
                "customer_name": ticket.customer_name,
                "customer_email": ticket.customer_email,
                "issue_type": ticket.issue_type,
                "description": ticket.description,
                "status": ticket.status,
                "priority": ticket.priority,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat(),
                "closed_at": ticket.closed_at.isoformat() if ticket.closed_at else None,
                "reported_by": ticket.reported_by,
                "assigned_to": ticket.assigned_to,
                "resolution": ticket.resolution,
                "messages": ticket.messages or [],
                "attachments": ticket.attachments or []
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo ticket: {str(e)}"
        )


@router.post("/tickets/{ticket_id}/messages", status_code=status.HTTP_201_CREATED)
async def add_ticket_message(
    ticket_id: str,
    message_data: TicketMessage,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Añade un mensaje/respuesta a un ticket
    """
    try:
        ticket = await ServiceTicket.get(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )

        # Crear mensaje
        new_message = {
            "from_user": f"{current_user.nombre} {current_user.apellidos}",
            "from_role": current_user.rol,
            "message": message_data.message,
            "timestamp": datetime.utcnow(),
            "attachments": message_data.attachments or []
        }

        # Añadir mensaje
        if not ticket.messages:
            ticket.messages = []

        ticket.messages.append(new_message)
        ticket.updated_at = datetime.utcnow()

        # Si el ticket estaba cerrado, reabrirlo
        if ticket.status == TicketStatus.CLOSED:
            ticket.status = TicketStatus.IN_PROGRESS

        await ticket.save()

        return {
            "success": True,
            "message": "Mensaje añadido exitosamente",
            "ticket_id": str(ticket.id)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error añadiendo mensaje: {str(e)}"
        )


@router.patch("/tickets/{ticket_id}", status_code=status.HTTP_200_OK)
async def update_ticket(
    ticket_id: str,
    update_data: TicketUpdate,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Actualiza un ticket (estado, prioridad, asignado, etc.)
    """
    try:
        ticket = await ServiceTicket.get(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )

        # Actualizar campos
        if update_data.status:
            ticket.status = TicketStatus(update_data.status)
            if update_data.status == "closed":
                ticket.closed_at = datetime.utcnow()

        if update_data.priority:
            ticket.priority = TicketPriority(update_data.priority)

        if update_data.assigned_to:
            ticket.assigned_to = update_data.assigned_to

        if update_data.notes:
            ticket.resolution = update_data.notes

        ticket.updated_at = datetime.utcnow()

        await ticket.save()

        return {
            "success": True,
            "message": "Ticket actualizado exitosamente",
            "ticket": {
                "id": str(ticket.id),
                "status": ticket.status,
                "priority": ticket.priority,
                "assigned_to": ticket.assigned_to
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando ticket: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════
# ENDPOINTS - RMA
# ════════════════════════════════════════════════════════════════════

@router.post("/rma", status_code=status.HTTP_201_CREATED)
async def create_rma(
    rma_data: RMACreate,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Crea un caso RMA a partir de un ticket
    """
    try:
        # Verificar ticket
        ticket = await ServiceTicket.get(rma_data.ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )

        # Generar número RMA
        rma_count = await RMACase.find_all().count()
        rma_number = f"RMA-{datetime.now().year}-{str(rma_count + 1).zfill(5)}"

        # Crear caso RMA
        rma_case = RMACase(
            rma_number=rma_number,
            device_id=ticket.device_id,
            device_imei=ticket.device_imei,
            ticket_id=str(ticket.id),
            customer_name=ticket.customer_name,
            customer_email=ticket.customer_email,
            rma_type=RMAType(rma_data.rma_type),
            reason=rma_data.reason,
            status=RMAStatus.PENDING,
            return_address=rma_data.return_address,
            created_by=str(current_user.id)
        )

        await rma_case.insert()

        # Actualizar ticket
        ticket.status = TicketStatus.ESCALATED
        ticket.updated_at = datetime.utcnow()
        await ticket.save()

        return {
            "success": True,
            "message": "Caso RMA creado exitosamente",
            "rma": {
                "id": str(rma_case.id),
                "rma_number": rma_case.rma_number,
                "status": rma_case.status,
                "rma_type": rma_case.rma_type
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando RMA: {str(e)}"
        )


@router.get("/rma", status_code=status.HTTP_200_OK)
async def get_rma_cases(
    status_filter: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Employee = Depends(get_current_employee)
):
    """
    Obtiene lista de casos RMA
    """
    try:
        query = {}
        if status_filter:
            query["status"] = status_filter

        rma_cases = await RMACase.find(query).sort("-created_at").skip(offset).limit(limit).to_list()
        total = await RMACase.find(query).count()

        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "rma_cases": [
                {
                    "id": str(rma.id),
                    "rma_number": rma.rma_number,
                    "imei": rma.imei,
                    "customer_name": rma.customer_name,
                    "rma_type": rma.rma_type,
                    "status": rma.status,
                    "reason": rma.reason,
                    "service_ticket_id": rma.service_ticket_id,
                    "ticket_number": rma.ticket_number,
                    "created_at": rma.created_at.isoformat(),
                    "updated_at": rma.updated_at.isoformat(),
                    "processing_time_days": rma.processing_time_days
                }
                for rma in rma_cases
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo casos RMA: {str(e)}"
        )


@router.get("/rma/{rma_id}", status_code=status.HTTP_200_OK)
async def get_rma_details(
    rma_id: str,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Obtiene detalles completos de un RMA
    """
    try:
        rma = await RMACase.get(rma_id)

        if not rma:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RMA no encontrado"
            )

        return {
            "success": True,
            "rma": {
                "id": str(rma.id),
                "rma_number": rma.rma_number,
                "imei": rma.imei,
                "device_id": rma.device_id,
                "customer_id": rma.customer_id,
                "customer_name": rma.customer_name,
                "service_ticket_id": rma.service_ticket_id,
                "ticket_number": rma.ticket_number,
                "status": rma.status,
                "rma_type": rma.rma_type,
                "reason": rma.reason,
                "reason_detail": rma.reason_detail,
                "under_warranty": rma.under_warranty,
                "warranty_void": rma.warranty_void,
                "warranty_void_reason": rma.warranty_void_reason,
                "replacement_imei": rma.replacement_imei,
                "cost_estimate": rma.cost_estimate,
                "cost_actual": rma.cost_actual,
                "charged_to_customer": rma.charged_to_customer,
                "amount_charged": rma.amount_charged,
                "inspection": rma.inspection,
                "return_shipping": rma.return_shipping,
                "replacement_shipping": rma.replacement_shipping,
                "resolution": rma.resolution,
                "resolution_date": rma.resolution_date.isoformat() if rma.resolution_date else None,
                "approved_by": rma.approved_by,
                "approved_at": rma.approved_at.isoformat() if rma.approved_at else None,
                "rejection_reason": rma.rejection_reason,
                "notes": rma.notes,
                "created_at": rma.created_at.isoformat(),
                "updated_at": rma.updated_at.isoformat(),
                "completed_at": rma.completed_at.isoformat() if rma.completed_at else None,
                "processing_time_days": rma.processing_time_days
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo RMA: {str(e)}"
        )


class RMAStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


@router.patch("/rma/{rma_id}/status", status_code=status.HTTP_200_OK)
async def update_rma_status(
    rma_id: str,
    update_data: RMAStatusUpdate,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Actualiza el estado de un RMA
    """
    from app.models.rma_case import RMAStatus

    try:
        rma = await RMACase.get(rma_id)

        if not rma:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="RMA no encontrado"
            )

        # Update status
        rma.status = RMAStatus(update_data.status)
        rma.updated_at = datetime.utcnow()

        # Add note if provided
        if update_data.notes:
            await rma.add_note(
                author=str(current_user.id),
                text=update_data.notes,
                author_name=f"{current_user.nombre} {current_user.apellidos}"
            )

        # Update special fields based on status
        if update_data.status == "approved":
            rma.approved_by = str(current_user.id)
            rma.approved_at = datetime.utcnow()
        elif update_data.status == "completed":
            rma.completed_at = datetime.utcnow()
            rma.resolution_date = datetime.utcnow()

        await rma.save()

        return {
            "success": True,
            "message": "Estado de RMA actualizado",
            "rma": {
                "id": str(rma.id),
                "rma_number": rma.rma_number,
                "status": rma.status
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando RMA: {str(e)}"
        )


@router.post("/rma/bulk-import", status_code=status.HTTP_201_CREATED)
async def bulk_import_rma(
    file: UploadFile = File(...),
    current_user: Employee = Depends(get_current_employee)
):
    """
    Importación masiva de RMA desde CSV

    Formato CSV:
    imei,customer_name,customer_email,rma_type,reason,reason_detail

    Ejemplo:
    123456789012345,Juan Pérez,juan@email.com,repair,defective,Pantalla rota
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Solo se permiten archivos CSV"
            )

        # Read file
        contents = await file.read()
        decoded = contents.decode('utf-8')

        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(decoded))

        results = {
            "total": 0,
            "success": 0,
            "errors": []
        }

        for idx, row in enumerate(csv_reader, start=2):  # Start at 2 (header is row 1)
            results["total"] += 1

            try:
                imei = row.get('imei', '').strip()
                customer_name = row.get('customer_name', '').strip()
                customer_email = row.get('customer_email', '').strip()
                rma_type = row.get('rma_type', 'repair').strip().lower()
                reason = row.get('reason', 'defective').strip().lower()
                reason_detail = row.get('reason_detail', '').strip()

                if not imei:
                    results["errors"].append({
                        "row": idx,
                        "error": "IMEI requerido"
                    })
                    continue

                # Find device
                device = await Device.buscar_por_imei(imei)
                if not device:
                    results["errors"].append({
                        "row": idx,
                        "imei": imei,
                        "error": f"Dispositivo con IMEI {imei} no encontrado"
                    })
                    continue

                # Find or create customer
                customer = None
                if device.cliente_id:
                    customer = await Customer.get(device.cliente_id)

                # Generate RMA number
                rma_number = await RMACase.generate_rma_number()

                # Create RMA
                rma = RMACase(
                    rma_number=rma_number,
                    device_id=str(device.id),
                    imei=device.imei,
                    customer_id=str(customer.id) if customer else "UNKNOWN",
                    customer_name=customer_name or (customer.nombre if customer else "Cliente Desconocido"),
                    rma_type=RMAType(rma_type) if rma_type in ['repair', 'replacement', 'refund', 'exchange'] else RMAType.REPAIR,
                    reason=RMAReason(reason) if reason in ['defective', 'doa', 'warranty_claim', 'customer_dissatisfaction', 'wrong_product', 'damaged_in_transit', 'other'] else RMAReason.DEFECTIVE,
                    reason_detail=reason_detail,
                    status=RMAStatus.INITIATED,
                    created_by=str(current_user.id)
                )

                await rma.insert()
                results["success"] += 1

            except Exception as row_error:
                results["errors"].append({
                    "row": idx,
                    "imei": row.get('imei', ''),
                    "error": str(row_error)
                })

        return {
            "success": True,
            "message": f"Importación completada: {results['success']}/{results['total']} RMA creados",
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importando RMA: {str(e)}"
        )


class RMABatchCreate(BaseModel):
    imeis: List[str]
    rma_type: str = "repair"
    reason: str = "defective"
    reason_detail: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None


@router.post("/rma/bulk-create", status_code=status.HTTP_201_CREATED)
async def bulk_create_rma(
    data: RMABatchCreate,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Creación masiva de RMA desde lista de IMEIs
    Útil para escanear múltiples códigos de barras
    """
    try:
        results = {
            "total": len(data.imeis),
            "success": 0,
            "errors": [],
            "created_rmas": []
        }

        for imei in data.imeis:
            try:
                imei = imei.strip()
                if not imei:
                    continue

                # Find device
                device = await Device.buscar_por_imei(imei)
                if not device:
                    results["errors"].append({
                        "imei": imei,
                        "error": f"Dispositivo con IMEI {imei} no encontrado"
                    })
                    continue

                # Find customer
                customer = None
                if device.cliente_id:
                    customer = await Customer.get(device.cliente_id)

                # Generate RMA number
                rma_number = await RMACase.generate_rma_number()

                # Create RMA
                rma = RMACase(
                    rma_number=rma_number,
                    device_id=str(device.id),
                    imei=device.imei,
                    customer_id=str(customer.id) if customer else "UNKNOWN",
                    customer_name=data.customer_name or (customer.nombre if customer else "Cliente Desconocido"),
                    rma_type=RMAType(data.rma_type),
                    reason=RMAReason(data.reason),
                    reason_detail=data.reason_detail,
                    status=RMAStatus.INITIATED,
                    created_by=str(current_user.id)
                )

                await rma.insert()
                results["success"] += 1
                results["created_rmas"].append({
                    "rma_number": rma.rma_number,
                    "imei": rma.imei
                })

            except Exception as item_error:
                results["errors"].append({
                    "imei": imei,
                    "error": str(item_error)
                })

        return {
            "success": True,
            "message": f"Creados {results['success']}/{results['total']} RMA",
            "results": results
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando RMA en lote: {str(e)}"
        )


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_stats(
    current_user: Employee = Depends(get_current_employee)
):
    """
    Obtiene estadísticas de tickets y RMA
    """
    try:
        # Estadísticas de tickets
        total_tickets = await ServiceTicket.find_all().count()
        open_tickets = await ServiceTicket.find(ServiceTicket.status == TicketStatus.OPEN).count()
        in_progress_tickets = await ServiceTicket.find(ServiceTicket.status == TicketStatus.IN_PROGRESS).count()
        closed_tickets = await ServiceTicket.find(ServiceTicket.status == TicketStatus.CLOSED).count()

        # Estadísticas de RMA
        total_rma = await RMACase.find_all().count()
        pending_rma = await RMACase.find(RMACase.status == RMAStatus.PENDING_APPROVAL).count()

        # Tickets por prioridad
        critical_tickets = await ServiceTicket.find(ServiceTicket.priority == TicketPriority.CRITICAL).count()
        high_tickets = await ServiceTicket.find(ServiceTicket.priority == TicketPriority.HIGH).count()

        return {
            "success": True,
            "stats": {
                "tickets": {
                    "total": total_tickets,
                    "open": open_tickets,
                    "in_progress": in_progress_tickets,
                    "closed": closed_tickets,
                    "critical_priority": critical_tickets,
                    "high_priority": high_tickets
                },
                "rma": {
                    "total": total_rma,
                    "pending": pending_rma
                }
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════
# ENDPOINTS - PUBLIC USERS MANAGEMENT (ADMIN)
# ════════════════════════════════════════════════════════════════════

class PublicUserCreate(BaseModel):
    email: str
    password: str
    nombre: str
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    empresa: Optional[str] = None
    notes: Optional[str] = None


class PublicUserUpdate(BaseModel):
    status: Optional[str] = None
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    empresa: Optional[str] = None
    notes: Optional[str] = None


@router.get("/public-users", status_code=status.HTTP_200_OK)
async def get_public_users(
    status_filter: Optional[str] = Query(None, description="Filtrar por estado"),
    search: Optional[str] = Query(None, description="Buscar por email, nombre o empresa"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Employee = Depends(get_current_employee)
):
    """
    Obtiene lista de usuarios del portal público (ADMIN)
    """
    from app.models.public_user import PublicUser

    try:
        # Construir query
        query = {}

        if status_filter:
            query["status"] = status_filter

        if search:
            query["$or"] = [
                {"email": {"$regex": search, "$options": "i"}},
                {"nombre": {"$regex": search, "$options": "i"}},
                {"empresa": {"$regex": search, "$options": "i"}}
            ]

        # Obtener usuarios
        users = await PublicUser.find(query).sort("-created_at").skip(offset).limit(limit).to_list()
        total = await PublicUser.find(query).count()

        return {
            "success": True,
            "total": total,
            "limit": limit,
            "offset": offset,
            "users": [
                {
                    "id": str(user.id),
                    "email": user.email,
                    "nombre": user.nombre,
                    "apellidos": user.apellidos,
                    "telefono": user.telefono,
                    "empresa": user.empresa,
                    "status": user.status,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None,
                    "notes": user.notes
                }
                for user in users
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo usuarios públicos: {str(e)}"
        )


@router.post("/public-users", status_code=status.HTTP_201_CREATED)
async def create_public_user_admin(
    user_data: PublicUserCreate,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Crea un nuevo usuario del portal público desde admin
    """
    from app.models.public_user import PublicUser, PublicUserStatus
    import bcrypt

    try:
        # Verificar si el email ya existe
        existing_user = await PublicUser.buscar_por_email(user_data.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )

        # Hash password
        password_hash = bcrypt.hashpw(
            user_data.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # Crear usuario
        new_user = PublicUser(
            email=user_data.email,
            password_hash=password_hash,
            nombre=user_data.nombre,
            apellidos=user_data.apellidos,
            telefono=user_data.telefono,
            empresa=user_data.empresa,
            status=PublicUserStatus.ACTIVE,
            is_verified=True,  # Creado por admin, ya verificado
            notes=user_data.notes,
            created_by=str(current_user.id)
        )

        await new_user.insert()

        return {
            "success": True,
            "message": "Usuario público creado exitosamente",
            "user": {
                "id": str(new_user.id),
                "email": new_user.email,
                "nombre": new_user.nombre,
                "status": new_user.status
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando usuario público: {str(e)}"
        )


@router.patch("/public-users/{user_id}", status_code=status.HTTP_200_OK)
async def update_public_user_admin(
    user_id: str,
    update_data: PublicUserUpdate,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Actualiza un usuario del portal público (ADMIN)
    """
    from app.models.public_user import PublicUser, PublicUserStatus

    try:
        user = await PublicUser.get(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Actualizar campos
        if update_data.status:
            user.status = PublicUserStatus(update_data.status)

        if update_data.nombre:
            user.nombre = update_data.nombre

        if update_data.apellidos is not None:
            user.apellidos = update_data.apellidos

        if update_data.telefono is not None:
            user.telefono = update_data.telefono

        if update_data.empresa is not None:
            user.empresa = update_data.empresa

        if update_data.notes is not None:
            user.notes = update_data.notes

        user.updated_at = datetime.utcnow()

        await user.save()

        return {
            "success": True,
            "message": "Usuario actualizado exitosamente",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "nombre": user.nombre,
                "status": user.status
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando usuario: {str(e)}"
        )


@router.get("/public-users/{user_id}/tickets", status_code=status.HTTP_200_OK)
async def get_public_user_tickets(
    user_id: str,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Obtiene todos los tickets de un usuario público (ADMIN)
    """
    from app.models.public_user import PublicUser

    try:
        user = await PublicUser.get(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )

        # Buscar tickets por email del usuario
        tickets = await ServiceTicket.find(
            ServiceTicket.customer_email == user.email
        ).sort("-created_at").to_list()

        return {
            "success": True,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "nombre": user.nombre
            },
            "total_tickets": len(tickets),
            "tickets": [
                {
                    "id": str(ticket.id),
                    "ticket_number": ticket.ticket_number,
                    "device_imei": ticket.device_imei,
                    "issue_type": ticket.issue_type,
                    "status": ticket.status,
                    "priority": ticket.priority,
                    "created_at": ticket.created_at.isoformat()
                }
                for ticket in tickets
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo tickets del usuario: {str(e)}"
        )
