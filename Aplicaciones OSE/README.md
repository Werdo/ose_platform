# 🚀 SISTEMA DE GESTIÓN OVERSUN ENERGY
## Migración PostgreSQL → MongoDB + API REST

---

## 📁 Estructura de Archivos

```
oversun-mongodb/
├── mongodb_schema_design.js      # Esquemas y validación de MongoDB
├── ARQUITECTURA_MONGODB.md       # Documentación completa de arquitectura
├── sample_data.js                # Datos de ejemplo para testing
├── init_mongodb.sh               # Script de inicialización automática
├── README.md                     # Este archivo
└── api/                          # (Próximo paso - API FastAPI)
    ├── main.py
    ├── models/
    ├── routes/
    └── requirements.txt
```

---

## 🎯 OBJETIVOS DEL PROYECTO

1. ✅ Crear estructura optimizada en MongoDB
2. ⚙️ Desarrollar API REST para acceso a datos
3. 🔄 Migrar datos desde PostgreSQL
4. 📊 Sistema de trazabilidad completo
5. 🎫 Módulo de post-venta y RMA
6. 📈 Dashboard de métricas

---

## 📋 PREREQUISITOS

### Software Requerido

- **MongoDB 6.0+** 
  ```bash
  # Ubuntu/Debian
  wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
  echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
  sudo apt update
  sudo apt install -y mongodb-org
  sudo systemctl start mongod
  sudo systemctl enable mongod
  ```

- **Python 3.10+** (para API)
  ```bash
  sudo apt install python3 python3-pip python3-venv
  ```

- **PostgreSQL Client** (para migración)
  ```bash
  sudo apt install postgresql-client
  ```

---

## 🚀 INSTALACIÓN RÁPIDA

### Paso 1: Iniciar MongoDB

```bash
# Iniciar servicio
sudo systemctl start mongod

# Verificar estado
sudo systemctl status mongod

# Conectar a MongoDB
mongosh
```

### Paso 2: Crear Base de Datos y Estructura

```bash
# Opción A: Manual
mongosh oversun_production < mongodb_schema_design.js

# Opción B: Automática (recomendada)
chmod +x init_mongodb.sh
./init_mongodb.sh
```

### Paso 3: Cargar Datos de Ejemplo (Opcional)

```bash
mongosh oversun_production < sample_data.js
```

---

## 🔧 CONFIGURACIÓN DETALLADA

### 1. Configuración de MongoDB

#### Crear usuario administrador

```javascript
// Conectar a MongoDB
mongosh

// Usar base de datos admin
use admin

// Crear usuario admin
db.createUser({
  user: "oversun_admin",
  pwd: "TU_PASSWORD_SEGURO_AQUI",
  roles: [
    { role: "userAdminAnyDatabase", db: "admin" },
    { role: "readWriteAnyDatabase", db: "admin" }
  ]
})
```

#### Crear usuarios específicos

```javascript
// Cambiar a base de datos de producción
use oversun_production

// Usuario de aplicación (lectura/escritura)
db.createUser({
  user: "oversun_api",
  pwd: "API_PASSWORD_AQUI",
  roles: [
    { role: "readWrite", db: "oversun_production" }
  ]
})

// Usuario de solo lectura (reportes/dashboards)
db.createUser({
  user: "oversun_readonly",
  pwd: "READONLY_PASSWORD_AQUI",
  roles: [
    { role: "read", db: "oversun_production" }
  ]
})
```

#### Habilitar autenticación (Producción)

```bash
# Editar archivo de configuración
sudo nano /etc/mongod.conf

# Añadir o descomentar:
security:
  authorization: enabled

# Reiniciar servicio
sudo systemctl restart mongod
```

### 2. Verificar Instalación

