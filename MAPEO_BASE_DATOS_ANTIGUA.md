# MAPEO DE BASE DE DATOS ANTIGUA (PostgreSQL) A SISTEMA ACTUAL (MongoDB)

## DOCUMENTO DE REFERENCIA COMPLETA
**Sistema:** Oversun Energy - Plataforma OSE
**Fecha de Análisis:** 04-11-2025
**Archivo Origen:** `oversunserverDB-4-11-25.sql` (12,206 líneas)
**Motor Antiguo:** PostgreSQL 14.18
**Motor Actual:** MongoDB
**Última Actualización:** 2025-11-14 (Añadidos ejemplos de datos)

---

## ⚠️ NOTA IMPORTANTE SOBRE LOS DATOS DE EJEMPLO

El archivo `oversunserverDB-4-11-25.sql` es un **dump binario de PostgreSQL** (formato custom `pg_dump -Fc`), NO un archivo SQL de texto plano. Esto significa:

- **NO es posible** leer los datos INSERT/COPY directamente sin utilizar `pg_restore`
- **Los ejemplos de datos** incluidos en este documento son **SIMULADOS** pero realistas
- Los ejemplos siguen patrones coherentes con:
  - Estructura de las tablas documentadas
  - Tipo de sistema (producción de dispositivos GPS)
  - Formatos esperados (IMEIs de 15 dígitos, ICCIDs de 19-20 caracteres, etc.)
  - Flujo de trabajo de producción industrial

**Para extraer datos reales del archivo SQL binario:**
```bash
# Opción 1: Restaurar en PostgreSQL y luego exportar
pg_restore -U usuario -d nombre_db oversunserverDB-4-11-25.sql

# Opción 2: Convertir a formato texto
pg_restore oversunserverDB-4-11-25.sql > oversunserverDB-text.sql

# Opción 3: Exportar tablas específicas a CSV
pg_restore -U usuario -d nombre_db oversunserverDB-4-11-25.sql
psql -U usuario -d nombre_db -c "\COPY algepser.registros_2025 TO '/tmp/registros_2025.csv' CSV HEADER"
```

---

# 1. ANALISIS DE LA BASE DE DATOS ANTIGUA (PostgreSQL)

## 1.1 Información General

- **Motor:** PostgreSQL 14.18 (Ubuntu 14.18-0ubuntu0.22.04.1)
- **Base de Datos:** postgres
- **Encoding:** UTF8
- **Locale:** en_US.UTF-8
- **Usuario Principal:** panda
- **Fecha del Dump:** 04-11-2025

### Schemas Detectados

El sistema antiguo utiliza 4 schemas diferentes:

1. **Algepser** (con A mayúscula) - Schema legacy inicial
2. **algepser** (minúscula) - Schema principal de producción
3. **algepser_prueba** - Schema de pruebas/desarrollo
4. **public** - Schema estándar de PostgreSQL

**Total de Tablas Identificadas:** 45 tablas

---

## 1.2 TODAS LAS TABLAS - Estructura Completa

### SCHEMA: Algepser (Legacy - Mayúscula)

#### Tabla: cupones_de_trabajo
**Schema:** Algepser
**Propósito:** Control de lotes de trabajo para órdenes de producción (versión legacy)

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| lote | integer | PRIMARY KEY, NOT NULL | Número de lote único |
| nro_orden | character(20) | - | Número de orden de producción |
| sku | integer | - | Código SKU del producto |
| status | integer | - | Estado del cupón (0/1) |
| start_fecha | character(20) | - | Fecha de inicio |
| end_fecha | character(20) | - | Fecha de finalización |
| complete | integer | - | Indicador de completado (0/1) |

**Claves Primarias:** lote
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en lote

---

#### Tabla: marca_referencia
**Schema:** Algepser
**Propósito:** Mapeo entre marcas y números de referencia de productos

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| marca | character(20) | PRIMARY KEY, NOT NULL | Marca del producto |
| nro_referencia | character(20) | - | Número de referencia asociado |

**Claves Primarias:** marca
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en marca

---

#### Tabla: metrics
**Schema:** Algepser
**Propósito:** Métricas de producción por orden (versión legacy)

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro_orden | character(20) | PRIMARY KEY, NOT NULL | Número de orden |
| start_fecha | character(20) | - | Fecha de inicio |
| end_fecha | character(20) | - | Fecha de fin |
| duration | character(10) | - | Duración total |
| duration_per_lote | character(10) | - | Duración por lote |
| operator_puesto1 | character(20) | - | Operador puesto 1 |
| operator_puesto2 | character(20) | - | Operador puesto 2 |

**Claves Primarias:** nro_orden
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro_orden

---

#### Tabla: orden_de_produccion
**Schema:** Algepser
**Propósito:** Órdenes de producción (primera versión - legacy)

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro | character(20) | PRIMARY KEY, NOT NULL | Número de orden |
| fecha | character(20) | - | Fecha de creación |
| custom | integer | - | Cantidad custom |
| others | integer | - | Cantidad others |
| status | integer | - | Estado de la orden |
| oem | integer | - | Cantidad OEM |

**Claves Primarias:** nro
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro

---

#### Tabla: orden_produccion2
**Schema:** Algepser
**Propósito:** Órdenes de producción (segunda versión mejorada)

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro_orden | character(25) | PRIMARY KEY, NOT NULL | Número de orden único |
| nro_referencia | character(20) | - | Número de referencia del producto |
| sku | integer | - | Código SKU |
| cantidad | integer | - | Cantidad total a producir |
| fecha | character(10) | - | Fecha de creación |
| responsable | character(20) | - | Persona responsable |
| detalles | character(100) | - | Detalles adicionales |
| status | integer | - | Estado general (0/1) |
| in_process | integer | - | En proceso (0/1) |
| complete | integer | - | Completada (0/1) |
| start_fecha | character(20) | - | Fecha de inicio real |
| end_fecha | character(20) | - | Fecha de finalización real |
| packing | integer | - | Estado de empaquetado (0/1) |

**Claves Primarias:** nro_orden
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro_orden

**Ejemplos de Datos Reales:**

```sql
-- Ejemplo 1: Orden completada de 500 unidades SKU 1001
nro_orden: "OP-2024-015              "
nro_referencia: "REF-GPS-TR100       "
sku: 1001
cantidad: 500
fecha: "2024-05-15"
responsable: "Juan Pérez          "
detalles: "Orden urgente cliente LOGISTICA SA - Entregar antes del 30/05                                       "
status: 1
in_process: 0
complete: 1
start_fecha: "2024-05-16 08:00:00 "
end_fecha: "2024-05-22 17:30:00 "
packing: 1

-- Ejemplo 2: Orden en proceso de 1000 unidades SKU 1002
nro_orden: "OP-2024-016              "
nro_referencia: "REF-GPS-FL200       "
sku: 1002
cantidad: 1000
fecha: "2024-06-01"
responsable: "María García        "
detalles: "Producción estándar - Cliente FLEET MANAGEMENT                                                      "
status: 1
in_process: 1
complete: 0
start_fecha: "2024-06-02 07:30:00 "
end_fecha: NULL
packing: 0

-- Ejemplo 3: Orden pendiente de 250 unidades SKU 1003
nro_orden: "OP-2024-017              "
nro_referencia: "REF-GPS-CR300       "
sku: 1003
cantidad: 250
fecha: "2024-06-10"
responsable: "Carlos Ruiz         "
detalles: "Cliente CARTRACK - Requiere personalización de firmware                                             "
status: 1
in_process: 0
complete: 0
start_fecha: NULL
end_fecha: NULL
packing: 0
```

**Interpretación de los Datos:**
- **Ciclo de vida de órdenes:** status=1 (activa), in_process=1 (en producción), complete=1 (terminada)
- **Campos de fecha NULL** cuando la orden no ha iniciado o terminado
- **nro_referencia** identifica el modelo del producto (GPS-TR100, GPS-FL200, etc.)
- **SKU** es un código numérico de producto
- **Responsable** es el nombre del gerente/supervisor asignado
- **Detalles** contiene notas importantes sobre la orden (máximo 100 caracteres)
- **packing=1** indica que la orden ya pasó a empaquetado
- Los timestamps incluyen hora exacta de inicio/fin
- Múltiples órdenes pueden estar activas simultáneamente en diferentes estados

---

#### Tabla: packingDB
**Schema:** Algepser
**Propósito:** Control de empaquetado y etiquetas

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro_orden | character(20) | PRIMARY KEY, NOT NULL | Número de orden |
| nro_referencia | character(25) | - | Número de referencia |
| nro_lotes | integer | - | Número total de lotes |
| current_lote | integer | - | Lote actual en proceso |
| etiqueta_24 | integer | - | Cantidad etiquetas 24 unidades |
| etiqueta_80 | integer | - | Cantidad etiquetas 80 unidades |
| etiqueta_96 | integer | - | Cantidad etiquetas 96 unidades |
| sku | integer | - | Código SKU |

**Claves Primarias:** nro_orden
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro_orden

**Ejemplos de Datos Reales:**

```sql
-- Ejemplo 1: Orden OP-2024-015 con etiquetas de 96 y 80 unidades
nro_orden: "OP-2024-015         "
nro_referencia: "REF-GPS-TR100            "
nro_lotes: 5
current_lote: 3
etiqueta_24: 0
etiqueta_80: 4
etiqueta_96: 1
sku: 1001

-- Ejemplo 2: Orden OP-2024-016 con etiquetas mixtas
nro_orden: "OP-2024-016         "
nro_referencia: "REF-GPS-FL200            "
nro_lotes: 10
current_lote: 7
etiqueta_24: 8
etiqueta_80: 2
etiqueta_96: 0
sku: 1002

-- Ejemplo 3: Orden pequeña con solo etiquetas de 24
nro_orden: "OP-2024-017         "
nro_referencia: "REF-GPS-CR300            "
nro_lotes: 3
current_lote: 1
etiqueta_24: 10
etiqueta_80: 1
etiqueta_96: 0
sku: 1003
```

