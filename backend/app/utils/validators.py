"""
OSE Platform - Custom Validators
Validadores personalizados para datos del negocio
"""

import re
from typing import Optional, Tuple


# ════════════════════════════════════════════════════════════════════════
# DISPOSITIVOS
# ════════════════════════════════════════════════════════════════════════

def validate_imei(imei: str) -> Tuple[bool, Optional[str]]:
    """
    Valida un IMEI

    Returns:
        (is_valid, error_message)
    """
    if not imei:
        return False, "IMEI is required"

    imei = imei.strip()

    # Debe ser numérico
    if not imei.isdigit():
        return False, "IMEI must contain only digits"

    # Debe tener exactamente 15 dígitos
    if len(imei) != 15:
        return False, "IMEI must be exactly 15 digits"

    # Validación Luhn (checksum)
    # Opcional pero recomendado para mayor seguridad
    if not _luhn_check(imei):
        return False, "IMEI checksum validation failed"

    return True, None


def validate_iccid(iccid: str) -> Tuple[bool, Optional[str]]:
    """
    Valida un ICCID (SIM card number)

    Returns:
        (is_valid, error_message)
    """
    if not iccid:
        return False, "ICCID is required"

    iccid = iccid.strip()

    # Debe ser numérico
    if not iccid.isdigit():
        return False, "ICCID must contain only digits"

    # Debe tener entre 19 y 22 dígitos
    if not (19 <= len(iccid) <= 22):
        return False, "ICCID must be between 19 and 22 digits"

    return True, None


def _luhn_check(number: str) -> bool:
    """
    Algoritmo de Luhn para validar checksums
    Usado en IMEI, tarjetas de crédito, etc.
    """
    def digits_of(n):
        return [int(d) for d in str(n)]

    digits = digits_of(number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]

    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))

    return checksum % 10 == 0


def parse_serial_number(serial: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parsea un número de serie que puede contener IMEI + ICCID

    Formatos soportados:
    - Solo IMEI (15 dígitos)
    - Solo ICCID (19-22 dígitos)
    - IMEI + espacio + ICCID
    - IMEI + guión + ICCID
    - IMEI + punto y coma + ICCID
    - IMEI + tabulación + ICCID

    Returns:
        (imei, iccid)
    """
    if not serial:
        return None, None

    serial = serial.strip()

    # Intentar separar por delimitadores comunes
    for delimiter in [' ', '-', ';', '\t', ',']:
        if delimiter in serial:
            parts = serial.split(delimiter)
            if len(parts) >= 2:
                imei_candidate = parts[0].strip()
                iccid_candidate = parts[1].strip()

                # Validar
                if validate_imei(imei_candidate)[0] and validate_iccid(iccid_candidate)[0]:
                    return imei_candidate, iccid_candidate

    # Si no hay delimitador, determinar por longitud
    if serial.isdigit():
        if len(serial) == 15:
            # Es solo IMEI
            if validate_imei(serial)[0]:
                return serial, None
        elif 19 <= len(serial) <= 22:
            # Es solo ICCID
            if validate_iccid(serial)[0]:
                return None, serial

    return None, None


# ════════════════════════════════════════════════════════════════════════
# CONTACTO
# ════════════════════════════════════════════════════════════════════════

def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Valida un email

    Returns:
        (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"

    email = email.strip().lower()

    # Regex básico para email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, "Invalid email format"

    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Valida un número de teléfono

    Acepta formatos:
    - +34 600 123 456
    - 600123456
    - +34600123456
    - 600-123-456

    Returns:
        (is_valid, error_message)
    """
    if not phone:
        return False, "Phone is required"

    # Remover espacios, guiones, paréntesis
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)

    # Debe empezar con + (opcional) y tener solo dígitos
    pattern = r'^\+?\d{9,15}$'

    if not re.match(pattern, cleaned):
        return False, "Invalid phone format"

    return True, None


def normalize_phone(phone: str) -> str:
    """
    Normaliza un número de teléfono
    Elimina espacios, guiones, paréntesis
    """
    return re.sub(r'[\s\-\(\)]', '', phone)


# ════════════════════════════════════════════════════════════════════════
# ÓRDENES Y CÓDIGOS
# ════════════════════════════════════════════════════════════════════════

def validate_order_number(order_number: str) -> Tuple[bool, Optional[str]]:
    """
    Valida un número de orden de producción

    Formato esperado: OP-YYYY-NNNNN
    Ejemplo: OP-2025-00001
    """
    if not order_number:
        return False, "Order number is required"

    order_number = order_number.strip().upper()

    pattern = r'^OP-\d{4}-\d{5,}$'

    if not re.match(pattern, order_number):
        return False, "Invalid order number format (expected: OP-YYYY-NNNNN)"

    return True, None


def validate_customer_code(customer_code: str) -> Tuple[bool, Optional[str]]:
    """
    Valida un código de cliente

    Formato esperado: alfanumérico, 3-20 caracteres
    """
    if not customer_code:
        return False, "Customer code is required"

    customer_code = customer_code.strip()

    if not (3 <= len(customer_code) <= 20):
        return False, "Customer code must be 3-20 characters"

    if not customer_code.replace('-', '').replace('_', '').isalnum():
        return False, "Customer code must be alphanumeric"

    return True, None


# ════════════════════════════════════════════════════════════════════════
# ARCHIVOS
# ════════════════════════════════════════════════════════════════════════

def validate_file_extension(filename: str, allowed_extensions: list) -> Tuple[bool, Optional[str]]:
    """
    Valida la extensión de un archivo

    Args:
        filename: Nombre del archivo
        allowed_extensions: Lista de extensiones permitidas (ej: ['.xlsx', '.csv'])

    Returns:
        (is_valid, error_message)
    """
    if not filename:
        return False, "Filename is required"

    # Obtener extensión
    if '.' not in filename:
        return False, "File has no extension"

    ext = '.' + filename.rsplit('.', 1)[1].lower()

    if ext not in allowed_extensions:
        return False, f"File type not allowed. Allowed: {', '.join(allowed_extensions)}"

    return True, None


def validate_file_size(file_size_bytes: int, max_size_mb: int) -> Tuple[bool, Optional[str]]:
    """
    Valida el tamaño de un archivo

    Args:
        file_size_bytes: Tamaño del archivo en bytes
        max_size_mb: Tamaño máximo permitido en MB

    Returns:
        (is_valid, error_message)
    """
    max_size_bytes = max_size_mb * 1024 * 1024

    if file_size_bytes > max_size_bytes:
        return False, f"File too large. Maximum size: {max_size_mb} MB"

    return True, None


# ════════════════════════════════════════════════════════════════════════
# CONTRASEÑAS
# ════════════════════════════════════════════════════════════════════════

def validate_password(password: str, min_length: int = 8) -> Tuple[bool, Optional[str]]:
    """
    Valida una contraseña

    Requisitos:
    - Longitud mínima
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número

    Returns:
        (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"

    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    return True, None


def password_strength(password: str) -> str:
    """
    Evalúa la fortaleza de una contraseña

    Returns:
        "weak", "medium", "strong", "very_strong"
    """
    score = 0

    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1

    if score <= 2:
        return "weak"
    elif score <= 4:
        return "medium"
    elif score <= 5:
        return "strong"
    else:
        return "very_strong"


# ════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════

def sanitize_string(text: str) -> str:
    """
    Sanitiza un string removiendo caracteres peligrosos
    """
    if not text:
        return ""

    # Remover caracteres no imprimibles
    text = ''.join(char for char in text if char.isprintable())

    # Trim
    text = text.strip()

    return text
