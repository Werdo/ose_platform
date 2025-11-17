# OSE Platform - Portal Público RMA/Tickets

Portal público para clientes externos que les permite registrarse, crear tickets de soporte y comunicarse con el equipo de soporte de OSE.

## Características

- ✅ Registro e inicio de sesión de usuarios externos
- ✅ Creación de tickets de soporte basados en IMEI
- ✅ Sistema de chat integrado para comunicación con soporte
- ✅ Seguimiento del estado de tickets en tiempo real
- ✅ Interfaz responsive con Bootstrap 5
- ✅ Seguridad con JWT tokens

## Tecnologías

- React 18 + TypeScript
- Vite (Build tool)
- React Bootstrap 5
- React Router DOM
- Axios (HTTP client)

## Instalación

```bash
# Instalar dependencias
npm install

# Copiar archivo de configuración
cp .env.example .env

# Editar .env con la URL del backend
nano .env
```

## Desarrollo

```bash
# Ejecutar en modo desarrollo (puerto 3003)
npm run dev
```

El portal estará disponible en http://localhost:3003

## Producción

### Build

```bash
# Generar build de producción
npm run build
```

Los archivos se generarán en la carpeta `dist/`

### Despliegue en Cloud

#### Opción 1: Vercel

```bash
# Instalar Vercel CLI
npm install -g vercel

# Desplegar
vercel --prod
```

**Variables de entorno en Vercel:**
- `VITE_API_URL`: URL de tu backend en producción

#### Opción 2: Netlify

```bash
# Instalar Netlify CLI
npm install -g netlify-cli

# Desplegar
netlify deploy --prod
```

**Variables de entorno en Netlify:**
- `VITE_API_URL`: URL de tu backend en producción

#### Opción 3: Docker

Crear `Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Crear `nginx.conf`:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

Build y deploy:

```bash
docker build -t ose-public-portal .
docker run -p 8080:80 ose-public-portal
```

#### Opción 4: AWS S3 + CloudFront

```bash
# Build
npm run build

# Subir a S3 bucket
aws s3 sync dist/ s3://your-bucket-name --delete

# Invalidar CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*"
```

## Configuración del Backend

### CORS Configuration

Asegúrate de que el backend permita peticiones desde el dominio del portal público:

```python
# backend-new/app/config.py
CORS_ORIGINS = [
    "http://localhost:3003",
    "https://portal.tu-dominio.com",  # Tu dominio en producción
]
```

### Seguridad

El portal público usa tokens JWT separados de los tokens de empleados. Los endpoints públicos están bajo `/api/v1/public/*`

## Gestión desde Admin

Los administradores pueden gestionar usuarios del portal público desde el panel de administración (App3 > Usuarios Públicos):

- Ver todos los usuarios registrados
- Crear usuarios manualmente
- Bloquear/desbloquear usuarios
- Ver tickets de cada usuario
- Gestionar tickets y responder mensajes

## Flujo de Uso

### Para Usuarios Externos:

1. **Registro**: Ir a `/register` y crear cuenta con email y contraseña
2. **Login**: Iniciar sesión en `/login`
3. **Dashboard**: Ver todos sus tickets
4. **Crear Ticket**: Ingresar IMEI del dispositivo y descripción del problema
5. **Chat**: Comunicarse con soporte a través de mensajes en el ticket
6. **Seguimiento**: Ver estado y prioridad del ticket en tiempo real

### Para Administradores:

1. Login en portal de gestión (puerto 3002)
2. App 3 > RMA & Tickets
3. Gestionar tickets de usuarios públicos
4. Responder a mensajes
5. Cambiar estado y prioridad
6. Gestionar usuarios públicos

## Seguridad Recomendada

### Para Producción:

1. **HTTPS obligatorio**: Configurar certificado SSL
2. **Rate Limiting**: Implementar en el backend
3. **Validación de emails**: Implementar verificación por email (código ya preparado)
4. **Contraseñas fuertes**: Mínimo 8 caracteres (ya implementado)
5. **Tokens con expiración**: 7 días (ya configurado)
6. **CORS restrictivo**: Solo dominios autorizados
7. **Firewall**: Restringir acceso al backend solo desde IPs autorizadas

## Soporte

Para soporte o preguntas, contactar al equipo de desarrollo de OSE Platform.

## Licencia

Propiedad de OSE Platform - Todos los derechos reservados
