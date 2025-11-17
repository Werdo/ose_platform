# Migracion PostgreSQL a MongoDB - OSE Platform

## Resumen de la Migracion

**Fecha**: 2025-11-13
**Origen**: PostgreSQL (192.168.100.118:5432, database: postgres, schema: algepser)
**Destino**: MongoDB (localhost:27018, database: ose_platform)

## Resultado de la Migracion

### Estadisticas Generales

- **Tablas totales**: 18
- **Tablas migradas exitosamente**: 11
- **Tablas vacias (omitidas)**: 7
- **Total de registros migrados**: 243,162
- **Tablas fallidas**: 0
- **Estado**: EXITOSO

## Colecciones Creadas

Todas las colecciones PostgreSQL se crearon con el prefijo `pg_` en MongoDB:

| Coleccion MongoDB | Registros | Tabla Original |
|-------------------|-----------|----------------|
| `pg_registros_2025` | 119,842 | registros_2025 |
| `pg_registros_2025_puesto2` | 119,573 | registros_2025_puesto2 |
| `pg_oem_registros` | 3,550 | oem_registros |
| `pg_control_calidad_linea1_history` | 109 | control_calidad_linea1_history |
| `pg_orden_produccion` | 57 | orden_produccion |
| `pg_personal` | 14 | personal |
| `pg_marca_referencia` | 8 | marca_referencia |
| `pg_personal_admin` | 4 | personal_admin |
| `pg_cupones_de_trabajo` | 3 | cupones_de_trabajo |
| `pg_control_calidad` | 1 | control_calidad |
| `pg_control_calidad_linea1` | 1 | control_calidad_linea1 |

## Tablas Omitidas (Vacias)

Las siguientes tablas no contenian datos y fueron omitidas:

- control_calidad_history
- control_calidad_linea2
- control_calidad_linea2_history
- cupon_de_trabajo
- cupon_de_trabajo_puesto2
- metrics
- oem_box

## Estructura de Datos

### Metadatos de Migracion

Cada documento migrado incluye los siguientes metadatos:

```javascript
{
  // ... campos originales de PostgreSQL ...
  "_migrated_from": "postgresql",
  "_migrated_at": "2025-11-13T...",
  "_original_table": "nombre_tabla"
}
```

### Ejemplo de Documento Migrado

Ejemplo de documento de `pg_registros_2025`:

```javascript
{
  "nro": 1,
  "nro_orden": "WH/MO/00032",
  "fecha": "04/02/2025 11:29:53",
  "lote": null,
  "imei": "865178065635508",
  "ccid": "8934014032312420747F",
  "linea1": null,
  "linea2": null,
  "operador": null,
  "linea3": null,
  "_migrated_from": "postgresql",
  "_migrated_at": "2025-11-13T...",
  "_original_table": "registros_2025"
}
```

## Detalles Tecnicos

### Credenciales PostgreSQL Utilizadas

```
Host: 192.168.100.118
Port: 5432
Database: postgres
Schema: algepser
User: panda
Password: [CONFIDENCIAL]
```

### Configuracion MongoDB

```
URI: mongodb://localhost:27018
Database: ose_platform
```

### Proceso de Migracion

1. **Conexion a PostgreSQL**: Conexion exitosa al schema `algepser`
2. **Conexion a MongoDB**: Conexion exitosa a puerto 27018
3. **Enumeracion de tablas**: 18 tablas encontradas
4. **Procesamiento por lotes**: Tablas grandes procesadas en lotes de 10,000 registros
5. **Limpieza de colecciones**: Documentos existentes eliminados antes de insercion
6. **Insercion de datos**: Todos los datos insertados exitosamente
7. **Metadata**: Agregados campos de trazabilidad a cada documento

### Optimizaciones Implementadas

- **Procesamiento por lotes**: Para tablas con >10,000 registros
- **Indicadores de progreso**: Para tablas grandes (registros_2025, registros_2025_puesto2)
- **Conversion de tipos**: Datetime convertido a formato ISO string
- **Manejo de valores NULL**: Preservados como null en MongoDB

## Uso de los Datos Migrados

### Consultar Datos en MongoDB

```python
from pymongo import MongoClient

# Conectar
client = MongoClient('mongodb://localhost:27018')
db = client['ose_platform']

# Obtener coleccion
registros = db['pg_registros_2025']

# Consultar datos
total = registros.count_documents({})
print(f"Total registros: {total}")

# Buscar por IMEI
registro = registros.find_one({"imei": "865178065635508"})
```

### Consultas Comunes

