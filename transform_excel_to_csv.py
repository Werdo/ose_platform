"""
Script de Transformacion Excel a CSV
OSE Platform - Sistema de Picking

Este script transforma archivos Excel de produccion al formato CSV
requerido para la importacion en el sistema de trazabilidad jerarquica
PALLET > CARTON > DISPOSITIVO.

Autor: Sistema OSE Platform
Fecha: 2025-11-14
Versión: 1.0
"""

import pandas as pd
import re
import os
import sys
from datetime import datetime

# Configurar encoding de salida para Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def extract_product_info_from_filename(filename):
    """
    Extrae información del producto desde el nombre del archivo.

    Ejemplo de nombre de archivo:
    "10.17 WL00079317 CARLITE 55296（15-38托盘号）.xls"

    Args:
        filename (str): Nombre del archivo Excel

    Returns:
        dict: Diccionario con production_order, product_model, product_reference
    """
    print(f"\n[INFO] Analizando nombre de archivo: {filename}")

    # Extraer número de orden (WL seguido de números)
    order_match = re.search(r'WL(\d+)', filename)
    production_order = f"WL{order_match.group(1)}" if order_match else None

    # Extraer modelo y referencia (entre orden y paréntesis)
    # Formato típico: WL00079317 CARLITE 55296
    parts = re.search(r'WL\d+\s+([A-Z]+)\s+(\d+)', filename)
    product_model = parts.group(1) if parts else None
    product_reference = parts.group(2) if parts else None

    result = {
        'production_order': production_order,
        'product_model': product_model,
        'product_reference': product_reference
    }

    print(f"[INFO] Información extraída:")
    print(f"       - Orden de producción: {result['production_order']}")
    print(f"       - Modelo: {result['product_model']}")
    print(f"       - Referencia: {result['product_reference']}")

    return result


def validate_imei(imei_str):
    """
    Valida que el IMEI tenga exactamente 15 dígitos numéricos.

    Args:
        imei_str (str): IMEI a validar

    Returns:
        bool: True si es válido, False si no
    """
    if pd.isna(imei_str):
        return False

    imei = str(imei_str).strip()
    return len(imei) == 15 and imei.isdigit()


def validate_iccid(iccid_str):
    """
    Valida que el ICCID tenga 19-20 caracteres alfanuméricos.

    Args:
        iccid_str (str): ICCID a validar

    Returns:
        bool: True si es válido, False si no
    """
    if pd.isna(iccid_str):
        return False

    iccid = str(iccid_str).strip()
    return 19 <= len(iccid) <= 20 and iccid.isalnum()


