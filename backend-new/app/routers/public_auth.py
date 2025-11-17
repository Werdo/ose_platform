"""
OSE Platform - Public Authentication Router
Sistema de autenticación para usuarios externos del portal público
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import secrets
from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext

from app.models.public_user import PublicUser, PublicUserStatus
from app.config import settings

router = APIRouter(
    prefix="/public/auth",
    tags=["Public Portal - Authentication"]
)

# Security
security = HTTPBearer()

# ════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ════════════════════════════════════════════════════════════════════════

class PublicRegister(BaseModel):
    email: EmailStr
    password: str
    nombre: str
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    empresa: Optional[str] = None


class PublicLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ════════════════════════════════════════════════════════════════════════
# UTILITIES
# ════════════════════════════════════════════════════════════════════════

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashea una contraseña usando bcrypt"""
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verifica una contraseña contra su hash"""
    try:
        return pwd_context.verify(password, hashed)
    except Exception:
        return False


def create_public_token(user_id: str, email: str) -> str:
    """Crea un JWT token para usuario público"""
    payload = {
        "sub": user_id,
        "email": email,
        "type": "public",
        "exp": datetime.utcnow() + timedelta(days=7),  # Token válido por 7 días
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def get_current_public_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> PublicUser:
    """
    Dependency para obtener el usuario público actual desde el token JWT
    """
    token = credentials.credentials

    try:
        # Decodificar token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Verificar que es un token público
        if payload.get("type") != "public":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido para portal público"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

        # Buscar usuario
        user = await PublicUser.get(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario no encontrado"
            )

        # Verificar estado
        if user.status != PublicUserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo o bloqueado"
            )

        return user

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


# ════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ════════════════════════════════════════════════════════════════════════

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_public_user(data: PublicRegister):
    """
    Registro de nuevo usuario público

    **Nota:** El usuario se crea activo pero no verificado.
    Se puede implementar verificación por email posteriormente.
    """
    try:
        # Verificar si el email ya existe
        existing_user = await PublicUser.buscar_por_email(data.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )

        # Validar contraseña
        if len(data.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe tener al menos 8 caracteres"
            )

        # Crear usuario
        new_user = PublicUser(
            email=data.email,
            password_hash=hash_password(data.password),
            nombre=data.nombre,
            apellidos=data.apellidos,
            telefono=data.telefono,
            empresa=data.empresa,
            status=PublicUserStatus.ACTIVE,
            is_verified=False,  # Puede implementarse verificación por email
            verification_token=secrets.token_urlsafe(32)
        )

        await new_user.insert()

        # Generar token
        token = create_public_token(str(new_user.id), new_user.email)

        return {
            "success": True,
            "message": "Usuario registrado exitosamente",
            "access_token": token,
            "token_type": "bearer",
            "user": new_user.dict_safe()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_public_user(data: PublicLogin):
    """
    Login de usuario público
    """
    try:
        # Buscar usuario por email
        user = await PublicUser.buscar_por_email(data.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )

        # Verificar contraseña
        if not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )

        # Verificar estado
        if user.status == PublicUserStatus.BLOCKED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario bloqueado. Contacte al administrador"
            )

        if user.status == PublicUserStatus.INACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo"
            )

        # Actualizar último login
        user.last_login = datetime.utcnow()
        await user.save()

        # Generar token
        token = create_public_token(str(user.id), user.email)

        return {
            "success": True,
            "message": "Login exitoso",
            "access_token": token,
            "token_type": "bearer",
            "user": user.dict_safe()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar sesión: {str(e)}"
        )


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: PublicUser = Depends(get_current_public_user)
):
    """
    Obtiene información del usuario público actual
    """
    return {
        "success": True,
        "user": current_user.dict_safe()
    }


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_public_user(
    current_user: PublicUser = Depends(get_current_public_user)
):
    """
    Logout (en JWT no hace nada en el servidor, el cliente debe eliminar el token)
    """
    return {
        "success": True,
        "message": "Sesión cerrada exitosamente"
    }
