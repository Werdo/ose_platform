# App 5: Invoice Management - Panel de Administración

Panel de administración completo para la gestión de facturas desde tickets.

## Estructura de Archivos

### Página Principal
- `InvoiceManagementPage.tsx` - Página principal con tabs y estadísticas

### Componentes
Located in `src/components/invoice/`:

#### Tablas
- `TicketTable.tsx` - Tabla de tickets subidos con filtros y acciones
- `InvoiceTable.tsx` - Tabla de facturas generadas con filtros y acciones

#### Modales
- `TicketEditModal.tsx` - Modal para editar datos de tickets manualmente
- `TicketImageModal.tsx` - Modal para visualizar imágenes de tickets
- `InvoicePreviewModal.tsx` - Modal para previsualizar facturas con detalles completos

#### Configuración
- `ConfigurationForm.tsx` - Formulario de configuración con 3 tabs (Empresa, Facturación, OCR)
- `LogoUploader.tsx` - Componente de drag & drop para subir logo de empresa

### Tipos TypeScript
- `src/types/invoice.ts` - Definiciones de tipos completas para toda la aplicación

## Características Implementadas

### Tab "Tickets"
- ✅ Tabla con todos los tickets subidos
- ✅ Filtros por estado, email, rango de fechas
- ✅ Búsqueda por número de ticket
- ✅ Subida de tickets (image upload)
- ✅ Procesamiento OCR automático
- ✅ Edición manual de datos
- ✅ Visualización de imagen del ticket
- ✅ Eliminación de tickets
- ✅ Estados: pending, processed, invoiced, error

### Tab "Facturas"
- ✅ Tabla de facturas generadas
- ✅ Columnas: número, cliente, fecha, total, estado
- ✅ Filtros por estado, cliente, rango de fechas
- ✅ Búsqueda por número de factura
- ✅ Acciones:
  - Ver detalles completos (modal)
  - Descargar/Ver PDF
  - Regenerar factura
  - Enviar por email
  - Cancelar factura
- ✅ Estados: draft, issued, sent, paid, cancelled

### Tab "Configuración"
- ✅ **Datos de Empresa:**
  - Nombre, NIF, dirección completa
  - Ciudad y código postal
  - Teléfono y email
  - Upload de logo con drag & drop
  - Preview del logo

- ✅ **Configuración de Facturación:**
  - Serie de factura (personalizable)
  - Próximo número (auto-incrementa, solo lectura)
  - Reset anual (checkbox)
  - Tasa de IVA configurable
  - Selección de plantilla (default, modern, classic, minimal)
  - Colores personalizados (primario y secundario)
  - Texto personalizado del pie de página

- ✅ **Configuración de OCR:**
  - Habilitar/deshabilitar OCR automático
  - Umbral de confianza ajustable (0.0 - 1.0)
  - Permitir entrada manual (switch)

### Estadísticas
- ✅ 4 tarjetas con métricas principales:
  - Total de tickets
  - Tickets pendientes
  - Facturas emitidas
  - Total facturado en el mes

## Endpoints API Utilizados

```typescript
// Estadísticas
GET /api/app5/stats

// Tickets
GET /api/app5/tickets?status=&email=&date_from=&date_to=&search=
POST /api/app5/tickets/upload (multipart/form-data)
PATCH /api/app5/tickets/:id
DELETE /api/app5/tickets/:id
POST /api/app5/tickets/:id/process-ocr

// Facturas
GET /api/app5/invoices?status=&customer=&date_from=&date_to=&search=
GET /api/app5/invoices/:id/pdf
POST /api/app5/invoices/:id/regenerate
POST /api/app5/invoices/:id/send-email
POST /api/app5/invoices/:id/cancel

// Configuración
GET /api/app5/config
PUT /api/app5/config
POST /api/app5/upload-logo (multipart/form-data)
```

## Rutas Configuradas

- `/app5` → InvoiceManagementPage
- `/invoice` → InvoiceManagementPage

## Tecnologías y Librerías

- **React** 18+ con TypeScript
- **React Bootstrap** - Componentes UI
- **React Hot Toast** - Notificaciones
- **date-fns** - Formateo de fechas
- **Axios** - Cliente HTTP
- **Bootstrap Icons** - Iconografía

## Integración con el Sistema

- ✅ Usa el servicio `apiService` existente
- ✅ Integrado con sistema de autenticación (`useAuth`)
- ✅ Sigue el patrón de diseño de las otras apps
- ✅ Manejo consistente de errores y loading states
- ✅ Responsive design con React Bootstrap

## Uso

### Instalación
No se requiere instalación adicional, todos los componentes usan las dependencias existentes del proyecto.

### Desarrollo
```bash
npm run dev
```

### Acceso
Navega a `/app5` o `/invoice` después de iniciar sesión en el portal.

## Próximas Mejoras Sugeridas

1. **Generación de facturas desde tickets**
   - Botón "Generar Factura" en TicketTable
   - Wizard/modal para configurar datos del cliente

2. **Dashboard de analytics**
   - Gráficos de facturas por mes
   - Análisis de ingresos
   - Top clientes

3. **Plantillas de PDF**
   - Editor visual de plantillas
   - Más opciones de personalización

4. **Notificaciones**
   - Alertas cuando se recibe un ticket
   - Confirmación de envío de email

5. **Exportación**
   - Exportar facturas a Excel/CSV
   - Generación de reportes

## Notas de Implementación

- Todos los componentes implementan loading states con spinners
- Error handling con toast notifications
- Formularios validados
- Filtros y búsquedas en tiempo real
- Diseño responsive para móviles y tablets
- Accesibilidad con ARIA labels
- Code splitting ready