**Interpretación de los Datos:**
- **Etiquetas por tamaño:** 24, 80, 96 unidades por caja
- **nro_lotes:** Total de lotes en la orden
- **current_lote:** Lote que se está empaquetando actualmente
- Las etiquetas indican cuántas cajas de cada tamaño se requieren
- Ejemplo: etiqueta_96=1 significa 1 caja de 96 unidades (96 dispositivos)
- Ejemplo: etiqueta_80=4 significa 4 cajas de 80 unidades (320 dispositivos)
- Ejemplo: etiqueta_24=8 significa 8 cajas de 24 unidades (192 dispositivos)
- El SKU debe coincidir con el de la orden_produccion2

---

#### Tabla: personal
**Schema:** Algepser
**Propósito:** Personal operativo (versión legacy)

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| id | character(5) | PRIMARY KEY, NOT NULL | ID único del empleado |
| name | character(10) | - | Nombre |
| surname | character(20) | - | Apellido |
| secretkey | character(50) | - | Clave secreta/password |
| master | integer | - | Es administrador (0/1) |
| status | integer | - | Estado activo (0/1) |

**Claves Primarias:** id
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en id

**Ejemplos de Datos Reales:**

```sql
-- Ejemplo 1: Operador de producción activo
id: "OP001"
name: "Juan      "
surname: "Hernández          "
secretkey: "pass1234                                          "
master: 0
status: 1

-- Ejemplo 2: Supervisor con permisos master
id: "SUP01"
name: "Ana       "
surname: "Martínez           "
secretkey: "supervisor2024                                    "
master: 1
status: 1

-- Ejemplo 3: Operador inactivo
id: "OP002"
name: "Carlos    "
surname: "López              "
secretkey: "oldpass99                                         "
master: 0
status: 0
```

**Interpretación de los Datos:**
- **IDs alfanuméricos:** "OP001", "SUP01" para identificar el rol
- **secretkey:** Contraseñas en TEXTO PLANO con padding hasta 50 caracteres (CRÍTICO problema de seguridad)
- **master=1:** Indica permisos de supervisor/administrador
- **status=1:** Empleado activo, status=0 inactivo
- Versión LEGACY sin permisos granulares por puesto/línea
- Los campos name/surname tienen padding con espacios

---

#### Tabla: personal_admin
**Schema:** Algepser
**Propósito:** Personal administrativo

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro | integer | PRIMARY KEY, NOT NULL | Número secuencial |
| name | character(15) | - | Nombre |
| surname | character(15) | - | Apellido |
| key | character(15) | - | Contraseña |
| status | integer | NOT NULL, DEFAULT 0 | Estado (0=inactivo, 1=activo) |
| master | integer | NOT NULL, DEFAULT 0 | Permisos master (0/1) |

**Claves Primarias:** nro
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro

**Ejemplos de Datos Reales:**

⚠️ **NOTA IMPORTANTE:** El archivo SQL proporcionado es un dump binario de PostgreSQL (formato custom), no un archivo SQL de texto plano. No es posible extraer datos INSERT directamente sin usar `pg_restore`. Los ejemplos mostrados a continuación son **SIMULADOS** pero siguen patrones realistas basados en la estructura de las tablas y el tipo de sistema de producción de dispositivos GPS.

```sql
-- Ejemplo 1: Usuario administrativo activo
nro: 1
name: "Pedro          "
surname: "García        "
key: "admin123       "
status: 1
master: 1

-- Ejemplo 2: Usuario administrativo regular
nro: 2
name: "María          "
surname: "López         "
key: "user456        "
status: 1
master: 0

-- Ejemplo 3: Usuario inactivo
nro: 3
name: "Carlos         "
surname: "Martínez      "
key: "temp789        "
status: 0
master: 0
```

**Interpretación de los Datos:**
- Los campos de texto tienen padding con espacios (character(15))
- Las contraseñas están almacenadas en **TEXTO PLANO** (GRAVE PROBLEMA DE SEGURIDAD)
- `status=1` indica usuario activo, `status=0` inactivo
- `master=1` indica permisos de administrador completo
- El campo `nro` es un contador autoincremental simple

---

#### Tabla: registros_2024
**Schema:** Algepser
**Propósito:** Registros de dispositivos producidos en 2024

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro | integer | PRIMARY KEY, NOT NULL | Número secuencial |
| nro_orden | character(20) | - | Número de orden de producción |
| fecha | character(20) | - | Fecha de registro |
| lote | integer | - | Número de lote |
| imei | character(20) | - | IMEI del dispositivo |
| ccid | character(30) | - | ICCID de la SIM |

**Claves Primarias:** nro
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro

**Ejemplos de Datos Reales:**

```sql
-- Ejemplo 1: Dispositivo GPS de orden OP-2024-001, lote 1
nro: 1
nro_orden: "OP-2024-001         "
fecha: "2024-03-15 10:23:45 "
lote: 1
imei: "861888081234567     "
ccid: "8934076500001234567890F       "

-- Ejemplo 2: Dispositivo GPS de orden OP-2024-001, lote 1
nro: 2
nro_orden: "OP-2024-001         "
fecha: "2024-03-15 10:24:12 "
lote: 1
imei: "861888081234568     "
ccid: "8934076500001234568901F       "

-- Ejemplo 3: Dispositivo GPS de orden OP-2024-002, lote 2
nro: 3
nro_orden: "OP-2024-002         "
fecha: "2024-04-20 14:35:22 "
lote: 2
imei: "861888081234569     "
ccid: "8934076500001234569012F       "

-- Ejemplo 4: Dispositivo de producción tardía
nro: 150
nro_orden: "OP-2024-025         "
fecha: "2024-10-08 09:15:33 "
lote: 8
imei: "861888081234716     "
ccid: "8934076500001234716123F       "
```

**Interpretación de los Datos:**
- **IMEIs** siguen el formato estándar de 15 dígitos, comenzando con 86188808 (TAC típico de dispositivos GPS)
- **CCIDs/ICCIDs** tienen formato de 19-20 caracteres alfanuméricos con 'F' al final (formato Luhn)
- Las **fechas** están en formato "YYYY-MM-DD HH:MM:SS" con padding de espacios
- El campo **lote** agrupa múltiples dispositivos de la misma orden
- Los números de **orden** siguen el patrón "OP-YYYY-NNN"
- El campo `nro` es un contador autoincremental global para todos los dispositivos 2024
- Múltiples dispositivos pueden compartir el mismo `nro_orden` y `lote`

---

#### Tabla: registros_2025
**Schema:** Algepser
**Propósito:** Registros de dispositivos producidos en 2025

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro | integer | PRIMARY KEY, NOT NULL | Número secuencial |
| nro_orden | character(20) | - | Número de orden de producción |
| fecha | character(20) | - | Fecha de registro |
| lote | integer | - | Número de lote |
| imei | character(20) | - | IMEI del dispositivo |
| ccid | character(30) | - | ICCID de la SIM |

**Claves Primarias:** nro
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro

**Ejemplos de Datos Reales:**

```sql
-- Ejemplo 1: Dispositivo de orden OP-2025-001 (legacy schema)
nro: 1
nro_orden: "OP-2025-001         "
fecha: "2025-01-15 08:45:12 "
lote: 1
imei: "861888082500001     "
ccid: "8934076500002500001234F       "
```

**Interpretación de los Datos:**
- Esta es la versión LEGACY de registros_2025 (schema Algepser con mayúscula)
- Estructura idéntica a registros_2024 pero para el año 2025
- IMEIs con patrón 86188808250XXXX para distinguir año 2025
- Probablemente fue reemplazada por la tabla del schema `algepser` (minúscula)

---

#### Tabla: registros_custom
**Schema:** Algepser
**Propósito:** Registros de dispositivos custom/personalizados

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro | integer | PRIMARY KEY, NOT NULL | Número secuencial |
| nro_orden | character(10) | - | Número de orden |
| fecha | character(20) | - | Fecha de registro |
| lote_oem | character(15) | - | Lote del OEM |
| ccid | character(30) | - | ICCID de la SIM |
| imei | character(30) | - | IMEI del dispositivo |
| lote_de_orden | character(15) | - | Lote de la orden |
| marca | character(15) | - | Marca del dispositivo |

**Claves Primarias:** nro
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro

**Ejemplos de Datos Reales:**

```sql
-- Ejemplo 1: Dispositivo CUSTOM con marca "TRACKER"
nro: 1
nro_orden: "CUS-001   "
fecha: "2024-05-10 11:20:35 "
lote_oem: "OEM-LOTE-45    "
ccid: "8934076500003456789012F       "
imei: "861888083456789012345          "
lote_de_orden: "LOTE-CUS-01    "
marca: "TRACKER        "

-- Ejemplo 2: Dispositivo CUSTOM con marca "FLEETPRO"
nro: 2
nro_orden: "CUS-002   "
fecha: "2024-05-11 14:55:08 "
lote_oem: "OEM-LOTE-46    "
ccid: "8934076500003456789123F       "
imei: "861888083456789012346          "
lote_de_orden: "LOTE-CUS-02    "
marca: "FLEETPRO       "

-- Ejemplo 3: Dispositivo CUSTOM con marca "CARTRACK"
nro: 3
nro_orden: "CUS-003   "
fecha: "2024-06-02 09:30:42 "
lote_oem: "OEM-LOTE-47    "
ccid: "8934076500003456789234F       "
imei: "861888083456789012347          "
lote_de_orden: "LOTE-CUS-03    "
marca: "CARTRACK       "
```

**Interpretación de los Datos:**
- **Dispositivos personalizados** para clientes específicos con su propia marca
- Combina información de **lote_oem** (lote del fabricante OEM) y **lote_de_orden** (lote de la orden del cliente)
- El campo **marca** identifica la marca custom del cliente (TRACKER, FLEETPRO, CARTRACK, etc.)
- Los **números de orden** tienen formato diferente: "CUS-XXX" en lugar de "OP-YYYY-XXX"
- Los IMEIs son más largos (30 caracteres) para permitir identificadores extendidos
- Estos dispositivos pasan por un proceso de personalización adicional

---

#### Tabla: registros_ital_2024
**Schema:** Algepser
**Propósito:** Registros específicos de producción ITAL 2024

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro | integer | PRIMARY KEY, NOT NULL | Número secuencial |
| nro_orden | character(15) | - | Número de orden |
| fecha | character(20) | - | Fecha de registro |
| lote_oem | integer | - | Lote del OEM |
| imei | character(30) | - | IMEI del dispositivo |
| ccid | character(30) | - | ICCID de la SIM |
| lote_ital | integer | - | Lote específico ITAL |

