✅ Documento generado: **App3 Rma Ticket**
# 📄 Documento de Especificaciones

## Aplicación 3 – Gestor de Incidencias y RMA Multiusuario

---

## 💪 1. Propósito General

La Aplicación 3 permite a clientes finales y distribuidores registrar y gestionar **incidencias, tickets de soporte y solicitudes de devolución (RMA)** de dispositivos. Esta herramienta forma parte del entorno AssetFlow y centraliza la comunicación postventa.

---

## 🛠️ 2. Tipos de Usuario

| Tipo            | Acceso a              | Puede registrar | Puede resolver |
| --------------- | --------------------- | --------------- | -------------- |
| Cliente final   | Sus dispositivos      | ✅               | ❌              |
| Distribuidor    | Dispositivos vendidos | ✅               | ❌              |
| Usuario interno | Todos                 | ✅               | ✅              |

> El sistema debe ser multitenant y multiusuario.

---

## 📝 3. Funcionalidades

### A. Registro de incidencia

* Ingreso de IMEI o código QR
* Datos recogidos:

  * Fecha
  * Motivo
  * Descripción
  * Fotos (opcional)
* Se genera un `service_ticket`

### B. Seguimiento y chat

* Sistema de mensajes tipo chat (cliente <-> soporte)
* Adjuntos permitidos
* Estados del ticket:

  * `pendiente`, `en_revision`, `resuelto`, `rechazado`

### C. Cierre o escalado a RMA

* Soporte interno puede:

  * Marcar como resuelto
  * Escalar a caso RMA (`rma_case`)

---

## 🛏️ 4. Interfaces

### Portal Web:

* Acceso con email/clave o código por ticket
* Historial del cliente
* Formulario de nueva incidencia

### Backend REST:

| Método | Ruta                         | Descripción                    |
| ------ | ---------------------------- | ------------------------------ |
| POST   | `/api/tickets/nuevo`         | Crear nueva incidencia         |
| GET    | `/api/tickets/mis`           | Listar tickets del usuario     |
| GET    | `/api/tickets/:id`           | Obtener detalles y mensajes    |
| POST   | `/api/tickets/:id/respuesta` | Enviar respuesta/chat          |
| PATCH  | `/api/tickets/:id/cerrar`    | Marcar como resuelto o cerrado |

---

## 🔧 5. Modelo de Datos MongoDB

### service_tickets

```json
{
  "ticket_number": "STK-2025-00124",
  "device_id": ObjectId("..."),
  "customer_id": ObjectId("..."),
  "status": "pendiente",
  "created_at": ISODate("2025-11-11T10:00:00Z"),
  "messages": [
    {
      "from": "cliente",
      "texto": "Mi baliza no enciende",
      "timestamp": ISODate("2025-11-11T10:01:00Z")
    }
  ]
}
```

### rma_cases (si se genera)

```json
{
  "rma_number": "RMA-2025-00045",
  "device_id": ObjectId("..."),
  "customer_id": ObjectId("..."),
  "ticket_id": ObjectId("..."),
  "status": "pendiente",
  "fecha_solicitud": ISODate("2025-11-11T12:00:00Z")
}
```

---

## 🛈 6. Estados de un ticket

| Estado      | Color | Acción disponible         |
| ----------- | ----- | ------------------------- |
| pendiente   | Gris  | Esperando respuesta       |
| en_revision | Azul  | Usuario interno revisando |
| resuelto    | Verde | Cierre confirmado         |
| rechazado   | Rojo  | Incidencia no admitida    |

---

## 🔒 7. Seguridad y Control de Acceso

* JWT obligatorio
* Cada usuario sólo puede ver sus tickets
* Operadores internos pueden acceder a todos
* Adjuntos con URL firmadas o acceso temporal

---

## 💡 8. Características adicionales

* Notificación por email al registrar/responder
* Historial completo disponible para exportar
* Asignación de responsable interna (soporte)
* Enlace con inventario para dispositivos en garantía

---

## 📰 9. Integraciones

* App 5 (factura) puede estar conectada para validar si el cliente tiene compra previa
* App 1 (notificación de serie) puede marcar que el dispositivo fue notificado

---

## 📅 10. Versión y Estado

* Versión: `v1.0.0`
* Web interna en desarrollo
* Backend funcional
* Integrado con colecciones `service_tickets`, `devices`, `customers`, `rma_cases`

---

## 🔹 11. Referencias

* Arquitectura Mongo: `ARQUITECTURA_MONGODB.md`【101†source】
* Diagrama de ciclo de vida: `DIAGRAMAS.md`【104†source】
* Origen de dispositivos: App 2 (importación)
* Documentos de garantía y RMA: App 5
