

# 📄 Documento de Especificaciones Técnicas

## Aplicación 1 – Notificación de IMEI/ICCID a Cliente Final

---

### 🧩 1. Descripción General

Esta aplicación permite buscar uno o varios números de serie (formados por IMEI + ICCID), extraerlos desde la base de datos, generar un CSV con los datos correspondientes, y enviarlos por email al cliente final.

Se utilizará principalmente en procesos de producción, logística y postventa para notificar qué dispositivos han sido entregados a cada cliente. Cada número de serie será marcado como “notificado” una vez se haya enviado.

---

### 🧠 2. Funcionalidad Principal

* Ingreso manual o escaneo de uno o varios códigos de número de serie.
* Búsqueda y validación de cada uno en base de datos.
* Generación automática de CSV con los campos solicitados.
* Envío de email al cliente con CSV adjunto.
* Registro del envío en histórico (fecha, cliente, contenido).
* Posibilidad de procesar:

  * ✅ Un único número
  * ✅ Un grupo/lote (automáticamente)

---

### 📦 3. Formato de Número de Serie (entrada/salida)

#### Entrada:

* Campo único que puede contener:

  * Solo IMEI
  * IMEI + espacio + ICCID (ej. `861888082667623 89882390001210884632`)
  * Solo ICCID (detectado por longitud 19–22)
  * Lote o innerbox completo (package_no)

#### Parseo Automático:

* Si el número tiene 15 dígitos → se considera un IMEI
* Si tiene entre 19–22 dígitos → se considera ICCID
* Si tiene ambos → se separa por espacio, guión, tabulación o punto y coma
* Si es un `package_no` → se extraen todos los dispositivos relacionados

---

### 📝 4. Comportamiento del Proceso

1. Usuario introduce código o sube archivo con varios números.

2. Sistema identifica si es un número individual o un lote (`package_no`).

3. Consulta en la base de datos y valida que no haya sido enviado antes.

4. Permite seleccionar al cliente destino.

5. Genera CSV con los campos deseados:

   **Opciones de exportación:**

   * ✅ IMEI + ICCID (en dos columnas)
   * ✅ Número de serie unificado (IMEI + espacio + ICCID en una columna)

6. Envía el correo con CSV adjunto.

7. Marca los registros como “notificados” en la base de datos.

---

### 📄 5. Formato de CSV de salida

#### Modo 1 – Columnas separadas:

| IMEI            | ICCID                |
| --------------- | -------------------- |
| 861888082667623 | 89882390001210884632 |

#### Modo 2 – Columna unificada:

| Número de Serie                      |
| ------------------------------------ |
| 861888082667623 89882390001210884632 |

---

### 🧱 6. Estructura base de datos relevante

Se reutiliza la tabla/colección de dispositivos ya definida en la aplicación 2 (importación):

Campos nuevos añadidos para trazabilidad:

```sql
ALTER TABLE dispositivos
ADD COLUMN notificado BOOLEAN DEFAULT FALSE,
ADD COLUMN cliente_notificado VARCHAR(100),
ADD COLUMN fecha_notificacion TIMESTAMP;
```

---

### 📬 7. Funcionalidad de Envío de Correo

* Sistema puede enviar a:

  * Cliente final (seleccionado)
  * Email de control (copias internas)
* Asunto y cuerpo personalizables con plantilla
* Se adjunta el CSV generado
* Se registra en histórico (por cada IMEI/ICCID enviado)

---

### 🛠️ 8. Endpoints

| Método | Ruta                  | Descripción                                   |
| ------ | --------------------- | --------------------------------------------- |
| POST   | `/notificar`          | Recibe número(s), genera CSV, envía y marca   |
| GET    | `/historial-envios`   | Devuelve histórico de notificaciones enviadas |
| GET    | `/dispositivo/{imei}` | Consulta estado de notificación               |

---

### ✅ 9. Validaciones

* Verifica que el IMEI/ICCID existe en la base de datos.
* No permite reenviar dispositivos ya notificados (a menos que se fuerce).
* Si el cliente ya está asignado, lo sugiere por defecto.
* Si no se encuentra el número: lo muestra como error y permite exportarlo.

---

### 📌 10. Ejemplo de flujo completo

1. Usuario escanea:
   → `861888082667623 89882390001210884632`

2. El sistema identifica:

   * IMEI: `861888082667623`
   * ICCID: `89882390001210884632`

3. Consulta en la base de datos y obtiene:

   * Marca: Neoway
   * Cliente: Correos
   * Lote: L20251110-A
   * Ya fue notificado: ❌

4. El usuario selecciona “Enviar” → genera CSV → se envía por email
   → marca como `notificado = TRUE`
   → registra `cliente_notificado = Correos`

---

### 🔒 11. Seguridad

* Solo usuarios autenticados pueden notificar.
* Se controla por permisos qué usuarios pueden reasignar cliente o modificar registros ya notificados.
Perfecto, Pedro. A continuación tienes la **documentación completa, técnica y funcional** de la **Aplicación 1 – Notificación de IMEI/ICCID a Clientes**, adaptada **a tu base de datos MongoDB `assetflow`**, con efectos logísticos reales, conexión a colecciones como `productos`, `depositos`, `movimientos`, y validaciones para trazabilidad operativa.

---

# 📄 Documento de Especificaciones Técnicas

## Aplicación 1 – Notificación de Números de Serie a Clientes (AssetFlow)

---

## 1. 🧠 Descripción General

Esta aplicación permite notificar oficialmente a los clientes la asignación de dispositivos (balizas, IoT, etc.) a través del envío por email de sus números de serie (IMEI + ICCID). Tiene efecto logístico directo: **marca los dispositivos como entregados**, **asigna cliente**, **registra movimientos**, **actualiza depósitos** y **alimenta KPIs y mapas** en AssetFlow.

