"""
OSE Platform - Movimiento Model
Modelo para registros de movimientos logísticos (CRÍTICO para trazabilidad)
"""

from beanie import Document
from pydantic import Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TipoMovimiento(str, Enum):
    """Tipos de movimientos logísticos"""
    ENTRADA = "entrada"  # Recepción de mercancía
    SALIDA = "salida"  # Envío a cliente
    ENVIO = "envio"  # Alias de salida
    TRANSFERENCIA = "transferencia"  # Entre almacenes
    AJUSTE = "ajuste"  # Ajuste de inventario
    DEVOLUCION = "devolucion"  # RMA / Devolución
    PRODUCCION = "produccion"  # Salida de producción
    SCRAP = "scrap"  # Baja por defecto


class Movimiento(Document):
    """
    Registro de movimiento logístico
    Trazabilidad completa de entradas/salidas/transferencias
    """

    # ════════════════════════════════════════════════════════════════════
    # INFORMACIÓN BÁSICA
    # ════════════════════════════════════════════════════════════════════

    tipo: TipoMovimiento = Field(
        ...,
        description="Tipo de movimiento",
        index=True
    )

    fecha: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha del movimiento",
        index=True
    )

    # ════════════════════════════════════════════════════════════════════
    # PRODUCTO / DISPOSITIVO
    # ════════════════════════════════════════════════════════════════════

    producto: Optional[str] = Field(
        default=None,
        description="ID del dispositivo (ObjectId como string)",
        index=True
    )

    imei: Optional[str] = Field(
        default=None,
        description="IMEI del dispositivo (denormalizado para búsqueda rápida)",
        index=True
    )

    ccid: Optional[str] = Field(
        default=None,
        description="ICCID del dispositivo (denormalizado)"
    )

    cantidad: int = Field(
        default=1,
        description="Cantidad de unidades movidas",
        ge=1
    )

    # ════════════════════════════════════════════════════════════════════
    # CLIENTE
    # ════════════════════════════════════════════════════════════════════

    cliente: Optional[str] = Field(
        default=None,
        description="ID del cliente (ObjectId como string)",
        index=True
    )

    cliente_nombre: Optional[str] = Field(
        default=None,
        description="Nombre del cliente (denormalizado)"
    )

    cliente_codigo: Optional[str] = Field(
        default=None,
        description="Código del cliente (denormalizado)"
    )

    # ════════════════════════════════════════════════════════════════════
    # UBICACIONES
    # ════════════════════════════════════════════════════════════════════

    deposito: Optional[str] = Field(
        default=None,
        description="Depósito/almacén origen",
        index=True
    )

    deposito_destino: Optional[str] = Field(
        default=None,
        description="Depósito/almacén destino (para transferencias)"
    )

    ubicacion_origen: Optional[str] = Field(
        default=None,
        description="Ubicación física origen"
    )

    ubicacion_destino: Optional[str] = Field(
        default=None,
        description="Ubicación física destino"
    )

    # ════════════════════════════════════════════════════════════════════
    # DOCUMENTACIÓN
    # ════════════════════════════════════════════════════════════════════

    documento_referencia: Optional[str] = Field(
        default=None,
        description="Número de documento relacionado (factura, albarán, etc.)",
        index=True
    )

    orden_produccion: Optional[str] = Field(
        default=None,
        description="Número de orden de producción relacionada"
    )

    lote: Optional[int] = Field(
        default=None,
        description="Lote de producción"
    )

    # ════════════════════════════════════════════════════════════════════
    # USUARIO Y ORIGEN
    # ════════════════════════════════════════════════════════════════════

    usuario: Optional[str] = Field(
        default=None,
        description="ID del usuario que registró el movimiento",
        index=True
    )

    usuario_nombre: Optional[str] = Field(
        default=None,
        description="Nombre del usuario (denormalizado)"
    )

    origen: str = Field(
        default="manual",
        description="Origen del movimiento (manual, app1, app2, import, etc.)"
    )

    # ════════════════════════════════════════════════════════════════════
    # DETALLES ADICIONALES
    # ════════════════════════════════════════════════════════════════════

    detalles: Optional[str] = Field(
        default=None,
        description="Detalles o notas del movimiento"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Datos adicionales personalizados"
    )

    # ════════════════════════════════════════════════════════════════════
    # COSTOS (opcional)
    # ════════════════════════════════════════════════════════════════════

    costo_unitario: Optional[float] = Field(
        default=None,
        description="Costo unitario del movimiento"
    )

    costo_total: Optional[float] = Field(
        default=None,
        description="Costo total del movimiento"
    )

    moneda: Optional[str] = Field(
        default="EUR",
        description="Moneda del costo"
    )

    # ════════════════════════════════════════════════════════════════════
    # AUDITORÍA
    # ════════════════════════════════════════════════════════════════════

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación del registro",
        index=True
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "movimientos"
        indexes = [
            "tipo",
            "fecha",
            "producto",
            "imei",
            "cliente",
            "deposito",
            "usuario",
            "documento_referencia",
            [("tipo", 1), ("fecha", -1)],
            [("producto", 1), ("fecha", -1)],
            [("cliente", 1), ("fecha", -1)],
            [("deposito", 1), ("fecha", -1)],
            [("usuario", 1), ("fecha", -1)]
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def get_by_device(device_id: str, limit: Optional[int] = None):
        """
        Obtiene los movimientos de un dispositivo específico
        """
        query = Movimiento.find(
            Movimiento.producto == device_id
        ).sort("-fecha")

        if limit:
            return await query.limit(limit).to_list()

        return await query.to_list()

    @staticmethod
    async def get_by_customer(customer_id: str, limit: Optional[int] = None):
        """
        Obtiene movimientos de un cliente específico
        """
        query = Movimiento.find(
            Movimiento.cliente == customer_id
        ).sort("-fecha")

        if limit:
            return await query.limit(limit).to_list()

        return await query.to_list()

    @staticmethod
    async def get_by_type_and_date(
        tipo: TipoMovimiento,
        start_date: datetime,
        end_date: datetime
    ):
        """
        Obtiene movimientos por tipo en un rango de fechas
        """
        return await Movimiento.find(
            Movimiento.tipo == tipo,
            Movimiento.fecha >= start_date,
            Movimiento.fecha <= end_date
        ).sort("-fecha").to_list()

    @staticmethod
    async def count_by_type(start_date: Optional[datetime] = None) -> dict:
        """
        Cuenta movimientos por tipo
        Opcionalmente desde una fecha específica
        """
        query = {}
        if start_date:
            query["fecha"] = {"$gte": start_date}

        movimientos = await Movimiento.find(query).to_list()

        counts = {}
        for mov in movimientos:
            tipo = mov.tipo
            counts[tipo] = counts.get(tipo, 0) + mov.cantidad

        return counts

    @staticmethod
    async def get_by_imei(imei: str, limit: Optional[int] = None):
        """
        Obtiene movimientos por IMEI
        """
        query = Movimiento.find(
            Movimiento.imei == imei
        ).sort("-fecha")

        if limit:
            return await query.limit(limit).to_list()

        return await query.to_list()
