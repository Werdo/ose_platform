# 📊 ARQUITECTURA MongoDB - OVERSUN ENERGY
## Sistema de Gestión, Trazabilidad y Post-Venta

---

## 🏗️ ARQUITECTURA GENERAL

### Modelo de Datos
La estructura está diseñada con los siguientes principios:

1. **Trazabilidad Completa**: Cada dispositivo tiene un historial completo desde producción hasta post-venta
2. **Denormalización Estratégica**: Campos duplicados (imei, ccid) para consultas rápidas
3. **Escalabilidad**: Colecciones separadas para eventos históricos
4. **Flexibilidad**: Campos metadata para adaptarse a necesidades futuras

---

## 📋 COLECCIONES Y RELACIONES

```
┌─────────────────────────────────────────────────────────────────┐
│                        FLUJO PRINCIPAL                          │
└─────────────────────────────────────────────────────────────────┘

production_orders → devices → device_events → service_tickets → rma_cases
       ↓                ↓           ↓                ↓              ↓
   employees    quality_control  metrics        customers      inventory
```

### 1️⃣ **devices** (Colección Central)
- **Propósito**: Registro maestro de cada dispositivo único
- **Clave única**: `imei` y `ccid`
- **Relaciones**:
  - `production_order` → production_orders
  - `shipping_info.customer_id` → customers
  - Genera eventos en `device_events`

### 2️⃣ **production_orders**
- **Propósito**: Gestión de órdenes de producción
- **Clave única**: `order_number`
- **Relaciones**:
  - Múltiples devices vinculados por `production_order`
  - `responsible` → employees

### 3️⃣ **device_events** (Historial)
- **Propósito**: Trazabilidad completa del ciclo de vida
- **Indexación**: Por `device_id` y `timestamp`
- **Tipo de eventos**:
  - Producción: created, production_started, production_completed
  - Calidad: quality_check_passed, quality_check_failed
  - Logística: packed, shipped, delivered
  - Operación: activated, warranty_started
  - Post-venta: service_request, repair, replacement
  - Final: returned, retired

### 4️⃣ **service_tickets**
- **Propósito**: Gestión de incidencias y soporte técnico
- **Clave única**: `ticket_number`
- **Relaciones**:
  - `device_id` → devices
  - `customer_id` → customers
  - `assigned_to` → employees
  - Puede generar → rma_cases

### 5️⃣ **rma_cases**
- **Propósito**: Gestión de devoluciones y reemplazos
- **Clave única**: `rma_number`
- **Relaciones**:
  - `device_id` → devices (original)
  - `replacement_device_id` → devices (nuevo)
  - `customer_id` → customers
  - `service_ticket_id` → service_tickets

### 6️⃣ **customers**
- **Propósito**: Base de clientes
- **Clave única**: `customer_code`
- **Tipos**: end_user, distributor, reseller, enterprise

### 7️⃣ **employees**
- **Propósito**: Personal y permisos
- **Clave única**: `employee_id`
- **Roles**: operator, supervisor, quality_inspector, technician, admin, manager

### 8️⃣ **quality_control**
- **Propósito**: Inspecciones de calidad detalladas
- **Relaciones**:
  - `device_id` → devices
  - `inspector` → employees

### 9️⃣ **inventory**
- **Propósito**: Control de stock
- **Clave única**: `part_number`
- **Categorías**: finished_product, component, packaging, tool, consumable

### 🔟 **metrics**
- **Propósito**: KPIs agregados
- **Períodos**: daily, weekly, monthly, quarterly, yearly
- **Tipos**: Producción, calidad, servicio, satisfacción

---

## 🔍 CONSULTAS COMUNES

### Producción

#### 1. Dispositivos producidos hoy
```javascript
db.devices.find({
  created_at: {
    $gte: new Date(new Date().setHours(0, 0, 0, 0))
  }
}).count()
```

#### 2. Estado de una orden de producción
```javascript
db.devices.aggregate([
  {
    $match: { production_order: "OP-2025-0001" }
  },
  {
    $group: {
      _id: "$status",
      count: { $sum: 1 }
    }
  }
])
```

#### 3. Producción por línea del mes actual
```javascript
db.devices.aggregate([
  {
    $match: {
      created_at: {
        $gte: new Date(new Date().getFullYear(), new Date().getMonth(), 1)
      }
    }
  },
  {
    $group: {
      _id: "$production_line",
      total: { $sum: 1 },
      approved: {
        $sum: { $cond: [{ $eq: ["$status", "approved"] }, 1, 0] }
      }
    }
  }
])
```

