"""
OSE Platform - App2: Data Import Router
Importación masiva de dispositivos desde Excel/CSV
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
import pandas as pd
import numpy as np
import io
import re

from app.models import Device, DeviceEvent, ImportRecord, ImportStatus, EstadoDispositivo
from app.dependencies.auth import get_current_active_user as get_current_employee
from app.models.employee import Employee
from app.models.transform_template import TransformTemplate, DestinationType
from app.models.iccid_generation import ICCIDGenerationBatch
from app.utils.iccid_utils import (
    generate_iccid_range,
    generate_iccid_count,
    validate_iccid_format,
    luhn_is_valid
)

router = APIRouter(
    prefix="/app2",
    tags=["App2 - Import Data"]
)


# ════════════════════════════════════════════════════════════════════
# UTILIDADES DE VALIDACIÓN
# ════════════════════════════════════════════════════════════════════

def validate_imei(imei: str) -> tuple[bool, Optional[str]]:
    """Valida el formato del IMEI"""
    if not imei:
        return False, "IMEI vacío"

    imei = str(imei).strip()

    if not imei.isdigit():
        return False, "IMEI debe contener solo dígitos"

    if len(imei) != 15:
        return False, "IMEI debe tener exactamente 15 dígitos"

    return True, None


def validate_iccid(iccid: str) -> tuple[bool, Optional[str]]:
    """Valida el formato del ICCID"""
    if not iccid:
        return False, "ICCID vacío"

    iccid = str(iccid).strip()

    if not iccid.isdigit():
        return False, "ICCID debe contener solo dígitos"

    if not (19 <= len(iccid) <= 22):
        return False, "ICCID debe tener entre 19 y 22 dígitos"

    return True, None


def normalize_column_name(col: str) -> str:
    """Normaliza los nombres de columnas"""
    # Convierte a minúsculas y remueve espacios extras
    col = col.lower().strip()
    # Reemplaza espacios por guiones bajos
    col = col.replace(' ', '_')
    # Remueve caracteres especiales
    col = re.sub(r'[^\w_]', '', col)
    return col


# ════════════════════════════════════════════════════════════════════
# MAPEO DE COLUMNAS
# ════════════════════════════════════════════════════════════════════

COLUMN_MAPPING = {
    # Variaciones de IMEI
    'imei': 'imei',
    'imei_1': 'imei',
    'imei1': 'imei',
    'imei_principal': 'imei',

    # IMEI 2 (validación)
    'imei_2': 'imei_2',
    'imei2': 'imei_2',
    'imei_validation': 'imei_2',

    # ICCID
    'iccid': 'iccid',
    'ccid': 'iccid',
    'sim': 'iccid',
    'sim_number': 'iccid',

    # Package
    'package_no': 'package_no',
    'package': 'package_no',
    'numero_caja': 'package_no',
    'caja': 'package_no',

    # Orden de producción
    'orden_produccion': 'nro_orden',
    'nro_orden': 'nro_orden',
    'production_order': 'nro_orden',
    'order': 'nro_orden',

    # Lote
    'lote': 'lote',
    'batch': 'lote',
    'batch_number': 'lote',

    # Códigos
    'codigo_innerbox': 'codigo_innerbox',
    'innerbox': 'codigo_innerbox',
    'inner_box': 'codigo_innerbox',

    'codigo_unitario': 'codigo_unitario',
    'unit_code': 'codigo_unitario',
    'qr_code': 'codigo_unitario',

    # Palet y depósito
    'num_palet': 'num_palet',
    'pallet': 'num_palet',
    'palet': 'num_palet',

    'num_deposito': 'num_deposito',
    'deposito': 'num_deposito',
    'warehouse': 'num_deposito',

    # Marca y cliente
    'marca': 'marca',
    'brand': 'marca',

    'cliente': 'cliente',
    'customer': 'cliente',
    'client': 'cliente',

    # Ubicación
    'ubicacion_actual': 'ubicacion_actual',
    'ubicacion': 'ubicacion_actual',
    'location': 'ubicacion_actual',
}


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normaliza los nombres de columnas del DataFrame"""
    # Normalizar nombres de columnas
    df.columns = [normalize_column_name(col) for col in df.columns]

    # Mapear a nombres estándar
    df = df.rename(columns=COLUMN_MAPPING)

    return df


# ════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════════════

