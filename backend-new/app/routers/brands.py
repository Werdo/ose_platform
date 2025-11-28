"""
Router para gestión de marcas (brands)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.models.brand import Brand
from app.dependencies.auth import get_current_active_user as get_current_employee
from app.models.employee import Employee

router = APIRouter(
    prefix="/brands",
    tags=["Brands"]
)


@router.get("", status_code=status.HTTP_200_OK)
async def get_brands(
    active_only: bool = True,
    current_user: Employee = Depends(get_current_employee)
):
    """Obtiene todas las marcas"""
    if active_only:
        brands = await Brand.get_active_brands()
    else:
        brands = await Brand.find_all().sort("name").to_list()

    return {
        "success": True,
        "count": len(brands),
        "brands": [brand.to_dict() for brand in brands]
    }


@router.get("/{brand_id}", status_code=status.HTTP_200_OK)
async def get_brand(
    brand_id: str,
    current_user: Employee = Depends(get_current_employee)
):
    """Obtiene una marca por ID"""
    brand = await Brand.get(brand_id)

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca no encontrada"
        )

    return {
        "success": True,
        "brand": brand.to_dict()
    }


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_brand(
    name: str,
    code: Optional[str] = None,
    description: Optional[str] = None,
    current_user: Employee = Depends(get_current_employee)
):
    """Crea una nueva marca"""

    # Verificar que no exista una marca con el mismo nombre
    existing = await Brand.find_by_name(name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una marca con el nombre '{name}'"
        )

    # Verificar código si se proporciona
    if code:
        existing_code = await Brand.find_by_code(code)
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una marca con el código '{code}'"
            )

    # Crear marca
    brand = Brand(
        name=name,
        code=code,
        description=description,
        created_by=str(current_user.id) if current_user.id else None
    )

    await brand.insert()

    return {
        "success": True,
        "message": "Marca creada exitosamente",
        "brand": brand.to_dict()
    }


@router.put("/{brand_id}", status_code=status.HTTP_200_OK)
async def update_brand(
    brand_id: str,
    name: Optional[str] = None,
    code: Optional[str] = None,
    description: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: Employee = Depends(get_current_employee)
):
    """Actualiza una marca existente"""

    brand = await Brand.get(brand_id)

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca no encontrada"
        )

    # Verificar nombre si se proporciona
    if name and name != brand.name:
        existing = await Brand.find_by_name(name)
        if existing and str(existing.id) != brand_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una marca con el nombre '{name}'"
            )
        brand.name = name

    # Verificar código si se proporciona
    if code and code != brand.code:
        existing_code = await Brand.find_by_code(code)
        if existing_code and str(existing_code.id) != brand_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una marca con el código '{code}'"
            )
        brand.code = code

    if description is not None:
        brand.description = description

    if is_active is not None:
        brand.is_active = is_active

    brand.updated_at = datetime.utcnow()
    await brand.save()

    return {
        "success": True,
        "message": "Marca actualizada exitosamente",
        "brand": brand.to_dict()
    }


@router.delete("/{brand_id}", status_code=status.HTTP_200_OK)
async def delete_brand(
    brand_id: str,
    current_user: Employee = Depends(get_current_employee)
):
    """Desactiva una marca (soft delete)"""

    brand = await Brand.get(brand_id)

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca no encontrada"
        )

    brand.is_active = False
    brand.updated_at = datetime.utcnow()
    await brand.save()

    return {
        "success": True,
        "message": "Marca desactivada exitosamente"
    }


@router.post("/initialize-defaults", status_code=status.HTTP_200_OK)
async def initialize_default_brands(
    current_user: Employee = Depends(get_current_employee)
):
    """Inicializa las marcas por defecto si no existen"""

    default_brands = [
        {"name": "NEOWAY", "code": "NEOWAY", "description": "Módulos y dispositivos Neoway"},
        {"name": "QUECTEL", "code": "QUECTEL", "description": "Módulos y dispositivos Quectel"},
        {"name": "FIBOCOM", "code": "FIBOCOM", "description": "Módulos y dispositivos Fibocom"},
        {"name": "SIMCOM", "code": "SIMCOM", "description": "Módulos y dispositivos SIMCOM"},
        {"name": "TELIT", "code": "TELIT", "description": "Módulos y dispositivos Telit"},
        {"name": "SIERRA WIRELESS", "code": "SIERRA", "description": "Módulos y dispositivos Sierra Wireless"},
        {"name": "U-BLOX", "code": "UBLOX", "description": "Módulos y dispositivos u-blox"},
        {"name": "OTROS", "code": "OTROS", "description": "Otras marcas"},
    ]

    created_count = 0
    existing_count = 0

    for brand_data in default_brands:
        existing = await Brand.find_by_name(brand_data["name"])
        if not existing:
            brand = Brand(
                name=brand_data["name"],
                code=brand_data["code"],
                description=brand_data["description"],
                created_by=str(current_user.id) if current_user.id else None
            )
            await brand.insert()
            created_count += 1
        else:
            existing_count += 1

    return {
        "success": True,
        "message": f"Marcas inicializadas: {created_count} creadas, {existing_count} ya existían",
        "created": created_count,
        "existing": existing_count
    }
