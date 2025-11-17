✅ Documento generado: **App1 Notificación Series**
# 📄 Documento de Especificaciones

## Aplicación 1 – Notificación de Números de Serie a Clientes (AssetFlow)

---

## 💪 1. Propósito General

La Aplicación 1 permite **notificar oficialmente a los clientes** la asignación de dispositivos (balizas u otros equipos) mediante el envío de números de serie, compuestos por `IMEI + ICCID`. Esto tiene efecto logístico directo:

* Marca los dispositivos como entregados
* Asigna cliente y ubicación actual
* Registra movimiento de salida
* Alimenta los dashboards e indicadores en AssetFlow

---

## 🔄 2. Flujo General

```mermaid
flowchart TB
  A[Usuario introduce número o lote] --> B[Parseo: IMEI/ICCID o package_no]
  B --> C[Consulta en MongoDB: devices]
  C --> D[Verificación de existencia y notificación previa]
  D --> E[Seleccionar cliente y formato de salida]
  E --> F[Generar CSV (1 o 2 columnas)]
  F --> G[Enviar email]
  G --> H[Actualizar estado en devices]
  H --> I[Registrar evento en device_events]
  I --> J[Insertar movimiento logístico en movimientos]
```

---

## 🔄 3. Formatos de Entrada

### Campo único de entrada:

* `861888082667623` → IMEI solo
* `89882390001210884632` → ICCID solo
* `861888082667623 89882390001210884632` → IMEI + ICCID
* `package_no`: `9912182508200007739500205` → Lote/caja (extrae todos)

### Desde CSV:

* Columna única con cualquier combinación anterior

---

## 📃 4. Formato de Salida CSV

### Opcion A: Separado

| IMEI      | ICCID      |
| --------- | ---------- |
| 861888... | 8988239... |

### Opcion B: Unificado

| Número de Serie      |
| -------------------- |
| 861888... 8988239... |

---

## 🔧 5. Operaciones en MongoDB

### 5.1 Colección `devices`

Actualiza:

```json
{
  "notificado": true,
  "cliente": ObjectId("..."),
  "fecha_notificacion": ISODate("2025-11-11T13:00:00Z"),
  "estado": "activo",
  "ubicacion_actual": "CLIENTE-CORREOS-ALMACEN-MADRID"
}
```

### 5.2 Colección `device_events`

Agrega:

```json
{
  "device_id": ObjectId("..."),
  "event_type": "notified_to_client",
  "timestamp": ISODate("2025-11-11T13:00:00Z"),
  "operator": "usuario-app1",
  "cliente": ObjectId("...")
}
```

### 5.3 Colección `movimientos`

Inserta:

```json
{
  "tipo": "envio",
  "producto": ObjectId("..."),
  "cliente": ObjectId("..."),
  "deposito": ObjectId("..."),
  "fecha": ISODate("2025-11-11T13:00:00Z"),
  "usuario": "usuario-app1",
  "detalles": "Notificado desde App 1"
}
```

---

## 📖 6. API REST

| Método | Ruta             | Descripción                                |
| ------ | ---------------- | ------------------------------------------ |
| POST   | `/api/notificar` | Enviar IMEI/ICCID o lote, cliente, formato |
| GET    | `/api/historial` | Lista de envíos realizados                 |
| GET    | `/api/opciones`  | Clientes, formatos, configuración inicial  |

---

## ✅ 7. Validaciones

* ✅ IMEI debe existir en `devices`
* ✅ IMEI no debe estar marcado como `notificado`
* ❌ Si `imei_1 ≠ imei_2`, error
* ⚠ ICCID vacío → advertencia
* ⚠ Cliente no especificado → bloquea envío

---

## 📰 8. Emails generados

* Se genera con plantilla configurable
* Puede incluir firma, logo y datos comerciales
* Enviado a:

  * Cliente destinatario
  * CC opcional a logística u operación interna

---

## 🚫 9. Seguridad

* Autenticación JWT obligatoria
* Acciones registradas por usuario
* No se permite modificar notificaciones anteriores (solo leer)

---

## 💡 10. Funcionalidades futuras

* Anulación de notificación (solo admin)
* Generador de informes PDF
* Enlace con sistema de ticketing postventa
* Asignación automática de cliente si viene del importador

---

## 📅 11. Versión y estado

* Versión App 1: `v1.0.0`
* Completamente integrada con `devices`, `movimientos`, `device_events`
* Dependencias: App 2 (Importación previa del dispositivo)

---

## 🔹 12. Referencias cruzadas

* Arquitectura Mongo: `ARQUITECTURA_MONGODB.md`【101†source】
* Diagrama de ciclo de vida: `DIAGRAMAS.md`【104†source】
* Origen de datos: `ESTRUCTURA_POSTGRESQL.txt`【100†source】
* Flujo App 2 (origen de datos): `GUIA_MIGRACION_DETALLADA.md`【102†source】
