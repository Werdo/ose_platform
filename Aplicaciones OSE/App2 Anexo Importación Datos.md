Perfecto — te dejo la **documentación técnica completa y práctica** para crear una **aplicación generadora de ICCID y MSISDN**. Está pensada para que puedas pasarla a desarrollo directamente (o usarla tú mismo para generar el primer prototipo). Contiene requisitos, modelo de datos, algoritmos (incluye Luhn), API, UI/CLI, ejemplos de archivos de salida, pruebas, seguridad y despliegue.

# Generador ICCID ↔ MSISDN — Especificación funcional y técnica

## 1. Objetivo

Crear una aplicación que:

* Genere **series de ICCID** válidos (E.118 + dígito Luhn) siguiendo rangos y/o patrones existentes.
* Asigne **MSISDN** correlativos o según reglas configurables.
* Permita generar reels/batches (por ejemplo 3.000, 50.000), exportar a CSV/XLSX y auditar la operación.
* Validar y verificar integridad (duplicados, Luhn, rangos).
* Facilitar integraciones (API REST y CLI) para uso automatizado o manual.

---

## 2. Requisitos funcionales (resumido)

* Ingreso de rangos (ICCID start, ICCID end) y generación de todos los ICCID entre ambos con recalculo del dígito Luhn.
* Posibilidad de generar N ICCID consecutivos a partir de un ICCID start.
* Asignación de MSISDN: 3 modos

  1. **Auto**: partiendo de un MSISDN inicial y asignando +1 por cada ICCID.
  2. **Map basado en reglas**: prefijo fijo + secuencia con padding.
  3. **Sin MSISDN**: solo generar ICCID.
* Exportar a CSV/XLSX, con columnas configurables (ICCID, Body, CheckDigit, MSISDN, Batch, Timestamp).
* Reportes: resumen (cantidad generada, primer/último, validación Luhn OK%), logs y auditoría.
* UI simple para batches + API programática (JSON).
* Prevención de duplicados (comparar con base de datos/inventario).
* Soporte para eSIM/EID escenarios (opcional extensión).

---

## 3. Requisitos no funcionales

* Rendimiento: generación de 250k rows en < 30s (depende del hardware).
* Concurrencia: evitar race conditions en asignación de MSISDN.
* Persistencia: PostgreSQL para inventario; archivos en disco o S3 para export.
* Seguridad: autenticación (JWT/OAuth2), roles (admin/generator/auditor).
* Trazabilidad: cada generación guarda usuario, batch_id, parámetros y checksum del fichero.
* Internacionalización (ES / EN).

---

## 4. Arquitectura propuesta

* **Backend**: FastAPI (Python) — rápido para APIs, fácil de probar.
* **DB**: PostgreSQL (tabla `iccid_inventory`, `generation_jobs`).
* **Frontend**: React (Facit template si lo deseas) — modulo admin para generar y descargar.
* **CLI**: Script `generate_iccid` (Python) para ejecución rápida en servidores.
* **Storage**: filesystem o S3 para CSV/XLSX.
* **Autenticación**: JWT with OAuth2 password flow or SSO.
* **Containerización**: Docker, orquestado con K8s.

---

## 5. Modelo de datos (simplificado)

### Tabla `iccid_inventory`

* `id` SERIAL PK
* `iccid` VARCHAR(32) UNIQUE NOT NULL
* `body` VARCHAR(31) NOT NULL  -- ICCID sin dígito
* `check_digit` CHAR(1) NOT NULL
* `msisdn` VARCHAR(20) NULL
* `batch_id` VARCHAR(50) NULL
* `status` VARCHAR(20) -- e.g., available, assigned, used
* `created_at` TIMESTAMP
* `assigned_at` TIMESTAMP
* `notes` TEXT

### Tabla `generation_jobs`

