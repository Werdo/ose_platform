"""
OSE Platform - InvoiceConfig Model
Configuración de facturación
"""

from beanie import Document
from pydantic import Field
from typing import Optional, Dict, Any
from datetime import datetime


class InvoiceConfig(Document):
    """
    Configuración global de facturación
    Solo debe existir un documento (singleton)
    """

    # Identificador fijo
    config_id: str = Field(default="default", description="ID fijo para singleton")

    # Serie de facturación
    invoice_series: str = Field(default="F", description="Serie de las facturas")
    next_invoice_number: int = Field(default=1, description="Próximo número de factura")
    reset_yearly: bool = Field(default=True, description="Resetear numeración cada año")

    # Datos de la empresa
    company_name: str = Field(default="", description="Nombre de la empresa")
    company_nif: str = Field(default="", description="NIF/CIF de la empresa")
    company_address: Optional[str] = Field(None, description="Dirección")
    company_city: Optional[str] = Field(None, description="Ciudad")
    company_postal_code: Optional[str] = Field(None, description="Código postal")
    company_phone: Optional[str] = Field(None, description="Teléfono")
    company_email: Optional[str] = Field(None, description="Email")
    company_website: Optional[str] = Field(None, description="Sitio web")

    # Logo
    company_logo_url: Optional[str] = Field(None, description="URL del logo")
    company_logo_filename: Optional[str] = Field(None, description="Nombre del archivo del logo")

    # Configuración de IVA
    default_tax_rate: float = Field(default=21.0, description="Tasa de IVA por defecto (%)")

    # Plantilla de factura
    invoice_template: str = Field(default="default", description="Plantilla a usar (default, modern, classic)")
    template_primary_color: str = Field(default="#1976d2", description="Color primario de la plantilla")
    template_secondary_color: str = Field(default="#424242", description="Color secundario")

    # Textos personalizables
    invoice_footer_text: Optional[str] = Field(None, description="Texto del pie de factura")
    payment_terms: str = Field(
        default="Pago al contado",
        description="Condiciones de pago"
    )
    legal_notice: Optional[str] = Field(None, description="Aviso legal")

    # Configuración de PDF
    pdf_page_size: str = Field(default="A4", description="Tamaño de página (A4, Letter)")
    pdf_orientation: str = Field(default="portrait", description="Orientación (portrait, landscape)")

    # OCR Configuration
    ocr_enabled: bool = Field(default=True, description="Habilitar OCR para tickets")
    ocr_confidence_threshold: float = Field(default=0.6, description="Umbral de confianza del OCR (0-1)")
    allow_manual_entry: bool = Field(default=True, description="Permitir entrada manual de datos")

    # Email configuration
    send_invoice_by_email: bool = Field(default=True, description="Enviar facturas por email automáticamente")
    email_subject_template: str = Field(
        default="Su factura {invoice_number} de {company_name}",
        description="Plantilla del asunto del email"
    )
    email_body_template: Optional[str] = Field(None, description="Plantilla del cuerpo del email")

    # Validación de tickets
    allow_duplicate_tickets: bool = Field(default=False, description="Permitir tickets duplicados")
    auto_reject_duplicates: bool = Field(default=True, description="Rechazar duplicados automáticamente")

    # Auditoría
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_modified_by: Optional[str] = Field(None, description="ID del último usuario que modificó")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Settings:
        name = "invoice_config"
        indexes = [
            "config_id",
        ]

    # ════════════════════════════════════════════════════════════════════
    # MÉTODOS ESTÁTICOS
    # ════════════════════════════════════════════════════════════════════

    @staticmethod
    async def get_config() -> "InvoiceConfig":
        """Obtiene la configuración (singleton)"""
        config = await InvoiceConfig.find_one(InvoiceConfig.config_id == "default")

        if not config:
            # Crear configuración por defecto
            config = InvoiceConfig(config_id="default")
            await config.save()

        return config

    async def increment_invoice_number(self) -> int:
        """Incrementa y retorna el próximo número de factura"""
        current = self.next_invoice_number
        self.next_invoice_number += 1
        self.updated_at = datetime.utcnow()
        await self.save()
        return current

    async def update_company_info(self, data: Dict[str, Any]):
        """Actualiza información de la empresa"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.updated_at = datetime.utcnow()
        await self.save()
