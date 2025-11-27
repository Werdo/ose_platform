"""
OSE Platform - App 1: Notificación de Series
Router para notificación de dispositivos a clientes
Incluye exportación por lotes de pallets
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
import logging
import csv
import io
import pandas as pd

from app.schemas.app1 import (
    NotificarSeriesRequest,
    NotificarSeriesResponse,
    BuscarDispositivosRequest,
    DispositivoResponse,
    HistorialDispositivoResponse,
    EstadisticasClienteResponse,
    ClienteSimpleResponse,
    ValidateBulkRequest,
    ValidateBulkResponse,
    SendNotificationRequest,
    SendNotificationResponse
)
from app.models.device import Device, EstadoDispositivo
from app.models.device_event import DeviceEvent
from app.models.movimiento import Movimiento, TipoMovimiento
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.series_notification import SeriesNotification
from app.dependencies.auth import get_current_active_user
from app.services.mail_service import mail_service
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/series-notifications", tags=["App 1: Notificación de Series"])


@router.post("/notificar", response_model=NotificarSeriesResponse)
async def notificar_series(
    request: NotificarSeriesRequest,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    **App 1 - Endpoint Principal: Notificar Series a Cliente**

    Notifica dispositivos (por IMEI) a un cliente específico.
    Marca los dispositivos como notificados, crea eventos y movimientos.
    Opcionalmente envía email de notificación.

    - **cliente_id**: ID del cliente (ObjectId)
    - **series**: Lista de IMEIs a notificar
    - **ubicacion**: Ubicación de los dispositivos (opcional)
    - **enviar_email**: Si enviar email de notificación (default: True)
    - **operador**: ID del operador (opcional, si no se usa el usuario actual)

    Requiere autenticación.
    """
    # Buscar cliente
    cliente = await Customer.get(request.cliente_id)

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente no encontrado: {request.cliente_id}"
        )

    if not cliente.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El cliente no está activo"
        )

    notificados = 0
    errores = []
    detalles = []

    operador_id = request.operador or current_user.employee_id

    # Procesar cada IMEI
    for imei in request.series:
        try:
            # Buscar dispositivo por IMEI
            device = await Device.buscar_por_imei(imei)

            if not device:
                errores.append(f"Dispositivo no encontrado: {imei}")
                detalles.append({
                    "imei": imei,
                    "status": "error",
                    "error": "No encontrado"
                })
                continue

            # Verificar que no esté ya notificado
            if device.notificado:
                errores.append(f"Dispositivo ya notificado: {imei}")
                detalles.append({
                    "imei": imei,
                    "status": "error",
                    "error": "Ya notificado",
                    "device_id": str(device.id)
                })
                continue

            # Marcar como notificado
            await device.marcar_como_notificado(
                cliente_id=request.cliente_id,
                cliente_nombre=cliente.full_name,
                cliente_codigo=cliente.customer_code,
                ubicacion=request.ubicacion,
                operador=operador_id
            )

            # Crear movimiento logístico (CRÍTICO según documentación)
            movimiento = Movimiento(
                tipo=TipoMovimiento.ENVIO,
                fecha=datetime.utcnow(),
                producto=str(device.id),
                imei=device.imei,
                ccid=device.ccid,
                cantidad=1,
                cliente=request.cliente_id,
                cliente_nombre=cliente.full_name,
                cliente_codigo=cliente.customer_code,
                ubicacion_destino=request.ubicacion,
                usuario=operador_id,
                usuario_nombre=current_user.full_name,
                origen="app1",
                detalles=f"Notificación de serie a {cliente.full_name}",
                documento_referencia=None
            )
            await movimiento.insert()

            # Incrementar contador de dispositivos del cliente
            await cliente.increment_devices_count(1)

            notificados += 1
            detalles.append({
                "imei": imei,
                "status": "notificado",
                "device_id": str(device.id)
            })

            logger.info(f"Dispositivo {imei} notificado a cliente {cliente.customer_code}")

        except Exception as e:
            logger.error(f"Error notificando dispositivo {imei}: {e}")
            errores.append(f"Error en {imei}: {str(e)}")
            detalles.append({
                "imei": imei,
                "status": "error",
                "error": str(e)
            })

    # Enviar email si se solicitó y si se notificó al menos un dispositivo
    email_enviado = False
    if request.enviar_email and notificados > 0 and cliente.email:
        try:
            series_list = [d["imei"] for d in detalles if d["status"] == "notificado"]

            email_enviado = await mail_service.send_notification_email(
                to=cliente.email,
                customer_name=cliente.full_name,
                series_count=notificados,
                series_list=series_list,
                ubicacion=request.ubicacion
            )

            if email_enviado:
                logger.info(f"Email de notificación enviado a {cliente.email}")
            else:
                errores.append("No se pudo enviar el email de notificación")

        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            errores.append(f"Error enviando email: {str(e)}")

    return NotificarSeriesResponse(
        success=notificados > 0,
        notificados=notificados,
        errores=errores,
        detalles=detalles,
        email_enviado=email_enviado
    )