@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_and_import_file(
    file: UploadFile = File(...),
    brand: Optional[str] = None,
    request: Request = None,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Carga e importa un archivo Excel o CSV con datos de dispositivos

    **Parámetros:**
    - file: Archivo Excel o CSV
    - brand: Marca del dispositivo (opcional). Si se especifica, sobrescribe la marca del archivo

    **Campos esperados en el archivo:**
    - imei o imei_1: IMEI principal (requerido, 15 dígitos)
    - imei_2: IMEI de validación (debe coincidir con imei_1)
    - iccid o ccid: ICCID de la SIM (requerido, 19-22 dígitos)
    - package_no: Número de paquete (opcional)
    - orden_produccion: Orden de producción (opcional)
    - lote: Número de lote (opcional)
    - codigo_innerbox: Código de caja intermedia (opcional)
    - codigo_unitario: Código unitario/QR (opcional)
    - num_palet: Número de palet (opcional)
    - marca: Marca del dispositivo (opcional)
    - cliente: Cliente asignado (opcional)
    - num_deposito: Número de depósito (opcional)
    - ubicacion_actual: Ubicación física (opcional)
    """

    start_time = time.time()

    # Validar tipo de archivo
    filename = file.filename.lower()
    if not (filename.endswith('.xlsx') or filename.endswith('.xls') or filename.endswith('.csv')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no soportado. Use .xlsx, .xls o .csv"
        )

    # Leer contenido del archivo
    try:
        contents = await file.read()
        file_size = len(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error leyendo el archivo: {str(e)}"
        )

    # Crear registro de importación
    import_record = ImportRecord(
        filename=file.filename,
        file_type=filename.split('.')[-1],
        file_size=file_size,
        status=ImportStatus.PROCESSING,
        imported_by=str(current_user.id),
        imported_by_name=current_user.name,
        ip_address=request.client.host if request else None
    )
    await import_record.insert()

    # Parsear archivo
    try:
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))
    except Exception as e:
        await import_record.mark_failed(f"Error parseando el archivo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parseando el archivo: {str(e)}"
        )

    # Normalizar DataFrame
    df = normalize_dataframe(df)

    # Actualizar total de filas
    import_record.total_rows = len(df)

    # Validar columnas requeridas
    if 'imei' not in df.columns:
        await import_record.mark_failed("Columna 'imei' o 'imei_1' no encontrada en el archivo")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Columna 'imei' o 'imei_1' es requerida"
        )

    # Procesar registros
    devices_created = []
    summary_data = {
        'ordenes': set(),
        'lotes': set(),
        'marcas': set(),
        'clientes': set(),
        'packages': set()
    }

    for index, row in df.iterrows():
        row_number = index + 2  # Excel empieza en 1, y tenemos header

        try:
            # Extraer y validar IMEI
            imei = str(row.get('imei', '')).strip()
            is_valid, error = validate_imei(imei)

            if not is_valid:
                import_record.add_error(row_number, 'imei', error)
                continue

            # Validar IMEI_2 si existe
            if 'imei_2' in row and pd.notna(row['imei_2']):
                imei_2 = str(row['imei_2']).strip()
                if imei != imei_2:
                    import_record.add_error(
                        row_number,
                        'imei_2',
                        f"IMEI_2 ({imei_2}) no coincide con IMEI_1 ({imei})"
                    )
                    continue

            # Validar ICCID
            iccid = str(row.get('iccid', '')).strip() if pd.notna(row.get('iccid')) else None

            if iccid:
                is_valid, error = validate_iccid(iccid)
                if not is_valid:
                    import_record.add_warning(row_number, 'iccid', error)
                    iccid = None

            # Verificar si el dispositivo ya existe
            existing_device = await Device.buscar_por_imei(imei)
            if existing_device:
                # Si existe y se especificó una marca, actualizar la marca del dispositivo
                if brand:
                    existing_device.marca = brand
                    await existing_device.save()
                    import_record.add_warning(
                        row_number,
                        'imei',
                        f"IMEI {imei} ya existía - marca actualizada a '{brand}'"
                    )
                else:
                    import_record.add_error(
                        row_number,
                        'imei',
                        f"IMEI {imei} ya existe en la base de datos"
                    )
                import_record.duplicate_count += 1
                continue

            # Preparar datos del dispositivo
            device_data = {
                'imei': imei,
                'ccid': iccid,
                'estado': EstadoDispositivo.APROBADO,
                'valido': True,
                'fecha_importacion': datetime.utcnow(),
                'creado_por': current_user.name
            }

            # Aplicar marca del parámetro si está especificado
            if brand:
                device_data['marca'] = brand
                summary_data['marcas'].add(brand)

            # Campos opcionales
            optional_fields = [
                'package_no', 'nro_orden', 'lote', 'codigo_innerbox',
                'codigo_unitario', 'num_palet', 'marca', 'cliente',
                'num_deposito', 'ubicacion_actual'
            ]

            for field in optional_fields:
                if field in row and pd.notna(row[field]):
                    value = row[field]
                    # Convertir a string
                    if isinstance(value, (int, float, np.integer, np.floating)):
                        # Si es numérico, convertir a string eliminando decimales innecesarios
                        if isinstance(value, (int, np.integer)):
                            value = str(value)
                        elif value == int(value):  # Float sin decimales (ej: 123.0)
                            value = str(int(value))
                        else:
                            value = str(value)
                    else:
                        value = str(value).strip()

                    # Si hay brand parameter, no sobrescribir la marca
                    if field == 'marca' and brand:
                        continue

                    device_data[field] = value

                    # Actualizar resumen
                    if field == 'nro_orden' and value:
                        summary_data['ordenes'].add(value)
                    elif field == 'lote' and value:
                        summary_data['lotes'].add(value)
                    elif field == 'marca' and value:
                        summary_data['marcas'].add(value)
                    elif field == 'cliente' and value:
                        summary_data['clientes'].add(value)
                    elif field == 'package_no' and value:
                        summary_data['packages'].add(value)

            # Crear dispositivo
            device = Device(**device_data)
            await device.insert()
            devices_created.append(device)

            # Crear evento de importación
            event = DeviceEvent(
                device_id=str(device.id),
                imei=device.imei,
                event_type="device_imported",
                timestamp=datetime.utcnow(),
                operator=current_user.name,
                data={
                    "import_record_id": str(import_record.id),
                    "filename": file.filename,
                    "row_number": row_number
                }
            )
            await event.insert()

            import_record.success_count += 1

        except Exception as e:
            import_record.add_error(row_number, 'general', str(e))

    # Preparar resumen
    import_record.summary = {
        'ordenes_unicas': len(summary_data['ordenes']),
        'ordenes': list(summary_data['ordenes']),
        'lotes_unicos': len(summary_data['lotes']),
        'lotes': list(summary_data['lotes']),
        'marcas_unicas': len(summary_data['marcas']),
        'marcas': list(summary_data['marcas']),
        'clientes_unicos': len(summary_data['clientes']),
        'clientes': list(summary_data['clientes']),
        'packages_unicos': len(summary_data['packages']),
        'packages': list(summary_data['packages'])
    }

    # Marcar como completado
    processing_time = time.time() - start_time
    await import_record.mark_completed(processing_time)

    return {
        "success": True,
        "message": "Importación completada",
        "import_id": str(import_record.id),
        "summary": {
            "total_rows": import_record.total_rows,
            "success_count": import_record.success_count,
            "error_count": import_record.error_count,
            "duplicate_count": import_record.duplicate_count,
            "success_rate": round(import_record.success_rate, 2),
            "processing_time_seconds": round(processing_time, 2)
        },
        "data_summary": import_record.summary,
        "has_errors": import_record.error_count > 0,
        "errors": import_record.errors[:50],  # Primeros 50 errores
        "warnings": import_record.warnings[:50]
    }


@router.get("/history", status_code=status.HTTP_200_OK)
async def get_import_history(
    limit: int = 20,
    offset: int = 0,
    current_user: Employee = Depends(get_current_employee)
):
    """Obtiene el historial de importaciones"""

    imports = await ImportRecord.find_all().sort("-created_at").skip(offset).limit(limit).to_list()
    total = await ImportRecord.find_all().count()

    return {
        "success": True,
        "total": total,
        "limit": limit,
        "offset": offset,
        "imports": [
            {
                "id": str(imp.id),
                "filename": imp.filename,
                "file_type": imp.file_type,
                "status": imp.status,
                "total_rows": imp.total_rows,
                "success_count": imp.success_count,
                "error_count": imp.error_count,
                "duplicate_count": imp.duplicate_count,
                "success_rate": round(imp.success_rate, 2),
                "processing_time_seconds": imp.processing_time_seconds,
                "imported_by": imp.imported_by_name,
                "created_at": imp.created_at.isoformat(),
                "completed_at": imp.completed_at.isoformat() if imp.completed_at else None
            }
            for imp in imports
        ]
    }


@router.get("/history/{import_id}", status_code=status.HTTP_200_OK)
async def get_import_details(
    import_id: str,
    current_user: Employee = Depends(get_current_employee)
):
    """Obtiene los detalles de una importación específica"""

    import_record = await ImportRecord.get(import_id)

    if not import_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro de importación no encontrado"
        )

    return {
        "success": True,
        "import": {
            "id": str(import_record.id),
            "filename": import_record.filename,
            "file_type": import_record.file_type,
            "file_size": import_record.file_size,
            "status": import_record.status,
            "total_rows": import_record.total_rows,
            "success_count": import_record.success_count,
            "error_count": import_record.error_count,
            "duplicate_count": import_record.duplicate_count,
            "success_rate": round(import_record.success_rate, 2),
            "processing_time_seconds": import_record.processing_time_seconds,
            "imported_by": import_record.imported_by_name,
            "ip_address": import_record.ip_address,
            "created_at": import_record.created_at.isoformat(),
            "completed_at": import_record.completed_at.isoformat() if import_record.completed_at else None,
            "summary": import_record.summary,
            "errors": import_record.errors,
            "warnings": import_record.warnings
        }
    }


@router.get("/stats", status_code=status.HTTP_200_OK)
async def get_import_stats(
    current_user: Employee = Depends(get_current_employee)
):
    """Obtiene estadísticas generales de las importaciones"""

    # Obtener todas las importaciones
    all_imports = await ImportRecord.find_all().to_list()

    if not all_imports:
        return {
            "success": True,
            "stats": {
                "total_imports": 0,
                "total_devices_imported": 0,
                "total_errors": 0,
                "total_duplicates": 0,
                "avg_success_rate": 0,
                "avg_processing_time": 0
            }
        }

    total_devices = sum(imp.success_count for imp in all_imports)
    total_errors = sum(imp.error_count for imp in all_imports)
    total_duplicates = sum(imp.duplicate_count for imp in all_imports)

    success_rates = [imp.success_rate for imp in all_imports if imp.success_rate is not None]
    avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0

    processing_times = [imp.processing_time_seconds for imp in all_imports if imp.processing_time_seconds is not None]
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0

    return {
        "success": True,
        "stats": {
            "total_imports": len(all_imports),
            "total_devices_imported": total_devices,
            "total_errors": total_errors,
            "total_duplicates": total_duplicates,
            "avg_success_rate": round(avg_success_rate, 2),
            "avg_processing_time": round(avg_processing_time, 2)
        }
    }


# ════════════════════════════════════════════════════════════════════
# ENDPOINTS PARA GENERACIÓN DE RANGOS DE ICCID
# ════════════════════════════════════════════════════════════════════

@router.post("/generate-iccid-range", status_code=status.HTTP_200_OK)
async def generate_iccid_range_endpoint(
    iccid_start: str,
    iccid_end: str,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Genera un rango de ICCIDs con dígito Luhn recalculado

    **Parámetros:**
    - iccid_start: ICCID inicial (19-22 dígitos)
    - iccid_end: ICCID final (19-22 dígitos)

    **Returns:**
    - Lista de ICCIDs generados con body y check digit
    """
    try:
        # Validar formato de ICCIDs
        is_valid, error = validate_iccid_format(iccid_start)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ICCID inicial inválido: {error}"
            )

        is_valid, error = validate_iccid_format(iccid_end)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"ICCID final inválido: {error}"
            )

        # Generar rango
        iccids = generate_iccid_range(iccid_start, iccid_end)

        # Limitar a 10,000 por seguridad
        if len(iccids) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El rango es demasiado grande: {len(iccids)} ICCIDs. Máximo permitido: 10,000"
            )

        return {
            "success": True,
            "count": len(iccids),
            "iccid_start": iccid_start,
            "iccid_end": iccid_end,
            "iccids": [
                {
                    "iccid": iccid,
                    "body": body,
                    "check_digit": check
                }
                for iccid, body, check in iccids
            ]
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando rango de ICCIDs: {str(e)}"
        )


