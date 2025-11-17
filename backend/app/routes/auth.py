"""
OSE Platform - Auth Routes
Endpoints para autenticación y gestión de usuarios
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from datetime import timedelta, datetime

from app.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshTokenRequest,
    TokenResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    MessageResponse,
    CurrentUserResponse,
    EmployeePublic,
)
from app.models.employee import Employee
from app.dependencies import get_current_user
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    generate_reset_token,
    verify_reset_token,
    hash_password,
)
from app.middleware import login_rate_limiter, password_reset_limiter, audit_logger
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


# ════════════════════════════════════════════════════════════════════════
# LOGIN
# ════════════════════════════════════════════════════════════════════════

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login",
    description="Autenticación de usuario con email/employee_id y contraseña"
)
async def login(request: Request, credentials: LoginRequest):
    """
    Login endpoint

    Args:
        credentials: Email o Employee ID y contraseña del usuario

    Returns:
        LoginResponse con tokens JWT y datos del usuario

    Raises:
        HTTPException 401: Si las credenciales son inválidas
        HTTPException 429: Si excede el rate limit
    """
    # Rate limiting
    login_rate_limiter.check(request)

    # Authenticate user - try by email first, then by employee_id
    user = await Employee.find_one(
        {"$or": [
            {"email": credentials.identifier},
            {"employee_id": credentials.identifier.upper()}
        ]}
    )

    # Verify password
    if not user or not user.verify_password(credentials.password):
        # Log failed attempt
        audit_logger.log_login(
            user_id="unknown",
            username=credentials.identifier,
            ip=request.client.host if request.client else "unknown",
            success=False,
            reason="Invalid credentials"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}
    )

    # Calculate refresh token expiration
    refresh_expires = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    # Save refresh token
    await user.set_refresh_token(refresh_token, refresh_expires)

    # Log successful login
    audit_logger.log_login(
        user_id=str(user.id),
        username=user.email,
        ip=request.client.host if request.client else "unknown",
        success=True
    )

    # Prepare response
    user_public = EmployeePublic(
        id=str(user.id),
        employee_id=user.employee_id,
        name=user.name,
        surname=user.surname,
        email=user.email,
        role=user.role,
        status=user.status,
        permissions=user.permissions,
        created_at=user.created_at,
        last_login=user.last_login
    )

    tokens = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return LoginResponse(
        user=user_public,
        tokens=tokens
    )


# ════════════════════════════════════════════════════════════════════════
# REFRESH TOKEN
# ════════════════════════════════════════════════════════════════════════

@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh Token",
    description="Obtiene un nuevo access token usando un refresh token"
)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh token endpoint

    Args:
        request: Refresh token

    Returns:
        TokenResponse con nuevo access token

    Raises:
        HTTPException 401: Si el refresh token es inválido
    """
    # Verify refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    user_id = payload.get("sub")

    # Verify user exists and refresh token matches
    try:
        from beanie import PydanticObjectId
        user = await Employee.get(PydanticObjectId(user_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user or user.refresh_token != request.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Create new access token
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,  # Keep same refresh token
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


# ════════════════════════════════════════════════════════════════════════
# CURRENT USER
# ════════════════════════════════════════════════════════════════════════

@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Current User",
    description="Obtiene la información del usuario autenticado"
)
async def get_current_user_info(current_user: Employee = Depends(get_current_user)):
    """
    Get current user endpoint

    Returns:
        CurrentUserResponse con datos del usuario autenticado
    """
    from app.schemas.auth import EmployeeProfile

    profile = EmployeeProfile(
        id=str(current_user.id),
        employee_id=current_user.employee_id,
        name=current_user.name,
        surname=current_user.surname,
        email=current_user.email,
        phone=current_user.phone,
        role=current_user.role,
        status=current_user.status,
        department=None,  # Campo no implementado en modelo actual
        position=None,     # Campo no implementado en modelo actual
        hire_date=None,    # Campo no implementado en modelo actual
        permissions=current_user.permissions,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

    return CurrentUserResponse(user=profile)


# ════════════════════════════════════════════════════════════════════════
# LOGOUT
# ════════════════════════════════════════════════════════════════════════

@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout",
    description="Cierra la sesión del usuario"
)
async def logout(request: Request, current_user: Employee = Depends(get_current_user)):
    """
    Logout endpoint

    Invalida el refresh token del usuario
    """
    # Clear refresh token
    current_user.refresh_token = None
    await current_user.save()

    # Log logout
    audit_logger.log_logout(
        user_id=str(current_user.id),
        username=current_user.email,
        ip=request.client.host if request.client else "unknown"
    )

    return MessageResponse(message="Logged out successfully")


# ════════════════════════════════════════════════════════════════════════
# PASSWORD RESET
# ════════════════════════════════════════════════════════════════════════

@router.post(
    "/password-reset",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request Password Reset",
    description="Solicita un reset de contraseña (envía email con token)"
)
async def request_password_reset(request: Request, data: PasswordResetRequest):
    """
    Request password reset endpoint

    Args:
        data: Email del usuario

    Returns:
        MessageResponse confirmando el envío (siempre éxito por seguridad)
    """
    # Rate limiting
    password_reset_limiter.check(request)

    # Find user
    user = await Employee.find_one(Employee.email == data.email)

    if user:
        # Generate reset token
        reset_token = generate_reset_token(user.email)

        # TODO: Send email with reset link
        # Por ahora solo log
        logger.info(f"Password reset requested for {user.email}. Token: {reset_token}")

        # Log event
        audit_logger.log_security_event(
            event_type="password_reset_requested",
            user_id=str(user.id),
            ip=request.client.host if request.client else "unknown"
        )

    # Always return success (security: don't reveal if email exists)
    return MessageResponse(
        message="If the email exists, a password reset link has been sent"
    )


@router.post(
    "/password-reset/confirm",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Confirm Password Reset",
    description="Confirma el reset de contraseña con el token recibido"
)
async def confirm_password_reset(request: Request, data: PasswordResetConfirm):
    """
    Confirm password reset endpoint

    Args:
        data: Token y nueva contraseña

    Returns:
        MessageResponse confirmando el cambio

    Raises:
        HTTPException 400: Si el token es inválido
    """
    # Verify reset token
    email = verify_reset_token(data.token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Find user
    user = await Employee.find_one(Employee.email == email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found"
        )

    # Update password
    await user.set_password(data.new_password)

    # Log event
    audit_logger.log_security_event(
        event_type="password_reset_completed",
        user_id=str(user.id),
        ip=request.client.host if request.client else "unknown"
    )

    return MessageResponse(message="Password reset successfully")


# ════════════════════════════════════════════════════════════════════════
# PASSWORD CHANGE
# ════════════════════════════════════════════════════════════════════════

@router.post(
    "/password-change",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change Password",
    description="Cambia la contraseña del usuario autenticado"
)
async def change_password(
    request: Request,
    data: PasswordChangeRequest,
    current_user: Employee = Depends(get_current_user)
):
    """
    Change password endpoint

    Args:
        data: Contraseña actual y nueva contraseña
        current_user: Usuario autenticado

    Returns:
        MessageResponse confirmando el cambio

    Raises:
        HTTPException 400: Si la contraseña actual es incorrecta
    """
    # Verify current password
    if not current_user.verify_password(data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Update password
    await current_user.set_password(data.new_password)

    # Log event
    audit_logger.log_security_event(
        event_type="password_changed",
        user_id=str(current_user.id),
        ip=request.client.host if request.client else "unknown"
    )

    return MessageResponse(message="Password changed successfully")