### Trazabilidad

#### 4. Historia completa de un dispositivo
```javascript
db.device_events.find({
  imei: "123456789012345"
}).sort({ timestamp: 1 })
```

#### 5. Buscar dispositivo por IMEI con toda su información
```javascript
db.devices.aggregate([
  {
    $match: { imei: "123456789012345" }
  },
  {
    $lookup: {
      from: "device_events",
      localField: "_id",
      foreignField: "device_id",
      as: "history"
    }
  },
  {
    $lookup: {
      from: "service_tickets",
      localField: "_id",
      foreignField: "device_id",
      as: "service_history"
    }
  },
  {
    $lookup: {
      from: "quality_control",
      localField: "_id",
      foreignField: "device_id",
      as: "quality_checks"
    }
  }
])
```

#### 6. Dispositivos por ubicación
```javascript
db.devices.aggregate([
  {
    $group: {
      _id: "$current_location",
      count: { $sum: 1 }
    }
  },
  {
    $sort: { count: -1 }
  }
])
```

### Post-Venta

#### 7. Tickets abiertos por prioridad
```javascript
db.service_tickets.aggregate([
  {
    $match: {
      status: { $in: ["open", "in_progress"] }
    }
  },
  {
    $group: {
      _id: "$priority",
      count: { $sum: 1 }
    }
  },
  {
    $sort: { "_id": 1 }
  }
])
```

#### 8. Tiempo promedio de resolución de tickets
```javascript
db.service_tickets.aggregate([
  {
    $match: {
      status: "closed",
      resolution_date: { $exists: true }
    }
  },
  {
    $project: {
      resolution_time: {
        $divide: [
          { $subtract: ["$resolution_date", "$created_at"] },
          1000 * 60 * 60 // Convertir a horas
        ]
      }
    }
  },
  {
    $group: {
      _id: null,
      avg_hours: { $avg: "$resolution_time" }
    }
  }
])
```

#### 9. Dispositivos de un cliente con tickets activos
```javascript
db.devices.aggregate([
  {
    $match: {
      "shipping_info.customer_id": ObjectId("customer_id_here")
    }
  },
  {
    $lookup: {
      from: "service_tickets",
      let: { device_id: "$_id" },
      pipeline: [
        {
          $match: {
            $expr: {
              $and: [
                { $eq: ["$device_id", "$$device_id"] },
                { $in: ["$status", ["open", "in_progress"]] }
              ]
            }
          }
        }
      ],
      as: "active_tickets"
    }
  },
  {
    $match: {
      "active_tickets.0": { $exists: true }
    }
  }
])
```

### Garantías y RMA

#### 10. Dispositivos próximos a vencer garantía (30 días)
```javascript
const thirtyDaysFromNow = new Date();
thirtyDaysFromNow.setDate(thirtyDaysFromNow.getDate() + 30);

db.devices.find({
  "warranty.end_date": {
    $gte: new Date(),
    $lte: thirtyDaysFromNow
  },
  status: { $in: ["shipped", "in_service"] }
})
```

#### 11. Tasa de RMA por SKU
```javascript
db.rma_cases.aggregate([
  {
    $lookup: {
      from: "devices",
      localField: "device_id",
      foreignField: "_id",
      as: "device"
    }
  },
  {
    $unwind: "$device"
  },
  {
    $group: {
      _id: "$device.sku",
      rma_count: { $sum: 1 }
    }
  },
  {
    $lookup: {
      from: "devices",
      let: { sku: "$_id" },
      pipeline: [
        {
          $match: {
            $expr: { $eq: ["$sku", "$$sku"] }
          }
        },
        {
          $count: "total"
        }
      ],
      as: "total_devices"
    }
  },
  {
    $project: {
      sku: "$_id",
      rma_count: 1,
      total_devices: { $arrayElemAt: ["$total_devices.total", 0] },
      rma_rate: {
        $multiply: [
          {
            $divide: [
              "$rma_count",
              { $arrayElemAt: ["$total_devices.total", 0] }
            ]
          },
          100
        ]
      }
    }
  }
])
```

### Calidad