```javascript
// Conectar a la base de datos
mongosh "mongodb://oversun_api:API_PASSWORD@localhost:27017/oversun_production"

// Verificar colecciones
show collections

// Debe mostrar:
// - customers
// - devices
// - device_events
// - employees
// - inventory
// - metrics
// - production_orders
// - quality_control
// - rma_cases
// - service_tickets

// Verificar índices
db.devices.getIndexes()

// Verificar vistas
show collections
// Debe incluir:
// - devices_under_warranty
// - open_tickets_by_priority
// - today_production
```

---

## 📊 USO BÁSICO

### Consultas Comunes

#### 1. Buscar dispositivo por IMEI
```javascript
db.devices.findOne({ imei: "356789123456789" })
```

#### 2. Ver historial completo de un dispositivo
```javascript
const device = db.devices.findOne({ imei: "356789123456789" })
db.device_events.find({ device_id: device._id }).sort({ timestamp: 1 })
```

#### 3. Listar órdenes de producción activas
```javascript
db.production_orders.find({
  status: { $in: ["pending", "in_progress"] }
}).sort({ created_at: -1 })
```

#### 4. Tickets abiertos de alta prioridad
```javascript
db.service_tickets.find({
  status: { $in: ["open", "in_progress"] },
  priority: { $in: ["high", "critical"] }
}).sort({ created_at: -1 })
```

#### 5. Producción del día actual
```javascript
db.today_production.find()
```

#### 6. Dispositivos bajo garantía
```javascript
db.devices_under_warranty.find().limit(10)
```

#### 7. Tasa de calidad por línea
```javascript
db.quality_control.aggregate([
  {
    $group: {
      _id: "$production_line",
      total: { $sum: 1 },
      passed: {
        $sum: { $cond: [{ $eq: ["$result", "passed"] }, 1, 0] }
      }
    }
  },
  {
    $project: {
      production_line: "$_id",
      total: 1,
      passed: 1,
      pass_rate: {
        $multiply: [{ $divide: ["$passed", "$total"] }, 100]
      }
    }
  }
])
```

---

## 🔄 MIGRACIÓN DESDE POSTGRESQL

### Conexión a PostgreSQL Origen

```bash
# Variables de entorno
export PGHOST="tu_host_postgres"
export PGPORT="5432"
export PGDATABASE="oversunserverDB"
export PGUSER="panda"
export PGPASSWORD="tu_password"

# Test de conexión
psql -c "SELECT version();"
```

### Script de Migración (Python)

Próximo archivo a crear: `migration_script.py`

```python
# Ejemplo básico de migración
import psycopg2
from pymongo import MongoClient
from datetime import datetime

# Conectar a PostgreSQL
pg_conn = psycopg2.connect(
    host="localhost",
    database="oversunserverDB",
    user="panda",
    password="password"
)

# Conectar a MongoDB
mongo_client = MongoClient("mongodb://oversun_api:password@localhost:27017/")
mongo_db = mongo_client["oversun_production"]

# Migrar registros_2025 → devices + device_events
pg_cursor = pg_conn.cursor()
pg_cursor.execute("SELECT * FROM algepser.registros_2025 LIMIT 100")

for row in pg_cursor.fetchall():
    # Crear documento de dispositivo
    device = {
        "imei": row[4].strip(),
        "ccid": row[5].strip(),
        "production_order": row[1].strip(),
        "batch": row[3],
        "production_line": 1 if row[6] else (2 if row[7] else 3),
        "status": "approved",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    # Insertar en MongoDB
    result = mongo_db.devices.insert_one(device)
    
    # Crear evento
    event = {
        "device_id": result.inserted_id,
        "imei": device["imei"],
        "event_type": "production_completed",
        "timestamp": datetime.now(),
        "operator": row[8].strip() if row[8] else None,
        "production_order": device["production_order"],
        "batch": device["batch"],
        "production_line": device["production_line"]
    }
    
    mongo_db.device_events.insert_one(event)

print("Migración completada")
```

---

## 🔐 SEGURIDAD

### Buenas Prácticas

1. **Nunca** uses credenciales en código fuente
2. Usa variables de entorno:
   ```bash
   export MONGODB_URI="mongodb://user:pass@host:port/database"
   ```
