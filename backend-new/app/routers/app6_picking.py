"""
OSE Platform - App 6: Sistema de Picking y Etiquetado
Router para gestión de palets y paquetería con tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
import logging
import re
import uuid
import qrcode
from io import BytesIO, StringIO
import base64
import csv
import pandas as pd

from app.models.pallet import Pallet
from app.models.package import Package
from app.models.device import Device
from app.models.employee import Employee
from app.dependencies.auth import get_current_active_user
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/app6", tags=["App 6: Picking & Etiquetado"])

# Mantener compatibilidad con código antiguo
PalletItem = Pallet


# ════════════════════════════════════════════════════════════════════════
# PICKING DE PALETS
# ════════════════════════════════════════════════════════════════════════

@router.post("/palets/nuevo")
async def crear_palet(
    tipo_contenido: str = Query(..., description="lote, caja, unidad, sku"),
    contenido_ids: List[str] = Query(..., description="IDs de lotes, cajas o dispositivos"),
    pedido_id: Optional[str] = Query(None, description="Código del pedido asociado"),
    peso_kg: Optional[float] = Query(None, description="Peso aproximado en kg"),
    volumen_m3: Optional[float] = Query(None, description="Volumen aproximado en m³"),
    ubicacion: Optional[str] = Query(None, description="Ubicación en almacén"),
    notas: Optional[str] = Query(None, description="Observaciones adicionales"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **Crear nuevo palet** con contenido escaneado

    Genera número de palet único y código QR para etiqueta A4

    - **tipo_contenido**: Tipo de contenido (lote, caja, unidad, sku)
    - **contenido_ids**: Lista de IDs escaneados
    - **pedido_id**: Pedido asociado (opcional)
    - **peso_kg**: Peso aproximado
    """
    try:
        # Generar número de palet único
        year = datetime.utcnow().year
        existing_count = await PalletItem.find().count() + 1
        pallet_number = f"PAL-{year}-{existing_count:04d}"

        # Generar código QR único
        qr_code = f"QR-{pallet_number}-{uuid.uuid4().hex[:8].upper()}"

        # Buscar dispositivos si el contenido es de tipo unidad o IMEI
        dispositivos_refs = []
        if tipo_contenido in ["unidad", "imei"]:
            for content_id in contenido_ids:
                # Intentar buscar por IMEI o serial
                device = await Device.find_one(
                    {"$or": [
                        {"imei": content_id},
                        {"serial_number": content_id}
                    ]}
                )
                if device:
                    dispositivos_refs.append(device.id)

        # Crear palet
        pallet = PalletItem(
            pallet_number=pallet_number,
            qr_code=qr_code,
            tipo_contenido=tipo_contenido,
            contenido_ids=contenido_ids,
            dispositivos=dispositivos_refs,
            pedido_id=pedido_id,
            peso_kg=peso_kg,
            volumen_m3=volumen_m3,
            ubicacion=ubicacion,
            notas=notas,
            creado_por=current_user.email,
            estado="preparado"
        )

        await pallet.save()

        logger.info(f"Palet creado: {pallet_number} por {current_user.email}")

        return {
            "success": True,
            "pallet_id": str(pallet.id),
            "pallet_number": pallet_number,
            "qr_code": qr_code,
            "contenido": {
                "tipo": tipo_contenido,
                "cantidad": len(contenido_ids),
                "dispositivos_vinculados": len(dispositivos_refs)
            },
            "message": "Palet creado exitosamente"
        }

    except Exception as e:
        logger.error(f"Error creando palet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el palet: {str(e)}"
        )


