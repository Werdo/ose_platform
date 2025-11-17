# PLANTILLA DE IMPORTACIÓN - SISTEMA DE PICKING
## OSE Platform - Trazabilidad Jerárquica

**Fecha de creación:** 2025-11-14
**Versión:** 1.0
**Autor:** Sistema de Análisis OSE Platform

---

## 1. ESTRUCTURA JERÁRQUICA

```
PALLET (Palet/Tarima)
  ├─ CARTON 1 (Caja/Cartón)
  │    ├─ DEVICE 1 (IMEI + ICCID)
  │    ├─ DEVICE 2 (IMEI + ICCID)
  │    ├─ DEVICE 3 (IMEI + ICCID)
  │    └─ ... (48 dispositivos por cartón)
  │
  ├─ CARTON 2
  │    ├─ DEVICE 1 (IMEI + ICCID)
  │    └─ ... (48 dispositivos)
  │
  ├─ CARTON 3
  │    └─ ... (48 dispositivos)
  │
  └─ CARTON 48
       └─ ... (48 dispositivos)

TOTALES POR PALLET:
- 48 cartones/cajas
- 2,304 dispositivos (48 cartones × 48 dispositivos)
```

---

## 2. ARCHIVO DE EJEMPLO ANALIZADO

### 2.1 Información del Archivo

