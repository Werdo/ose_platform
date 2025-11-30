"""
OSE Platform - Router para Albaranes/Delivery Notes
Gestión de albaranes con códigos de palet EST912
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import logging

from app.models.delivery_note import DeliveryNote, DeliveryNoteSequence
from app.models.employee import Employee
from app.dependencies.auth import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/delivery-notes",
    tags=["Delivery Notes / Albaranes"]
)


# ════════════════════════════════════════════════════════════════════════
# CREAR ALBARÁN
# ════════════════════════════════════════════════════════════════════════

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_delivery_note(
    delivery_note_number: str = Query(..., description="Número de albarán"),
    customer_name: str = Query(..., description="Nombre del cliente"),
    total_boxes: int = Query(..., ge=1, description="Cantidad total de cajas"),
    order_number: Optional[str] = Query(None, description="Número de pedido"),
    customer_code: Optional[str] = Query(None, description="Código de cliente"),
    box_configuration: Optional[str] = Query(None, description="Configuración de cajas"),
    total_units: Optional[int] = Query(None, description="Total de unidades"),
    product_description: Optional[str] = Query(None, description="Descripción del producto"),
    sender_name: str = Query("Oversun Energy SL", description="Nombre del remitente"),
    sender_address: Optional[str] = Query(None, description="Dirección del remitente"),
    destination_address: Optional[str] = Query(None, description="Dirección de destino"),
    total_pallets_in_order: int = Query(1, ge=1, description="Total de palets en el pedido"),
    pallet_number_in_order: int = Query(1, ge=1, description="Número de este palet"),
    labels_to_print: int = Query(1, ge=1, description="Cantidad de etiquetas a imprimir"),
    notes: Optional[str] = Query(None, description="Notas adicionales"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **Crear nuevo albarán con código de palet EST912**

    El sistema genera automáticamente un código único en formato EST912XXXXXXXXXX:
    - EST: Código de país (España)
    - 912: Código fijo
    - XXXXXXXXXX: Número secuencial de 10 dígitos

    Parámetros requeridos:
    - delivery_note_number: Número de albarán
    - customer_name: Nombre del cliente
    - total_boxes: Cantidad de cajas en el palet
    """
    try:
        # Generar código de palet EST912
        pallet_code = await DeliveryNote.generate_pallet_code()

        # Crear albarán
        delivery_note = DeliveryNote(
            pallet_code=pallet_code,
            delivery_note_number=delivery_note_number,
            order_number=order_number,
            customer_name=customer_name,
            customer_code=customer_code,
            total_boxes=total_boxes,
            box_configuration=box_configuration,
            total_units=total_units,
            product_description=product_description,
            sender_name=sender_name,
            sender_address=sender_address,
            destination_address=destination_address,
            total_pallets_in_order=total_pallets_in_order,
            pallet_number_in_order=pallet_number_in_order,
            labels_to_print=labels_to_print,
            notes=notes,
            created_by=current_user.email,
            status="preparado"
        )

        await delivery_note.insert()

        logger.info(f"Albarán creado: {pallet_code} - {delivery_note_number} por {current_user.email}")

        return {
            "success": True,
            "message": "Albarán creado exitosamente",
            "delivery_note": delivery_note.to_dict()
        }

    except Exception as e:
        logger.error(f"Error creando albarán: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el albarán: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# CONSULTAR ALBARANES
# ════════════════════════════════════════════════════════════════════════

@router.get("", status_code=status.HTTP_200_OK)
async def list_delivery_notes(
    status_filter: Optional[str] = Query(None, description="Filtrar por estado"),
    customer_name: Optional[str] = Query(None, description="Filtrar por cliente"),
    order_number: Optional[str] = Query(None, description="Filtrar por número de pedido"),
    delivery_note_number: Optional[str] = Query(None, description="Filtrar por número de albarán"),
    pallet_code: Optional[str] = Query(None, description="Filtrar por código de palet"),
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0),
    current_user: Employee = Depends(get_current_active_user)
):
    """Listar albaranes con filtros opcionales"""
    try:
        query = {}

        if status_filter:
            query["status"] = status_filter

        if customer_name:
            query["customer_name"] = {"$regex": customer_name, "$options": "i"}

        if order_number:
            query["order_number"] = order_number

        if delivery_note_number:
            query["delivery_note_number"] = delivery_note_number

        if pallet_code:
            query["pallet_code"] = pallet_code

        if fecha_desde or fecha_hasta:
            query["created_at"] = {}
            if fecha_desde:
                query["created_at"]["$gte"] = datetime.fromisoformat(fecha_desde)
            if fecha_hasta:
                query["created_at"]["$lte"] = datetime.fromisoformat(fecha_hasta)

        delivery_notes = await DeliveryNote.find(query).sort("-created_at").skip(skip).limit(limit).to_list()
        total = await DeliveryNote.find(query).count()

        return {
            "success": True,
            "count": len(delivery_notes),
            "total": total,
            "skip": skip,
            "limit": limit,
            "delivery_notes": [dn.to_dict() for dn in delivery_notes]
        }

    except Exception as e:
        logger.error(f"Error listando albaranes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar albaranes: {str(e)}"
        )