* `job_id` UUID PK
* `user` VARCHAR
* `batch_id` VARCHAR
* `iccid_start` VARCHAR
* `iccid_end` VARCHAR
* `msisdn_start` VARCHAR NULL
* `count_requested` INT
* `count_generated` INT
* `mode` VARCHAR -- e.g., range_inclusive, n_from_start
* `created_at`, `finished_at`
* `status` (pending/running/done/error)
* `file_path` text (link to csv/xlsx)

---

## 6. Algoritmos y reglas

### 6.1 Cálculo dígito Luhn (para ICCID)

Pseudocódigo (Python-like):

```
def luhn_check_digit(number_without_check: str) -> str:
    digits = [int(d) for d in number_without_check + "0"]
    odd = digits[-1::-2]
    even = digits[-2::-2]
    checksum = sum(odd)
    for d in even:
        d2 = d * 2
        if d2 > 9:
            d2 -= 9
        checksum += d2
    return str((10 - (checksum % 10)) % 10)
```

Validación Luhn:

```
def luhn_is_valid(full_number: str) -> bool:
    base, chk = full_number[:-1], full_number[-1]
    return luhn_check_digit(base) == chk
```

### 6.2 Generación ICCID

* Tomar `pad = len(iccid) - 1` como longitud del body.
* Convertir start_body = int(start_iccid[:-1]), end_body = int(end_iccid[:-1]).
* Iterar `for b in range(start_body, end_body + 1)`:

  * body_str = str(b).zfill(pad)
  * check = luhn_check_digit(body_str)
  * iccid = body_str + check

### 6.3 Asignación MSISDN

* Si `msisdn_start` proporcionado: msisdn = msisdn_start + index.
* Formateo: pad con ceros si necesario; validar formato E.164 si quieres (opcional).

### 6.4 Reglas anti-duplicado

* Antes de insertar o marcar, verificar existencia en `iccid_inventory`.
* Si existe y status != 'available', fallar o registrar conflicto (según política).

---

## 7. API (REST) — endpoints principales

### POST /api/v1/generate

Request body (JSON):

```json
{
  "batch_id": "60086",
  "mode": "range_inclusive",             // or "count_from_start"
  "iccid_start": "8934014042530750015",
  "iccid_end": "8934014042530780004",
  "count": 3000,                         // optional, used in count_from_start
  "msisdn_start": "882390118251850",     // optional
  "export": ["csv","xlsx"],              // optional
  "columns": ["ICCID","MSISDN","Body","CheckDigit","Batch"]
}
```

Response:

```json
{
  "job_id": "uuid",
  "status": "pending",
  "estimated_count": 3000
}
```

### GET /api/v1/generate/{job_id}/status

Response shows progress and download link when done.

### GET /api/v1/inventory?batch=60086

List ICCIDs by batch, pagination.

### POST /api/v1/validate

Validate one or many ICCID strings (return Luhn status, dup status).

---

## 8. UI / UX

* Página “New Batch”:

  * Inputs: batch_id, iccid_start, iccid_end OR count, msisdn_start (optional), export options, columns.
  * Preview 10 first/last.
  * Button: Generate (shows job ID and progress).
* Page “Jobs”:

  * List de jobs con status, descargar CSV/XLSX.
* Page “Inventory”:

  * Filtros por prefix, batch, msisdn, status.
* Botón “split” para dividir en reels (ej: chunk size 500 o 1000) y descargar múltiples ficheros.

---

## 9. Formatos de salida

* CSV: columnas en orden configurado, header incluido, encoding UTF-8, CRLF opcional.
* XLSX: hoja con metadatos (job info): batch_id, date, count_generated, user.
* Naming convention: `batch_{batch_id}_{job_id}_{rows}rows_{YYYYMMDD_HHMM}.csv`

---

## 10. Validaciones y pruebas

* Unit tests:

  * test_luhn_known_examples()
  * test_generate_range_inclusive()
  * test_generate_n_from_start()
  * test_no_duplicates_when_inventory_has_preexisting()