**Archivo:** `10.17 WL00079317 CARLITE 55296（15-38托盘号）.xls`
**Fecha de análisis:** 2025-11-14
**Ubicación:** `C:\Users\pedro\Dropbox\ICCID-SIM\`

### 2.2 Estadísticas Generales

| Métrica | Valor |
|---------|-------|
| **Total de filas** | 55,296 |
| **Total de columnas** | 41 |
| **Dispositivos únicos** | 55,296 |
| **Cartones únicos** | 1,152 |
| **Pallets únicos** | 24 |
| **Órdenes de trabajo** | 1 (WL00079317) |
| **Dispositivos por cartón** | 48 (constante) |
| **Cartones por pallet** | 48 (constante) |
| **Dispositivos por pallet** | 2,304 (48 × 48) |

### 2.3 Rango de Fechas

| Campo | Fecha Mínima | Fecha Máxima |
|-------|--------------|--------------|
| **package_date** | 2025-10-12 10:52:53 | 2025-10-15 18:58:10 |
| **INFO6** (pallet_timestamp) | 2025-10-14 08:11:43 | 2025-10-15 19:30:30 |
| **INFO10** | 2025-10-12 10:42:03 | 2025-10-15 18:56:00 |

### 2.4 Pallets del Archivo

El archivo contiene 24 pallets numerados del 15 al 38:

| Pallet ID | Dispositivos | Cartones |
|-----------|--------------|----------|
| T9121800079317015 | 2,304 | 48 |
| T9121800079317016 | 2,304 | 48 |
| T9121800079317017 | 2,304 | 48 |
| T9121800079317018 | 2,304 | 48 |
| T9121800079317019 | 2,304 | 48 |
| T9121800079317020 | 2,304 | 48 |
| T9121800079317021 | 2,304 | 48 |
| T9121800079317022 | 2,304 | 48 |
| T9121800079317023 | 2,304 | 48 |
| T9121800079317024 | 2,304 | 48 |
| T9121800079317025 | 2,304 | 48 |
| T9121800079317026 | 2,304 | 48 |
| T9121800079317027 | 2,304 | 48 |
| T9121800079317028 | 2,304 | 48 |
| T9121800079317029 | 2,304 | 48 |
| T9121800079317030 | 2,304 | 48 |
| T9121800079317031 | 2,304 | 48 |
| T9121800079317032 | 2,304 | 48 |
| T9121800079317033 | 2,304 | 48 |
| T9121800079317034 | 2,304 | 48 |
| T9121800079317035 | 2,304 | 48 |
| T9121800079317036 | 2,304 | 48 |
| T9121800079317037 | 2,304 | 48 |
| T9121800079317038 | 2,304 | 48 |
| **TOTAL** | **55,296** | **1,152** |

---

## 3. COLUMNAS DEL ARCHIVO EXCEL

### 3.1 Todas las Columnas Disponibles (41 columnas)

| # | Columna | Tipo | Descripción |
|---|---------|------|-------------|
| 1 | info_id | int64 | ID interno del registro |
| 2 | factory_id | int64 | ID de la fábrica (18) |
| 3 | **work_order_id** | **int64** | **Número de orden de trabajo** |
| 4 | **product_sn** | **int64** | **IMEI del dispositivo (principal)** |
| 5 | **imei_1** | **int64** | **IMEI primario (igual que product_sn)** |
| 6 | imei_2 | int64 | IMEI secundario (igual que imei_1) |
| 7 | meid | float64 | MEID (vacío) |
| 8 | bt_mac | float64 | MAC Bluetooth (vacío) |
| 9 | product_id | int64 | ID del producto (79317) |
| 10 | wifi_mac1 | float64 | MAC WiFi 1 (vacío) |
| 11 | wifi_mac2 | float64 | MAC WiFi 2 (vacío) |
| 12 | wifi_mac3 | float64 | MAC WiFi 3 (vacío) |
| 13 | wifi_mac4 | float64 | MAC WiFi 4 (vacío) |
| 14 | **package_no** | **object** | **ID del cartón/caja** |
| 15 | **package_date** | **object** | **Fecha de empaquetado del cartón** |
| 16 | tray_no | float64 | Número de bandeja (vacío) |
| 17 | tray_date | float64 | Fecha de bandeja (vacío) |
| 18 | ship_time | float64 | Tiempo de envío (vacío) |
| 19 | info_issearched | float64 | Indicador de búsqueda (vacío) |
| 20 | oem_tz_sn | float64 | OEM TZ SN (vacío) |
| 21 | oem_tz_id | float64 | OEM TZ ID (vacío) |
| 22 | ssid | float64 | SSID WiFi (vacío) |
| 23 | password | float64 | Contraseña (vacío) |
| 24 | obd_sn | float64 | OBD Serial Number (vacío) |
| 25 | main_sn | float64 | Main Serial Number (vacío) |
| 26 | adb_password | float64 | ADB Password (vacío) |
| 27 | **ccid** | **object** | **ICCID de la tarjeta SIM** |
| 28 | authorization_code | float64 | Código de autorización (vacío) |
| 29 | INFO0 | float64 | Campo extra 0 (vacío) |
| 30 | INFO1 | float64 | Campo extra 1 (vacío) |
| 31 | INFO2 | float64 | Campo extra 2 (vacío) |
| 32 | INFO3 | float64 | Campo extra 3 (vacío) |
| 33 | INFO4 | float64 | Campo extra 4 (vacío) |
| 34 | **INFO5** | **object** | **ID del pallet/tarima** |
| 35 | **INFO6** | **object** | **Timestamp de pallet** |
| 36 | INFO7 | float64 | Campo extra 7 (vacío) |
| 37 | INFO8 | float64 | Campo extra 8 (vacío) |
| 38 | **INFO9** | **object** | **Identificador secundario** |
| 39 | **INFO10** | **object** | **Timestamp secundario** |
| 40 | INFO11 | float64 | Campo extra 11 (vacío) |
| 41 | INFO12 | float64 | Campo extra 12 (vacío) |

### 3.2 Campos Clave para Importación

Los campos **en negrita** son los más relevantes para el sistema de trazabilidad:

- **work_order_id** - Número de orden de trabajo
- **product_sn / imei_1** - IMEI del dispositivo
- **ccid** - ICCID de la tarjeta SIM
- **package_no** - ID del cartón/caja
- **package_date** - Fecha de empaquetado
- **INFO5** - ID del pallet
- **INFO6** - Timestamp del pallet
- **INFO9** - Identificador adicional
- **INFO10** - Timestamp adicional

---

## 4. MAPEO DE CAMPOS

### 4.1 Excel → Modelos MongoDB

#### A. Modelo Device (collection: `devices`)

```javascript
{
  // IDENTIFICACIÓN ÚNICA
  imei: "861888086768500",                    // ← product_sn o imei_1
  iccid: "89882390001223815227",              // ← ccid

  // ORDEN DE PRODUCCIÓN
  production_order: "WL00079317",             // ← work_order_id (sin prefijo "18")
  work_order_id: 1800079317,                  // ← work_order_id (completo)

  // UBICACIÓN EN JERARQUÍA
  package_no: "9912182510100007931700674",    // ← package_no
  carton_id: "9912182510100007931700674",     // ← package_no (alias)
  pallet_id: "T9121800079317017",             // ← INFO5

  // PRODUCTO
  product_model: "CARLITE",                   // ← extraer del nombre de archivo
  product_reference: "55296",                 // ← extraer del nombre de archivo
  product_id: 79317,                          // ← product_id
  factory_id: 18,                             // ← factory_id

  // IDENTIFICADORES ADICIONALES
  info9: "8912182510100007931702698",         // ← INFO9

  // TIMESTAMPS
  package_date: ISODate("2025-10-12T16:06:52Z"),  // ← package_date
  pallet_timestamp: ISODate("2025-10-14T09:45:36Z"), // ← INFO6
  info10_timestamp: ISODate("2025-10-12T16:04:19Z"), // ← INFO10
  created_at: ISODate("2025-11-14T00:00:00Z"),
  updated_at: ISODate("2025-11-14T00:00:00Z"),

  // ESTADO
  notified: false,
  status: "packed"
}
```

#### B. Modelo Package (collection: `packages`)

```javascript
{
  // IDENTIFICACIÓN DEL CARTÓN
  package_id: "9912182510100007931700674",    // ← package_no
  package_no: "9912182510100007931700674",    // ← package_no

  // RELACIÓN CON PALLET
  pallet_id: "T9121800079317017",             // ← INFO5

  // ORDEN DE PRODUCCIÓN
  production_order: "WL00079317",             // ← work_order_id
  work_order_id: 1800079317,                  // ← work_order_id (completo)

  // CONTENIDO
  device_count: 48,                           // Contar dispositivos del cartón
  devices: [                                  // Array de IMEIs
    "861888086768500",
    "861888086912421",
    // ... (48 IMEIs totales)
  ],

  // PRODUCTO
  product_model: "CARLITE",
  product_reference: "55296",
  factory_id: 18,

  // TIMESTAMPS
  packed_at: ISODate("2025-10-12T16:06:52Z"),  // ← package_date (primera del grupo)
  created_at: ISODate("2025-11-14T00:00:00Z"),
  updated_at: ISODate("2025-11-14T00:00:00Z"),

  // ESTADO
  status: "packed"                            // packed, shipped, delivered
}
```

#### C. Modelo Pallet (collection: `pallets`)

```javascript
{
  // IDENTIFICACIÓN DEL PALLET
  pallet_id: "T9121800079317017",             // ← INFO5
  pallet_number: 17,                          // ← Extraer número del INFO5

  // ORDEN DE PRODUCCIÓN
  production_order: "WL00079317",             // ← work_order_id
  work_order_id: 1800079317,                  // ← work_order_id (completo)

  // CONTENIDO
  package_count: 48,                          // Contar cartones únicos del pallet
  packages: [                                 // Array de package_ids
    "9912182510100007931700674",
    "9912182510100007931700673",
    // ... (48 package_no totales)
  ],

  device_count: 2304,                         // Total de dispositivos (48 × 48)

  // PRODUCTO
  product_model: "CARLITE",
  product_reference: "55296",
  factory_id: 18,

  // TIMESTAMPS
  assembled_at: ISODate("2025-10-14T09:45:36Z"),  // ← INFO6 (primera del pallet)
  package_date_min: ISODate("2025-10-12T16:05:23Z"),
  package_date_max: ISODate("2025-10-12T19:09:14Z"),
  created_at: ISODate("2025-11-14T00:00:00Z"),
  updated_at: ISODate("2025-11-14T00:00:00Z"),

  // ESTADO
  status: "ready",                            // ready, in_transit, delivered

  // UBICACIÓN (opcional)
  warehouse_location: null
}
```

---

## 5. FORMATO CSV REQUERIDO PARA IMPORTACIÓN

### 5.1 Plantilla CSV Simplificada

**Archivo:** `import_template.csv`

```csv
order_number,imei,iccid,carton_id,pallet_id,product_model,product_reference,package_date,factory_id
1800079317,861888086768500,89882390001223815227,9912182510100007931700674,T9121800079317017,CARLITE,55296,2025-10-12 16:06:52,18
1800079317,861888086912421,89882390001223728461,9912182510100007931700674,T9121800079317017,CARLITE,55296,2025-10-12 16:06:52,18
1800079317,867572080278344,89882390001224733528,9912182510100007931700673,T9121800079317017,CARLITE,55296,2025-10-12 16:05:23,18
```

### 5.2 Descripción de Campos CSV

| Campo | Tipo | Obligatorio | Descripción | Ejemplo |
|-------|------|-------------|-------------|---------|
| **order_number** | número | ✅ Sí | Número de orden de trabajo | 1800079317 |
| **imei** | número | ✅ Sí | IMEI del dispositivo (15 dígitos) | 861888086768500 |
| **iccid** | texto | ✅ Sí | ICCID de la SIM (20 caracteres) | 89882390001223815227 |
| **carton_id** | texto | ✅ Sí | ID del cartón/caja | 9912182510100007931700674 |
| **pallet_id** | texto | ✅ Sí | ID del pallet/tarima | T9121800079317017 |
| **product_model** | texto | ❌ No | Modelo del producto | CARLITE |
| **product_reference** | texto | ❌ No | Referencia del producto | 55296 |
| **package_date** | fecha | ❌ No | Fecha de empaquetado | 2025-10-12 16:06:52 |
| **factory_id** | número | ❌ No | ID de la fábrica | 18 |

---

## 6. TRANSFORMACIÓN EXCEL → CSV

### 6.1 Script Python de Transformación

```python
import pandas as pd
import re

