# GUÍA RÁPIDA - SISTEMA DE PICKING E IMPORTACIÓN

## OSE Platform - Trazabilidad Jerárquica

**Fecha:** 2025-11-14
**Versión:** 1.0

---

## ARCHIVOS GENERADOS

Este análisis ha generado los siguientes archivos:

### 1. PLANTILLA_IMPORTACION_PICKING.md
**Descripción:** Documentación completa del sistema de trazabilidad jerárquica.

**Contenido:**
- Estructura jerárquica PALLET → CARTON → DISPOSITIVO
- Análisis detallado del archivo Excel
- Mapeo completo de campos Excel → MongoDB
- Modelos de datos (Devices, Packages, Pallets)
- Formato CSV requerido
- Endpoints API necesarios
- Validaciones requeridas
- Operaciones de búsqueda en MongoDB
- Integración con apps existentes

**Uso:** Documento de referencia para desarrolladores e implementadores del sistema.

### 2. transform_excel_to_csv.py
**Descripción:** Script Python para transformar archivos Excel a formato CSV importable.

**Funcionalidades:**
- Lee archivos Excel (.xls, .xlsx)
- Extrae información del producto desde el nombre del archivo
- Mapea columnas al formato requerido
- Valida todos los datos (IMEI, ICCID, duplicados, consistencia)
- Genera archivo CSV listo para importación
- Proporciona estadísticas detalladas

**Uso:** Ver sección "Cómo usar el script" más abajo.

### 3. import_ready.csv
**Descripción:** Archivo CSV generado con los datos transformados del archivo de ejemplo.

**Estadísticas:**
- 55,296 dispositivos
- 1,152 cartones
- 24 pallets
- 1 orden de trabajo (WL00079317)

**Formato:**
```csv
order_number,imei,iccid,carton_id,pallet_id,product_model,product_reference,package_date,factory_id
```

**Uso:** Archivo listo para importar en el sistema OSE Platform.

---

## CÓMO USAR EL SCRIPT DE TRANSFORMACIÓN

### Requisitos Previos

```bash
# Instalar Python 3.12+ (si no está instalado)

# Instalar dependencias
pip install pandas xlrd
```

### Uso Básico

```bash
# Ejecutar el script con el archivo de ejemplo
python transform_excel_to_csv.py
```

### Personalizar Archivos de Entrada/Salida

Editar las rutas en `transform_excel_to_csv.py`:

```python
# Líneas 382-383
excel_file = r"C:\ruta\a\tu\archivo.xls"
output_file = r"C:\ruta\de\salida\import_ready.csv"
```

### Usar como Módulo Python

```python
from transform_excel_to_csv import transform_excel_to_csv

# Transformar archivo
df, stats, errors, warnings = transform_excel_to_csv(
    excel_path="C:/path/to/file.xls",
    output_csv_path="C:/path/to/output.csv",
    validate_only=False  # True = solo validar, no generar CSV
)

# Ver estadísticas
print(f"Dispositivos: {stats['total_devices']}")
print(f"Cartones: {stats['total_cartons']}")
print(f"Pallets: {stats['total_pallets']}")

# Ver errores (si los hay)
if len(errors) > 0:
    for error in errors:
        print(f"{error['type']}: {error['message']}")
```

---

## ESTRUCTURA DEL ARCHIVO EXCEL DE ENTRADA

### Columnas Requeridas

El archivo Excel debe contener estas columnas:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `work_order_id` | Número de orden de trabajo | 1800079317 |
| `product_sn` | IMEI del dispositivo | 861888086768500 |
| `ccid` | ICCID de la tarjeta SIM | 89882390001223815227 |
| `package_no` | ID del cartón/caja | 9912182510100007931700674 |
| `INFO5` | ID del pallet | T9121800079317017 |

### Columnas Opcionales

| Columna | Descripción |
|---------|-------------|
| `factory_id` | ID de la fábrica |
| `package_date` | Fecha de empaquetado |
| `INFO6` | Timestamp del pallet |
| `INFO9` | Identificador adicional |
| `INFO10` | Timestamp adicional |