@router.get("/palets/{pallet_id}")
async def obtener_palet(
    pallet_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener detalles de un palet por ID"""
    try:
        if not ObjectId.is_valid(pallet_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de palet inválido"
            )

        pallet = await PalletItem.get(ObjectId(pallet_id))

        if not pallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Palet no encontrado"
            )

        return pallet

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo palet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el palet: {str(e)}"
        )


@router.get("/palets")
async def listar_palets(
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    pedido_id: Optional[str] = Query(None, description="Filtrar por pedido"),
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: Employee = Depends(get_current_active_user)
):
    """Listar palets con filtros opcionales"""
    try:
        query = {}

        if estado:
            query["estado"] = estado

        if pedido_id:
            query["pedido_id"] = pedido_id

        if fecha_desde or fecha_hasta:
            query["fecha_creacion"] = {}
            if fecha_desde:
                query["fecha_creacion"]["$gte"] = datetime.fromisoformat(fecha_desde)
            if fecha_hasta:
                query["fecha_creacion"]["$lte"] = datetime.fromisoformat(fecha_hasta)

        palets = await PalletItem.find(query).sort("-fecha_creacion").skip(skip).limit(limit).to_list()
        total = await PalletItem.find(query).count()

        return {
            "palets": palets,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error listando palets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar palets: {str(e)}"
        )


@router.put("/palets/{pallet_id}/estado")
async def actualizar_estado_palet(
    pallet_id: str,
    nuevo_estado: str = Query(..., description="preparado, en_transito, entregado, cancelado"),
    current_user: Employee = Depends(get_current_active_user)
):
    """Actualizar estado de un palet"""
    try:
        if not ObjectId.is_valid(pallet_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de palet inválido"
            )

        pallet = await PalletItem.get(ObjectId(pallet_id))

        if not pallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Palet no encontrado"
            )

        estados_validos = ["preparado", "en_transito", "entregado", "cancelado"]
        if nuevo_estado not in estados_validos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}"
            )

        pallet.estado = nuevo_estado
        pallet.fecha_modificacion = datetime.utcnow()
        await pallet.save()

        logger.info(f"Palet {pallet.pallet_number} actualizado a estado: {nuevo_estado}")

        return {
            "success": True,
            "pallet_number": pallet.pallet_number,
            "estado": nuevo_estado,
            "message": "Estado actualizado correctamente"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando estado del palet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar estado: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# PICKING DE PAQUETERÍA (con tracking)
# ════════════════════════════════════════════════════════════════════════

def validar_tracking_format(tracking_number: str, transportista: str) -> bool:
    """Valida el formato del número de tracking según el transportista"""
    patterns = {
        "seur": r"^[A-Z]{2}\d{9}[A-Z]{2}$",  # Ej: CX123456789ES
        "correos": r"^\d{14}$",  # 14 dígitos
        "dhl": r"^\d{10,11}$",  # 10-11 dígitos
        "ups": r"^1Z[A-Z0-9]{16}$",  # Formato UPS
        "fedex": r"^\d{12,14}$",  # 12-14 dígitos
    }

    pattern = patterns.get(transportista.lower())
    if not pattern:
        return True  # Aceptar si no hay patrón definido

    return bool(re.match(pattern, tracking_number))


@router.post("/paquetes/nuevo")
async def crear_paquete(
    tracking_number: str = Query(..., description="Número de seguimiento del transportista"),
    transportista: str = Query(..., description="Nombre del transportista (Seur, Correos, etc.)"),
    order_code: str = Query(..., description="Código del pedido web"),
    cliente_email: str = Query(..., description="Email del cliente"),
    dispositivos_imeis: List[str] = Query(..., description="Lista de IMEIs a incluir"),
    cliente_nombre: Optional[str] = Query(None),
    direccion_envio: Optional[str] = Query(None),
    ciudad: Optional[str] = Query(None),
    codigo_postal: Optional[str] = Query(None),
    peso_kg: Optional[float] = Query(None),
    enlace_seguimiento: Optional[str] = Query(None),
    notas: Optional[str] = Query(None),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **Crear nuevo paquete** con tracking de transportista

    Asocia dispositivos escaneados con el tracking y envía email al cliente

    - **tracking_number**: Número de seguimiento leído de la etiqueta
    - **transportista**: Seur, Correos, DHL, etc.
    - **order_code**: Código del pedido web
    - **dispositivos_imeis**: IMEIs de los dispositivos incluidos
    """
    try:
        # Validar formato del tracking
        if not validar_tracking_format(tracking_number, transportista):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Formato de tracking inválido para {transportista}"
            )

        # Verificar que no exista el tracking
        existing = await Package.find_one({"tracking_number": tracking_number})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un paquete con el tracking {tracking_number}"
            )

        # Buscar y validar dispositivos
        dispositivos_refs = []
        dispositivos_info = []

        for imei in dispositivos_imeis:
            device = await Device.find_one({"imei": imei})

            if not device:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Dispositivo con IMEI {imei} no encontrado"
                )

            # Verificar que el dispositivo esté disponible
            if hasattr(device, 'status') and device.status not in ["available", "ready", "in_stock"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Dispositivo {imei} no está disponible (estado: {device.status})"
                )

            dispositivos_refs.append(device.id)
            dispositivos_info.append({
                "imei": device.imei,
                "modelo": getattr(device, 'model', 'N/A'),
                "descripcion": getattr(device, 'description', ''),
                "serial_number": getattr(device, 'serial_number', '')
            })

        # Crear paquete
        package = Package(
            tracking_number=tracking_number,
            transportista=transportista,
            order_code=order_code,
            cliente_email=cliente_email,
            cliente_nombre=cliente_nombre,
            direccion_envio=direccion_envio,
            ciudad=ciudad,
            codigo_postal=codigo_postal,
            dispositivos=dispositivos_refs,
            dispositivos_info=dispositivos_info,
            peso_kg=peso_kg,
            enlace_seguimiento=enlace_seguimiento,
            notas=notas,
            creado_por=current_user.email,
            estado="preparado"
        )

        await package.save()

        logger.info(f"Paquete creado: {tracking_number} con {len(dispositivos_refs)} dispositivos")

        return {
            "success": True,
            "package_id": str(package.id),
            "tracking_number": tracking_number,
            "transportista": transportista,
            "order_code": order_code,
            "dispositivos_incluidos": len(dispositivos_refs),
            "cliente_email": cliente_email,
            "message": "Paquete creado exitosamente. Listo para enviar notificación al cliente."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando paquete: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el paquete: {str(e)}"
        )