def extract_product_info_from_filename(filename):
    """
    Extrae información del producto desde el nombre del archivo.
    Ejemplo: "10.17 WL00079317 CARLITE 55296（15-38托盘号）.xls"
    """
    # Extraer número de orden (WL seguido de números)
    order_match = re.search(r'WL(\d+)', filename)
    production_order = f"WL{order_match.group(1)}" if order_match else None

    # Extraer modelo y referencia (entre orden y paréntesis)
    # Formato típico: WL00079317 CARLITE 55296
    parts = re.search(r'WL\d+\s+([A-Z]+)\s+(\d+)', filename)
    product_model = parts.group(1) if parts else None
    product_reference = parts.group(2) if parts else None

    return {
        'production_order': production_order,
        'product_model': product_model,
        'product_reference': product_reference
    }

def transform_excel_to_csv(excel_path, output_csv_path):
    """
    Transforma el archivo Excel al formato CSV requerido.
    """
    # Leer Excel
    print(f"Leyendo archivo: {excel_path}")
    df = pd.read_excel(excel_path, engine='xlrd')

    # Extraer información del nombre del archivo
    import os
    filename = os.path.basename(excel_path)
    product_info = extract_product_info_from_filename(filename)

    print(f"Información extraída del archivo:")
    print(f"  - Orden de producción: {product_info['production_order']}")
    print(f"  - Modelo: {product_info['product_model']}")
    print(f"  - Referencia: {product_info['product_reference']}")

    # Mapear columnas
    df_mapped = pd.DataFrame({
        'order_number': df['work_order_id'],
        'imei': df['product_sn'].astype(str),  # Usar product_sn como IMEI principal
        'iccid': df['ccid'],
        'carton_id': df['package_no'],
        'pallet_id': df['INFO5'],
        'product_model': product_info['product_model'],
        'product_reference': product_info['product_reference'],
        'package_date': df['package_date'],
        'factory_id': df['factory_id']
    })

    # Eliminar filas con datos faltantes críticos
    print(f"\nFilas antes de limpieza: {len(df_mapped)}")
    df_mapped = df_mapped.dropna(subset=['order_number', 'imei', 'iccid', 'carton_id', 'pallet_id'])
    print(f"Filas después de limpieza: {len(df_mapped)}")

    # Validaciones
    print("\n=== VALIDACIONES ===")

    # Validar longitud de IMEI (15 dígitos)
    invalid_imei = df_mapped[df_mapped['imei'].str.len() != 15]
    if len(invalid_imei) > 0:
        print(f"⚠️ ADVERTENCIA: {len(invalid_imei)} IMEIs con longitud incorrecta")
    else:
        print(f"✅ Todos los IMEIs tienen 15 dígitos")

    # Validar longitud de ICCID (20 caracteres)
    invalid_iccid = df_mapped[df_mapped['iccid'].str.len() != 20]
    if len(invalid_iccid) > 0:
        print(f"⚠️ ADVERTENCIA: {len(invalid_iccid)} ICCIDs con longitud incorrecta")
    else:
        print(f"✅ Todos los ICCIDs tienen 20 caracteres")

    # Validar duplicados
    duplicated_imei = df_mapped['imei'].duplicated().sum()
    if duplicated_imei > 0:
        print(f"⚠️ ADVERTENCIA: {duplicated_imei} IMEIs duplicados")
    else:
        print(f"✅ No hay IMEIs duplicados")

    duplicated_iccid = df_mapped['iccid'].duplicated().sum()
    if duplicated_iccid > 0:
        print(f"⚠️ ADVERTENCIA: {duplicated_iccid} ICCIDs duplicados")
    else:
        print(f"✅ No hay ICCIDs duplicados")

    # Estadísticas
    print("\n=== ESTADÍSTICAS ===")
    print(f"Total de dispositivos: {len(df_mapped)}")
    print(f"Total de cartones: {df_mapped['carton_id'].nunique()}")
    print(f"Total de pallets: {df_mapped['pallet_id'].nunique()}")
    print(f"Dispositivos por cartón: {df_mapped.groupby('carton_id').size().mean():.0f}")
    print(f"Cartones por pallet: {df_mapped.groupby('pallet_id')['carton_id'].nunique().mean():.0f}")

    # Exportar a CSV
    df_mapped.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(f"\n✅ Archivo CSV generado: {output_csv_path}")

    return df_mapped

