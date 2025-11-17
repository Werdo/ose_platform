# Sincronización PostgreSQL a MongoDB - Guía de Uso

## Resumen

Este proyecto incluye dos scripts para gestionar los datos de PostgreSQL:

1. **Migración Completa**: Importa todos los datos (borra y re-importa todo)
2. **Sincronización Incremental**: Solo importa registros nuevos ✅ RECOMENDADO

## Scripts Disponibles

### 1. Migración Completa
**Archivo**: `scripts/migrate_postgresql.py`
**Cuándo usar**: Solo la primera vez o para resetear completamente los datos

```bash
cd backend-new
python scripts/migrate_postgresql.py
```

**Comportamiento**:
- ❌ Borra todos los datos existentes en MongoDB
- ✅ Re-importa todos los registros desde PostgreSQL
- ⚠️ Puede tardar varios minutos
- ⚠️ Sobrescribe fechas de migración

### 2. Sincronización Incremental ✅ RECOMENDADO
**Archivo**: `scripts/sync_postgresql_incremental.py`
**Cuándo usar**: Para actualizaciones diarias/regulares

```bash
cd backend-new
python scripts/sync_postgresql_incremental.py
```

**Comportamiento**:
- ✅ Solo trae registros nuevos
- ✅ No borra datos existentes
- ✅ Muy rápido (segundos)
- ✅ Seguro de ejecutar múltiples veces

## Tablas Sincronizadas

El script de sincronización incremental trabaja con 4 tablas principales:

| Tabla PostgreSQL | Colección MongoDB | Campo Único | Registros Actuales |
|------------------|-------------------|-------------|-------------------|
| `registros_2025` | `pg_registros_2025` | `nro` | ~119,842 |
| `registros_2025_puesto2` | `pg_registros_2025_puesto2` | `nro` | ~119,573 |
| `oem_registros` | `pg_oem_registros` | `nro` | ~3,550 |
| `personal_admin` | `pg_personal_admin` | `nro` | ~4 |

**Total**: ~243,000 registros

## Cómo Funciona la Sincronización Incremental

### Proceso

1. **Consulta MongoDB** - Obtiene el valor máximo del campo `nro` en cada colección
2. **Consulta PostgreSQL** - Solo trae registros donde `nro > máximo_mongodb`
3. **Inserta nuevos** - Solo añade los registros que no existen

### Ejemplo

```
MongoDB tiene: registros con nro del 1 al 119,842
PostgreSQL tiene: registros con nro del 1 al 119,900

Resultado: Solo importa 58 registros nuevos (119,843 a 119,900)
```

## Configuración

### Credenciales PostgreSQL

En el archivo `scripts/sync_postgresql_incremental.py`:

```python
POSTGRESQL_CONFIG = {
    'host': '192.168.100.118',
    'port': 5432,
    'database': 'postgres',
    'user': 'panda',
    'password': 'f2e2l1i9x6',
    'schema': 'algepser'
}
```

### Configuración MongoDB

Se obtiene automáticamente de `app/config.py`:
- URI: `mongodb://localhost:27018`
- Database: `ose_platform`

## Uso Recomendado

### Primera Vez

```bash
# 1. Migración completa inicial
cd backend-new
python scripts/migrate_postgresql.py
```

### Actualizaciones Diarias

```bash
# 2. Sincronización incremental (ejecutar diariamente)
cd backend-new
python scripts/sync_postgresql_incremental.py
```

### Automatización con Cron (Linux/Mac)

```cron
# Ejecutar cada día a las 2 AM
0 2 * * * cd /ruta/al/proyecto/backend-new && python scripts/sync_postgresql_incremental.py >> /var/log/pg_sync.log 2>&1
```

### Automatización con Task Scheduler (Windows)

1. Abrir **Programador de tareas**
2. Crear **Tarea básica**
3. Nombre: "PostgreSQL Sync"
4. Desencadenador: **Diariamente** a las **2:00 AM**
5. Acción: **Iniciar programa**
   - Programa: `C:\Python\python.exe`
   - Argumentos: `scripts\sync_postgresql_incremental.py`
   - Carpeta: `C:\ruta\al\proyecto\backend-new`

## Salida del Script

### Cuando TODO está actualizado

```
================================================================================
PostgreSQL to MongoDB - INCREMENTAL SYNC
================================================================================

[OK] PostgreSQL connection: 192.168.100.118:5432
[OK] MongoDB connection: mongodb://localhost:27018

================================================================================
Source: PostgreSQL at 192.168.100.118, schema algepser
Target: MongoDB at mongodb://localhost:27018, database ose_platform
Mode: INCREMENTAL (only new records)
================================================================================

Processing table: registros_2025
  Max nro in MongoDB: 119842
  New records in PostgreSQL: 0
  Status: UP TO DATE (no new records)

Processing table: registros_2025_puesto2
  Max nro in MongoDB: 119573
  New records in PostgreSQL: 0
  Status: UP TO DATE (no new records)

Processing table: oem_registros
  Max nro in MongoDB: 3550
  New records in PostgreSQL: 0
  Status: UP TO DATE (no new records)

Processing table: personal_admin
  Max nro in MongoDB: 4
  New records in PostgreSQL: 0
  Status: UP TO DATE (no new records)

================================================================================
Sync Summary
================================================================================
Total tables: 4
Tables with new data: 0
Tables up to date: 4
Failed: 0
Total new records synced: 0
================================================================================

[SUCCESS] Sync completed! All tables are up to date.
```

