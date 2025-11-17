# OSE Platform - Portal Público: Guía de Despliegue y Seguridad

## Resumen del Sistema

El **Portal Público de RMA/Tickets** es una aplicación independiente que permite a clientes externos:

- ✅ Registrarse y crear cuentas
- ✅ Iniciar sesión de forma segura
- ✅ Crear tickets de soporte basados en IMEI de dispositivos
- ✅ Comunicarse con el equipo de soporte mediante chat integrado
- ✅ Seguimiento del estado de sus tickets en tiempo real

Desde el **Portal de Gestión** (Admin), los empleados pueden:

- ✅ Ver y gestionar todos los usuarios públicos
- ✅ Crear usuarios públicos manualmente
- ✅ Bloquear/desbloquear usuarios
- ✅ Ver todos los tickets de cada usuario
- ✅ Responder mensajes y gestionar tickets

---

## Arquitectura del Sistema

### Componentes

1. **Backend** (FastAPI - Python)
   - Puerto: 8001
   - Base de datos: MongoDB
   - API REST con JWT authentication
   - Endpoints separados para:
     - Empleados: `/api/v1/auth/*`, `/api/v1/app3/*`
     - Usuarios públicos: `/api/v1/public/auth/*`, `/api/v1/public/tickets/*`

2. **Portal de Gestión** (Admin - React)
   - Puerto: 3002
   - Para empleados internos
   - Gestión completa de tickets y usuarios públicos

3. **Portal Público** (React)
   - Puerto: 3003
   - Para clientes externos
   - Interfaz simplificada para crear y consultar tickets

### Flujo de Autenticación

```
Usuarios Públicos:
1. Registro en /public/auth/register
2. Login en /public/auth/login
3. JWT token (válido 7 días)
4. Token tipo "public" en payload

Empleados:
1. Login en /api/v1/auth/login
2. JWT token (válido 30 minutos)
3. Token tipo "employee" en payload
```

---

## Instalación Local

### Backend

```bash
cd backend-new

# Activar entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tu configuración

# Ejecutar
python main.py
```

### Portal de Gestión (Admin)

```bash
cd frontend-react/portal

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev  # Puerto 3002
```

### Portal Público

```bash
cd frontend-public-portal

# Instalar dependencias
npm install

# Configurar API URL
cp .env.example .env
# Editar VITE_API_URL

# Ejecutar en desarrollo
npm run dev  # Puerto 3003
```

---

## Despliegue en Producción

### 1. Backend (FastAPI)

#### Opción A: Docker

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: secure_password

  backend:
    build: ./backend-new
    ports:
      - "8001:8001"
    environment:
      - MONGODB_URI=mongodb://admin:secure_password@mongodb:27017
      - JWT_SECRET_KEY=your-super-secure-secret-key-min-32-chars
      - CORS_ORIGINS=https://portal.tu-dominio.com,https://admin.tu-dominio.com
    depends_on:
      - mongodb

volumes:
  mongo_data:
```

Ejecutar:

```bash
docker-compose up -d
```

#### Opción B: VPS (Ubuntu/Debian)

```bash
# Instalar dependencias
sudo apt update
sudo apt install python3.11 python3.11-venv nginx mongodb

# Configurar aplicación
cd /opt/ose-platform
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Crear servicio systemd
sudo nano /etc/systemd/system/ose-backend.service
```

**ose-backend.service:**

```ini
[Unit]
Description=OSE Platform Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/ose-platform/backend-new
Environment="PATH=/opt/ose-platform/venv/bin"
ExecStart=/opt/ose-platform/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable ose-backend
sudo systemctl start ose-backend
```

### 2. Portal de Gestión (Admin)

```bash
cd frontend-react/portal

# Build
npm run build

# Los archivos están en dist/
```

Desplegar en:
- **Vercel**: `vercel --prod`
- **Netlify**: `netlify deploy --prod`
- **AWS S3 + CloudFront**
- **Nginx** (servidor propio)

### 3. Portal Público

```bash
cd frontend-public-portal

# Configurar API URL de producción
echo "VITE_API_URL=https://api.tu-dominio.com/api/v1" > .env

# Build
npm run build
```

#### Recomendado: Desplegar en CDN separado

El portal público debe estar en un dominio/servidor separado del portal de gestión:

- Portal de gestión: `https://admin.tu-dominio.com` (restringido por IP)
- Portal público: `https://portal.tu-dominio.com` (acceso público)

**Ventajas:**
- Mayor seguridad (aislamiento)
- Mejor escalabilidad
- Fácil implementación de CDN
- Menor carga en servidor principal

---

## Configuración de Seguridad

### 1. CORS (Backend)

Editar `backend-new/app/config.py`:

```python
CORS_ORIGINS: List[str] = [
    "https://admin.tu-dominio.com",  # Portal de gestión
    "https://portal.tu-dominio.com",  # Portal público
]
```

### 2. JWT Tokens

- **Empleados**: Token válido 30 minutos
- **Usuarios públicos**: Token válido 7 días
- Usar `JWT_SECRET_KEY` fuerte (mínimo 32 caracteres)

### 3. Contraseñas

- Mínimo 8 caracteres (configurado en backend)
- Hashing con bcrypt (implementado)

### 4. Rate Limiting (Recomendado)

Instalar `slowapi`:

```bash
pip install slowapi
```

