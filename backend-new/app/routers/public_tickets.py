"""
OSE Platform - Public Tickets Router
Endpoints para que usuarios externos creen y consulten sus tickets
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.models.public_user import PublicUser
from app.models.service_ticket import ServiceTicket, TicketStatus, TicketPriority
from app.models.device import Device
from app.routers.public_auth import get_current_public_user

router = APIRouter(
    prefix="/public/tickets",
    tags=["Public Portal - Tickets"]
)


# ════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ════════════════════════════════════════════════════════════════════════

class PublicTicketCreate(BaseModel):
    device_imei: str
    issue_type: str
    description: str
    priority: str = "medium"


class PublicTicketMessage(BaseModel):
    message: str


# ════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════════════════

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_public_ticket(
    ticket_data: PublicTicketCreate,
    current_user: PublicUser = Depends(get_current_public_user)
):
    """
    Crea un nuevo ticket desde el portal público

    **Campos:**
    - device_imei: IMEI del dispositivo con problemas
    - issue_type: Tipo de problema (technical, hardware, software, connectivity, other)
    - description: Descripción detallada del problema
    - priority: Prioridad (low, medium, high, critical) - Default: medium
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
            customer_name=f"{current_user.nombre} {current_user.apellidos or ''}".strip(),
            customer_email=current_user.email,
            issue_type=ticket_data.issue_type,
            description=ticket_data.description,
            priority=TicketPriority(ticket_data.priority),
            status=TicketStatus.OPEN,
            reported_by=f"{current_user.nombre} (Portal Público)",
            created_by=str(current_user.id)  # ID del usuario público
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
                "device_imei": ticket.device_imei,
                "created_at": ticket.created_at.isoformat()
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creando ticket: {str(e)}"
        )


@router.get("/", status_code=status.HTTP_200_OK)
async def get_my_tickets(
    status_filter: Optional[str] = Query(None, description="Filtrar por estado"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: PublicUser = Depends(get_current_public_user)
):
    """
    Obtiene todos los tickets del usuario público actual
    """
    try:
        # Construir query - solo tickets del usuario actual
        query = {"customer_email": current_user.email}

        if status_filter:
            query["status"] = status_filter

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
                    "issue_type": ticket.issue_type,
                    "description": ticket.description,
                    "status": ticket.status,
                    "priority": ticket.priority,
                    "created_at": ticket.created_at.isoformat(),
                    "updated_at": ticket.updated_at.isoformat(),
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


@router.get("/{ticket_id}", status_code=status.HTTP_200_OK)
async def get_ticket_details(
    ticket_id: str,
    current_user: PublicUser = Depends(get_current_public_user)
):
    """
    Obtiene detalles de un ticket específico
    Solo si pertenece al usuario actual
    """
    try:
        ticket = await ServiceTicket.get(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )

        # Verificar que el ticket pertenece al usuario
        if ticket.customer_email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para ver este ticket"
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
                    "imei": device.imei if device else None,
                    "marca": device.marca if device else None,
                    "estado": device.estado if device else None
                } if device else None,
                "issue_type": ticket.issue_type,
                "description": ticket.description,
                "status": ticket.status,
                "priority": ticket.priority,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat(),
                "closed_at": ticket.closed_at.isoformat() if ticket.closed_at else None,
                "assigned_to": ticket.assigned_to,
                "resolution": ticket.resolution,
                "messages": ticket.messages or []
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo ticket: {str(e)}"
        )


@router.post("/{ticket_id}/messages", status_code=status.HTTP_201_CREATED)
async def add_message_to_ticket(
    ticket_id: str,
    message_data: PublicTicketMessage,
    current_user: PublicUser = Depends(get_current_public_user)
):
    """
    Añade un mensaje a un ticket
    Solo si pertenece al usuario actual
    """
    try:
        ticket = await ServiceTicket.get(ticket_id)

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )

        # Verificar que el ticket pertenece al usuario
        if ticket.customer_email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tiene permiso para comentar en este ticket"
            )

        # Crear mensaje
        new_message = {
            "from_user": f"{current_user.nombre} (Cliente)",
            "from_role": "public_user",
            "message": message_data.message,
            "timestamp": datetime.utcnow(),
            "attachments": []
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


@router.get("/track/{ticket_number}", status_code=status.HTTP_200_OK)
async def track_ticket_by_number(
    ticket_number: str,
    email: str = Query(..., description="Email del cliente"),
    current_user: PublicUser = Depends(get_current_public_user)
):
    """
    Rastrea un ticket por su número
    Requiere el email del cliente para validación
    """
    try:
        # Buscar ticket
        ticket = await ServiceTicket.find_one(
            ServiceTicket.ticket_number == ticket_number
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket no encontrado"
            )

        # Verificar email
        if ticket.customer_email != email or ticket.customer_email != current_user.email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email no coincide con el ticket"
            )

        return {
            "success": True,
            "ticket": {
                "ticket_number": ticket.ticket_number,
                "status": ticket.status,
                "priority": ticket.priority,
                "created_at": ticket.created_at.isoformat(),
                "updated_at": ticket.updated_at.isoformat(),
                "description": ticket.description,
                "messages_count": len(ticket.messages) if ticket.messages else 0
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rastreando ticket: {str(e)}"
        )