### Cuando hay NUEVOS registros

```
Processing table: registros_2025
  Max nro in MongoDB: 119842
  New records in PostgreSQL: 58
  Progress: 58/58 (100%)
  Inserted 58 new records into collection: pg_registros_2025
  Status: SUCCESS

================================================================================
Sync Summary
================================================================================
Total tables: 4
Tables with new data: 1
Tables up to date: 3
Failed: 0
Total new records synced: 58
================================================================================

[SUCCESS] Sync completed! 58 new records added.
```

## Verificación de Datos

### Ver registros más recientes

```python
from pymongo import MongoClient

# Conectar
client = MongoClient('mongodb://localhost:27018')
db = client['ose_platform']

# Ver últimos 5 registros de registros_2025
registros = db['pg_registros_2025'].find().sort('nro', -1).limit(5)

for reg in registros:
    print(f"NRO: {reg['nro']}, IMEI: {reg['imei']}, Fecha: {reg['fecha']}")
```

### Contar registros por tabla

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27018')
db = client['ose_platform']

tables = [
    'pg_registros_2025',
    'pg_registros_2025_puesto2',
    'pg_oem_registros',
    'pg_personal_admin'
]

for table in tables:
    count = db[table].count_documents({})
    print(f'{table}: {count:,} registros')
```

## Troubleshooting

### Error: "PostgreSQL connection failed"

**Causa**: No se puede conectar a PostgreSQL

**Solución**:
1. Verificar que PostgreSQL está corriendo
2. Verificar credenciales en el script
3. Verificar conectividad de red (ping 192.168.100.118)

### Error: "MongoDB connection failed"

**Causa**: MongoDB no está corriendo o puerto incorrecto

**Solución**:
1. Verificar que MongoDB está corriendo: `mongosh --port 27018`
2. Verificar puerto en `.env` file

### Sin nuevos registros pero deberían existir

**Causa**: El campo `nro` en PostgreSQL no es secuencial

**Solución**:
Ejecutar migración completa una vez:
```bash
python scripts/migrate_postgresql.py
```

## Añadir Nuevas Tablas

Si quieres sincronizar tablas adicionales:

1. Abre `scripts/sync_postgresql_incremental.py`
2. Añade la tabla a `TABLE_CONFIG`:

```python
TABLE_CONFIG = {
    # Existentes...
    'registros_2025': {'unique_field': 'nro'},

    # Nueva tabla
    'nueva_tabla': {'unique_field': 'id_campo_unico'},
}
```

3. **Requisitos**:
   - La tabla debe tener un campo único numérico
   - El campo debe ser auto-incremental o secuencial
   - Los valores deben incrementar con nuevos registros

## Scripts Disponibles

| Script | Propósito | Cuándo Usar |
|--------|-----------|-------------|
| `migrate_postgresql.py` | Migración completa | Primera vez o reset total |
| `sync_postgresql_incremental.py` | Solo nuevos registros | Actualizaciones regulares |

## Comparación

| Característica | Migración Completa | Sincronización Incremental |
|----------------|-------------------|---------------------------|
| **Borra datos existentes** | ✅ Sí | ❌ No |
| **Tiempo de ejecución** | Varios minutos | Segundos |
| **Registros procesados** | Todos (~243k) | Solo nuevos |
| **Uso de recursos** | Alto | Bajo |
| **Seguro para prod** | ⚠️ Con cuidado | ✅ Sí |
| **Frecuencia recomendada** | Una vez | Diario/On-demand |

## Monitoreo

Para monitorear la sincronización, puedes crear un log:

```bash
# Ejecutar con log
python scripts/sync_postgresql_incremental.py >> /var/log/pg_sync.log 2>&1

# Ver últimas 20 líneas del log
tail -20 /var/log/pg_sync.log

# Ver solo las sincronizaciones exitosas
grep "SUCCESS" /var/log/pg_sync.log
```

## Preguntas Frecuentes

### ¿Puedo ejecutar el sync incremental varias veces al día?

✅ Sí, es completamente seguro. Si no hay nuevos registros, simplemente dirá que todo está actualizado.

### ¿Qué pasa si añado un registro antiguo en PostgreSQL?

❌ NO se sincronizará. El script solo toma registros con `nro` mayor al máximo existente en MongoDB.

### ¿Puedo hacer rollback?

⚠️ Con migración completa NO (borra todo).
✅ Con sync incremental SÍ (puedes borrar los documentos nuevos manualmente).

### ¿Afecta al rendimiento de la base de datos?

❌ No. El script lee de PostgreSQL y escribe en MongoDB sin afectar consultas en producción.

## Soporte

Para problemas o preguntas:
- Email: serviciorma@neowaybyose.com
- Documentación: backend-new/POSTGRESQL_SYNC_README.md
- Migración completa: backend-new/POSTGRESQL_MIGRATION.md
