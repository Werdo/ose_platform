# OSE Platform - Backend API v2.0

Sistema de gestión integral para dispositivos IoT/GPS desarrollado con FastAPI y MongoDB.

## 🏗️ Arquitectura

- **Framework**: FastAPI 0.109.0
- **Base de Datos**: MongoDB 7.0 con Beanie (ODM async)
- **Autenticación**: JWT (JSON Web Tokens)
- **Servicios**:
  - Email: aiosmtplib + Jinja2
  - PDF: WeasyPrint + Jinja2
  - QR: qrcode + PIL
  - Documentos: openpyxl, pandas

## 📋 Requisitos Previos

- Python 3.11+
- MongoDB 7.0+
- Docker y Docker Compose (opcional)

## 🚀 Instalación

### Opción 1: Instalación Local

1. **Clonar el repositorio**
```bash
cd backend-new
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Iniciar MongoDB** (si no está en Docker)
```bash
mongod --dbpath /path/to/data
```

6. **Ejecutar el servidor**
```bash
python main.py
# o
uvicorn main:app --reload
```

7. **Acceder a la documentación**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Opción 2: Docker Compose (Recomendado)

1. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env
```

2. **Iniciar servicios**
```bash
docker-compose up -d
```

3. **Ver logs**
```bash
docker-compose logs -f backend
```

4. **Acceder**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- MongoDB: localhost:27017

## 📁 Estructura del Proyecto

```
backend-new/
├── main.py                      # Aplicación FastAPI principal
├── requirements.txt             # Dependencias Python
├── Dockerfile                   # Dockerfile para producción
├── docker-compose.yml           # Orquestación de servicios
├── .env.example                 # Variables de entorno de ejemplo
│
├── platform/
│   ├── __init__.py
│   ├── config.py                # Configuración centralizada
│   ├── database.py              # Conexión MongoDB/Beanie
│   │
│   ├── auth/                    # Autenticación
│   │   ├── __init__.py
│   │   └── jwt_handler.py       # Manejo de JWT tokens
│   │
│   ├── models/                  # Modelos MongoDB (Beanie)
│   │   ├── __init__.py
│   │   ├── device.py            # Dispositivos
│   │   ├── device_event.py      # Eventos de dispositivos
│   │   ├── movimiento.py        # Movimientos logísticos ⭐
│   │   ├── production_order.py  # Órdenes de producción
│   │   ├── employee.py          # Empleados/Usuarios
│   │   ├── customer.py          # Clientes
│   │   ├── quality_control.py   # Control de calidad
│   │   ├── service_ticket.py    # Tickets de soporte
│   │   ├── rma_case.py          # Casos RMA
│   │   ├── inventory.py         # Inventario
│   │   ├── metric.py            # Métricas/KPIs
│   │   └── setting.py           # Configuración del sistema
│   │
│   ├── schemas/                 # Schemas Pydantic
│   │   ├── __init__.py
│   │   ├── auth.py              # Schemas de autenticación
│   │   └── app1.py              # Schemas App 1
│   │
│   ├── routers/                 # Routers FastAPI
│   │   ├── __init__.py
│   │   ├── auth.py              # Login, logout, refresh
│   │   └── app1_notify.py       # App 1: Notificación Series ⭐
│   │
│   ├── services/                # Servicios auxiliares
│   │   ├── __init__.py
│   │   ├── mail_service.py      # Envío de emails
│   │   ├── pdf_service.py       # Generación de PDFs
│   │   └── qr_service.py        # Generación de QR codes
│   │
│   ├── dependencies/            # FastAPI dependencies
│   │   ├── __init__.py
│   │   └── auth.py              # Dependencies de autenticación
│   │
│   ├── utils/                   # Utilidades
│   │   ├── __init__.py
│   │   └── security.py          # Hashing, JWT, encryption
│   │
│   └── templates/               # Templates Jinja2
│       ├── emails/              # Templates de email
│       │   └── notificacion_series.html
│       ├── etiquetas/           # Etiquetas para impresión
│       │   ├── etiqueta_dispositivo.html
│       │   └── etiqueta_paquete.html
│       └── pdfs/                # Templates de PDF
│
├── uploads/                     # Archivos subidos
└── logs/                        # Logs de la aplicación
```

## 🔐 Autenticación

### Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "identifier": "EMP001",  # Employee ID o email
  "password": "password123"
}

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Usar Token
```bash
GET /api/auth/me
Authorization: Bearer {access_token}
```

## 📱 Aplicaciones

### App 1: Notificación de Series ⭐

Notifica dispositivos a clientes específicos.