```javascript
// MongoDB Shell

// 1. Contar registros por tabla original
db.pg_registros_2025.countDocuments({})

// 2. Buscar por fecha
db.pg_registros_2025.find({
  fecha: { $regex: "04/02/2025" }
})

// 3. Buscar por orden de produccion
db.pg_registros_2025.find({
  nro_orden: "WH/MO/00032"
})

// 4. Listar todos los IMEIs
db.pg_registros_2025.distinct("imei")

// 5. Buscar registros migrados hoy
db.pg_registros_2025.find({
  _migrated_at: { $regex: "2025-11-13" }
})
```

## Integracion con la Plataforma OSE

### Acceso desde Backend FastAPI

Para acceder a estos datos desde la plataforma OSE:

```python
# backend-new/app/services/postgresql_data.py

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import get_settings

settings = get_settings()

class PostgreSQLDataService:
    """Servicio para acceder a datos migrados de PostgreSQL"""

    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_DB_NAME]

    async def get_registros_2025(self, skip: int = 0, limit: int = 100):
        """Obtener registros 2025"""
        collection = self.db['pg_registros_2025']
        cursor = collection.find({}).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def search_by_imei(self, imei: str):
        """Buscar por IMEI"""
        collection = self.db['pg_registros_2025']
        return await collection.find_one({"imei": imei})

    async def search_by_order(self, order_number: str):
        """Buscar por numero de orden"""
        collection = self.db['pg_registros_2025']
        cursor = collection.find({"nro_orden": order_number})
        return await cursor.to_list(length=None)
```

## Proximos Pasos

### 1. Crear Indices

Para mejorar el rendimiento de consultas:

```javascript
// Crear indices en MongoDB
db.pg_registros_2025.createIndex({ "imei": 1 })
db.pg_registros_2025.createIndex({ "ccid": 1 })
db.pg_registros_2025.createIndex({ "nro_orden": 1 })
db.pg_registros_2025.createIndex({ "fecha": 1 })

db.pg_oem_registros.createIndex({ "imei": 1 })
db.pg_orden_produccion.createIndex({ "nro_orden": 1 })
```

### 2. Crear Modelos Beanie

Para integrar con la aplicacion OSE:

```python
# backend-new/app/models/postgresql_models.py

from beanie import Document
from datetime import datetime
from typing import Optional

class Registro2025(Document):
    nro: int
    nro_orden: str
    fecha: str
    lote: Optional[str]
    imei: str
    ccid: str
    linea1: Optional[str]
    linea2: Optional[str]
    operador: Optional[str]
    linea3: Optional[str]
    _migrated_from: str
    _migrated_at: str
    _original_table: str

    class Settings:
        name = "pg_registros_2025"
```

### 3. Crear Endpoints API

Exponer los datos a traves de la API:

```python
# backend-new/app/routers/postgresql_data.py

from fastapi import APIRouter, Query
from app.services.postgresql_data import PostgreSQLDataService

router = APIRouter(prefix="/api/postgresql", tags=["PostgreSQL Data"])

@router.get("/registros-2025")
async def get_registros_2025(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Obtener registros 2025"""
    service = PostgreSQLDataService()
    return await service.get_registros_2025(skip, limit)

@router.get("/search/imei/{imei}")
async def search_by_imei(imei: str):
    """Buscar por IMEI"""
    service = PostgreSQLDataService()
    return await service.search_by_imei(imei)
```

## Mantenimiento

### Re-ejecutar la Migracion

Si necesitas volver a migrar los datos:

```bash
cd backend-new
python -c "import script_migracion"
```

El script automaticamente:
- Elimina documentos existentes en las colecciones
- Vuelve a importar todos los datos
- Actualiza las fechas de migracion

### Backup de Datos Migrados

```bash
# Exportar colecciones migradas
mongodump --port 27018 --db ose_platform --out ./backups/postgresql_migration_backup

# Restaurar desde backup
mongorestore --port 27018 --db ose_platform ./backups/postgresql_migration_backup/ose_platform
```

## Notas Importantes

1. **Prefijo `pg_`**: Todas las colecciones tienen el prefijo `pg_` para distinguirlas de colecciones nativas de OSE Platform

2. **Datos originales preservados**: Los datos originales en PostgreSQL permanecen intactos

3. **Sincronizacion**: Esta es una migracion puntual. No hay sincronizacion automatica entre PostgreSQL y MongoDB

4. **Campos NULL**: Los valores NULL de PostgreSQL se preservan como `null` en MongoDB

5. **Fechas**: Las fechas se almacenan como strings en el formato original de PostgreSQL

## Contacto y Soporte

Para preguntas sobre la migracion o los datos:
- Email: serviciorma@neowaybyose.com
- Documentacion: backend-new/POSTGRESQL_MIGRATION.md