# EJEMPLO DE USO
if __name__ == "__main__":
    excel_file = r"C:\Users\pedro\Dropbox\ICCID-SIM\10.17 WL00079317 CARLITE 55296（15-38托盘号）.xls"
    output_file = r"C:\Users\pedro\claude-code-workspace\OSE-Platform\import_ready.csv"

    df_result = transform_excel_to_csv(excel_file, output_file)

    # Mostrar muestra
    print("\n=== MUESTRA DE DATOS (primeras 5 filas) ===")
    print(df_result.head().to_string())
```

### 6.2 Ejecutar la Transformación

```bash
# Ejecutar el script de transformación
python transform_excel.py

# Resultado esperado:
# - Archivo CSV generado: import_ready.csv
# - 55,296 filas de dispositivos
# - 1,152 cartones únicos
# - 24 pallets únicos
```

---

## 7. OPERACIONES DE BÚSQUEDA EN MONGODB

### 7.1 Buscar por PALLET → Ver todos los CARTONS

```javascript
// MongoDB Query
db.packages.find({ pallet_id: "T9121800079317017" })
  .sort({ package_no: 1 })

// Resultado esperado: 48 cartones
[
  {
    package_id: "9912182510100007931700674",
    pallet_id: "T9121800079317017",
    device_count: 48,
    production_order: "WL00079317",
    packed_at: ISODate("2025-10-12T16:06:52Z")
  },
  {
    package_id: "9912182510100007931700673",
    pallet_id: "T9121800079317017",
    device_count: 48,
    production_order: "WL00079317",
    packed_at: ISODate("2025-10-12T16:05:23Z")
  },
  // ... (46 cartones más)
]

// Contar cartones en un pallet
db.packages.countDocuments({ pallet_id: "T9121800079317017" })
// Resultado: 48
```

### 7.2 Buscar por CARTON → Ver todos los DISPOSITIVOS

```javascript
// MongoDB Query
db.devices.find({ package_no: "9912182510100007931700674" })
  .sort({ imei: 1 })

// Resultado esperado: 48 dispositivos
[
  {
    imei: "861888086768500",
    iccid: "89882390001223815227",
    package_no: "9912182510100007931700674",
    pallet_id: "T9121800079317017",
    production_order: "WL00079317"
  },
  {
    imei: "861888086912421",
    iccid: "89882390001223728461",
    package_no: "9912182510100007931700674",
    pallet_id: "T9121800079317017",
    production_order: "WL00079317"
  },
  // ... (46 dispositivos más)
]

// Contar dispositivos en un cartón
db.devices.countDocuments({ package_no: "9912182510100007931700674" })
// Resultado: 48
```

### 7.3 Buscar por IMEI → Ver CARTON y PALLET

```javascript
// MongoDB Query
db.devices.findOne({ imei: "861888086768500" })

// Resultado: Dispositivo con ubicación completa
{
  imei: "861888086768500",
  iccid: "89882390001223815227",
  package_no: "9912182510100007931700674",
  carton_id: "9912182510100007931700674",
  pallet_id: "T9121800079317017",
  production_order: "WL00079317",
  product_model: "CARLITE",
  product_reference: "55296",
  package_date: ISODate("2025-10-12T16:06:52Z"),
  pallet_timestamp: ISODate("2025-10-14T09:45:36Z")
}
```

### 7.4 Buscar por ICCID → Ver ubicación completa

```javascript
// MongoDB Query
db.devices.findOne({ iccid: "89882390001223815227" })

// Resultado: Mismo que búsqueda por IMEI
{
  imei: "861888086768500",
  iccid: "89882390001223815227",
  package_no: "9912182510100007931700674",
  pallet_id: "T9121800079317017",
  production_order: "WL00079317"
}
```

### 7.5 Obtener jerarquía completa de un PALLET

```javascript
// Aggregation Pipeline para obtener PALLET → CARTONS → DEVICES
db.pallets.aggregate([
  { $match: { pallet_id: "T9121800079317017" } },
  {
    $lookup: {
      from: "packages",
      localField: "pallet_id",
      foreignField: "pallet_id",
      as: "cartons"
    }
  },
  {
    $lookup: {
      from: "devices",
      localField: "pallet_id",
      foreignField: "pallet_id",
      as: "devices"
    }
  },
  {
    $project: {
      pallet_id: 1,
      production_order: 1,
      package_count: 1,
      device_count: 1,
      cartons: {
        $map: {
          input: "$cartons",
          as: "carton",
          in: {
            package_id: "$$carton.package_id",
            device_count: "$$carton.device_count",
            packed_at: "$$carton.packed_at"
          }
        }
      },
      total_devices: { $size: "$devices" }
    }
  }
])
```

### 7.6 Buscar dispositivos por rango de fechas

```javascript
// Buscar dispositivos empaquetados en un rango de fechas
db.devices.find({
  package_date: {
    $gte: ISODate("2025-10-12T00:00:00Z"),
    $lte: ISODate("2025-10-12T23:59:59Z")
  }
}).count()
```

### 7.7 Obtener resumen de una orden de trabajo

```javascript
// Resumen completo de la orden WL00079317
db.devices.aggregate([
  { $match: { production_order: "WL00079317" } },
  {
    $group: {
      _id: "$production_order",
      total_devices: { $sum: 1 },
      unique_pallets: { $addToSet: "$pallet_id" },
      unique_cartons: { $addToSet: "$package_no" },
      min_date: { $min: "$package_date" },
      max_date: { $max: "$package_date" }
    }
  },
  {
    $project: {
      production_order: "$_id",
      total_devices: 1,
      total_pallets: { $size: "$unique_pallets" },
      total_cartons: { $size: "$unique_cartons" },
      date_range: {
        from: "$min_date",
        to: "$max_date"
      }
    }
  }
])

