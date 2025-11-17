"""
OSE Platform - Device Routes
Endpoints CRUD para dispositivos
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from beanie import PydanticObjectId

from app.schemas import (
    DeviceCreate,
    DeviceUpdate,
    DeviceResponse,
    DeviceSummary,
    DeviceFilter,
    DeviceStatusChange,
    DeviceShipping,
    DeviceAssignment,
    DeviceStatistics,
    PaginatedResponse,
    PaginationParams,
    PaginationMeta,
    MessageResponse,
    SuccessResponse,
)
from app.models.device import Device, DeviceStatus
from app.models.employee import Employee
from app.dependencies import get_current_user, require_admin
from app.middleware import audit_logger
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/devices", tags=["Devices"])


# ════════════════════════════════════════════════════════════════════════
# CREATE
# ════════════════════════════════════════════════════════════════════════

@router.post(
    "",
    response_model=SuccessResponse[DeviceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Device",
    description="Crea un nuevo dispositivo"
)
async def create_device(
    device_data: DeviceCreate,
    current_user: Employee = Depends(get_current_user)
):
    """Crea un nuevo dispositivo"""
    # Check if IMEI already exists
    existing = await Device.find_one(Device.imei == device_data.imei)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Device with IMEI {device_data.imei} already exists"
        )

    # Create device
    device = Device(
        **device_data.model_dump(),
        operator_id=str(current_user.id)
    )
    await device.save()

    # Log event
    audit_logger.log_data_access(
        user_id=str(current_user.id),
        resource="device",
        action="create",
        resource_id=str(device.id)
    )

    device_response = DeviceResponse(**device.model_dump(), id=str(device.id))
    return SuccessResponse(data=device_response)


# ════════════════════════════════════════════════════════════════════════
# READ
# ════════════════════════════════════════════════════════════════════════

@router.get(
    "",
    response_model=PaginatedResponse[DeviceSummary],
    status_code=status.HTTP_200_OK,
    summary="List Devices",
    description="Lista dispositivos con filtros y paginación"
)
async def list_devices(
    pagination: PaginationParams = Depends(),
    filters: DeviceFilter = Depends(),
    current_user: Employee = Depends(get_current_user)
):
    """Lista dispositivos con filtros y paginación"""
    # Build query
    query = {}

    if filters.status:
        query["status"] = filters.status
    if filters.production_order:
        query["production_order"] = filters.production_order
    if filters.batch:
        query["batch"] = filters.batch
    if filters.production_line:
        query["production_line"] = filters.production_line
    if filters.sku:
        query["sku"] = filters.sku
    if filters.customer_id:
        query["customer_id"] = filters.customer_id
    if filters.qc_approved is not None:
        query["qc_approved"] = filters.qc_approved
    if filters.warranty_active is not None:
        query["warranty_active"] = filters.warranty_active

    # Search
    if filters.search:
        query["$or"] = [
            {"imei": {"$regex": filters.search, "$options": "i"}},
            {"ccid": {"$regex": filters.search, "$options": "i"}},
        ]

    # Count total
    total = await Device.find(query).count()

    # Get paginated results
    devices = await Device.find(query)\
        .skip(pagination.skip)\
        .limit(pagination.page_size)\
        .to_list()

    # Convert to summaries
    summaries = [
        DeviceSummary(**device.model_dump(), id=str(device.id))
        for device in devices
    ]

    # Pagination meta
    meta = PaginationMeta.create(
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )

    return PaginatedResponse(data=summaries, meta=meta)


@router.get(
    "/{device_id}",
    response_model=SuccessResponse[DeviceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Device",
    description="Obtiene un dispositivo por ID"
)
async def get_device(
    device_id: str,
    current_user: Employee = Depends(get_current_user)
):
    """Obtiene un dispositivo por ID"""
    try:
        device = await Device.get(PydanticObjectId(device_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    device_response = DeviceResponse(**device.model_dump(), id=str(device.id))
    return SuccessResponse(data=device_response)


@router.get(
    "/imei/{imei}",
    response_model=SuccessResponse[DeviceResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Device by IMEI",
    description="Obtiene un dispositivo por IMEI"
)
async def get_device_by_imei(
    imei: str,
    current_user: Employee = Depends(get_current_user)
):
    """Obtiene un dispositivo por IMEI"""
    device = await Device.find_one(Device.imei == imei)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with IMEI {imei} not found"
        )

    device_response = DeviceResponse(**device.model_dump(), id=str(device.id))
    return SuccessResponse(data=device_response)


# ════════════════════════════════════════════════════════════════════════
# UPDATE
# ════════════════════════════════════════════════════════════════════════

@router.patch(
    "/{device_id}",
    response_model=SuccessResponse[DeviceResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Device",
    description="Actualiza un dispositivo"
)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    current_user: Employee = Depends(get_current_user)
):
    """Actualiza un dispositivo"""
    try:
        device = await Device.get(PydanticObjectId(device_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # Update fields
    update_data = device_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)

    await device.save()

    # Log event
    audit_logger.log_data_access(
        user_id=str(current_user.id),
        resource="device",
        action="update",
        resource_id=str(device.id)
    )

    device_response = DeviceResponse(**device.model_dump(), id=str(device.id))
    return SuccessResponse(data=device_response)


# ════════════════════════════════════════════════════════════════════════
# DELETE
# ════════════════════════════════════════════════════════════════════════

@router.delete(
    "/{device_id}",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete Device",
    description="Elimina un dispositivo (solo admin)"
)
async def delete_device(
    device_id: str,
    current_user: Employee = Depends(require_admin)
):
    """Elimina un dispositivo (solo admin)"""
    try:
        device = await Device.get(PydanticObjectId(device_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    await device.delete()

    # Log event
    audit_logger.log_data_access(
        user_id=str(current_user.id),
        resource="device",
        action="delete",
        resource_id=device_id
    )

    return MessageResponse(message="Device deleted successfully")


# ════════════════════════════════════════════════════════════════════════
# SPECIAL OPERATIONS
# ════════════════════════════════════════════════════════════════════════

@router.post(
    "/{device_id}/status",
    response_model=SuccessResponse[DeviceResponse],
    status_code=status.HTTP_200_OK,
    summary="Change Device Status",
    description="Cambia el status de un dispositivo"
)
async def change_device_status(
    device_id: str,
    status_change: DeviceStatusChange,
    current_user: Employee = Depends(get_current_user)
):
    """Cambia el status de un dispositivo"""
    try:
        device = await Device.get(PydanticObjectId(device_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # Change status (uses model method for event logging)
    await device.change_status(
        new_status=status_change.new_status,
        operator_id=str(current_user.id),
        reason=status_change.reason,
        notes=status_change.notes
    )

    device_response = DeviceResponse(**device.model_dump(), id=str(device.id))
    return SuccessResponse(data=device_response)


@router.post(
    "/{device_id}/assign",
    response_model=SuccessResponse[DeviceResponse],
    status_code=status.HTTP_200_OK,
    summary="Assign Device to Customer",
    description="Asigna un dispositivo a un cliente"
)
async def assign_device(
    device_id: str,
    assignment: DeviceAssignment,
    current_user: Employee = Depends(get_current_user)
):
    """Asigna un dispositivo a un cliente"""
    try:
        device = await Device.get(PydanticObjectId(device_id))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # Assign to customer
    from datetime import datetime
    device.customer_id = assignment.customer_id
    device.assigned_at = datetime.utcnow()

    if assignment.activate_warranty:
        device.activate_warranty()

    if assignment.notes:
        device.notes = assignment.notes

    await device.save()

    # TODO: Send notification if requested

    device_response = DeviceResponse(**device.model_dump(), id=str(device.id))
    return SuccessResponse(data=device_response)


# ════════════════════════════════════════════════════════════════════════
# STATISTICS
# ════════════════════════════════════════════════════════════════════════

@router.get(
    "/stats/overview",
    response_model=SuccessResponse[DeviceStatistics],
    status_code=status.HTTP_200_OK,
    summary="Device Statistics",
    description="Obtiene estadísticas de dispositivos"
)
async def get_device_statistics(
    current_user: Employee = Depends(get_current_user)
):
    """Obtiene estadísticas de dispositivos"""
    from datetime import datetime, timedelta

    total = await Device.find({}).count()

    # By status
    statuses = {}
    for status_val in DeviceStatus:
        count = await Device.find({"status": status_val}).count()
        statuses[status_val.value] = count

    # By SKU
    skus = {}
    # Simple aggregation (can be optimized with MongoDB aggregation pipeline)
    all_devices = await Device.find({}).to_list()
    for device in all_devices:
        sku = device.sku or "unknown"
        skus[sku] = skus.get(sku, 0) + 1

    # Produced today/week/month
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=now.weekday())
    month_start = today_start.replace(day=1)

    produced_today = await Device.find({"produced_at": {"$gte": today_start}}).count()
    produced_this_week = await Device.find({"produced_at": {"$gte": week_start}}).count()
    produced_this_month = await Device.find({"produced_at": {"$gte": month_start}}).count()

    # QC pass rate
    total_qc = await Device.find({"qc_date": {"$ne": None}}).count()
    passed_qc = await Device.find({"qc_approved": True}).count()
    qc_pass_rate = (passed_qc / total_qc * 100) if total_qc > 0 else 0

    # Under warranty
    devices_under_warranty = await Device.find({"warranty_active": True}).count()

    stats = DeviceStatistics(
        total=total,
        by_status=statuses,
        by_sku=skus,
        produced_today=produced_today,
        produced_this_week=produced_this_week,
        produced_this_month=produced_this_month,
        qc_pass_rate=round(qc_pass_rate, 2),
        devices_under_warranty=devices_under_warranty
    )

    return SuccessResponse(data=stats)
