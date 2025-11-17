✅ Actualizado el documento **App6 Picking Palets** para incluir también el **modo de picking de paquetería pequeña**, con integración de transportistas (Seur, Correos), tracking, notificación por email y vinculación con el pedido.
# 📄 Documento de Especificaciones

## Aplicación 6 – Gestor de Picking y Etiquetado de Palets y Paquetería

---

## 🚀 1. Propósito General

La Aplicación 6 permite a los operarios de logística:

* Realizar **picking de palets** a partir de lotes, cajas o productos.
* Registrar contenido y vincular con pedidos.
* Generar **etiquetas A4** adhesivas con QR para identificar palets.
* Gestionar **picking de paquetes pequeños** (no paletizados) usando APIs de transporte (Seur, Correos).
* Asociar número de seguimiento y notificar al cliente por email con los dispositivos incluidos.

---

## 🧭 2. Modos de Picking

### A. Picking de Palets (modo logístico)

* Escaneo de lote, caja, unidad o SKU
* Asignación a pedido
* Generación de número de palet
* Impresión de etiqueta A4 con código QR

### B. Picking de Paquetería (modo eCommerce o pequeños envíos)

* Lectura de pedido web y datos del cliente
* Escaneo de dispositivos (IMEIs, cajas)
* Lectura de etiqueta de transporte (número de seguimiento)
* Asignación de transportista (Seur, Correos, etc.)
* Envío de email automático al cliente con:

  * Nº de seguimiento
  * Transportista
  * Productos incluidos

---

## 🔁 3. Flujo Picking Paquetería

```mermaid
flowchart TD
    A[Inicio Picking] --> B[Escaneo de dispositivos]
    B --> C[Asignar a pedido web existente]
    C --> D[Lectura de etiqueta de transporte (tracking)]
    D --> E[Asociar IMEIs a tracking y transportista]
    E --> F[Enviar email al cliente con confirmación de envío]
    F --> G[Registrar evento y estado de envío en MongoDB]
```

---

## 🛠️ 4. Datos adicionales para paquetería

* Número de seguimiento (tracking)
* Transportista (Seur, Correos...)
* Pedido web (orden web)
* Cliente (extraído de pedido)

---

## 🧱 5. Registro MongoDB adicional

### Colección: `packages`

```json
{
  "tracking_number": "CX123456789ES",
  "order_code": "PEDWEB-20251111-0021",
  "cliente": ObjectId("..."),
  "transportista": "Seur",
  "dispositivos": [ObjectId("..."), ObjectId("...")],
  "tipo": "paqueteria",
  "fecha_envio": ISODate("2025-11-11T12:30:00Z"),
  "estado": "preparado"
}
```

---

## ✉️ 6. Envío automático al cliente

* Email con:

  * Nº de pedido
  * Tracking number
  * Nombre del transportista
  * Productos incluidos (IMEIs, descripción, etc.)
  * Enlace de seguimiento (si aplica)

---

## 🔐 7. API REST adicionales

| Método | Ruta                      | Descripción                               |
| ------ | ------------------------- | ----------------------------------------- |
| POST   | `/api/paquetes/nuevo`     | Crear paquete con dispositivos y tracking |
| GET    | `/api/paquetes/:tracking` | Ver detalles de un envío por tracking     |
| POST   | `/api/paquetes/notificar` | Enviar email de notificación al cliente   |

---

## ✅ 8. Validaciones

* Tracking debe tener formato válido (regex por transportista)
* Todos los dispositivos deben estar disponibles y sin asignar
* Pedido debe coincidir con los IMEIs
* Email del cliente debe estar presente en pedido

---

## 📦 9. Versionado y Estado

* Versión: `v1.1.0`
* Incluye gestión de paquetes pequeños + tracking
* Envío de correos y vinculación con transportistas activada

---

## 🔗 10. Referencias cruzadas

* App 2: origen de `devices`
* App 5: módulo de email / factura
* Diagrama de picking y logística: `DIAGRAMAS.md`【104†source】
