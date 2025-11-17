"""
OSE Platform - Mail Service
Servicio para envío de emails usando aiosmtplib y Jinja2
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from jinja2 import Environment, FileSystemLoader, Template

from app.config import settings

logger = logging.getLogger(__name__)


class MailService:
    """
    Servicio de envío de emails
    Usa aiosmtplib (async) y Jinja2 para templates
    """

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_tls = settings.SMTP_TLS
        self.smtp_ssl = settings.SMTP_SSL
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME

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

    async def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        html: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        reply_to: Optional[str] = None
    ) -> bool:
        """
        Envía un email

        Args:
            to: Lista de destinatarios
            subject: Asunto del email
            body: Cuerpo del email (texto plano)
            html: Cuerpo HTML (opcional)
            cc: Lista de CC (opcional)
            bcc: Lista de BCC (opcional)
            attachments: Lista de archivos adjuntos (opcional)
                         Formato: [{"filename": "file.pdf", "content": bytes, "content_type": "application/pdf"}]
            reply_to: Email de respuesta (opcional)

        Returns:
            bool: True si se envió correctamente, False si no
        """
        if not settings.SMTP_ENABLED:
            logger.warning("SMTP is disabled, email not sent")
            return False

        try:
            # Crear mensaje
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = ", ".join(to)

            if cc:
                message["Cc"] = ", ".join(cc)

            if reply_to:
                message["Reply-To"] = reply_to
            elif settings.EMAIL_REPLY_TO:
                message["Reply-To"] = settings.EMAIL_REPLY_TO

            # Añadir cuerpo (texto plano)
            part_text = MIMEText(body, "plain", "utf-8")
            message.attach(part_text)

            # Añadir cuerpo HTML si existe
            if html:
                part_html = MIMEText(html, "html", "utf-8")
                message.attach(part_html)

            # Añadir archivos adjuntos si existen
            if attachments:
                for attachment in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment["content"])
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachment['filename']}"
                    )
                    message.attach(part)

            # Preparar lista de destinatarios (to + cc + bcc)
            recipients = to.copy()
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)

            # Enviar email
            if self.smtp_tls:
                # Usar STARTTLS
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_user,
                    password=self.smtp_password,
                    start_tls=True,
                    timeout=settings.SMTP_TIMEOUT
                )
            elif self.smtp_ssl:
                # Usar SSL directo
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_user,
                    password=self.smtp_password,
                    use_tls=True,
                    timeout=settings.SMTP_TIMEOUT
                )
            else:
                # Sin encriptación
                await aiosmtplib.send(
                    message,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_user,
                    password=self.smtp_password,
                    timeout=settings.SMTP_TIMEOUT
                )

            logger.info(f"Email sent successfully to {', '.join(to)}")
            return True

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    async def send_template_email(
        self,
        to: List[str],
        subject: str,
        template_name: str,
        template_data: Dict[str, Any],
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Envía un email usando un template Jinja2

        Args:
            to: Lista de destinatarios
            subject: Asunto del email
            template_name: Nombre del template (ej: "notificacion_series.html")
            template_data: Diccionario con datos para el template
            cc: Lista de CC (opcional)
            bcc: Lista de BCC (opcional)
            attachments: Lista de archivos adjuntos (opcional)

        Returns:
            bool: True si se envió correctamente, False si no
        """
        if not self.jinja_env:
            logger.error("Jinja environment not initialized, cannot send template email")
            return False

        try:
            # Renderizar template
            template = self.jinja_env.get_template(template_name)
            html_content = template.render(**template_data)

            # Generar versión texto plano (simplificada)
            # TODO: Mejorar conversión HTML -> texto
            text_content = self._html_to_text(html_content)

            # Enviar email
            return await self.send_email(
                to=to,
                subject=subject,
                body=text_content,
                html=html_content,
                cc=cc,
                bcc=bcc,
                attachments=attachments
            )

        except Exception as e:
            logger.error(f"Error sending template email: {e}")
            return False

    def _html_to_text(self, html: str) -> str:
        """
        Convierte HTML a texto plano (simplificado)
        Para una mejor conversión, usar BeautifulSoup o html2text
        """
        # Por ahora, simplemente remover tags HTML
        import re
        text = re.sub('<[^<]+?>', '', html)
        return text.strip()

    async def send_notification_email(
        self,
        to: str,
        customer_name: str,
        series_count: int,
        series_list: List[str],
        ubicacion: Optional[str] = None
    ) -> bool:
        """
        Envía email de notificación de series (App 1)

        Args:
            to: Email del destinatario
            customer_name: Nombre del cliente
            series_count: Cantidad de series notificadas
            series_list: Lista de IMEIs notificados
            ubicacion: Ubicación de los dispositivos (opcional)

        Returns:
            bool: True si se envió correctamente
        """
        subject = f"Notificación de {series_count} {'serie' if series_count == 1 else 'series'} - OSE Platform"

        template_data = {
            "customer_name": customer_name,
            "series_count": series_count,
            "series_list": series_list,
            "ubicacion": ubicacion or "No especificada",
            "company_name": settings.COMPANY_NAME,
            "support_email": settings.EMAIL_SUPPORT
        }

        return await self.send_template_email(
            to=[to],
            subject=subject,
            template_name="notificacion_series.html",
            template_data=template_data
        )

    async def send_welcome_email(
        self,
        to: str,
        customer_name: str,
        temp_password: Optional[str] = None
    ) -> bool:
        """
        Envía email de bienvenida a nuevo cliente

        Args:
            to: Email del destinatario
            customer_name: Nombre del cliente
            temp_password: Contraseña temporal (opcional)

        Returns:
            bool: True si se envió correctamente
        """
        subject = f"Bienvenido a {settings.COMPANY_NAME}"

        template_data = {
            "customer_name": customer_name,
            "temp_password": temp_password,
            "company_name": settings.COMPANY_NAME,
            "support_email": settings.EMAIL_SUPPORT,
            "portal_url": settings.FRONTEND_URL
        }

        return await self.send_template_email(
            to=[to],
            subject=subject,
            template_name="welcome.html",
            template_data=template_data
        )

    async def send_ticket_notification(
        self,
        to: str,
        ticket_number: str,
        customer_name: str,
        subject_text: str,
        status: str
    ) -> bool:
        """
        Envía email de notificación de ticket (App 3)

        Args:
            to: Email del destinatario
            ticket_number: Número del ticket
            customer_name: Nombre del cliente
            subject_text: Asunto del ticket
            status: Estado del ticket

        Returns:
            bool: True si se envió correctamente
        """
        subject = f"Ticket {ticket_number} - {status}"

        template_data = {
            "ticket_number": ticket_number,
            "customer_name": customer_name,
            "subject_text": subject_text,
            "status": status,
            "company_name": settings.COMPANY_NAME,
            "support_email": settings.EMAIL_SUPPORT
        }

        return await self.send_template_email(
            to=[to],
            subject=subject,
            template_name="ticket_notification.html",
            template_data=template_data
        )


# Singleton instance
mail_service = MailService()
