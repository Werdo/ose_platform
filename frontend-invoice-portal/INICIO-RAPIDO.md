# Inicio Rápido - Portal de Facturación

## Instalación y Ejecución

### 1. Las dependencias ya están instaladas

El proyecto ya tiene todas las dependencias instaladas. Si necesitas reinstalarlas:

```bash
npm install
```

### 2. Ejecutar el proyecto

```bash
npm run dev
# O alternativamente
npm start
```

El servidor se iniciará en: **http://localhost:5005**

### 3. Asegúrate de que el backend esté corriendo

El frontend necesita comunicarse con el backend de App5 (Invoice Service) en:
- **URL**: http://localhost:8001

## Arquitectura del Proyecto

### Páginas Principales

1. **HomePage** (`/`)
   - Formulario de email para acceso
   - Botones para ver tickets o subir nuevo

2. **UploadTicketPage** (`/upload-ticket?email=...`)
   - Drag & drop de imágenes
   - Escaneo OCR automático
   - Formulario editable de ticket
   - Formulario de facturación

3. **MyTicketsPage** (`/my-tickets?email=...`)
   - Lista de tickets del usuario
   - Selección múltiple
   - Botón para generar factura

4. **GenerateInvoicePage** (`/generate-invoice?email=...&tickets=1,2,3`)
   - Preview de factura
   - Confirmación de datos
   - Descarga de PDF

### Componentes Reutilizables

- **TicketUpload**: Componente de drag & drop con preview de imagen
- **TicketForm**: Formulario para datos del ticket (número, fecha, productos)
- **BillingForm**: Formulario para datos de facturación (nombre, NIF, dirección)
- **TicketList**: Tabla de tickets con selección múltiple
- **InvoicePreview**: Vista previa de la factura antes de generar

### Servicio de API

Todas las llamadas HTTP están centralizadas en `src/services/api.ts`:

- Configuración de Axios
- Interfaces TypeScript
- Métodos para todos los endpoints
- Manejo de errores

## Flujo de Datos

```
1. Usuario ingresa email en HomePage
   ↓
2. Puede ir a:
   a) MyTicketsPage → Ver tickets existentes
   b) UploadTicketPage → Subir nuevo ticket
   ↓
3. En UploadTicketPage:
   - Sube imagen
   - OCR extrae datos automáticamente
   - Usuario edita/completa datos
   - Guarda ticket
   ↓
4. En MyTicketsPage:
   - Ve todos sus tickets
   - Selecciona tickets pendientes
   - Click en "Generar Factura"
   ↓
5. En GenerateInvoicePage:
   - Revisa datos
   - Confirma información de facturación
   - Genera y descarga PDF
```

## Tecnologías Usadas

- **React 19** con TypeScript
- **Vite** - Build tool rápido
- **React Router DOM** - Navegación SPA
- **Bootstrap 5** - Framework CSS
- **React-Bootstrap** - Componentes React de Bootstrap
- **Axios** - Cliente HTTP
- **React-Dropzone** - Drag & drop de archivos

## Variables de Entorno

Archivo `.env`:
```
VITE_API_URL=http://localhost:8001
```

## Scripts NPM

```bash
npm run dev      # Desarrollo (puerto 5005)
npm start        # Alias de dev
npm run build    # Build para producción
npm run preview  # Preview del build
npm run lint     # Linter ESLint
```

## Estructura de Carpetas

```
frontend-invoice-portal/
├── public/              # Archivos estáticos
├── src/
│   ├── components/      # Componentes reutilizables
│   │   ├── BillingForm.tsx
│   │   ├── InvoicePreview.tsx
│   │   ├── TicketForm.tsx
│   │   ├── TicketList.tsx
│   │   └── TicketUpload.tsx
│   ├── pages/           # Páginas de la app
│   │   ├── GenerateInvoicePage.tsx
│   │   ├── HomePage.tsx
│   │   ├── MyTicketsPage.tsx
│   │   └── UploadTicketPage.tsx
│   ├── services/        # Servicios de API
│   │   └── api.ts
│   ├── App.tsx          # Router principal
│   ├── main.tsx         # Punto de entrada
│   └── vite-env.d.ts    # Tipos de Vite
├── .env                 # Variables de entorno
├── .gitignore
├── index.html           # HTML principal
├── package.json         # Dependencias
├── tsconfig.json        # Config de TypeScript
├── vite.config.ts       # Config de Vite
└── README.md            # Documentación completa
```

## Características Implementadas

### Funcionalidades Core

- [x] Sistema de acceso sin registro (solo email)
- [x] Subida de imágenes con drag & drop
- [x] Integración con OCR para escaneo automático
- [x] Formulario editable de tickets
- [x] Gestión de productos con tabla editable
- [x] Formulario de datos de facturación
- [x] Lista de tickets con filtros por estado
- [x] Selección múltiple de tickets
- [x] Preview de factura antes de generar
- [x] Generación de facturas en PDF
- [x] Descarga automática de PDFs

### UX/UI

- [x] Diseño responsive (mobile-first)
- [x] Iconografía con Bootstrap Icons
- [x] Feedback visual (spinners, alerts)
- [x] Validación de formularios
- [x] Manejo de errores amigable
- [x] Estados de carga
- [x] Confirmaciones antes de acciones críticas

### Integraciones

- [x] API REST completa
- [x] Manejo de archivos (upload/download)
- [x] OCR automático
- [x] Generación de PDFs

## Testing Manual

1. **Acceso**:
   - Ir a http://localhost:5005
   - Ingresar email válido
   - Verificar navegación

2. **Subir Ticket**:
   - Arrastrar imagen de ticket
   - Verificar preview
   - Click en "Escanear Ticket"
   - Verificar que datos se autorellenan
   - Editar datos si es necesario
   - Agregar datos de facturación
   - Guardar

3. **Ver Tickets**:
   - Ver lista de tickets
   - Verificar estados (pendiente, facturado)
   - Seleccionar múltiples tickets
   - Verificar total calculado

4. **Generar Factura**:
   - Seleccionar tickets
   - Ir a generar factura
   - Verificar preview
   - Confirmar datos
   - Generar PDF
   - Verificar descarga

## Integración con Backend

El frontend espera estos endpoints del backend:

### Tickets
- `GET /public/tickets?email={email}`
- `GET /public/tickets/{id}`
- `POST /public/tickets`
- `POST /public/tickets/{id}/upload`
- `POST /public/tickets/scan`

### Invoices
- `GET /public/invoices?email={email}`
- `POST /public/invoices`
- `GET /public/invoices/{id}/pdf`

## Próximos Pasos

1. Ejecutar el frontend: `npm run dev`
2. Asegurar que el backend está corriendo en http://localhost:8001
3. Abrir http://localhost:5005 en el navegador
4. Probar el flujo completo de usuario

## Soporte

Si encuentras problemas:

1. Verifica que el backend esté corriendo
2. Revisa la consola del navegador para errores
3. Verifica la configuración en `.env`
4. Asegúrate de que todas las dependencias estén instaladas
