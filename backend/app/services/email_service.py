"""
OSE Platform - Email Service
Servicio para envío de emails con configuración dinámica
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

from app.config import settings, dynamic_config

logger = logging.getLogger(__name__)


class EmailService:
    """
    Servicio de envío de emails
    Soporta configuración desde .env o MongoDB (dinámico)
    """

    def __init__(self):
        self.smtp_client = None

    async def get_config(self) -> Dict[str, Any]:
        """
        Obtiene la configuración de email
        Prioridad: MongoDB > .env > defaults
        """
        return {
            "enabled": await dynamic_config.get("email_enabled", settings.EMAIL_ENABLED),
            "host": await dynamic_config.get("smtp_host", settings.SMTP_HOST),
            "port": await dynamic_config.get("smtp_port", settings.SMTP_PORT),
            "tls": await dynamic_config.get("smtp_tls", settings.SMTP_TLS),
            "ssl": await dynamic_config.get("smtp_ssl", settings.SMTP_SSL),
            "user": await dynamic_config.get("smtp_user", settings.SMTP_USER),
            "password": await dynamic_config.get("smtp_password", settings.SMTP_PASSWORD),
            "timeout": await dynamic_config.get("smtp_timeout", settings.SMTP_TIMEOUT),
            "from": await dynamic_config.get("email_from", settings.EMAIL_FROM),
            "reply_to": await dynamic_config.get("email_reply_to", settings.EMAIL_REPLY_TO),
        }

    async def test_connection(self) -> Dict[str, Any]:
        """
        Prueba la conexión SMTP
        Retorna estado y mensaje
        """
        try:
            config = await self.get_config()

            if not config["enabled"]:
                return {
                    "success": False,
                    "message": "Email service is disabled"
                }

            if not config["host"] or not config["user"] or not config["password"]:
                return {
                    "success": False,
                    "message": "SMTP configuration incomplete"
                }

            # Intentar conexión
            if config["ssl"]:
                smtp = aiosmtplib.SMTP(
                    hostname=config["host"],
                    port=config["port"],
                    use_tls=True,
                    timeout=config["timeout"]
                )
            else:
                smtp = aiosmtplib.SMTP(
                    hostname=config["host"],
                    port=config["port"],
                    timeout=config["timeout"]
                )

            await smtp.connect()

            if config["tls"] and not config["ssl"]:
                await smtp.starttls()

            await smtp.login(config["user"], config["password"])
            await smtp.quit()

            return {
                "success": True,
                "message": f"Successfully connected to {config['host']}:{config['port']}"
            }

        except aiosmtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "message": "Authentication failed. Check SMTP user and password."
            }
        except aiosmtplib.SMTPConnectError:
            return {
                "success": False,
                "message": f"Cannot connect to SMTP server {config.get('host')}:{config.get('port')}"
            }
        except Exception as e:
            logger.error(f"SMTP test connection failed: {e}")
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }

    async def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        html: bool = False,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envía un email

        Args:
            to: Lista de destinatarios
            subject: Asunto del email
            body: Cuerpo del email (texto plano o HTML)
            html: Si el body es HTML
            cc: Lista de CC (opcional)
            bcc: Lista de BCC (opcional)
            attachments: Lista de archivos adjuntos
            reply_to: Email de respuesta (opcional)

        Returns:
            Dict con success y message
        """
        try:
            config = await self.get_config()

            # Verificar que el servicio esté habilitado
            if not config["enabled"]:
                logger.warning("Email service is disabled")
                return {
                    "success": False,
                    "message": "Email service is disabled"
                }

            # Verificar configuración mínima
            if not config["host"] or not config["user"] or not config["password"]:
                logger.error("SMTP configuration incomplete")
                return {
                    "success": False,
                    "message": "SMTP configuration incomplete"
                }

            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = config["from"] or config["user"]
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject

            if reply_to or config["reply_to"]:
                msg['Reply-To'] = reply_to or config["reply_to"]

            if cc:
                msg['Cc'] = ', '.join(cc)

            # Cuerpo del mensaje
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))

            # Adjuntos
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)

            # Enviar
            if config["ssl"]:
                smtp = aiosmtplib.SMTP(
                    hostname=config["host"],
                    port=config["port"],
                    use_tls=True,
                    timeout=config["timeout"]
                )
            else:
                smtp = aiosmtplib.SMTP(
                    hostname=config["host"],
                    port=config["port"],
                    timeout=config["timeout"]
                )

            await smtp.connect()

            if config["tls"] and not config["ssl"]:
                await smtp.starttls()

            await smtp.login(config["user"], config["password"])

            # Destinatarios completos
            recipients = to.copy()
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)

            await smtp.send_message(msg, recipients=recipients)
            await smtp.quit()

            logger.info(f"Email sent successfully to {', '.join(to)}")

            return {
                "success": True,
                "message": f"Email sent to {len(to)} recipient(s)"
            }

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}"
            }

    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """
        Añade un adjunto al mensaje

        attachment debe contener:
        - filename: Nombre del archivo
        - content: Contenido (bytes) o path al archivo
        """
        try:
            filename = attachment.get("filename")
            content = attachment.get("content")
            filepath = attachment.get("filepath")

            if filepath:
                # Leer desde archivo
                with open(filepath, "rb") as f:
                    content = f.read()

            if not content:
                return

            part = MIMEBase("application", "octet-stream")
            part.set_payload(content)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}"
            )

            msg.attach(part)

        except Exception as e:
            logger.error(f"Error adding attachment: {e}")

    async def send_template_email(
        self,
        to: List[str],
        template: str,
        context: Dict[str, Any],
        subject: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Envía un email usando una plantilla

        Args:
            to: Destinatarios
            template: Nombre de la plantilla
            context: Variables para la plantilla
            subject: Asunto del email
            **kwargs: Argumentos adicionales para send_email

        Returns:
            Dict con success y message
        """
        try:
            # Renderizar plantilla (simple string replacement por ahora)
            # TODO: Integrar Jinja2 para plantillas más complejas
            body = self._render_template(template, context)

            return await self.send_email(
                to=to,
                subject=subject,
                body=body,
                html=True,
                **kwargs
            )

        except Exception as e:
            logger.error(f"Failed to send template email: {e}")
            return {
                "success": False,
                "message": f"Failed to send email: {str(e)}"
            }

    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """
        Renderiza una plantilla simple
        TODO: Integrar Jinja2 para plantillas más potentes
        """
        # Por ahora, plantillas simples hardcoded
        templates = {
            "customer_notification": """
                <html>
                <body>
                    <h2>OSE Platform - Notificación de Dispositivos</h2>
                    <p>Estimado cliente,</p>
                    <p>Le informamos que los siguientes dispositivos han sido asignados a su cuenta:</p>
                    <ul>
                        {devices}
                    </ul>
                    <p>Saludos,<br>Equipo de Oversun Energy</p>
                </body>
                </html>
            """,

            "ticket_created": """
                <html>
                <body>
                    <h2>Ticket de Soporte Creado</h2>
                    <p>Número de Ticket: <strong>{ticket_number}</strong></p>
                    <p>Asunto: {subject}</p>
                    <p>Descripción: {description}</p>
                    <p>Prioridad: {priority}</p>
                    <p>Acceda al portal para más detalles.</p>
                </body>
                </html>
            """,

            "rma_approved": """
                <html>
                <body>
                    <h2>RMA Aprobado</h2>
                    <p>Su solicitud RMA ha sido aprobada.</p>
                    <p>Número RMA: <strong>{rma_number}</strong></p>
                    <p>Próximos pasos: {next_steps}</p>
                </body>
                </html>
            """
        }

        template_html = templates.get(template, "")

        # Simple string format
        try:
            return template_html.format(**context)
        except KeyError as e:
            logger.error(f"Missing context variable in template: {e}")
            return template_html


# ════════════════════════════════════════════════════════════════════════
# INSTANCIA GLOBAL Y HELPERS
# ════════════════════════════════════════════════════════════════════════

email_service = EmailService()


async def send_email(**kwargs) -> Dict[str, Any]:
    """Helper function para enviar email"""
    return await email_service.send_email(**kwargs)


async def send_template_email(**kwargs) -> Dict[str, Any]:
    """Helper function para enviar email con plantilla"""
    return await email_service.send_template_email(**kwargs)


async def test_smtp_connection() -> Dict[str, Any]:
    """Helper function para probar conexión SMTP"""
    return await email_service.test_connection()