3. Habilita SSL/TLS en producción
4. Implementa rate limiting en la API
5. Audita accesos regularmente
6. Backups automáticos diarios

### Backup y Restauración

```bash
# Backup completo
mongodump --uri="mongodb://user:pass@localhost:27017/oversun_production" --out=/backups/$(date +%Y%m%d)

# Restaurar backup
mongorestore --uri="mongodb://user:pass@localhost:27017/oversun_production" /backups/20250115

# Backup de una colección específica
mongodump --uri="mongodb://user:pass@localhost:27017/oversun_production" --collection=devices --out=/backups/devices_$(date +%Y%m%d)
```

---

## 📈 MONITOREO

### Comandos Útiles

```javascript
// Estado de la base de datos
db.stats()

// Tamaño de colecciones
db.devices.stats()
db.device_events.stats()

// Operaciones en curso
db.currentOp()

// Índices más usados
db.devices.aggregate([{ $indexStats: {} }])

// Queries lentas
db.setProfilingLevel(2)
db.system.profile.find().sort({ ts: -1 }).limit(5)
```

### Logs

```bash
# Ver logs de MongoDB
sudo tail -f /var/log/mongodb/mongod.log

# Logs de queries lentas
mongosh oversun_production --eval "db.setProfilingLevel(1, { slowms: 100 })"
```

---

## 🧪 TESTING

### Validar Estructura

```bash
# Ejecutar test de esquemas
mongosh oversun_production --eval "
  // Test 1: Insertar dispositivo válido
  try {
    db.devices.insertOne({
      imei: '999999999999999',
      ccid: '99999999999999999999',
      production_order: 'TEST-001',
      status: 'approved',
      created_at: new Date()
    });
    print('✅ Test 1: OK');
  } catch(e) {
    print('❌ Test 1: FAIL - ' + e);
  }
  
  // Test 2: Intentar insertar dispositivo inválido (debe fallar)
  try {
    db.devices.insertOne({
      imei: 'invalid',
      status: 'invalid_status'
    });
    print('❌ Test 2: FAIL - Validación no funcionó');
  } catch(e) {
    print('✅ Test 2: OK - Validación funcionó correctamente');
  }
  
  // Limpiar tests
  db.devices.deleteOne({ imei: '999999999999999' });
"
```

---

## 🎯 PRÓXIMOS PASOS

### 1. API REST (FastAPI)
- [ ] Crear endpoints CRUD para cada colección
- [ ] Autenticación JWT
- [ ] Documentación Swagger automática
- [ ] Rate limiting y validación

### 2. Script de Migración Completo
- [ ] Mapeo completo de todas las tablas PostgreSQL
- [ ] Transformación de datos
- [ ] Validación post-migración
- [ ] Rollback en caso de error

### 3. Dashboard Web
- [ ] Vue.js + Chart.js
- [ ] Métricas en tiempo real
- [ ] Visualización de trazabilidad
- [ ] Panel de control de calidad

### 4. Sistema de Notificaciones
- [ ] Emails automáticos para RMA
- [ ] Alertas de tickets críticos
- [ ] Notificaciones de garantías próximas a vencer

---

## 📞 SOPORTE

Para dudas o problemas:
- Revisa la documentación en `ARQUITECTURA_MONGODB.md`
- Consulta los ejemplos en `sample_data.js`
- Verifica logs: `sudo tail -f /var/log/mongodb/mongod.log`

---

## 📝 CHANGELOG

### v1.0.0 (2025-01-15)
- ✅ Estructura inicial de MongoDB
- ✅ 10 colecciones principales
- ✅ Esquemas de validación
- ✅ Índices optimizados
- ✅ Vistas para consultas frecuentes
- ✅ Datos de ejemplo
- ✅ Documentación completa

### v1.1.0 (Próximo)
- ⏳ API REST con FastAPI
- ⏳ Script de migración desde PostgreSQL
- ⏳ Sistema de autenticación

---

## 📄 LICENCIA

Uso interno de Oversun Energy - Todos los derechos reservados