// Resultado esperado:
{
  production_order: "WL00079317",
  total_devices: 55296,
  total_pallets: 24,
  total_cartons: 1152,
  date_range: {
    from: ISODate("2025-10-12T10:52:53Z"),
    to: ISODate("2025-10-15T18:58:10Z")
  }
}
```

---

## 8. ENDPOINTS API REQUERIDOS

### 8.1 Importar archivo Excel/CSV

**Endpoint:** `POST /api/v1/picking/import`

**Request:**
```http
POST /api/v1/picking/import HTTP/1.1
Content-Type: multipart/form-data
Authorization: Bearer {token}

Body:
  file: [archivo Excel (.xls, .xlsx) o CSV]
  validate_only: false (opcional, default: false)
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Archivo importado correctamente",
  "data": {
    "devices_imported": 55296,
    "devices_updated": 0,
    "packages_created": 1152,
    "packages_updated": 0,
    "pallets_created": 24,
    "pallets_updated": 0,
    "production_order": "WL00079317",
    "import_duration_ms": 12543
  },
  "errors": [],
  "warnings": []
}
```

**Response (con errores):**
```json
{
  "success": false,
  "message": "Importación completada con errores",
  "data": {
    "devices_imported": 55200,
    "devices_failed": 96,
    "packages_created": 1150,
    "pallets_created": 24
  },
  "errors": [
    {
      "row": 1234,
      "imei": "861888086768500",
      "error": "IMEI duplicado en la base de datos",
      "severity": "error"
    },
    {
      "row": 5678,
      "imei": "86188808676850X",
      "error": "IMEI con formato inválido (debe tener 15 dígitos numéricos)",
      "severity": "error"
    }
  ],
  "warnings": [
    {
      "row": 100,
      "imei": "861888086768500",
      "warning": "package_date no proporcionado, usando fecha actual",
      "severity": "warning"
    }
  ]
}
```

### 8.2 Buscar por Pallet

**Endpoint:** `GET /api/v1/picking/pallets/{pallet_id}`

**Request:**
```http
GET /api/v1/picking/pallets/T9121800079317017 HTTP/1.1
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "pallet_id": "T9121800079317017",
    "pallet_number": 17,
    "production_order": "WL00079317",
    "product_model": "CARLITE",
    "product_reference": "55296",
    "package_count": 48,
    "device_count": 2304,
    "status": "ready",
    "assembled_at": "2025-10-14T09:45:36.000Z",
    "created_at": "2025-11-14T00:00:00.000Z"
  }
}
```

### 8.3 Buscar Cartons de un Pallet

**Endpoint:** `GET /api/v1/picking/pallets/{pallet_id}/packages`

**Request:**
```http
GET /api/v1/picking/pallets/T9121800079317017/packages HTTP/1.1
Authorization: Bearer {token}
```

**Query Parameters:**
- `page` (opcional): Número de página (default: 1)
- `limit` (opcional): Registros por página (default: 50, max: 100)
- `sort` (opcional): Campo de ordenamiento (default: "package_no")

**Response:**
```json
{
  "success": true,
  "data": {
    "pallet_id": "T9121800079317017",
    "package_count": 48,
    "packages": [
      {
        "package_id": "9912182510100007931700674",
        "package_no": "9912182510100007931700674",
        "device_count": 48,
        "packed_at": "2025-10-12T16:06:52.000Z",
        "status": "packed"
      },
      {
        "package_id": "9912182510100007931700673",
        "package_no": "9912182510100007931700673",
        "device_count": 48,
        "packed_at": "2025-10-12T16:05:23.000Z",
        "status": "packed"
      }
      // ... (46 más)
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 48,
      "pages": 1
    }
  }
}
```

### 8.4 Buscar Dispositivos de un Carton

**Endpoint:** `GET /api/v1/picking/packages/{package_id}/devices`

**Request:**
```http
GET /api/v1/picking/packages/9912182510100007931700674/devices HTTP/1.1
Authorization: Bearer {token}
```

**Query Parameters:**
- `page` (opcional): Número de página (default: 1)
- `limit` (opcional): Registros por página (default: 50, max: 100)

**Response:**
```json
{
  "success": true,
  "data": {
    "package_id": "9912182510100007931700674",
    "pallet_id": "T9121800079317017",
    "device_count": 48,
    "devices": [
      {
        "imei": "861888086768500",
        "iccid": "89882390001223815227",
        "product_model": "CARLITE",
        "package_date": "2025-10-12T16:06:52.000Z",
        "status": "packed",
        "notified": false
      },
      {
        "imei": "861888086912421",
        "iccid": "89882390001223728461",
        "product_model": "CARLITE",
        "package_date": "2025-10-12T16:06:52.000Z",
        "status": "packed",
        "notified": false
      }
      // ... (46 más)
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 48,
      "pages": 1
    }
  }
}
```

### 8.5 Buscar Dispositivo por IMEI

**Endpoint:** `GET /api/v1/picking/devices/{imei}`

**Request:**
```http
GET /api/v1/picking/devices/861888086768500 HTTP/1.1
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "imei": "861888086768500",
    "iccid": "89882390001223815227",
    "production_order": "WL00079317",
    "product_model": "CARLITE",
    "product_reference": "55296",
    "location": {
      "package_no": "9912182510100007931700674",
      "carton_id": "9912182510100007931700674",
      "pallet_id": "T9121800079317017",
      "pallet_number": 17
    },
    "timestamps": {
      "package_date": "2025-10-12T16:06:52.000Z",
      "pallet_timestamp": "2025-10-14T09:45:36.000Z",
      "created_at": "2025-11-14T00:00:00.000Z"
    },
    "status": "packed",
    "notified": false
  }
}
```

### 8.6 Buscar Dispositivo por ICCID

**Endpoint:** `GET /api/v1/picking/devices/by-iccid/{iccid}`

**Request:**
```http
GET /api/v1/picking/devices/by-iccid/89882390001223815227 HTTP/1.1
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    // Mismo formato que búsqueda por IMEI
  }
}
```

### 8.7 Listar todos los Pallets de una Orden

**Endpoint:** `GET /api/v1/picking/orders/{production_order}/pallets`

**Request:**
```http
GET /api/v1/picking/orders/WL00079317/pallets HTTP/1.1
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "production_order": "WL00079317",
    "product_model": "CARLITE",
    "product_reference": "55296",
    "pallet_count": 24,
    "total_packages": 1152,
    "total_devices": 55296,
    "pallets": [
      {
        "pallet_id": "T9121800079317015",
        "pallet_number": 15,
        "package_count": 48,
        "device_count": 2304,
        "status": "ready",
        "assembled_at": "2025-10-14T08:11:43.000Z"
      },
      {
        "pallet_id": "T9121800079317016",
        "pallet_number": 16,
        "package_count": 48,
        "device_count": 2304,
        "status": "ready",
        "assembled_at": "2025-10-14T09:30:12.000Z"
      }
      // ... (22 más)
    ]
  }
}
```

### 8.8 Obtener estadísticas de una orden

**Endpoint:** `GET /api/v1/picking/orders/{production_order}/stats`

**Request:**
```http
GET /api/v1/picking/orders/WL00079317/stats HTTP/1.1
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "production_order": "WL00079317",
    "product_model": "CARLITE",
    "product_reference": "55296",
    "summary": {
      "total_pallets": 24,
      "total_packages": 1152,
      "total_devices": 55296,
      "devices_per_package": 48,
      "packages_per_pallet": 48,
      "devices_per_pallet": 2304
    },
    "status_breakdown": {
      "pallets": {
        "ready": 24,
        "in_transit": 0,
        "delivered": 0
      },
      "packages": {
        "packed": 1152,
        "shipped": 0,
        "delivered": 0
      },
      "devices": {
        "packed": 55296,
        "notified": 0
      }
    },
    "date_range": {
      "package_date_min": "2025-10-12T10:52:53.000Z",
      "package_date_max": "2025-10-15T18:58:10.000Z",
      "pallet_timestamp_min": "2025-10-14T08:11:43.000Z",
      "pallet_timestamp_max": "2025-10-15T19:30:30.000Z"
    }
  }
}
```

---

## 9. VALIDACIONES REQUERIDAS

### 9.1 Validaciones durante la importación

Durante la importación de archivos Excel/CSV, el sistema debe validar:

#### A. Validaciones de Formato

| Campo | Validación | Error si falla |
|-------|------------|----------------|
| **IMEI** | - Debe tener exactamente 15 dígitos<br>- Solo caracteres numéricos<br>- No puede estar vacío | "IMEI inválido: debe contener 15 dígitos numéricos" |
| **ICCID** | - Debe tener 19-20 caracteres<br>- Solo caracteres alfanuméricos<br>- No puede estar vacío | "ICCID inválido: debe contener 19-20 caracteres" |
| **order_number** | - Debe ser numérico<br>- No puede estar vacío | "Número de orden inválido" |
| **carton_id** | - No puede estar vacío<br>- Formato texto | "ID de cartón faltante" |
| **pallet_id** | - No puede estar vacío<br>- Formato texto | "ID de pallet faltante" |

#### B. Validaciones de Unicidad

```javascript
// Validación 1: IMEI único en la base de datos
const existingDevice = await db.devices.findOne({ imei: "861888086768500" });
if (existingDevice) {
  throw new ValidationError("IMEI duplicado en la base de datos");
}

