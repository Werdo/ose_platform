# Portal de Facturación para Clientes (App5)

Frontend público para que los clientes puedan gestionar tickets y generar facturas sin necesidad de registrarse.

## Características

- **Sin registro**: Los clientes solo necesitan su email para acceder
- **Subida de tickets**: Drag & drop de imágenes con escaneo OCR automático
- **Gestión de tickets**: Ver, editar y organizar tickets
- **Generación de facturas**: Crear facturas en PDF a partir de múltiples tickets
- **Responsive**: Diseño adaptable a todos los dispositivos

## Tecnologías

- **React 19** con TypeScript
- **Vite** como build tool
- **React Router** para navegación
- **Bootstrap 5** y React-Bootstrap para UI
- **Axios** para llamadas HTTP
- **React-Dropzone** para subida de archivos

## Instalación

```bash
# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev

# O usar el script personalizado
npm start
```

## Configuración

El archivo `.env` contiene la configuración de la API:

```env
VITE_API_URL=http://localhost:8001
```

## Scripts Disponibles

- `npm run dev` - Inicia el servidor de desarrollo en el puerto 5005
- `npm start` - Alias para iniciar el servidor
- `npm run build` - Construye la aplicación para producción
- `npm run preview` - Previsualiza la versión de producción
- `npm run lint` - Ejecuta el linter

## Estructura del Proyecto

```
src/
├── components/          # Componentes reutilizables
│   ├── TicketUpload.tsx        # Drag & drop de imágenes
│   ├── TicketForm.tsx          # Formulario de tickets
│   ├── BillingForm.tsx         # Datos de facturación
│   ├── TicketList.tsx          # Lista de tickets
│   └── InvoicePreview.tsx      # Preview de factura
├── pages/               # Páginas de la aplicación
│   ├── HomePage.tsx            # Landing con formulario de email
│   ├── UploadTicketPage.tsx    # Subir nuevo ticket
│   ├── MyTicketsPage.tsx       # Ver mis tickets
│   └── GenerateInvoicePage.tsx # Generar factura
├── services/            # Servicios de API
│   └── api.ts                  # Llamadas al backend
├── App.tsx              # Configuración de rutas
└── main.tsx             # Punto de entrada
```

## Flujo de Usuario

1. **Inicio**: El usuario ingresa su email en la página principal
2. **Opciones**:
   - Ver tickets existentes
   - Subir nuevo ticket
3. **Subir Ticket**:
   - Arrastrar imagen del ticket
   - Escanear con OCR (automático)
   - Editar/completar datos
   - Agregar información de facturación
   - Guardar
4. **Gestionar Tickets**:
   - Ver lista de tickets (pendientes, facturados, rechazados)
   - Seleccionar múltiples tickets pendientes
   - Generar factura
5. **Generar Factura**:
   - Revisar tickets seleccionados
   - Confirmar datos de facturación
   - Generar y descargar PDF

## API Endpoints Utilizados

### Tickets
- `GET /public/tickets?email={email}` - Obtener tickets por email
- `GET /public/tickets/{id}` - Obtener ticket específico
- `POST /public/tickets` - Crear nuevo ticket
- `POST /public/tickets/{id}/upload` - Subir imagen
- `POST /public/tickets/scan` - Escanear ticket con OCR

### Facturas
- `GET /public/invoices?email={email}` - Obtener facturas por email
- `POST /public/invoices` - Crear nueva factura
- `GET /public/invoices/{id}/pdf` - Descargar PDF

## Estilos y UI

- **Bootstrap 5**: Framework CSS principal
- **Bootstrap Icons**: Iconografía
- **Colores**: Paleta corporativa con Bootstrap
- **Responsive**: Mobile-first design
- **Componentes**: Cards, Forms, Tables, Buttons, Alerts

## Desarrollo

Para desarrollar nuevas características:

1. Crear componentes en `src/components/`
2. Crear páginas en `src/pages/`
3. Agregar rutas en `App.tsx`
4. Actualizar API service en `src/services/api.ts`

## Producción

Para construir para producción:

```bash
npm run build
```

Los archivos se generarán en la carpeta `dist/`.

## Puerto

La aplicación se ejecuta en el puerto **5005** por defecto.

## Integración con Backend

El frontend se comunica con el backend en `http://localhost:8001` (App5 - Invoice Service).

Asegúrate de que el backend esté corriendo antes de iniciar el frontend.