### Formato del Nombre del Archivo

El script extrae información del nombre del archivo:

**Formato:** `[fecha] [order_number] [model] [reference]（[info]）.xls`

**Ejemplo:** `10.17 WL00079317 CARLITE 55296（15-38托盘号）.xls`

**Extrae:**
- Orden: `WL00079317`
- Modelo: `CARLITE`
- Referencia: `55296`

---

## VALIDACIONES REALIZADAS

El script valida automáticamente:

### ✓ Validaciones de Formato
- IMEI: 15 dígitos numéricos
- ICCID: 19-20 caracteres alfanuméricos
- Campos obligatorios no vacíos

### ✓ Validaciones de Unicidad
- No hay IMEIs duplicados
- No hay ICCIDs duplicados

### ✓ Validaciones de Integridad
- Cada cartón pertenece a un único pallet
- Cada pallet pertenece a una única orden

### ⚠ Advertencias (no bloquean la importación)
- Número de dispositivos por cartón (esperado: 48)
- Número de cartones por pallet (esperado: 48)

---

## SIGUIENTE PASO: IMPORTAR EN OSE PLATFORM

### Opción 1: API REST

```bash
# Importar usando el endpoint API
curl -X POST http://localhost:3000/api/v1/picking/import \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@import_ready.csv"
```

### Opción 2: Script de Importación

```javascript
// Crear script de importación en Node.js
const fs = require('fs');
const csv = require('csv-parser');
const Device = require('./models/Device');
const Package = require('./models/Package');
const Pallet = require('./models/Pallet');

async function importCSV(filePath) {
  const devices = [];
  const packages = new Map();
  const pallets = new Map();

  // Leer CSV
  fs.createReadStream(filePath)
    .pipe(csv())
    .on('data', (row) => {
      // Crear dispositivo
      devices.push({
        imei: row.imei,
        iccid: row.iccid,
        production_order: row.order_number,
        package_no: row.carton_id,
        pallet_id: row.pallet_id,
        product_model: row.product_model,
        product_reference: row.product_reference,
        package_date: new Date(row.package_date),
        factory_id: parseInt(row.factory_id)
      });

      // Agrupar por package
      if (!packages.has(row.carton_id)) {
        packages.set(row.carton_id, {
          package_id: row.carton_id,
          pallet_id: row.pallet_id,
          production_order: row.order_number,
          devices: []
        });
      }
      packages.get(row.carton_id).devices.push(row.imei);

      // Agrupar por pallet
      if (!pallets.has(row.pallet_id)) {
        pallets.set(row.pallet_id, {
          pallet_id: row.pallet_id,
          production_order: row.order_number,
          packages: new Set()
        });
      }
      pallets.get(row.pallet_id).packages.add(row.carton_id);
    })
    .on('end', async () => {
      // Insertar en MongoDB
      await Device.insertMany(devices);

      for (const pkg of packages.values()) {
        pkg.device_count = pkg.devices.length;
        await Package.create(pkg);
      }

      for (const pallet of pallets.values()) {
        pallet.packages = Array.from(pallet.packages);
        pallet.package_count = pallet.packages.length;
        pallet.device_count = pallet.package_count * 48;
        await Pallet.create(pallet);
      }

      console.log(`Importados ${devices.length} dispositivos`);
      console.log(`Creados ${packages.size} cartones`);
      console.log(`Creados ${pallets.size} pallets`);
    });
}

// Ejecutar
importCSV('./import_ready.csv');
```

---

## CONSULTAS MONGODB DE EJEMPLO

### Buscar por PALLET

```javascript
// Ver todos los cartones de un pallet
db.packages.find({ pallet_id: "T9121800079317017" })

// Contar dispositivos en un pallet
db.devices.countDocuments({ pallet_id: "T9121800079317017" })
// Resultado: 2,304
```

### Buscar por CARTON

