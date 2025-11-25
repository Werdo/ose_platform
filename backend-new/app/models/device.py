"""
OSE Platform - Device Model
Modelo principal para gestión de dispositivos IoT/GPS
CORREGIDO según documentación oficial
"""

from beanie import Document
from pydantic import Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EstadoDispositivo(str, Enum):
    """Estados del ciclo de vida del dispositivo"""
    EN_PRODUCCION = "en_produccion"
    CONTROL_CALIDAD = "control_calidad"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    EMPAQUETADO = "empaquetado"
    ENVIADO = "enviado"
    ACTIVO = "activo"  # En servicio
    DEFECTUOSO = "defectuoso"
    RMA = "rma"
    REEMPLAZADO = "reemplazado"
    RETIRADO = "retirado"


class Device(Document):
    """
    Modelo principal de dispositivo
    Registro maestro de cada dispositivo único (IMEI/CCID)
    """

    # ════════════════════════════════════════════════════════════════════
    # IDENTIFICACIÓN ÚNICA
    # ════════════════════════════════════════════════════════════════════

    imei: str = Field(
        ...,
        description="IMEI del dispositivo (15 dígitos)",
        min_length=15,
        max_length=15,
        index=True
    )

    ccid: Optional[str] = Field(
        default=None,
        description="ICCID de la tarjeta SIM (19-22 dígitos)",
        min_length=19,
        max_length=22,
        index=True
    )

    # ════════════════════════════════════════════════════════════════════
    # OPERADOR (inferido del ICCID)
    # ════════════════════════════════════════════════════════════════════

    operador: Optional[str] = Field(
        default=None,
        description="Operador de telefonía (inferido del ICCID)",
        index=True
    )

    operador_marca: Optional[str] = Field(
        default=None,
        description="Marca comercial del operador"
    )

    operador_pais: Optional[str] = Field(
        default=None,
        description="País del operador"
    )

    operador_region: Optional[str] = Field(
        default=None,
        description="Región del operador (Global, Europa, etc.)"
    )

    iin_prefix: Optional[str] = Field(
        default=None,
        description="Prefijo IIN del ICCID (6-8 dígitos)",
        index=True
    )

    operador_uso: Optional[str] = Field(
        default=None,
        description="Tipo de uso (IoT, M2M, Consumer, etc.)"
    )

    operador_red: Optional[str] = Field(
        default=None,
        description="Tipo de red (LTE-M, NB-IoT, 2G/3G/4G, etc.)"
    )

    operador_actualizado: Optional[datetime] = Field(
        default=None,
        description="Fecha de última actualización de información del operador"
    )

    # ════════════════════════════════════════════════════════════════════
    # PRODUCCIÓN
    # ════════════════════════════════════════════════════════════════════

    nro_orden: Optional[str] = Field(
        default=None,
        description="Número de orden de producción",
        index=True
    )

    lote: Optional[int] = Field(
        default=None,
        description="Número de lote dentro de la orden"
    )

    linea: Optional[int] = Field(
        default=None,
        description="Línea de producción (1, 2, 3)",
        ge=1,
        le=3
    )

    puesto: Optional[int] = Field(
        default=None,
        description="Puesto de trabajo (1, 2)"
    )

    # ════════════════════════════════════════════════════════════════════
    # PRODUCTO
    # ════════════════════════════════════════════════════════════════════

    marca: str = Field(
        default="Neoway",
        description="Marca del dispositivo (Neoway, CARLITE, OversunTrack, etc.)"
    )

    nro_referencia: Optional[str] = Field(
        default=None,
        description="Número de referencia del modelo"
    )

    sku: Optional[str] = Field(
        default=None,
        description="SKU del producto"
    )

    # ════════════════════════════════════════════════════════════════════
    # ESTADO Y UBICACIÓN
    # ════════════════════════════════════════════════════════════════════

    estado: EstadoDispositivo = Field(
        default=EstadoDispositivo.EN_PRODUCCION,
        description="Estado actual del dispositivo",
        index=True
    )

    ubicacion_actual: Optional[str] = Field(
        default=None,
        description="Ubicación física actual"
    )

    # ════════════════════════════════════════════════════════════════════
    # EMPAQUETADO Y LOGÍSTICA
    # ════════════════════════════════════════════════════════════════════

    # JERARQUÍA DE PICKING (PALLET → CARTON → DEVICE)
    package_no: Optional[str] = Field(
        default=None,
        description="Número de caja/paquete/cartón (CARTON_ID)",
        alias="carton_id",
        index=True
    )

    pallet_id: Optional[str] = Field(
        default=None,
        description="ID del pallet que contiene el cartón",
        index=True
    )

    factory_id: Optional[int] = Field(
        default=None,
        description="ID de la fábrica de producción"
    )

    package_date: Optional[datetime] = Field(
        default=None,
        description="Fecha de empaquetado"
    )

    codigo_innerbox: Optional[str] = Field(
        default=None,
        description="Código de caja intermedia/expositora"
    )

    codigo_unitario: Optional[str] = Field(
        default=None,
        description="Código individual/QR del dispositivo"
    )

    num_deposito: Optional[str] = Field(
        default=None,
        description="Número de depósito"
    )

    # ════════════════════════════════════════════════════════════════════
    # CLIENTE (SEGÚN DOCUMENTACIÓN)
    # ════════════════════════════════════════════════════════════════════

    cliente: Optional[str] = Field(
        default=None,
        description="ID del cliente asignado (ObjectId como string)",
        index=True
    )

    cliente_codigo: Optional[str] = Field(
        default=None,
        description="Código del cliente (denormalizado)"
    )

    cliente_nombre: Optional[str] = Field(
        default=None,
        description="Nombre del cliente (denormalizado)"
    )

    # ════════════════════════════════════════════════════════════════════
    # NOTIFICACIÓN (APP 1)
    # ════════════════════════════════════════════════════════════════════

    notificado: bool = Field(
        default=False,
        description="Si se notificó al cliente (App 1)",
        index=True
    )

    fecha_notificacion: Optional[datetime] = Field(
        default=None,
        description="Fecha de notificación al cliente"
    )

    # ════════════════════════════════════════════════════════════════════
    # GARANTÍA
    # ════════════════════════════════════════════════════════════════════

    garantia: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "fecha_inicio": None,
            "fecha_fin": None,
            "duracion_meses": 12,
            "tipo": "fabricante",
            "activa": False
        },
        description="Información de garantía"
    )

    # ════════════════════════════════════════════════════════════════════
    # ENVÍO
    # ════════════════════════════════════════════════════════════════════

    info_envio: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Información de envío"
    )

    # ════════════════════════════════════════════════════════════════════
    # VALIDACIÓN
    # ════════════════════════════════════════════════════════════════════

    valido: bool = Field(
        default=True,
        description="Si el dispositivo pasó todas las validaciones"
    )

    errores: Optional[list] = Field(
        default_factory=list,
        description="Lista de errores de validación"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Campos adicionales personalizados"
    )

    # ════════════════════════════════════════════════════════════════════
    # AUDITORÍA
    # ════════════════════════════════════════════════════════════════════

    fecha_creacion: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha de creación/registro",
        index=True
    )

    fecha_actualizacion: datetime = Field(
        default_factory=datetime.utcnow,
        description="Última actualización"
    )

    creado_por: Optional[str] = Field(
        default=None,
        description="Operador que creó el registro"
    )

    fecha_importacion: Optional[datetime] = Field(
        default=None,
        description="Fecha de importación (si fue importado)"
    )

    # ════════════════════════════════════════════════════════════════════
    # CONFIGURACIÓN DE BEANIE
    # ════════════════════════════════════════════════════════════════════

    class Settings:
        name = "devices"
        indexes = [
            "imei",  # Unique
            "ccid",
            "nro_orden",
            "estado",
            "cliente",
            "package_no",
            "notificado",
            "fecha_creacion",
            "operador",  # Nuevo: búsqueda por operador
            "iin_prefix",  # Nuevo: búsqueda por IIN
            [("imei", 1), ("estado", 1)],
            [("nro_orden", 1), ("lote", 1)],
            [("cliente", 1), ("estado", 1)],
            [("notificado", 1), ("cliente", 1)],
            [("operador", 1), ("estado", 1)],  # Nuevo: dispositivos por operador
            [("iin_prefix", 1), ("operador", 1)]  # Nuevo: análisis por IIN
        ]

    # ════════════════════════════════════════════════════════════════════
    # VALIDADORES
    # ════════════════════════════════════════════════════════════════════

    @validator('imei')
    def validate_imei(cls, v):
        """Valida que el IMEI sea numérico de 15 dígitos"""
        v = v.strip()
        if not v.isdigit():
            raise ValueError('IMEI debe contener solo dígitos')
        if len(v) != 15:
            raise ValueError('IMEI debe tener exactamente 15 dígitos')
        return v

    @validator('ccid')
    def validate_ccid(cls, v):
        """Valida que el CCID sea numérico de 19-22 dígitos"""
        if v is None:
            return v
        v = v.strip()
        if not v.isdigit():
            raise ValueError('CCID debe contener solo dígitos')
        if not (19 <= len(v) <= 22):
            raise ValueError('CCID debe tener entre 19 y 22 dígitos')
        return v

    # ════════════════════════════════════════════════════════════════════
    # PROPIEDADES
    # ════════════════════════════════════════════════════════════════════

    @property
    def numero_serie(self) -> str:
        """Retorna el número de serie completo (IMEI + CCID)"""
        if self.ccid:
            return f"{self.imei} {self.ccid}"
        return self.imei

    @property
    def esta_bajo_garantia(self) -> bool:
        """Verifica si el dispositivo está bajo garantía"""
        if not self.garantia or not self.garantia.get('activa'):
            return False

        fecha_fin = self.garantia.get('fecha_fin')
        if not fecha_fin:
            return False

        return datetime.utcnow() < fecha_fin

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ════════════════════════════════════════════════════════════════════

    async def marcar_como_notificado(
        self,
        cliente_id: str,
        cliente_nombre: str,
        cliente_codigo: str,
        ubicacion: Optional[str] = None,
        operador: Optional[str] = None
    ):
        """
        Marca el dispositivo como notificado (App 1)
        Según especificación de la documentación
        """
        self.notificado = True
        self.cliente = cliente_id
        self.cliente_nombre = cliente_nombre
        self.cliente_codigo = cliente_codigo
        self.fecha_notificacion = datetime.utcnow()
        self.estado = EstadoDispositivo.ACTIVO

        if ubicacion:
            self.ubicacion_actual = ubicacion

        self.fecha_actualizacion = datetime.utcnow()
        await self.save()

        # Crear evento en device_events
        from app.models.device_event import DeviceEvent

        event = DeviceEvent(
            device_id=str(self.id),
            imei=self.imei,
            event_type="notified_to_client",  # Según documentación
            timestamp=datetime.utcnow(),
            operator=operador,
            cliente=cliente_id,
            data={
                "cliente_nombre": cliente_nombre,
                "cliente_codigo": cliente_codigo,
                "ubicacion": ubicacion
            }
        )
        await event.insert()

    async def actualizar_operador_desde_iccid(self) -> bool:
        """
        Actualiza la información del operador desde el ICCID usando el analizador

        Returns:
            bool: True si se actualizó la información, False si no hay ICCID o no se encontró IIN
        """
        if not self.ccid:
            return False

        from app.utils.iccid_analyzer import analyze_iccid

        try:
            # Analizar el ICCID
            result = analyze_iccid(self.ccid)

            # Si hay perfil de IIN, actualizar los campos
            if result.get("iin_profile"):
                profile = result["iin_profile"]

                self.operador = profile.get("operator")
                self.operador_marca = profile.get("brand")
                self.operador_pais = profile.get("country")
                self.operador_region = profile.get("region")
                self.iin_prefix = result.get("iin_prefix")
                self.operador_uso = profile.get("use_case")
                self.operador_red = profile.get("core_network")
                self.operador_actualizado = datetime.utcnow()

                await self.save()
                return True

        except Exception as e:
            # Log del error pero no falla
            import logging
            logging.error(f"Error al actualizar operador para device {self.imei}: {e}")

        return False

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def buscar_por_imei(imei: str) -> Optional["Device"]:
        """Busca un dispositivo por IMEI"""
        return await Device.find_one(Device.imei == imei.strip())

    @staticmethod
    async def buscar_por_ccid(ccid: str) -> Optional["Device"]:
        """Busca un dispositivo por CCID"""
        return await Device.find_one(Device.ccid == ccid.strip())

    @staticmethod
    async def buscar_por_paquete(package_no: str):
        """Busca todos los dispositivos de un paquete"""
        return await Device.find(Device.package_no == package_no.strip()).to_list()

    @staticmethod
    async def buscar_por_orden(nro_orden: str):
        """Busca todos los dispositivos de una orden de producción"""
        return await Device.find(Device.nro_orden == nro_orden.strip()).to_list()