@router.get("/paquetes/{tracking_number}")
async def obtener_paquete_por_tracking(
    tracking_number: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener detalles de un paquete por número de tracking"""
    try:
        package = await Package.find_one({"tracking_number": tracking_number})

        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paquete con tracking {tracking_number} no encontrado"
            )

        return package

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo paquete: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el paquete: {str(e)}"
        )


@router.get("/paquetes")
async def listar_paquetes(
    transportista: Optional[str] = Query(None, description="Filtrar por transportista"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    order_code: Optional[str] = Query(None, description="Filtrar por pedido"),
    cliente_email: Optional[str] = Query(None, description="Filtrar por cliente"),
    fecha_desde: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    fecha_hasta: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: Employee = Depends(get_current_active_user)
):
    """Listar paquetes con filtros opcionales"""
    try:
        query = {}

        if transportista:
            query["transportista"] = {"$regex": transportista, "$options": "i"}

        if estado:
            query["estado"] = estado

        if order_code:
            query["order_code"] = order_code

        if cliente_email:
            query["cliente_email"] = cliente_email

        if fecha_desde or fecha_hasta:
            query["fecha_creacion"] = {}
            if fecha_desde:
                query["fecha_creacion"]["$gte"] = datetime.fromisoformat(fecha_desde)
            if fecha_hasta:
                query["fecha_creacion"]["$lte"] = datetime.fromisoformat(fecha_hasta)

        packages = await Package.find(query).sort("-fecha_creacion").skip(skip).limit(limit).to_list()
        total = await Package.find(query).count()

        return {
            "paquetes": packages,
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        logger.error(f"Error listando paquetes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar paquetes: {str(e)}"
        )


@router.put("/paquetes/{tracking_number}/estado")
async def actualizar_estado_paquete(
    tracking_number: str,
    nuevo_estado: str = Query(..., description="preparado, enviado, en_transito, entregado, incidencia"),
    current_user: Employee = Depends(get_current_active_user)
):
    """Actualizar estado de un paquete"""
    try:
        package = await Package.find_one({"tracking_number": tracking_number})

        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paquete con tracking {tracking_number} no encontrado"
            )

        await package.actualizar_estado(nuevo_estado)

        logger.info(f"Paquete {tracking_number} actualizado a estado: {nuevo_estado}")

        return {
            "success": True,
            "tracking_number": tracking_number,
            "estado": nuevo_estado,
            "message": "Estado actualizado correctamente"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando estado del paquete: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar estado: {str(e)}"
        )


@router.post("/paquetes/{tracking_number}/marcar-enviado")
async def marcar_paquete_enviado(
    tracking_number: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Marcar paquete como enviado y registrar fecha"""
    try:
        package = await Package.find_one({"tracking_number": tracking_number})

        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paquete con tracking {tracking_number} no encontrado"
            )

        await package.marcar_como_enviado()

        logger.info(f"Paquete {tracking_number} marcado como enviado")

        return {
            "success": True,
            "tracking_number": tracking_number,
            "estado": "enviado",
            "fecha_envio": package.fecha_envio,
            "message": "Paquete marcado como enviado"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marcando paquete como enviado: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al marcar como enviado: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# NOTIFICACIÓN POR EMAIL
# ════════════════════════════════════════════════════════════════════════

@router.post("/paquetes/{tracking_number}/notificar")
async def enviar_notificacion_cliente(
    tracking_number: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **Enviar email de notificación al cliente**

    Envía un email con los detalles del envío:
    - Número de tracking
    - Transportista
    - Dispositivos incluidos
    - Enlace de seguimiento
    """
    try:
        package = await Package.find_one({"tracking_number": tracking_number})

        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paquete con tracking {tracking_number} no encontrado"
            )

        if package.email_enviado:
            logger.warning(f"Email ya fue enviado para el paquete {tracking_number}")
            return {
                "success": False,
                "message": "El email de notificación ya fue enviado anteriormente",
                "fecha_envio_email": package.fecha_email
            }

        # TODO: Implementar envío de email real con servicio de email
        # Por ahora solo registramos que se "envió"

        await package.marcar_email_enviado()

        logger.info(f"Email de notificación enviado para paquete {tracking_number}")

        return {
            "success": True,
            "tracking_number": tracking_number,
            "cliente_email": package.cliente_email,
            "dispositivos_incluidos": len(package.dispositivos),
            "message": "Email de notificación enviado correctamente",
            "fecha_envio": package.fecha_email
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enviando notificación: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar notificación: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# PICKING JERÁRQUICO (PALLET → CARTON → DEVICE)
# ════════════════════════════════════════════════════════════════════════

@router.post("/hierarchy/import")
async def importar_picking_jerarquico(
    file: UploadFile = File(..., description="Archivo CSV con datos de picking"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **Importar datos de picking jerárquico desde CSV**

    Formato esperado del CSV:
    - order_number: Número de orden de producción
    - imei: IMEI del dispositivo (15 dígitos)
    - iccid: ICCID de la SIM (19-20 caracteres)
    - carton_id: ID del cartón/caja
    - pallet_id: ID del pallet
    - product_model: Modelo del producto (opcional)
    - product_reference: Referencia del producto (opcional)
    - date: Fecha (opcional)

    Crea:
    - Registros de Device con pallet_id y carton_id
    - Registros de Pallet con estadísticas
    """
    try:
        # Validar que sea un archivo CSV
        if not file.filename.endswith(('.csv', '.CSV')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El archivo debe ser un CSV (.csv)"
            )

        # Leer el contenido del archivo
        contents = await file.read()

        try:
            # Intentar decodificar como UTF-8
            csv_text = contents.decode('utf-8')
        except UnicodeDecodeError:
            # Si falla, intentar con latin-1
            csv_text = contents.decode('latin-1')

        # Parsear CSV
        csv_file = StringIO(csv_text)
        csv_reader = csv.DictReader(csv_file)

        # Estadísticas de importación
        stats = {
            "total_rows": 0,
            "devices_created": 0,
            "devices_updated": 0,
            "devices_skipped": 0,
            "pallets_created": 0,
            "errors": []
        }

        # Diccionarios para tracking
        pallets_dict: Dict[str, Dict[str, Any]] = {}
        devices_batch = []

        # Procesar cada fila del CSV
        for row_num, row in enumerate(csv_reader, start=2):  # Start=2 because row 1 is header
            stats["total_rows"] += 1

            try:
                # Extraer y validar campos requeridos
                imei = row.get('imei', '').strip()
                iccid = row.get('iccid', row.get('ccid', '')).strip()
                carton_id = row.get('carton_id', row.get('package_no', row.get('batch', ''))).strip()
                pallet_id = row.get('pallet_id', '').strip()
                order_number = row.get('order_number', '').strip()

                # Validaciones básicas
                if not imei or len(imei) != 15 or not imei.isdigit():
                    stats["errors"].append(f"Fila {row_num}: IMEI inválido '{imei}'")
                    stats["devices_skipped"] += 1
                    continue

                if iccid and (len(iccid) < 19 or len(iccid) > 22):
                    stats["errors"].append(f"Fila {row_num}: ICCID inválido '{iccid}'")
                    stats["devices_skipped"] += 1
                    continue

                # Verificar si el dispositivo ya existe
                existing_device = await Device.find_one(Device.imei == imei)

                if existing_device:
                    # Actualizar dispositivo existente
                    existing_device.ccid = iccid if iccid else existing_device.ccid
                    existing_device.package_no = carton_id if carton_id else existing_device.package_no
                    existing_device.pallet_id = pallet_id if pallet_id else existing_device.pallet_id
                    existing_device.nro_orden = order_number if order_number else existing_device.nro_orden
                    existing_device.marca = row.get('product_model', existing_device.marca)
                    existing_device.nro_referencia = row.get('product_reference', existing_device.nro_referencia)
                    existing_device.fecha_actualizacion = datetime.utcnow()

                    await existing_device.save()
                    stats["devices_updated"] += 1

                else:
                    # Crear nuevo dispositivo
                    new_device = Device(
                        imei=imei,
                        ccid=iccid if iccid else None,
                        package_no=carton_id if carton_id else None,
                        pallet_id=pallet_id if pallet_id else None,
                        nro_orden=order_number if order_number else None,
                        marca=row.get('product_model', None),
                        nro_referencia=row.get('product_reference', None),
                        sku=row.get('sku', None),
                        estado="en_produccion",
                        creado_por=current_user.email
                    )

                    await new_device.insert()
                    stats["devices_created"] += 1

                # Trackear pallet para crear registro después
                if pallet_id and order_number:
                    if pallet_id not in pallets_dict:
                        pallets_dict[pallet_id] = {
                            "pallet_id": pallet_id,
                            "order_number": order_number,
                            "cartons": set(),
                            "device_count": 0,
                            "product_model": row.get('product_model'),
                            "product_reference": row.get('product_reference')
                        }

                    if carton_id:
                        pallets_dict[pallet_id]["cartons"].add(carton_id)
                    pallets_dict[pallet_id]["device_count"] += 1

            except Exception as row_error:
                stats["errors"].append(f"Fila {row_num}: {str(row_error)}")
                stats["devices_skipped"] += 1
                logger.error(f"Error procesando fila {row_num}: {row_error}")

        # Crear o actualizar registros de Pallet
        for pallet_id, pallet_data in pallets_dict.items():
            try:
                existing_pallet = await Pallet.find_one(Pallet.pallet_id == pallet_id)

                if existing_pallet:
                    # Actualizar pallet existente
                    existing_pallet.carton_ids = list(pallet_data["cartons"])
                    existing_pallet.carton_count = len(pallet_data["cartons"])
                    existing_pallet.device_count = pallet_data["device_count"]
                    existing_pallet.fecha_modificacion = datetime.utcnow()
                    await existing_pallet.save()

                else:
                    # Crear nuevo pallet
                    new_pallet = Pallet(
                        pallet_id=pallet_id,
                        order_number=pallet_data["order_number"],
                        carton_ids=list(pallet_data["cartons"]),
                        carton_count=len(pallet_data["cartons"]),
                        device_count=pallet_data["device_count"],
                        devices_per_carton=pallet_data["device_count"] // len(pallet_data["cartons"]) if pallet_data["cartons"] else 0,
                        product_model=pallet_data["product_model"],
                        product_reference=pallet_data["product_reference"],
                        estado="preparado",
                        creado_por=current_user.email
                    )

                    await new_pallet.insert()
                    stats["pallets_created"] += 1

            except Exception as pallet_error:
                stats["errors"].append(f"Error creando pallet {pallet_id}: {str(pallet_error)}")
                logger.error(f"Error creando pallet {pallet_id}: {pallet_error}")

        logger.info(f"Importación completada por {current_user.email}: {stats['devices_created']} creados, {stats['devices_updated']} actualizados")

        return {
            "success": True,
            "message": "Importación completada",
            "statistics": stats,
            "pallets_processed": len(pallets_dict)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en importación de picking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando archivo: {str(e)}"
        )


@router.get("/hierarchy/pallets/{pallet_id}")
async def obtener_pallet_jerarquico(
    pallet_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **Obtener pallet con jerarquía completa**

    Retorna el pallet con la lista de cartones y estadísticas
    """
    try:
        pallet = await Pallet.find_one(Pallet.pallet_id == pallet_id)

        if not pallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pallet {pallet_id} no encontrado"
            )

        # Obtener cartones únicos del pallet
        devices = await Device.find(Device.pallet_id == pallet_id).to_list()

        cartons_dict = {}
        for device in devices:
            if device.package_no:  # package_no = carton_id
                if device.package_no not in cartons_dict:
                    cartons_dict[device.package_no] = []
                cartons_dict[device.package_no].append({
                    "imei": device.imei,
                    "ccid": device.ccid,
                    "estado": device.estado.value if hasattr(device.estado, 'value') else device.estado
                })

        cartons_list = [
            {
                "carton_id": carton_id,
                "device_count": len(devices_in_carton),
                "devices": devices_in_carton
            }
            for carton_id, devices_in_carton in cartons_dict.items()
        ]

        return {
            "pallet": pallet,
            "cartons": cartons_list,
            "summary": {
                "pallet_id": pallet.pallet_id,
                "order_number": pallet.order_number,
                "carton_count": len(cartons_list),
                "device_count": len(devices),
                "estado": pallet.estado
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo pallet jerárquico: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener pallet: {str(e)}"
        )


@router.get("/hierarchy/cartons/{carton_id}")
async def obtener_carton_jerarquico(
    carton_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **Obtener cartón con todos sus dispositivos**

    Retorna todos los dispositivos (IMEI + ICCID) dentro del cartón
    """
    try:
        devices = await Device.find(Device.package_no == carton_id).to_list()

        if not devices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cartón {carton_id} no encontrado o sin dispositivos"
            )

        # Obtener pallet_id del primer dispositivo
        pallet_id = devices[0].pallet_id if devices else None

        devices_list = [
            {
                "imei": device.imei,
                "ccid": device.ccid,
                "estado": device.estado.value if hasattr(device.estado, 'value') else device.estado,
                "marca": device.marca,
                "nro_referencia": device.nro_referencia,
                "notificado": device.notificado,
                "cliente_nombre": device.cliente_nombre
            }
            for device in devices
        ]

        return {
            "carton_id": carton_id,
            "pallet_id": pallet_id,
            "device_count": len(devices),
            "devices": devices_list
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo cartón: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener cartón: {str(e)}"
        )


@router.get("/hierarchy/devices/search")
async def buscar_dispositivo_jerarquico(
    imei: Optional[str] = Query(None, description="IMEI del dispositivo"),
    iccid: Optional[str] = Query(None, description="ICCID (CCID) del dispositivo"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **Buscar dispositivo y mostrar su ubicación jerárquica**

    Busca por IMEI o ICCID y retorna el dispositivo con su ubicación:
    PALLET → CARTON → DEVICE
    """
    try:
        if not imei and not iccid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe proporcionar IMEI o ICCID"
            )

        device = None

        if imei:
            device = await Device.find_one(Device.imei == imei.strip())
        elif iccid:
            device = await Device.find_one(Device.ccid == iccid.strip())

        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dispositivo no encontrado"
            )

        # Obtener información del pallet si existe
        pallet = None
        if device.pallet_id:
            pallet = await Pallet.find_one(Pallet.pallet_id == device.pallet_id)

        return {
            "device": {
                "imei": device.imei,
                "ccid": device.ccid,
                "estado": device.estado.value if hasattr(device.estado, 'value') else device.estado,
                "marca": device.marca,
                "nro_referencia": device.nro_referencia,
                "sku": device.sku
            },
            "ubicacion": {
                "pallet_id": device.pallet_id,
                "carton_id": device.package_no,
                "order_number": pallet.order_number if pallet else None,
                "ubicacion_almacen": pallet.ubicacion if pallet else None
            },
            "pallet_info": {
                "pallet_id": pallet.pallet_id if pallet else None,
                "estado": pallet.estado if pallet else None,
                "carton_count": pallet.carton_count if pallet else None,
                "device_count": pallet.device_count if pallet else None
            } if pallet else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error buscando dispositivo: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en búsqueda: {str(e)}"
        )


@router.get("/hierarchy/orders/{order_number}")
async def obtener_orden_jerarquica(
    order_number: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **Obtener orden de producción con todos sus pallets**

    Retorna todos los pallets de una orden con estadísticas
    """
    try:
        pallets = await Pallet.find(Pallet.order_number == order_number).to_list()

        if not pallets:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden {order_number} no encontrada o sin pallets"
            )

        pallets_summary = [
            {
                "pallet_id": pallet.pallet_id,
                "carton_count": pallet.carton_count,
                "device_count": pallet.device_count,
                "estado": pallet.estado,
                "ubicacion": pallet.ubicacion,
                "fecha_creacion": pallet.fecha_creacion
            }
            for pallet in pallets
        ]

        total_cartons = sum(p.carton_count for p in pallets)
        total_devices = sum(p.device_count for p in pallets)

        return {
            "order_number": order_number,
            "pallet_count": len(pallets),
            "total_cartons": total_cartons,
            "total_devices": total_devices,
            "pallets": pallets_summary,
            "product_model": pallets[0].product_model if pallets else None,
            "product_reference": pallets[0].product_reference if pallets else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo orden: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener orden: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# UTILIDADES
# ════════════════════════════════════════════════════════════════════════

@router.get("/stats")
async def obtener_estadisticas(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtener estadísticas generales de picking"""
    try:
        # Estadísticas de palets
        total_palets = await PalletItem.find().count()
        palets_preparados = await PalletItem.find({"estado": "preparado"}).count()
        palets_en_transito = await PalletItem.find({"estado": "en_transito"}).count()
        palets_entregados = await PalletItem.find({"estado": "entregado"}).count()

        # Estadísticas de paquetes
        total_paquetes = await Package.find().count()
        paquetes_preparados = await Package.find({"estado": "preparado"}).count()
        paquetes_enviados = await Package.find({"estado": "enviado"}).count()
        paquetes_entregados = await Package.find({"estado": "entregado"}).count()
        emails_pendientes = await Package.find({"email_enviado": False}).count()

        return {
            "palets": {
                "total": total_palets,
                "preparados": palets_preparados,
                "en_transito": palets_en_transito,
                "entregados": palets_entregados
            },
            "paquetes": {
                "total": total_paquetes,
                "preparados": paquetes_preparados,
                "enviados": paquetes_enviados,
                "entregados": paquetes_entregados,
                "emails_pendientes": emails_pendientes
            }
        }

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )
