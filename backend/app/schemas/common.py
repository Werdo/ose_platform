"""
OSE Platform - Common Schemas
Schemas base y comunes para toda la API
"""

from typing import Generic, TypeVar, Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime


# ════════════════════════════════════════════════════════════════════════
# RESPONSE WRAPPERS
# ════════════════════════════════════════════════════════════════════════

T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """
    Respuesta exitosa estándar

    Example:
        {
            "success": true,
            "data": {...}
        }
    """
    success: bool = True
    data: T


class ErrorDetail(BaseModel):
    """Detalle de un error"""
    code: str
    message: str
    detail: Optional[str] = None
    field: Optional[str] = None


class ErrorResponse(BaseModel):
    """
    Respuesta de error estándar

    Example:
        {
            "success": false,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input",
                "detail": "Email is required"
            }
        }
    """
    success: bool = False
    error: ErrorDetail


class MessageResponse(BaseModel):
    """
    Respuesta simple con mensaje

    Example:
        {
            "success": true,
            "message": "Operation completed successfully"
        }
    """
    success: bool = True
    message: str


# ════════════════════════════════════════════════════════════════════════
# PAGINATION
# ════════════════════════════════════════════════════════════════════════

class PaginationParams(BaseModel):
    """
    Parámetros de paginación para queries

    Example query params:
        ?page=1&page_size=50
    """
    page: int = Field(default=1, ge=1, description="Número de página (1-indexed)")
    page_size: int = Field(default=50, ge=1, le=500, description="Elementos por página")

    @property
    def skip(self) -> int:
        """Calcula el offset para MongoDB"""
        return (self.page - 1) * self.page_size


class PaginationMeta(BaseModel):
    """
    Metadata de paginación en responses

    Example:
        {
            "total": 250,
            "page": 1,
            "page_size": 50,
            "total_pages": 5,
            "has_next": true,
            "has_prev": false
        }
    """
    total: int = Field(..., description="Total de elementos")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Elementos por página")
    total_pages: int = Field(..., description="Total de páginas")
    has_next: bool = Field(..., description="Hay página siguiente")
    has_prev: bool = Field(..., description="Hay página anterior")

    @classmethod
    def create(cls, total: int, page: int, page_size: int) -> "PaginationMeta":
        """Helper para crear metadata de paginación"""
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return cls(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Respuesta paginada estándar

    Example:
        {
            "success": true,
            "data": [...],
            "meta": {
                "total": 250,
                "page": 1,
                "page_size": 50,
                ...
            }
        }
    """
    success: bool = True
    data: List[T]
    meta: PaginationMeta


# ════════════════════════════════════════════════════════════════════════
# FILTERING Y SORTING
# ════════════════════════════════════════════════════════════════════════

class SortParams(BaseModel):
    """
    Parámetros de ordenamiento

    Example query params:
        ?sort_by=created_at&sort_order=desc
    """
    sort_by: str = Field(default="created_at", description="Campo para ordenar")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Orden: asc o desc")

    @property
    def mongo_sort(self) -> List[tuple]:
        """Convierte a formato MongoDB sort"""
        direction = 1 if self.sort_order == "asc" else -1
        return [(self.sort_by, direction)]


class DateRangeFilter(BaseModel):
    """
    Filtro por rango de fechas

    Example query params:
        ?date_from=2025-01-01&date_to=2025-01-31
    """
    date_from: Optional[datetime] = Field(None, description="Fecha desde (inclusive)")
    date_to: Optional[datetime] = Field(None, description="Fecha hasta (inclusive)")


# ════════════════════════════════════════════════════════════════════════
# FILE UPLOAD
# ════════════════════════════════════════════════════════════════════════

class FileInfo(BaseModel):
    """Información de un archivo"""
    filename: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class FileUploadResponse(BaseModel):
    """Respuesta de upload de archivo"""
    success: bool = True
    file_id: str
    filename: str
    url: Optional[str] = None


# ════════════════════════════════════════════════════════════════════════
# BULK OPERATIONS
# ════════════════════════════════════════════════════════════════════════

class BulkOperationResult(BaseModel):
    """
    Resultado de operación masiva

    Example:
        {
            "success": true,
            "total": 100,
            "succeeded": 95,
            "failed": 5,
            "errors": [...]
        }
    """
    success: bool = True
    total: int = Field(..., description="Total de operaciones intentadas")
    succeeded: int = Field(..., description="Operaciones exitosas")
    failed: int = Field(..., description="Operaciones fallidas")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Detalles de errores")


# ════════════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ════════════════════════════════════════════════════════════════════════

class HealthStatus(BaseModel):
    """Status de health check"""
    status: str = Field(..., description="healthy, degraded, unhealthy")
    version: str = Field(..., description="Versión de la API")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database: Dict[str, Any] = Field(..., description="Estado de la base de datos")
    services: Dict[str, Any] = Field(default_factory=dict, description="Estado de servicios externos")


# ════════════════════════════════════════════════════════════════════════
# STATISTICS
# ════════════════════════════════════════════════════════════════════════

class StatisticsResponse(BaseModel):
    """Respuesta de estadísticas genérica"""
    period: str = Field(..., description="Período: daily, weekly, monthly")
    date_from: datetime
    date_to: datetime
    data: Dict[str, Any]
