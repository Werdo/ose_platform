

# 📄 Documento de Especificaciones Técnicas

## Aplicación de Importación de Datos

---

### 🧩 1. Descripción General

La Aplicación de Importación de Datos forma parte del sistema centralizado de gestión de activos y producción. Permite importar automáticamente información contenida en archivos Excel o CSV generados por fabricantes, socios logísticos o procesos internos.

Su objetivo principal es registrar, validar y almacenar los datos de trazabilidad de cada unidad (baliza, dispositivo, etc.), asociándolos a su número de serie, SIM, lote, depósito, y ubicación actual.

---

### 🔁 2. Flujo Funcional

1. El usuario carga un archivo Excel o CSV desde la interfaz.
2. El backend interpreta los campos clave (IMEI, ICCID, etc.).
3. Valida la coherencia y formato de cada registro.
4. Inserta los datos en la base de datos PostgreSQL y/o MongoDB.
5. Genera un informe de errores (si los hay) y lo muestra o descarga.

---

### 📥 3. Formato de Archivo Soportado

* **Extensiones aceptadas:** `.xlsx`, `.xls`, `.csv`
* **Encabezados esperados en el archivo:**

| Columna en Excel   | Campo Interno (base de datos) | Obligatorio | Descripción                            |
| ------------------ | ----------------------------- | ----------- | -------------------------------------- |
| `imei_1`           | `imei`                        | ✅ Sí        | IMEI principal del dispositivo         |
| `imei_2`           | Validación interna            | ✅ Sí        | Debe coincidir con `imei_1`            |
| `iccid`            | `iccid`                       | ✅ Sí        | Código SIM del dispositivo             |
| `package_no`       | `package_no`                  | Opcional    | Número de caja física                  |
| `orden_produccion` | `orden_produccion`            | Opcional    | Orden de producción interna            |
| `lote`             | `lote`                        | Opcional    | Número de lote de fabricación          |
| `codigo_innerbox`  | `codigo_innerbox`             | Opcional    | Código de expositora o caja intermedia |
| `codigo_unitario`  | `codigo_unitario`             | Opcional    | Código visual o QR de unidad           |
| `num_palet`        | `num_palet`                   | Opcional    | Palet asociado                         |
| `marca`            | `marca`                       | Opcional    | Marca comercial (propia o cliente)     |
| `cliente`          | `cliente`                     | Opcional    | Nombre del cliente/distribuidor        |
| `num_deposito`     | `num_deposito`                | Opcional    | Código de depósito                     |
| `ubicacion_actual` | `ubicacion_actual`            | Opcional    | Ubicación física actual                |

---

### ✅ 4. Validaciones

* **IMEI:** debe ser único y numérico (15 dígitos).
* **IMEI_1 = IMEI_2:** si no coinciden → error.
* **ICCID:** debe tener entre 19 y 22 caracteres numéricos.
* **Evita duplicados por IMEI o ICCID.**
* **Campos opcionales:** si no existen en el archivo, se ignoran sin error.

---

### 🧱 5. Modelo de Datos

#### MongoDB (estructura JSON):

```json
{
  "imei": "861888082667623",
  "iccid": "89882390001210884632",
  "package_no": "9912182508200007739500205",
  "orden_produccion": "OP-20251110-001",
  "lote": "L20251110-A",
  "codigo_innerbox": "INBX-44519",
  "codigo_unitario": "UNIT-00001234",
  "num_palet": "PAL-88",
  "marca": "Neoway",
  "cliente": "Correos",
  "num_deposito": "DEP-221108-A",
  "ubicacion_actual": "CLIENTE-CORREOS-ALMACEN-MADRID",
  "valid": true,
  "errores": [],
  "fecha_importacion": "2025-11-11T13:15:00Z"
}
```

#### PostgreSQL (tabla `dispositivos`):

```sql
CREATE TABLE dispositivos (
    id UUID PRIMARY KEY,
    imei VARCHAR(20) UNIQUE NOT NULL,
    iccid VARCHAR(25),
    package_no VARCHAR(40),
    orden_produccion VARCHAR(50),
    lote VARCHAR(50),
    codigo_innerbox VARCHAR(50),
    codigo_unitario VARCHAR(50),
    num_palet VARCHAR(50),
    marca VARCHAR(50),
    cliente VARCHAR(100),
    num_deposito VARCHAR(50),
    ubicacion_actual VARCHAR(100),
    valid BOOLEAN DEFAULT TRUE,
    errores TEXT[],
    fecha_importacion TIMESTAMP DEFAULT NOW()
);
```

---

### ⚙️ 6. Endpoints del Microservicio

| Método | Ruta                       | Descripción                         |
| ------ | -------------------------- | ----------------------------------- |
| POST   | `/importar`                | Carga e importa archivo Excel/CSV   |
| GET    | `/errores`                 | Devuelve los errores detectados     |
| GET    | `/resumen`                 | Muestra resumen de la importación   |
| GET    | `/dispositivos?filtros...` | Consulta de dispositivos importados |

---

### 🛑 7. Gestión de Errores

* Registros con errores no se insertan.
* Se genera un listado descargable con:

  * Línea del error
  * Campo afectado
  * Descripción del problema

---

### 🔒 8. Seguridad y Control de Accesos

* Requiere token JWT o sesión autenticada para importar.
* Registro automático de:

  * Usuario que sube el archivo
  * IP origen
  * Timestamp
* Control de duplicados y alertas si ya se ha importado ese paquete/lote.

---

### 📎 9. Compatibilidad e Integraciones

* Compatible con módulos de trazabilidad, depósitos, logística, y RMA.
* Permite enriquecer dispositivos ya existentes (merge inteligente).
* Se podrá invocar también desde bots (Telegram/WhatsApp) en el futuro.

---

### 📌 10. Consideraciones Finales

* Esta aplicación será la **puerta de entrada oficial de datos productivos y comerciales** al sistema.
* Toda unidad debe pasar por esta importación o por una app que escriba en esta misma tabla para garantizar trazabilidad completa.
* Se podrá extender en el futuro con OCR para leer PDFs logísticos u hojas de producción.
