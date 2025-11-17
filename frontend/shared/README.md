# @ose/shared - OSE Platform Shared Library

Librería compartida de componentes, servicios y utilidades para todas las aplicaciones de OSE Platform.

## 📦 Contenido

- **Components**: Componentes Vue reutilizables (botones, tablas, formularios, layouts)
- **Services**: Servicios API (Axios, autenticación, CRUD)
- **Stores**: Stores de Pinia (auth, user, app state)
- **Utils**: Utilidades (validadores, formateadores, helpers)
- **Composables**: Composables de Vue (useAuth, useApi, useNotification)
- **Types**: Tipos TypeScript compartidos

## 🚀 Instalación

```bash
npm install
```

## 📝 Scripts Disponibles

```bash
# Desarrollo
npm run dev

# Build para producción
npm run build

# Type checking
npm run type-check

# Linting
npm run lint

# Formateo de código
npm run format

# Tests
npm run test
npm run test:ui
npm run test:coverage
```

## 🏗️ Estructura

```
src/
├── components/
│   ├── common/          # Componentes comunes (Button, Card, Dialog, etc.)
│   ├── forms/           # Componentes de formulario (Input, Select, etc.)
│   └── layout/          # Componentes de layout (Header, Sidebar, etc.)
├── services/
│   ├── api.service.ts   # Cliente Axios configurado
│   ├── auth.service.ts  # Servicio de autenticación
│   └── ...
├── stores/
│   ├── auth.store.ts    # Store de autenticación
│   └── ...
├── utils/
│   ├── validators.ts    # Validadores
│   ├── formatters.ts    # Formateadores
│   └── ...
├── composables/
│   └── ...
├── types/
│   └── ...
└── index.ts             # Punto de entrada principal
```

## 💻 Uso

```typescript
// Importar desde otras apps
import { apiService, authStore, AppButton } from '@ose/shared'
```

## 🧪 Testing

Esta librería usa Vitest para testing:

```bash
npm run test          # Ejecutar tests
npm run test:ui       # UI de tests
npm run test:coverage # Coverage report
```

## 📄 Licencia

© 2025 Oversun Energy - Todos los derechos reservados