#### 12. Tasa de rechazo por línea
```javascript
db.quality_control.aggregate([
  {
    $group: {
      _id: {
        production_line: "$production_line",
        result: "$result"
      },
      count: { $sum: 1 }
    }
  },
  {
    $group: {
      _id: "$_id.production_line",
      results: {
        $push: {
          result: "$_id.result",
          count: "$count"
        }
      },
      total: { $sum: "$count" }
    }
  },
  {
    $project: {
      production_line: "$_id",
      results: 1,
      total: 1,
      rejection_rate: {
        $multiply: [
          {
            $divide: [
              {
                $sum: {
                  $map: {
                    input: "$results",
                    as: "r",
                    in: {
                      $cond: [
                        { $eq: ["$$r.result", "failed"] },
                        "$$r.count",
                        0
                      ]
                    }
                  }
                }
              },
              "$total"
            ]
          },
          100
        ]
      }
    }
  }
])
```

#### 13. Defectos más comunes
```javascript
db.quality_control.aggregate([
  {
    $match: {
      result: "failed",
      defects_found: { $exists: true }
    }
  },
  {
    $unwind: "$defects_found"
  },
  {
    $group: {
      _id: {
        category: "$defects_found.category",
        severity: "$defects_found.severity"
      },
      count: { $sum: 1 }
    }
  },
  {
    $sort: { count: -1 }
  },
  {
    $limit: 10
  }
])
```

### Clientes

#### 14. Top 10 clientes por número de dispositivos
```javascript
db.devices.aggregate([
  {
    $match: {
      "shipping_info.customer_id": { $exists: true }
    }
  },
  {
    $group: {
      _id: "$shipping_info.customer_id",
      device_count: { $sum: 1 }
    }
  },
  {
    $lookup: {
      from: "customers",
      localField: "_id",
      foreignField: "_id",
      as: "customer"
    }
  },
  {
    $unwind: "$customer"
  },
  {
    $sort: { device_count: -1 }
  },
  {
    $limit: 10
  },
  {
    $project: {
      customer_code: "$customer.customer_code",
      company_name: "$customer.company_name",
      device_count: 1
    }
  }
])
```

### Personal

#### 15. Productividad por operador
```javascript
db.device_events.aggregate([
  {
    $match: {
      event_type: "production_completed",
      timestamp: {
        $gte: new Date(new Date().setDate(new Date().getDate() - 30))
      }
    }
  },
  {
    $group: {
      _id: "$operator",
      devices_produced: { $sum: 1 }
    }
  },
  {
    $sort: { devices_produced: -1 }
  }
])
```

---

## 📊 MÉTRICAS Y KPIs RECOMENDADOS

### Producción
- Unidades producidas por línea/día/mes
- Tiempo promedio de producción por lote
- Eficiencia de línea (% tiempo productivo)
- Cumplimiento de órdenes (a tiempo vs retrasadas)

### Calidad
- Tasa de aprobación/rechazo por línea
- First Pass Yield (FPY)
- Defectos por millón de unidades (DPMU)
- Top 5 defectos más comunes

### Post-Venta
- Tiempo promedio de resolución de tickets
- Tasa de RMA por SKU
- Customer Satisfaction Score (CSAT)
- Net Promoter Score (NPS)
- Tickets abiertos vs cerrados (tendencia)

### Garantías
- Dispositivos bajo garantía activa
- Claims rate (% de dispositivos con claim)
- Costo promedio de garantía por dispositivo
- Tiempo promedio de procesamiento de RMA

---

## 🔒 SEGURIDAD Y PERMISOS

### Recomendaciones de Roles MongoDB

```javascript
// Usuario de solo lectura (dashboards, reportes)
db.createUser({
  user: "oversun_readonly",
  pwd: "secure_password",
  roles: [
    { role: "read", db: "oversun_production" }
  ]
})

// Usuario de producción (registros, actualización)
db.createUser({
  user: "oversun_production",
  pwd: "secure_password",
  roles: [
    { role: "readWrite", db: "oversun_production" }
  ]
})

// Usuario administrador
db.createUser({
  user: "oversun_admin",
  pwd: "secure_password",
  roles: [
    { role: "dbOwner", db: "oversun_production" }
  ]
})
```

---

## 🚀 OPTIMIZACIONES

### Índices Compuestos Adicionales

Para consultas frecuentes específicas:

```javascript
// Búsqueda de dispositivos por cliente y estado
db.devices.createIndex({
  "shipping_info.customer_id": 1,
  "status": 1,
  "created_at": -1
});

// Tickets por técnico asignado y estado
db.service_tickets.createIndex({
  "assigned_to": 1,
  "status": 1,
  "priority": 1
});

// Eventos por tipo y fecha para reportes
db.device_events.createIndex({
  "event_type": 1,
  "timestamp": -1,
  "production_line": 1
});

// Órdenes por estado y fecha
db.production_orders.createIndex({
  "status": 1,
  "created_at": -1,
  "production_line": 1
});
```

