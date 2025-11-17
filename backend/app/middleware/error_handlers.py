"""
OSE Platform - Error Handlers
Manejadores centralizados de errores para FastAPI
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pymongo.errors import DuplicateKeyError, PyMongoError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════
# EXCEPTION HANDLERS
# ════════════════════════════════════════════════════════════════════════

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Maneja HTTPException de forma uniforme

    Retorna:
        {
            "success": false,
            "error": {
                "code": "HTTP_404",
                "message": "Not Found",
                "detail": "Resource not found"
            }
        }
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": _get_status_message(exc.status_code),
                "detail": str(exc.detail)
            }
        },
        headers=exc.headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Maneja errores de validación de Pydantic

    Retorna:
        {
            "success": false,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": [
                    {
                        "field": "email",
                        "message": "Invalid email format",
                        "type": "value_error.email"
                    }
                ]
            }
        }
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"][1:])  # Skip 'body'
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(f"Validation error on {request.url.path}: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": errors
            }
        }
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """
    Maneja errores de validación de Pydantic en modelos
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Data validation failed",
                "details": errors
            }
        }
    )


async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyError):
    """
    Maneja errores de clave duplicada en MongoDB

    Retorna:
        {
            "success": false,
            "error": {
                "code": "DUPLICATE_KEY",
                "message": "Resource already exists",
                "detail": "A resource with this value already exists"
            }
        }
    """
    # Extraer campo del error si es posible
    error_msg = str(exc)
    field = "unknown"

    if "index:" in error_msg:
        # Ejemplo: "E11000 duplicate key error collection: ose.devices index: imei_1 dup key: { imei: \"123456789012345\" }"
        try:
            index_part = error_msg.split("index:")[1].split("dup key")[0].strip()
            field = index_part.split("_")[0]
        except:
            pass

    logger.warning(f"Duplicate key error on {request.url.path}: field={field}")

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "error": {
                "code": "DUPLICATE_KEY",
                "message": "Resource already exists",
                "detail": f"A resource with this {field} already exists"
            }
        }
    )


async def pymongo_exception_handler(request: Request, exc: PyMongoError):
    """
    Maneja errores generales de MongoDB
    """
    logger.error(f"MongoDB error on {request.url.path}: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Database operation failed",
                "detail": "An error occurred while processing your request"
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Maneja excepciones no capturadas

    Registra el error completo y retorna respuesta genérica al cliente
    """
    logger.error(
        f"Unhandled exception on {request.url.path}: {type(exc).__name__}: {exc}",
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "detail": "An unexpected error occurred. Please try again later."
            }
        }
    )


# ════════════════════════════════════════════════════════════════════════
# CUSTOM EXCEPTIONS
# ════════════════════════════════════════════════════════════════════════

class BusinessLogicError(Exception):
    """
    Error de lógica de negocio

    Uso:
        raise BusinessLogicError("Cannot approve RMA without inspection")
    """

    def __init__(self, message: str, code: str = "BUSINESS_LOGIC_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


async def business_logic_exception_handler(request: Request, exc: BusinessLogicError):
    """
    Maneja errores de lógica de negocio
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": "Business rule violation",
                "detail": exc.message
            }
        }
    )


class ResourceNotFoundError(Exception):
    """
    Error cuando un recurso no existe

    Uso:
        raise ResourceNotFoundError("Device", imei="123456789012345")
    """

    def __init__(self, resource_type: str, **identifiers):
        self.resource_type = resource_type
        self.identifiers = identifiers
        identifier_str = ", ".join(f"{k}={v}" for k, v in identifiers.items())
        self.message = f"{resource_type} not found: {identifier_str}"
        super().__init__(self.message)


async def resource_not_found_exception_handler(request: Request, exc: ResourceNotFoundError):
    """
    Maneja errores de recurso no encontrado
    """
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "success": False,
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": f"{exc.resource_type} not found",
                "detail": exc.message
            }
        }
    )


class PermissionDeniedError(Exception):
    """
    Error cuando el usuario no tiene permisos

    Uso:
        raise PermissionDeniedError("You don't have access to this production line")
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


async def permission_denied_exception_handler(request: Request, exc: PermissionDeniedError):
    """
    Maneja errores de permisos denegados
    """
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "success": False,
            "error": {
                "code": "PERMISSION_DENIED",
                "message": "Access denied",
                "detail": exc.message
            }
        }
    )


# ════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════

def _get_status_message(status_code: int) -> str:
    """Obtiene el mensaje para un status code"""
    messages = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        409: "Conflict",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
        502: "Bad Gateway",
        503: "Service Unavailable",
    }
    return messages.get(status_code, "Error")


# ════════════════════════════════════════════════════════════════════════
# REGISTRO DE EXCEPTION HANDLERS
# ════════════════════════════════════════════════════════════════════════

def register_exception_handlers(app):
    """
    Registra todos los exception handlers en la app FastAPI

    Usage:
        from app.middleware.error_handlers import register_exception_handlers
        app = FastAPI()
        register_exception_handlers(app)
    """
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(DuplicateKeyError, duplicate_key_exception_handler)
    app.add_exception_handler(PyMongoError, pymongo_exception_handler)
    app.add_exception_handler(BusinessLogicError, business_logic_exception_handler)
    app.add_exception_handler(ResourceNotFoundError, resource_not_found_exception_handler)
    app.add_exception_handler(PermissionDeniedError, permission_denied_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    logger.info("Exception handlers registered successfully")