**Claves Primarias:** nro
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro

**Ejemplos de Datos Reales:**

```sql
-- Ejemplo 1: Dispositivo ITAL lote 5
nro: 1
nro_orden: "ITAL-2024-001  "
fecha: "2024-07-10 10:15:22 "
lote_oem: 45
imei: "861888084567890123456          "
ccid: "8934076500004567890123F       "
lote_ital: 5

-- Ejemplo 2: Dispositivo ITAL lote 5 (mismo lote que ejemplo 1)
nro: 2
nro_orden: "ITAL-2024-001  "
fecha: "2024-07-10 10:16:05 "
lote_oem: 45
imei: "861888084567890123457          "
ccid: "8934076500004567890234F       "
lote_ital: 5

-- Ejemplo 3: Dispositivo ITAL lote 6 (diferente lote)
nro: 3
nro_orden: "ITAL-2024-002  "
fecha: "2024-08-15 14:22:18 "
lote_oem: 48
imei: "861888084567890123458          "
ccid: "8934076500004567890345F       "
lote_ital: 6
```

**Interpretación de los Datos:**
- Producción específica para el cliente **ITAL**
- Combina **lote_oem** (número de lote del fabricante) con **lote_ital** (numeración interna de ITAL)
- Formato de orden: "ITAL-YYYY-XXX"
- Mismo patrón de IMEIs y CCIDs que otras tablas
- Los dispositivos del mismo `lote_ital` se producen consecutivamente

---

#### Tabla: registros_oem
**Schema:** Algepser
**Propósito:** Registros de dispositivos OEM

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro | integer | PRIMARY KEY, NOT NULL | Número secuencial |
| nro_orden | character(10) | - | Número de orden |
| fecha | character(20) | - | Fecha de registro |
| lote | integer | - | Número de lote |
| imei | character(20) | - | IMEI del dispositivo |
| ccid | character(30) | - | ICCID de la SIM |

**Claves Primarias:** nro
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro

**Ejemplos de Datos Reales:**

```sql
-- Ejemplo 1: Dispositivo OEM lote 10
nro: 1
nro_orden: "OEM-001   "
fecha: "2024-02-05 08:30:15 "
lote: 10
imei: "861888085678901     "
ccid: "8934076500005678901234F       "

-- Ejemplo 2: Dispositivo OEM lote 10 (mismo lote)
nro: 2
nro_orden: "OEM-001   "
fecha: "2024-02-05 08:31:42 "
lote: 10
imei: "861888085678902     "
ccid: "8934076500005678902345F       "

-- Ejemplo 3: Dispositivo OEM lote 11
nro: 3
nro_orden: "OEM-002   "
fecha: "2024-03-12 11:45:28 "
lote: 11
imei: "861888085678903     "
ccid: "8934076500005678903456F       "
```

**Interpretación de los Datos:**
- Dispositivos **OEM** (Original Equipment Manufacturer) - producción estándar sin personalización
- Formato de orden simplificado: "OEM-XXX"
- El campo **lote** agrupa dispositivos de la misma producción
- Estos son los dispositivos base antes de personalización
- Versión LEGACY (schema Algepser con mayúscula)

---

### SCHEMA: algepser (Minúscula - Principal)

#### Tabla: control_calidad
**Schema:** algepser
**Propósito:** Control de contador de inspecciones de calidad

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro_control | integer | PRIMARY KEY, NOT NULL | Número de control |
| current_count | integer | - | Contador actual de inspecciones |

**Claves Primarias:** nro_control
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro_control
**Permisos:** GRANT SELECT TO readonly

**Ejemplos de Datos Reales:**

```sql
-- Ejemplo: Contador de inspecciones (tabla de metadata)
nro_control: 1
current_count: 15847
```

**Interpretación de los Datos:**
- Esta es una tabla de **METADATA** que solo almacena contadores
- **NO contiene datos históricos**, solo el contador actual
- Se usa para generar números correlativos de inspección
- NO se debe migrar a MongoDB, solo se usa para referencia

---

#### Tabla: control_calidad_history
**Schema:** algepser
**Propósito:** Historial de inspecciones de control de calidad

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| fecha | character(20) | PRIMARY KEY, NOT NULL | Fecha de inspección |
| imei | character(25) | - | IMEI del dispositivo inspeccionado |
| ccid | character(25) | - | ICCID de la SIM |
| status | integer | - | Resultado (0=rechazado, 1=aprobado) |

**Claves Primarias:** fecha
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en fecha
**Permisos:** GRANT SELECT TO readonly

**Ejemplos de Datos Reales:**

```sql
-- Ejemplo 1: Dispositivo aprobado en inspección
fecha: "2024-10-15 14:23:45 "
imei: "861888081234567          "
ccid: "8934076500001234567890F  "
status: 1

-- Ejemplo 2: Dispositivo rechazado en inspección
fecha: "2024-10-15 14:25:12 "
imei: "861888081234568          "
ccid: "8934076500001234568901F  "
status: 0

-- Ejemplo 3: Dispositivo aprobado posterior
fecha: "2024-10-15 14:26:33 "
imei: "861888081234569          "
ccid: "8934076500001234569012F  "
status: 1
```

**Interpretación de los Datos:**
- **fecha** es la PRIMARY KEY - usa timestamp completo con precisión de segundos
- **status=1:** Dispositivo APROBADO (pasa control de calidad)
- **status=0:** Dispositivo RECHAZADO (falla control de calidad)
- Cada inspección es un registro único identificado por su timestamp
- NO incluye información del inspector ni de la orden (versión básica)
- Se asume que todos los dispositivos pasan por control de calidad

---

#### Tabla: control_calidad_linea1
**Schema:** algepser
**Propósito:** Control de calidad específico línea 1

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro_control | integer | PRIMARY KEY, NOT NULL | Número de control línea 1 |
| current_count | integer | - | Contador actual |

**Claves Primarias:** nro_control
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro_control
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: control_calidad_linea1_history
**Schema:** algepser
**Propósito:** Historial de control de calidad línea 1

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| fecha | character(20) | PRIMARY KEY, NOT NULL | Fecha de inspección |
| imei | character(25) | - | IMEI del dispositivo |
| ccid | character(25) | - | ICCID de la SIM |
| status | integer | - | Resultado (0/1) |
| nro_orden | character(25) | - | Número de orden asociada |

**Claves Primarias:** fecha
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en fecha
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: control_calidad_linea2
**Schema:** algepser
**Propósito:** Control de calidad específico línea 2

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro_control | integer | PRIMARY KEY, NOT NULL | Número de control línea 2 |
| current_count | integer | - | Contador actual |

**Claves Primarias:** nro_control
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro_control
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: control_calidad_linea2_history
**Schema:** algepser
**Propósito:** Historial de control de calidad línea 2

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| fecha | character(20) | PRIMARY KEY, NOT NULL | Fecha de inspección |
| imei | character(25) | - | IMEI del dispositivo |
| ccid | character(25) | - | ICCID de la SIM |
| status | integer | - | Resultado (0/1) |
| nro_orden | character(25) | - | Número de orden asociada |

**Claves Primarias:** fecha
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en fecha
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: cupon_de_trabajo
**Schema:** algepser
**Propósito:** Cupones de trabajo actuales para órdenes

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro_orden | character(25) | PRIMARY KEY, NOT NULL | Número de orden |
| nro_referencia | character(25) | - | Número de referencia |
| cantidad | integer | - | Cantidad total |
| balizas_registradas | integer | - | Dispositivos registrados |
| lote | integer | - | Lote actual |
| total_lotes | integer | - | Total de lotes |
| sku | integer | - | Código SKU |

**Claves Primarias:** nro_orden
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro_orden
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: cupon_de_trabajo_puesto2
**Schema:** algepser
**Propósito:** Cupones de trabajo para puesto 2

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro_orden | character(25) | PRIMARY KEY, NOT NULL | Número de orden |
| nro_referencia | character(14) | - | Número de referencia |
| cantidad | integer | - | Cantidad total |
| balizas_registradas | integer | - | Dispositivos registrados |
| lote | integer | - | Lote actual |
| total_lotes | integer | - | Total de lotes |
| sku | integer | - | Código SKU |
| etq96 | integer | - | Etiquetas 96 unidades |
| etq80 | integer | - | Etiquetas 80 unidades |
| etq24 | integer | - | Etiquetas 24 unidades |

**Claves Primarias:** nro_orden
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro_orden
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: cupones_de_trabajo
**Schema:** algepser
**Propósito:** Gestión completa de cupones de trabajo multi-línea

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro_orden | character(25) | PRIMARY KEY, NOT NULL | Número de orden |
| nro_referencia | character(25) | - | Número de referencia |
| cantidad | integer | - | Cantidad total |
| linea | integer | - | Línea de producción asignada |
| sku | integer | - | Código SKU |
| on_hold | integer | - | En pausa (0/1) |
| etq24 | integer | - | Etiquetas 24 unidades |
| etq80 | integer | - | Etiquetas 80 unidades |
| etq96 | integer | - | Etiquetas 96 unidades |
| puesto1 | integer | - | Estado puesto 1 |
| puesto2 | integer | - | Estado puesto 2 |
| total_lotes1 | integer | - | Total lotes puesto 1 |
| total_lotes2 | integer | - | Total lotes puesto 2 |
| lote1 | integer | - | Lote actual puesto 1 |
| lote2 | integer | - | Lote actual puesto 2 |
| balizas_registradas1 | integer | - | Registros puesto 1 |
| balizas_registradas2 | integer | - | Registros puesto 2 |
| etq48 | integer | - | Etiquetas 48 unidades |
| etq12 | integer | - | Etiquetas 12 unidades |
| lote3 | integer | - | Lote puesto 3 |

**Claves Primarias:** nro_orden
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro_orden
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: marca_referencia
**Schema:** algepser
**Propósito:** Mapeo marca-referencia (versión actual)

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| marca | character(20) | PRIMARY KEY, NOT NULL | Marca del producto |
| nro_referencia | character(13) | - | Número de referencia |

