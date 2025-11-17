"""
OSE Platform - QR Code Service
Servicio para generación de códigos QR
"""

import qrcode
from qrcode.image.pil import PilImage
from io import BytesIO
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class QRService:
    """
    Servicio de generación de códigos QR
    Usa la librería qrcode con PIL
    """

    def __init__(self):
        self.default_version = 1  # Tamaño del QR (1 = más pequeño, 40 = más grande)
        self.default_error_correction = qrcode.constants.ERROR_CORRECT_L
        self.default_box_size = 10  # Tamaño de cada "caja" del QR en pixels
        self.default_border = 4  # Grosor del borde en cajas

    def generate_qr(
        self,
        data: str,
        version: Optional[int] = None,
        error_correction: Optional[int] = None,
        box_size: Optional[int] = None,
        border: Optional[int] = None,
        fill_color: str = "black",
        back_color: str = "white"
    ) -> bytes:
        """
        Genera un código QR y lo retorna como bytes (PNG)

        Args:
            data: Datos a codificar en el QR
            version: Versión del QR (1-40, None = auto)
            error_correction: Nivel de corrección de errores
                             (ERROR_CORRECT_L, M, Q, H)
            box_size: Tamaño de cada caja en pixels
            border: Grosor del borde en cajas
            fill_color: Color del QR (ej: "black", "#000000")
            back_color: Color del fondo (ej: "white", "#FFFFFF")

        Returns:
            bytes: Imagen PNG del código QR
        """
        try:
            # Crear objeto QR
            qr = qrcode.QRCode(
                version=version or self.default_version,
                error_correction=error_correction or self.default_error_correction,
                box_size=box_size or self.default_box_size,
                border=border or self.default_border,
            )

            # Añadir datos
            qr.add_data(data)
            qr.make(fit=True)

            # Generar imagen
            img = qr.make_image(
                fill_color=fill_color,
                back_color=back_color,
                image_factory=PilImage
            )

            # Convertir a bytes
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            logger.info(f"QR code generated successfully for data length: {len(data)}")
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            raise

    def generate_device_qr(
        self,
        imei: str,
        ccid: Optional[str] = None,
        device_id: Optional[str] = None
    ) -> bytes:
        """
        Genera un QR para un dispositivo (IMEI + CCID)

        Args:
            imei: IMEI del dispositivo
            ccid: CCID de la SIM (opcional)
            device_id: ID interno del dispositivo (opcional)

        Returns:
            bytes: Imagen PNG del código QR
        """
        # Formato del QR: IMEI|CCID|DEVICE_ID
        data_parts = [imei]

        if ccid:
            data_parts.append(ccid)
        else:
            data_parts.append("")

        if device_id:
            data_parts.append(device_id)

        data = "|".join(data_parts)

        return self.generate_qr(
            data=data,
            error_correction=qrcode.constants.ERROR_CORRECT_M
        )

    def generate_package_qr(self, package_no: str) -> bytes:
        """
        Genera un QR para un paquete/caja

        Args:
            package_no: Número de paquete (25 dígitos)

        Returns:
            bytes: Imagen PNG del código QR
        """
        # Formato del QR: PKG:XXXXXXXXXXXXXXXXXXXXXX
        data = f"PKG:{package_no}"

        return self.generate_qr(
            data=data,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12
        )

    def generate_batch_qr(
        self,
        order_number: str,
        batch_number: int,
        line: Optional[int] = None
    ) -> bytes:
        """
        Genera un QR para un lote de producción

        Args:
            order_number: Número de orden de producción
            batch_number: Número de lote
            line: Línea de producción (opcional)

        Returns:
            bytes: Imagen PNG del código QR
        """
        # Formato del QR: BATCH:ORDER_NUMBER:BATCH_NO:LINE
        data = f"BATCH:{order_number}:{batch_number}"

        if line:
            data += f":{line}"

        return self.generate_qr(
            data=data,
            error_correction=qrcode.constants.ERROR_CORRECT_M
        )

    def generate_url_qr(self, url: str, size: Optional[int] = None) -> bytes:
        """
        Genera un QR para una URL

        Args:
            url: URL completa
            size: Tamaño del box_size (opcional, default 10)

        Returns:
            bytes: Imagen PNG del código QR
        """
        return self.generate_qr(
            data=url,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size or 10
        )

    def generate_vcard_qr(
        self,
        name: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        company: Optional[str] = None,
        url: Optional[str] = None
    ) -> bytes:
        """
        Genera un QR con vCard (tarjeta de contacto)

        Args:
            name: Nombre completo
            phone: Teléfono (opcional)
            email: Email (opcional)
            company: Empresa (opcional)
            url: Sitio web (opcional)

        Returns:
            bytes: Imagen PNG del código QR
        """
        # Formato vCard 3.0
        vcard = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"FN:{name}",
        ]

        if phone:
            vcard.append(f"TEL:{phone}")

        if email:
            vcard.append(f"EMAIL:{email}")

        if company:
            vcard.append(f"ORG:{company}")

        if url:
            vcard.append(f"URL:{url}")

        vcard.append("END:VCARD")

        data = "\n".join(vcard)

        return self.generate_qr(
            data=data,
            error_correction=qrcode.constants.ERROR_CORRECT_M
        )

    def generate_wifi_qr(
        self,
        ssid: str,
        password: str,
        security: str = "WPA"
    ) -> bytes:
        """
        Genera un QR para conectarse a WiFi

        Args:
            ssid: Nombre de la red WiFi
            password: Contraseña
            security: Tipo de seguridad (WPA, WEP, nopass)

        Returns:
            bytes: Imagen PNG del código QR
        """
        # Formato WiFi QR: WIFI:T:WPA;S:ssid;P:password;;
        data = f"WIFI:T:{security};S:{ssid};P:{password};;"

        return self.generate_qr(
            data=data,
            error_correction=qrcode.constants.ERROR_CORRECT_H
        )


# Singleton instance
qr_service = QRService()
