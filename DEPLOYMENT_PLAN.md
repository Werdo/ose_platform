# 🚀 PLAN DE DESPLIEGUE - OSE Platform

## 📋 Resumen

Desplegar **OSE Platform** en el servidor de producción junto con AssetFlow:

- **Servidor**: 167.235.58.24
- **Dominio**: platform.oversunenergy.com
- **Usuario SSH**: admin
- **Password**: bb474edf
- **Directorio**: `/var/www/ose-platform/`

---

## 🎯 Arquitectura Final

```
Servidor 167.235.58.24
│
├── AssetFlow (ya existente)
│   ├── Frontend: http://167.235.58.24:3000
│   ├── Backend: http://167.235.58.24:5000
│   ├── MongoDB: 27017
│   └── Dominio: https://assetflow.oversunenergy.com
│
└── OSE Platform (nuevo)
    ├── Frontend: http://167.235.58.24:3001
    ├── Backend: http://167.235.58.24:8001
    ├── MongoDB: 27018 (o compartir con AssetFlow)
    └── Dominio: https://platform.oversunenergy.com
```

---

## 📦 Componentes a Desplegar

### 1. **Backend (FastAPI + Python)**
- Puerto: 8001
- MongoDB: Puerto 27018 (o compartir 27017)
- Variables de entorno en `.env.production`

### 2. **Frontend (React + Vite)**
- Puerto: 3001
- Build estático servido por Nginx
- Configurado para producción

### 3. **MongoDB**
- Opción A: Nueva instancia en puerto 27018
- Opción B: Compartir MongoDB de AssetFlow (puerto 27017)

### 4. **Nginx**
- Reverse proxy para ambos dominios
- SSL con Certbot

---

## 🔧 Pasos de Despliegue

### **Paso 1: Preparar Archivos Localmente**

#### 1.1. Crear `Dockerfile` para Backend

```dockerfile
# backend-new/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8001

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### 1.2. Crear `Dockerfile` para Frontend

```dockerfile
# frontend-react/portal/Dockerfile
FROM node:20-alpine as build

WORKDIR /app

# Copiar package files
COPY package*.json ./
RUN npm install

# Copiar código y build
COPY . .
RUN npm run build

# Stage 2: Nginx
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

#### 1.3. Crear `docker-compose.yml`

```yaml
version: '3.8'

services:
  # MongoDB (nueva instancia para OSE Platform)
  mongodb:
    image: mongo:6.0
    container_name: ose-mongodb
    restart: always
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_ROOT_USERNAME}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_ROOT_PASSWORD}
      MONGO_INITDB_DATABASE: ${MONGODB_DB_NAME}
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27018:27017"
    networks:
      - ose-network

  # Backend (FastAPI)
  backend:
    build:
      context: ./backend-new
      dockerfile: Dockerfile
    container_name: ose-backend
    restart: always
    env_file:
      - .env.production
    ports:
      - "8001:8001"
    depends_on:
      - mongodb
    networks:
      - ose-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend (React)
  frontend:
    build:
      context: ./frontend-react/portal
      dockerfile: Dockerfile
    container_name: ose-frontend
    restart: always
    ports:
      - "3001:80"
    depends_on:
      - backend
    networks:
      - ose-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  ose-network:
    driver: bridge

volumes:
  mongodb_data:
```

#### 1.4. Crear `.env.production`

```bash
# MongoDB
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=oseplatform2025secure
MONGODB_URI=mongodb://admin:oseplatform2025secure@mongodb:27017/ose_platform?authSource=admin
MONGODB_DB_NAME=ose_platform

# Backend
HOST=0.0.0.0
PORT=8001
APP_NAME=OSE Platform API
APP_VERSION=2.0.0
ENVIRONMENT=production

# JWT
JWT_SECRET=your-secure-jwt-secret-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080

# CORS
CORS_ORIGINS=["https://platform.oversunenergy.com","https://assetflow.oversunenergy.com"]

# Frontend URL
FRONTEND_URL=https://platform.oversunenergy.com

# Features
FEATURE_APP1_ENABLED=true
FEATURE_APP2_ENABLED=true
FEATURE_APP3_ENABLED=true
FEATURE_APP4_ENABLED=true
FEATURE_APP5_ENABLED=true
FEATURE_APP6_ENABLED=true
FEATURE_APP8_ENABLED=true
```

### **Paso 2: Configurar Nginx en el Servidor**

#### 2.1. Crear configuración para `platform.oversunenergy.com`