@router.post("/generate-iccid-csv", status_code=status.HTTP_200_OK)
async def generate_iccid_csv_endpoint(
    batches: List[Dict[str, str]],
    current_user: Employee = Depends(get_current_employee)
):
    """
    Genera un archivo CSV con múltiples lotes de ICCIDs

    **Parámetros:**
    - batches: Lista de lotes, cada uno con iccid_start, iccid_end, y nombre opcional

    **Returns:**
    - CSV content como string
    """
    try:
        all_rows = []
        batch_summary = []

        for idx, batch in enumerate(batches):
            iccid_start = batch.get('iccid_start', '').strip()
            iccid_end = batch.get('iccid_end', '').strip()
            batch_name = batch.get('name', f'Lote_{idx + 1}')

            if not iccid_start or not iccid_end:
                continue

            # Validar formato
            is_valid, error = validate_iccid_format(iccid_start)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"ICCID inicial inválido en {batch_name}: {error}"
                )

            is_valid, error = validate_iccid_format(iccid_end)
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"ICCID final inválido en {batch_name}: {error}"
                )

            # Generar rango
            iccids = generate_iccid_range(iccid_start, iccid_end)

            # Añadir a las filas
            for iccid, body, check_digit in iccids:
                all_rows.append({
                    'iccid': iccid,
                    'body': body,
                    'check_digit': check_digit,
                    'batch': batch_name
                })

            batch_summary.append({
                'name': batch_name,
                'count': len(iccids),
                'iccid_start': iccid_start,
                'iccid_end': iccid_end
            })

        # Limitar total
        if len(all_rows) > 250000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Demasiados ICCIDs: {len(all_rows)}. Máximo permitido: 250,000"
            )

        # Crear DataFrame
        df = pd.DataFrame(all_rows)

        # Generar CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_content = csv_buffer.getvalue()

        # Generar nombre del archivo
        filename = f"iccid_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        # Guardar historial en la base de datos
        generation_record = ICCIDGenerationBatch(
            name=f"Generación ICCID - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            total_iccids=len(all_rows),
            total_batches=len(batch_summary),
            batches=batch_summary,
            csv_filename=filename,
            csv_size_bytes=len(csv_content.encode('utf-8')),
            generated_by=str(current_user.id) if current_user.id else None,
            generated_by_name=f"{current_user.first_name} {current_user.last_name}" if hasattr(current_user, 'first_name') else current_user.employee_id,
            generated_by_email=current_user.email if hasattr(current_user, 'email') else None
        )
        await generation_record.insert()

        return {
            "success": True,
            "total_iccids": len(all_rows),
            "batches": batch_summary,
            "csv_content": csv_content,
            "filename": filename,
            "generation_id": str(generation_record.id)
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando CSV: {str(e)}"
        )


