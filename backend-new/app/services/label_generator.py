"""
OSE Platform - Servicio de Generación de Etiquetas
Genera etiquetas en PDF (folios A4) y ZPL (impresoras Zebra)
"""

import io
import barcode
from barcode.writer import ImageWriter
from typing import Dict, Any, List, Optional
from datetime import datetime
import base64

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class LabelGenerator:
    """Generador de etiquetas para palets con códigos EST912"""

    # Configuraciones de tamaños de etiqueta (en mm)
    LABEL_SIZES = {
        "100x150": (100, 150),  # Etiqueta estándar Zebra
        "100x100": (100, 100),  # Etiqueta cuadrada
        "A6": (105, 148),       # A6 para folios
    }

    @staticmethod
    def generate_barcode_image(code: str) -> bytes:
        """
        Genera imagen del código de barras en formato PNG

        Args:
            code: Código a codificar (ej: EST9120000000001)

        Returns:
            bytes: Imagen PNG del código de barras
        """
        # Generar código de barras Code128
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(code, writer=ImageWriter())

        # Generar imagen en memoria
        buffer = io.BytesIO()
        barcode_instance.write(buffer, options={
            'module_width': 0.3,
            'module_height': 15,
            'quiet_zone': 6,
            'font_size': 10,
            'text_distance': 5,
            'write_text': True
        })
        buffer.seek(0)

        return buffer.read()

    @staticmethod
    def generate_pdf_label(
        delivery_note_data: Dict[str, Any],
        labels_count: int = 1,
        label_size: str = "A6"
    ) -> bytes:
        """
        Genera etiquetas en PDF para impresión en folios A4

        Args:
            delivery_note_data: Datos del albarán
            labels_count: Número de etiquetas a generar
            label_size: Tamaño de etiqueta ("100x150", "100x100", "A6")

        Returns:
            bytes: PDF generado
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab no está instalado. Instalar con: pip install reportlab")

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        page_width, page_height = A4

        # Obtener tamaño de etiqueta
        label_width, label_height = LabelGenerator.LABEL_SIZES.get(label_size, (105, 148))
        label_width_pts = label_width * mm
        label_height_pts = label_height * mm

        # Calcular etiquetas por página (2x4 para A6 en A4)
        labels_per_row = 2
        labels_per_col = int(page_height / label_height_pts)

        # Datos del albarán
        pallet_code = delivery_note_data.get("pallet_code", "")
        delivery_note_number = delivery_note_data.get("delivery_note_number", "")
        customer_name = delivery_note_data.get("customer_name", "")
        total_boxes = delivery_note_data.get("total_boxes", 0)
        product_description = delivery_note_data.get("product_description", "")
        pallet_number = delivery_note_data.get("pallet_number_in_order", 1)
        total_pallets = delivery_note_data.get("total_pallets_in_order", 1)
        order_number = delivery_note_data.get("order_number", "")

        # Generar imagen de código de barras
        barcode_img_data = LabelGenerator.generate_barcode_image(pallet_code)

        for label_idx in range(labels_count):
            # Calcular posición de la etiqueta
            col = label_idx % labels_per_row
            row = (label_idx // labels_per_row) % labels_per_col

            # Nueva página si es necesario
            if label_idx > 0 and label_idx % (labels_per_row * labels_per_col) == 0:
                c.showPage()

            # Posición de la etiqueta
            x = col * label_width_pts + 10 * mm
            y = page_height - (row + 1) * label_height_pts

            # Dibuja el título
            c.setFont("Helvetica-Bold", 16)
            c.drawString(x + 5*mm, y + label_height_pts - 10*mm, "OVERSUN ENERGY SL")

            # Línea separadora
            c.line(x + 5*mm, y + label_height_pts - 12*mm, x + label_width_pts - 5*mm, y + label_height_pts - 12*mm)

            # Código de palet (grande y destacado)
            c.setFont("Helvetica-Bold", 14)
            c.drawString(x + 5*mm, y + label_height_pts - 20*mm, f"Código Palet:")
            c.setFont("Helvetica", 12)
            c.drawString(x + 5*mm, y + label_height_pts - 26*mm, pallet_code)

            # Información del albarán
            c.setFont("Helvetica", 9)
            y_pos = y + label_height_pts - 35*mm

            c.drawString(x + 5*mm, y_pos, f"Albarán: {delivery_note_number}")
            y_pos -= 5*mm

            if order_number:
                c.drawString(x + 5*mm, y_pos, f"Pedido: {order_number}")
                y_pos -= 5*mm

            c.drawString(x + 5*mm, y_pos, f"Cliente: {customer_name[:40]}")
            y_pos -= 5*mm

            c.drawString(x + 5*mm, y_pos, f"Total Cajas: {total_boxes}")
            y_pos -= 5*mm

            if product_description:
                c.drawString(x + 5*mm, y_pos, f"Producto: {product_description[:35]}")
                y_pos -= 5*mm

            # Palet X/N
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x + 5*mm, y_pos, f"Palet {pallet_number} de {total_pallets}")
            y_pos -= 8*mm

            # Código de barras (guardamos y cargamos la imagen)
            from PIL import Image as PILImage
            barcode_img = PILImage.open(io.BytesIO(barcode_img_data))

            # Guardar temporalmente
            temp_barcode = io.BytesIO()
            barcode_img.save(temp_barcode, format='PNG')
            temp_barcode.seek(0)

            # Dibujar código de barras
            barcode_width = label_width_pts - 10*mm
            barcode_height = 20*mm
            c.drawImage(temp_barcode, x + 5*mm, y + 15*mm,
                       width=barcode_width, height=barcode_height,
                       preserveAspectRatio=True, mask='auto')

            # Fecha de generación
            c.setFont("Helvetica", 7)
            c.drawString(x + 5*mm, y + 5*mm, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

            # Borde de la etiqueta (para guía de corte)
            c.setStrokeColor(colors.lightgrey)
            c.setDash(2, 2)
            c.rect(x, y, label_width_pts, label_height_pts)

        c.save()
        buffer.seek(0)
        return buffer.read()

    @staticmethod
    def generate_zpl_label(
        delivery_note_data: Dict[str, Any],
        dpi: int = 203,
        label_width: int = 100,
        label_height: int = 150
    ) -> str:
        """
        Genera etiqueta en formato ZPL para impresoras Zebra

        Args:
            delivery_note_data: Datos del albarán
            dpi: DPI de la impresora (203 o 300)
            label_width: Ancho de etiqueta en mm
            label_height: Alto de etiqueta en mm

        Returns:
            str: Código ZPL
        """
        # Convertir mm a dots
        dots_per_mm = dpi / 25.4
        width_dots = int(label_width * dots_per_mm)
        height_dots = int(label_height * dots_per_mm)

        # Datos del albarán
        pallet_code = delivery_note_data.get("pallet_code", "")
        delivery_note_number = delivery_note_data.get("delivery_note_number", "")
        customer_name = delivery_note_data.get("customer_name", "")
        total_boxes = delivery_note_data.get("total_boxes", 0)
        product_description = delivery_note_data.get("product_description", "")
        pallet_number = delivery_note_data.get("pallet_number_in_order", 1)
        total_pallets = delivery_note_data.get("total_pallets_in_order", 1)
        order_number = delivery_note_data.get("order_number", "")

        # Generar código ZPL
        zpl = f"""^XA
