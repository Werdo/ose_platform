"""
OSE Platform - SalesTicket Model
Modelo para tickets de venta físicos
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TicketStatus(str, Enum):
    """Estado del ticket"""
    PENDING = "pending"  # Pendiente de facturar
    INVOICED = "invoiced"  # Ya facturado
    REJECTED = "rejected"  # Rechazado (duplicado, inválido, etc.)
    PROCESSING = "processing"  # En proceso de OCR


class TicketLineItem(dict):
    """Línea de producto en el ticket"""
    producto: str
    cantidad: int
    precio_unitario: float
    total: float


class SalesTicket(Document):
    """
    Ticket de venta físico
    Representa un ticket que el cliente sube para generar factura
    """

    # Identificación
    ticket_number: str = Field(..., description="Número único del ticket")

    # Imagen del ticket
    image_url: Optional[str] = Field(None, description="URL de la imagen del ticket")
    image_filename: Optional[str] = Field(None, description="Nombre del archivo de imagen")

    # Datos extraídos (OCR o manual)
    fecha_ticket: Optional[datetime] = Field(None, description="Fecha del ticket")
    establecimiento: Optional[str] = Field(None, description="Nombre del establecimiento")

    # Productos
    lineas: List[Dict[str, Any]] = Field(default_factory=list, description="Líneas de productos")

    # Totales
    subtotal: float = Field(0.0, description="Subtotal sin IVA")
    iva_porcentaje: float = Field(21.0, description="Porcentaje de IVA aplicado")
    iva_importe: float = Field(0.0, description="Importe del IVA")
    total: float = Field(0.0, description="Total del ticket")

    # Forma de pago
    forma_pago: Optional[str] = Field(None, description="Forma de pago (TPV, Efectivo, etc.)")

    # Estado
    status: TicketStatus = Field(default=TicketStatus.PENDING, description="Estado del ticket")

    # Datos del cliente que lo subió
    customer_email: str = Field(..., description="Email del cliente")
    customer_name: Optional[str] = Field(None, description="Nombre del cliente")

    # Datos de facturación (si los proporciona)
    billing_name: Optional[str] = Field(None, description="Nombre fiscal")
    billing_nif: Optional[str] = Field(None, description="NIF/CIF")
    billing_address: Optional[str] = Field(None, description="Dirección fiscal")
    billing_city: Optional[str] = Field(None, description="Ciudad")
    billing_postal_code: Optional[str] = Field(None, description="Código postal")

    # Factura asociada
    invoice_id: Optional[str] = Field(None, description="ID de la factura generada")
    invoice_number: Optional[str] = Field(None, description="Número de factura")

    # OCR
    ocr_confidence: Optional[float] = Field(None, description="Confianza del OCR (0-1)")
    ocr_raw_text: Optional[str] = Field(None, description="Texto raw extraído por OCR")
    manual_entry: bool = Field(False, description="Si los datos fueron ingresados manualmente")

    # Validación
    is_duplicate: bool = Field(False, description="Si es un ticket duplicado")
    duplicate_of: Optional[str] = Field(None, description="ID del ticket original si es duplicado")

    # Auditoría
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(None, description="Cuándo se procesó/facturó")

    # Metadata
    notes: Optional[str] = Field(None, description="Notas adicionales")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "sales_tickets"
        indexes = [
            "ticket_number",
            "customer_email",
            "status",
            "created_at",
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS DE CÁLCULO
    # ════════════════════════════════════════════════════════════════════

    def calculate_totals(self):
        """Calcula los totales del ticket basado en las líneas"""
        self.subtotal = sum(
            line.get("precio_unitario", 0) * line.get("cantidad", 0)
            for line in self.lineas
        )
        self.iva_importe = self.subtotal * (self.iva_porcentaje / 100)
        self.total = self.subtotal + self.iva_importe

    def mark_as_invoiced(self, invoice_id: str, invoice_number: str):
        """Marca el ticket como facturado"""
        self.status = TicketStatus.INVOICED
        self.invoice_id = invoice_id
        self.invoice_number = invoice_number
        self.processed_at = datetime.utcnow()

    def mark_as_duplicate(self, original_ticket_id: str):
        """Marca el ticket como duplicado"""
        self.status = TicketStatus.REJECTED
        self.is_duplicate = True
        self.duplicate_of = original_ticket_id

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS DE VALIDACIÓN
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def check_duplicate(ticket_number: str) -> Optional["SalesTicket"]:
        """Verifica si ya existe un ticket con este número"""
        return await SalesTicket.find_one(
            SalesTicket.ticket_number == ticket_number,
            SalesTicket.status != TicketStatus.REJECTED
        )

    @staticmethod
    async def get_by_customer_email(email: str, status: Optional[TicketStatus] = None):
        """Obtiene todos los tickets de un cliente"""
        query = SalesTicket.customer_email == email
        if status:
            query = query & (SalesTicket.status == status)
        return await SalesTicket.find(query).sort("-created_at").to_list()

    @staticmethod
    async def get_pending_for_invoice(email: str):
        """Obtiene tickets pendientes de un cliente para generar factura"""
        return await SalesTicket.find(
            SalesTicket.customer_email == email,
            SalesTicket.status == TicketStatus.PENDING
        ).sort("created_at").to_list()