---

## 2. 🎯 Objetivo de Uso

* Leer uno o varios **números de serie** (IMEI + ICCID) desde campo manual o CSV.
* Buscar la información en la base de datos Mongo (`productos`).
* Asociar cada dispositivo a un **cliente y depósito**.
* Generar un archivo **CSV configurable**.
* Enviar email con el CSV adjunto.
* Registrar en la base:

  * El cliente receptor.
  * Que fue **notificado**.
  * El **movimiento logístico**.
  * La **actualización del depósito**.

---

## 3. 📥 Entrada de Datos

### Modo manual:

* Escaneo o pegado en un campo de texto.
* Formato único aceptado:

  * `IMEI`
  * `ICCID`
  * `IMEI ICCID` (separados por espacio, guion, tabulación o punto y coma)
  * `package_no` (lote o caja)

### Modo por archivo:

* CSV o Excel con una sola columna: número de serie (en cualquiera de los formatos anteriores)

---

## 4. 📤 Salida

### CSV generado con opciones:

* **Formato A:** Dos columnas → `IMEI`, `ICCID`
* **Formato B:** Una sola columna → `IMEI ICCID`

> El usuario podrá elegir el formato antes de generar el CSV.

---

## 5. 🧱 Modelo de Datos MongoDB (Colecciones utilizadas)

### 🧩 `productos`

```json
{
  "imei": "861888082667623",
  "iccid": "89882390001210884632",
  "notificado": true,
  "cliente": ObjectId("..."),
  "deposito": ObjectId("..."),
  "fecha_notificacion": ISODate("2025-11-11T14:00:00Z"),
  "ubicacion_actual": "CLIENTE-CORREOS-ALMACEN-MADRID"
}
```

### 🧾 `movimientos`

```json
{
  "tipo": "envio",
  "producto": ObjectId("..."),
  "cliente": ObjectId("..."),
  "deposito": ObjectId("..."),
  "fecha": ISODate("2025-11-11T14:00:00Z"),
  "usuario": ObjectId("..."),
  "detalles": "Notificación enviada al cliente Correos vía App 1"
}
```

### 📦 `depositos` (actualización opcional)

```json
{
  "codigo": "DEP-221108-A",
  "cliente": ObjectId("..."),
  "estado": "activo",
  "productos": [ObjectId("..."), ...],
  "fecha_ultimo_movimiento": ISODate("2025-11-11T14:00:00Z")
}
```

---

## 6. 🔁 Flujo Operativo

```mermaid
graph TD
  A[Usuario ingresa número(s)] --> B{¿Individual o Lote?}
  B -->|Individual| C[Parsear IMEI/ICCID]
  B -->|Lote| D[Buscar todos por package_no]
  C --> E[Buscar en Mongo productos]
  D --> E
  E --> F[Verificar ya notificados]
  F --> G[Seleccionar cliente y formato]
  G --> H[Generar CSV]
  H --> I[Enviar email al cliente]
  I --> J[Actualizar productos]
  J --> K[Crear movimiento logístico]
  K --> L[Actualizar depósito]
  L --> M[Finalizado]
```

---

## 7. ✅ Validaciones

* Verifica si el producto ya ha sido notificado (`notificado = true`)
* Si `imei_1 ≠ imei_2`, genera error
* Verifica existencia en la colección `productos`
* Controla duplicados dentro del archivo/campo

---

## 8. 📬 Envío de Correo

* Plantilla personalizable por cliente
* Soporte para múltiples idiomas
* Permite enviar copia interna (control/logística)

---

## 9. 🔒 Seguridad

* Solo usuarios autenticados con permisos pueden notificar
* Se registra `usuario` e `IP` en la colección `movimientos`
* Solo usuarios con rol "admin" pueden re-notificar dispositivos ya enviados

---

## 10. 📡 Integración con AssetFlow

| Acción realizada en App 1 | Impacto en AssetFlow                              |
| ------------------------- | ------------------------------------------------- |
| Notificación de IMEI      | Actualiza `productos`, `movimientos`, `depositos` |
| Generación de CSV         | Alimenta KPIs internos                            |
| Registro de envío         | Se muestra en `dashboard/kpis`, `mapa`, `alertas` |

---

## 11. 📦 API REST de Microservicio (App 1)

| Método | Ruta                      | Descripción                                               |
| ------ | ------------------------- | --------------------------------------------------------- |
| POST   | `/api/notificar`          | Envía dispositivos, cliente y formato, genera CSV y email |
| GET    | `/api/notificaciones`     | Lista de notificaciones realizadas (histórico)            |
| GET    | `/api/notificar/opciones` | Devuelve clientes, formatos, configuración base           |

---

## 12. 🧪 Casos de Prueba Críticos

* ✅ Enviar IMEI único → marca como notificado
* ✅ Enviar lote (package_no) → notifica todos los dispositivos del lote
* ❌ Enviar IMEI ya notificado → bloquea con mensaje o permite reenviar si es admin
* ✅ CSV generado correctamente en ambos formatos
* ✅ Registro correcto en `movimientos`
* ✅ Enlace correcto entre `producto`, `cliente`, `deposito`

---

## 13. 🗂️ Carpetas asociadas

```plaintext
/app-notificacion-series/
├── src/
│   ├── controllers/
│   ├── routes/
│   ├── services/         <- Email, CSV, MongoService
│   └── utils/
├── public/
├── config/
├── .env
├── app.js
```

---

¿Quieres que te genere esta documentación también en formato `.docx`, `.pdf` o lista para subir al Git/Wiki de desarrollo? ¿O pasamos a documentar la App 3?