* Integration tests:

  * API generate -> job -> file download -> Luhn validation of all rows.
* Edge cases:

  * start > end -> error.
  * different lengths -> error.
  * non-digit characters in inputs -> sanitize & error.
  * excessively large ranges ( > 1M ) -> require confirmation/warning.

---

## 11. Seguridad y roles

* Usuarios: `admin` (crear, borrar), `generator` (crear jobs), `auditor` (ver, download).
* Autenticación: JWT + password + optional SSO.
* Rate limit: per-user job limit (avoid DoS).
* File retention: configurable (e.g., 30 days) and secure deletion.

---

## 12. Logging & Audit

* Guardar en `generation_jobs`: parameters, user, start/finish, exception messages.
* Store hash (SHA256) of generated file for integrity check.
* Each ICCID inserted into inventory must have `created_by` and timestamp.

---

## 13. CLI (ejemplos)

Comando básico:

```
generate_iccid --batch 60086 --start 8934014042530750015 --end 8934014042530780004 --msisdn-start 882390118251850 --out batch_60086.csv
```

Opciones:

* `--chunk-size` (dividir salida)
* `--dry-run` (no escribir)
* `--overwrite` (si ya existe)

---

## 14. Deployment y CI/CD

* Dockerfile para backend; Github Actions para tests + build + push.
* K8s manifests para deployment; mount secrets para DB credentials.
* Cron job o cleanup job para borrar archivos antiguos.

---

## 15. Consideraciones operativas y notas

* **No existe relación matemática entre ICCID y MSISDN** — solo asignarás MSISDN por regla de negocio. Guarda mapping en la DB.
* **Luhn**: recalcular siempre — no usar patrones “+8” manualizados: el paso correcto es incrementar el cuerpo y recalcular.
* **eSIM**: si trabajas con eUICC, cada perfil tiene ICCID; podrías añadir campo `eid` y `profile_name`.
* **Integración con Operador**: antes de entregar lotes al operador, conviene exportar en el layout que el operador exige (campos, orden, encoding).
* **Backup**: realiza backup de la tabla `iccid_inventory` antes de cargas masivas.

---

## 16. Ejemplo de implementación mínima (pseudocódigo)

```python
# FastAPI endpoint
@router.post("/generate")
def generate(payload):
    # validate payload
    pad = len(payload.iccid_start) - 1
    start = int(payload.iccid_start[:-1])
    end = int(payload.iccid_end[:-1]) if payload.iccid_end else start + payload.count - 1

    # check duplicates in DB
    # start job row in generation_jobs

    results = []
    for i, b in enumerate(range(start, end+1)):
        body = str(b).zfill(pad)
        check = luhn_check_digit(body)
        iccid = body + check
        msisdn = None
        if payload.msisdn_start:
            msisdn = str(int(payload.msisdn_start) + i)
        results.append((iccid, body, check, msisdn))
        # optionally stream to CSV to avoid memory spike

    # insert to iccid_inventory with batch info, mark assigned if msisdn present
    # finalize job, save file
    return job_id
```

---

## 17. Checklist de entrega para cuando quieras que lo desarrollen

* [ ] Endpoints listos y documentados (OpenAPI).
* [ ] Scripts unitarios para Luhn + gen range.
* [ ] DB schema aplicado y migrations.
* [ ] UI minimal funcional (generate, jobs, inventory).
* [ ] Jobs asíncronos (celery / background worker) para rangos grandes.
* [ ] Logging + auditoría + tests.

---

Si quieres, ahora:

* 1. Te preparo un **README técnico** listo para un repo con ejemplos de comando y cómo ejecutar localmente (Docker + docker-compose).
* 2. O genero **el esqueleto del backend (FastAPI)** con los endpoints básicos y tests unitarios iniciales (listo para poner en Git).
* 3. O te entrego **el script CLI** completo para generar ICCID y CSV (lista para ejecutar en el servidor).

Dime cuál te interesa que haga y lo genero.