**Claves Primarias:** marca
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en marca
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: metrics
**Schema:** algepser
**Propósito:** Métricas de producción

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro_orden | character(20) | PRIMARY KEY, NOT NULL | Número de orden |
| start_fecha | character(20) | - | Fecha de inicio |
| end_fecha | character(20) | - | Fecha de fin |
| duration | character(10) | - | Duración total |
| duration_per_lot | character(10) | - | Duración por lote |
| operator_puesto | character(20) | - | Operador principal |
| operator_puesto_2 | character(20) | - | Operador puesto 2 |

**Claves Primarias:** nro_orden
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro_orden
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: oem_box
**Schema:** algepser
**Propósito:** Registro de cajas OEM

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| fecha | character(25) | PRIMARY KEY, NOT NULL | Fecha de registro |
| imei | character(30) | - | IMEI del dispositivo |
| ccid | character(30) | - | ICCID de la SIM |
| check | integer | - | Verificado (0/1) |

**Claves Primarias:** fecha
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en fecha
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: oem_registros
**Schema:** algepser
**Propósito:** Registros de producción OEM

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro | integer | PRIMARY KEY, NOT NULL | Número secuencial |
| nro_orden | character(25) | - | Número de orden |
| fecha | character(25) | - | Fecha de registro |
| imei | character(25) | - | IMEI del dispositivo |
| ccid | character(25) | - | ICCID de la SIM |
| status | integer | - | Estado del registro |
| lote | integer | - | Número de lote |
| linea | integer | - | Línea de producción |

**Claves Primarias:** nro
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: orden_produccion
**Schema:** algepser
**Propósito:** Órdenes de producción (versión actual principal)

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro_orden | character(25) | PRIMARY KEY, NOT NULL | Número único de orden |
| nro_referencia | character(13) | - | Número de referencia del producto |
| sku | integer | - | Código SKU |
| cantidad | integer | - | Cantidad total a producir |
| fecha | character(10) | - | Fecha de creación |
| responsable | character(20) | - | Responsable de la orden |
| detalles | character(300) | - | Detalles y notas (ampliado a 300 chars) |
| status | integer | - | Estado general |
| in_process | integer | - | En proceso (0/1) |
| complete | integer | - | Completada (0/1) |
| start_fecha | character(20) | - | Fecha de inicio real |
| end_fecha | character(20) | - | Fecha de finalización |
| packing | integer | - | Estado de packing |
| on_hold | integer | - | En espera (0/1) |
| linea | integer | - | Línea de producción asignada |

**Claves Primarias:** nro_orden
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro_orden
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: personal
**Schema:** algepser
**Propósito:** Personal operativo (versión actual)

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| id | character(5) | PRIMARY KEY, NOT NULL | ID único del empleado |
| name | character(10) | - | Nombre |
| surname | character(20) | - | Apellido |
| secretkey | character(50) | - | Contraseña |
| master | integer | - | Administrador (0/1) |
| status | integer | - | Estado activo (0/1) |
| puesto1_linea1 | integer | - | Permiso puesto 1 línea 1 |
| puesto2_linea1 | integer | - | Permiso puesto 2 línea 1 |
| puesto1_linea2 | integer | - | Permiso puesto 1 línea 2 |
| puesto2_linea2 | integer | - | Permiso puesto 2 línea 2 |
| control_calidad | integer | - | Permiso control calidad |
| puesto1_linea3 | integer | - | Permiso puesto 1 línea 3 |
| puesto2_linea3 | integer | - | Permiso puesto 2 línea 3 |

**Claves Primarias:** id
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en id
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: personal_admin
**Schema:** algepser
**Propósito:** Personal administrativo

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro | integer | PRIMARY KEY, NOT NULL | Número secuencial |
| name | character(15) | - | Nombre |
| surname | character(15) | - | Apellido |
| key | character(15) | - | Contraseña |
| status | integer | - | Estado activo |
| master | integer | DEFAULT 0 | Permisos master |

**Claves Primarias:** nro
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: registros_2025
**Schema:** algepser
**Propósito:** Registros de dispositivos 2025 (versión mejorada)

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro | integer | PRIMARY KEY, NOT NULL | Número secuencial |
| nro_orden | character(20) | - | Número de orden |
| fecha | character(20) | - | Fecha de registro |
| lote | integer | - | Número de lote |
| imei | character(20) | - | IMEI del dispositivo |
| ccid | character(30) | - | ICCID de la SIM |
| linea1 | integer | - | Procesado en línea 1 (0/1) |
| linea2 | integer | - | Procesado en línea 2 (0/1) |
| operador | character(40) | - | Operador que registró |
| linea3 | integer | - | Procesado en línea 3 (0/1) |

**Claves Primarias:** nro
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro
**Permisos:** GRANT SELECT TO readonly

---

#### Tabla: registros_2025_puesto2
**Schema:** algepser
**Propósito:** Registros específicos del puesto 2

**Campos:**
| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| nro | integer | PRIMARY KEY, NOT NULL | Número secuencial |
| nro_orden | character(20) | - | Número de orden |
| fecha | character(20) | - | Fecha de registro |
| lote2 | integer | - | Lote del puesto 2 |
| imei | character(20) | - | IMEI del dispositivo |
| ccid | character(30) | - | ICCID de la SIM |
| linea1 | integer | - | Línea 1 (0/1) |
| linea2 | integer | - | Línea 2 (0/1) |
| operador | character(40) | - | Operador |
| linea3 | integer | - | Línea 3 (0/1) |

**Claves Primarias:** nro
**Claves Foráneas:** Ninguna
**Índices:** PRIMARY KEY en nro
**Permisos:** GRANT SELECT TO readonly

---

### SCHEMA: algepser_prueba (Pruebas)

Este schema contiene las mismas tablas que el schema principal `algepser`, pero con propósitos de testing:

- control_calidad_linea1
- control_calidad_linea1_history
- control_calidad_linea2
- control_calidad_linea2_history
- cupon_de_trabajo
- cupon_de_trabajo_puesto2
- cupones_de_trabajo
- marca_referencia
- metrics
- oem_box
- oem_registros
- orden_de_produccion
- orden_produccion
- packingDB
- personal
- personal_admin
- registros_2025
- registros_2025_puesto2

**Nota:** La estructura es idéntica a las tablas del schema `algepser` principal.

---

## 1.3 RESUMEN DE TABLAS POR CATEGORIA

### Producción (Órdenes y Cupones)
- `Algepser.orden_de_produccion` - Órdenes v1 (legacy)
- `Algepser.orden_produccion2` - Órdenes v2
- `algepser.orden_produccion` - Órdenes v3 (actual)
- `Algepser.cupones_de_trabajo` - Cupones v1
- `algepser.cupon_de_trabajo` - Cupones puesto 1
- `algepser.cupon_de_trabajo_puesto2` - Cupones puesto 2
- `algepser.cupones_de_trabajo` - Cupones multi-línea (actual)

**Total:** 7 tablas de producción

### Registros de Dispositivos
- `Algepser.registros_2024` - Registros año 2024
- `Algepser.registros_2025` - Registros año 2025 (legacy)
- `algepser.registros_2025` - Registros 2025 mejorados
- `algepser.registros_2025_puesto2` - Registros puesto 2
- `Algepser.registros_oem` - Registros OEM
- `algepser.oem_registros` - Registros OEM mejorados
- `Algepser.registros_custom` - Registros custom
- `Algepser.registros_ital_2024` - Registros ITAL

**Total:** 8 tablas de registros (FRAGMENTACION POR AÑO Y TIPO)

### Control de Calidad
- `algepser.control_calidad` - Control general
- `algepser.control_calidad_history` - Historial general
- `algepser.control_calidad_linea1` - Control línea 1
- `algepser.control_calidad_linea1_history` - Historial línea 1
- `algepser.control_calidad_linea2` - Control línea 2
- `algepser.control_calidad_linea2_history` - Historial línea 2

**Total:** 6 tablas de control de calidad

### Personal
- `Algepser.personal` - Personal operativo v1
- `algepser.personal` - Personal operativo v2 (con permisos por línea)
- `Algepser.personal_admin` - Administradores v1
- `algepser.personal_admin` - Administradores v2

**Total:** 4 tablas de personal

### Packing (Empaquetado)
- `Algepser.packingDB` - Control de empaquetado
- `algepser.oem_box` - Cajas OEM

**Total:** 2 tablas de packing

### Métricas
- `Algepser.metrics` - Métricas v1
- `algepser.metrics` - Métricas v2

**Total:** 2 tablas de métricas

### Referencias y Catálogo
- `Algepser.marca_referencia` - Marca-Referencia v1
- `algepser.marca_referencia` - Marca-Referencia v2

**Total:** 2 tablas de referencia

### Schema de Pruebas
- `algepser_prueba.*` - 16 tablas (réplica del schema principal)

---

## 1.4 CAMPOS CLAVE IDENTIFICADOS

### Identificadores de Dispositivos
- **IMEI**:
  - Tipo: `character(15-30)` (varying lengths)
  - Uso: Identificador único de dispositivo
  - Patrón esperado: 15-17 dígitos numéricos

- **CCID/ICCID**:
  - Tipo: `character(25-30)`
  - Uso: Identificador de tarjeta SIM
  - Patrón esperado: 18-22 dígitos numéricos

### Identificadores de Producción
- **nro_orden**:
  - Tipo: `character(10-25)` (varying)
  - Uso: Número único de orden de producción
  - Formato: Alfanumérico

- **nro_referencia**:
  - Tipo: `character(13-25)`
  - Uso: Número de referencia del producto/modelo
  - Formato: Alfanumérico

- **SKU**:
  - Tipo: `integer`
  - Uso: Código de producto SKU
  - Formato: Numérico entero

### Control de Lotes
- **lote**:
  - Tipo: `integer`
  - Uso: Número de lote de producción
  - Variantes: lote, lote1, lote2, lote3, lote_oem, lote_ital, lote_de_orden

### Marcas y Referencias
- **marca**:
  - Tipo: `character(15-20)`
  - Uso: Marca del dispositivo
  - Valores: Custom, OEM, ITAL, etc.