@router.get("/{delivery_note_id}", status_code=status.HTTP_200_OK)
async def get_delivery_note(
    delivery_note_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener albarán por ID"""
    try:
        if not ObjectId.is_valid(delivery_note_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de albarán inválido"
            )

        delivery_note = await DeliveryNote.get(ObjectId(delivery_note_id))

        if not delivery_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Albarán no encontrado"
            )

        return {
            "success": True,
            "delivery_note": delivery_note.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo albarán: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el albarán: {str(e)}"
        )


@router.get("/by-pallet-code/{pallet_code}", status_code=status.HTTP_200_OK)
async def get_by_pallet_code(
    pallet_code: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener albarán por código de palet EST912"""
    try:
        delivery_note = await DeliveryNote.find_one(DeliveryNote.pallet_code == pallet_code)

        if not delivery_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Albarán con código de palet {pallet_code} no encontrado"
            )

        return {
            "success": True,
            "delivery_note": delivery_note.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo albarán por código: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el albarán: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# ACTUALIZAR ALBARÁN
# ════════════════════════════════════════════════════════════════════════

@router.put("/{delivery_note_id}", status_code=status.HTTP_200_OK)
async def update_delivery_note(
    delivery_note_id: str,
    delivery_note_number: Optional[str] = Query(None),
    customer_name: Optional[str] = Query(None),
    customer_code: Optional[str] = Query(None),
    total_boxes: Optional[int] = Query(None, ge=1),
    box_configuration: Optional[str] = Query(None),
    total_units: Optional[int] = Query(None),
    product_description: Optional[str] = Query(None),
    destination_address: Optional[str] = Query(None),
    labels_to_print: Optional[int] = Query(None, ge=1),
    notes: Optional[str] = Query(None),
    current_user: Employee = Depends(get_current_active_user)
):
    """Actualizar albarán existente"""
    try:
        if not ObjectId.is_valid(delivery_note_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de albarán inválido"
            )

        delivery_note = await DeliveryNote.get(ObjectId(delivery_note_id))

        if not delivery_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Albarán no encontrado"
            )

        # Actualizar campos si se proporcionan
        if delivery_note_number is not None:
            delivery_note.delivery_note_number = delivery_note_number
        if customer_name is not None:
            delivery_note.customer_name = customer_name
        if customer_code is not None:
            delivery_note.customer_code = customer_code
        if total_boxes is not None:
            delivery_note.total_boxes = total_boxes
        if box_configuration is not None:
            delivery_note.box_configuration = box_configuration
        if total_units is not None:
            delivery_note.total_units = total_units
        if product_description is not None:
            delivery_note.product_description = product_description
        if destination_address is not None:
            delivery_note.destination_address = destination_address
        if labels_to_print is not None:
            delivery_note.labels_to_print = labels_to_print
        if notes is not None:
            delivery_note.notes = notes

        delivery_note.updated_at = datetime.utcnow()
        await delivery_note.save()

        logger.info(f"Albarán actualizado: {delivery_note.pallet_code}")

        return {
            "success": True,
            "message": "Albarán actualizado exitosamente",
            "delivery_note": delivery_note.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando albarán: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el albarán: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# ACTUALIZAR ESTADO
# ════════════════════════════════════════════════════════════════════════

@router.put("/{delivery_note_id}/status", status_code=status.HTTP_200_OK)
async def update_status(
    delivery_note_id: str,
    new_status: str = Query(..., description="preparado, enviado, entregado, cancelado"),
    current_user: Employee = Depends(get_current_active_user)
):
    """Actualizar estado del albarán"""
    try:
        if not ObjectId.is_valid(delivery_note_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de albarán inválido"
            )

        delivery_note = await DeliveryNote.get(ObjectId(delivery_note_id))

        if not delivery_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Albarán no encontrado"
            )

        valid_statuses = ["preparado", "enviado", "entregado", "cancelado"]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido. Debe ser uno de: {', '.join(valid_statuses)}"
            )

        # Usar métodos específicos si existen
        if new_status == "enviado":
            await delivery_note.mark_as_sent()
        elif new_status == "entregado":
            await delivery_note.mark_as_delivered()
        elif new_status == "cancelado":
            await delivery_note.cancel()
        else:
            delivery_note.status = new_status
            delivery_note.updated_at = datetime.utcnow()
            await delivery_note.save()

        logger.info(f"Estado de albarán {delivery_note.pallet_code} cambiado a: {new_status}")

        return {
            "success": True,
            "message": f"Estado actualizado a {new_status}",
            "delivery_note": delivery_note.to_dict()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando estado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el estado: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# ESTADÍSTICAS
# ════════════════════════════════════════════════════════════════════════

@router.get("/stats/summary", status_code=status.HTTP_200_OK)
async def get_statistics(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estadísticas generales de albaranes"""
    try:
        total = await DeliveryNote.find().count()
        preparados = await DeliveryNote.find(DeliveryNote.status == "preparado").count()
        enviados = await DeliveryNote.find(DeliveryNote.status == "enviado").count()
        entregados = await DeliveryNote.find(DeliveryNote.status == "entregado").count()
        cancelados = await DeliveryNote.find(DeliveryNote.status == "cancelado").count()

        # Obtener el valor actual del contador
        sequence = await DeliveryNoteSequence.find_one(
            DeliveryNoteSequence.sequence_name == "EST912"
        )

        return {
            "success": True,
            "statistics": {
                "total": total,
                "preparados": preparados,
                "enviados": enviados,
                "entregados": entregados,
                "cancelados": cancelados,
                "next_sequence_number": sequence.current_value + 1 if sequence else 1
            }
        }

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# GENERAR PREVIEW DE CÓDIGO (PARA TESTING)
# ════════════════════════════════════════════════════════════════════════

@router.get("/preview/next-code", status_code=status.HTTP_200_OK)
async def preview_next_code(
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **Preview del próximo código EST912 sin crearlo**

    Útil para ver qué código se generaría en el próximo albarán
    """
    try:
        sequence = await DeliveryNoteSequence.find_one(
            DeliveryNoteSequence.sequence_name == "EST912"
        )

        if not sequence:
            next_value = 1
        else:
            next_value = sequence.current_value + 1

        next_code = f"EST912{str(next_value).zfill(10)}"

        return {
            "success": True,
            "next_code": next_code,
            "next_sequence_number": next_value,
            "note": "Este es solo un preview. El código real se genera al crear el albarán."
        }

    except Exception as e:
        logger.error(f"Error generando preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar preview: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# GENERACIÓN DE ETIQUETAS
# ════════════════════════════════════════════════════════════════════════

@router.get("/{delivery_note_id}/label/pdf", status_code=status.HTTP_200_OK)
async def generate_pdf_label(
    delivery_note_id: str,
    labels_count: int = Query(1, ge=1, le=100, description="Cantidad de etiquetas"),
    label_size: str = Query("A6", description="Tamaño: 100x150, 100x100, A6"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **Generar etiquetas PDF para impresión en folios A4**

    Compatible con impresoras láser/inkjet estándar.
    Las etiquetas incluyen código de barras EST912.
    """
    try:
        from app.services.label_generator import LabelGenerator
        from fastapi.responses import Response

        if not ObjectId.is_valid(delivery_note_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de albarán inválido"
            )

        delivery_note = await DeliveryNote.get(ObjectId(delivery_note_id))

        if not delivery_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Albarán no encontrado"
            )

        # Generar PDF
        pdf_data = LabelGenerator.generate_pdf_label(
            delivery_note.to_dict(),
            labels_count=labels_count,
            label_size=label_size
        )

        logger.info(f"PDF generado para albarán {delivery_note.pallet_code} - {labels_count} etiquetas")

        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="etiqueta_{delivery_note.pallet_code}.pdf"'
            }
        )

    except ImportError as e:
        logger.error(f"Error importando dependencias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Librerías de generación de PDF no disponibles. Instalar: pip install reportlab python-barcode pillow"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando PDF: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar PDF: {str(e)}"
        )


@router.get("/{delivery_note_id}/label/zpl", status_code=status.HTTP_200_OK)
async def generate_zpl_label(
    delivery_note_id: str,
    dpi: int = Query(203, description="DPI impresora (203 o 300)"),
    label_width: int = Query(100, description="Ancho etiqueta (mm)"),
    label_height: int = Query(150, description="Alto etiqueta (mm)"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **Generar etiqueta ZPL para impresoras Zebra**

    Compatible con impresoras de etiquetas Zebra (ZPL II).
    Retorna código ZPL listo para enviar a la impresora.
    """
    try:
        from app.services.label_generator import LabelGenerator

        if not ObjectId.is_valid(delivery_note_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de albarán inválido"
            )

        delivery_note = await DeliveryNote.get(ObjectId(delivery_note_id))

        if not delivery_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Albarán no encontrado"
            )

        # Generar ZPL
        zpl_code = LabelGenerator.generate_zpl_label(
            delivery_note.to_dict(),
            dpi=dpi,
            label_width=label_width,
            label_height=label_height
        )

        logger.info(f"ZPL generado para albarán {delivery_note.pallet_code}")

        return {
            "success": True,
            "pallet_code": delivery_note.pallet_code,
            "format": "ZPL",
            "zpl_code": zpl_code,
            "instructions": {
                "method_1": "Copiar el código ZPL y enviarlo directamente a la impresora Zebra",
                "method_2": "Guardar en archivo .zpl y enviar a la impresora",
                "method_3": "Usar software Zebra Designer para previsualizar"
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando ZPL: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar ZPL: {str(e)}"
        )


@router.get("/{delivery_note_id}/label/preview", status_code=status.HTTP_200_OK)
async def generate_html_preview(
    delivery_note_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **Previsualizar etiqueta en HTML**

    Genera una vista previa HTML de la etiqueta para visualizar en navegador.
    Útil para verificar antes de imprimir.
    """
    try:
        from app.services.label_generator import LabelGenerator
        from fastapi.responses import HTMLResponse

        if not ObjectId.is_valid(delivery_note_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de albarán inválido"
            )

        delivery_note = await DeliveryNote.get(ObjectId(delivery_note_id))

        if not delivery_note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Albarán no encontrado"
            )

        # Generar HTML preview
        html_content = LabelGenerator.generate_html_preview(delivery_note.to_dict())

        logger.info(f"Preview HTML generado para albarán {delivery_note.pallet_code}")

        return HTMLResponse(content=html_content)

    except ImportError as e:
        logger.error(f"Error importando dependencias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Librerías de generación de etiquetas no disponibles"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando preview HTML: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al generar preview: {str(e)}"
        )