// Validación 2: ICCID único en la base de datos
const existingICCID = await db.devices.findOne({ iccid: "89882390001223815227" });
if (existingICCID) {
  throw new ValidationError("ICCID duplicado en la base de datos");
}

// Validación 3: IMEI único en el archivo de importación
const imeiCount = importData.filter(row => row.imei === "861888086768500").length;
if (imeiCount > 1) {
  throw new ValidationError("IMEI duplicado en el archivo de importación");
}
```

#### C. Validaciones de Integridad

```javascript
// Validación 4: Cada IMEI debe tener su ICCID correspondiente
if (row.imei && !row.iccid) {
  throw new ValidationError("Dispositivo tiene IMEI pero falta ICCID");
}

if (row.iccid && !row.imei) {
  throw new ValidationError("Dispositivo tiene ICCID pero falta IMEI");
}

// Validación 5: Consistencia de pallets y cartones
// Todos los dispositivos del mismo carton_id deben tener el mismo pallet_id
const cartonDevices = importData.filter(row => row.carton_id === "9912182510100007931700674");
const uniquePallets = [...new Set(cartonDevices.map(row => row.pallet_id))];
if (uniquePallets.length > 1) {
  throw new ValidationError("Cartón asociado a múltiples pallets");
}

// Validación 6: Consistencia de orden de trabajo
// Todos los dispositivos del mismo pallet deben tener el mismo order_number
const palletDevices = importData.filter(row => row.pallet_id === "T9121800079317017");
const uniqueOrders = [...new Set(palletDevices.map(row => row.order_number))];
if (uniqueOrders.length > 1) {
  throw new ValidationError("Pallet asociado a múltiples órdenes de trabajo");
}
```

#### D. Validaciones de Contenido

```javascript
// Validación 7: Dispositivos por cartón (verificar consistencia)
const devicesInCarton = importData.filter(row => row.carton_id === "9912182510100007931700674").length;
if (devicesInCarton !== 48) {
  warnings.push(`Cartón tiene ${devicesInCarton} dispositivos (esperado: 48)`);
}