def transform_excel_to_csv(excel_path, output_csv_path, validate_only=False):
    """
    Transforma el archivo Excel al formato CSV requerido.

    Args:
        excel_path (str): Ruta del archivo Excel de entrada
        output_csv_path (str): Ruta del archivo CSV de salida
        validate_only (bool): Si es True, solo valida sin generar CSV

    Returns:
        pd.DataFrame: DataFrame con los datos transformados
    """
    print("=" * 80)
    print("TRANSFORMACION EXCEL a CSV")
    print("OSE Platform - Sistema de Picking")
    print("=" * 80)

    # Verificar que el archivo existe
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Archivo no encontrado: {excel_path}")

    # Leer Excel
    print(f"\n[1/6] Leyendo archivo Excel...")
    print(f"      Ruta: {excel_path}")

    try:
        df = pd.read_excel(excel_path, engine='xlrd')
        print(f"      [OK] Archivo leido correctamente")
        print(f"      [OK] Total de filas: {len(df):,}")
        print(f"      [OK] Total de columnas: {len(df.columns)}")
    except Exception as e:
        print(f"      [ERROR] Error al leer el archivo: {str(e)}")
        raise

    # Extraer información del nombre del archivo
    print(f"\n[2/6] Extrayendo información del archivo...")
    filename = os.path.basename(excel_path)
    product_info = extract_product_info_from_filename(filename)

    # Verificar que las columnas necesarias existen
    required_columns = ['work_order_id', 'product_sn', 'ccid', 'package_no', 'INFO5']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        print(f"\n[ERROR] Faltan columnas requeridas: {missing_columns}")
        print(f"[ERROR] Columnas disponibles: {list(df.columns)}")
        raise ValueError(f"Faltan columnas requeridas: {missing_columns}")

    # Mapear columnas
    print(f"\n[3/6] Mapeando columnas...")
    df_mapped = pd.DataFrame({
        'order_number': df['work_order_id'],
        'imei': df['product_sn'].astype(str),  # Usar product_sn como IMEI principal
        'iccid': df['ccid'].astype(str),
        'carton_id': df['package_no'].astype(str),
        'pallet_id': df['INFO5'].astype(str),
        'product_model': product_info['product_model'],
        'product_reference': product_info['product_reference'],
        'package_date': df['package_date'] if 'package_date' in df.columns else None,
        'factory_id': df['factory_id'] if 'factory_id' in df.columns else None
    })

    print(f"      [OK] Columnas mapeadas correctamente")

    # Eliminar filas con datos faltantes críticos
    print(f"\n[4/6] Limpiando datos...")
    print(f"      Filas antes de limpieza: {len(df_mapped):,}")

    initial_count = len(df_mapped)
    df_mapped = df_mapped.dropna(subset=['order_number', 'imei', 'iccid', 'carton_id', 'pallet_id'])
    removed_count = initial_count - len(df_mapped)

    print(f"      Filas despues de limpieza: {len(df_mapped):,}")
    if removed_count > 0:
        print(f"      [!] Filas eliminadas por datos faltantes: {removed_count:,}")

    # Validaciones
    print(f"\n[5/6] Ejecutando validaciones...")
    print("-" * 80)

    errors = []
    warnings = []

    # Validación 1: Longitud de IMEI (15 dígitos)
    print("\n   [A] Validando IMEIs...")
    invalid_imei_mask = ~df_mapped['imei'].apply(validate_imei)
    invalid_imei_count = invalid_imei_mask.sum()

    if invalid_imei_count > 0:
        errors.append({
            'type': 'IMEI_FORMAT',
            'count': invalid_imei_count,
            'message': f'{invalid_imei_count} IMEIs con formato inválido (deben tener 15 dígitos numéricos)'
        })
        print(f"       [X] {invalid_imei_count:,} IMEIs con longitud incorrecta")
        # Mostrar ejemplos
        examples = df_mapped[invalid_imei_mask]['imei'].head(3).tolist()
        print(f"       Ejemplos: {examples}")
    else:
        print(f"       [OK] Todos los IMEIs tienen 15 digitos")

    # Validación 2: Longitud de ICCID (19-20 caracteres)
    print("\n   [B] Validando ICCIDs...")
    invalid_iccid_mask = ~df_mapped['iccid'].apply(validate_iccid)
    invalid_iccid_count = invalid_iccid_mask.sum()

    if invalid_iccid_count > 0:
        errors.append({
            'type': 'ICCID_FORMAT',
            'count': invalid_iccid_count,
            'message': f'{invalid_iccid_count} ICCIDs con formato inválido (deben tener 19-20 caracteres)'
        })
        print(f"       [X] {invalid_iccid_count:,} ICCIDs con longitud incorrecta")
        # Mostrar ejemplos
        examples = df_mapped[invalid_iccid_mask]['iccid'].head(3).tolist()
        print(f"       Ejemplos: {examples}")
    else:
        print(f"       [OK] Todos los ICCIDs tienen 19-20 caracteres")

    # Validación 3: IMEIs duplicados en el archivo
    print("\n   [C] Validando duplicados de IMEI...")
    duplicated_imei = df_mapped['imei'].duplicated().sum()

    if duplicated_imei > 0:
        errors.append({
            'type': 'IMEI_DUPLICATE',
            'count': duplicated_imei,
            'message': f'{duplicated_imei} IMEIs duplicados en el archivo'
        })
        print(f"       [X] {duplicated_imei:,} IMEIs duplicados")
        # Mostrar ejemplos
        dup_imeis = df_mapped[df_mapped['imei'].duplicated(keep=False)]['imei'].unique()[:3]
        print(f"       Ejemplos: {dup_imeis.tolist()}")
    else:
        print(f"       [OK] No hay IMEIs duplicados")

    # Validación 4: ICCIDs duplicados en el archivo
    print("\n   [D] Validando duplicados de ICCID...")
    duplicated_iccid = df_mapped['iccid'].duplicated().sum()

    if duplicated_iccid > 0:
        errors.append({
            'type': 'ICCID_DUPLICATE',
            'count': duplicated_iccid,
            'message': f'{duplicated_iccid} ICCIDs duplicados en el archivo'
        })
        print(f"       [X] {duplicated_iccid:,} ICCIDs duplicados")
    else:
        print(f"       [OK] No hay ICCIDs duplicados")

    # Validacion 5: Consistencia Carton -> Pallet
    print("\n   [E] Validando consistencia Carton > Pallet...")
    carton_pallet_consistency = df_mapped.groupby('carton_id')['pallet_id'].nunique()
    inconsistent_cartons = (carton_pallet_consistency > 1).sum()

    if inconsistent_cartons > 0:
        errors.append({
            'type': 'CARTON_PALLET_INCONSISTENCY',
            'count': inconsistent_cartons,
            'message': f'{inconsistent_cartons} cartones asociados a múltiples pallets'
        })
        print(f"       [X] {inconsistent_cartons:,} cartones asociados a multiples pallets")
    else:
        print(f"       [OK] Consistencia Carton > Pallet correcta")

    # Validacion 6: Consistencia Pallet -> Orden
    print("\n   [F] Validando consistencia Pallet > Orden...")
    pallet_order_consistency = df_mapped.groupby('pallet_id')['order_number'].nunique()
    inconsistent_pallets = (pallet_order_consistency > 1).sum()

    if inconsistent_pallets > 0:
        errors.append({
            'type': 'PALLET_ORDER_INCONSISTENCY',
            'count': inconsistent_pallets,
            'message': f'{inconsistent_pallets} pallets asociados a múltiples órdenes'
        })
        print(f"       [X] {inconsistent_pallets:,} pallets asociados a multiples ordenes")
    else:
        print(f"       [OK] Consistencia Pallet > Orden correcta")

    # Validacion 7: Dispositivos por carton (advertencia si no es 48)
    print("\n   [G] Validando dispositivos por carton...")
    devices_per_carton = df_mapped.groupby('carton_id').size()
    avg_devices = devices_per_carton.mean()
    min_devices = devices_per_carton.min()
    max_devices = devices_per_carton.max()

    print(f"       Promedio: {avg_devices:.2f} dispositivos/carton")
    print(f"       Rango: {min_devices} - {max_devices}")

    if avg_devices != 48:
        warnings.append({
            'type': 'DEVICES_PER_CARTON',
            'message': f'Promedio de dispositivos por carton: {avg_devices:.2f} (esperado: 48)'
        })
        print(f"       [!] Promedio difiere del esperado (48)")
    else:
        print(f"       [OK] Promedio correcto (48 dispositivos/carton)")

    # Validacion 8: Cartones por pallet (advertencia si no es 48)
    print("\n   [H] Validando cartones por pallet...")
    cartons_per_pallet = df_mapped.groupby('pallet_id')['carton_id'].nunique()
    avg_cartons = cartons_per_pallet.mean()
    min_cartons = cartons_per_pallet.min()
    max_cartons = cartons_per_pallet.max()

    print(f"       Promedio: {avg_cartons:.2f} cartones/pallet")
    print(f"       Rango: {min_cartons} - {max_cartons}")

    if avg_cartons != 48:
        warnings.append({
            'type': 'CARTONS_PER_PALLET',
            'message': f'Promedio de cartones por pallet: {avg_cartons:.2f} (esperado: 48)'
        })
        print(f"       [!] Promedio difiere del esperado (48)")
    else:
        print(f"       [OK] Promedio correcto (48 cartones/pallet)")

    # Estadisticas finales
    print(f"\n[6/6] Generando estadisticas...")
    print("-" * 80)

    stats = {
        'total_devices': len(df_mapped),
        'total_cartons': df_mapped['carton_id'].nunique(),
        'total_pallets': df_mapped['pallet_id'].nunique(),
        'total_orders': df_mapped['order_number'].nunique(),
        'devices_per_carton_avg': devices_per_carton.mean(),
        'cartons_per_pallet_avg': cartons_per_pallet.mean(),
        'devices_per_pallet_avg': len(df_mapped) / df_mapped['pallet_id'].nunique()
    }

    print(f"\n   RESUMEN DE DATOS:")
    print(f"   - Total de dispositivos: {stats['total_devices']:,}")
    print(f"   - Total de cartones: {stats['total_cartons']:,}")
    print(f"   - Total de pallets: {stats['total_pallets']:,}")
    print(f"   - Total de ordenes: {stats['total_orders']:,}")
    print(f"   - Dispositivos por carton (promedio): {stats['devices_per_carton_avg']:.0f}")
    print(f"   - Cartones por pallet (promedio): {stats['cartons_per_pallet_avg']:.0f}")
    print(f"   - Dispositivos por pallet (promedio): {stats['devices_per_pallet_avg']:.0f}")

    # Resumen de validacion
    print("\n" + "=" * 80)
    print("RESULTADO DE VALIDACION")
    print("=" * 80)

    if len(errors) == 0:
        print("\n[OK] VALIDACION EXITOSA - No se encontraron errores criticos")
    else:
        print(f"\n[X] VALIDACION FALLIDA - Se encontraron {len(errors)} tipos de errores:")
        for i, error in enumerate(errors, 1):
            print(f"\n   {i}. {error['type']}")
            print(f"      {error['message']}")

    if len(warnings) > 0:
        print(f"\n[!] ADVERTENCIAS - {len(warnings)} advertencias:")
        for i, warning in enumerate(warnings, 1):
            print(f"\n   {i}. {warning['type']}")
            print(f"      {warning['message']}")

    # Si solo es validacion, no generar CSV
    if validate_only:
        print("\n[INFO] Modo validacion - No se genero archivo CSV")
        return df_mapped, stats, errors, warnings

    # Exportar a CSV solo si no hay errores criticos
    if len(errors) == 0:
        print(f"\n[EXPORT] Generando archivo CSV...")
        df_mapped.to_csv(output_csv_path, index=False, encoding='utf-8')
        print(f"         [OK] Archivo CSV generado: {output_csv_path}")
    else:
        print(f"\n[ERROR] No se genero el archivo CSV debido a errores de validacion")
        print(f"        Por favor, corrija los errores e intente nuevamente")

    print("\n" + "=" * 80)
    print("FIN DE LA TRANSFORMACION")
    print("=" * 80 + "\n")

    return df_mapped, stats, errors, warnings


# EJEMPLO DE USO
if __name__ == "__main__":
    # Rutas de archivos
    excel_file = r"C:\Users\pedro\Dropbox\ICCID-SIM\10.17 WL00079317 CARLITE 55296（15-38托盘号）.xls"
    output_file = r"C:\Users\pedro\claude-code-workspace\OSE-Platform\import_ready.csv"

    try:
        # Ejecutar transformación
        df_result, stats, errors, warnings = transform_excel_to_csv(excel_file, output_file)

        # Mostrar muestra de datos
        if len(errors) == 0:
            print("\n" + "=" * 80)
            print("MUESTRA DE DATOS (primeras 10 filas)")
            print("=" * 80)
            print(df_result.head(10).to_string())

            print("\n" + "=" * 80)
            print("PROCESO COMPLETADO EXITOSAMENTE")
            print("=" * 80)
            print(f"\nArchivo CSV listo para importación: {output_file}")
            print(f"Total de dispositivos: {stats['total_devices']:,}")
            print(f"Total de cartones: {stats['total_cartons']:,}")
            print(f"Total de pallets: {stats['total_pallets']:,}")

    except Exception as e:
        print(f"\n[ERROR FATAL] {str(e)}")
        import traceback
        traceback.print_exc()
