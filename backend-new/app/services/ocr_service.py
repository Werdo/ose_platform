"""
OSE Platform - OCR Service
Servicio para procesamiento OCR de tickets de venta
"""

import re
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

# Intentar importar pytesseract
try:
    import pytesseract
    from PIL import Image
    import cv2
    import numpy as np
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    print("WARNING: pytesseract, PIL, or cv2 not available. OCR will use MOCK mode.")
    print("Install with: pip install pytesseract pillow opencv-python")

logger = logging.getLogger(__name__)


class OCRService:
    """
    Servicio para extraer información de tickets usando OCR

    Usa pytesseract para OCR real. Si no está disponible, usa modo MOCK.
    """

    def __init__(self):
        self.confidence_threshold = 0.6
        self.use_real_ocr = PYTESSERACT_AVAILABLE

        if self.use_real_ocr:
            logger.info("OCR Service initialized (REAL mode with pytesseract)")
            # Configurar pytesseract si está en Windows
            # En Linux/Docker generalmente no es necesario
            if os.name == 'nt':  # Windows
                # Intentar encontrar tesseract en las rutas comunes de Windows
                possible_paths = [
                    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        logger.info(f"Tesseract found at: {path}")
                        break
        else:
            logger.warning("OCR Service initialized (MOCK mode - pytesseract not available)")

    def _preprocess_image(self, image_path: str):
        """
        Preprocesa la imagen para mejorar el OCR
        """
        if not PYTESSERACT_AVAILABLE:
            return None

        # Leer imagen
        img = cv2.imread(image_path)

        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Aplicar threshold para mejorar contraste
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # Reducir ruido
        denoised = cv2.fastNlMeansDenoising(thresh)

        return denoised

    async def process_ticket_image(self, image_path: str) -> Dict[str, Any]:
        """
        Procesa una imagen de ticket y extrae información

        Args:
            image_path: Ruta al archivo de imagen

        Returns:
            Dict con la información extraída y confianza del OCR
        """
        try:
            # Si pytesseract está disponible, usar OCR real
            if self.use_real_ocr:
                logger.info(f"Processing ticket image with REAL OCR: {image_path}")

                # Preprocesar imagen
                processed_img = self._preprocess_image(image_path)

                # Extraer texto con pytesseract
                # Usar idioma español si está disponible
                try:
                    text = pytesseract.image_to_string(processed_img, lang='spa')
                except Exception:
                    # Fallback a inglés
                    text = pytesseract.image_to_string(processed_img, lang='eng')

                logger.info(f"OCR extracted text length: {len(text)} chars")

                # Extraer información estructurada
                ticket_number = self._extract_ticket_number(text)
                fecha = self._extract_date(text)
                total = self._extract_total(text)
                lineas = self._extract_products(text)

                # Calcular subtotal e IVA si tenemos el total
                subtotal = 0.0
                iva_importe = 0.0
                if total:
                    # Asumir IVA del 21%
                    subtotal = round(total / 1.21, 2)
                    iva_importe = round(total - subtotal, 2)

                extracted_data = {
                    "ticket_number": ticket_number,
                    "fecha_ticket": fecha or datetime.utcnow(),
                    "lineas": lineas,
                    "subtotal": subtotal,
                    "iva_porcentaje": 21.0,
                    "iva_importe": iva_importe,
                    "total": total or 0.0,
                }

                # Calcular confianza
                confidence = self.calculate_confidence(extracted_data)

                result = {
                    "success": True,
                    "raw_text": text,
                    "confidence": confidence,
                    "extracted_data": extracted_data,
                    "metadata": {
                        "processing_method": "pytesseract",
                        "image_path": image_path,
                        "processed_at": datetime.utcnow().isoformat()
                    }
                }

                return result

            else:
                # MOCK: Simular extracción de datos
                logger.info(f"Processing ticket image (MOCK): {image_path}")

                result = {
                    "success": True,
                    "raw_text": self._generate_mock_text(),
                    "confidence": 0.85,
                    "extracted_data": {
                        "ticket_number": self._extract_ticket_number_mock(),
                        "fecha_ticket": datetime.utcnow(),
                        "establecimiento": "Tienda OSE - Mock",
                        "lineas": self._extract_lines_mock(),
                        "subtotal": 45.45,
                        "iva_porcentaje": 21.0,
                        "iva_importe": 9.54,
                        "total": 54.99,
                        "forma_pago": "TARJETA"
                    },
                    "metadata": {
                        "processing_method": "mock",
                        "image_path": image_path,
                        "processed_at": datetime.utcnow().isoformat()
                    }
                }

                return result

        except Exception as e:
            logger.error(f"Error processing ticket image: {e}")
            return {
                "success": False,
                "error": str(e),
                "raw_text": "",
                "confidence": 0.0,
                "extracted_data": {},
                "metadata": {
                    "processing_method": "error",
                    "image_path": image_path,
                    "error": str(e)
                }
            }

    def _generate_mock_text(self) -> str:
        """Genera texto mock que simula un ticket OCR"""
        return """
        TIENDA OSE
        C/ Ejemplo, 123
        28001 Madrid

        TICKET: TCK-2025-001234
        Fecha: 13/11/2025 14:30

        ---------------------------
        Baliza V16 DGT           1  15.00€
        Cable USB-C              2  10.00€
        Adaptador 12V            1  20.45€

        ---------------------------
        SUBTOTAL:               45.45€
        IVA (21%):               9.54€
        TOTAL:                  54.99€

        PAGO: TARJETA
        ****1234

        GRACIAS POR SU COMPRA
        """

    def _extract_ticket_number_mock(self) -> str:
        """Genera un número de ticket mock"""
        import random
        return f"TCK-2025-{random.randint(100000, 999999):06d}"

    def _extract_lines_mock(self) -> List[Dict[str, Any]]:
        """Extrae líneas de productos (mock)"""
        return [
            {
                "producto": "Baliza V16 DGT",
                "cantidad": 1,
                "precio_unitario": 15.00,
                "total": 15.00
            },
            {
                "producto": "Cable USB-C",
                "cantidad": 2,
                "precio_unitario": 10.00,
                "total": 20.00
            },
            {
                "producto": "Adaptador 12V",
                "cantidad": 1,
                "precio_unitario": 20.45,
                "total": 20.45
            }
        ]

    # ════════════════════════════════════════════════════════════════════════
    # MÉTODOS PARA IMPLEMENTACIÓN REAL CON PYTESSERACT
    # ════════════════════════════════════════════════════════════════════════

    def _extract_ticket_number(self, text: str) -> Optional[str]:
        """
        Extrae el número de ticket del texto OCR
        Patrones comunes: TICKET: XXX, No. XXX, #XXX, etc.
        """
        patterns = [
            r'TICKET[:\s]+([A-Z0-9-]+)',
            r'No\.?\s*([A-Z0-9-]+)',
            r'#\s*([A-Z0-9-]+)',
            r'Nº\s*([A-Z0-9-]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _extract_date(self, text: str) -> Optional[datetime]:
        """
        Extrae la fecha del ticket
        Formatos: DD/MM/YYYY, DD-MM-YYYY, etc.
        """
        patterns = [
            r'(\d{2}[/-]\d{2}[/-]\d{4})',
            r'(\d{2}[/-]\d{2}[/-]\d{2})',
            r'FECHA[:\s]+(\d{2}[/-]\d{2}[/-]\d{4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Intentar parsear diferentes formatos
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue

        return None

    def _extract_total(self, text: str) -> Optional[float]:
        """
        Extrae el total del ticket
        """
        patterns = [
            r'TOTAL[:\s]+(\d+[.,]\d{2})',
            r'IMPORTE[:\s]+(\d+[.,]\d{2})',
            r'A PAGAR[:\s]+(\d+[.,]\d{2})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '.')
                try:
                    return float(amount_str)
                except ValueError:
                    continue

        return None

    def _extract_products(self, text: str) -> List[Dict[str, Any]]:
        """
        Extrae las líneas de productos del ticket
        Esto es muy dependiente del formato del ticket
        """
        products = []

        # Patrón básico: Descripción Cantidad Precio
        # Ejemplo: "Baliza V16    1    15.00"
        pattern = r'(.+?)\s+(\d+)\s+(\d+[.,]\d{2})'

        matches = re.finditer(pattern, text)

        for match in matches:
            description = match.group(1).strip()
            quantity = int(match.group(2))
            price = float(match.group(3).replace(',', '.'))

            # Filtrar líneas que no son productos (totales, etc.)
            if any(keyword in description.upper() for keyword in ['TOTAL', 'IVA', 'SUBTOTAL', 'PAGO']):
                continue

            products.append({
                "producto": description,
                "cantidad": quantity,
                "precio_unitario": price,
                "total": quantity * price
            })

        return products

    def calculate_confidence(self, data: Dict[str, Any]) -> float:
        """
        Calcula la confianza basada en los datos extraídos

        Returns:
            Confianza entre 0.0 y 1.0
        """
        confidence = 0.0
        checks = 0

        # Verificar campos críticos
        if data.get('ticket_number'):
            confidence += 0.3
        checks += 1

        if data.get('fecha_ticket'):
            confidence += 0.2
        checks += 1

        if data.get('total') and data.get('total') > 0:
            confidence += 0.2
        checks += 1

        if data.get('lineas') and len(data.get('lineas', [])) > 0:
            confidence += 0.3
        checks += 1

        return min(confidence, 1.0)


# Instancia global del servicio
ocr_service = OCRService()
