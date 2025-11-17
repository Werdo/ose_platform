"""
OSE Platform - PDF Service
Servicio para generación de PDFs usando WeasyPrint y Jinja2
"""

# Try to import WeasyPrint, fallback to simple PDF if not available
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False
    print("WARNING: WeasyPrint not available. Using simple PDF generation.")

from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from app.config import settings
from app.services.qr_service import qr_service

logger = logging.getLogger(__name__)


class PDFService:
    """
    Servicio de generación de PDFs
    Usa WeasyPrint para renderizar HTML a PDF
    Usa Jinja2 para templates
    """

    def __init__(self):
        # Configurar Jinja2 para templates de PDFs
        template_path = Path(settings.TEMPLATES_DIR) / "pdfs"
        if template_path.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(template_path)),
                autoescape=True
            )
        else:
            self.jinja_env = None
            logger.warning(f"PDF templates directory not found: {template_path}")

        # Configurar Jinja2 para etiquetas
        labels_path = Path(settings.TEMPLATES_DIR) / "etiquetas"
        if labels_path.exists():
            self.jinja_labels = Environment(
                loader=FileSystemLoader(str(labels_path)),
                autoescape=True
            )
        else:
            self.jinja_labels = None
            logger.warning(f"Labels templates directory not found: {labels_path}")

        # Configurar Jinja2 para facturas
        invoices_path = Path(settings.TEMPLATES_DIR) / "invoices"
        if invoices_path.exists():
            self.jinja_invoices = Environment(
                loader=FileSystemLoader(str(invoices_path)),
                autoescape=True
            )
            # Añadir filtros personalizados
            self.jinja_invoices.filters['format_currency'] = self._format_currency
        else:
            self.jinja_invoices = None
            logger.warning(f"Invoices templates directory not found: {invoices_path}")

    def generate_pdf_from_html(
        self,
        html_content: str,
        css_content: Optional[str] = None
    ) -> bytes:
        """
        Genera un PDF desde HTML

        Args:
            html_content: Contenido HTML
            css_content: CSS adicional (opcional)

        Returns:
            bytes: PDF generado
        """
        try:
            # Crear CSS por defecto
            default_css = CSS(string=f"""
                @page {{
                    size: {settings.PDF_PAGE_SIZE};
                    margin: {settings.PDF_MARGIN};
                }}
                body {{
                    font-family: {settings.PDF_FONT_FAMILY};
                    font-size: 12pt;
                }}
            """)

            # Verificar si WeasyPrint está disponible
            if not WEASYPRINT_AVAILABLE:
                # Fallback: crear un PDF simple con texto plano
                logger.warning("WeasyPrint not available, generating simple PDF")
                simple_pdf = f"PDF Content (WeasyPrint not available)\n\n{html_content[:500]}...".encode('utf-8')
                return simple_pdf

            # Si hay CSS adicional, agregarlo
            stylesheets = [default_css]
            if css_content:
                stylesheets.append(CSS(string=css_content))

            # Generar PDF
            html = HTML(string=html_content)
            pdf = html.write_pdf(stylesheets=stylesheets)

            logger.info("PDF generated successfully from HTML")
            return pdf

        except Exception as e:
            logger.error(f"Error generating PDF from HTML: {e}")
            raise

    def generate_pdf_from_template(
        self,
        template_name: str,
        data: Dict[str, Any],
        css_content: Optional[str] = None
    ) -> bytes:
        """
        Genera un PDF desde un template Jinja2

        Args:
            template_name: Nombre del template (ej: "reporte_produccion.html")
            data: Diccionario con datos para el template
            css_content: CSS adicional (opcional)

        Returns:
            bytes: PDF generado
        """
        if not self.jinja_env:
            raise RuntimeError("Jinja environment not initialized")

        try:
            # Renderizar template
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**data)

            # Generar PDF
            return self.generate_pdf_from_html(html_content, css_content)

        except Exception as e:
            logger.error(f"Error generating PDF from template: {e}")
            raise

    def generate_device_label(
        self,
        imei: str,
        ccid: Optional[str] = None,
        marca: Optional[str] = None,
        referencia: Optional[str] = None,
        orden: Optional[str] = None,
        lote: Optional[int] = None,
        include_qr: bool = True
    ) -> bytes:
        """
        Genera una etiqueta para un dispositivo

        Args:
            imei: IMEI del dispositivo
            ccid: CCID de la SIM (opcional)
            marca: Marca del dispositivo (opcional)
            referencia: Referencia del producto (opcional)
            orden: Número de orden de producción (opcional)
            lote: Número de lote (opcional)
            include_qr: Si incluir código QR (default: True)

        Returns:
            bytes: PDF con la etiqueta
        """
        if not self.jinja_labels:
            raise RuntimeError("Labels Jinja environment not initialized")

        try:
            # Generar QR si se solicita
            qr_base64 = None
            if include_qr:
                qr_bytes = qr_service.generate_device_qr(imei=imei, ccid=ccid)
                import base64
                qr_base64 = base64.b64encode(qr_bytes).decode()

            # Preparar datos para el template
            data = {
                "imei": imei,
                "ccid": ccid or "N/A",
                "marca": marca or "OversunTrack",
                "referencia": referencia or "N/A",
                "orden": orden or "",
                "lote": lote or "",
                "qr_base64": qr_base64,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "company_name": settings.COMPANY_NAME
            }

            # Renderizar template
            template = self.jinja_labels.get_template("etiqueta_dispositivo.html")
            html_content = template.render(**data)

            # CSS específico para etiquetas
            label_css = """
                @page {
                    size: 80mm 48mm;
                    margin: 2mm;
                }
                body {
                    font-family: Arial, sans-serif;
                    font-size: 8pt;
                    margin: 0;
                    padding: 2mm;
                }
                .qr-code {
                    width: 35mm;
                    height: 35mm;
                }
            """

            # Generar PDF
            return self.generate_pdf_from_html(html_content, label_css)

        except Exception as e:
            logger.error(f"Error generating device label: {e}")
            raise

    def generate_package_label(
        self,
        package_no: str,
        quantity: int,
        orden: Optional[str] = None,
        destino: Optional[str] = None
    ) -> bytes:
        """
        Genera una etiqueta para un paquete/caja

        Args:
            package_no: Número de paquete (25 dígitos)
            quantity: Cantidad de dispositivos en el paquete
            orden: Número de orden de producción (opcional)
            destino: Cliente o destino (opcional)

        Returns:
            bytes: PDF con la etiqueta
        """
        if not self.jinja_labels:
            raise RuntimeError("Labels Jinja environment not initialized")

        try:
            # Generar QR del paquete
            qr_bytes = qr_service.generate_package_qr(package_no)
            import base64
            qr_base64 = base64.b64encode(qr_bytes).decode()

            # Preparar datos
            data = {
                "package_no": package_no,
                "quantity": quantity,
                "orden": orden or "N/A",
                "destino": destino or "Almacén",
                "qr_base64": qr_base64,
                "fecha": datetime.now().strftime("%Y-%m-%d"),
                "company_name": settings.COMPANY_NAME
            }

            # Renderizar template
            template = self.jinja_labels.get_template("etiqueta_paquete.html")
            html_content = template.render(**data)

            # CSS para etiquetas de paquete (más grande)
            label_css = """
                @page {
                    size: 100mm 100mm;
                    margin: 3mm;
                }
                body {
                    font-family: Arial, sans-serif;
                    font-size: 10pt;
                    margin: 0;
                    padding: 3mm;
                }
                .qr-code {
                    width: 60mm;
                    height: 60mm;
                }
            """

            return self.generate_pdf_from_html(html_content, label_css)

        except Exception as e:
            logger.error(f"Error generating package label: {e}")
            raise

    def generate_production_report(
        self,
        order_number: str,
        order_data: Dict[str, Any],
        devices: List[Dict[str, Any]],
        stats: Dict[str, Any]
    ) -> bytes:
        """
        Genera un reporte de producción

        Args:
            order_number: Número de orden de producción
            order_data: Datos de la orden
            devices: Lista de dispositivos producidos
            stats: Estadísticas de la orden

        Returns:
            bytes: PDF del reporte
        """
        if not self.jinja_env:
            raise RuntimeError("Jinja environment not initialized")

        try:
            data = {
                "order_number": order_number,
                "order": order_data,
                "devices": devices,
                "stats": stats,
                "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "company_name": settings.COMPANY_NAME
            }

            return self.generate_pdf_from_template(
                template_name="reporte_produccion.html",
                data=data
            )

        except Exception as e:
            logger.error(f"Error generating production report: {e}")
            raise

    def generate_customer_report(
        self,
        customer_data: Dict[str, Any],
        devices: List[Dict[str, Any]],
        summary: Dict[str, Any]
    ) -> bytes:
        """
        Genera un reporte de cliente (App 1)

        Args:
            customer_data: Datos del cliente
            devices: Lista de dispositivos del cliente
            summary: Resumen/estadísticas

        Returns:
            bytes: PDF del reporte
        """
        if not self.jinja_env:
            raise RuntimeError("Jinja environment not initialized")

        try:
            data = {
                "customer": customer_data,
                "devices": devices,
                "summary": summary,
                "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "company_name": settings.COMPANY_NAME
            }

            return self.generate_pdf_from_template(
                template_name="reporte_cliente.html",
                data=data
            )

        except Exception as e:
            logger.error(f"Error generating customer report: {e}")
            raise

    def generate_quality_report(
        self,
        inspection_data: Dict[str, Any],
        defects: List[Dict[str, Any]]
    ) -> bytes:
        """
        Genera un reporte de control de calidad

        Args:
            inspection_data: Datos de la inspección
            defects: Lista de defectos encontrados

        Returns:
            bytes: PDF del reporte
        """
        if not self.jinja_env:
            raise RuntimeError("Jinja environment not initialized")

        try:
            data = {
                "inspection": inspection_data,
                "defects": defects,
                "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "company_name": settings.COMPANY_NAME
            }

            return self.generate_pdf_from_template(
                template_name="reporte_calidad.html",
                data=data
            )

        except Exception as e:
            logger.error(f"Error generating quality report: {e}")
            raise

    # ════════════════════════════════════════════════════════════════════════
    # UTILITY METHODS
    # ════════════════════════════════════════════════════════════════════════

    def _format_currency(self, value: float) -> str:
        """Formatea un valor como moneda"""
        return f"{value:.2f} €"

    def _prepare_invoice_template_data(
        self,
        invoice_data: Dict[str, Any],
        logo_base64: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Prepara los datos de la factura para la plantilla Jinja2

        Args:
            invoice_data: Datos de la factura
            logo_base64: Logo en base64 (opcional)

        Returns:
            Dict con datos formateados para la plantilla
        """
        # Formatear fecha
        invoice_date = invoice_data.get('invoice_date', datetime.utcnow())
        if isinstance(invoice_date, str):
            invoice_date = datetime.fromisoformat(invoice_date.replace('Z', '+00:00'))
        fecha_str = invoice_date.strftime("%d/%m/%Y")

        # Logo
        company_logo_url = None
        if logo_base64:
            company_logo_url = f"data:image/png;base64,{logo_base64}"
        elif invoice_data.get('company_logo_url'):
            company_logo_url = invoice_data.get('company_logo_url')

        # Extraer números de tickets si existen
        ticket_numbers = []
        if invoice_data.get('tickets'):
            ticket_numbers = [t.get('ticket_number') for t in invoice_data.get('tickets', [])]

        # Preparar datos para la plantilla
        template_data = {
            # Configuración de color
            'primary_color': invoice_data.get('template_primary_color', '#1976d2'),
            'secondary_color': invoice_data.get('template_secondary_color', '#424242'),

            # Datos de la empresa
            'company_name': invoice_data.get('company_name', ''),
            'company_nif': invoice_data.get('company_nif', ''),
            'company_address': invoice_data.get('company_address', ''),
            'company_city': invoice_data.get('company_city', ''),
            'company_postal_code': invoice_data.get('company_postal_code', ''),
            'company_phone': invoice_data.get('company_phone', ''),
            'company_email': invoice_data.get('company_email', ''),
            'company_website': invoice_data.get('company_website', ''),
            'company_logo_url': company_logo_url,

            # Datos de la factura
            'invoice_number': invoice_data.get('invoice_number', ''),
            'invoice_series': invoice_data.get('invoice_series', 'F'),
            'invoice_date': fecha_str,
            'invoice_due_date': invoice_data.get('invoice_due_date', ''),

            # Datos del cliente
            'customer_name': invoice_data.get('customer_name', ''),
            'customer_nif': invoice_data.get('customer_nif', ''),
            'customer_address': invoice_data.get('customer_address', ''),
            'customer_city': invoice_data.get('customer_city', ''),
            'customer_postal_code': invoice_data.get('customer_postal_code', ''),
            'customer_phone': invoice_data.get('customer_phone', ''),
            'customer_email': invoice_data.get('customer_email', ''),

            # Tickets asociados
            'ticket_numbers': ticket_numbers,

            # Líneas de factura
            'lines': invoice_data.get('lines', []),

            # Totales
            'subtotal': invoice_data.get('subtotal', 0.0),
            'tax_rate': invoice_data.get('tax_rate', 21.0),
            'tax_total': invoice_data.get('tax_total', 0.0),
            'total': invoice_data.get('total', 0.0),

            # Información de pago
            'payment_terms': invoice_data.get('payment_terms', 'Pago al contado'),
            'bank_account': invoice_data.get('bank_account', ''),
            'payment_reference': invoice_data.get('payment_reference', ''),

            # Footer
            'footer_text': invoice_data.get('footer_text', 'Gracias por su confianza'),
            'legal_notice': invoice_data.get('legal_notice', ''),

            # Notas
            'notes': invoice_data.get('notes', ''),
        }

        return template_data

    # ════════════════════════════════════════════════════════════════════════
    # APP 5: GENERACIÓN DE FACTURAS
    # ════════════════════════════════════════════════════════════════════════

    def generate_invoice_pdf(
        self,
        invoice_data: Dict[str, Any],
        logo_base64: Optional[str] = None,
        template_name: str = "invoice_default.html"
    ) -> bytes:
        """
        Genera un PDF de factura profesional usando plantilla Jinja2

        Args:
            invoice_data: Datos completos de la factura
            logo_base64: Logo de la empresa en base64 (opcional)
            template_name: Nombre de la plantilla a usar (default: invoice_default.html)

        Returns:
            bytes: PDF de la factura
        """
        try:
            # Si tenemos el entorno de Jinja para facturas, usar la plantilla
            if self.jinja_invoices:
                logger.info(f"Generating invoice PDF using template: {template_name}")

                # Preparar datos para la plantilla
                template_data = self._prepare_invoice_template_data(invoice_data, logo_base64)

                # Renderizar template
                template = self.jinja_invoices.get_template(template_name)
                html_content = template.render(**template_data)
            else:
                # Fallback: generar HTML inline
                logger.warning("Invoice templates not available, using inline HTML")
                html_content = self._generate_invoice_html(invoice_data, logo_base64)

            # CSS específico para facturas
            invoice_css = """
                @page {
                    size: A4;
                    margin: 20mm;
                }
                body {
                    font-family: Arial, Helvetica, sans-serif;
                    font-size: 11pt;
                    color: #333;
                    line-height: 1.4;
                }
                .invoice-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #1976d2;
                    padding-bottom: 15px;
                }
                .company-info {
                    width: 60%;
                }
                .invoice-info {
                    width: 35%;
                    text-align: right;
                }
                .logo {
                    max-width: 150px;
                    max-height: 80px;
                    margin-bottom: 10px;
                }
                .section-title {
                    font-size: 14pt;
                    font-weight: bold;
                    color: #1976d2;
                    margin-top: 20px;
                    margin-bottom: 10px;
                }
                .customer-billing {
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                .invoice-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                .invoice-table th {
                    background-color: #1976d2;
                    color: white;
                    padding: 10px;
                    text-align: left;
                    font-weight: bold;
                }
                .invoice-table td {
                    padding: 10px;
                    border-bottom: 1px solid #ddd;
                }
                .invoice-table tr:nth-child(even) {
                    background-color: #f9f9f9;
                }
                .totals-section {
                    margin-top: 20px;
                    text-align: right;
                }
                .totals-table {
                    margin-left: auto;
                    width: 300px;
                }
                .totals-table td {
                    padding: 5px 10px;
                }
                .total-row {
                    font-weight: bold;
                    font-size: 14pt;
                    color: #1976d2;
                    border-top: 2px solid #1976d2;
                }
                .footer {
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ddd;
                    font-size: 9pt;
                    color: #666;
                    text-align: center;
                }
                .text-right {
                    text-align: right;
                }
                .text-center {
                    text-align: center;
                }
            """

            # Generar PDF
            return self.generate_pdf_from_html(html_content, invoice_css)

        except Exception as e:
            logger.error(f"Error generating invoice PDF: {e}")
            raise

    def _generate_invoice_html(
        self,
        invoice_data: Dict[str, Any],
        logo_base64: Optional[str] = None
    ) -> str:
        """
        Genera el HTML de la factura

        Args:
            invoice_data: Datos de la factura
            logo_base64: Logo en base64

        Returns:
            HTML string
        """
        # Formatear fecha
        invoice_date = invoice_data.get('invoice_date', datetime.utcnow())
        if isinstance(invoice_date, str):
            invoice_date = datetime.fromisoformat(invoice_date.replace('Z', '+00:00'))
        fecha_str = invoice_date.strftime("%d/%m/%Y")

        # Logo
        logo_html = ""
        if logo_base64:
            logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="logo" />'
        elif invoice_data.get('company_logo_url'):
            logo_html = f'<img src="{invoice_data.get("company_logo_url")}" class="logo" />'

        # Construir HTML
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Factura {invoice_data.get('invoice_number', '')}</title>
        </head>
        <body>
            <!-- HEADER -->
            <div class="invoice-header">
                <div class="company-info">
                    {logo_html}
                    <h1 style="margin: 0; color: #1976d2;">{invoice_data.get('company_name', 'Empresa')}</h1>
                    <p style="margin: 5px 0;">
                        <strong>NIF:</strong> {invoice_data.get('company_nif', '')}<br>
                        {invoice_data.get('company_address', '')}<br>
                        {invoice_data.get('company_postal_code', '')} {invoice_data.get('company_city', '')}<br>
                        Tel: {invoice_data.get('company_phone', '')}<br>
                        Email: {invoice_data.get('company_email', '')}
                    </p>
                </div>
                <div class="invoice-info">
                    <h2 style="margin: 0; color: #1976d2;">FACTURA</h2>
                    <p style="margin: 10px 0;">
                        <strong>Nº:</strong> {invoice_data.get('invoice_number', '')}<br>
                        <strong>Fecha:</strong> {fecha_str}<br>
                        <strong>Serie:</strong> {invoice_data.get('invoice_series', 'F')}
                    </p>
                </div>
            </div>

            <!-- DATOS DEL CLIENTE -->
            <div class="section-title">DATOS DEL CLIENTE</div>
            <div class="customer-billing">
                <p style="margin: 5px 0;">
                    <strong>{invoice_data.get('customer_name', '')}</strong><br>
                    NIF/CIF: {invoice_data.get('customer_nif', 'No proporcionado')}<br>
                    {invoice_data.get('customer_address', '')}<br>
                    {invoice_data.get('customer_postal_code', '')} {invoice_data.get('customer_city', '')}<br>
                    Email: {invoice_data.get('customer_email', '')}
                </p>
            </div>

            <!-- LÍNEAS DE FACTURA -->
            <div class="section-title">DETALLE</div>
            <table class="invoice-table">
                <thead>
                    <tr>
                        <th style="width: 50%;">Descripción</th>
                        <th style="width: 10%; text-align: center;">Cant.</th>
                        <th style="width: 15%; text-align: right;">P. Unit.</th>
                        <th style="width: 10%; text-align: center;">IVA %</th>
                        <th style="width: 15%; text-align: right;">Total</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Añadir líneas
        for line in invoice_data.get('lines', []):
            html += f"""
                    <tr>
                        <td>{line.get('description', '')}</td>
                        <td class="text-center">{line.get('quantity', 0)}</td>
                        <td class="text-right">{line.get('unit_price', 0):.2f} €</td>
                        <td class="text-center">{line.get('tax_rate', 21)}%</td>
                        <td class="text-right">{line.get('total', 0):.2f} €</td>
                    </tr>
            """

        # Totales
        subtotal = invoice_data.get('subtotal', 0.0)
        tax_total = invoice_data.get('tax_total', 0.0)
        total = invoice_data.get('total', 0.0)

        html += f"""
                </tbody>
            </table>

            <!-- TOTALES -->
            <div class="totals-section">
                <table class="totals-table">
                    <tr>
                        <td><strong>Subtotal:</strong></td>
                        <td class="text-right">{subtotal:.2f} €</td>
                    </tr>
                    <tr>
                        <td><strong>IVA:</strong></td>
                        <td class="text-right">{tax_total:.2f} €</td>
                    </tr>
                    <tr class="total-row">
                        <td><strong>TOTAL:</strong></td>
                        <td class="text-right">{total:.2f} €</td>
                    </tr>
                </table>
            </div>
        """

        # Notas y condiciones
        if invoice_data.get('notes') or invoice_data.get('payment_terms'):
            html += '<div style="margin-top: 30px;">'
            if invoice_data.get('payment_terms'):
                html += f'<p><strong>Condiciones de pago:</strong> {invoice_data.get("payment_terms")}</p>'
            if invoice_data.get('notes'):
                html += f'<p><strong>Notas:</strong> {invoice_data.get("notes")}</p>'
            html += '</div>'

        # Footer
        footer_text = invoice_data.get('footer_text', '')
        if not footer_text:
            footer_text = "Gracias por su confianza"

        html += f"""
            <!-- FOOTER -->
            <div class="footer">
                <p>{footer_text}</p>
                <p style="font-size: 8pt; color: #999;">
                    Documento generado electrónicamente - {datetime.now().strftime("%d/%m/%Y %H:%M")}
                </p>
            </div>
        </body>
        </html>
        """

        return html


# Singleton instance
pdf_service = PDFService()