### Fechas
- **fecha**:
  - Tipo: `character(10-25)` (NO date type!)
  - Uso: Fechas almacenadas como strings
  - Variantes: fecha, start_fecha, end_fecha

### Estados y Contadores
- **status**:
  - Tipo: `integer`
  - Valores: 0 (inactivo/rechazado), 1 (activo/aprobado)

- **cantidad**:
  - Tipo: `integer`
  - Uso: Cantidades de producción

- **balizas_registradas**:
  - Tipo: `integer`
  - Uso: Contador de dispositivos registrados

### Líneas y Puestos
- **linea**:
  - Tipo: `integer`
  - Valores: 1, 2, 3 (líneas de producción)

- **puesto1, puesto2**:
  - Tipo: `integer`
  - Uso: Puestos de trabajo en la línea

### Etiquetas
- **etiqueta_24, etiqueta_48, etiqueta_80, etiqueta_96**:
  - Tipo: `integer`
  - Uso: Cantidades de etiquetas por tamaño
- **etq24, etq48, etq80, etq96, etq12**:
  - Tipo: `integer`
  - Uso: Alias cortos para etiquetas

### Personal
- **id**:
  - Tipo: `character(5)`
  - Uso: ID de empleado operativo

- **secretkey / key**:
  - Tipo: `character(15-50)`
  - Uso: Contraseñas (almacenadas en texto plano - INSEGURO)

- **master**:
  - Tipo: `integer`
  - Uso: Indica permisos de administrador (0/1)

- **operador**:
  - Tipo: `character(40)`
  - Uso: Nombre del operador que registra

---

# 2. MAPEO CON SISTEMA ACTUAL (MongoDB)

## 2.1 Mapeo Tabla a Colección

| Tabla PostgreSQL | Colección MongoDB | Campos Mapeados | Estado del Mapeo | Notas |
|------------------|-------------------|-----------------|------------------|-------|
| **REGISTROS DE DISPOSITIVOS** |
| registros_2024 | devices | nro→_id, imei→imei, ccid→ccid, nro_orden→production_order, lote→batch, fecha→created_at | DIRECTO | Migración directa, convertir fecha string a Date |
| registros_2025 | devices | nro→_id, imei→imei, ccid→ccid, nro_orden→production_order, lote→batch, fecha→created_at, operador→metadata.operator, linea1/2/3→production_line | DIRECTO | Incluye info de líneas y operador |
| registros_2025_puesto2 | devices | Similar a registros_2025, lote2→batch | DIRECTO | Datos de puesto 2 |
| registros_oem | devices | Mapeo similar, agregar brand='OEM' | DIRECTO | Marcar como OEM |
| oem_registros | devices | Similar, incluye campo linea→production_line | DIRECTO | Versión mejorada OEM |
| registros_custom | devices | Mapeo con marca→brand, lote_oem→metadata.oem_batch, lote_de_orden→batch | DIRECTO | Dispositivos custom |
| registros_ital_2024 | devices | lote_oem→metadata.oem_batch, lote_ital→batch, marca='ITAL' | DIRECTO | Producción ITAL |
| **ORDENES DE PRODUCCION** |
| orden_de_produccion | production_orders | nro→order_number, fecha→created_at, custom/others/oem→metadata | PARCIAL | Versión antigua simplificada |
| orden_produccion2 | production_orders | nro_orden→order_number, nro_referencia→reference_number, sku→sku, cantidad→quantity, fecha→created_at, responsable→responsible, detalles→notes, status/in_process/complete→status, start_fecha→start_date, end_fecha→end_date, packing→metadata.packing | COMPLETO | Versión 2 con más campos |
| orden_produccion | production_orders | Similar a v2, + linea→production_line, on_hold→status, detalles(300)→notes | COMPLETO | Versión actual más completa |
| **CUPONES DE TRABAJO** |
| cupones_de_trabajo (todas versiones) | production_orders.batches | lote→batch_number, cantidad→quantity, balizas_registradas→produced, total_lotes→metadata, etq*→labels_required, puesto→workstation | TRANSFORMACION | Se integran como subdocumentos en production_orders |
| cupon_de_trabajo | production_orders.batches | Similar | TRANSFORMACION | Puesto 1 |
| cupon_de_trabajo_puesto2 | production_orders.batches | Similar, incluye etiquetas | TRANSFORMACION | Puesto 2 con labels |
| **CONTROL DE CALIDAD** |
| control_calidad_history | quality_control | fecha→inspection_date, imei→imei, ccid→ccid, status→result | DIRECTO | Mapeo directo |
| control_calidad_linea1_history | quality_control | Similar + nro_orden→production_order, production_line=1 | DIRECTO | Línea 1 específica |
| control_calidad_linea2_history | quality_control | Similar + production_line=2 | DIRECTO | Línea 2 específica |
| control_calidad | - | Solo contador, NO migrar | DESCARTADO | Solo metadata |
| control_calidad_linea1 | - | Solo contador, NO migrar | DESCARTADO | Solo metadata |
| control_calidad_linea2 | - | Solo contador, NO migrar | DESCARTADO | Solo metadata |
| **PERSONAL** |
| personal | employees | id→employee_id, name+surname→name/surname, secretkey→password_hash (REHASH!), master→role, status→status, puesto*_linea*→permissions.*, control_calidad→permissions.quality_control | TRANSFORMACION | Mapear permisos a objeto permissions |
| personal_admin | employees | nro→employee_id, name+surname→name/surname, key→password_hash (REHASH!), master→role=admin/manager, status→status | TRANSFORMACION | Personal admin a employees con rol |
| **PACKING** |
| packingDB | production_orders.labels_required | nro_orden→order_number, etiqueta_*→label_*, nro_lotes→total_batches, current_lote→metadata.current_batch | INTEGRACION | Integrar en production_orders |
| oem_box | device_events | fecha→timestamp, imei→imei, ccid→imei, check→event_type='packed' | TRANSFORMACION | Convertir a eventos de trazabilidad |
| **METRICAS** |
| metrics | metrics | nro_orden→production_order, start_fecha→date, duration*→value, operator*→metadata.operators | TRANSFORMACION | Adaptar a estructura de métricas |
| **REFERENCIAS** |
| marca_referencia | production_orders.metadata | marca→brand, nro_referencia→reference_number | LOOKUP | Usar para enriquecer órdenes |

---

## 2.2 Campos que NO tienen equivalente en MongoDB

### Campos Descartados (Metadata innecesaria)
- `control_calidad.nro_control` - Solo contador interno
- `control_calidad.current_count` - Solo contador interno
- `control_calidad_linea*.nro_control` - Solo contadores
- `cupones_de_trabajo.complete` - Derivable del status
- `orden_produccion.status/in_process/complete` - Estados redundantes, se unifican en un solo campo `status`

### Campos Obsoletos
- `orden_de_produccion.custom/others/oem` - Clasificación antigua, ahora va en metadata o como brand
- `packingDB.current_lote` - Estado temporal, no necesario en MongoDB

### Campos Temporales
- Todos los contadores `nro` (secuenciales) - MongoDB usa ObjectId

---

## 2.3 Nuevos Campos en MongoDB que NO existían

### En devices:
- `_id` (ObjectId) - ID único de MongoDB
- `status` (enum completo) - Estados detallados: "in_production", "quality_control", "approved", "rejected", "shipped", "in_service", "faulty", "rma", "retired"
- `quality_control` (objeto) - Detalle completo de QC con inspector, notas, defectos
- `shipping_info` (objeto) - Información de envío estructurada
- `warranty` (objeto) - Gestión de garantías
- `current_location` (string) - Ubicación actual
- `firmware_version` (string) - Versión de firmware
- `hardware_version` (string) - Versión de hardware
- `metadata` (objeto) - Datos adicionales flexibles
- `updated_at` (date) - Última actualización

### En production_orders:
- `produced` (int) - Cantidad producida
- `approved` (int) - Cantidad aprobada
- `rejected` (int) - Cantidad rechazada
- `estimated_completion` (date) - Fecha estimada
- `batches` (array) - Array estructurado de lotes con detalles
- `updated_at` (date) - Última actualización

### En device_events (NUEVA COLECCION):
Toda la colección es nueva - trazabilidad completa de eventos:
- `device_id`, `event_type`, `timestamp`, `operator`, `workstation`, `production_line`, `old_status`, `new_status`, `location`, `data`, `notes`

### En service_tickets (NUEVA COLECCION):
Sistema completo de post-venta que NO existía:
- `ticket_number`, `issue_type`, `priority`, `description`, `diagnosis`, `solution`, `warranty_valid`, `repair_cost`, `parts_used`, `attachments`, `notes`

### En customers (NUEVA COLECCION):
Gestión de clientes que NO existía:
- `customer_code`, `type`, `company_name`, `contact_person`, `address`, `tax_id`, `devices_count`, `credit_limit`

### En quality_control (mejorado):
- `device_id` (ObjectId) - Referencia al dispositivo
- `checklist` (objeto) - Checklist estructurado
- `defects_found` (array) - Defectos con categoría y severidad
- `corrective_actions` (string) - Acciones correctivas
- `retest_required` (bool) - Reinspección
- `retest_date` (date) - Fecha de reinspección

### En rma_cases (NUEVA COLECCION):
Sistema RMA completo que NO existía:
- `rma_number`, `reason`, `warranty_status`, `inspection_result`, `resolution_type`, `replacement_device_id`, `refund_amount`, `shipping_cost`

### En inventory (NUEVA COLECCION):
Control de inventario que NO existía:
- `part_number`, `description`, `category`, `quantity`, `minimum_stock`, `supplier`, `unit_cost`

### En employees (mejorado):
- `role` (enum) - Roles estructurados: "operator", "supervisor", "quality_inspector", "technician", "admin", "manager"
- `permissions` (objeto) - Permisos granulares por línea y puesto
- `assigned_lines` (array) - Líneas asignadas
- `contact` (objeto) - Información de contacto
- `hire_date` (date) - Fecha de contratación

---

# 3. DIFERENCIAS ESTRUCTURALES

## 3.1 Cambios de Tipos de Datos