@router.post("/validate-iccid", status_code=status.HTTP_200_OK)
async def validate_iccid_endpoint(
    iccid: str,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Valida un ICCID (formato y dígito Luhn)

    **Parámetros:**
    - iccid: ICCID a validar

    **Returns:**
    - Resultado de la validación
    """
    is_valid, message = validate_iccid_format(iccid)

    return {
        "success": True,
        "iccid": iccid,
        "is_valid": is_valid,
        "message": message,
        "luhn_valid": luhn_is_valid(iccid) if iccid.isdigit() else False
    }


# ════════════════════════════════════════════════════════════════════
# ENDPOINTS PARA HISTORIAL DE GENERACIÓN DE ICCID
# ════════════════════════════════════════════════════════════════════

@router.get("/iccid-generation-history", status_code=status.HTTP_200_OK)
async def get_iccid_generation_history(
    limit: int = 20,
    skip: int = 0,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Obtiene el historial de generaciones de ICCID

    **Parámetros:**
    - limit: Cantidad máxima de registros a retornar (default: 20)
    - skip: Cantidad de registros a saltar (para paginación)

    **Returns:**
    - Lista de generaciones con sus detalles
    """
    try:
        # Obtener registros con paginación
        generations = await ICCIDGenerationBatch.find_all()\
            .sort("-created_at")\
            .skip(skip)\
            .limit(limit)\
            .to_list()

        # Contar total de registros
        total = await ICCIDGenerationBatch.find_all().count()

        return {
            "success": True,
            "total": total,
            "skip": skip,
            "limit": limit,
            "generations": [
                {
                    "id": str(gen.id),
                    "name": gen.name,
                    "total_iccids": gen.total_iccids,
                    "total_batches": gen.total_batches,
                    "batches": gen.batches,
                    "csv_filename": gen.csv_filename,
                    "csv_size_bytes": gen.csv_size_bytes,
                    "generated_by": gen.generated_by,
                    "generated_by_name": gen.generated_by_name,
                    "generated_by_email": gen.generated_by_email,
                    "created_at": gen.created_at,
                    "processing_time_seconds": gen.processing_time_seconds,
                    "notes": gen.notes
                }
                for gen in generations
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo historial: {str(e)}"
        )


@router.get("/iccid-generation-stats", status_code=status.HTTP_200_OK)
async def get_iccid_generation_stats(
    current_user: Employee = Depends(get_current_employee)
):
    """
    Obtiene estadísticas de generación de ICCID

    **Returns:**
    - Estadísticas generales de generación
    """
    try:
        # Total de generaciones
        total_generations = await ICCIDGenerationBatch.find_all().count()

        # Total de ICCIDs generados
        total_iccids = await ICCIDGenerationBatch.get_total_iccids_generated()

        # Última generación
        last_generation = await ICCIDGenerationBatch.find_all()\
            .sort("-created_at")\
            .limit(1)\
            .to_list()

        return {
            "success": True,
            "total_generations": total_generations,
            "total_iccids_generated": total_iccids,
            "last_generation": {
                "id": str(last_generation[0].id),
                "name": last_generation[0].name,
                "total_iccids": last_generation[0].total_iccids,
                "created_at": last_generation[0].created_at
            } if last_generation else None
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )


# ════════════════════════════════════════════════════════════════════
# ENDPOINTS PARA GESTIÓN DE PLANTILLAS DE IMPORTACIÓN
# ════════════════════════════════════════════════════════════════════

@router.get("/templates", status_code=status.HTTP_200_OK)
async def get_import_templates(
    current_user: Employee = Depends(get_current_employee)
):
    """Obtiene todas las plantillas de importación activas"""
    templates = await TransformTemplate.get_active_templates()

    return {
        "success": True,
        "count": len(templates),
        "templates": [
            {
                "id": str(t.id),
                "name": t.name,
                "description": t.description,
                "destination": t.destination,
                "usage_count": t.usage_count,
                "last_used_at": t.last_used_at.isoformat() if t.last_used_at else None,
                "created_at": t.created_at.isoformat()
            }
            for t in templates
        ]
    }


@router.get("/templates/{template_id}", status_code=status.HTTP_200_OK)
async def get_template_details(
    template_id: str,
    current_user: Employee = Depends(get_current_employee)
):
    """Obtiene los detalles completos de una plantilla"""
    template = await TransformTemplate.get(template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plantilla no encontrada"
        )

    return {
        "success": True,
        "template": {
            "id": str(template.id),
            "name": template.name,
            "description": template.description,
            "destination": template.destination,
            "file_types": template.file_types,
            "mapping": template.mapping,
            "validation": template.validation,
            "transformations": template.transformations,
            "default_values": template.default_values,
            "required_fields": template.required_fields,
            "skip_rows": template.skip_rows,
            "encoding": template.encoding,
            "delimiter": template.delimiter,
            "sheet_name": template.sheet_name,
            "is_active": template.is_active,
            "usage_count": template.usage_count,
            "last_used_at": template.last_used_at.isoformat() if template.last_used_at else None,
            "created_at": template.created_at.isoformat(),
            "updated_at": template.updated_at.isoformat()
        }
    }


@router.post("/templates", status_code=status.HTTP_201_CREATED)
async def create_import_template(
    name: str,
    description: Optional[str] = None,
    destination: DestinationType = DestinationType.DEVICES,
    file_types: List[str] = ["csv", "xlsx", "xls"],
    mapping: Dict[str, str] = {},
    validation: Dict[str, Dict[str, Any]] = {},
    transformations: Optional[Dict[str, Any]] = None,
    default_values: Optional[Dict[str, Any]] = None,
    required_fields: List[str] = [],
    skip_rows: int = 0,
    encoding: str = "utf-8",
    delimiter: str = ",",
    sheet_name: Optional[str] = None,
    current_user: Employee = Depends(get_current_employee)
):
    """Crea una nueva plantilla de importación"""

    # Verificar que no exista una plantilla con el mismo nombre
    existing = await TransformTemplate.find_by_name(name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una plantilla con el nombre '{name}'"
        )

    # Crear plantilla
    template = TransformTemplate(
        name=name,
        description=description,
        destination=destination,
        file_types=file_types,
        mapping=mapping,
        validation=validation,
        transformations=transformations,
        default_values=default_values,
        required_fields=required_fields,
        skip_rows=skip_rows,
        encoding=encoding,
        delimiter=delimiter,
        sheet_name=sheet_name,
        created_by=str(current_user.id)
    )

    await template.insert()

    return {
        "success": True,
        "message": "Plantilla creada exitosamente",
        "template_id": str(template.id),
        "template": {
            "id": str(template.id),
            "name": template.name,
            "description": template.description
        }
    }


@router.put("/templates/{template_id}", status_code=status.HTTP_200_OK)
async def update_import_template(
    template_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    mapping: Optional[Dict[str, str]] = None,
    validation: Optional[Dict[str, Dict[str, Any]]] = None,
    transformations: Optional[Dict[str, Any]] = None,
    default_values: Optional[Dict[str, Any]] = None,
    required_fields: Optional[List[str]] = None,
    skip_rows: Optional[int] = None,
    encoding: Optional[str] = None,
    delimiter: Optional[str] = None,
    sheet_name: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: Employee = Depends(get_current_employee)
):
    """Actualiza una plantilla existente"""

    template = await TransformTemplate.get(template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plantilla no encontrada"
        )

    # Actualizar campos si se proporcionan
    if name is not None:
        template.name = name
    if description is not None:
        template.description = description
    if mapping is not None:
        template.mapping = mapping
    if validation is not None:
        template.validation = validation
    if transformations is not None:
        template.transformations = transformations
    if default_values is not None:
        template.default_values = default_values
    if required_fields is not None:
        template.required_fields = required_fields
    if skip_rows is not None:
        template.skip_rows = skip_rows
    if encoding is not None:
        template.encoding = encoding
    if delimiter is not None:
        template.delimiter = delimiter
    if sheet_name is not None:
        template.sheet_name = sheet_name
    if is_active is not None:
        template.is_active = is_active

    template.updated_at = datetime.utcnow()
    await template.save()

    return {
        "success": True,
        "message": "Plantilla actualizada exitosamente",
        "template_id": str(template.id)
    }


@router.delete("/templates/{template_id}", status_code=status.HTTP_200_OK)
async def delete_import_template(
    template_id: str,
    current_user: Employee = Depends(get_current_employee)
):
    """Desactiva una plantilla (soft delete)"""

    template = await TransformTemplate.get(template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plantilla no encontrada"
        )

    template.is_active = False
    template.updated_at = datetime.utcnow()
    await template.save()

    return {
        "success": True,
        "message": "Plantilla desactivada exitosamente"
    }


@router.post("/upload-with-template", status_code=status.HTTP_200_OK)
async def upload_with_template(
    file: UploadFile = File(...),
    template_id: str = None,
    template_name: str = None,
    brand: Optional[str] = None,
    request: Request = None,
    current_user: Employee = Depends(get_current_employee)
):
    """
    Importa un archivo Excel/CSV usando una plantilla específica
    Puede especificar template_id o template_name

    **Parámetros:**
    - file: Archivo Excel o CSV
    - template_id: ID de la plantilla (opcional)
    - template_name: Nombre de la plantilla (opcional)
    - brand: Marca del dispositivo (opcional). Si se especifica, sobrescribe la marca de la plantilla
    """

    start_time = time.time()

    # Buscar plantilla
    template = None
    if template_id:
        template = await TransformTemplate.get(template_id)
    elif template_name:
        template = await TransformTemplate.find_by_name(template_name)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe especificar template_id o template_name"
        )

    if not template or not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plantilla no encontrada o inactiva"
        )

    # Validar tipo de archivo
    filename = file.filename.lower()
    file_extension = filename.split('.')[-1]

    if file_extension not in template.file_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no soportado por esta plantilla. Tipos permitidos: {', '.join(template.file_types)}"
        )

    # Leer contenido del archivo
    try:
        contents = await file.read()
        file_size = len(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error leyendo el archivo: {str(e)}"
        )

    # Crear registro de importación
    import_record = ImportRecord(
        filename=file.filename,
        file_type=file_extension,
        file_size=file_size,
        status=ImportStatus.PROCESSING,
        imported_by=str(current_user.id),
        imported_by_name=current_user.name,
        ip_address=request.client.host if request else None,
        notes=f"Importado usando plantilla: {template.name}"
    )
    await import_record.insert()

    # Parsear archivo según configuración de la plantilla
    try:
        if file_extension == 'csv':
            df = pd.read_csv(
                io.BytesIO(contents),
                encoding=template.encoding,
                delimiter=template.delimiter,
                skiprows=template.skip_rows
            )
        else:  # xlsx o xls
            df = pd.read_excel(
                io.BytesIO(contents),
                sheet_name=template.sheet_name if template.sheet_name else 0,
                skiprows=template.skip_rows
            )
    except Exception as e:
        await import_record.mark_failed(f"Error parseando el archivo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error parseando el archivo: {str(e)}"
        )

    # Actualizar total de filas
    import_record.total_rows = len(df)

    # Normalizar nombres de columnas (minúsculas, sin espacios)
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

    # Aplicar mapeo de plantilla
    df_mapped = df.rename(columns=template.mapping)

    # Verificar campos requeridos
    missing_fields = [field for field in template.required_fields if field not in df_mapped.columns]
    if missing_fields:
        await import_record.mark_failed(f"Campos requeridos faltantes: {', '.join(missing_fields)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Campos requeridos faltantes en el archivo: {', '.join(missing_fields)}"
        )

    # Procesar registros
    devices_created = []
    summary_data = {
        'ordenes': set(),
        'lotes': set(),
        'marcas': set(),
        'clientes': set(),
        'packages': set()
    }

    for index, row in df_mapped.iterrows():
        row_number = index + 2 + template.skip_rows  # Excel empieza en 1, header, y filas saltadas

        try:
            # Extraer y validar IMEI
            imei = str(row.get('imei', '')).strip() if pd.notna(row.get('imei')) else ''
            is_valid, error = validate_imei(imei)

            if not is_valid:
                import_record.add_error(row_number, 'imei', error)
                continue

            # Validar ICCID si existe
            iccid = str(row.get('iccid', '')).strip() if pd.notna(row.get('iccid')) else None
            ccid = str(row.get('ccid', '')).strip() if pd.notna(row.get('ccid')) else None
            iccid = iccid or ccid  # Priorizar iccid sobre ccid

            if iccid:
                is_valid_iccid, error = validate_iccid(iccid)
                if not is_valid_iccid:
                    import_record.add_warning(row_number, 'iccid', error)
                    iccid = None

            # Verificar si el dispositivo ya existe
            existing_device = await Device.buscar_por_imei(imei)
            if existing_device:
                # Si existe y se especificó una marca, actualizar la marca del dispositivo
                if brand:
                    existing_device.marca = brand
                    await existing_device.save()
                    import_record.add_warning(
                        row_number,
                        'imei',
                        f"IMEI {imei} ya existía - marca actualizada a '{brand}'"
                    )
                else:
                    import_record.add_error(
                        row_number,
                        'imei',
                        f"IMEI {imei} ya existe en la base de datos"
                    )
                import_record.duplicate_count += 1
                continue

            # Preparar datos del dispositivo
            device_data = {
                'imei': imei,
                'ccid': iccid,
                'estado': EstadoDispositivo.APROBADO,
                'valido': True,
                'fecha_importacion': datetime.utcnow(),
                'creado_por': current_user.name
            }

            # Aplicar valores por defecto de la plantilla
            if template.default_values:
                device_data.update(template.default_values)

            # Sobrescribir marca si se especificó el parámetro brand
            if brand:
                device_data['marca'] = brand
                summary_data['marcas'].add(brand)

            # Mapear campos del DataFrame a device_data
            field_mapping = {
                'package_no': 'package_no',
                'nro_orden': 'nro_orden',
                'work_order_id': 'nro_orden',  # Alias
                'lote': 'lote',
                'codigo_innerbox': 'codigo_innerbox',
                'codigo_unitario': 'codigo_unitario',
                'num_palet': 'num_palet',
                'pallet_id': 'pallet_id',
                'marca': 'marca',
                'cliente': 'cliente',
                'num_deposito': 'num_deposito',
                'ubicacion_actual': 'ubicacion_actual',
                'info5': 'info5',  # Campo adicional para NEOWAY
            }

            for source_field, target_field in field_mapping.items():
                if source_field in row and pd.notna(row[source_field]):
                    value = row[source_field]
                    # Convertir a string
                    if isinstance(value, (int, float, np.integer, np.floating)):
                        # Si es numérico, convertir a string eliminando decimales innecesarios
                        if isinstance(value, (int, np.integer)):
                            value = str(value)
                        elif value == int(value):  # Float sin decimales (ej: 123.0)
                            value = str(int(value))
                        else:
                            value = str(value)
                    else:
                        value = str(value).strip()

                    # Si hay brand parameter, no sobrescribir la marca
                    if target_field == 'marca' and brand:
                        continue

                    device_data[target_field] = value

                    # Actualizar resumen
                    if target_field == 'nro_orden' and value:
                        summary_data['ordenes'].add(value)
                    elif target_field == 'lote' and value:
                        summary_data['lotes'].add(value)
                    elif target_field == 'marca' and value:
                        summary_data['marcas'].add(value)
                    elif target_field == 'cliente' and value:
                        summary_data['clientes'].add(value)
                    elif target_field == 'package_no' and value:
                        summary_data['packages'].add(value)

            # Crear dispositivo
            device = Device(**device_data)
            await device.insert()
            devices_created.append(device)

            # Crear evento de importación
            event = DeviceEvent(
                device_id=str(device.id),
                imei=device.imei,
                event_type="device_imported",
                timestamp=datetime.utcnow(),
                operator=current_user.name,
                data={
                    "import_record_id": str(import_record.id),
                    "template_name": template.name,
                    "filename": file.filename,
                    "row_number": row_number
                }
            )
            await event.insert()

            import_record.success_count += 1

        except Exception as e:
            import_record.add_error(row_number, 'general', str(e))

    # Incrementar contador de uso de la plantilla
    await template.increment_usage()

    # Preparar resumen
    import_record.summary = {
        'template_used': template.name,
        'ordenes_unicas': len(summary_data['ordenes']),
        'ordenes': list(summary_data['ordenes']),
        'lotes_unicos': len(summary_data['lotes']),
        'lotes': list(summary_data['lotes']),
        'marcas_unicas': len(summary_data['marcas']),
        'marcas': list(summary_data['marcas']),
        'clientes_unicos': len(summary_data['clientes']),
        'clientes': list(summary_data['clientes']),
        'packages_unicos': len(summary_data['packages']),
        'packages': list(summary_data['packages'])
    }

    # Marcar como completado
    processing_time = time.time() - start_time
    await import_record.mark_completed(processing_time)

    return {
        "success": True,
        "message": "Importación completada",
        "import_id": str(import_record.id),
        "template_used": template.name,
        "summary": {
            "total_rows": import_record.total_rows,
            "success_count": import_record.success_count,
            "error_count": import_record.error_count,
            "duplicate_count": import_record.duplicate_count,
            "success_rate": round(import_record.success_rate, 2),
            "processing_time_seconds": round(processing_time, 2)
        },
        "data_summary": import_record.summary,
        "has_errors": import_record.error_count > 0,
        "errors": import_record.errors[:50],  # Primeros 50 errores
        "warnings": import_record.warnings[:50]
    }