Configurar en `main.py`:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# En endpoints públicos
@router.post("/login")
@limiter.limit("5/minute")  # 5 intentos por minuto
async def login(request: Request, ...):
    ...
```

### 5. HTTPS Obligatorio

**Nginx Configuration:**

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name portal.tu-dominio.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS - Portal Público
server {
    listen 443 ssl http2;
    server_name portal.tu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/portal.tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/portal.tu-dominio.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /var/www/portal-publico/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# HTTPS - Portal de Gestión (Admin)
server {
    listen 443 ssl http2;
    server_name admin.tu-dominio.com;

    ssl_certificate /etc/letsencrypt/live/admin.tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/admin.tu-dominio.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Restringir por IP (opcional pero recomendado)
    allow 1.2.3.4;  # IP de oficina
    deny all;

    root /var/www/portal-admin/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Obtener certificado SSL con Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d portal.tu-dominio.com -d admin.tu-dominio.com
```

### 6. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable

# Bloquear acceso directo a MongoDB desde fuera
sudo ufw deny 27017
```

### 7. MongoDB Security

```javascript
// Conectar a MongoDB
use admin

// Crear usuario admin
db.createUser({
  user: "admin",
  pwd: "secure_password_here",
  roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase", "readWriteAnyDatabase"]
})

// Crear usuario específico para la app
use ose_platform
db.createUser({
  user: "ose_app",
  pwd: "app_password_here",
  roles: [{role: "readWrite", db: "ose_platform"}]
})
```

Editar `/etc/mongod.conf`:

```yaml
security:
  authorization: enabled

net:
  bindIp: 127.0.0.1  # Solo localhost
```

### 8. Logs y Monitoreo

Configurar logging en `main.py`:

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/ose-platform.log',
    maxBytes=10000000,  # 10MB
    backupCount=5
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[handler]
)
```

---

## Checklist de Seguridad Pre-Producción

- [ ] Cambiar `JWT_SECRET_KEY` a valor único y seguro (mín. 32 chars)
- [ ] Cambiar contraseñas de MongoDB
- [ ] Configurar HTTPS con certificado válido
- [ ] Actualizar `CORS_ORIGINS` con dominios reales
- [ ] Implementar rate limiting en endpoints públicos
- [ ] Configurar firewall (UFW/iptables)
- [ ] Habilitar autenticación en MongoDB
- [ ] Configurar backups automáticos de MongoDB
- [ ] Implementar logging y monitoreo
- [ ] Revisar permisos de archivos en servidor
- [ ] Configurar alertas de seguridad
- [ ] Documentar credenciales en gestor seguro (1Password, Bitwarden)

---

## Gestión de Usuarios Públicos

### Desde el Portal de Administración

1. Login como admin en `https://admin.tu-dominio.com`
2. Ir a **App 3: RMA & Tickets**
3. Click en pestaña **Usuarios Públicos**

**Acciones disponibles:**
- Ver lista completa de usuarios registrados
- Buscar por email, nombre o empresa
- Ver tickets de cada usuario
- Crear usuarios manualmente
- Bloquear/desbloquear usuarios
- Añadir notas administrativas

### Estados de Usuario

- **active**: Usuario activo, puede iniciar sesión
- **inactive**: Usuario inactivo, no puede iniciar sesión
- **blocked**: Usuario bloqueado por administrador

---

## Monitoreo y Mantenimiento

### Logs a Revisar

1. **Backend**: `/opt/ose-platform/logs/ose-platform.log`
2. **Nginx**: `/var/log/nginx/access.log` y `error.log`
3. **MongoDB**: `/var/log/mongodb/mongod.log`

### Métricas Importantes

- Usuarios públicos registrados
- Tickets creados por día
- Tasa de respuesta de soporte
- Tiempo medio de resolución
- Intentos de login fallidos

### Backups

**MongoDB:**

```bash
# Backup diario
mongodump --out /backup/$(date +%Y%m%d)

# Restore
mongorestore /backup/20250112
```

**Automatizar con cron:**

```bash
crontab -e

# Backup diario a las 2AM
0 2 * * * mongodump --out /backup/$(date +\%Y\%m\%d)

# Limpiar backups antiguos (mantener 30 días)
0 3 * * * find /backup -type d -mtime +30 -exec rm -rf {} +
```

---

## Troubleshooting

### Problema: CORS Error

**Síntoma:** Error en consola del navegador: "CORS policy blocked"

**Solución:**
1. Verificar que el dominio está en `CORS_ORIGINS` del backend
2. Reiniciar backend después de cambios
3. Verificar que el request incluye credenciales si es necesario

### Problema: Token Expirado

**Síntoma:** Usuario redirigido a login constantemente

**Solución:**
1. Usuarios públicos: tokens válidos 7 días
2. Verificar `ACCESS_TOKEN_EXPIRE_MINUTES` en config.py
3. Asegurar que fecha/hora del servidor es correcta

### Problema: No se Pueden Crear Tickets

**Síntoma:** Error 404 al buscar dispositivo por IMEI

**Solución:**
1. Verificar que el dispositivo existe en la BD
2. Importar dispositivos desde **App 2: Importación de Datos**
3. Verificar que el IMEI es correcto

---

## Contacto y Soporte

Para soporte técnico o consultas sobre el despliegue, contactar al equipo de desarrollo de OSE Platform.

---

## Licencia

Propiedad de OSE Platform - Todos los derechos reservados
