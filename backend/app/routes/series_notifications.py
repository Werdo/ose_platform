"""
OSE Platform - Series Notification Routes
API endpoints para App 1: Notificación de Números de Serie
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from datetime import datetime
import re
import io

from app.models import (
    Device,
    Customer,
    CustomerStatus,
    SeriesNotification,
    DeviceEvent,
    Employee
)
from app.schemas.series_notification import (
    ParseInputRequest,
    ParseResult,
    DeviceSerialOutput,
    ValidateSerialRequest,
    ValidateBulkRequest,
    ValidationResult,
    BulkValidationResult,
    SendNotificationRequest,
    NotificationResponse,
    CustomerOutput,
    NotificationHistoryResponse,
    NotificationHistoryItem,
    NotificationDetailsResponse,
    OptionsResponse,
    CSVFormatEnum
)
from app.dependencies.auth import get_current_user
from app.services.email_service import email_service

router = APIRouter(prefix="/api/v1/series-notifications", tags=["Series Notifications"])


# ════════════════════════════════════════════════════════════════════════
# PARSEO Y VALIDACIÓN
# ════════════════════════════════════════════════════════════════════════

@router.post("/parse", response_model=ParseResult)
async def parse_input(
    request: ParseInputRequest,
    current_user: Employee = Depends(get_current_user)
):
    """
    Parsea texto de entrada para extraer IMEI/ICCID/Package numbers

    Formatos soportados:
    - IMEI solo (15 dígitos)
    - ICCID solo (19-20 dígitos)
    - IMEI ICCID (separados por espacio)
    - Package number (25 dígitos comenzando con 99)
    """
    lines = request.input_text.strip().split('\n')
    valid = []
    invalid = []

    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            continue

        # Verificar si es un package number (25 dígitos empezando con 99)
        if re.match(r'^99\d{23}$', trimmed):
            valid.append(DeviceSerialOutput(
                imei="",
                iccid=None,
                package_no=trimmed
            ))
            continue

        # Dividir por espacios o tabs
        parts = re.split(r'\s+', trimmed)

        if len(parts) == 1:
            value = parts[0]
            # Determinar si es IMEI (15 dígitos) o ICCID (19-20 dígitos)
            if re.match(r'^\d{15}$', value):
                valid.append(DeviceSerialOutput(imei=value, iccid=None))
            elif re.match(r'^\d{19,20}$', value):
                valid.append(DeviceSerialOutput(imei="", iccid=value))
            else:
                invalid.append({
                    "input": trimmed,
                    "error": "Formato inválido. Debe ser IMEI (15 dígitos) o ICCID (19-20 dígitos)"
                })

        elif len(parts) == 2:
            first, second = parts
            imei = ""
            iccid = ""

            # Identificar cual es IMEI y cual ICCID
            if re.match(r'^\d{15}$', first):
                imei = first
            elif re.match(r'^\d{19,20}$', first):
                iccid = first

            if re.match(r'^\d{15}$', second):
                imei = second
            elif re.match(r'^\d{19,20}$', second):
                iccid = second

            if imei or iccid:
                valid.append(DeviceSerialOutput(imei=imei, iccid=iccid or None))
            else:
                invalid.append({
                    "input": trimmed,
                    "error": "No se pudo identificar IMEI o ICCID válidos"
                })

        else:
            invalid.append({
                "input": trimmed,
                "error": "Demasiados valores en la línea"
            })

    return ParseResult(
        valid=valid,
        invalid=invalid,
        total=len(valid) + len(invalid)
    )


@router.post("/validate", response_model=ValidationResult)
async def validate_serial(
    request: ValidateSerialRequest,
    current_user: Employee = Depends(get_current_user)
):
    """
    Valida un serial individual contra la base de datos
    Verifica existencia y si ya fue notificado
    """
    serial = request.serial
    device = None

    # Buscar dispositivo por IMEI, ICCID o package_no
    if serial.imei:
        device = await Device.find_by_imei(serial.imei)
    elif serial.iccid:
        device = await Device.find_by_ccid(serial.iccid)
    elif serial.package_no:
        # Si es package, buscar todos los dispositivos de ese paquete
        devices = await Device.find_by_package(serial.package_no)
        if devices:
            device = devices[0]  # Tomar el primero como referencia

    if not device:
        return ValidationResult(
            serial=DeviceSerialOutput(**serial.dict()),
            valid=False,
            exists=False,
            already_notified=False,
            error="Dispositivo no encontrado en la base de datos"
        )

    # Verificar si ya fue notificado
    if device.notificado:
        return ValidationResult(
            serial=DeviceSerialOutput(
                **serial.dict(),
                device_id=str(device.id)
            ),
            valid=False,
            exists=True,
            already_notified=True,
            error=f"Ya notificado el {device.fecha_notificacion.strftime('%Y-%m-%d') if device.fecha_notificacion else 'fecha desconocida'}",
            device_id=str(device.id)
        )

    # Dispositivo válido para notificar
    return ValidationResult(
        serial=DeviceSerialOutput(
            **serial.dict(),
            device_id=str(device.id)
        ),
        valid=True,
        exists=True,
        already_notified=False,
        device_id=str(device.id)
    )


@router.post("/validate-bulk", response_model=BulkValidationResult)
async def validate_bulk(
    request: ValidateBulkRequest,
    current_user: Employee = Depends(get_current_user)
):
    """
    Valida múltiples seriales en lote
    Retorna estadísticas y detalles de cada uno
    """
    results = []

    for serial_input in request.serials:
        result = await validate_serial(
            ValidateSerialRequest(serial=serial_input),
            current_user
        )
        results.append(result)

    valid_count = sum(1 for r in results if r.valid)
    already_notified_count = sum(1 for r in results if r.already_notified)
    invalid_count = len(results) - valid_count - already_notified_count

    return BulkValidationResult(
        total=len(results),
        valid=valid_count,
        invalid=invalid_count,
        already_notified=already_notified_count,
        results=results
    )


# ════════════════════════════════════════════════════════════════════════
# NOTIFICACIÓN Y ENVÍO
# ════════════════════════════════════════════════════════════════════════

def generate_csv_content(serials: list, format_type: CSVFormatEnum) -> str:
    """Genera el contenido del CSV según el formato"""
    csv_buffer = io.StringIO()

    if format_type == CSVFormatEnum.SEPARATED:
        # Dos columnas: IMEI,ICCID
        csv_buffer.write("IMEI,ICCID\n")
        for serial in serials:
            imei = serial.imei if hasattr(serial, 'imei') else serial.get('imei', '')
            iccid = serial.iccid if hasattr(serial, 'iccid') else serial.get('iccid', '')
            csv_buffer.write(f"{imei or ''},{iccid or ''}\n")
    else:
        # Una columna: "IMEI ICCID"
        csv_buffer.write("Número de Serie\n")
        for serial in serials:
            imei = serial.imei if hasattr(serial, 'imei') else serial.get('imei', '')
            iccid = serial.iccid if hasattr(serial, 'iccid') else serial.get('iccid', '')
            parts = [p for p in [imei, iccid] if p]
            combined = ' '.join(parts)
            csv_buffer.write(f"{combined}\n")

    return csv_buffer.getvalue()


@router.post("/send", response_model=NotificationResponse)
async def send_notification(
    request: SendNotificationRequest,
    current_user: Employee = Depends(get_current_user)
):
    """
    Envía notificación de series a un cliente

    Proceso:
    1. Valida todos los dispositivos
    2. Genera CSV
    3. Envía email con CSV adjunto
    4. Marca dispositivos como notificados
    5. Registra eventos en device_events
    6. Guarda historial en series_notifications
    """
    try:
        # 1. Verificar que el cliente existe
        customer = await Customer.find_one(Customer.id == request.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado"
            )

        # 2. Validar todos los seriales
        device_ids = []
        failed_serials = []
        valid_devices = []

        for serial_input in request.serials:
            # Buscar dispositivo
            device = None
            if serial_input.imei:
                device = await Device.find_by_imei(serial_input.imei)
            elif serial_input.iccid:
                device = await Device.find_by_ccid(serial_input.iccid)
            elif serial_input.package_no:
                devices = await Device.find_by_package(serial_input.package_no)
                if devices:
                    # Si es un package, agregar todos los dispositivos
                    for dev in devices:
                        if not dev.notificado:
                            device_ids.append(str(dev.id))
                            valid_devices.append(dev)
                    continue

            if not device:
                failed_serials.append(serial_input.imei or serial_input.iccid or "")
                continue

            if device.notificado:
                failed_serials.append(serial_input.imei)
                continue

            device_ids.append(str(device.id))
            valid_devices.append(device)

        if not valid_devices:
            return NotificationResponse(
                success=False,
                message="No hay dispositivos válidos para notificar",
                notified_count=0,
                csv_filename="",
                email_sent=False,
                failed_serials=failed_serials
            )

        # 3. Generar CSV
        csv_content = generate_csv_content(request.serials, request.csv_format)
        csv_filename = f"series_{customer.customer_code}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

        # 4. Enviar email
        email_subject = f"OSE Platform - Notificación de Dispositivos - {customer.full_name}"
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #667eea;">OSE Platform - Notificación de Dispositivos</h2>

            <p>Estimado cliente <strong>{customer.full_name}</strong>,</p>

            <p>Le informamos que se han asignado <strong>{len(valid_devices)} dispositivos</strong> a su cuenta.</p>

            <p>Adjunto encontrará un archivo CSV con los números de serie (IMEI/ICCID) de los dispositivos.</p>

            {f'<p><strong>Ubicación:</strong> {request.location}</p>' if request.location else ''}
            {f'<p><strong>Notas:</strong> {request.notes}</p>' if request.notes else ''}

            <p>Para cualquier consulta, no dude en contactarnos.</p>

            <hr style="border: 1px solid #e0e0e0; margin: 20px 0;">

            <p style="color: #666; font-size: 12px;">
                <strong>Oversun Energy</strong><br>
                Este es un email automático generado por OSE Platform<br>
                Operador: {current_user.name} {current_user.surname} ({current_user.email})
            </p>
        </body>
        </html>
        """

        email_result = await email_service.send_email(
            to=[request.email_to],
            cc=request.email_cc or [],
            subject=email_subject,
            body=email_body,
            html=True,
            attachments=[{
                "filename": csv_filename,
                "content": csv_content.encode('utf-8')
            }]
        )

        # 5. Marcar dispositivos como notificados y crear eventos
        for device in valid_devices:
            await device.mark_as_notified(
                customer=customer.full_name,
                operator=str(current_user.id)
            )

            # Actualizar ubicación si se especificó
            if request.location:
                device.current_location = request.location
                await device.save()

        # 6. Guardar en historial
        notification = SeriesNotification(
            notification_date=datetime.utcnow(),
            customer_id=str(customer.id),
            customer_name=customer.full_name,
            customer_code=customer.customer_code,
            customer_email=customer.email,
            device_count=len(valid_devices),
            device_ids=device_ids,
            serials=[{
                "imei": s.imei,
                "iccid": s.iccid
            } for s in request.serials],
            csv_format=request.csv_format.value,
            csv_filename=csv_filename,
            csv_content=csv_content,  # Opcional, puede ser muy grande
            email_to=request.email_to,
            email_cc=request.email_cc or [],
            email_subject=email_subject,
            email_sent=email_result["success"],
            location=request.location,
            notes=request.notes,
            operator_id=str(current_user.id),
            operator_name=f"{current_user.name} {current_user.surname}",
            operator_email=current_user.email,
            source="app1"
        )
        await notification.insert()

        return NotificationResponse(
            success=True,
            message=f"Notificación enviada exitosamente a {customer.full_name}",
            notification_id=str(notification.id),
            notified_count=len(valid_devices),
            csv_content=csv_content,
            csv_filename=csv_filename,
            email_sent=email_result["success"],
            failed_serials=failed_serials
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar notificación: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════════
# HISTORIAL Y CONSULTAS
# ════════════════════════════════════════════════════════════════════════

@router.get("/history", response_model=NotificationHistoryResponse)
async def get_history(
    page: int = 1,
    limit: int = 20,
    customer_id: Optional[str] = None,
    operator_id: Optional[str] = None,
    current_user: Employee = Depends(get_current_user)
):
    """
    Obtiene el historial de notificaciones con paginación
    Puede filtrar por cliente u operador
    """
    history = await SeriesNotification.get_history(
        page=page,
        limit=limit,
        customer_id=customer_id,
        operator_id=operator_id
    )

    items = [
        NotificationHistoryItem(
            id=str(item.id),
            notification_date=item.notification_date,
            customer_id=item.customer_id,
            customer_name=item.customer_name,
            customer_email=item.customer_email,
            device_count=item.device_count,
            csv_format=item.csv_format,
            csv_filename=item.csv_filename,
            email_to=item.email_to,
            email_cc=item.email_cc,
            email_sent=item.email_sent,
            location=item.location,
            notes=item.notes,
            operator_id=item.operator_id,
            operator_name=item.operator_name,
            operator_email=item.operator_email,
            serials=item.serials,
            created_at=item.created_at
        )
        for item in history["items"]
    ]

    return NotificationHistoryResponse(
        items=items,
        total=history["total"],
        page=history["page"],
        limit=history["limit"],
        pages=history["pages"]
    )


@router.get("/{notification_id}", response_model=NotificationDetailsResponse)
async def get_notification_details(
    notification_id: str,
    current_user: Employee = Depends(get_current_user)
):
    """
    Obtiene los detalles completos de una notificación específica
    Incluye información de los dispositivos notificados
    """
    notification = await SeriesNotification.find_one(
        SeriesNotification.id == notification_id
    )

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificación no encontrada"
        )

    # Obtener información de dispositivos
    devices = []
    for device_id in notification.device_ids:
        device = await Device.find_one(Device.id == device_id)
        if device:
            devices.append({
                "id": str(device.id),
                "imei": device.imei,
                "ccid": device.ccid,
                "status": device.status.value,
                "current_location": device.current_location
            })

    return NotificationDetailsResponse(
        notification=NotificationHistoryItem(
            id=str(notification.id),
            notification_date=notification.notification_date,
            customer_id=notification.customer_id,
            customer_name=notification.customer_name,
            customer_email=notification.customer_email,
            device_count=notification.device_count,
            csv_format=notification.csv_format,
            csv_filename=notification.csv_filename,
            email_to=notification.email_to,
            email_cc=notification.email_cc,
            email_sent=notification.email_sent,
            location=notification.location,
            notes=notification.notes,
            operator_id=notification.operator_id,
            operator_name=notification.operator_name,
            operator_email=notification.operator_email,
            serials=notification.serials,
            created_at=notification.created_at
        ),
        devices=devices
    )


# ════════════════════════════════════════════════════════════════════════
# OPCIONES Y CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════════════

@router.get("/config/options", response_model=OptionsResponse)
async def get_options(
    current_user: Employee = Depends(get_current_user)
):
    """
    Obtiene las opciones de configuración para la aplicación
    Incluye lista de clientes activos y formatos de CSV disponibles
    """
    # Obtener clientes activos
    customers = await Customer.find_active_customers()

    customer_list = [
        CustomerOutput(
            id=str(c.id),
            name=c.full_name,
            email=c.email,
            code=c.customer_code,
            active=c.is_active,
            customer_type=c.customer_type.value
        )
        for c in customers
    ]

    return OptionsResponse(
        customers=customer_list
    )