@router.get("/dispositivos", response_model=List[DispositivoResponse])
async def buscar_dispositivos(
    cliente_id: Optional[str] = Query(None, description="Filtrar por cliente"),
    nro_orden: Optional[str] = Query(None, description="Filtrar por orden"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    notificado: Optional[bool] = Query(None, description="Filtrar por notificado"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Buscar dispositivos disponibles para notificar

    Permite filtrar por cliente, orden, estado, etc.

    Requiere autenticación.
    """
    # Construir query
    filters = {}

    if cliente_id:
        filters["cliente"] = cliente_id

    if nro_orden:
        filters["nro_orden"] = nro_orden

    if estado:
        filters["estado"] = estado

    if notificado is not None:
        filters["notificado"] = notificado

    # Buscar dispositivos
    query = Device.find(filters)

    devices = await query.skip(skip).limit(limit).to_list()

    # Convertir a response
    return [
        DispositivoResponse(
            id=str(device.id),
            imei=device.imei,
            ccid=device.ccid,
            marca=device.marca,
            nro_referencia=device.nro_referencia,
            estado=device.estado.value,
            notificado=device.notificado,
            cliente=device.cliente,
            cliente_nombre=device.cliente_nombre,
            nro_orden=device.nro_orden,
            lote=device.lote,
            fecha_creacion=device.fecha_creacion
        )
        for device in devices
    ]


@router.get("/dispositivos/{imei}", response_model=DispositivoResponse)
async def obtener_dispositivo(
    imei: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Obtener información de un dispositivo por IMEI

    Requiere autenticación.
    """
    device = await Device.buscar_por_imei(imei)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo no encontrado: {imei}"
        )

    return DispositivoResponse(
        id=str(device.id),
        imei=device.imei,
        ccid=device.ccid,
        marca=device.marca,
        nro_referencia=device.nro_referencia,
        estado=device.estado.value,
        notificado=device.notificado,
        cliente=device.cliente,
        cliente_nombre=device.cliente_nombre,
        nro_orden=device.nro_orden,
        lote=device.lote,
        fecha_creacion=device.fecha_creacion
    )


@router.get("/dispositivos/{imei}/historial", response_model=HistorialDispositivoResponse)
async def obtener_historial_dispositivo(
    imei: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Obtener historial completo de un dispositivo (eventos + movimientos)

    Requiere autenticación.
    """
    device = await Device.buscar_por_imei(imei)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dispositivo no encontrado: {imei}"
        )

    # Obtener eventos
    eventos = await DeviceEvent.obtener_historial_por_imei(imei)

    # Obtener movimientos
    movimientos = await Movimiento.get_by_imei(imei)

    return HistorialDispositivoResponse(
        device_id=str(device.id),
        imei=device.imei,
        eventos=[
            {
                "event_type": e.event_type,
                "timestamp": e.timestamp,
                "descripcion": e.descripcion,
                "operator": e.operator,
                "cliente": e.cliente,
                "data": e.data
            }
            for e in eventos
        ],
        movimientos=[
            {
                "tipo": m.tipo.value,
                "fecha": m.fecha,
                "cliente_nombre": m.cliente_nombre,
                "ubicacion_destino": m.ubicacion_destino,
                "usuario_nombre": m.usuario_nombre,
                "detalles": m.detalles
            }
            for m in movimientos
        ]
    )


@router.get("/clientes", response_model=List[ClienteSimpleResponse])
async def listar_clientes(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Listar clientes disponibles para notificación

    Requiere autenticación.
    """
    filters = {}

    if status_filter:
        filters["status"] = status_filter

    customers = await Customer.find(filters).limit(limit).to_list()

    return [
        ClienteSimpleResponse(
            id=str(c.id),
            customer_code=c.customer_code,
            full_name=c.full_name,
            email=c.email,
            status=c.status.value,
            devices_count=c.devices_count
        )
        for c in customers
    ]


@router.get("/clientes/{cliente_id}/estadisticas", response_model=EstadisticasClienteResponse)
async def obtener_estadisticas_cliente(
    cliente_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Obtener estadísticas de un cliente

    Requiere autenticación.
    """
    cliente = await Customer.get(cliente_id)

    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cliente no encontrado: {cliente_id}"
        )

    # Contar dispositivos notificados
    dispositivos_notificados = await Device.find(
        Device.cliente == cliente_id,
        Device.notificado == True
    ).count()

    # Buscar última notificación
    ultima_notificacion = None
    ultimo_dispositivo = await Device.find(
        Device.cliente == cliente_id,
        Device.notificado == True
    ).sort("-fecha_notificacion").limit(1).to_list()

    if ultimo_dispositivo:
        ultima_notificacion = ultimo_dispositivo[0].fecha_notificacion

    return EstadisticasClienteResponse(
        cliente_id=str(cliente.id),
        cliente_nombre=cliente.full_name,
        total_dispositivos=cliente.devices_count,
        dispositivos_activos=cliente.active_devices_count,
        dispositivos_notificados=dispositivos_notificados,
        ultima_notificacion=ultima_notificacion
    )


@router.get("/config/options")
async def get_config_options(
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Obtener opciones de configuración para el formulario de notificación

    Retorna lista de clientes activos y otras opciones necesarias.

    Requiere autenticación.
    """
    # Obtener clientes activos
    customers = await Customer.find_many(
        Customer.is_active == True
    ).limit(1000).to_list()

    customers_list = [
        {
            "id": str(c.id),
            "customer_code": c.customer_code,
            "full_name": c.full_name,
            "email": c.email,
            "status": c.status.value,
            "devices_count": c.devices_count
        }
        for c in customers
    ]

    return {
        "success": True,
        "customers": customers_list,
        "total_customers": len(customers_list)
    }


@router.post("/validate-bulk", response_model=ValidateBulkResponse)
async def validate_bulk_series(
    request: ValidateBulkRequest,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Validar múltiples IMEIs antes de notificar

    Verifica que cada IMEI existe en el sistema y si está disponible para notificar.

    Retorna:
    - valido: Si el IMEI tiene formato correcto
    - existe: Si el dispositivo existe en el sistema
    - notificado: Si ya fue notificado a un cliente
    - message: Mensaje descriptivo del estado

    Requiere autenticación.
    """
    resultados = []
    validos = 0
    invalidos = 0

    for imei in request.series:
        # Limpiar IMEI
        imei_clean = imei.strip()

        # Validar formato
        if not imei_clean or len(imei_clean) != 15 or not imei_clean.isdigit():
            resultados.append({
                "imei": imei,
                "valido": False,
                "existe": False,
                "notificado": False,
                "message": "IMEI inválido: debe tener 15 dígitos numéricos"
            })
            invalidos += 1
            continue

        # Buscar dispositivo
        try:
            device = await Device.buscar_por_imei(imei_clean)

            if not device:
                resultados.append({
                    "imei": imei_clean,
                    "valido": True,
                    "existe": False,
                    "notificado": False,
                    "message": "No encontrado en el sistema"
                })
                invalidos += 1
                continue

            # Dispositivo existe, verificar si ya está notificado
            if device.notificado:
                resultados.append({
                    "imei": imei_clean,
                    "valido": True,
                    "existe": True,
                    "notificado": True,
                    "device_id": str(device.id),
                    "marca": device.marca,
                    "nro_referencia": device.nro_referencia,
                    "estado": device.estado.value,
                    "cliente": device.cliente,
                    "cliente_nombre": device.cliente_nombre,
                    "message": f"⚠️ Ya notificado a: {device.cliente_nombre or 'cliente desconocido'} (se puede reenviar)"
                })
                validos += 1  # Cambiado: permitir reenvío
            else:
                resultados.append({
                    "imei": imei_clean,
                    "valido": True,
                    "existe": True,
                    "notificado": False,
                    "device_id": str(device.id),
                    "marca": device.marca,
                    "nro_referencia": device.nro_referencia,
                    "estado": device.estado.value,
                    "message": "✓ Disponible para notificar"
                })
                validos += 1

        except Exception as e:
            logger.error(f"Error validando IMEI {imei_clean}: {e}")
            resultados.append({
                "imei": imei_clean,
                "valido": False,
                "existe": False,
                "notificado": False,
                "message": f"Error al validar: {str(e)}"
            })
            invalidos += 1

    return ValidateBulkResponse(
        success=True,
        total=len(request.series),
        validos=validos,
        invalidos=invalidos,
        resultados=resultados
    )

@router.post("/send", response_model=SendNotificationResponse)
async def send_notification(
    request: SendNotificationRequest,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Enviar notificación completa con generación de CSV y email

    Este endpoint maneja el flujo completo:
    1. Genera el CSV en el formato solicitado
    2. Notifica los dispositivos en el sistema (si hay cliente)
    3. Envía el email con el CSV adjunto

    Requiere autenticación.
    """
    from datetime import datetime

    # Generar nombre de archivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"series_{timestamp}.csv"

    # Generar contenido CSV según formato
    csv_content = ""

    if request.csv_format == "separated":
        # Estándar - Dos columnas
        csv_content = "IMEI,ICCID\n"
        for serial in request.serials:
            csv_content += f"{serial.imei},{serial.iccid or ''}\n"

    elif request.csv_format == "unified":
        # Simplificado - Una columna
        csv_content = "Número de Serie\n"
        for serial in request.serials:
            combined = f"{serial.imei}"
            if serial.iccid:
                combined += f" {serial.iccid}"
            csv_content += f"{combined}\n"

    elif request.csv_format == "detailed":
        # Detallado - Múltiples columnas
        csv_content = "IMEI,ICCID,Paquete,Marca,Referencia\n"
        for serial in request.serials:
            csv_content += f"{serial.imei},{serial.iccid or ''},{serial.package_no or ''},N/A,N/A\n"

    elif request.csv_format == "compact":
        # Compacto - Solo IMEIs
        csv_content = "IMEI\n"
        for serial in request.serials:
            csv_content += f"{serial.imei}\n"

    elif request.csv_format == "logistica-trazable":
        # Logística Trazable - IMEI, ICCID, Marca, Operador, Caja Master, Pallet
        csv_content = "IMEI,ICCID,Marca,Operador,Caja Master,Pallet\n"
        for serial in request.serials:
            # Fetch additional data from device if needed
            marca = getattr(serial, 'marca', '') or ''
            operador = getattr(serial, 'operador', '') or ''
            caja_master = getattr(serial, 'caja_master', '') or ''
            pallet_id = getattr(serial, 'pallet_id', '') or ''
            csv_content += f"{serial.imei},{serial.iccid or ''},{marca},{operador},{caja_master},{pallet_id}\n"

    elif request.csv_format == "imei-marca":
        # IMEI-Marca - IMEI, Marca
        csv_content = "IMEI,Marca\n"
        for serial in request.serials:
            marca = getattr(serial, 'marca', '') or ''
            csv_content += f"{serial.imei},{marca}\n"

    elif request.csv_format == "inspide":
        # Inspide - IMEI, ICCID (similar a separated pero con nombre específico)
        csv_content = "IMEI,ICCID\n"
        for serial in request.serials:
            csv_content += f"{serial.imei},{serial.iccid or ''}\n"

    elif request.csv_format == "clientes-genericos":
        # Clientes Genéricos - IMEI, Marca, Número de Orden
        csv_content = "IMEI,Marca,Número de Orden\n"
        for serial in request.serials:
            marca = getattr(serial, 'marca', '') or ''
            order_number = getattr(serial, 'order_number', '') or getattr(serial, 'nro_referencia', '') or ''
            csv_content += f"{serial.imei},{marca},{order_number}\n"

    else:
        # Formato por defecto
        csv_content = "IMEI,ICCID\n"
        for serial in request.serials:
            csv_content += f"{serial.imei},{serial.iccid or ''}\n"

    # Notificar dispositivos si hay customer_id
    notificados = 0
    failed_serials = []
    errors = []

    if request.customer_id:
        try:
            # Buscar cliente
            cliente = await Customer.get(request.customer_id)

            if cliente and cliente.is_active:
                # Procesar cada IMEI
                for serial in request.serials:
                    try:
                        device = await Device.buscar_por_imei(serial.imei)

                        if device:
                            # Permitir reenvío incluso si ya estaba notificado
                            was_notified = device.notificado

                            await device.marcar_como_notificado(
                                cliente_id=request.customer_id,
                                cliente_nombre=request.customer_name or cliente.full_name,
                                cliente_codigo=cliente.customer_code,
                                ubicacion=request.location,
                                operador=current_user.employee_id
                            )

                            # Crear movimiento
                            detalles = f"Notificación de serie - LOTE: {request.location}"
                            if was_notified:
                                detalles += " (REENVÍO)"

                            movimiento = Movimiento(
                                tipo=TipoMovimiento.ENVIO,
                                fecha=datetime.utcnow(),
                                producto=str(device.id),
                                imei=device.imei,
                                ccid=device.ccid,
                                cantidad=1,
                                cliente=request.customer_id,
                                cliente_nombre=request.customer_name or cliente.full_name,
                                cliente_codigo=cliente.customer_code,
                                ubicacion_destino=request.location,
                                usuario=current_user.employee_id,
                                usuario_nombre=current_user.full_name,
                                origen="app1_send",
                                detalles=detalles,
                                documento_referencia=None
                            )
                            await movimiento.insert()

                            notificados += 1
                        else:
                            failed_serials.append(serial.imei)
                            errors.append(f"{serial.imei}: No encontrado en el sistema")

                    except Exception as e:
                        failed_serials.append(serial.imei)
                        errors.append(f"{serial.imei}: {str(e)}")
                        logger.error(f"Error notificando {serial.imei}: {e}")

        except Exception as e:
            errors.append(f"Error con cliente: {str(e)}")
            logger.error(f"Error procesando cliente: {e}")

    # Enviar email con CSV adjunto
    email_sent = False
    try:
        # Preparar destinatarios
        to_list = [request.email_to]
        cc_list = request.email_cc if request.email_cc else None

        # Preparar adjunto CSV
        csv_bytes = csv_content.encode('utf-8')
        attachments = [{
            "filename": csv_filename,
            "content": csv_bytes,
            "content_type": "text/csv"
        }]

        # Preparar cuerpo del email
        customer_name = request.customer_name or "Destinatario"
        subject = f"Notificación de Series - LOTE: {request.location}"

        body_text = f"""
Estimado/a {customer_name},

Por la presente le notificamos el envío de {len(request.serials)} dispositivo(s).

Detalles del envío:
- Número de LOTE/Albarán: {request.location}
- Cantidad de dispositivos: {len(request.serials)}
- Formato de archivo: {request.csv_format}

Adjunto encontrará un archivo CSV con los números de serie (IMEI/ICCID) de los dispositivos.

"""

        if request.notes:
            body_text += f"\nNotas adicionales:\n{request.notes}\n"

        body_text += f"""
Atentamente,
{settings.COMPANY_NAME}
{settings.COMPANY_EMAIL}

---
Este es un email automático generado por {settings.APP_NAME}
"""

        # Cuerpo HTML
        body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #2c3e50;">Notificación de Series de Dispositivos</h2>

    <p>Estimado/a <strong>{customer_name}</strong>,</p>

    <p>Por la presente le notificamos el envío de <strong>{len(request.serials)} dispositivo(s)</strong>.</p>

    <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0;">
        <h3 style="margin-top: 0;">Detalles del envío:</h3>
        <ul style="list-style: none; padding-left: 0;">
            <li>📦 <strong>Número de LOTE/Albarán:</strong> {request.location}</li>
            <li>📱 <strong>Cantidad de dispositivos:</strong> {len(request.serials)}</li>
            <li>📄 <strong>Formato de archivo:</strong> {request.csv_format}</li>
            <li>{"📊 <strong>Notificados:</strong> " + str(notificados) if request.customer_id else ""}</li>
        </ul>
    </div>

    <p>Adjunto encontrará un archivo CSV con los números de serie (IMEI/ICCID) de los dispositivos.</p>

    {"<div style='background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 15px 0;'><strong>Notas adicionales:</strong><br>" + request.notes + "</div>" if request.notes else ""}

    <hr style="border: none; border-top: 1px solid #dee2e6; margin: 30px 0;">

    <p style="font-size: 0.9em;">
        Atentamente,<br>
        <strong>{settings.COMPANY_NAME}</strong><br>
        {settings.COMPANY_EMAIL}
    </p>

    <p style="font-size: 0.8em; color: #6c757d;">
        <em>Este es un email automático generado por {settings.APP_NAME}</em>
    </p>
</body>
</html>
"""

        # Enviar email
        email_sent = await mail_service.send_email(
            to=to_list,
            subject=subject,
            body=body_text,
            html=body_html,
            cc=cc_list,
            attachments=attachments
        )

        if email_sent:
            logger.info(f"Email enviado exitosamente a {request.email_to} con {len(request.serials)} dispositivos")
        else:
            errors.append("El sistema de email está deshabilitado o hubo un error al enviar")
            logger.warning(f"Email no enviado (SMTP deshabilitado o error)")

    except Exception as e:
        errors.append(f"Error enviando email: {str(e)}")
        logger.error(f"Error enviando email: {e}", exc_info=True)

    # ════════════════════════════════════════════════════════════════════
    # GUARDAR HISTORIAL EN BASE DE DATOS
    # ════════════════════════════════════════════════════════════════════
    try:
        # Preparar datos de dispositivos para el historial
        serials_data = []
        for serial in request.serials:
            serials_data.append({
                "imei": serial.imei,
                "iccid": serial.iccid or "",
                "package_no": serial.package_no or ""
            })

        # Obtener código de cliente si existe
        customer_code = None
        if request.customer_id:
            try:
                cliente = await Customer.get(request.customer_id)
                if cliente:
                    customer_code = cliente.customer_code
            except:
                pass

        # Crear registro de historial
        notification_history = SeriesNotification(
            fecha=datetime.utcnow(),
            customer_id=request.customer_id,
            customer_name=request.customer_name,
            customer_code=customer_code,
            location=request.location,
            serials=serials_data,
            device_count=len(request.serials),
            notified_count=notificados,
            failed_serials=failed_serials,
            csv_format=request.csv_format,
            csv_filename=csv_filename,
            csv_content=None,  # No guardamos el contenido completo para ahorrar espacio
            email_to=request.email_to,
            email_cc=request.email_cc,
            email_sent=email_sent,
            operator_id=current_user.employee_id,
            operator_name=current_user.full_name,
            operator_email=current_user.email,
            notes=request.notes,
            errors=errors if errors else None
        )

        await notification_history.insert()
        logger.info(f"Historial de notificación guardado: {notification_history.id}")

    except Exception as e:
        logger.error(f"Error guardando historial de notificación: {e}", exc_info=True)
        # No propagamos el error, el envío fue exitoso aunque no se guardó el historial

    return SendNotificationResponse(
        success=True,
        notified_count=notificados if request.customer_id else len(request.serials),
        csv_content=csv_content,
        csv_filename=csv_filename,
        email_sent=email_sent,
        failed_serials=failed_serials,
        errors=errors if errors else None
    )


@router.get("/history")
async def get_history(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search_email: Optional[str] = Query(None, description="Buscar por email"),
    search_customer: Optional[str] = Query(None, description="Buscar por nombre de cliente"),
    search_location: Optional[str] = Query(None, description="Buscar por ubicación/lote"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Obtener historial de notificaciones desde la base de datos

    Soporta búsqueda por:
    - Email (destinatario)
    - Nombre de cliente
    - Ubicación/Lote
    """
    try:
        # Calcular skip
        skip = (page - 1) * limit

        # Construir filtros de búsqueda
        filters = {}

        if search_email:
            # Búsqueda case-insensitive en email
            filters["email_to"] = {"$regex": search_email, "$options": "i"}

        if search_customer:
            # Búsqueda case-insensitive en nombre de cliente
            filters["customer_name"] = {"$regex": search_customer, "$options": "i"}

        if search_location:
            # Búsqueda case-insensitive en ubicación/lote
            filters["location"] = {"$regex": search_location, "$options": "i"}

        # Obtener total de registros con filtros
        total = await SeriesNotification.find(filters).count()

        # Obtener registros paginados, ordenados por fecha descendente
        notifications = await SeriesNotification.find(filters).sort([("fecha", -1)]).skip(skip).limit(limit).to_list()

        # Transformar a formato del frontend
        items = []
        for notif in notifications:
            items.append({
                "id": str(notif.id),
                "date": notif.fecha.isoformat(),
                "customer_name": notif.customer_name or "N/A",
                "customer_id": notif.customer_id,
                "device_count": notif.device_count,
                "csv_format": notif.csv_format,
                "email_to": notif.email_to,
                "operator": notif.operator_name,
                "operator_email": notif.operator_email,
                "csv_filename": notif.csv_filename,
                "notes": notif.notes,
                "serials": notif.serials,
                "location": notif.location
            })

        # Calcular páginas
        import math
        pages = math.ceil(total / limit) if limit > 0 else 0

        return {
            "items": items,
            "total": total,
            "pages": pages
        }

    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}", exc_info=True)
        return {
            "items": [],
            "total": 0,
            "pages": 0
        }


# ════════════════════════════════════════════════════════════════════
# ENDPOINTS DE BÚSQUEDA JERÁRQUICA (LOTE/CARTÓN/PALET)
# ════════════════════════════════════════════════════════════════════

@router.get("/search/by-location/{location}")
async def search_by_location(
    location: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Buscar dispositivos por número de LOTE o Albarán

    Retorna todos los dispositivos asociados a ese lote con formato
    de serie (IMEI/ICCID) para agregar a notificación.

    Requiere autenticación.
    """
    try:
        # Buscar dispositivos por location/lote
        devices = await Device.find(
            Device.lote == location
        ).to_list()

        if not devices:
            return {
                "success": False,
                "message": f"No se encontraron dispositivos para el lote: {location}",
                "count": 0,
                "serials": []
            }

        # Formatear como serials
        serials = []
        for device in devices:
            serials.append({
                "imei": device.imei,
                "iccid": device.ccid or "",
                "package_no": device.package_no or "",
                "pallet_id": device.pallet_id or "",
                "notificado": device.notificado,
                "cliente_nombre": device.cliente_nombre if device.notificado else None
            })

        return {
            "success": True,
            "type": "lote",
            "identifier": location,
            "count": len(serials),
            "serials": serials,
            "message": f"Se encontraron {len(serials)} dispositivo(s) en el lote {location}"
        }

    except Exception as e:
        logger.error(f"Error buscando por lote {location}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error buscando dispositivos: {str(e)}"
        )


@router.get("/search/by-carton/{carton_id}")
async def search_by_carton(
    carton_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Buscar dispositivos por número de CARTÓN (package_no)

    Retorna todos los dispositivos dentro de ese cartón con formato
    de serie (IMEI/ICCID) para agregar a notificación.

    Requiere autenticación.
    """
    try:
        # Buscar dispositivos por package_no (carton_id)
        devices = await Device.find(
            Device.package_no == carton_id
        ).to_list()

        if not devices:
            return {
                "success": False,
                "message": f"No se encontraron dispositivos para el cartón: {carton_id}",
                "count": 0,
                "serials": []
            }

        # Formatear como serials
        serials = []
        pallet_id = None
        lote = None

        for device in devices:
            if not pallet_id and device.pallet_id:
                pallet_id = device.pallet_id
            if not lote and device.lote:
                lote = device.lote

            serials.append({
                "imei": device.imei,
                "iccid": device.ccid or "",
                "package_no": device.package_no or "",
                "pallet_id": device.pallet_id or "",
                "notificado": device.notificado,
                "cliente_nombre": device.cliente_nombre if device.notificado else None
            })

        return {
            "success": True,
            "type": "carton",
            "identifier": carton_id,
            "pallet_id": pallet_id,
            "lote": lote,
            "count": len(serials),
            "serials": serials,
            "message": f"Se encontraron {len(serials)} dispositivo(s) en el cartón {carton_id}"
        }

    except Exception as e:
        logger.error(f"Error buscando por cartón {carton_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error buscando dispositivos: {str(e)}"
        )


@router.get("/search/by-pallet/{pallet_id}")
async def search_by_pallet(
    pallet_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Buscar dispositivos por ID de PALLET

    Retorna todos los dispositivos dentro de ese palet (en todos sus cartones)
    con formato de serie (IMEI/ICCID) para agregar a notificación.

    Requiere autenticación.
    """
    try:
        # Buscar dispositivos por pallet_id
        devices = await Device.find(
            Device.pallet_id == pallet_id
        ).to_list()

        if not devices:
            return {
                "success": False,
                "message": f"No se encontraron dispositivos para el palet: {pallet_id}",
                "count": 0,
                "serials": []
            }

        # Formatear como serials y contar cartones únicos
        serials = []
        cartons = set()
        lote = None

        for device in devices:
            if device.package_no:
                cartons.add(device.package_no)
            if not lote and device.lote:
                lote = device.lote

            serials.append({
                "imei": device.imei,
                "iccid": device.ccid or "",
                "package_no": device.package_no or "",
                "pallet_id": device.pallet_id or "",
                "notificado": device.notificado,
                "cliente_nombre": device.cliente_nombre if device.notificado else None
            })

        return {
            "success": True,
            "type": "pallet",
            "identifier": pallet_id,
            "lote": lote,
            "carton_count": len(cartons),
            "count": len(serials),
            "serials": serials,
            "message": f"Se encontraron {len(serials)} dispositivo(s) en {len(cartons)} cartón(es) del palet {pallet_id}"
        }

    except Exception as e:
        logger.error(f"Error buscando por palet {pallet_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error buscando dispositivos: {str(e)}"
        )


@router.post("/search/smart-scan")
async def smart_scan_code(
    code: str = Query(..., description="Código escaneado (QR/Barcode)"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Búsqueda inteligente por código escaneado

    Detecta automáticamente si el código es:
    - LOTE/Location
    - Cartón (package_no) - típicamente 25 dígitos empezando con 99
    - Pallet ID - típicamente empieza con T
    - IMEI - 15 dígitos
    - ICCID - 19-22 caracteres

    Retorna los dispositivos encontrados según el tipo detectado.

    Requiere autenticación.
    """
    try:
        code = code.strip()

        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El código no puede estar vacío"
            )

        # Detectar tipo de código
        code_type = None
        results = None

        # 1. Verificar si es un IMEI (15 dígitos)
        if len(code) == 15 and code.isdigit():
            code_type = "imei"
            device = await Device.buscar_por_imei(code)
            if device:
                results = {
                    "success": True,
                    "type": "imei",
                    "identifier": code,
                    "count": 1,
                    "serials": [{
                        "imei": device.imei,
                        "iccid": device.ccid or "",
                        "package_no": device.package_no or "",
                        "pallet_id": device.pallet_id or "",
                        "notificado": device.notificado,
                        "cliente_nombre": device.cliente_nombre if device.notificado else None
                    }],
                    "message": f"Dispositivo encontrado por IMEI"
                }

        # 2. Verificar si es un ICCID (19-22 caracteres)
        elif len(code) >= 19 and len(code) <= 22:
            code_type = "iccid"
            device = await Device.find_one(Device.ccid == code)
            if device:
                results = {
                    "success": True,
                    "type": "iccid",
                    "identifier": code,
                    "count": 1,
                    "serials": [{
                        "imei": device.imei,
                        "iccid": device.ccid or "",
                        "package_no": device.package_no or "",
                        "pallet_id": device.pallet_id or "",
                        "notificado": device.notificado,
                        "cliente_nombre": device.cliente_nombre if device.notificado else None
                    }],
                    "message": f"Dispositivo encontrado por ICCID"
                }

        # 3. Verificar si es un package_no/cartón (típicamente 25 dígitos empezando con 99)
        elif len(code) == 25 and code.startswith("99"):
            code_type = "carton"
            return await search_by_carton(code, current_user)

        # 4. Verificar si es un pallet_id (empieza con T)
        elif code.startswith("T") and len(code) > 10:
            code_type = "pallet"
            return await search_by_pallet(code, current_user)

        # 5. Si no coincide con patrones conocidos, buscar como lote
        else:
            code_type = "lote"
            return await search_by_location(code, current_user)

        # Si llegamos aquí y no encontramos resultados, intentar buscar en todos los tipos
        if not results:
            # Intentar como lote
            lote_devices = await Device.find(Device.lote == code).limit(1).to_list()
            if lote_devices:
                return await search_by_location(code, current_user)

            # Intentar como cartón
            carton_devices = await Device.find(Device.package_no == code).limit(1).to_list()
            if carton_devices:
                return await search_by_carton(code, current_user)

            # Intentar como pallet
            pallet_devices = await Device.find(Device.pallet_id == code).limit(1).to_list()
            if pallet_devices:
                return await search_by_pallet(code, current_user)

            return {
                "success": False,
                "type": "unknown",
                "identifier": code,
                "count": 0,
                "serials": [],
                "message": f"No se encontraron dispositivos para el código: {code}"
            }

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en smart scan para código {code}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando código: {str(e)}"
        )


@router.post("/export-by-pallets")
async def export_devices_by_pallets(
    file: UploadFile = File(..., description="Archivo con lista de pallets (txt, csv, o xlsx)"),
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Exportar CSV con dispositivos de múltiples pallets

    Acepta un archivo con lista de códigos de pallet y genera un CSV con:
    - IMEI
    - ICCID
    - MARCA
    - OPERADOR
    - NUMERO_PALET

    El archivo de entrada puede ser:
    - TXT: un pallet por línea
    - CSV: primera columna con pallets
    - XLSX: primera columna con pallets
    """
    try:
        logger.info(f"Usuario {current_user.username} exportando dispositivos por lote de pallets")

        # Leer archivo
        content = await file.read()
        pallet_codes = []

        # Detectar tipo de archivo y extraer pallets
        filename = file.filename.lower()

        if filename.endswith('.txt'):
            # Archivo TXT: un pallet por línea
            lines = content.decode('utf-8').split('\n')
            pallet_codes = [line.strip() for line in lines if line.strip()]

        elif filename.endswith('.csv'):
            # Archivo CSV: primera columna
            lines = content.decode('utf-8').split('\n')
            for line in lines:
                if line.strip():
                    parts = line.split(',')
                    if parts[0].strip():
                        pallet_codes.append(parts[0].strip())

        elif filename.endswith(('.xlsx', '.xls')):
            # Archivo Excel: primera columna
            df = pd.read_excel(io.BytesIO(content))
            pallet_codes = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Formato de archivo no soportado. Use .txt, .csv o .xlsx"
            )

        if not pallet_codes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se encontraron códigos de pallet en el archivo"
            )

        logger.info(f"Se leyeron {len(pallet_codes)} códigos de pallet del archivo")

        # Buscar dispositivos con esos pallets
        devices = await Device.find(
            {"pallet_id": {"$in": pallet_codes}}
        ).to_list()

        if not devices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontraron dispositivos para los {len(pallet_codes)} pallets proporcionados"
            )

        logger.info(f"Se encontraron {len(devices)} dispositivos")

        # Crear CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)

        # Escribir encabezados
        writer.writerow(['IMEI', 'ICCID', 'MARCA', 'OPERADOR', 'NUMERO_PALET'])

        # Escribir datos
        for device in devices:
            writer.writerow([
                device.imei or '',
                device.ccid or '',
                device.marca or '',
                device.operador or '',
                device.pallet_id or ''
            ])

        # Preparar respuesta
        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=dispositivos_pallets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exportando dispositivos por pallets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando CSV: {str(e)}"
        )


# End of router endpoints
