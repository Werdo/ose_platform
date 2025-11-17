"""
OSE Platform - Brand Update Router
Endpoint para actualizar marcas mediante archivo
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse
from beanie import PydanticObjectId
from typing import List, Dict
import pandas as pd
import io
from datetime import datetime

from app.models.device import Device
from app.models.employee import Employee
from app.dependencies.auth import get_current_user  # Usar get_current_user (no get_current_employee)

router = APIRouter()


@router.post("/upload-brand-file")
async def upload_brand_file(
    file: UploadFile = File(...),
    current_user: Employee = Depends(get_current_user)
):
    """
    Subir archivo con números de serie y marca para actualizar la BD

    Formato del archivo (Excel o CSV):
    - Columna 1: IMEI o ICCID (numero_serie)
    - Columna 2: Marca (marca)

    Retorna:
    - total: Total de registros en el archivo
    - found: Dispositivos encontrados en la BD
    - updated: Dispositivos actualizados
    - not_found: Dispositivos no encontrados
    - errors: Lista de errores
    """

    # Verificar extensión del archivo
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=400,
            detail="Formato de archivo no soportado. Use Excel (.xlsx, .xls) o CSV (.csv)"
        )

    try:
        # Leer archivo
        contents = await file.read()

        # Parsear según formato
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))

        # Validar columnas requeridas
        required_columns = ['numero_serie', 'marca']
        if not all(col in df.columns for col in required_columns):
            # Intentar con nombres alternativos
            alternative_names = {
                'numero_serie': ['imei', 'iccid', 'serial', 'serie', 'number'],
                'marca': ['brand', 'manufacturer', 'fabricante']
            }

            # Renombrar columnas si se encuentran alternativas
            for req_col, alternatives in alternative_names.items():
                if req_col not in df.columns:
                    for alt in alternatives:
                        if alt.lower() in [c.lower() for c in df.columns]:
                            # Encontrar el nombre exacto de la columna
                            actual_col = next(c for c in df.columns if c.lower() == alt.lower())
                            df.rename(columns={actual_col: req_col}, inplace=True)
                            break

            # Verificar de nuevo
            if not all(col in df.columns for col in required_columns):
                raise HTTPException(
                    status_code=400,
                    detail=f"El archivo debe contener las columnas: {', '.join(required_columns)}"
                )

        # Estadísticas
        stats = {
            'total': len(df),
            'found': 0,
            'updated': 0,
            'not_found': 0,
            'no_change': 0,
            'errors': [],
            'details': []
        }

        # Procesar cada fila
        for index, row in df.iterrows():
            try:
                numero_serie = str(row['numero_serie']).strip()
                marca_nueva = str(row['marca']).strip()

                # Buscar dispositivo por IMEI o ICCID
                device = None

                # Intentar buscar por IMEI (15 dígitos)
                if len(numero_serie) == 15 and numero_serie.isdigit():
                    device = await Device.find_one(Device.imei == numero_serie)

                # Si no se encontró, intentar por ICCID (19-22 dígitos)
                if not device and 19 <= len(numero_serie) <= 22 and numero_serie.isdigit():
                    device = await Device.find_one(Device.ccid == numero_serie)

                if not device:
                    stats['not_found'] += 1
                    stats['details'].append({
                        'numero_serie': numero_serie,
                        'marca': marca_nueva,
                        'status': 'not_found',
                        'message': 'Dispositivo no encontrado en la BD'
                    })
                    continue

                stats['found'] += 1

                # Verificar si la marca es diferente
                if device.marca != marca_nueva:
                    # Actualizar marca
                    marca_anterior = device.marca
                    device.marca = marca_nueva
                    device.fecha_actualizacion = datetime.utcnow()
                    await device.save()

                    stats['updated'] += 1
                    stats['details'].append({
                        'numero_serie': numero_serie,
                        'marca_anterior': marca_anterior,
                        'marca_nueva': marca_nueva,
                        'status': 'updated',
                        'message': f'Marca actualizada de {marca_anterior} a {marca_nueva}'
                    })
                else:
                    stats['no_change'] += 1
                    stats['details'].append({
                        'numero_serie': numero_serie,
                        'marca': marca_nueva,
                        'status': 'no_change',
                        'message': 'Marca ya es correcta, no requiere actualización'
                    })

            except Exception as e:
                stats['errors'].append({
                    'row': index + 2,  # +2 porque empieza en 0 y hay header
                    'numero_serie': numero_serie if 'numero_serie' in locals() else 'N/A',
                    'error': str(e)
                })

        return JSONResponse(content={
            "success": True,
            "message": f"Procesamiento completado: {stats['updated']} dispositivos actualizados",
            "statistics": stats
        })

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="El archivo está vacío")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando archivo: {str(e)}"
        )