**Endpoint Principal:**
```bash
POST /api/app1/notificar
Authorization: Bearer {token}
Content-Type: application/json

{
  "cliente_id": "507f1f77bcf86cd799439011",
  "series": [
    "123456789012345",
    "123456789012346"
  ],
  "ubicacion": "Almacén Central - Madrid",
  "enviar_email": true
}

# Response:
{
  "success": true,
  "notificados": 2,
  "errores": [],
  "detalles": [...],
  "email_enviado": true
}
```

**Otros Endpoints:**
- `GET /api/app1/dispositivos` - Buscar dispositivos
- `GET /api/app1/dispositivos/{imei}` - Info de dispositivo
- `GET /api/app1/dispositivos/{imei}/historial` - Historial completo
- `GET /api/app1/clientes` - Listar clientes
- `GET /api/app1/clientes/{id}/estadisticas` - Estadísticas de cliente

## 🗄️ Modelos de Datos Principales

### Device (Dispositivo)
- **Campos clave**: `imei`, `ccid`, `nro_orden`, `lote`, `estado`, `cliente`
- **Estados**: `en_produccion`, `control_calidad`, `aprobado`, `activo`, `defectuoso`, `rma`
- **Métodos**: `marcar_como_notificado()`, `buscar_por_imei()`, `buscar_por_paquete()`

### DeviceEvent (Evento de Dispositivo)
- Trazabilidad completa del ciclo de vida
- **Tipos de eventos**: `created`, `notified_to_client`, `quality_check_passed`, `shipped`, etc.
- Índices optimizados para búsquedas por dispositivo y fecha

### Movimiento (Logística) ⭐ NUEVO
- **Tipos**: `entrada`, `salida`, `envio`, `transferencia`, `devolucion`, `produccion`
- Trazabilidad de movimientos logísticos
- Integración con notificación de series

### Customer (Cliente)
- Información de clientes/distribuidores
- Contador de dispositivos activos
- Historial de notificaciones

## 🛠️ Servicios

### Mail Service
```python
from platform.services.mail_service import mail_service

await mail_service.send_notification_email(
    to="cliente@empresa.com",
    customer_name="Cliente XYZ",
    series_count=10,
    series_list=["123...", "456..."],
    ubicacion="Madrid"
)
```

### PDF Service
```python
from platform.services.pdf_service import pdf_service

# Generar etiqueta de dispositivo
pdf_bytes = pdf_service.generate_device_label(
    imei="123456789012345",
    ccid="89340123456789012345",
    marca="OversunTrack"
)
```

### QR Service
```python
from platform.services.qr_service import qr_service

# Generar QR de dispositivo
qr_bytes = qr_service.generate_device_qr(
    imei="123456789012345",
    ccid="89340123456789012345"
)
```

## 🔧 Configuración Avanzada

### Variables de Entorno Importantes

```bash
# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=ose_platform

# JWT
SECRET_KEY=your-very-long-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# SMTP (para emails)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Features
FEATURE_APP1_ENABLED=true
FEATURE_APP2_ENABLED=true
# ... etc
```

### Crear Primer Usuario

```python
# Desde Python shell
from platform.models.employee import Employee, EmployeeRole
from platform.utils.security import hash_password
import asyncio

async def create_admin():
    admin = Employee(
        employee_id="ADMIN",
        name="Admin",
        surname="System",
        email="admin@oversunenergy.com",
        password_hash=hash_password("admin123"),
        role=EmployeeRole.SUPER_ADMIN
    )
    await admin.insert()
    print("Admin creado")

asyncio.run(create_admin())
```

## 📊 Monitoreo y Logs

### Health Check
```bash
GET /health

# Response:
{
  "status": "healthy",
  "api": "online",
  "database": "healthy",
  "version": "2.0.0"
}
```

### Logs
Los logs se guardan en:
- Consola (desarrollo)
- `logs/ose-platform.log` (producción)

## 🧪 Testing

```bash
# TODO: Implementar tests
pytest tests/
```

## 🚢 Despliegue en Producción

1. **Configurar variables de entorno de producción**
2. **Cambiar SECRET_KEY a un valor aleatorio seguro**
3. **Configurar SMTP con credenciales reales**
4. **Usar MongoDB en replica set para alta disponibilidad**
5. **Configurar HTTPS con nginx/traefik**
6. **Habilitar logging adecuado**

### Docker Compose Producción
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📚 Documentación Adicional

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🤝 Soporte

Para soporte técnico:
- Email: support@oversunenergy.com
- Documentación interna: Ver carpeta `Aplicaciones OSE/`

## 📝 Licencia

© 2025 Oversun Energy. Todos los derechos reservados.

---

**Versión**: 2.0.0
**Última actualización**: 2025-01-15
