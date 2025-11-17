"""
OSE Platform - Security Utilities
Funciones de seguridad (hashing, encriptación, JWT)
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import secrets
from cryptography.fernet import Fernet
import base64

from app.config import settings

# ════════════════════════════════════════════════════════════════════════
# PASSWORD HASHING
# ════════════════════════════════════════════════════════════════════════

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Genera un hash bcrypt de una contraseña
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su hash
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


# ════════════════════════════════════════════════════════════════════════
# JWT TOKENS
# ════════════════════════════════════════════════════════════════════════

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un JWT access token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Crea un JWT refresh token (válido por más tiempo)
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decodifica y valida un JWT token
    Retorna el payload si es válido, None si no
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def generate_random_token(length: int = 32) -> str:
    """
    Genera un token aleatorio seguro
    Útil para tokens de verificación, reset password, etc.
    """
    return secrets.token_urlsafe(length)


# ════════════════════════════════════════════════════════════════════════
# ENCRYPTION (para valores sensibles en BD)
# ════════════════════════════════════════════════════════════════════════

def _get_fernet_key() -> bytes:
    """
    Obtiene la clave de encriptación desde settings
    La clave debe ser de 32 bytes codificada en base64
    """
    # Si no hay clave configurada, generar una (solo para desarrollo)
    if not hasattr(settings, 'ENCRYPTION_KEY') or not settings.ENCRYPTION_KEY:
        # En producción esto debería venir de variables de entorno
        key = Fernet.generate_key()
        return key

    return settings.ENCRYPTION_KEY.encode()


def encrypt_value(value: str) -> str:
    """
    Encripta un valor usando Fernet (symmetric encryption)
    Útil para guardar API keys, contraseñas, etc. en la BD
    """
    f = Fernet(_get_fernet_key())
    encrypted = f.encrypt(value.encode())
    return base64.b64encode(encrypted).decode()


def decrypt_value(encrypted_value: str) -> str:
    """
    Desencripta un valor previamente encriptado
    """
    f = Fernet(_get_fernet_key())
    decrypted = f.decrypt(base64.b64decode(encrypted_value))
    return decrypted.decode()


# ════════════════════════════════════════════════════════════════════════
# VALIDACIONES
# ════════════════════════════════════════════════════════════════════════

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Valida la fortaleza de una contraseña
    Retorna (es_valida, mensaje_error)
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"

    if not any(c.isupper() for c in password):
        return False, "La contraseña debe contener al menos una mayúscula"

    if not any(c.islower() for c in password):
        return False, "La contraseña debe contener al menos una minúscula"

    if not any(c.isdigit() for c in password):
        return False, "La contraseña debe contener al menos un número"

    return True, "Contraseña válida"


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza un nombre de archivo para evitar path traversal
    """
    # Remover path separators y caracteres peligrosos
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']

    sanitized = filename
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')

    return sanitized.strip()


def generate_api_key() -> str:
    """
    Genera una API key aleatoria
    Formato: ose_XXXXXXXXXXXXXXXXXXXXXXXX
    """
    random_part = secrets.token_urlsafe(32)
    return f"ose_{random_part}"