^FO50,30^A0N,40,40^FDOVERSUN ENERGY SL^FS
^FO50,80^GB{width_dots-100},2,2^FS

^FO50,100^A0N,35,35^FDCodigo Palet:^FS
^FO50,140^A0N,30,30^FD{pallet_code}^FS

^FO50,200^A0N,25,25^FDAlbaran: {delivery_note_number}^FS
"""

        y_pos = 240
        if order_number:
            zpl += f"^FO50,{y_pos}^A0N,25,25^FDPedido: {order_number}^FS\n"
            y_pos += 40

        zpl += f"^FO50,{y_pos}^A0N,23,23^FDCliente: {customer_name[:30]}^FS\n"
        y_pos += 35

        zpl += f"^FO50,{y_pos}^A0N,23,23^FDCajas: {total_boxes}^FS\n"
        y_pos += 35

        if product_description:
            zpl += f"^FO50,{y_pos}^A0N,20,20^FDProducto: {product_description[:25]}^FS\n"
            y_pos += 35

        zpl += f"^FO50,{y_pos}^A0N,30,30^FDPalet {pallet_number}/{total_pallets}^FS\n"
        y_pos += 50

        # Código de barras Code128
        zpl += f"^FO50,{y_pos}^BY3^BCN,100,Y,N,N^FD{pallet_code}^FS\n"
        y_pos += 120

        # Fecha
        fecha = datetime.now().strftime('%d/%m/%Y %H:%M')
        zpl += f"^FO50,{height_dots-40}^A0N,18,18^FDGenerado: {fecha}^FS\n"

        zpl += "^XZ"

        return zpl

    @staticmethod
    def generate_html_preview(delivery_note_data: Dict[str, Any]) -> str:
        """
        Genera preview HTML de la etiqueta para visualización en navegador

        Args:
            delivery_note_data: Datos del albarán

        Returns:
            str: HTML de la etiqueta
        """
        pallet_code = delivery_note_data.get("pallet_code", "")
        delivery_note_number = delivery_note_data.get("delivery_note_number", "")
        customer_name = delivery_note_data.get("customer_name", "")
        total_boxes = delivery_note_data.get("total_boxes", 0)
        product_description = delivery_note_data.get("product_description", "")
        pallet_number = delivery_note_data.get("pallet_number_in_order", 1)
        total_pallets = delivery_note_data.get("total_pallets_in_order", 1)
        order_number = delivery_note_data.get("order_number", "")

        # Generar código de barras en base64
        barcode_img = LabelGenerator.generate_barcode_image(pallet_code)
        barcode_b64 = base64.b64encode(barcode_img).decode()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Etiqueta {pallet_code}</title>
    <style>
        @page {{
            size: 105mm 148mm;
            margin: 0;
        }}
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        .label {{
            width: 105mm;
            height: 148mm;
            padding: 5mm;
            box-sizing: border-box;
            border: 1px dashed #ccc;
            page-break-after: always;
        }}
        .header {{
            text-align: center;
            font-size: 16pt;
            font-weight: bold;
            margin-bottom: 3mm;
            padding-bottom: 2mm;
            border-bottom: 2px solid #000;
        }}
        .code-title {{
            font-size: 12pt;
            font-weight: bold;
            margin-top: 5mm;
        }}
        .code-value {{
            font-size: 14pt;
            font-weight: bold;
            color: #000;
            margin: 2mm 0;
        }}
        .info {{
            font-size: 9pt;
            margin: 2mm 0;
        }}
        .pallet-number {{
            font-size: 12pt;
            font-weight: bold;
            margin: 4mm 0;
            text-align: center;
        }}
        .barcode {{
            text-align: center;
            margin: 5mm 0;
        }}
        .barcode img {{
            max-width: 95mm;
            height: auto;
        }}
        .footer {{
            font-size: 7pt;
            color: #666;
            margin-top: 3mm;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="label">
        <div class="header">OVERSUN ENERGY SL</div>

        <div class="code-title">Código Palet:</div>
        <div class="code-value">{pallet_code}</div>

        <div class="info">Albarán: {delivery_note_number}</div>
        {"<div class='info'>Pedido: " + order_number + "</div>" if order_number else ""}
        <div class="info">Cliente: {customer_name}</div>
        <div class="info">Total Cajas: {total_boxes}</div>
        {"<div class='info'>Producto: " + product_description + "</div>" if product_description else ""}

        <div class="pallet-number">Palet {pallet_number} de {total_pallets}</div>

        <div class="barcode">
            <img src="data:image/png;base64,{barcode_b64}" alt="Código de barras {pallet_code}">
        </div>

        <div class="footer">Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</div>
    </div>
</body>
</html>
"""
        return html
