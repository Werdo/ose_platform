# 🧪 OSE Platform - Testing Guide

Guía completa para probar y validar el backend de OSE Platform.

## 📋 Tabla de Contenidos

1. [Iniciar el Sistema](#iniciar-el-sistema)
2. [Verificar Health Checks](#verificar-health-checks)
3. [Crear Usuario Admin](#crear-usuario-admin)
4. [Probar Autenticación](#probar-autenticación)
5. [Probar Endpoints CRUD](#probar-endpoints-crud)
6. [Configurar Email](#configurar-email)
7. [Testing Automatizado](#testing-automatizado)
8. [Troubleshooting](#troubleshooting)

---

## 🚀 Iniciar el Sistema

### 1. Levantar los contenedores

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Ver logs
docker-compose logs -f backend
```

### 2. Verificar que los servicios están corriendo

```bash
# Verificar estado de los contenedores
docker-compose ps

# Deberías ver:
# - mongodb (healthy)
# - backend (healthy)
# - mongo-express (opcional, para desarrollo)
```

### 3. Acceder a las interfaces

- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **MongoDB Admin (Mongo Express)**: http://localhost:8081

---

## ✅ Verificar Health Checks

### 1. Health Check Básico

```bash
curl http://localhost:8000/api/v1/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:00:00Z",
  "database": {
    "status": "healthy",
    "collections": 11
  },
  "services": {
    "email": {"status": "not_checked"}
  }
}
```

### 2. Ping Simple

```bash
curl http://localhost:8000/api/v1/health/ping
```

**Respuesta esperada:**
```json
{
  "ping": "pong",
  "timestamp": "2025-01-15T10:00:00Z"
}
```

---

## 👤 Crear Usuario Admin

### Opción 1: Usar MongoDB Shell

```bash
# Conectar a MongoDB
docker exec -it ose-mongodb mongosh -u ose_user -p ose_secure_pass_2025 --authenticationDatabase admin ose_platform

# Crear usuario admin (dentro de mongosh)
db.employees.insertOne({
  employee_id: "ADMIN-001",
  name: "Admin",
  surname: "User",
  email: "admin@oversun.com",
  password_hash: "$2b$10$8K1p/a0dL2LkzJGgWPO8JO7oZPJqW1Yv8K1p/a0dL2LkzJGgWPO8J", // Admin123!
  role: "admin",
  status: "active",
  permissions: {
    production_lines: true,
    stations: true,
    quality_control: true,
    warehouse: true,
    support_tickets: true,
    rma_cases: true,
    customer_management: true,
    reports: true,
    admin_panel: true
  },
  created_at: new Date(),
  last_login: null,
  failed_login_attempts: 0
})
```

### Opción 2: Usar Mongo Express

1. Ir a http://localhost:8081
2. Navegar a `ose_platform` > `employees`
3. Crear documento con los datos del usuario admin

### Opción 3: Usar el endpoint de registro (si lo implementas)

```bash
# POST /api/v1/auth/register (si implementas este endpoint)
```

---

## 🔐 Probar Autenticación

### 1. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@oversun.com",
    "password": "Admin123!"
  }'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": "...",
    "employee_id": "ADMIN-001",
    "name": "Admin",
    "surname": "User",
    "email": "admin@oversun.com",
    "role": "admin",
    "status": "active",
    "permissions": {...}
  },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

**Guardar el access_token para las siguientes pruebas.**

### 2. Obtener Usuario Actual

```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### 3. Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

---

## 📦 Probar Endpoints CRUD

### Empleados

#### Crear Empleado

```bash
curl -X POST http://localhost:8000/api/v1/employees \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP-001",
    "name": "John",
    "surname": "Doe",
    "email": "john@oversun.com",
    "password": "SecurePass123",
    "role": "operator",
    "permissions": {
      "production_lines": true,
      "stations": true
    }
  }'
```

#### Listar Empleados

```bash
curl http://localhost:8000/api/v1/employees?page=1&page_size=50 \
  -H "Authorization: Bearer <access_token>"
```

### Dispositivos

#### Crear Dispositivo

```bash
curl -X POST http://localhost:8000/api/v1/devices \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "imei": "123456789012345",
    "ccid": "8934071234567890123",
    "production_order": "OP-2025-00001",
    "batch": "BATCH-001",
    "production_line": "LINE-1",
    "sku": "OSE-GPS-4G-V2"
  }'
```

#### Obtener Dispositivo por IMEI

```bash
curl http://localhost:8000/api/v1/devices/imei/123456789012345 \
  -H "Authorization: Bearer <access_token>"
```

#### Cambiar Status de Dispositivo

```bash
curl -X POST http://localhost:8000/api/v1/devices/<device_id>/status \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "new_status": "quality_control",
    "reason": "Production completed",
    "notes": "Ready for QC inspection"
  }'
```

#### Estadísticas de Dispositivos

```bash
curl http://localhost:8000/api/v1/devices/stats/overview \
  -H "Authorization: Bearer <access_token>"
```

---

## 📧 Configurar Email

### 1. Obtener Configuración Actual

```bash
curl http://localhost:8000/api/v1/settings/email/config \
  -H "Authorization: Bearer <access_token>"
```

### 2. Actualizar Configuración de Email

```bash
curl -X POST http://localhost:8000/api/v1/settings/email/config \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "smtp_tls": true,
    "smtp_ssl": false,
    "smtp_user": "tu-email@gmail.com",
    "smtp_password": "tu-app-password",
    "smtp_timeout": 30,
    "email_from": "OSE Platform <noreply@oversun.com>",
    "email_reply_to": "support@oversun.com"
  }'
```

### 3. Probar Conexión SMTP

```bash
curl -X POST http://localhost:8000/api/v1/settings/email/test \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "test_connection_only": true
  }'
```

### 4. Enviar Email de Prueba

```bash
curl -X POST http://localhost:8000/api/v1/settings/email/test \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "test_connection_only": false,
    "recipient": "tu-email@example.com"
  }'
```

---

## 🧪 Testing Automatizado

### Ejecutar Tests con Pytest

```bash
# Dentro del contenedor backend
docker exec -it ose-backend pytest

# Con cobertura
docker exec -it ose-backend pytest --cov=app --cov-report=html

# Tests específicos
docker exec -it ose-backend pytest tests/test_auth.py
```

### Ejemplo de Test (tests/test_auth.py)

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_login_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "admin@oversun.com",
                "password": "Admin123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["tokens"]
```

---

## 🔧 Troubleshooting

### Problema: MongoDB no conecta

**Solución:**
```bash
# Verificar logs de MongoDB
docker-compose logs mongodb

# Reiniciar MongoDB
docker-compose restart mongodb

# Verificar credenciales en .env
cat backend/.env | grep MONGODB
```

### Problema: Backend no inicia

**Solución:**
```bash
# Ver logs detallados
docker-compose logs -f backend

# Verificar variables de entorno
docker exec -it ose-backend env | grep MONGODB

# Rebuild del contenedor
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

### Problema: JWT Token inválido

**Solución:**
- Verificar que JWT_SECRET_KEY sea la misma en .env
- Verificar que el token no haya expirado
- Verificar el formato del header: `Authorization: Bearer <token>`

### Problema: CORS errors

**Solución:**
- Verificar CORS_ORIGINS en .env
- Añadir el origen del frontend a CORS_ORIGINS
- Reiniciar el backend después de cambiar .env

### Problema: Email no envía

**Solución:**
- Verificar configuración SMTP en settings
- Probar conexión con `/api/v1/settings/email/test`
- Verificar que el firewall no bloquee el puerto SMTP
- Para Gmail: usar "App Password" en lugar de contraseña normal

---

## 📊 Swagger UI - Testing Interactivo

### 1. Acceder a Swagger

Ir a: http://localhost:8000/docs

### 2. Autenticarse en Swagger

1. Click en el botón **"Authorize"** (candado verde)
2. Ejecutar primero `/auth/login` para obtener token
3. Copiar el `access_token` de la respuesta
4. En el modal de autorización, pegar: `Bearer <access_token>`
5. Click en **"Authorize"**

### 3. Probar Endpoints

Ahora puedes probar todos los endpoints directamente desde Swagger UI.

---

## ✅ Checklist de Testing Completo

- [ ] Health checks funcionan
- [ ] Login con usuario admin exitoso
- [ ] Crear, listar, actualizar, eliminar empleados
- [ ] Crear, listar, actualizar dispositivos
- [ ] Cambiar status de dispositivos
- [ ] Obtener estadísticas
- [ ] Configurar email desde API
- [ ] Probar conexión SMTP
- [ ] Enviar email de prueba
- [ ] Rate limiting funciona (5 logins por minuto)
- [ ] Refresh token funciona
- [ ] Password reset funciona
- [ ] Logs de auditoría se registran
- [ ] CORS funciona desde frontend
- [ ] MongoDB persistencia funciona (reiniciar contenedor)

---

## 🎯 Próximos Pasos

Una vez completado el testing del backend:

1. **Desarrollar Frontend** - React/Vue para cada aplicación
2. **Añadir Endpoints Restantes** - Production orders, tickets, RMA, customers
3. **Implementar WebSockets** - Para notificaciones en tiempo real
4. **Añadir Reportes** - Exportación a PDF/Excel
5. **Optimizar Queries** - Índices adicionales en MongoDB
6. **Deploy a Producción** - Configurar CI/CD, SSL, backups

---

**¿Preguntas o problemas?** Consulta los logs y la documentación de MongoDB/FastAPI.