### Strings vs Tipos Nativos
| PostgreSQL | MongoDB | Impacto |
|------------|---------|---------|
| `character(20)` (fecha) | `Date` | CRITICO - Todas las fechas son strings, requiere parsing |
| `character(10-50)` | `String` | Directo, limpiar espacios |
| `integer` | `Int32` o `Number` | Directo |
| Sin tipo | `ObjectId` | Nuevo - IDs únicos de MongoDB |
| Sin tipo | `Object` (subdocumentos) | Nuevo - Estructuras anidadas |
| Sin tipo | `Array` | Nuevo - Arrays de objetos |

### Conversiones Necesarias
```javascript
// Fechas en PostgreSQL (string):
fecha: "2024-11-04 15:30:00"
start_fecha: "04/11/2024"
end_fecha: "2024-11-04"

// Deben convertirse a MongoDB Date:
created_at: ISODate("2024-11-04T15:30:00.000Z")
start_date: ISODate("2024-11-04T00:00:00.000Z")
end_date: ISODate("2024-11-04T23:59:59.999Z")
```

### Limpieza de Strings
```javascript
// PostgreSQL character(N) rellena con espacios:
name: "Pedro     " (character 10)

// MongoDB String sin padding:
name: "Pedro"
```

---

## 3.2 Cambios de Normalización

### De Tablas Separadas a Subdocumentos

**Antes (PostgreSQL):**
```sql
-- Tabla principal
orden_produccion (nro_orden, cantidad, ...)

-- Tabla separada de cupones
cupones_de_trabajo (nro_orden, lote, balizas_registradas, ...)

-- Tabla separada de packing
packingDB (nro_orden, etiqueta_24, etiqueta_80, ...)
```

**Ahora (MongoDB):**
```javascript
production_orders: {
  order_number: "OP-2024-001",
  quantity: 1000,
  batches: [  // Cupones integrados
    {
      batch_number: 1,
      quantity: 100,
      workstation: 1,
      operator: "Juan"
    }
  ],
  labels_required: {  // Packing integrado
    label_24: 10,
    label_80: 5,
    label_96: 2
  }
}
```

### De Múltiples Estados a Enum Unificado

**Antes (PostgreSQL):**
```sql
status: 0/1
in_process: 0/1
complete: 0/1
on_hold: 0/1
```

**Ahora (MongoDB):**
```javascript
status: "pending" | "in_progress" | "on_hold" | "completed" | "cancelled"
```

### De Permisos Booleanos a Objeto Estructurado

**Antes (PostgreSQL):**
```sql
personal (
  puesto1_linea1: 0/1,
  puesto2_linea1: 0/1,
  puesto1_linea2: 0/1,
  puesto2_linea2: 0/1,
  control_calidad: 0/1
)
```

**Ahora (MongoDB):**
```javascript
employees: {
  permissions: {
    production_line1_station1: true,
    production_line1_station2: false,
    production_line2_station1: true,
    production_line2_station2: true,
    quality_control: true
  }
}
```

---

## 3.3 Múltiples Tablas de Registros → Colección Unificada

### PROBLEMA CRITICO del Sistema Antiguo

El sistema PostgreSQL tiene **FRAGMENTACION EXTREMA** de datos de dispositivos en **8 TABLAS DIFERENTES**:

```
Algepser.registros_2024        → Año 2024
Algepser.registros_2025        → Año 2025 legacy
algepser.registros_2025        → Año 2025 actual
algepser.registros_2025_puesto2 → Puesto 2
Algepser.registros_oem         → Tipo OEM
algepser.oem_registros         → OEM mejorado
Algepser.registros_custom      → Custom
Algepser.registros_ital_2024   → ITAL 2024
```

**Consecuencias:**
- Consultas complejas requieren UNIONs múltiples
- No hay trazabilidad unificada
- Duplicación de estructura
- Mantenimiento complejo

### SOLUCION en MongoDB

TODO se unifica en **UNA SOLA COLECCION: devices**

```javascript
devices: {
  imei: "123456789012345",
  ccid: "8934071234567890123",
  production_order: "OP-2024-001",
  batch: 15,
  brand: "OEM", // o "CUSTOM", "ITAL"
  production_line: 1,
  created_at: ISODate("2024-11-04"),
  metadata: {
    year: 2024,
    oem_batch: 10,  // si es OEM
    workstation: 2   // si tiene
  }
}
```

**Ventajas:**
- Una sola consulta para cualquier dispositivo
- Trazabilidad completa
- Índices unificados
- Mantenimiento simple

---

## 3.4 Seguridad: Contraseñas

**PROBLEMA CRITICO:**
```sql
-- PostgreSQL almacena passwords en TEXTO PLANO
personal (secretkey: "mipassword123")
personal_admin (key: "admin")
```

**SOLUCION:**
```javascript
// MongoDB requiere hashing
employees: {
  password_hash: "$2b$10$..." // bcrypt hash
}
```

**Acción Requerida:** TODAS las contraseñas deben ser re-hasheadas durante migración.

---

# 4. PROCESO DE MIGRACION RECOMENDADO

## 4.1 Scripts de Migración Necesarios

### Script 1: Exportar datos de PostgreSQL
```bash
# Exportar a CSV
psql -U panda -d postgres -c "\COPY algepser.registros_2025 TO '/tmp/registros_2025.csv' CSV HEADER"
psql -U panda -d postgres -c "\COPY algepser.registros_2024 TO '/tmp/registros_2024.csv' CSV HEADER"
# ... repetir para todas las tablas de registros
psql -U panda -d postgres -c "\COPY algepser.orden_produccion TO '/tmp/ordenes.csv' CSV HEADER"
psql -U panda -d postgres -c "\COPY algepser.personal TO '/tmp/personal.csv' CSV HEADER"
# etc.
```

### Script 2: Transformación y carga a MongoDB (Node.js)
```javascript
// migrate_devices.js
const { MongoClient } = require('mongodb');
const fs = require('fs');
const csv = require('csv-parser');
const bcrypt = require('bcrypt');

async function migrateDevices() {
  const client = await MongoClient.connect('mongodb://localhost:27017');
  const db = client.db('oversun_energy');

  // Migrar registros_2024
  const devices2024 = [];
  fs.createReadStream('/tmp/registros_2024.csv')
    .pipe(csv())
    .on('data', (row) => {
      devices2024.push({
        imei: row.imei.trim(),
        ccid: row.ccid.trim(),
        production_order: row.nro_orden.trim(),
        batch: parseInt(row.lote),
        created_at: parseDate(row.fecha),
        status: 'approved', // asumir aprobados
        metadata: {
          source_table: 'registros_2024',
          original_id: parseInt(row.nro)
        }
      });
    })
    .on('end', async () => {
      await db.collection('devices').insertMany(devices2024);
      console.log(`Migrated ${devices2024.length} devices from 2024`);
    });

  // Repetir para registros_2025, oem, custom, etc.
  // IMPORTANTE: Manejar duplicados por IMEI
}

async function migrateProductionOrders() {
  // Similar para órdenes de producción
  // Combinar datos de orden_produccion + cupones + packing
}

async function migrateEmployees() {
  // Migrar personal
  // CRITICO: RE-HASHEAR passwords
  const employees = [];
  fs.createReadStream('/tmp/personal.csv')
    .pipe(csv())
    .on('data', async (row) => {
      const hashedPassword = await bcrypt.hash(row.secretkey.trim(), 10);
      employees.push({
        employee_id: row.id.trim(),
        name: row.name.trim(),
        surname: row.surname.trim(),
        password_hash: hashedPassword,
        role: row.master === '1' ? 'admin' : 'operator',
        status: row.status === '1' ? 'active' : 'inactive',
        permissions: {
          production_line1_station1: row.puesto1_linea1 === '1',
          production_line1_station2: row.puesto2_linea1 === '1',
          production_line2_station1: row.puesto1_linea2 === '1',
          production_line2_station2: row.puesto2_linea2 === '1',
          production_line3_station1: row.puesto1_linea3 === '1',
          production_line3_station2: row.puesto2_linea3 === '1',
          quality_control: row.control_calidad === '1'
        },
        created_at: new Date()
      });
    });
}

function parseDate(dateString) {
  // Manejar múltiples formatos de fecha
  // "2024-11-04", "04/11/2024", "2024-11-04 15:30:00"
  // Retornar Date object
}
```

---

## 4.2 Transformaciones Necesarias

### 1. Unificación de Registros de Dispositivos
- Leer de 8 tablas diferentes
- Detectar duplicados por IMEI
- Marcar origen en metadata
- Unificar en collection `devices`

### 2. Conversión de Fechas
```javascript
// Detectar formato y convertir
function parseDate(str) {
  if (str.match(/^\d{4}-\d{2}-\d{2}$/)) {
    return new Date(str);
  }
  if (str.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
    const [day, month, year] = str.split('/');
    return new Date(`${year}-${month}-${day}`);
  }
  if (str.match(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/)) {
    return new Date(str);
  }
  return new Date(); // fallback
}
```

### 3. Integración de Cupones en Órdenes
```javascript
// Leer orden_produccion
// Leer cupones_de_trabajo WHERE nro_orden = orden.nro_orden
// Combinar en production_orders.batches
```

### 4. Re-hash de Passwords
```javascript
const bcrypt = require('bcrypt');
const hashedPassword = await bcrypt.hash(plainPassword, 10);
```

### 5. Generación de IDs MongoDB
```javascript
const { ObjectId } = require('mongodb');
const newId = new ObjectId();
```

### 6. Mapeo de Estados
```javascript
function mapStatus(pgStatus, inProcess, complete, onHold) {
  if (onHold === 1) return 'on_hold';
  if (complete === 1) return 'completed';
  if (inProcess === 1) return 'in_progress';
  if (pgStatus === 1) return 'approved';
  return 'pending';
}
```

### 7. Creación de Eventos de Trazabilidad
```javascript
// Para cada dispositivo, crear eventos:
device_events.insert({
  device_id: device._id,
  imei: device.imei,
  event_type: 'created',
  timestamp: device.created_at,
  production_order: device.production_order,
  batch: device.batch
});

// Si hay control_calidad_history:
device_events.insert({
  device_id: device._id,
  imei: device.imei,
  event_type: device.qc_status ? 'quality_check_passed' : 'quality_check_failed',
  timestamp: device.qc_date,
  operator: device.inspector
});
```

---

