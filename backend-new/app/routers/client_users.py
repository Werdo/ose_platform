"""
OSE Platform - Client Users Router
Router para gestión de usuarios clientes (solo admin)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from passlib.context import CryptContext

from app.models.employee import Employee
from app.models.client_user import ClientUser, ClientUserRole, AppPermission
from app.dependencies.auth import get_current_active_user


router = APIRouter(
    prefix="/users/clients",
    tags=["Client Users Management"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ═══════════════════════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════

class CreateClientUserRequest(BaseModel):
    """Request para crear un usuario cliente"""
    email: EmailStr
    company_name: str
    contact_name: str
    phone: Optional[str] = None
    password: str = Field(..., min_length=6)
    role: ClientUserRole = ClientUserRole.CLIENT
    permissions: List[AppPermission] = Field(default_factory=list)
    client_code: Optional[str] = None
    notes: Optional[str] = None
    allowed_imei_prefixes: List[str] = Field(default_factory=list)
    allowed_iccid_prefixes: List[str] = Field(default_factory=list)
    assetflow_url: Optional[str] = "https://assetflow.oversunenergy.com"
    assetflow_username: Optional[str] = None


class UpdateClientUserRequest(BaseModel):
    """Request para actualizar un usuario cliente"""
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[ClientUserRole] = None
    permissions: Optional[List[AppPermission]] = None
    is_active: Optional[bool] = None
    client_code: Optional[str] = None
    notes: Optional[str] = None
    allowed_imei_prefixes: Optional[List[str]] = None
    allowed_iccid_prefixes: Optional[List[str]] = None
    assetflow_url: Optional[str] = None
    assetflow_username: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    """Request para cambiar contraseña de cliente"""
    new_password: str = Field(..., min_length=6)


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def verify_admin(current_user: Employee):
    """Verifica que el usuario actual sea admin"""
    if current_user.role.value not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden gestionar usuarios clientes"
        )


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS - CRUD
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_client_user(
    request: CreateClientUserRequest,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Crea un nuevo usuario cliente.

    Solo accesible para admin/super_admin.
    """
    verify_admin(current_user)

    # Verificar que el email no exista
    existing = await ClientUser.find_one(ClientUser.email == request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email"
        )

    # Verificar client_code si se proporciona
    if request.client_code:
        existing_code = await ClientUser.find_one(
            ClientUser.client_code == request.client_code
        )
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con este código de cliente"
            )

    # Hash de la contraseña
    hashed_password = pwd_context.hash(request.password)

    # Crear usuario
    client_user = ClientUser(
        email=request.email,
        company_name=request.company_name,
        contact_name=request.contact_name,
        phone=request.phone,
        hashed_password=hashed_password,
        role=request.role,
        permissions=request.permissions,
        client_code=request.client_code,
        notes=request.notes,
        allowed_imei_prefixes=request.allowed_imei_prefixes,
        allowed_iccid_prefixes=request.allowed_iccid_prefixes,
        assetflow_url=request.assetflow_url,
        assetflow_username=request.assetflow_username,
        created_by=current_user.employee_id
    )

    await client_user.insert()

    return {
        "success": True,
        "message": "Usuario cliente creado correctamente",
        "client_user": {
            "_id": str(client_user.id),
            "email": client_user.email,
            "company_name": client_user.company_name,
            "role": client_user.role,
            "permissions": client_user.permissions,
            "is_active": client_user.is_active
        }
    }


@router.get("/")
async def list_client_users(
    skip: int = 0,
    limit: int = 50,
    is_active: Optional[bool] = None,
    role: Optional[ClientUserRole] = None,
    search: Optional[str] = None,
    current_user: Employee = Depends(get_current_active_user)
):
    """
    Lista todos los usuarios clientes.

    Filtros opcionales:
    - is_active: Filtrar por activos/inactivos
    - role: Filtrar por rol
    - search: Buscar por email, company_name o contact_name
    """
    verify_admin(current_user)

    # Construir query
    query = {}

    if is_active is not None:
        query["is_active"] = is_active

    if role:
        query["role"] = role

    # Buscar
    if search:
        # MongoDB regex search (case insensitive)
        clients = await ClientUser.find(
            {
                "$and": [
                    query,
                    {
                        "$or": [
                            {"email": {"$regex": search, "$options": "i"}},
                            {"company_name": {"$regex": search, "$options": "i"}},
                            {"contact_name": {"$regex": search, "$options": "i"}},
                            {"client_code": {"$regex": search, "$options": "i"}}
                        ]
                    }
                ]
            }
        ).sort(-ClientUser.created_at).skip(skip).limit(limit).to_list()
    else:
        clients = await ClientUser.find(query)\
            .sort(-ClientUser.created_at)\
            .skip(skip)\
            .limit(limit)\
            .to_list()

    total = await ClientUser.count()

    return {
        "success": True,
        "total": total,
        "skip": skip,
        "limit": limit,
        "clients": [
            {
                "_id": str(client.id),
                "email": client.email,
                "company_name": client.company_name,
                "contact_name": client.contact_name,
                "phone": client.phone,
                "role": client.role,
                "permissions": client.permissions,
                "is_active": client.is_active,
                "is_verified": client.is_verified,
                "client_code": client.client_code,
                "created_at": client.created_at,
                "last_login": client.last_login
            }
            for client in clients
        ]
    }