```nginx
# /etc/nginx/sites-available/platform.oversunenergy.com

server {
    listen 80;
    server_name platform.oversunenergy.com;

    # Frontend (React)
    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 2.2. Habilitar sitio y SSL

```bash
# En el servidor
sudo ln -s /etc/nginx/sites-available/platform.oversunenergy.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Obtener SSL con Certbot
sudo certbot --nginx -d platform.oversunenergy.com
```

### **Paso 3: Desplegar al Servidor**

#### 3.1. Conectar al servidor

```bash
ssh admin@167.235.58.24
```

#### 3.2. Crear directorio

```bash
sudo mkdir -p /var/www/ose-platform
sudo chown -R admin:admin /var/www/ose-platform
cd /var/www/ose-platform
```

#### 3.3. Inicializar Git

```bash
git init
git remote add origin <URL_DEL_REPO_GIT>
```

#### 3.4. Subir código desde local

```bash
# Desde Windows (tu máquina local)
cd C:\Users\pedro\claude-code-workspace\OSE-Platform

# Crear .gitignore si no existe
echo "node_modules/" > .gitignore
echo "__pycache__/" >> .gitignore
echo ".env" >> .gitignore
echo "*.pyc" >> .gitignore

# Commit y push (necesitarás crear un repo en GitHub primero)
git add .
git commit -m "Initial deployment"
git push origin main
```

#### 3.5. En el servidor, pull del código

```bash
cd /var/www/ose-platform
git pull origin main
```

#### 3.6. Crear archivo .env.production

```bash
nano .env.production
# Copiar el contenido del paso 1.4
```

#### 3.7. Levantar servicios con Docker

```bash
sudo docker-compose -f docker-compose.yml up -d --build
```

#### 3.8. Verificar servicios

```bash
sudo docker-compose ps
sudo docker logs ose-backend
sudo docker logs ose-frontend
```

---

## ✅ Verificación

### 1. **Verificar Backend**
```bash
curl http://localhost:8001/
curl http://localhost:8001/api/v1/health
```

### 2. **Verificar Frontend**
```bash
curl http://localhost:3001/
```

### 3. **Verificar Nginx**
```bash
curl http://platform.oversunenergy.com
curl https://platform.oversunenergy.com
```

### 4. **Verificar MongoDB**
```bash
sudo docker exec -it ose-mongodb mongosh -u admin -p oseplatform2025secure
```

---

## 🔐 DNS Configuration

Configurar en tu proveedor de DNS (DonDominio, Cloudflare, etc.):

```
Type: A
Name: platform
Value: 167.235.58.24
TTL: 3600
```

---

## 📊 Monitoreo

### Logs del Backend
```bash
sudo docker logs -f ose-backend
```

### Logs del Frontend
```bash
sudo docker logs -f ose-frontend
```

### Logs de MongoDB
```bash
sudo docker logs -f ose-mongodb
```

---

## 🛠️ Comandos Útiles

### Reiniciar servicios
```bash
cd /var/www/ose-platform
sudo docker-compose restart
```

### Rebuild sin caché
```bash
sudo docker-compose build --no-cache
sudo docker-compose up -d
```

### Ver recursos
```bash
sudo docker stats --no-stream
```

### Backup de MongoDB
```bash
sudo docker exec ose-mongodb mongodump --out /backup --username admin --password oseplatform2025secure --authenticationDatabase admin
```

---

## 📝 Notas Importantes

1. **MongoDB**: Se puede compartir con AssetFlow o usar instancia separada
2. **Puertos**: Frontend 3001, Backend 8001, MongoDB 27018
3. **SSL**: Certbot configurará automáticamente HTTPS
4. **Firewall**: Asegurar que puertos 80 y 443 estén abiertos

---

## 🚦 Próximos Pasos

Después del despliegue básico:

1. ✅ Verificar que todo funciona
2. Configurar backups automáticos
3. Implementar frontend de gestión de usuarios
4. Integrar AssetFlow como App 7
5. Crear panel de dashboard unificado

---

## ⚠️ Troubleshooting

### Backend no inicia
```bash
sudo docker logs ose-backend
# Verificar .env.production
# Verificar conexión MongoDB
```

### Frontend muestra página en blanco
```bash
# Verificar que API_URL esté correcto en el build
# Revisar logs del navegador (F12)
```

### MongoDB no conecta
```bash
sudo docker exec -it ose-mongodb mongosh
# Verificar credenciales en .env.production
```
