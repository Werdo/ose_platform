"""
OSE Platform - Settings Routes
Endpoints para configuración del sistema
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas import (
    SettingResponse,
    EmailConfig,
    EmailConfigResponse,
    EmailTestRequest,
    EmailTestResponse,
    MessageResponse,
    SuccessResponse,
)
from app.models.setting import SystemSetting, SettingCategory
from app.models.employee import Employee
from app.dependencies import require_admin
from app.config import dynamic_config
from app.services import test_smtp_connection, send_email
from app.middleware import audit_logger

router = APIRouter(prefix="/settings", tags=["Settings"])


# ════════════════════════════════════════════════════════════════════════
# GENERAL SETTINGS
# ════════════════════════════════════════════════════════════════════════

@router.get(
    "",
    response_model=SuccessResponse[List[SettingResponse]],
    summary="Get All Settings",
    description="Obtiene todos los settings (solo admin)"
)
async def get_all_settings(current_user: Employee = Depends(require_admin)):
    """Obtiene todos los settings"""
    settings = await SystemSetting.find({"ui_visible": True}).to_list()
    settings_response = [
        SettingResponse(**s.model_dump(), id=str(s.id))
        for s in settings
    ]
    return SuccessResponse(data=settings_response)


@router.get(
    "/category/{category}",
    response_model=SuccessResponse[List[SettingResponse]],
    summary="Get Settings by Category",
    description="Obtiene settings de una categoría"
)
async def get_settings_by_category(
    category: SettingCategory,
    current_user: Employee = Depends(require_admin)
):
    """Obtiene settings de una categoría"""
    settings = await SystemSetting.get_by_category(category)
    settings_response = [
        SettingResponse(**s.model_dump(), id=str(s.id))
        for s in settings
    ]
    return SuccessResponse(data=settings_response)


@router.patch(
    "/{key}",
    response_model=SuccessResponse[SettingResponse],
    summary="Update Setting",
    description="Actualiza un setting"
)
async def update_setting(
    key: str,
    value: dict,  # {"value": any}
    current_user: Employee = Depends(require_admin)
):
    """Actualiza un setting"""
    # Get setting
    setting = await SystemSetting.find_one({"key": key})

    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Setting {key} not found"
        )

    # Update value
    old_value = str(setting.value)
    await SystemSetting.set_value(
        key=key,
        value=value.get("value"),
        modified_by=str(current_user.id)
    )

    # Reload setting
    setting = await SystemSetting.find_one({"key": key})

    # Clear cache
    dynamic_config.cache.pop(key, None)

    # Log change
    audit_logger.log_configuration_change(
        user_id=str(current_user.id),
        setting_key=key,
        old_value=old_value,
        new_value=str(setting.value)
    )

    return SuccessResponse(data=SettingResponse(**setting.model_dump(), id=str(setting.id)))


# ════════════════════════════════════════════════════════════════════════
# EMAIL CONFIGURATION
# ════════════════════════════════════════════════════════════════════════

@router.get(
    "/email/config",
    response_model=SuccessResponse[EmailConfigResponse],
    summary="Get Email Configuration",
    description="Obtiene la configuración de email"
)
async def get_email_config(current_user: Employee = Depends(require_admin)):
    """Obtiene la configuración de email"""
    config = {
        "enabled": await dynamic_config.get("email_enabled", True),
        "smtp_host": await dynamic_config.get("smtp_host", ""),
        "smtp_port": await dynamic_config.get("smtp_port", 587),
        "smtp_tls": await dynamic_config.get("smtp_tls", True),
        "smtp_ssl": await dynamic_config.get("smtp_ssl", False),
        "smtp_user": await dynamic_config.get("smtp_user", ""),
        "smtp_password": "********",  # Hidden
        "smtp_timeout": await dynamic_config.get("smtp_timeout", 30),
        "email_from": await dynamic_config.get("email_from", ""),
        "email_reply_to": await dynamic_config.get("email_reply_to", None),
    }

    return SuccessResponse(data=EmailConfigResponse(**config))


@router.post(
    "/email/config",
    response_model=MessageResponse,
    summary="Update Email Configuration",
    description="Actualiza la configuración de email"
)
async def update_email_config(
    config: EmailConfig,
    current_user: Employee = Depends(require_admin)
):
    """Actualiza la configuración de email"""
    # Save each setting
    settings_map = {
        "email_enabled": config.enabled,
        "smtp_host": config.smtp_host,
        "smtp_port": config.smtp_port,
        "smtp_tls": config.smtp_tls,
        "smtp_ssl": config.smtp_ssl,
        "smtp_user": config.smtp_user,
        "smtp_password": config.smtp_password,
        "smtp_timeout": config.smtp_timeout,
        "email_from": config.email_from,
        "email_reply_to": config.email_reply_to,
    }

    for key, value in settings_map.items():
        await SystemSetting.set_value(
            key=key,
            value=value,
            modified_by=str(current_user.id)
        )

        # Clear cache
        dynamic_config.cache.pop(key, None)

    # Log change
    audit_logger.log_configuration_change(
        user_id=str(current_user.id),
        setting_key="email_config",
        old_value="***",
        new_value=f"Updated by {current_user.email}"
    )

    return MessageResponse(message="Email configuration updated successfully")


@router.post(
    "/email/test",
    response_model=EmailTestResponse,
    summary="Test Email Configuration",
    description="Prueba la configuración de email"
)
async def test_email_config(
    test_request: EmailTestRequest,
    current_user: Employee = Depends(require_admin)
):
    """Prueba la configuración de email"""
    if test_request.test_connection_only:
        # Only test SMTP connection
        result = await test_smtp_connection()
        return EmailTestResponse(**result)
    else:
        # Send test email
        if not test_request.recipient:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recipient email is required for test email"
            )

        # Test connection first
        conn_result = await test_smtp_connection()
        if not conn_result["success"]:
            return EmailTestResponse(**conn_result)

        # Send test email
        result = await send_email(
            to=[test_request.recipient],
            subject="OSE Platform - Test Email",
            body="This is a test email from OSE Platform. If you received this, your email configuration is working correctly.",
            html=False
        )

        return EmailTestResponse(**result)


# ════════════════════════════════════════════════════════════════════════
# SYSTEM INFO
# ════════════════════════════════════════════════════════════════════════

@router.get(
    "/system/info",
    response_model=dict,
    summary="System Information",
    description="Obtiene información del sistema"
)
async def get_system_info(current_user: Employee = Depends(require_admin)):
    """Obtiene información del sistema"""
    from app.config import settings

    return {
        "success": True,
        "data": {
            "app_name": "OSE Platform",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "features": {
                "email": await dynamic_config.get("email_enabled", True),
                "api_docs": settings.ENVIRONMENT != "production",
            }
        }
    }
