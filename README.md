# OSE Platform v2.0.0

Sistema de gestión de producción para plantas fotovoltaicas de Oversun Energy.

## Descripción

OSE Platform es un sistema integral para la gestión de producción en plantas de fabricación de módulos fotovoltaicos. Incluye:

- Autenticación y autorización basada en roles
- Gestión de estaciones de trabajo
- Control de calidad
- Seguimiento de producción en tiempo real
- Generación de reportes y etiquetas QR
- Gestión de empleados y permisos

## Arquitectura

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Base de datos**: MongoDB 6.0
- **ODM**: Beanie 1.24.0
- **Autenticación**: JWT (access + refresh tokens)
- **Seguridad**: bcrypt 3.2.2 + passlib 1.7.4 para hashing de contraseñas
- **Validación**: Pydantic 2.5.3

### Frontend
- **Framework**: React 18/19 con Vite
- **Estado**: Context API
- **Routing**: React Router v6
- **HTTP**: Axios
- **Estilos**: TailwindCSS

### Infraestructura
- **Containerización**: Docker + Docker Compose
- **Puertos**:
  - Backend: 8001
  - Frontend: 5173
  - MongoDB: 27017

## Instalación

### Prerrequisitos
- Docker y Docker Compose instalados
- Git

### Pasos

1. Clonar el repositorio:
```bash
git clone https://github.com/[username]/ose_platform.git
cd ose_platform
```

2. Configurar variables de entorno (crear `.env` si no existe):
```bash
# Backend (.env en backend-new/)
MONGODB_URL=mongodb://mongodb:27017/ose_platform
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

3. Iniciar servicios con Docker Compose:
```bash
docker-compose up -d
```

4. Verificar que los servicios estén corriendo:
```bash
docker-compose ps
```

5. Acceder a la aplicación:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

## Estructura del Proyecto

```
OSE-Platform/
├── backend-new/           # Backend FastAPI
│   ├── app/
│   │   ├── routers/       # Endpoints API
│   │   ├── models/        # Modelos Beanie
│   │   ├── schemas/       # Schemas Pydantic
│   │   ├── auth/          # JWT handlers
│   │   ├── dependencies/  # Dependencias FastAPI
│   │   └── utils/         # Utilidades
│   ├── Dockerfile
│   └── requirements.txt
├── frontend-react/        # Frontend React
│   └── portal/
│       ├── src/
│       │   ├── components/
│       │   ├── services/
│       │   ├── contexts/
│       │   └── pages/
│       ├── Dockerfile
│       └── package.json
├── docker-compose.yml     # Orquestación de servicios
└── README.md
```

## Uso

### Login
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"identifier": "ADMIN", "password": "your-password"}'
```

Respuesta:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": "...",
    "employee_id": "ADMIN",
    "name": "Admin",
    "surname": "User",
    "email": "admin@oversunenergy.com",
    "role": "super_admin",
    "permissions": {...},
    "last_login": "2025-11-17T12:00:00"
  }
}
```

### Endpoints Principales

- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refrescar token
- `GET /api/v1/auth/me` - Información del usuario
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/employees` - Lista empleados (super_admin)
- `POST /api/v1/auth/employees` - Crear empleado (super_admin)
- `PUT /api/v1/auth/employees/{id}` - Actualizar empleado (super_admin)
- `DELETE /api/v1/auth/employees/{id}` - Eliminar empleado (super_admin)

## Roles y Permisos

### Roles disponibles:
- `super_admin` - Acceso total al sistema
- `admin` - Gestión de usuarios y configuración
- `supervisor` - Supervisión de producción
- `operator` - Operador de estación
- `quality_control` - Control de calidad

### Permisos granulares:
Los permisos se asignan por estación/función:
```json
{
  "admin_access": true,
  "manage_users": true,
  "manage_settings": true,
  "view_reports": true,
  "production_line1_station1": true,
  "quality_control": true
}
```

## Troubleshooting

### Error: "Login exitoso pero no accede al dashboard"
**Causa**: Frontend requiere tanto token como objeto user en localStorage.

**Solución**: Verificar que el endpoint `/api/v1/auth/login` retorne el schema completo `LoginResponse`:
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": { ... }  // DEBE estar presente
}
```

### Error: "AttributeError: module 'bcrypt' has no attribute '__about__'"
**Causa**: Incompatibilidad entre bcrypt 5.0.0 y passlib 1.7.4.

**Solución**: El proyecto usa bcrypt 3.2.2 pinneado en requirements.txt. Rebuild:
```bash
cd backend-new
docker-compose down
docker-compose build backend
docker-compose up -d
```

### Error: Cambios en código Python no se reflejan
**Causa**: Docker cache.

**Solución**: Rebuild completo:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Puerto 8001 ya en uso
**Solución**:
```bash
# Windows
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8001 | xargs kill -9
```

### MongoDB no arranca
**Solución**: Verificar que el puerto 27017 esté libre y que Docker tenga permisos para crear volúmenes.

## Desarrollo

### Ejecutar tests
```bash
cd backend-new
docker-compose exec backend pytest
```

### Ver logs
```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo frontend
docker-compose logs -f frontend
```

### Acceder al contenedor
```bash
# Backend
docker-compose exec backend bash

# MongoDB
docker-compose exec mongodb mongosh
```

## Tecnologías

### Backend
- FastAPI 0.109.0
- Motor 3.3.2 (MongoDB async driver)
- Beanie 1.24.0 (ODM)
- python-jose 3.3.0 (JWT)
- passlib 1.7.4 + bcrypt 3.2.2 (password hashing)
- Pydantic 2.5.3 (validation)
- Uvicorn 0.27.0 (ASGI server)

### Frontend
- React 18/19
- Vite
- React Router v6
- Axios
- TailwindCSS

### Database
- MongoDB 6.0

## Seguridad

- Contraseñas hasheadas con bcrypt (12 rounds)
- JWT con access token (30 min) + refresh token (7 días)
- Refresh tokens almacenados en BD
- CORS configurado
- Validación de entrada con Pydantic
- Roles y permisos granulares

## Changelog

### v2.0.0 (2025-11-17)
- Fixed authentication flow - backend now returns complete LoginResponse with user object
- Fixed Pydantic forward reference error in auth schemas
- Pinned bcrypt to 3.2.2 for passlib compatibility
- Updated employee management endpoints
- Enhanced security with JWT refresh tokens

## Licencia

Propiedad de Oversun Energy - Todos los derechos reservados

## Contacto

Para soporte: soporte@oversunenergy.com

---

**Versión**: 2.0.0
**Última actualización**: 2025-11-17
**Estado**: Producción