```javascript
// Ver todos los dispositivos de un cartón
db.devices.find({ package_no: "9912182510100007931700674" })

// Contar dispositivos en un cartón
db.devices.countDocuments({ package_no: "9912182510100007931700674" })
// Resultado: 48
```

### Buscar por IMEI

```javascript
// Encontrar ubicación de un dispositivo
db.devices.findOne({ imei: "861888086768500" })

// Resultado:
{
  imei: "861888086768500",
  iccid: "89882390001223815227",
  package_no: "9912182510100007931700674",
  pallet_id: "T9121800079317017",
  production_order: "WL00079317"
}
```

### Estadísticas por Orden

```javascript
// Resumen de una orden de trabajo
db.devices.aggregate([
  { $match: { production_order: "WL00079317" } },
  {
    $group: {
      _id: "$production_order",
      total_devices: { $sum: 1 },
      unique_pallets: { $addToSet: "$pallet_id" },
      unique_cartons: { $addToSet: "$package_no" }
    }
  },
  {
    $project: {
      production_order: "$_id",
      total_devices: 1,
      total_pallets: { $size: "$unique_pallets" },
      total_cartons: { $size: "$unique_cartons" }
    }
  }
])
```

---

## SOLUCIÓN DE PROBLEMAS

### Error: "Missing optional dependency 'xlrd'"

```bash
pip install xlrd
```

### Error: "UnicodeEncodeError"

El script ya está configurado para manejar archivos con caracteres especiales (chino, japonés, etc.).

Si aún así hay problemas:

```bash
# Windows
chcp 65001
python transform_excel_to_csv.py

# Linux/Mac
export PYTHONIOENCODING=utf-8
python transform_excel_to_csv.py
```

### Error: "Columnas faltantes"

Verificar que el archivo Excel tenga las columnas requeridas:
- `work_order_id`
- `product_sn`
- `ccid`
- `package_no`
- `INFO5`

### Advertencia: "Dispositivos por cartón difiere de 48"

Esto es solo una advertencia. El script generará el CSV de todas formas.

Si es intencional, ignorar la advertencia.

Si es un error, revisar el archivo Excel de origen.

---

## RESUMEN DE FLUJO COMPLETO

```
1. ARCHIVO EXCEL
   ↓
2. EJECUTAR transform_excel_to_csv.py
   ↓
3. VALIDAR RESULTADOS
   ↓
4. GENERAR import_ready.csv
   ↓
5. IMPORTAR EN OSE PLATFORM (API o script)
   ↓
6. CREAR COLECCIONES MONGODB
   - devices (55,296 registros)
   - packages (1,152 registros)
   - pallets (24 registros)
   ↓
7. SISTEMA LISTO PARA USAR
   - Búsquedas por IMEI/ICCID
   - Gestión de picking
   - Notificaciones por pallet/carton
   - RMA y tickets
```

---

## ARCHIVOS DE REFERENCIA

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| **PLANTILLA_IMPORTACION_PICKING.md** | Raíz del proyecto | Documentación completa |
| **transform_excel_to_csv.py** | Raíz del proyecto | Script de transformación |
| **import_ready.csv** | Raíz del proyecto | CSV generado (ejemplo) |
| **README_PICKING_IMPORT.md** | Raíz del proyecto | Esta guía rápida |

---

## CONTACTO Y SOPORTE

Para dudas o problemas con la implementación:

1. Revisar **PLANTILLA_IMPORTACION_PICKING.md** (documentación completa)
2. Ejecutar el script en modo validación: `validate_only=True`
3. Verificar logs de validación
4. Consultar sección de APIs en la plantilla

---

**IMPORTANTE:**
- Todos los datos mostrados son del archivo REAL analizado
- Las validaciones garantizan la integridad de los datos
- El CSV generado está listo para producción
- La estructura jerárquica es escalable

---

**Última actualización:** 2025-11-14
**Versión:** 1.0
**Sistema:** OSE Platform - Picking & Trazabilidad
