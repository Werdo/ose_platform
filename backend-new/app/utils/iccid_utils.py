"""
OSE Platform - ICCID Utilities
Algoritmo Luhn y generación de rangos de ICCID
"""

from typing import List, Tuple


def luhn_check_digit(number_without_check: str) -> str:
    """
    Calcula el dígito de control Luhn para un número

    Args:
        number_without_check: Número sin el dígito de control

    Returns:
        Dígito de control (0-9)
    """
    # Añadir un 0 temporal al final para calcular
    digits = [int(d) for d in number_without_check + "0"]

    # Separar posiciones impares y pares (de derecha a izquierda)
    odd = digits[-1::-2]
    even = digits[-2::-2]

    # Sumar posiciones impares
    checksum = sum(odd)

    # Procesar posiciones pares (duplicar y restar 9 si > 9)
    for d in even:
        d2 = d * 2
        if d2 > 9:
            d2 -= 9
        checksum += d2

    # Calcular dígito de control
    return str((10 - (checksum % 10)) % 10)


def luhn_is_valid(full_number: str) -> bool:
    """
    Valida si un número completo tiene un dígito Luhn correcto

    Args:
        full_number: Número completo incluyendo dígito de control

    Returns:
        True si el dígito de control es válido
    """
    if not full_number or len(full_number) < 2:
        return False

    base = full_number[:-1]
    check_digit = full_number[-1]

    calculated = luhn_check_digit(base)
    return calculated == check_digit


def generate_iccid_range(
    iccid_start: str,
    iccid_end: str
) -> List[Tuple[str, str, str]]:
    """
    Genera todos los ICCIDs en un rango (inclusive) con dígito Luhn recalculado

    Args:
        iccid_start: ICCID inicial (con o sin dígito de control)
        iccid_end: ICCID final (con o sin dígito de control)

    Returns:
        Lista de tuplas (iccid_completo, body, check_digit)
    """
    # Limpiar espacios y validar
    iccid_start = iccid_start.strip()
    iccid_end = iccid_end.strip()

    # Verificar que solo contengan dígitos
    if not iccid_start.isdigit() or not iccid_end.isdigit():
        raise ValueError("Los ICCIDs deben contener solo dígitos")

    # Verificar que tengan la misma longitud
    if len(iccid_start) != len(iccid_end):
        raise ValueError("Los ICCIDs deben tener la misma longitud")

    # Calcular el padding (longitud del body sin dígito de control)
    pad = len(iccid_start) - 1

    # Extraer el body (sin el último dígito)
    start_body = int(iccid_start[:-1])
    end_body = int(iccid_end[:-1])

    # Validar que start <= end
    if start_body > end_body:
        raise ValueError("El ICCID inicial debe ser menor o igual al final")

    # Generar rangos
    results = []
    for body_int in range(start_body, end_body + 1):
        # Convertir a string con padding
        body_str = str(body_int).zfill(pad)

        # Calcular dígito de control
        check_digit = luhn_check_digit(body_str)

        # ICCID completo
        iccid_full = body_str + check_digit

        results.append((iccid_full, body_str, check_digit))

    return results


def generate_iccid_count(
    iccid_start: str,
    count: int
) -> List[Tuple[str, str, str]]:
    """
    Genera N ICCIDs consecutivos a partir de un ICCID inicial

    Args:
        iccid_start: ICCID inicial
        count: Cantidad de ICCIDs a generar

    Returns:
        Lista de tuplas (iccid_completo, body, check_digit)
    """
    # Limpiar y validar
    iccid_start = iccid_start.strip()

    if not iccid_start.isdigit():
        raise ValueError("El ICCID debe contener solo dígitos")

    if count <= 0:
        raise ValueError("La cantidad debe ser mayor a 0")

    if count > 1000000:
        raise ValueError("La cantidad máxima es 1,000,000")

    # Calcular el ICCID final
    pad = len(iccid_start) - 1
    start_body = int(iccid_start[:-1])
    end_body = start_body + count - 1

    # Crear ICCID final
    iccid_end = str(end_body).zfill(pad) + "0"  # El dígito final no importa aquí

    # Usar la función de rango
    return generate_iccid_range(iccid_start, iccid_end)


def generate_iccid_with_checksum(base_iccid: str, number: int) -> str:
    """
    Genera un ICCID con checksum a partir de un base y un número

    Args:
        base_iccid: Prefijo del ICCID (ej: "89882260")
        number: Número secuencial a agregar

    Returns:
        ICCID completo con dígito de control Luhn
    """
    # Concatenar base + número
    iccid_without_check = base_iccid + str(number)

    # Calcular dígito de control
    check_digit = luhn_check_digit(iccid_without_check)

    # Retornar ICCID completo
    return iccid_without_check + check_digit


def validate_iccid_format(iccid: str) -> Tuple[bool, str]:
    """
    Valida el formato básico de un ICCID

    Args:
        iccid: ICCID a validar

    Returns:
        Tupla (es_valido, mensaje_error)
    """
    iccid = iccid.strip()

    # Verificar longitud (típicamente 19-22 dígitos)
    if len(iccid) < 19 or len(iccid) > 22:
        return False, f"Longitud inválida: {len(iccid)} (debe ser 19-22 dígitos)"

    # Verificar que solo contenga dígitos
    if not iccid.isdigit():
        return False, "El ICCID debe contener solo dígitos"

    # Validar dígito Luhn
    if not luhn_is_valid(iccid):
        return False, "Dígito de control Luhn inválido"

    return True, "ICCID válido"
