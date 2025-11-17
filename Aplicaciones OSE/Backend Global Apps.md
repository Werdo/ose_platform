✅ Documento generado: **Backend Global Apps**
# 📘 Documentación Técnica Backend – Plataforma Global de Aplicaciones (Apps 1–6)

Versión: `v1.0.0`
Última actualización: 2025-11-11

---

## 🧭 1. Propósito General

Este backend unificado gestiona todas las funcionalidades de las aplicaciones 1 a 6 del ecosistema AssetFlow. Incluye control de usuarios, trazabilidad, operaciones logísticas, generación de documentos y comunicaciones con terceros.

Está diseñado como **micro-backend modular bajo un mismo núcleo** con autenticación JWT, conexión con MongoDB, motor de templates para PDFs y componentes reutilizables.

---

## ⚙️ 2. Aplicaciones Integradas

| App | Funcionalidad                                        |
| --- | ---------------------------------------------------- |
| 1   | Notificación de números de serie a clientes          |
| 2   | Importación estructurada de datos (CSV, Excel)       |
| 3   | Registro y gestión de tickets postventa y RMA        |
| 4   | Transformación de documentos externos                |
| 5   | Generación automática de facturas desde tickets      |
| 6   | Picking de palets y paquetería, etiquetas y tracking |

---

## 🧱 3. Arquitectura Técnica

* Lenguaje: `Python 3.11`
* Framework: `FastAPI`
* DB: `MongoDB` (conexión única)
* Motor de PDF: `WeasyPrint`
* Plantillas: `Jinja2`
* Autenticación: `JWT + OAuth2PasswordBearer`
* Background tasks: `FastAPI BackgroundTasks`

### Estructura modular de carpetas

```bash
/backend/platform/
├── main.py
├── auth/
│   └── security.py
├── config.py
├── database.py
├── routers/
│   ├── app1_notify.py
│   ├── app2_import.py
│   ├── app3_tickets.py
│   ├── app4_transform.py
│   ├── app5_facturas.py
│   ├── app6_picking.py
├── models/
│   └── [por app]
├── services/
│   ├── pdf_service.py
│   ├── mail_service.py
│   ├── mongo_service.py
│   └── qr_service.py
└── templates/
    └── [facturas, etiquetas, emails...]
```

---

## 🔐 4. Autenticación y Seguridad

* JWT con roles (`admin`, `operador`, `cliente`, `tecnico`, etc.)
* Rate-limiting por IP (opcional)
* Protección CORS
* Autorización granular por endpoint
* Logs por usuario/IP/token

---

## 🔁 5. API REST Unificada

### Categorías de rutas:

#### 🔹 Autenticación

* `/auth/login`
* `/auth/register`
* `/auth/refresh`

#### 🔹 Notificación (App 1)

* `/api/notificar`
* `/api/notificaciones`

#### 🔹 Importación (App 2)

* `/api/importar`
* `/api/importar/preview`

#### 🔹 Incidencias (App 3)

* `/api/tickets/nuevo`
* `/api/tickets/{id}`
* `/api/rma/generar`

#### 🔹 Documentos externos (App 4)

* `/api/transformar`
* `/api/plantillas`

#### 🔹 Facturas (App 5)

* `/api/factura/generar`
* `/api/factura/{id}`

#### 🔹 Picking (App 6)

* `/api/pallets/nuevo`
* `/api/paquetes/nuevo`
* `/api/paquetes/notificar`

---

## 🧠 6. Servicios Comunes

### `mongo_service.py`

* CRUD generalizado
* Funciones de búsqueda y validación cruzada

### `pdf_service.py`

* Generación de PDF desde Jinja2 → WeasyPrint
* Uso de plantillas personalizadas por App

### `mail_service.py`

* Envío SMTP con plantillas HTML
* Manejo de CC, adjuntos, firmas

### `qr_service.py`

* Generación de QR dinámico
* Embebido en PDFs o retorno como imagen

---

## 🧪 7. Testing y Calidad

* Pruebas unitarias por módulo (`pytest`)
* Mocks de base de datos y servicios externos
* Tests de rendimiento para endpoints críticos
* Cobertura mínima recomendada: 85%

---

## 📈 8. Logging y Métricas

* Logs JSON estructurados por usuario, acción, timestamp
* Métricas integradas vía Prometheus
* Integrable con Grafana / UptimeKuma / Elastic

---

## 📦 9. Despliegue recomendado

* Servidor Linux Ubuntu 22.04+
* MongoDB replicado o single node
* Uvicorn + Nginx + Supervisor
* SMTP configurado (mailgun o propio)
* Certificados TLS si expuesto públicamente

---

## 📄 10. Versionado y Releases

* Actualizaciones por módulo independiente
* Integración continua con `GitHub Actions` o `GitLab CI`
* Docker disponible por app o por plataforma unificada

---

## 🔗 11. Dependencias y librerías clave

```txt
fastapi
uvicorn[standard]
pymongo
motor
python-jose
passlib
jinja2
weasyprint
python-multipart
python-dotenv
qrcode
email-validator
pytest
```

---

## ✅ 12. Estado actual

* Apps 1 a 6 conectadas
* MongoDB centralizado
* Envío de correos operativo
* Generación de PDFs y etiquetas estable
* Preparado para extensión con App 7+ (postventa, inventario avanzado, etc.)

---

## 📌 13. Referencias cruzadas

* `App1 Notificación`: IMEIs y clientes【691340003dc4819192ecbb7be16f5342】
* `App2 Importación`: CSV estructurados【69133f0b00448191b7f410206e9f9826】
* `App3 RMA`: tickets de servicio y devoluciones【6913408d25f4819196809ab16df89367】
* `App4 Transformación`: OCR y mapeo documental【691340fa00d48191868348db21441b30】
* `App5 Factura`: PDF y email al cliente【69134052b2bc8191b5f66124999773e9】
* `App6 Picking`: palets, paquetes y logística【691343e7fcf8819193a27ee170285be7】