// Validación 8: Cartones por pallet (verificar consistencia)
const cartonsInPallet = [...new Set(
  importData
    .filter(row => row.pallet_id === "T9121800079317017")
    .map(row => row.carton_id)
)].length;
if (cartonsInPallet !== 48) {
  warnings.push(`Pallet tiene ${cartonsInPallet} cartones (esperado: 48)`);
}
```

### 9.2 Checklist de Validación

Antes de guardar los datos en MongoDB, verificar:

- ✅ **IMEI:** 15 dígitos numéricos
- ✅ **ICCID:** 19-20 caracteres alfanuméricos
- ✅ **IMEI único:** No existe en la BD
- ✅ **ICCID único:** No existe en la BD
- ✅ **IMEI ↔ ICCID:** Cada IMEI tiene su ICCID
- ✅ **Carton_ID:** No está vacío
- ✅ **Pallet_ID:** No está vacío
- ✅ **Order_number:** Es válido y no está vacío
- ✅ **Consistencia Carton → Pallet:** Un cartón = un pallet
- ✅ **Consistencia Pallet → Orden:** Un pallet = una orden

---

## 10. INTEGRACIÓN CON APPS EXISTENTES

### 10.1 App 1: Notificación de Series

**Funcionalidad:** Notificar IMEIs/ICCIDs de dispositivos empaquetados.

**Uso de la jerarquía:**
- Notificar por **dispositivo individual** (IMEI único)
- Notificar por **cartón completo** (48 dispositivos)
- Notificar por **pallet completo** (2,304 dispositivos)

**Ejemplo de API:**
```javascript
// Notificar un pallet completo
POST /api/v1/notifications/notify-pallet
{
  "pallet_id": "T9121800079317017",
  "notification_type": "series_registration"
}

// Esto notificará automáticamente:
// - 48 cartones
// - 2,304 dispositivos (IMEIs + ICCIDs)
```

### 10.2 App 2: Importación

**Funcionalidad:** Importar archivos Excel con la estructura jerárquica.

**Uso de la jerarquía:**
- Importar archivo Excel → Crear automáticamente:
  - Registros de **Devices** (collection `devices`)
  - Registros de **Packages** (collection `packages`)
  - Registros de **Pallets** (collection `pallets`)

**Proceso de importación:**
```
1. Leer archivo Excel
2. Validar estructura y datos
3. Agrupar por pallet_id → Crear pallets
4. Agrupar por carton_id → Crear packages
5. Insertar dispositivos → Crear devices
6. Actualizar contadores en pallets y packages
```

### 10.3 App 3: RMA/Tickets

**Funcionalidad:** Gestión de devoluciones y tickets de soporte.

**Uso de la jerarquía:**
- Buscar dispositivo defectuoso por **IMEI**
- Identificar en qué **cartón** se encuentra
- Identificar en qué **pallet** se encuentra
- Ver todos los dispositivos del **mismo cartón** (posible lote defectuoso)

**Ejemplo de consulta:**
```javascript
// Dispositivo defectuoso
GET /api/v1/rma/devices/861888086768500