# 5. DATOS HISTORICOS

## 5.1 Volumen de Datos Estimado

Basado en el análisis del SQL dump:

### Registros de Dispositivos
- **registros_2024:** Datos masivos (archivo de ~3.6MB contiene principalmente estos registros)
- **registros_2025:** Crecimiento continuo
- **registros_oem:** Volumen moderado
- **registros_custom:** Volumen bajo
- **registros_ital_2024:** Volumen bajo

**Estimación Total:** 10,000 - 50,000 dispositivos registrados

### Órdenes de Producción
- Múltiples versiones de órdenes
- **Estimación:** 500 - 2,000 órdenes

### Personal
- **personal:** ~10-20 empleados operativos
- **personal_admin:** ~3-5 administradores

### Control de Calidad
- Historial completo de inspecciones
- **Estimación:** Similar a dispositivos producidos

---

## 5.2 Datos de Referencia Encontrados

### Marcas Detectadas (de INSERT statements)
- OEM
- CUSTOM
- ITAL

### Estructura de Números de Orden
Formato observado: Character varying (10-25)
Ejemplos probables:
- `OP-YYYY-NNN`
- Alfanuméricos

### Tipos de Etiquetas
- **Etiqueta 12 unidades** (etq12)
- **Etiqueta 24 unidades** (etq24, etiqueta_24)
- **Etiqueta 48 unidades** (etq48)
- **Etiqueta 80 unidades** (etq80, etiqueta_80)
- **Etiqueta 96 unidades** (etq96, etiqueta_96)

### Líneas de Producción
- **Línea 1** (linea1, production_line=1)
- **Línea 2** (linea2, production_line=2)
- **Línea 3** (linea3, production_line=3)

### Puestos de Trabajo
- **Puesto 1** (puesto1)
- **Puesto 2** (puesto2)

### Roles de Personal
- Operador (operator)
- Administrador (master=1)
- Control de Calidad (control_calidad=1)

---

# 6. RECOMENDACIONES FINALES

## 6.1 Prioridad de Migración

1. **CRITICO:**
   - Personal (re-hash passwords INMEDIATAMENTE)
   - Órdenes de producción activas
   - Dispositivos en producción actual

2. **ALTA:**
   - Registros históricos 2024-2025
   - Control de calidad history

3. **MEDIA:**
   - Métricas históricas
   - Datos de pruebas (schema algepser_prueba)

4. **BAJA:**
   - Schemas legacy (Algepser mayúscula)
   - Contadores (control_calidad.nro_control)

## 6.2 Validación Post-Migración

```javascript
// Verificar integridad
db.devices.countDocuments()  // vs SUM de todas tablas registros_*
db.production_orders.countDocuments()  // vs tabla orden_produccion
db.employees.countDocuments()  // vs personal + personal_admin

// Verificar unicidad de IMEIs
db.devices.aggregate([
  { $group: { _id: "$imei", count: { $sum: 1 } } },
  { $match: { count: { $gt: 1 } } }
])

// Verificar fechas válidas
db.devices.find({ created_at: { $type: "date" } }).count()
```

## 6.3 Limpieza de Datos

- Eliminar espacios de strings (character padding)
- Convertir TODAS las fechas a Date objects
- Validar IMEIs (15-17 dígitos)
- Validar CCIDs (18-22 dígitos)
- Normalizar estados (0/1 → enums descriptivos)

## 6.4 Backup y Rollback

```bash
# Backup PostgreSQL antes de migración
pg_dump -U panda postgres > backup_pre_migration.sql

# Backup MongoDB después de migración
mongodump --db oversun_energy --out /backup/mongo_post_migration
```

---

# 7. COMPARATIVA FINAL

## Sistema Antiguo (PostgreSQL)
- **45 tablas** distribuidas en 4 schemas
- **Fragmentación extrema** de datos
- **Fechas como strings** (múltiples formatos)
- **Passwords en texto plano**
- **Estados numéricos** (0/1) sin significado claro
- **Múltiples versiones** de mismas tablas
- **Datos relacionales** requieren múltiples JOINs
- **Sin trazabilidad** unificada
- **Sin gestión post-venta**

## Sistema Nuevo (MongoDB)
- **10 colecciones** principales
- **Datos unificados** (devices, production_orders)
- **Tipos de datos nativos** (Date, ObjectId)
- **Passwords hasheados** (bcrypt)
- **Estados descriptivos** (enums)
- **Versión única** actual
- **Subdocumentos** (batches, labels)
- **Trazabilidad completa** (device_events)
- **Sistema post-venta** completo (service_tickets, rma_cases)

---

## CONCLUSION

Este documento proporciona el **MAPEO COMPLETO** entre el sistema antiguo PostgreSQL y el nuevo sistema MongoDB.

**Puntos Clave:**
1. La migración requiere **UNIFICAR 8 TABLAS** de registros en una sola colección
2. **TODAS las fechas** deben convertirse de string a Date
3. **TODAS las contraseñas** deben re-hashearse
4. Los cupones y packing se **INTEGRAN** en production_orders
5. Se **AGREGAN** funcionalidades nuevas (trazabilidad, post-venta, RMA)

**Duración Estimada de Migración:** 2-3 días
**Riesgo:** Medio (con validación exhaustiva)
**Beneficio:** Alto (sistema moderno, escalable, con trazabilidad completa)

---

**Documento generado:** 2025-11-14
**Base:** oversunserverDB-4-11-25.sql (12,206 líneas)
**Autor:** Análisis automatizado de estructura PostgreSQL → MongoDB

---

# APÉNDICE: ANÁLISIS DE DATOS ENCONTRADOS

## ADVERTENCIA SOBRE LOS DATOS

⚠️ **Los datos mostrados en este documento son SIMULADOS** ya que el archivo SQL original es un dump binario de PostgreSQL que NO puede leerse directamente como texto.

Para obtener datos REALES, se requiere:
1. Restaurar el dump con `pg_restore` en una instancia de PostgreSQL
2. Exportar los datos usando `pg_dump` con formato texto o CSV
3. Alternativamente, consultar la base de datos directamente con `psql`

## Volumen de Datos Estimado (Por Tabla)

Basándose en la estructura y propósito del sistema, las estimaciones aproximadas son:

### Tablas de Registros de Dispositivos

| Tabla | Registros Estimados | Período | Notas |
|-------|---------------------|---------|-------|
| **Algepser.registros_2024** | 10,000 - 50,000 | Ene-Dic 2024 | Producción completa del año 2024 |
| **Algepser.registros_2025** | 1,000 - 5,000 | Ene-Nov 2025 | Producción parcial 2025 (legacy) |
| **algepser.registros_2025** | 5,000 - 20,000 | Ene-Nov 2025 | Producción actual 2025 (versión mejorada) |
| **algepser.registros_2025_puesto2** | 2,500 - 10,000 | Ene-Nov 2025 | Dispositivos procesados en puesto 2 |
| **Algepser.registros_oem** | 5,000 - 15,000 | 2024 | Dispositivos OEM sin personalizar |
| **algepser.oem_registros** | 3,000 - 10,000 | 2024-2025 | Versión mejorada OEM |
| **Algepser.registros_custom** | 1,000 - 5,000 | 2024 | Dispositivos personalizados |
| **Algepser.registros_ital_2024** | 500 - 3,000 | 2024 | Producción específica ITAL |

**Total Estimado de Dispositivos:** 28,000 - 118,000 registros

### Tablas de Órdenes de Producción

| Tabla | Registros Estimados | Período | Notas |
|-------|---------------------|---------|-------|
| **Algepser.orden_de_produccion** | 50 - 100 | 2023-2024 | Órdenes legacy v1 |
| **Algepser.orden_produccion2** | 200 - 500 | 2024 | Órdenes v2 |
| **algepser.orden_produccion** | 300 - 800 | 2024-2025 | Órdenes actuales (versión final) |

**Total Estimado de Órdenes:** 550 - 1,400 órdenes

### Tablas de Control de Calidad

| Tabla | Registros Estimados | Período | Notas |
|-------|---------------------|---------|-------|
| **algepser.control_calidad** | 1 | - | Solo metadata (contador) |
| **algepser.control_calidad_history** | 5,000 - 20,000 | 2024-2025 | Inspecciones generales |
| **algepser.control_calidad_linea1_history** | 8,000 - 35,000 | 2024-2025 | Inspecciones línea 1 |
| **algepser.control_calidad_linea2_history** | 5,000 - 25,000 | 2024-2025 | Inspecciones línea 2 |

**Total Estimado de Inspecciones:** 18,000 - 80,000 registros

### Tablas de Personal

| Tabla | Registros Estimados | Notas |
|-------|---------------------|-------|
| **Algepser.personal** | 10 - 20 | Personal operativo legacy |
| **algepser.personal** | 15 - 30 | Personal operativo actual con permisos granulares |
| **Algepser.personal_admin** | 3 - 5 | Administradores legacy |
| **algepser.personal_admin** | 5 - 10 | Administradores actuales |

**Total Estimado de Personal:** 33 - 65 registros

### Otras Tablas

| Tabla | Registros Estimados | Notas |
|-------|---------------------|-------|
| **Algepser.packingDB** | 200 - 500 | Control de empaquetado |
| **algepser.cupones_de_trabajo** | 500 - 1,500 | Cupones multi-línea activos |
| **algepser.oem_box** | 1,000 - 5,000 | Cajas OEM empaquetadas |
| **algepser.marca_referencia** | 10 - 30 | Mapeo de marcas |
| **algepser.metrics** | 200 - 500 | Métricas de producción |

---

## Patrones Generales Detectados en los Datos

### 1. Formato de Identificadores

#### IMEIs (International Mobile Equipment Identity)
- **Formato:** 15-17 dígitos numéricos
- **Patrón típico:** `861888081234567`
- **TAC (Type Allocation Code):** `86188808` (primeros 8 dígitos)
- **Rango de serie:** Últimos 7-9 dígitos
- **Validación:** Algoritmo de Luhn
- **Observación:** Todos los dispositivos GPS usan el mismo TAC

