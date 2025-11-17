"""
OSE Platform - Invoice Model
Modelo para facturas generadas
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class InvoiceStatus(str, Enum):
    """Estado de la factura"""
    DRAFT = "draft"  # Borrador
    GENERATED = "generated"  # Generada
    SENT = "sent"  # Enviada al cliente
    PAID = "paid"  # Pagada
    CANCELLED = "cancelled"  # Cancelada


class Invoice(Document):
    """
    Factura generada
    Puede contener uno o múltiples tickets
    """

    # Número de factura (único, correlativo)
    invoice_number: str = Field(..., description="Número de factura único")
    invoice_series: str = Field(default="F", description="Serie de la factura")

    # Fecha
    invoice_date: datetime = Field(default_factory=datetime.utcnow, description="Fecha de emisión")
    due_date: Optional[datetime] = Field(None, description="Fecha de vencimiento")

    # Cliente
    customer_email: str = Field(..., description="Email del cliente")
    customer_name: str = Field(..., description="Nombre del cliente")
    customer_nif: Optional[str] = Field(None, description="NIF/CIF del cliente")
    customer_address: Optional[str] = Field(None, description="Dirección del cliente")
    customer_city: Optional[str] = Field(None, description="Ciudad")
    customer_postal_code: Optional[str] = Field(None, description="Código postal")
    customer_country: str = Field(default="España", description="País")

    # Líneas de factura (productos)
    lines: List[Dict[str, Any]] = Field(default_factory=list, description="Líneas de la factura")
    """
    Cada línea tiene:
    {
        "description": "Baliza V16",
        "quantity": 1,
        "unit_price": 15.00,
        "tax_rate": 21,
        "tax_amount": 3.15,
        "total": 18.15,
        "ticket_number": "TCK-2025-001" (opcional, para trazabilidad)
    }
    """

    # Totales
    subtotal: float = Field(0.0, description="Subtotal sin impuestos")
    tax_total: float = Field(0.0, description="Total de impuestos")
    total: float = Field(0.0, description="Total de la factura")

    # Tickets incluidos
    ticket_ids: List[str] = Field(default_factory=list, description="IDs de tickets incluidos")
    ticket_numbers: List[str] = Field(default_factory=list, description="Números de tickets incluidos")

    # PDF
    pdf_url: Optional[str] = Field(None, description="URL del PDF generado")
    pdf_filename: Optional[str] = Field(None, description="Nombre del archivo PDF")

    # Estado
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT, description="Estado de la factura")

    # Información de la empresa emisora
    company_name: str = Field(..., description="Nombre de la empresa")
    company_nif: str = Field(..., description="NIF/CIF de la empresa")
    company_address: Optional[str] = Field(None, description="Dirección de la empresa")
    company_city: Optional[str] = Field(None, description="Ciudad de la empresa")
    company_postal_code: Optional[str] = Field(None, description="CP de la empresa")
    company_phone: Optional[str] = Field(None, description="Teléfono de la empresa")
    company_email: Optional[str] = Field(None, description="Email de la empresa")
    company_logo_url: Optional[str] = Field(None, description="URL del logo de la empresa")

    # Notas y condiciones
    notes: Optional[str] = Field(None, description="Notas adicionales")
    payment_terms: Optional[str] = Field(None, description="Condiciones de pago")
    footer_text: Optional[str] = Field(None, description="Texto del pie de página")

    # Auditoría
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = Field(None, description="Cuándo se envió al cliente")
    paid_at: Optional[datetime] = Field(None, description="Cuándo se pagó")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "invoices"
        indexes = [
            "invoice_number",
            "customer_email",
            "status",
            "invoice_date",
            "created_at",
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS DE CÁLCULO
    # ════════════════════════════════════════════════════════════════════

    def calculate_totals(self):
        """Calcula los totales de la factura basado en las líneas"""
        self.subtotal = 0.0
        self.tax_total = 0.0

        for line in self.lines:
            quantity = line.get("quantity", 0)
            unit_price = line.get("unit_price", 0)
            tax_rate = line.get("tax_rate", 21)

            line_subtotal = quantity * unit_price
            line_tax = line_subtotal * (tax_rate / 100)
            line_total = line_subtotal + line_tax

            # Actualizar línea
            line["tax_amount"] = round(line_tax, 2)
            line["total"] = round(line_total, 2)

            # Sumar a totales
            self.subtotal += line_subtotal
            self.tax_total += line_tax

        self.subtotal = round(self.subtotal, 2)
        self.tax_total = round(self.tax_total, 2)
        self.total = round(self.subtotal + self.tax_total, 2)

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS DE ESTADO
    # ════════════════════════════════════════════════════════════════════

    def mark_as_generated(self, pdf_url: str, pdf_filename: str):
        """Marca la factura como generada"""
        self.status = InvoiceStatus.GENERATED
        self.pdf_url = pdf_url
        self.pdf_filename = pdf_filename
        self.updated_at = datetime.utcnow()

    def mark_as_sent(self):
        """Marca la factura como enviada"""
        self.status = InvoiceStatus.SENT
        self.sent_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def mark_as_paid(self):
        """Marca la factura como pagada"""
        self.status = InvoiceStatus.PAID
        self.paid_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def cancel(self):
        """Cancela la factura"""
        self.status = InvoiceStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS DE BÚSQUEDA
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def get_by_customer_email(email: str, limit: int = 50):
        """Obtiene las facturas de un cliente"""
        return await Invoice.find(
            Invoice.customer_email == email
        ).sort("-invoice_date").limit(limit).to_list()

    @staticmethod
    async def get_by_invoice_number(invoice_number: str) -> Optional["Invoice"]:
        """Busca una factura por número"""
        return await Invoice.find_one(Invoice.invoice_number == invoice_number)

    @staticmethod
    async def get_latest_invoice_number(series: str) -> Optional[str]:
        """Obtiene el último número de factura de una serie"""
        latest = await Invoice.find(
            Invoice.invoice_series == series
        ).sort("-invoice_number").limit(1).to_list()

        return latest[0].invoice_number if latest else None

    @staticmethod
    async def generate_next_invoice_number(series: str, year: Optional[int] = None) -> str:
        """Genera el siguiente número de factura"""
        if year is None:
            year = datetime.utcnow().year

        # Buscar el último número de esta serie y año
        prefix = f"{series}-{year}-"

        last_invoice = await Invoice.find(
            Invoice.invoice_number.startswith(prefix)  # type: ignore
        ).sort("-invoice_number").limit(1).to_list()

        if last_invoice:
            # Extraer el número secuencial
            last_number = int(last_invoice[0].invoice_number.split("-")[-1])
            next_number = last_number + 1
        else:
            next_number = 1

        # Formatear con ceros a la izquierda
        return f"{prefix}{next_number:06d}"