// Respuesta incluye ubicación:
{
  "imei": "861888086768500",
  "package_no": "9912182510100007931700674",
  "pallet_id": "T9121800079317017",
  "production_order": "WL00079317",

  // Ver dispositivos del mismo lote
  "batch_devices_count": 48,
  "batch_devices_url": "/api/v1/picking/packages/9912182510100007931700674/devices"
}
```

### 10.4 App 6: Picking

**Funcionalidad:** Gestión completa de pallets y cartones para envíos.

**Uso de la jerarquía:**
- Seleccionar **pallets** para envío
- Ver contenido de cada **pallet** (48 cartones)
- Ver contenido de cada **cartón** (48 dispositivos)
- Generar etiquetas de envío por pallet o cartón
- Tracking de ubicación física en almacén

**Flujo de trabajo:**
```
1. Listar pallets disponibles (status: "ready")
2. Seleccionar pallet para envío
3. Ver contenido del pallet (cartones + dispositivos)
4. Marcar pallet como "in_transit"
5. Generar documentación de envío
6. Actualizar ubicación física
```

### 10.5 Campos compartidos entre Apps

Todas las apps utilizan los mismos campos base:

```javascript
// Campos comunes en todas las apps
{
  imei: "861888086768500",
  iccid: "89882390001223815227",
  production_order: "WL00079317",
  package_no: "9912182510100007931700674",
  pallet_id: "T9121800079317017",
  product_model: "CARLITE",
  product_reference: "55296"
}
```

---

## 11. EJEMPLO COMPLETO DE DATOS DEL ARCHIVO

### 11.1 Muestra de 20 Dispositivos Reales

| # | order_number | imei | iccid | carton_id | pallet_id | package_date | pallet_timestamp |
|---|--------------|------|-------|-----------|-----------|--------------|------------------|
| 1 | 1800079317 | 861888086768500 | 89882390001223815227 | 9912182510100007931700674 | T9121800079317017 | 2025-10-12 16:06:52 | 2025-10-14 09:45:36 |
| 2 | 1800079317 | 861888086912421 | 89882390001223728461 | 9912182510100007931700674 | T9121800079317017 | 2025-10-12 16:06:52 | 2025-10-14 09:45:36 |
| 3 | 1800079317 | 867572080278344 | 89882390001224733528 | 9912182510100007931700673 | T9121800079317017 | 2025-10-12 16:05:23 | 2025-10-14 09:45:36 |
| 4 | 1800079317 | 867572080473945 | 89882390001270879795 | 9912182510100007931700770 | T9121800079317025 | 2025-10-12 19:09:14 | 2025-10-14 18:32:16 |
| 5 | 1800079317 | 861888086672215 | 89882390001270740088 | 9912182510100007931700682 | T9121800079317017 | 2025-10-12 16:19:08 | 2025-10-14 09:45:40 |
| 6 | 1800079317 | 861888086735269 | 89882390001223834830 | 9912182510100007931700715 | T9121800079317017 | 2025-10-12 17:38:00 | 2025-10-14 09:45:32 |
| 7 | 1800079317 | 861888086705494 | 89882390001223829244 | 9912182510100007931700683 | T9121800079317017 | 2025-10-12 16:21:10 | 2025-10-14 09:45:40 |
| 8 | 1800079317 | 867572080014517 | 89882390001270632160 | 9912182510100007931700686 | T9121800079317017 | 2025-10-12 16:25:41 | 2025-10-14 09:45:35 |
| 9 | 1800079317 | 867572080422611 | 89882390001270642193 | 9912182510100007931700684 | T9121800079317017 | 2025-10-12 16:22:56 | 2025-10-14 09:45:40 |
| 10 | 1800079317 | 867572080465388 | 89882390001270871339 | 9912182510100007931700751 | T9121800079317026 | 2025-10-12 18:36:53 | 2025-10-14 19:37:54 |
| 11 | 1800079317 | 867572080567605 | 89882390001270867352 | 9912182510100007931700676 | T9121800079317017 | 2025-10-12 16:09:53 | 2025-10-14 09:45:41 |
| 12 | 1800079317 | 861888086665722 | 89882390001270747083 | 9912182510100007931700752 | T9121800079317026 | 2025-10-12 18:38:27 | 2025-10-14 19:37:53 |
| 13 | 1800079317 | 867572080470412 | 89882390001270874861 | 9912182510100007931700676 | T9121800079317017 | 2025-10-12 16:09:53 | 2025-10-14 09:45:41 |
| 14 | 1800079317 | 867572080474943 | 89882390001270871032 | 9912182510100007931700541 | T9121800079317018 | 2025-10-12 11:11:12 | 2025-10-14 10:50:01 |
| 15 | 1800079317 | 867572080465487 | 89882390001270871701 | 9912182510100007931700761 | T9121800079317026 | 2025-10-12 18:54:05 | 2025-10-14 19:37:45 |
| 16 | 1800079317 | 867572080507973 | 89882390001271116643 | 9912182510100007931701314 | T9121800079317031 | 2025-10-14 10:17:21 | 2025-10-15 11:18:05 |
| 17 | 1800079317 | 861888086385420 | 89882390001270783419 | 9912182510100007931700679 | T9121800079317017 | 2025-10-12 16:14:27 | 2025-10-14 09:45:35 |
| 18 | 1800079317 | 867572080530066 | 89882390001270802110 | 9912182510100007931700755 | T9121800079317026 | 2025-10-12 18:44:07 | 2025-10-14 19:37:48 |
| 19 | 1800079317 | 867572080152739 | 89882390001224725037 | 9912182510100007931700745 | T9121800079317026 | 2025-10-12 18:27:57 | 2025-10-14 19:37:48 |
| 20 | 1800079317 | 861888087309114 | 89882390001223748030 | 9912182510100007931700674 | T9121800079317017 | 2025-10-12 16:06:52 | 2025-10-14 09:45:36 |

### 11.2 Observaciones de los Datos

1. **Orden de trabajo única:** Todos los dispositivos pertenecen a la orden `1800079317` (WL00079317)

2. **Distribución de pallets:**
   - Pallet `T9121800079317017`: aparece en 13 de 20 dispositivos (más frecuente)
   - Pallet `T9121800079317026`: aparece en 5 dispositivos
   - Otros pallets: 025, 018, 031

3. **Cartones:**
   - Cartón `9912182510100007931700674`: contiene al menos 3 dispositivos (filas 1, 2, 20)
   - Cada cartón está asociado a un único pallet

4. **Formatos validados:**
   - **IMEI:** 15 dígitos exactos
   - **ICCID:** 20 caracteres exactos
   - **Carton_ID:** 25 caracteres (formato: `9912182510100007931700XXX`)
   - **Pallet_ID:** 17 caracteres (formato: `T9121800079317XXX`)

5. **Timestamps:**
   - `package_date`: Rango de 2025-10-12 a 2025-10-14
   - `pallet_timestamp`: Rango de 2025-10-14 a 2025-10-15
   - El pallet_timestamp siempre es posterior al package_date (lógico: primero se empaquetan los cartones, luego se ensamblan en pallets)

---

## 12. RESUMEN EJECUTIVO

### 12.1 Puntos Clave

1. **Jerarquía de 3 niveles:**
   - PALLET (2,304 dispositivos)
   - CARTON (48 dispositivos)
   - DEVICE (IMEI + ICCID)

2. **Campos obligatorios para importación:**
   - `order_number` - Número de orden
   - `imei` - IMEI del dispositivo
   - `iccid` - ICCID de la SIM
   - `carton_id` - ID del cartón
   - `pallet_id` - ID del pallet

3. **Estructura del archivo analizado:**
   - 55,296 dispositivos
   - 1,152 cartones (48 dispositivos cada uno)
   - 24 pallets (48 cartones cada uno)
   - 1 orden de trabajo (WL00079317)

4. **Validaciones críticas:**
   - IMEI: 15 dígitos únicos
   - ICCID: 20 caracteres únicos
   - No duplicados
   - Integridad jerárquica

5. **APIs principales:**
   - Importación de archivos
   - Búsqueda por pallet → cartones → dispositivos
   - Búsqueda por IMEI/ICCID → ubicación completa

### 12.2 Próximos Pasos

1. **Implementar modelos MongoDB:**
   - Collection `devices`
   - Collection `packages`
   - Collection `pallets`

2. **Crear endpoints API:**
   - POST `/api/v1/picking/import`
   - GET `/api/v1/picking/pallets/{id}`
   - GET `/api/v1/picking/pallets/{id}/packages`
   - GET `/api/v1/picking/packages/{id}/devices`
   - GET `/api/v1/picking/devices/{imei}`

3. **Desarrollar script de transformación:**
   - Leer archivos Excel
   - Validar datos
   - Generar CSV para importación

4. **Integrar con apps existentes:**
   - App 1: Notificación de series
   - App 2: Importación
   - App 3: RMA/Tickets
   - App 6: Picking

---

**FIN DEL DOCUMENTO**

**Última actualización:** 2025-11-14
**Versión:** 1.0
**Contacto:** Sistema OSE Platform
