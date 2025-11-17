# 🎨 PLAN DE ACCIÓN - DESARROLLO DE FRONTENDS
**OSE Platform - Sistema de Gestión Integral**

**Fecha**: 12 de Noviembre, 2025
**Versión**: 1.0.0
**Responsable**: Equipo de Desarrollo

---

## 📋 ÍNDICE

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura Propuesta](#arquitectura-propuesta)
3. [Stack Tecnológico](#stack-tecnológico)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Plan de Desarrollo por Fases](#plan-de-desarrollo-por-fases)
6. [Aplicaciones Detalladas](#aplicaciones-detalladas)
7. [Componentes Compartidos](#componentes-compartidos)
8. [Integración con Backend](#integración-con-backend)
9. [Docker y Deployment](#docker-y-deployment)
10. [Timeline y Recursos](#timeline-y-recursos)

---

## 🎯 RESUMEN EJECUTIVO

### Objetivo
Desarrollar **6 aplicaciones frontend independientes** pero integradas, que consuman la API REST del backend de OSE Platform para gestionar producción, trazabilidad y post-venta de dispositivos IoT.

### Enfoque Arquitectónico
**Micro-Frontends Centralizados**
- Cada aplicación es independiente pero comparte componentes comunes
- Todas consumen la misma API REST
- Despliegue unificado con Docker Compose
- Portal único de acceso con routing centralizado

### Beneficios
✅ **Escalabilidad** - Cada app puede desarrollarse y desplegarse independientemente
✅ **Mantenibilidad** - Código modular y separado por funcionalidad
✅ **Reutilización** - Componentes compartidos entre aplicaciones
✅ **Flexibilidad** - Tecnologías específicas por app si es necesario
✅ **Despliegue Simple** - Un solo docker-compose para todo

---

## 🏗️ ARQUITECTURA PROPUESTA

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO FINAL                             │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PORTAL PRINCIPAL (App Shell)                   │
│                   http://localhost:3000                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • Autenticación centralizada (JWT)                       │  │
│  │  • Menú de navegación                                     │  │
│  │  • Gestión de sesión                                      │  │
│  │  • Enrutamiento a aplicaciones                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   APP 1      │    │   APP 2      │    │   APP 3      │
│ Notificación │    │ Importación  │    │ RMA/Tickets  │
│   Series     │    │    Datos     │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   APP 4      │    │   APP 5      │    │   APP 6      │
│   Import     │    │   Factura    │    │   Picking    │
│  Transform   │    │   Ticket     │    │   Palets     │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SHARED COMPONENTS LIBRARY                       │
│  • API Service (Axios)                                           │
│  • Auth Service (JWT interceptors)                              │
│  • UI Components (Buttons, Forms, Tables)                       │
│  • Layout Components (Sidebar, Header, Footer)                  │
│  • Utils (formatters, validators)                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BACKEND API (FastAPI)                           │
│                  http://localhost:8001/api/v1                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     MongoDB Database                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💻 STACK TECNOLÓGICO

### Frontend Framework
**Vue 3** (Composition API) - Elegido por:
- ✅ Curva de aprendizaje suave
- ✅ Excelente documentación en español
- ✅ Ecosystem maduro (Vuetify, Pinia, Vue Router)
- ✅ Performance superior
- ✅ TypeScript support

### UI Framework
**Vuetify 3** - Material Design:
- ✅ 100+ componentes pre-hechos
- ✅ Responsive automático
- ✅ Tema personalizable
- ✅ Iconos Material Design
- ✅ Layouts grid flexibles

### Gestión de Estado
**Pinia** - State management:
- ✅ Simple y moderno
- ✅ TypeScript nativo
- ✅ DevTools integration
- ✅ Module splitting

### HTTP Client
**Axios** - HTTP requests:
- ✅ Interceptors para JWT
- ✅ Request/Response transformers
- ✅ Error handling centralizado
- ✅ Cancel tokens

### Build Tool
**Vite** - Next generation tooling:
- ✅ Hot Module Replacement ultra-rápido
- ✅ Build optimizado
- ✅ Native ES modules
- ✅ TypeScript support

### Routing
**Vue Router 4**:
- ✅ Lazy loading de rutas
- ✅ Guards de autenticación
- ✅ Nested routes

### Gráficos y Visualización
**Chart.js + vue-chartjs**:
- ✅ Múltiples tipos de gráficos
- ✅ Responsive
- ✅ Animaciones

### Manejo de Archivos
**xlsx** para Excel:
- ✅ Leer/escribir Excel
- ✅ CSV support
- ✅ Data transformation

### Date/Time
**date-fns**:
- ✅ Ligera (vs moment.js)
- ✅ Modular
- ✅ Inmutable

---

## 📁 ESTRUCTURA DEL PROYECTO

```
OSE-Platform/
├── backend/                          # ✅ YA COMPLETADO
│   └── ...
│
├── frontend/                         # 🔴 A DESARROLLAR
│   │
│   ├── shared/                       # 📦 Librería compartida
│   │   ├── src/
│   │   │   ├── components/          # Componentes UI reutilizables
│   │   │   │   ├── common/
│   │   │   │   │   ├── AppButton.vue
│   │   │   │   │   ├── AppTable.vue
│   │   │   │   │   ├── AppDialog.vue
│   │   │   │   │   ├── AppSnackbar.vue
│   │   │   │   │   └── AppCard.vue
│   │   │   │   │
│   │   │   │   ├── forms/
│   │   │   │   │   ├── TextInput.vue
│   │   │   │   │   ├── SelectInput.vue
│   │   │   │   │   ├── DatePicker.vue
│   │   │   │   │   └── FileUpload.vue
│   │   │   │   │
│   │   │   │   └── layout/
│   │   │   │       ├── AppHeader.vue
│   │   │   │       ├── AppSidebar.vue
│   │   │   │       ├── AppFooter.vue
│   │   │   │       └── MainLayout.vue
│   │   │   │
│   │   │   ├── services/            # Servicios API
│   │   │   │   ├── api.service.js       # Axios instance
│   │   │   │   ├── auth.service.js      # Autenticación
│   │   │   │   ├── device.service.js    # CRUD dispositivos
│   │   │   │   ├── employee.service.js  # CRUD empleados
│   │   │   │   └── settings.service.js  # Configuración
│   │   │   │
│   │   │   ├── stores/              # Pinia stores
│   │   │   │   ├── auth.store.js        # Estado autenticación
│   │   │   │   ├── user.store.js        # Usuario actual
│   │   │   │   └── app.store.js         # Estado global app
│   │   │   │
│   │   │   ├── utils/               # Utilidades
│   │   │   │   ├── validators.js        # Validaciones
│   │   │   │   ├── formatters.js        # Formateo datos
│   │   │   │   ├── constants.js         # Constantes
│   │   │   │   └── helpers.js           # Helpers
│   │   │   │
│   │   │   ├── composables/         # Vue composables
│   │   │   │   ├── useAuth.js
│   │   │   │   ├── useApi.js
│   │   │   │   └── useNotification.js
│   │   │   │
│   │   │   └── plugins/             # Vue plugins
│   │   │       ├── vuetify.js
│   │   │       ├── router.js
│   │   │       └── pinia.js
│   │   │
│   │   ├── package.json
│   │   └── README.md
│   │
│   ├── portal/                       # 🏠 Portal principal (App Shell)
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── assets/
│   │   │   ├── components/
│   │   │   │   ├── AppMenu.vue
│   │   │   │   ├── UserProfile.vue
│   │   │   │   └── AppSelector.vue
│   │   │   ├── views/
│   │   │   │   ├── Login.vue
│   │   │   │   ├── Dashboard.vue
│   │   │   │   └── Home.vue
│   │   │   ├── router/
│   │   │   │   └── index.js
│   │   │   ├── App.vue
│   │   │   └── main.js
│   │   ├── Dockerfile
│   │   ├── package.json
│   │   ├── vite.config.js
│   │   └── nginx.conf
│   │
│   ├── app1-notificacion/            # 📱 App 1
│   │   ├── public/
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── SeriesForm.vue
│   │   │   │   ├── SeriesTable.vue
│   │   │   │   └── EmailPreview.vue
│   │   │   ├── views/
│   │   │   │   ├── NotificationList.vue
│   │   │   │   └── NotificationCreate.vue
│   │   │   ├── router/
│   │   │   ├── App.vue
│   │   │   └── main.js
│   │   ├── Dockerfile
│   │   └── package.json
│   │
│   ├── app2-importacion/             # 📊 App 2
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── FileUploader.vue
│   │   │   │   ├── DataPreview.vue
│   │   │   │   └── ValidationResults.vue
│   │   │   ├── views/
│   │   │   │   ├── ImportWizard.vue
│   │   │   │   └── ImportHistory.vue
│   │   │   └── ...
│   │   └── ...
│   │
│   ├── app3-rma-tickets/             # 🎫 App 3
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── TicketCard.vue
│   │   │   │   ├── RMAForm.vue
│   │   │   │   └── TicketTimeline.vue
│   │   │   ├── views/
│   │   │   │   ├── TicketList.vue
│   │   │   │   ├── TicketDetail.vue
│   │   │   │   └── RMAManagement.vue
│   │   │   └── ...
│   │   └── ...
│   │
│   ├── app4-transform/               # 🔄 App 4
│   │   └── ...
│   │
│   ├── app5-factura/                 # 💰 App 5
│   │   └── ...
│   │
│   ├── app6-picking/                 # 📦 App 6
│   │   └── ...
│   │
│   └── docker-compose.frontend.yml   # Docker compose frontends
│
└── docker-compose.yml                # Docker compose completo
```

---

## 🚀 PLAN DE DESARROLLO POR FASES

### **FASE 0: Setup Inicial** (1 día)
**Objetivo**: Preparar infraestructura base

#### Tareas:
1. ✅ Crear estructura de carpetas
2. ✅ Inicializar proyecto `shared` library
3. ✅ Configurar Vite, Vue 3, Vuetify
4. ✅ Configurar linters (ESLint, Prettier)
5. ✅ Setup TypeScript (opcional)
6. ✅ Crear plantilla base de aplicación

#### Entregables:
- `frontend/shared/` con componentes base
- Configuración Vuetify
- API service con Axios configurado
- Auth store con Pinia

---

### **FASE 1: Portal Principal** (2-3 días)
**Objetivo**: App shell con autenticación

#### Tareas:
1. ✅ Login page con validación
2. ✅ Layout principal (sidebar, header, footer)
3. ✅ Dashboard home
4. ✅ Menú de navegación a apps
5. ✅ Integración JWT con backend
6. ✅ Guards de autenticación
7. ✅ Gestión de sesión (refresh token)
8. ✅ Profile page

#### Componentes Clave:
- `Login.vue` - Formulario de login
- `MainLayout.vue` - Layout principal
- `AppMenu.vue` - Menú lateral con apps
- `Dashboard.vue` - Dashboard principal
- `UserProfile.vue` - Perfil de usuario

#### API Endpoints Usados:
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`

---

### **FASE 2: App 1 - Notificación de Series** (3-4 días)
**Objetivo**: Notificar series de dispositivos nuevos

#### Funcionalidad:
- Formulario para ingresar serie de dispositivos (IMEI/CCID)
- Selección de clientes/distribuidores
- Preview de email de notificación
- Envío masivo de notificaciones
- Historial de notificaciones enviadas

#### Pantallas:
1. **Lista de Notificaciones** (`/app1/notifications`)
   - Tabla con notificaciones enviadas
   - Filtros: fecha, cliente, estado
   - Búsqueda

2. **Nueva Notificación** (`/app1/notifications/new`)
   - Input de series (IMEI/CCID)
   - Selector de clientes
   - Plantilla de email editable
   - Preview en tiempo real
   - Botón enviar

3. **Detalle de Notificación** (`/app1/notifications/:id`)
   - Info de la notificación
   - Dispositivos incluidos
   - Estado de envío por destinatario
   - Reenviar si falló

#### Componentes:
- `NotificationList.vue`
- `NotificationForm.vue`
- `SeriesInput.vue` (textarea múltiple IMEI)
- `ClientSelector.vue`
- `EmailPreview.vue`
- `NotificationDetail.vue`

#### API Endpoints:
- `GET /api/v1/devices?imei__in=...`
- `GET /api/v1/customers`
- `POST /api/v1/notifications` (crear)
- `GET /api/v1/notifications` (listar)

---

### **FASE 3: App 2 - Importación de Datos** (4-5 días)
**Objetivo**: Importar datos masivos desde Excel/CSV

#### Funcionalidad:
- Upload de archivos Excel/CSV
- Preview de datos antes de importar
- Validación de datos (IMEI únicos, campos requeridos)
- Mapeo de columnas
- Importación en background
- Reporte de errores/warnings
- Historial de importaciones

#### Pantallas:
1. **Wizard de Importación** (`/app2/import`)
   - Paso 1: Upload archivo
   - Paso 2: Mapeo de columnas
   - Paso 3: Preview y validación
   - Paso 4: Confirmación e importación
   - Paso 5: Resultados

2. **Historial** (`/app2/history`)
   - Lista de importaciones previas
   - Detalle de cada importación
   - Descargar reporte de errores

#### Componentes:
- `FileUploader.vue` (drag & drop)
- `ColumnMapper.vue` (mapeo visual)
- `DataPreview.vue` (tabla preview)
- `ValidationResults.vue` (lista errores)
- `ImportProgress.vue` (progress bar)
- `ImportHistory.vue`

#### API Endpoints:
- `POST /api/v1/devices/bulk` (crear múltiples)
- `POST /api/v1/devices/validate` (validar datos)
- `GET /api/v1/imports` (historial)

---

### **FASE 4: App 3 - RMA & Tickets** (5-6 días)
**Objetivo**: Gestión de post-venta

#### Funcionalidad:
- Crear tickets de soporte
- Asignar tickets a técnicos
- Seguimiento de estado
- Crear casos RMA
- Inspección de dispositivos
- Reemplazos y reembolsos
- Timeline de eventos
- Comentarios y notas

#### Pantallas:
1. **Dashboard Tickets** (`/app3/dashboard`)
   - Métricas: abiertos, cerrados, pendientes
   - Gráficos de tendencias
   - Tickets por prioridad

2. **Lista Tickets** (`/app3/tickets`)
   - Tabla con filtros avanzados
   - Búsqueda por IMEI, cliente, número
   - Estados: abierto, en progreso, cerrado

3. **Detalle Ticket** (`/app3/tickets/:id`)
   - Info completa del ticket
   - Timeline de eventos
   - Comentarios
   - Archivos adjuntos
   - Acciones rápidas

4. **Nuevo Ticket** (`/app3/tickets/new`)
   - Formulario completo
   - Búsqueda de dispositivo
   - Categorización automática

5. **RMA Management** (`/app3/rma`)
   - Lista de casos RMA
   - Crear nuevo RMA
   - Inspección
   - Aprobación/rechazo

#### Componentes:
- `TicketCard.vue`
- `TicketForm.vue`
- `TicketTimeline.vue`
- `TicketComments.vue`
- `RMAForm.vue`
- `InspectionForm.vue`
- `TicketStats.vue`

#### API Endpoints:
- `GET /api/v1/tickets`
- `POST /api/v1/tickets`
- `PATCH /api/v1/tickets/:id`
- `GET /api/v1/rma-cases`
- `POST /api/v1/rma-cases`

---

### **FASE 5: Apps 4, 5, 6** (6-8 días)
**Objetivo**: Completar aplicaciones restantes

#### App 4: Import Transform
- Transformación de datos importados
- Reglas de negocio configurables
- Validaciones personalizadas

#### App 5: Factura Ticket
- Generar facturas desde tickets
- Templates PDF
- Envío por email

#### App 6: Picking Palets
- Gestión de picking de almacén
- Escaneo de códigos
- Paletización
- Etiquetas de envío

---

### **FASE 6: Integración y Testing** (3-4 días)
**Objetivo**: Integrar todo y probar

#### Tareas:
1. ✅ Docker Compose para todos los frontends
2. ✅ Nginx como reverse proxy
3. ✅ Testing E2E con Cypress
4. ✅ Testing unitario con Vitest
5. ✅ Performance optimization
6. ✅ Mobile responsiveness
7. ✅ Accessibility (a11y)
8. ✅ Browser compatibility

---

## 📦 COMPONENTES COMPARTIDOS (Shared Library)

### API Service (`shared/src/services/api.service.js`)
```javascript
import axios from 'axios';
import { useAuthStore } from '@/stores/auth.store';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor - Add JWT token
apiClient.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Handle 401, refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const authStore = useAuthStore();
      const refreshed = await authStore.refreshToken();

      if (refreshed) {
        return apiClient(originalRequest);
      } else {
        authStore.logout();
        router.push('/login');
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;
```

### Auth Store (`shared/src/stores/auth.store.js`)
```javascript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import apiClient from '@/services/api.service';

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token'));
  const refreshToken = ref(localStorage.getItem('refreshToken'));
  const user = ref(null);

  const isAuthenticated = computed(() => !!token.value);

  async function login(credentials) {
    const response = await apiClient.post('/auth/login', credentials);
    const { access_token, refresh_token, user: userData } = response.data;

    token.value = access_token;
    refreshToken.value = refresh_token;
    user.value = userData;

    localStorage.setItem('token', access_token);
    localStorage.setItem('refreshToken', refresh_token);

    return true;
  }

  async function logout() {
    await apiClient.post('/auth/logout');

    token.value = null;
    refreshToken.value = null;
    user.value = null;

    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
  }

  async function refreshTokenFn() {
    try {
      const response = await apiClient.post('/auth/refresh', {
        refresh_token: refreshToken.value
      });

      token.value = response.data.access_token;
      localStorage.setItem('token', response.data.access_token);

      return true;
    } catch (error) {
      return false;
    }
  }

  async function fetchUser() {
    const response = await apiClient.get('/auth/me');
    user.value = response.data;
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout,
    refreshToken: refreshTokenFn,
    fetchUser
  };
});
```

---

## 🔗 INTEGRACIÓN CON BACKEND

### Autenticación JWT
```javascript
// 1. Login
POST /api/v1/auth/login
Body: { email, password }
Response: { access_token, refresh_token, user }

// 2. Todas las requests incluyen header:
Authorization: Bearer <access_token>

// 3. Si token expira (30 min):
POST /api/v1/auth/refresh
Body: { refresh_token }
Response: { access_token }

// 4. Logout
POST /api/v1/auth/logout
```

### CRUD Endpoints Pattern
```javascript
// Dispositivos
GET    /api/v1/devices              // Listar
GET    /api/v1/devices/:id          // Obtener uno
GET    /api/v1/devices/imei/:imei   // Por IMEI
POST   /api/v1/devices              // Crear
PUT    /api/v1/devices/:id          // Actualizar completo
PATCH  /api/v1/devices/:id          // Actualizar parcial
DELETE /api/v1/devices/:id          // Eliminar
```

### Error Handling
```javascript
// Backend responde con:
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "status_code": 400
}

// Frontend maneja:
try {
  const response = await deviceService.create(data);
} catch (error) {
  if (error.response) {
    // Error del backend
    showError(error.response.data.detail);
  } else if (error.request) {
    // No hubo respuesta
    showError('No se pudo conectar al servidor');
  } else {
    // Error en la request
    showError('Error inesperado');
  }
}
```

---

## 🐳 DOCKER Y DEPLOYMENT

### Docker Compose para Frontends
```yaml
# docker-compose.frontend.yml
version: '3.8'

services:
  # Portal principal (nginx)
  portal:
    build:
      context: ./frontend/portal
      dockerfile: Dockerfile
    container_name: ose_portal
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=http://localhost:8001/api/v1
    networks:
      - ose_network

  # App 1 - Notificación
  app1-notificacion:
    build: ./frontend/app1-notificacion
    container_name: ose_app1
    ports:
      - "3001:80"
    environment:
      - VITE_API_URL=http://localhost:8001/api/v1
    networks:
      - ose_network

  # App 2 - Importación
  app2-importacion:
    build: ./frontend/app2-importacion
    container_name: ose_app2
    ports:
      - "3002:80"
    environment:
      - VITE_API_URL=http://localhost:8001/api/v1
    networks:
      - ose_network

  # App 3 - RMA/Tickets
  app3-rma:
    build: ./frontend/app3-rma-tickets
    container_name: ose_app3
    ports:
      - "3003:80"
    environment:
      - VITE_API_URL=http://localhost:8001/api/v1
    networks:
      - ose_network

  # App 4 - Transform
  app4-transform:
    build: ./frontend/app4-transform
    container_name: ose_app4
    ports:
      - "3004:80"
    networks:
      - ose_network

  # App 5 - Factura
  app5-factura:
    build: ./frontend/app5-factura
    container_name: ose_app5
    ports:
      - "3005:80"
    networks:
      - ose_network

  # App 6 - Picking
  app6-picking:
    build: ./frontend/app6-picking
    container_name: ose_app6
    ports:
      - "3006:80"
    networks:
      - ose_network

networks:
  ose_network:
    external: true
```

### Dockerfile Template
```dockerfile
# Multi-stage build para optimizar tamaño
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar package files
COPY package*.json ./
RUN npm ci

# Copiar código
COPY . .

# Build production
RUN npm run build

# Stage 2 - Nginx
FROM nginx:alpine

# Copiar build
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Config
```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/css application/javascript application/json;

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 📊 TIMELINE Y RECURSOS

### Timeline Estimado

| Fase | Duración | Acumulado |
|------|----------|-----------|
| Fase 0: Setup | 1 día | 1 día |
| Fase 1: Portal | 3 días | 4 días |
| Fase 2: App 1 | 4 días | 8 días |
| Fase 3: App 2 | 5 días | 13 días |
| Fase 4: App 3 | 6 días | 19 días |
| Fase 5: Apps 4-6 | 8 días | 27 días |
| Fase 6: Testing | 4 días | 31 días |

**Total: ~6 semanas (31 días hábiles)**

### Recursos Necesarios

#### Humanos:
- **1 Frontend Lead** - Arquitectura y shared components
- **2-3 Frontend Developers** - Desarrollo de apps
- **1 UX/UI Designer** - Diseño de interfaces
- **1 QA Tester** - Testing y validación

#### Herramientas:
- **Figma** - Diseño UI/UX
- **VS Code** - IDE
- **Vue DevTools** - Debugging
- **Postman** - Testing API
- **Cypress** - E2E testing
- **Git** - Control de versiones

### Priorización

**Alta Prioridad** (MVP):
1. ✅ Portal Principal (login + dashboard)
2. ✅ App 1: Notificación de Series
3. ✅ App 2: Importación de Datos
4. ✅ App 3: RMA & Tickets

**Media Prioridad**:
5. ⚠️ App 4: Import Transform
6. ⚠️ App 5: Factura Ticket

**Baja Prioridad**:
7. 🔵 App 6: Picking Palets

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

### Hoy (12 Nov 2025)
1. ✅ Revisar y aprobar este plan
2. ⬜ Crear estructura de carpetas base
3. ⬜ Inicializar proyecto `shared`
4. ⬜ Setup Vite + Vue 3 + Vuetify

### Mañana (13 Nov 2025)
1. ⬜ Desarrollar componentes shared básicos
2. ⬜ Configurar API service con Axios
3. ⬜ Crear auth store con Pinia
4. ⬜ Iniciar desarrollo del Portal

### Esta Semana
1. ⬜ Completar Portal Principal
2. ⬜ Iniciar App 1 (Notificación)
3. ⬜ Configurar Docker Compose

---

## 📝 NOTAS ADICIONALES

### Consideraciones de UX/UI
- **Mobile First**: Diseñar primero para móvil
- **Accesibilidad**: WCAG 2.1 Level AA
- **Dark Mode**: Opcional pero recomendado
- **Shortcuts**: Atajos de teclado para power users
- **Loading States**: Skeletons, spinners, progress bars
- **Error States**: Mensajes claros y accionables
- **Empty States**: Guiar al usuario qué hacer

### Performance
- **Lazy Loading**: Cargar rutas bajo demanda
- **Code Splitting**: Dividir bundles por app
- **Image Optimization**: WebP, lazy images
- **Virtual Scrolling**: Para tablas grandes
- **Debounce**: En búsquedas y filtros
- **Caching**: LocalStorage para datos estáticos

### Seguridad
- **XSS Protection**: Sanitizar inputs
- **CSRF**: Tokens en forms
- **JWT Expiration**: Renovar automáticamente
- **Sensitive Data**: No logs en producción
- **HTTPS**: Forzar en producción

---

## ✅ CHECKLIST DE INICIO

Antes de empezar el desarrollo:

### Ambiente de Desarrollo
- [ ] Node.js 18+ instalado
- [ ] npm o yarn configurado
- [ ] Git configurado
- [ ] VS Code con extensiones Vue
- [ ] Docker Desktop corriendo
- [ ] Backend corriendo en http://localhost:8001

### Accesos
- [ ] API docs accesible: http://localhost:8001/docs
- [ ] Health check OK: http://localhost:8001/api/v1/health
- [ ] MongoDB accesible
- [ ] Credenciales de prueba creadas

### Documentación
- [ ] Revisar ESTADO_PROYECTO.md
- [ ] Revisar API endpoints en /docs
- [ ] Tener README.md a mano
- [ ] Plan de diseño UI/UX aprobado

---

**¡Listos para empezar el desarrollo! 🚀**

*Plan generado por: Equipo de Desarrollo OSE Platform*
*Última actualización: 2025-11-12 01:30 AM*
