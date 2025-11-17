# 📄 Documento de Especificaciones

## Aplicación 5 – Generación Automática de Facturas desde Ticket o Chat

---

## 🚀 1. Propósito General

La Aplicación 5 permite generar de forma automática una factura en PDF para un cliente final a partir de:

* Un **número de ticket** ingresado en un portal web
* Una **interacción por chat** (WhatsApp, Telegram, etc.)

El objetivo es simplificar el acceso del cliente a su justificante de compra, garantizando trazabilidad, validez legal y entrega automática.

---

## 🌐 2. Canales de Entrada

### A. Portal Web de Facturación (simple)

* Campo: `Número de ticket`
* Validación: formato y existencia
* Al enviar, genera la factura PDF y permite descarga directa

### B. Bot de Chat (WhatsApp / Telegram)

* Flujo:

  1. Cliente escribe: "Hola, quiero mi factura"
  2. Bot responde: "Envíame tu número de ticket o foto"
  3. El cliente responde con el código o imagen (OCR)
  4. El bot valida y responde con el PDF o enlace

---

## 📓 3. Datos Requeridos para Generar la Factura

| Campo               | Fuente                    | Obligatorio | Comentario                          |
| ------------------- | ------------------------- | ----------- | ----------------------------------- |
| `ticket_number`     | Entrada cliente           | ✅ Sí        | Identificador de la compra          |
| `fecha`             | ticket o sistema          | ✅ Sí        | Fecha de emisión                    |
| `cliente.nombre`    | ticket o enriquecido      | ✅ Sí        | Nombre fiscal                       |
| `cliente.nif`       | si disponible             | Opcional    | NIF/CIF si aplica                   |
| `cliente.email`     | extraído o preguntado     | Opcional    | Para envío automático               |
| `lineas_producto[]` | ticket                    | ✅ Sí        | Productos/servicios incluidos       |
| `importe_total`     | calculado                 | ✅ Sí        | Total factura                       |
| `iva_aplicado`      | definido por regla fiscal | ✅ Sí        | IVA o exento                        |
| `forma_pago`        | predefinido               | Opcional    | "Pago online", "TPV", "Bizum", etc. |

---

## 🔧 4. Estructura de la Factura (PDF)

* Encabezado con logotipo y datos fiscales
* Datos del cliente
* Fecha y número de factura
* Tabla de líneas con:

  * Producto
  * Cantidad
  * Precio unitario
  * Total
* Subtotal + IVA + Total
* Pie con condiciones legales y datos de contacto

> Generado en PDF usando una plantilla HTML+CSS renderizada por `WeasyPrint`, `Puppeteer`, `wkhtmltopdf` o similar.

---

## 💳 5. Fuente de Datos: `tickets` (MongoDB)

```json
{
  "ticket_number": "TCK-2025-0000234",
  "fecha": "2025-11-11T10:25:00Z",
  "cliente": {
    "nombre": "Juan Pérez",
    "nif": "12345678A",
    "email": "juan@email.com"
  },
  "lineas": [
    { "producto": "Baliza V16", "cantidad": 1, "precio_unitario": 15.00 },
    { "producto": "Envió estándar", "cantidad": 1, "precio_unitario": 2.95 }
  ],
  "iva": 21,
  "estado": "facturado"
}
```

---

## 📆 6. API REST

| Método | Ruta                             | Descripción                       |
| ------ | -------------------------------- | --------------------------------- |
| POST   | `/api/factura/generar`           | Genera y retorna el PDF           |
| GET    | `/api/factura/:id`               | Devuelve PDF generado previamente |
| GET    | `/api/factura/verificar/:ticket` | Valida si existe el ticket        |

---

## 📄 7. Integración con Chatbot

* El bot debe:

  * Validar que el mensaje contenga un ticket o una foto
  * Ejecutar `GET /verificar` para confirmar existencia
  * Si existe, llamar a `POST /generar`
  * Enviar el PDF o un enlace seguro

> Opcionalmente puede recoger email si no está disponible en el ticket

---

## 🚪 8. Seguridad y Privacidad

* Verificación de ticket obligatorio
* No mostrar datos si el ticket no existe
* Tokens o firmas en enlaces de descarga
* Opcional: encriptación temporal de factura

---

## 🚀 9. Futuras extensiones

* Firma electrónica en PDF
* Enlace con Hacienda para SII o TicketBAI
* Carga masiva de facturas por lote de tickets
* Exportación a SAGE, Odoo, etc.

---

## 📅 10. Versión y Estado

* Versión: `v1.0.0`
* PDF 100% funcional
* Portal web en desarrollo
* WhatsApp bot compatible
* Integración con `tickets` de base de datos MongoDB

---

## 🔹 11. Referencias

* Colección `tickets` (MongoDB)【101†source】
* Diagramas de integración con chatbot: `DIAGRAMAS.md`【104†source】
* Arquitectura general Mongo: `ARQUITECTURA_MONGODB.md`【101†source】
✅ Documento generado: **App5 Factura Ticket**