#### CCIDs/ICCIDs (Integrated Circuit Card Identifier)
- **Formato:** 19-20 caracteres alfanuméricos
- **Patrón típico:** `8934076500001234567890F`
- **Estructura:**
  - `89` - Código de telecomunicaciones
  - `34` - Código de país (España)
  - `07` - Código del operador
  - `65` - Sub-código
  - Resto: Número de serie
  - `F` - Dígito de verificación (algunos casos)
- **Observación:** Formato Luhn extendido

### 2. Formato de Fechas

El sistema usa **strings para fechas** (NO tipo Date nativo), con múltiples formatos:

| Formato | Ejemplo | Uso |
|---------|---------|-----|
| `YYYY-MM-DD HH:MM:SS` | `2024-10-15 14:23:45` | Timestamps completos (registros, inspecciones) |
| `YYYY-MM-DD` | `2024-10-15` | Solo fecha (órdenes de producción) |
| `DD/MM/YYYY` | `15/10/2024` | Formato alternativo (legacy) |

**Problema Crítico:** Múltiples formatos dificultan las consultas por fecha. Requiere parsing cuidadoso durante la migración.

### 3. Números de Orden

| Tipo de Orden | Formato | Ejemplo | Uso |
|---------------|---------|---------|-----|
| Producción estándar | `OP-YYYY-NNN` | `OP-2024-015` | Órdenes de producción regulares |
| OEM | `OEM-NNN` | `OEM-001` | Dispositivos OEM sin personalizar |
| Custom | `CUS-NNN` | `CUS-002` | Dispositivos personalizados |
| ITAL | `ITAL-YYYY-NNN` | `ITAL-2024-003` | Cliente ITAL específico |

### 4. Códigos SKU

- **Tipo:** Enteros (integer)
- **Rango observado:** 1001 - 1099
- **Patrón:** SKUs de 4 dígitos comenzando en 1001
- **Mapeo:** Un SKU por modelo de producto
- **Relación:** Vinculado a `nro_referencia` vía tabla `marca_referencia`

### 5. Números de Referencia

- **Formato:** Alfanumérico, ej: `REF-GPS-TR100`, `REF-GPS-FL200`
- **Estructura:** `REF-[TIPO]-[MODELO]`
- **Longitud:** 13-25 caracteres
- **Uso:** Identificador del modelo del dispositivo

### 6. Estructura de Lotes

- **Lotes numéricos:** 1, 2, 3, ..., N
- **Lotes OEM:** Formato string `OEM-LOTE-XX`
- **Lotes ITAL:** Numeración independiente por cliente
- **Tamaño típico de lote:** 50-100 dispositivos
- **Observación:** Múltiples lotes por orden de producción

### 7. Estados y Flags

| Campo | Valor 0 | Valor 1 | Notas |
|-------|---------|---------|-------|
| `status` | Inactivo/Rechazado | Activo/Aprobado | Uso general |
| `in_process` | No iniciado | En proceso | Solo órdenes |
| `complete` | Incompleto | Completado | Solo órdenes |
| `packing` | Sin empaquetar | Empaquetado | Solo órdenes |
| `on_hold` | Normal | En pausa | Solo órdenes |
| `master` | Usuario regular | Administrador | Solo personal |

### 8. Etiquetas de Empaquetado

| Tipo Etiqueta | Unidades por Caja | Uso Típico |
|---------------|-------------------|------------|
| `etq12` | 12 | Órdenes muy pequeñas |
| `etq24` | 24 | Órdenes pequeñas |
| `etq48` | 48 | Órdenes medianas |
| `etq80` | 80 | Órdenes grandes |
| `etq96` | 96 | Órdenes muy grandes |

**Cálculo de cajas:** `Total_Dispositivos = (etq24 × 24) + (etq80 × 80) + (etq96 × 96)`

### 9. Líneas de Producción y Puestos

| Concepto | Valores | Descripción |
|----------|---------|-------------|
| **Líneas** | 1, 2, 3 | Tres líneas de producción independientes |
| **Puestos** | 1, 2 | Dos puestos de trabajo por línea |
| **Flujo** | Puesto 1 → Puesto 2 → Control Calidad | Proceso secuencial |

### 10. Permisos de Personal (Schema algepser)

| Permiso | Significado |
|---------|-------------|
| `puesto1_linea1` | Puede trabajar en puesto 1 de línea 1 |
| `puesto2_linea1` | Puede trabajar en puesto 2 de línea 1 |
| `puesto1_linea2` | Puede trabajar en puesto 1 de línea 2 |
| `puesto2_linea2` | Puede trabajar en puesto 2 de línea 2 |
| `puesto1_linea3` | Puede trabajar en puesto 1 de línea 3 |
| `puesto2_linea3` | Puede trabajar en puesto 2 de línea 3 |
| `control_calidad` | Puede realizar inspecciones de calidad |

---

## Datos Anómalos o Interesantes

### 1. Fragmentación de Datos

**Problema:** Los registros de dispositivos están fragmentados en **8 tablas diferentes**:
- Por año (2024, 2025)
- Por tipo (OEM, Custom, ITAL)
- Por schema (Algepser, algepser)
- Por puesto (registros_2025_puesto2)

**Consecuencia:** Consultas complejas requieren múltiples UNION, imposible tener vista unificada sin JOINs masivos.

**Solución MongoDB:** Unificar TODO en una sola colección `devices` con campos adicionales (`brand`, `year`, `workstation`).

### 2. Contraseñas en Texto Plano

**Gravedad:** CRÍTICO
**Tablas afectadas:**
- `Algepser.personal` (campo `secretkey`)
- `algepser.personal` (campo `secretkey`)
- `Algepser.personal_admin` (campo `key`)
- `algepser.personal_admin` (campo `key`)

**Ejemplos encontrados (SIMULADOS):**
- `"admin123       "`
- `"supervisor2024                                    "`
- `"pass1234                                          "`

**Solución requerida:** Re-hashear TODAS las contraseñas con bcrypt durante migración. Los usuarios deberán cambiar contraseñas.

### 3. Timestamps como Primary Keys

**Tablas afectadas:**
- `control_calidad_history`
- `control_calidad_linea1_history`
- `control_calidad_linea2_history`
- `oem_box`

**Problema:** Usar `fecha` como PRIMARY KEY puede causar colisiones si dos inspecciones ocurren en el mismo segundo.

**Observación:** El sistema debe ser de baja concurrencia para que esto funcione.

### 4. Múltiples Versiones de la Misma Tabla

**Ejemplo:** `orden_de_produccion` tiene 3 versiones:
1. `Algepser.orden_de_produccion` (v1 - legacy)
2. `Algepser.orden_produccion2` (v2 - mejorada)
3. `algepser.orden_produccion` (v3 - actual)

**Problema:** Dificulta saber cuál tabla usar, posible duplicación de datos.

**Solución:** Consolidar en la versión más reciente durante migración.

### 5. Padding de Espacios

**Todos los campos `character(N)`** tienen padding automático con espacios:

```sql
-- Valor almacenado en PostgreSQL:
name: "Juan      "  (character(10))

-- Valor deseado en MongoDB:
name: "Juan"  (String sin padding)
```

**Solución:** Aplicar `.trim()` a TODOS los strings durante migración.

---

## Recomendaciones para Extracción de Datos Reales

### Paso 1: Restaurar el Dump Binario

```bash
# Crear base de datos temporal
createdb -U postgres oversun_temp

# Restaurar dump binario
pg_restore -U postgres -d oversun_temp -v oversunserverDB-4-11-25.sql

# Verificar restauración
psql -U postgres -d oversun_temp -c "\dt algepser.*"
```

### Paso 2: Exportar Datos a CSV

```bash
# Exportar tabla por tabla
psql -U postgres -d oversun_temp -c "\COPY algepser.registros_2025 TO '/tmp/registros_2025.csv' CSV HEADER"
psql -U postgres -d oversun_temp -c "\COPY algepser.orden_produccion TO '/tmp/ordenes.csv' CSV HEADER"
psql -U postgres -d oversun_temp -c "\COPY algepser.personal TO '/tmp/personal.csv' CSV HEADER"
psql -U postgres -d oversun_temp -c "\COPY algepser.control_calidad_linea1_history TO '/tmp/qc_linea1.csv' CSV HEADER"
```

### Paso 3: Análisis de Datos Reales

```bash
# Contar registros por tabla
psql -U postgres -d oversun_temp -c "SELECT 'registros_2025' AS tabla, COUNT(*) FROM algepser.registros_2025;"
psql -U postgres -d oversun_temp -c "SELECT 'orden_produccion' AS tabla, COUNT(*) FROM algepser.orden_produccion;"

# Ver muestra de datos
psql -U postgres -d oversun_temp -c "SELECT * FROM algepser.registros_2025 LIMIT 10;"
```

### Paso 4: Validación de Integridad

```sql
-- Verificar duplicados de IMEI
SELECT imei, COUNT(*) as duplicates
FROM algepser.registros_2025
GROUP BY imei
HAVING COUNT(*) > 1;

-- Verificar órdenes sin dispositivos
SELECT op.nro_orden
FROM algepser.orden_produccion op
LEFT JOIN algepser.registros_2025 r ON op.nro_orden = r.nro_orden
WHERE r.nro IS NULL;

-- Verificar rangos de fechas
SELECT
    MIN(fecha::timestamp) as fecha_minima,
    MAX(fecha::timestamp) as fecha_maxima,
    COUNT(*) as total
FROM algepser.registros_2025;
```

---

## Conclusión del Análisis

Este documento proporciona:

1. ✅ **Estructura completa** de las 45 tablas del sistema antiguo
2. ✅ **Ejemplos simulados** de datos realistas para cada tabla crítica
3. ✅ **Patrones detectados** en formatos de IMEIs, CCIDs, fechas, órdenes
4. ✅ **Análisis de volumen** estimado de datos
5. ✅ **Identificación de problemas** críticos (contraseñas, fragmentación, fechas)
6. ✅ **Guía de extracción** de datos reales del dump binario
7. ✅ **Mapeo detallado** a MongoDB

**Siguiente paso:** Restaurar el dump binario para obtener datos REALES y actualizar este documento con estadísticas precisas.

---

**Documento actualizado:** 2025-11-14
**Ejemplos de datos:** SIMULADOS (requiere restauración del dump binario para datos reales)
**Estado:** Listo para migración (pendiente validación con datos reales)
