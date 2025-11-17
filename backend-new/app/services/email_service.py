"""
OSE Platform - Email Service
Servicio para envío de emails (facturas, notificaciones, etc.)
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Servicio de envío de emails
    Usa SMTP configurado en settings
    """

    def __init__(self):
        self.smtp_enabled = settings.SMTP_ENABLED
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
        self.smtp_ssl = settings.SMTP_SSL

        self.email_from = settings.EMAIL_FROM
        self.email_from_name = settings.EMAIL_FROM_NAME

        # Configurar Jinja2 para templates de email
        template_path = Path(settings.TEMPLATES_DIR) / "emails"
        if template_path.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(str(template_path)),
                autoescape=True
            )
        else:
            self.jinja_env = None
            logger.warning(f"Email templates directory not found: {template_path}")

        if self.smtp_enabled:
            logger.info(f"Email Service initialized (SMTP: {self.smtp_host}:{self.smtp_port})")
        else:
            logger.warning("Email Service initialized (SMTP DISABLED)")

    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        attachments: Optional[List[dict]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """
        Envía un email

        Args:
            to_email: Email del destinatario
            subject: Asunto del email
            body_html: Cuerpo del email en HTML
            body_text: Cuerpo del email en texto plano (opcional)
            attachments: Lista de archivos adjuntos [{filename, content_bytes}]
            cc: Lista de emails en copia
            bcc: Lista de emails en copia oculta

        Returns:
            bool: True si se envió correctamente
        """
        if not self.smtp_enabled:
            logger.warning(f"SMTP disabled, email not sent to: {to_email}")
            logger.info(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
            return False

        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.email_from_name} <{self.email_from}>"
            msg['To'] = to_email

            if cc:
                msg['Cc'] = ', '.join(cc)
            if bcc:
                msg['Bcc'] = ', '.join(bcc)

            # Añadir cuerpo texto plano
            if body_text:
                part1 = MIMEText(body_text, 'plain', 'utf-8')
                msg.attach(part1)

            # Añadir cuerpo HTML
            part2 = MIMEText(body_html, 'html', 'utf-8')
            msg.attach(part2)

            # Añadir archivos adjuntos
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content_bytes'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    msg.attach(part)

            # Conectar y enviar
            if self.smtp_ssl:
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.smtp_tls:
                    server.starttls()

            # Login
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)

            # Enviar
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)

            server.sendmail(self.email_from, recipients, msg.as_string())
            server.quit()

            logger.info(f"Email sent successfully to: {to_email}")
            return True

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {e}")
            return False

    def send_invoice_email(
        self,
        to_email: str,
        invoice_number: str,
        customer_name: str,
        invoice_pdf_bytes: bytes,
        company_name: str,
        custom_message: Optional[str] = None
    ) -> bool:
        """
        Envía una factura por email

        Args:
            to_email: Email del cliente
            invoice_number: Número de factura
            customer_name: Nombre del cliente
            invoice_pdf_bytes: Bytes del PDF de la factura
            company_name: Nombre de la empresa
            custom_message: Mensaje personalizado (opcional)

        Returns:
            bool: True si se envió correctamente
        """
        try:
            # Asunto
            subject = f"Su factura {invoice_number} de {company_name}"

            # Cuerpo HTML
            if self.jinja_env:
                try:
                    template = self.jinja_env.get_template("invoice_email.html")
                    body_html = template.render(
                        customer_name=customer_name,
                        invoice_number=invoice_number,
                        company_name=company_name,
                        custom_message=custom_message or ""
                    )
                except Exception as e:
                    logger.warning(f"Error loading email template, using default: {e}")
                    body_html = self._generate_default_invoice_email_html(
                        customer_name, invoice_number, company_name, custom_message
                    )
            else:
                body_html = self._generate_default_invoice_email_html(
                    customer_name, invoice_number, company_name, custom_message
                )

            # Cuerpo texto plano
            body_text = f"""
Estimado/a {customer_name},

Adjuntamos su factura {invoice_number}.

{custom_message or ''}

Gracias por su confianza.

Atentamente,
{company_name}
            """.strip()

            # Adjuntar PDF
            attachments = [{
                'filename': f"Factura_{invoice_number}.pdf",
                'content_bytes': invoice_pdf_bytes
            }]

            # Enviar
            return self.send_email(
                to_email=to_email,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                attachments=attachments
            )

        except Exception as e:
            logger.error(f"Error sending invoice email: {e}")
            return False

    def _generate_default_invoice_email_html(
        self,
        customer_name: str,
        invoice_number: str,
        company_name: str,
        custom_message: Optional[str] = None
    ) -> str:
        """
        Genera HTML por defecto para email de factura

        Args:
            customer_name: Nombre del cliente
            invoice_number: Número de factura
            company_name: Nombre de la empresa
            custom_message: Mensaje personalizado

        Returns:
            HTML string
        """
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #1976d2;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            background-color: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 5px 5px;
        }}
        .invoice-number {{
            font-size: 24px;
            font-weight: bold;
            color: #1976d2;
            margin: 20px 0;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 12px;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{company_name}</h1>
    </div>
    <div class="content">
        <p>Estimado/a <strong>{customer_name}</strong>,</p>

        <p>Adjuntamos su factura:</p>

        <div class="invoice-number">{invoice_number}</div>

        {"<p>" + custom_message + "</p>" if custom_message else ""}

        <p>Si tiene alguna pregunta sobre esta factura, no dude en contactarnos.</p>

        <p>Gracias por su confianza.</p>

        <p>Atentamente,<br>
        <strong>{company_name}</strong></p>
    </div>
    <div class="footer">
        <p>Este es un email automático. Por favor, no responda a este mensaje.</p>
    </div>
</body>
</html>
        """.strip()

    def send_ticket_notification_email(
        self,
        to_email: str,
        ticket_number: str,
        customer_name: str,
        status: str,
        company_name: str
    ) -> bool:
        """
        Envía notificación sobre un ticket

        Args:
            to_email: Email del cliente
            ticket_number: Número de ticket
            customer_name: Nombre del cliente
            status: Estado del ticket
            company_name: Nombre de la empresa

        Returns:
            bool: True si se envió correctamente
        """
        try:
            subject = f"Actualización de su ticket {ticket_number}"

            status_messages = {
                "pending": "está pendiente de procesamiento",
                "processing": "está siendo procesado",
                "completed": "ha sido procesado correctamente",
                "rejected": "ha sido rechazado",
                "invoiced": "ha sido facturado"
            }

            status_text = status_messages.get(status, status)

            body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #1976d2;
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .content {{
            background-color: #f9f9f9;
            padding: 30px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{company_name}</h1>
    </div>
    <div class="content">
        <p>Estimado/a <strong>{customer_name}</strong>,</p>

        <p>Le informamos que su ticket <strong>{ticket_number}</strong> {status_text}.</p>

        <p>Puede consultar el estado de sus tickets en nuestro portal.</p>

        <p>Atentamente,<br>
        <strong>{company_name}</strong></p>
    </div>
</body>
</html>
            """.strip()

            body_text = f"Estimado/a {customer_name},\n\nLe informamos que su ticket {ticket_number} {status_text}.\n\nAtentamente,\n{company_name}"

            return self.send_email(
                to_email=to_email,
                subject=subject,
                body_html=body_html,
                body_text=body_text
            )

        except Exception as e:
            logger.error(f"Error sending ticket notification email: {e}")
            return False


# Singleton instance
email_service = EmailService()