@router.post("/templates/create-neoway", status_code=status.HTTP_201_CREATED)
async def create_neoway_template(
    current_user: Employee = Depends(get_current_employee)
):
    """Crea la plantilla NEOWAY_PRODUCCION_IMPORT si no existe"""

    # Verificar si ya existe
    existing = await TransformTemplate.find_by_name("NEOWAY_PRODUCCION_IMPORT")
    if existing:
        return {
            "success": True,
            "message": "La plantilla NEOWAY_PRODUCCION_IMPORT ya existe",
            "template_id": str(existing.id),
            "already_existed": True
        }

    # Crear plantilla para archivos de producción Neoway
    template = TransformTemplate(
        name="NEOWAY_PRODUCCION_IMPORT",
        description="Plantilla para importar datos de producción Neoway con IMEI, ICCID, Package No, Work Order ID e Info5",
        destination=DestinationType.DEVICES,
        file_types=["xlsx", "xls", "csv"],

        # Mapeo de columnas (origen → destino)
        mapping={
            # Variaciones comunes de columnas en archivos Neoway
            "imei": "imei",
            "imei_1": "imei",
            "imei1": "imei",
            "iccid": "iccid",
            "ccid": "iccid",
            "package_no": "package_no",
            "package": "package_no",
            "carton_no": "package_no",
            "work_order_id": "work_order_id",
            "work_order": "work_order_id",
            "order_id": "work_order_id",
            "orden_produccion": "work_order_id",
            "info5": "info5",
            "info_5": "info5",
            "additional_info": "info5",
        },

        # Campos requeridos
        required_fields=["imei"],

        # Validaciones
        validation={
            "imei": {
                "type": "string",
                "min_length": 15,
                "max_length": 15,
                "pattern": "^\\d{15}$"
            },
            "iccid": {
                "type": "string",
                "min_length": 19,
                "max_length": 22
            }
        },

        # Valores por defecto
        default_values={
            "marca": "NEOWAY",
            "estado": "APROBADO"
        },

        # Configuración del archivo
        skip_rows=0,
        encoding="utf-8",
        delimiter=",",
        sheet_name=None,  # Primera hoja por defecto

        created_by=str(current_user.id),
        is_active=True
    )

    await template.insert()

    return {
        "success": True,
        "message": "Plantilla NEOWAY_PRODUCCION_IMPORT creada exitosamente",
        "template_id": str(template.id),
        "template": {
            "id": str(template.id),
            "name": template.name,
            "description": template.description,
            "required_fields": template.required_fields,
            "mapping": template.mapping
        }
    }