### Sharding Strategy (Para escala masiva)

```javascript
// Shard key por rango de fechas en device_events
sh.shardCollection("oversun_production.device_events", {
  "timestamp": 1
});

// Shard key por hash en devices (distribución uniforme)
sh.shardCollection("oversun_production.devices", {
  "_id": "hashed"
});
```

---

## 📦 MIGRACIÓN DESDE POSTGRESQL

### Mapeo de Tablas

| PostgreSQL | MongoDB | Notas |
|------------|---------|-------|
| registros_2025 | devices + device_events | Separar registro de historial |
| orden_produccion | production_orders | Estructura mejorada |
| cupones_de_trabajo | Embebido en production_orders | Como array de batches |
| personal | employees | Permisos más granulares |
| control_calidad* | quality_control | Consolidar todas las líneas |
| marca_referencia | Campo en devices/production_orders | Denormalizar |
| oem_registros | devices (con flag type) | Unificar con registros regulares |
| metrics | metrics | Agregaciones pre-calculadas |

### Script de Migración (Ejemplo)

```javascript
// Migrar registros_2025 a devices
db.registros_2025_temp.find().forEach(function(reg) {
  // Buscar o crear device
  var device = db.devices.findOne({ imei: reg.imei.trim() });
  
  if (!device) {
    db.devices.insertOne({
      imei: reg.imei.trim(),
      ccid: reg.ccid.trim(),
      production_order: reg.nro_orden.trim(),
      batch: reg.lote,
      production_line: reg.linea1 ? 1 : (reg.linea2 ? 2 : 3),
      status: "approved",
      created_at: new Date(reg.fecha),
      updated_at: new Date()
    });
    
    device = db.devices.findOne({ imei: reg.imei.trim() });
  }
  
  // Crear evento de producción
  db.device_events.insertOne({
    device_id: device._id,
    imei: device.imei,
    event_type: "production_completed",
    timestamp: new Date(reg.fecha),
    operator: reg.operador ? reg.operador.trim() : null,
    production_order: reg.nro_orden.trim(),
    batch: reg.lote,
    production_line: reg.linea1 ? 1 : (reg.linea2 ? 2 : 3),
    data: {
      migrated_from: "registros_2025",
      original_nro: reg.nro
    }
  });
});
```

---

## 🔄 MANTENIMIENTO

### Tareas Periódicas

1. **Backup diario** de colecciones críticas
2. **Análisis de índices** mensuales para optimización
3. **Limpieza de eventos** antiguos (> 2 años) mediante archiving
4. **Recálculo de métricas** diarias mediante aggregation pipelines
5. **Actualización de contadores** en customers (devices_count, tickets_count)

### Archiving de Datos Históricos

```javascript
// Mover eventos antiguos a colección de archivo
var twoYearsAgo = new Date();
twoYearsAgo.setFullYear(twoYearsAgo.getFullYear() - 2);

db.device_events.aggregate([
  {
    $match: {
      timestamp: { $lt: twoYearsAgo }
    }
  },
  {
    $out: "device_events_archive_2023"
  }
]);

// Eliminar de colección principal
db.device_events.deleteMany({
  timestamp: { $lt: twoYearsAgo }
});
```

---

## 📱 INTEGRACIONES RECOMENDADAS

### APIs Externas
- **ERP**: Sincronización de órdenes de producción
- **CRM**: Datos de clientes y contratos
- **Logística**: Tracking de envíos
- **Email/SMS**: Notificaciones de tickets y RMA

### Aplicaciones
- **Dashboard Web**: Vue.js + Chart.js para métricas en tiempo real
- **App Móvil**: React Native para operadores en planta
- **Portal Cliente**: Consulta de garantías y apertura de tickets
- **Sistema de Tickets**: Integración con Zendesk/Freshdesk

---

## 💡 PRÓXIMOS PASOS

1. ✅ Crear estructura en MongoDB
2. ⚙️ Desarrollar API REST con FastAPI
3. 🔄 Script de migración desde PostgreSQL
4. 📊 Dashboard de métricas
5. 🔐 Sistema de autenticación y autorización
6. 📱 Portal de cliente
7. 🤖 Automatizaciones y notificaciones
