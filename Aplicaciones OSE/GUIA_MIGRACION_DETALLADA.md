# 🔄 GUÍA DE MIGRACIÓN: PostgreSQL → MongoDB
## Oversun Energy - Mapeo Campo por Campo

---

## 📋 ÍNDICE

1. [Estrategia General](#estrategia-general)
2. [Mapeo Detallado por Tabla](#mapeo-detallado)
3. [Transformaciones de Datos](#transformaciones)
4. [Scripts de Ejemplo](#scripts)

---

## 🎯 ESTRATEGIA GENERAL

### Principios de Migración

1. **Consolidación**: Múltiples tablas pequeñas → Una colección con subdocumentos
2. **Denormalización**: Eliminar joins frecuentes
3. **Trazabilidad**: Separar eventos históricos
4. **Tipos nativos**: Convertir strings a Date, Number, Boolean

### Transformaciones Clave

```
PostgreSQL              →  MongoDB
────────────────────────────────────────────
character(20)           →  String (trimmed)
integer                 →  Int32 / Int64
character(20) [fecha]   →  ISODate
0/1 (flags)             →  Boolean
```

---

## 📊 MAPEO DETALLADO

### 1. ORDEN_PRODUCCION → production_orders

**Estrategia**: Migración directa con enriquecimiento

#### Mapeo de Campos

| PostgreSQL Campo | Tipo PG | MongoDB Campo | Tipo Mongo | Transformación |
|-----------------|---------|---------------|------------|----------------|
| nro_orden | character(25) | order_number | String | trim() |
| nro_referencia | character(13) | reference_number | String | trim() |
| sku | integer | sku | Int32 | directo |
| cantidad | integer | quantity | Int32 | directo |
| fecha | character(10) | created_at | Date | parseDate() |
| responsable | character(20) | responsible | String | trim() → employees.employee_id |
| detalles | character(300) | notes | String | trim() |
| status | integer | status | String | mapStatus() |
| in_process | integer | - | - | usar en status |
| complete | integer | - | - | usar en status |
| start_fecha | character(20) | start_date | Date | parseDate() |
| end_fecha | character(20) | end_date | Date | parseDate() |
| packing | integer | - | - | usar en status |
| on_hold | integer | - | - | usar en status |
| linea | integer | production_line | Int32 | directo |

#### Mapeo de Estados

```javascript
function mapStatus(row) {
  if (row.complete === 1) return "completed";
  if (row.on_hold === 1) return "on_hold";
  if (row.in_process === 1) return "in_progress";
  if (row.status === 0) return "pending";
  return "in_progress";
}
```

#### Ejemplo de Documento MongoDB

```javascript
{
  _id: ObjectId("..."),
  order_number: "OP-2025-0001",
  reference_number: "OSE-TRACK-V2",
  sku: 1001,
  quantity: 1000,
  produced: 0,  // calculado desde registros
  approved: 0,  // calculado desde QC
  rejected: 0,  // calculado desde QC
  status: "in_progress",
  production_line: 1,
  responsible: "EMP003",
  start_date: ISODate("2025-01-05T08:00:00Z"),
  end_date: null,
  estimated_completion: ISODate("2025-01-20T18:00:00Z"),
  notes: "Orden prioritaria",
  created_at: ISODate("2025-01-02T10:00:00Z"),
  updated_at: ISODate("2025-01-15T14:30:00Z"),
  
  // NUEVO: Información de batches desde cupones_de_trabajo
  batches: [
    {
      batch_number: 1,
      quantity: 250,
      start_date: ISODate("2025-01-05T08:00:00Z"),
      operator: "EMP001",
      workstation: 1
    }
  ],
  
  // NUEVO: Información de etiquetas
  labels_required: {
    label_24: 250,
    label_80: 500,
    label_96: 250
  }
}
```

---

### 2. REGISTROS_2025 + REGISTROS_2025_PUESTO2 → devices + device_events

**Estrategia**: 
- Crear un documento `devices` por cada IMEI único
- Crear documento `device_events` por cada registro

#### Mapeo registros_2025 → devices

| PostgreSQL Campo | MongoDB devices | Transformación |
|-----------------|-----------------|----------------|
| nro | - | ignorar (sequence) |
| nro_orden | production_order | trim() |
| fecha | created_at | parseDate() |
| lote | batch | directo |
| imei | imei | trim() |
| ccid | ccid | trim() |
| linea1/linea2/linea3 | production_line | detectLine() |
| operador | - | usar en device_events |

#### Mapeo registros_2025 → device_events

Cada registro genera UN evento:

```javascript
{
  _id: ObjectId("..."),
  device_id: ObjectId("ref_a_devices"),
  imei: "356789123456789",
  event_type: "production_completed",  // o "quality_check_passed"
  timestamp: ISODate("2025-01-15T10:30:00Z"),
  operator: "Juan Rodriguez",
  production_order: "OP-2025-0001",
  batch: 1,
  workstation: 1,  // desde puesto2 vs registros_2025
  production_line: 1,
  old_status: "in_production",
  new_status: "quality_control",
  data: {
    original_table: "registros_2025",
    original_nro: 12345
  }
}
```

#### Función detectLine()

```javascript
function detectLine(row) {
  if (row.linea1 === 1) return 1;
  if (row.linea2 === 1) return 2;
  if (row.linea3 === 1) return 3;
  return 1; // default
}
```

---

### 3. CUPONES_DE_TRABAJO → production_orders.batches

**Estrategia**: Embeber como subdocumento en production_orders

#### Mapeo

| PostgreSQL Campo | Embebido en | Transformación |
|-----------------|-------------|----------------|
| nro_orden | - | buscar production_order |
| lote1 | batches[].batch_number | directo |
| total_lotes1 | - | count(batches) |
| balizas_registradas1 | batches[].quantity | directo |
| etq24, etq80, etq96 | labels_required | objeto |
| linea | production_line | directo |
| puesto1, puesto2 | batches[].workstation | 1 o 2 |

#### Ejemplo de Integración

```javascript
// Desde cupones_de_trabajo
{
  nro_orden: "OP-2025-0001",
  lote1: 1,
  lote2: 2,
  balizas_registradas1: 250,
  balizas_registradas2: 250,
  etq80: 500
}

// Se convierte en production_orders con:
{
  order_number: "OP-2025-0001",
  batches: [
    {
      batch_number: 1,
      quantity: 250,
      workstation: 1
    },
    {
      batch_number: 2,
      quantity: 250,
      workstation: 2
    }
  ],
  labels_required: {
    label_80: 500
  }
}
```

---

### 4. CONTROL_CALIDAD_*_HISTORY → quality_control + device_events

**Estrategia**: 
- Registro detallado en `quality_control`
- Evento en `device_events`

#### Mapeo control_calidad_linea1_history → quality_control

| PostgreSQL Campo | MongoDB Campo | Transformación |
|-----------------|---------------|----------------|
| fecha | inspection_date | parseDate() |
| imei | imei | trim() + buscar device_id |
| ccid | ccid | trim() |
| status | result | mapQCResult() |
| nro_orden | production_order | trim() |
| - | production_line | desde tabla name (linea1 → 1) |

#### Función mapQCResult()

```javascript
function mapQCResult(status) {
  // 0 = failed, 1 = passed
  return status === 1 ? "passed" : "failed";
}
```

#### También crear device_events

```javascript
{
  event_type: status === 1 ? "quality_check_passed" : "quality_check_failed",
  timestamp: parseDate(fecha),
  // ... resto de campos
}
```

---

### 5. PERSONAL → employees

**Estrategia**: Consolidar personal + personal_admin

#### Mapeo personal → employees

| PostgreSQL Campo | MongoDB Campo | Transformación |
|-----------------|---------------|----------------|
| id | employee_id | trim() |
| name | name | trim() |
| surname | surname | trim() |
| secretkey | - | NO migrar (seguridad) |
| master | role | mapRole() |
| status | status | mapStatus() |
| puesto1_linea1 | permissions.production_line1_station1 | toBoolean() |
| puesto2_linea1 | permissions.production_line1_station2 | toBoolean() |
| puesto1_linea2 | permissions.production_line2_station1 | toBoolean() |
| puesto2_linea2 | permissions.production_line2_station2 | toBoolean() |
| control_calidad | permissions.quality_control | toBoolean() |
| puesto1_linea3 | permissions.production_line3_station1 | toBoolean() |
| puesto2_linea3 | permissions.production_line3_station2 | toBoolean() |

#### Función mapRole()

```javascript
function mapRole(master, hasQC) {
  if (master === 1) return "supervisor";
  if (hasQC === 1) return "quality_inspector";
  return "operator";
}
```

---

### 6. MARCA_REFERENCIA → devices.brand (embedded)

**Estrategia**: Denormalizar - agregar marca directamente en devices

#### Mapeo

```javascript
// PostgreSQL
marca_referencia: {
  marca: "OversunTrack",
  nro_referencia: "OSE-TRACK-V2"
}

// MongoDB devices
{
  reference_number: "OSE-TRACK-V2",
  brand: "OversunTrack"  // JOIN durante migración
}
```

---

### 7. OEM_REGISTROS → devices (type: oem)

**Estrategia**: Unificar con devices regulares, usar flag

#### Mapeo

| PostgreSQL Campo | MongoDB Campo | Notas |
|-----------------|---------------|-------|
| nro | - | ignorar |
| nro_orden | production_order | |
| fecha | created_at | |
| imei | imei | |
| ccid | ccid | |
| status | status | mapear |
| lote | batch | |
| linea | production_line | |
| - | metadata.type | agregar "oem" |

---

### 8. METRICS → metrics

**Estrategia**: Transformar a métricas agregadas

#### Mapeo

| PostgreSQL Campo | MongoDB Campo | Transformación |
|-----------------|---------------|----------------|
| nro_orden | production_order | referencia |
| start_fecha | - | usar para calcular |
| end_fecha | - | usar para calcular |
| duration | value | parseDuration() |
| duration_per_lot | - | calcular |
| operator_puesto | operator | |
| operator_puesto_2 | - | agregar al array |

#### Transformación a Métricas Agregadas

```javascript
// PostgreSQL
{
  nro_orden: "OP-2025-0001",
  start_fecha: "2025-01-05 08:00",
  end_fecha: "2025-01-05 18:00",
  duration: "10:00:00"
}

// MongoDB metrics (múltiples documentos)
[
  {
    metric_type: "production_daily",
    period: "daily",
    date: ISODate("2025-01-05"),
    value: 10.0,  // horas
    production_order: "OP-2025-0001"
  },
  {
    metric_type: "average_production_time",
    period: "daily",
    date: ISODate("2025-01-05"),
    value: 120.0,  // minutos por unidad
    production_order: "OP-2025-0001"
  }
]
```

---

## 🔧 TRANSFORMACIONES DE DATOS

### Fechas

```javascript
function parseDate(dateStr) {
  if (!dateStr || dateStr.trim() === '') return null;
  
  // Formatos posibles:
  // "2025-01-15"
  // "2025-01-15 14:30:00"
  // "15/01/2025"
  
  const date = new Date(dateStr);
  return isNaN(date) ? null : date;
}
```

### Booleanos

```javascript
function toBoolean(value) {
  return value === 1 || value === '1' || value === true;
}
```

### Trim y Limpieza

```javascript
function cleanString(str) {
  if (!str) return null;
  const cleaned = str.trim();
  return cleaned === '' ? null : cleaned;
}
```

---

## 📝 SCRIPTS DE MIGRACIÓN

### Script Python - Ejemplo Completo

```python
#!/usr/bin/env python3
import psycopg2
from pymongo import MongoClient
from datetime import datetime
import re

# Conexiones
pg_conn = psycopg2.connect(
    host="localhost",
    database="oversunserverDB",
    user="panda",
    password="your_password"
)

mongo_client = MongoClient("mongodb://oversun_api:password@localhost:27017/")
mongo_db = mongo_client["oversun_production"]

# ============================================================
# 1. MIGRAR ORDEN_PRODUCCION
# ============================================================

def migrate_production_orders():
    print("Migrando orden_produccion...")
    
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("""
        SELECT 
            nro_orden, nro_referencia, sku, cantidad, fecha,
            responsable, detalles, status, in_process, complete,
            start_fecha, end_fecha, packing, on_hold, linea
        FROM algepser.orden_produccion
    """)
    
    migrated = 0
    for row in pg_cursor.fetchall():
        # Mapear estado
        if row[9] == 1:  # complete
            status = "completed"
        elif row[13] == 1:  # on_hold
            status = "on_hold"
        elif row[8] == 1:  # in_process
            status = "in_progress"
        else:
            status = "pending"
        
        # Crear documento
        doc = {
            "order_number": row[0].strip() if row[0] else None,
            "reference_number": row[1].strip() if row[1] else None,
            "sku": row[2],
            "quantity": row[3],
            "produced": 0,  # Calcular después
            "approved": 0,
            "rejected": 0,
            "status": status,
            "production_line": row[14],
            "responsible": row[5].strip() if row[5] else None,
            "start_date": parse_date(row[10]),
            "end_date": parse_date(row[11]),
            "notes": row[6].strip() if row[6] else None,
            "created_at": parse_date(row[4]),
            "updated_at": datetime.now(),
            "batches": [],  # Llenar después con cupones
            "labels_required": {}
        }
        
        # Insertar
        result = mongo_db.production_orders.insert_one(doc)
        migrated += 1
        
        if migrated % 100 == 0:
            print(f"  Migradas {migrated} órdenes...")
    
    print(f"✓ {migrated} órdenes migradas")

# ============================================================
# 2. MIGRAR REGISTROS_2025
# ============================================================

def migrate_devices():
    print("Migrando registros_2025 a devices...")
    
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("""
        SELECT DISTINCT imei, ccid, nro_orden, fecha, lote,
               linea1, linea2, linea3, operador
        FROM algepser.registros_2025
        WHERE imei IS NOT NULL AND imei != ''
    """)
    
    migrated = 0
    for row in pg_cursor.fetchall():
        imei = row[0].strip()
        ccid = row[1].strip() if row[1] else None
        
        # Verificar si ya existe
        existing = mongo_db.devices.find_one({"imei": imei})
        if existing:
            continue
        
        # Detectar línea
        production_line = 1
        if row[6] == 1:
            production_line = 2
        elif row[7] == 1:
            production_line = 3
        
        # Crear documento
        doc = {
            "imei": imei,
            "ccid": ccid,
            "production_order": row[2].strip() if row[2] else None,
            "batch": row[4],
            "production_line": production_line,
            "status": "approved",  # Ajustar según QC
            "created_at": parse_date(row[3]),
            "updated_at": datetime.now(),
            "metadata": {
                "migrated_from": "registros_2025"
            }
        }
        
        # Insertar
        result = mongo_db.devices.insert_one(doc)
        device_id = result.inserted_id
        
        # Crear evento
        event = {
            "device_id": device_id,
            "imei": imei,
            "event_type": "production_completed",
            "timestamp": parse_date(row[3]),
            "operator": row[8].strip() if row[8] else None,
            "production_order": doc["production_order"],
            "batch": doc["batch"],
            "production_line": production_line,
            "new_status": "approved"
        }
        
        mongo_db.device_events.insert_one(event)
        
        migrated += 1
        if migrated % 1000 == 0:
            print(f"  Migrados {migrated} dispositivos...")
    
    print(f"✓ {migrated} dispositivos migrados")

# ============================================================
# 3. MIGRAR PERSONAL
# ============================================================

def migrate_employees():
    print("Migrando personal...")
    
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("""
        SELECT 
            id, name, surname, master, status,
            puesto1_linea1, puesto2_linea1,
            puesto1_linea2, puesto2_linea2,
            control_calidad,
            puesto1_linea3, puesto2_linea3
        FROM algepser.personal
    """)
    
    migrated = 0
    for row in pg_cursor.fetchall():
        # Determinar rol
        role = "operator"
        if row[3] == 1:
            role = "supervisor"
        elif row[9] == 1:
            role = "quality_inspector"
        
        # Crear documento
        doc = {
            "employee_id": row[0].strip(),
            "name": row[1].strip() if row[1] else None,
            "surname": row[2].strip() if row[2] else None,
            "role": role,
            "status": "active" if row[4] == 1 else "inactive",
            "permissions": {
                "production_line1_station1": row[5] == 1,
                "production_line1_station2": row[6] == 1,
                "production_line2_station1": row[7] == 1,
                "production_line2_station2": row[8] == 1,
                "production_line3_station1": row[10] == 1 if len(row) > 10 else False,
                "production_line3_station2": row[11] == 1 if len(row) > 11 else False,
                "quality_control": row[9] == 1,
                "admin_access": row[3] == 1
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        mongo_db.employees.insert_one(doc)
        migrated += 1
    
    print(f"✓ {migrated} empleados migrados")

# ============================================================
# UTILIDADES
# ============================================================

def parse_date(date_str):
    if not date_str:
        return None
    
    try:
        # Intentar varios formatos
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y']:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None
    except:
        return None

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MIGRACIÓN POSTGRESQL → MONGODB - OVERSUN ENERGY")
    print("=" * 70)
    print()
    
    try:
        migrate_production_orders()
        migrate_devices()
        migrate_employees()
        
        print()
        print("=" * 70)
        print("✓ MIGRACIÓN COMPLETADA")
        print("=" * 70)
        
        # Estadísticas
        stats = {
            "production_orders": mongo_db.production_orders.count_documents({}),
            "devices": mongo_db.devices.count_documents({}),
            "device_events": mongo_db.device_events.count_documents({}),
            "employees": mongo_db.employees.count_documents({})
        }
        
        print()
        print("Estadísticas finales:")
        for collection, count in stats.items():
            print(f"  {collection}: {count:,} documentos")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pg_conn.close()
        mongo_client.close()
```

---

## ✅ CHECKLIST DE MIGRACIÓN

### Pre-Migración
- [ ] Backup completo de PostgreSQL
- [ ] MongoDB instalado y configurado
- [ ] Estructura MongoDB creada
- [ ] Scripts de migración probados
- [ ] Espacio en disco verificado

### Durante Migración
- [ ] Migrar production_orders
- [ ] Migrar devices + device_events
- [ ] Migrar quality_control
- [ ] Migrar employees
- [ ] Verificar counts por tabla

### Post-Migración
- [ ] Verificar integridad de datos
- [ ] Recrear índices si necesario
- [ ] Pruebas de consultas
- [ ] Comparar totales PG vs Mongo
- [ ] Documentar cualquier dato perdido

---

## 🚨 DATOS QUE NO SE MIGRAN

### Campos de Seguridad
- `personal.secretkey` - No migrar por seguridad
- `personal_admin.key` - No migrar por seguridad

### Campos Redundantes
- Flags derivados (in_process, complete, etc.) → usar status
- Contadores que se pueden calcular

### Tablas Legacy
- Esquema "Algepser" (mayúsculas) - deprecado
- Tablas de años anteriores si no son necesarias

---

## 📞 CONTACTO

Para dudas sobre la migración, consulta la documentación principal o contacta al equipo técnico.
