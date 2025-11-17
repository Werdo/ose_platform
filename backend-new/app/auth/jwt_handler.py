"""
OSE Platform - JWT Handler
Manejo de tokens JWT para autenticación
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt

from app.config import settings
from app.utils.security import create_access_token, create_refresh_token, decode_token


class JWTHandler:
    """
    Manejador de tokens JWT
    Proporciona métodos para crear, validar y refrescar tokens
    """

    @staticmethod
    def create_tokens_for_user(
        user_id: str,
        employee_id: str,
        role: str,
        permissions: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """
        Crea access token y refresh token para un usuario

        Args:
            user_id: ID del usuario (ObjectId como string)
            employee_id: ID del empleado
            role: Rol del empleado
            permissions: Diccionario de permisos (opcional)

        Returns:
            dict: {"access_token": ..., "refresh_token": ..., "token_type": "bearer"}
        """
        # Payload para el token
        token_data = {
            "sub": user_id,  # Subject (ID del usuario)
            "employee_id": employee_id,
            "role": role,
        }

        # Añadir permisos si existen
        if permissions:
            token_data["permissions"] = permissions

        # Crear tokens
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token({"sub": user_id, "employee_id": employee_id})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # En segundos
        }

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica y decodifica un token JWT

        Args:
            token: Token JWT

        Returns:
            dict: Payload del token si es válido, None si no
        """
        payload = decode_token(token)

        if not payload:
            return None

        # Verificar que tenga los campos requeridos
        if "sub" not in payload:
            return None

        return payload

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Genera un nuevo access token usando un refresh token válido

        Args:
            refresh_token: Refresh token válido

        Returns:
            dict: Nuevo access token o None si el refresh token no es válido
        """
        payload = decode_token(refresh_token)

        if not payload:
            return None

        # Verificar que sea un refresh token
        if payload.get("type") != "refresh":
            return None

        # Verificar que tenga los campos necesarios
        user_id = payload.get("sub")
        employee_id = payload.get("employee_id")

        if not user_id or not employee_id:
            return None

        # Aquí deberíamos verificar que el refresh token coincida con el almacenado en la BD
        # Por seguridad, verificar contra Employee.refresh_token

        # Por ahora, crear un nuevo access token básico
        # En producción, deberíamos obtener el Employee de la BD para incluir role y permissions
        token_data = {
            "sub": user_id,
            "employee_id": employee_id
        }

        new_access_token = create_access_token(token_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    @staticmethod
    def get_token_expiration(token: str) -> Optional[datetime]:
        """
        Obtiene la fecha de expiración de un token

        Args:
            token: Token JWT

        Returns:
            datetime: Fecha de expiración o None si el token no es válido
        """
        payload = decode_token(token)

        if not payload or "exp" not in payload:
            return None

        return datetime.fromtimestamp(payload["exp"])

    @staticmethod
    def is_token_expired(token: str) -> bool:
        """
        Verifica si un token ha expirado

        Args:
            token: Token JWT

        Returns:
            bool: True si expiró, False si no
        """
        expiration = JWTHandler.get_token_expiration(token)

        if not expiration:
            return True

        return datetime.utcnow() > expiration


# Singleton instance
jwt_handler = JWTHandler()