@router.get("/{client_id}")
async def get_client_user(
    client_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtiene los detalles de un usuario cliente"""
    verify_admin(current_user)

    client = await ClientUser.get(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario cliente no encontrado"
        )

    return {
        "success": True,
        "client": {
            "_id": str(client.id),
            "email": client.email,
            "company_name": client.company_name,
            "contact_name": client.contact_name,
            "phone": client.phone,
            "role": client.role,
            "permissions": client.permissions,
            "is_active": client.is_active,
            "is_verified": client.is_verified,
            "client_code": client.client_code,
            "notes": client.notes,
            "allowed_imei_prefixes": client.allowed_imei_prefixes,
            "allowed_iccid_prefixes": client.allowed_iccid_prefixes,
            "assetflow_url": client.assetflow_url,
            "assetflow_username": client.assetflow_username,
            "created_by": client.created_by,
            "created_at": client.created_at,
            "updated_at": client.updated_at,
            "last_login": client.last_login,
            "accessible_apps": client.get_accessible_apps()
        }
    }


@router.put("/{client_id}")
async def update_client_user(
    client_id: str,
    request: UpdateClientUserRequest,
    current_user: Employee = Depends(get_current_active_user)
):
    """Actualiza un usuario cliente"""
    verify_admin(current_user)

    client = await ClientUser.get(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario cliente no encontrado"
        )

    # Actualizar campos
    update_data = request.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(client, field, value)

    client.updated_at = datetime.utcnow()
    await client.save()

    return {
        "success": True,
        "message": "Usuario cliente actualizado correctamente",
        "client": {
            "_id": str(client.id),
            "email": client.email,
            "company_name": client.company_name,
            "is_active": client.is_active,
            "permissions": client.permissions
        }
    }


@router.delete("/{client_id}")
async def delete_client_user(
    client_id: str,
    current_user: Employee = Depends(get_current_active_user)
):
    """Elimina un usuario cliente (solo super_admin)"""
    if current_user.role.value != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo super_admin puede eliminar usuarios"
        )

    client = await ClientUser.get(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario cliente no encontrado"
        )

    await client.delete()

    return {
        "success": True,
        "message": f"Usuario '{client.email}' eliminado correctamente"
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS - GESTIÓN DE PERMISOS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/{client_id}/permissions")
async def update_permissions(
    client_id: str,
    permissions: List[AppPermission],
    current_user: Employee = Depends(get_current_active_user)
):
    """Actualiza los permisos de un usuario cliente"""
    verify_admin(current_user)

    client = await ClientUser.get(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario cliente no encontrado"
        )

    client.permissions = permissions
    client.updated_at = datetime.utcnow()
    await client.save()

    return {
        "success": True,
        "message": "Permisos actualizados correctamente",
        "permissions": client.permissions,
        "accessible_apps": client.get_accessible_apps()
    }


@router.post("/{client_id}/change-password")
async def change_client_password(
    client_id: str,
    request: ChangePasswordRequest,
    current_user: Employee = Depends(get_current_active_user)
):
    """Cambia la contraseña de un usuario cliente"""
    verify_admin(current_user)

    client = await ClientUser.get(client_id)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario cliente no encontrado"
        )

    # Hash nueva contraseña
    client.hashed_password = pwd_context.hash(request.new_password)
    client.updated_at = datetime.utcnow()
    await client.save()

    return {
        "success": True,
        "message": "Contraseña actualizada correctamente"
    }


# ═══════════════════════════════════════════════════════════════════════════
# ENDPOINTS - ESTADÍSTICAS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/stats/overview")
async def get_client_stats(
    current_user: Employee = Depends(get_current_active_user)
):
    """Obtiene estadísticas de usuarios clientes"""
    verify_admin(current_user)

    total = await ClientUser.count()
    active = await ClientUser.find(ClientUser.is_active == True).count()
    inactive = total - active

    # Contar por rol
    clients_by_role = {}
    for role in ClientUserRole:
        count = await ClientUser.find(ClientUser.role == role).count()
        clients_by_role[role.value] = count

    return {
        "success": True,
        "stats": {
            "total": total,
            "active": active,
            "inactive": inactive,
            "by_role": clients_by_role
        }
    }
