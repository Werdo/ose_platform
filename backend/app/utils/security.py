"""
OSE Platform - Security Utilities
Funciones de seguridad: hash, JWT, encriptación
"""

from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import base64
import hashlib

from app.config import settings


# ════════════════════════════════════════════════════════════════════════
# PASSWORD HASHING (bcrypt)
# ════════════════════════════════════════════════════════════════════════

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.PASSWORD_HASH_ROUNDS
)


def hash_password(password: str) -> str:
    """
    Genera un hash de la contraseña usando bcrypt
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


# Alias para compatibilidad
get_password_hash = hash_password


# ════════════════════════════════════════════════════════════════════════
# JWT TOKENS
# ════════════════════════════════════════════════════════════════════════

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un access token JWT

    Args:
        data: Datos a incluir en el token (ej: {"sub": "user_id", "role": "admin"})
        expires_delta: Duración del token (opcional)

    Returns:
        Token JWT firmado
    """
    to_encode = data.copy()

    # Expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
        "iss": settings.JWT_ISSUER
    })

    # Firmar token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un refresh token JWT

    Args:
        data: Datos a incluir en el token
        expires_delta: Duración del token (opcional)

    Returns:
        Refresh token JWT firmado
    """
    to_encode = data.copy()

    # Expiración (más larga que access token)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
        "iss": settings.JWT_ISSUER
    })

    # Firmar token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verifica y decodifica un token JWT

    Args:
        token: Token JWT a verificar
        token_type: Tipo esperado de token ("access" o "refresh")

    Returns:
        Payload del token si es válido, None si no
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": True}
        )

        # Verificar tipo de token
        if payload.get("type") != token_type:
            return None

        # Verificar emisor
        if payload.get("iss") != settings.JWT_ISSUER:
            return None

        return payload

    except JWTError:
        return None
    except Exception:
        return None


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica un token sin verificar (útil para debugging)
    ⚠️ NO usar para autenticación, solo para inspección
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_signature": False, "verify_exp": False}
        )
        return payload
    except Exception:
        return None


# ════════════════════════════════════════════════════════════════════════
# ENCRIPTACIÓN SIMÉTRICA (para datos sensibles en BD)
# ════════════════════════════════════════════════════════════════════════

def _get_fernet_key() -> bytes:
    """
    Genera una clave Fernet desde la clave de configuración
    Fernet requiere una clave de 32 bytes URL-safe base64-encoded
    """
    # Usar la clave de configuración
    key = settings.ENCRYPTION_SECRET_KEY.encode()

    # Generar hash SHA256 (32 bytes)
    hash_digest = hashlib.sha256(key).digest()

    # Codificar en base64 URL-safe
    fernet_key = base64.urlsafe_b64encode(hash_digest)

    return fernet_key


def encrypt_value(value: str) -> str:
    """
    Encripta un valor usando Fernet (AES)

    Args:
        value: Valor a encriptar (string)

    Returns:
        Valor encriptado (string base64)
    """
    try:
        fernet = Fernet(_get_fernet_key())
        encrypted = fernet.encrypt(value.encode())
        return encrypted.decode()
    except Exception as e:
        # En caso de error, retornar el valor original
        # (no ideal, pero evita pérdida de datos)
        return value


def decrypt_value(encrypted_value: str) -> str:
    """
    Desencripta un valor encriptado con Fernet

    Args:
        encrypted_value: Valor encriptado (string base64)

    Returns:
        Valor desencriptado (string)
    """
    try:
        fernet = Fernet(_get_fernet_key())
        decrypted = fernet.decrypt(encrypted_value.encode())
        return decrypted.decode()
    except Exception as e:
        # Si falla la desencriptación, puede ser que no esté encriptado
        # Retornar el valor original
        return encrypted_value


# ════════════════════════════════════════════════════════════════════════
# API KEYS
# ════════════════════════════════════════════════════════════════════════

def generate_api_key() -> str:
    """
    Genera una API key aleatoria
    """
    import secrets
    return secrets.token_urlsafe(32)


# ════════════════════════════════════════════════════════════════════════
# VALIDACIÓN DE TOKENS
# ════════════════════════════════════════════════════════════════════════

def is_token_expired(token: str) -> bool:
    """
    Verifica si un token ha expirado
    """
    payload = decode_token(token)
    if not payload:
        return True

    exp = payload.get("exp")
    if not exp:
        return True

    return datetime.utcnow().timestamp() > exp


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Obtiene la fecha de expiración de un token
    """
    payload = decode_token(token)
    if not payload:
        return None

    exp = payload.get("exp")
    if not exp:
        return None

    return datetime.fromtimestamp(exp)


def get_token_subject(token: str) -> Optional[str]:
    """
    Obtiene el subject (usuario) de un token
    """
    payload = verify_token(token)
    if not payload:
        return None

    return payload.get("sub")


# ════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════

def generate_reset_token(email: str) -> str:
    """
    Genera un token para reset de contraseña
    """
    data = {
        "sub": email,
        "purpose": "password_reset"
    }
    return create_access_token(data, expires_delta=timedelta(hours=1))


def verify_reset_token(token: str) -> Optional[str]:
    """
    Verifica un token de reset de contraseña
    Retorna el email si es válido
    """
    payload = verify_token(token)
    if not payload:
        return None

    if payload.get("purpose") != "password_reset":
        return None

    return payload.get("sub")
