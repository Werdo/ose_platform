# OSE Picking Portal - Frontend

A React + TypeScript + Bootstrap application for warehouse picking operations.

## Overview

The Picking Portal is a warehouse management system designed to handle two types of shipments:
- **Palets**: Large consolidated shipments with multiple items
- **Paquetes**: Individual packages sent via courier services

## Features

### Pallet Picking
- Create new pallets with detailed information
- Track pallet status (pendiente, picking, completado, enviado)
- Generate QR code labels for each pallet
- View recent pallets list with full details
- Print pallet labels with QR codes

### Package Picking
- Create new packages with tracking numbers
- Support for multiple courier services (Seur, Correos, DHL, UPS, FedEx)
- Mark packages as sent
- Send email notifications to customers
- Generate QR code labels for packages
- Track package status through the workflow

### Dashboard
- Real-time statistics display
- Total pallets and packages count
- Pending and completed items tracking
- Quick access to both picking modules

## Technology Stack

- **React 19**: UI framework
- **TypeScript**: Type-safe development
- **Vite**: Build tool and dev server
- **Bootstrap 5**: UI component library
- **React Bootstrap**: React components for Bootstrap
- **React Router DOM**: Client-side routing
- **Axios**: HTTP client for API calls
- **QRCode**: QR code generation library
- **Bootstrap Icons**: Icon library

## Project Structure

```
frontend-picking-portal/
├── src/
│   ├── pages/
│   │   ├── HomePage.tsx           # Landing page with stats
│   │   ├── PalletPicking.tsx      # Pallet management page
│   │   └── PackagePicking.tsx     # Package management page
│   ├── services/
│   │   └── api.ts                 # API service layer
│   ├── types/
│   │   └── index.ts               # TypeScript interfaces
│   ├── App.tsx                    # Main app component
│   ├── main.tsx                   # Entry point
│   └── index.css                  # Custom styles
├── index.html
├── vite.config.ts                 # Vite configuration
├── package.json
└── tsconfig.json
```

## Installation

1. Install dependencies:
```bash
npm install
```

## Running the Application

### Development Mode
```bash
npm run dev
```
The application will be available at `http://localhost:5006`

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## API Integration

The frontend connects to the backend API at `http://localhost:8001/api/app6`

### API Endpoints Used

#### Pallets
- `POST /api/app6/palets` - Create new pallet
- `GET /api/app6/palets` - Get pallets list
- `GET /api/app6/palets/{id}` - Get pallet by ID
- `PUT /api/app6/palets/{id}/status` - Update pallet status

#### Packages
- `POST /api/app6/paquetes` - Create new package
- `GET /api/app6/paquetes` - Get packages list
- `GET /api/app6/paquetes/tracking/{tracking}` - Get package by tracking number
- `PUT /api/app6/paquetes/{id}/status` - Update package status
- `POST /api/app6/paquetes/{id}/marcar-enviado` - Mark package as sent
- `POST /api/app6/paquetes/{id}/notificar` - Send notification email

#### Statistics
- `GET /api/app6/stats` - Get dashboard statistics

## Configuration

### Backend URL
The backend URL is configured in `src/services/api.ts`:
```typescript
const API_BASE_URL = 'http://localhost:8001/api/app6';
```

### Proxy Configuration
The Vite dev server is configured to proxy API requests in `vite.config.ts`:
```typescript
server: {
  port: 5006,
  proxy: {
    '/api': {
      target: 'http://localhost:8001',
      changeOrigin: true,
      secure: false,
    },
  },
}
```

## User Roles

Currently, the application uses a hardcoded user email:
- Default user: `operario@ose.com`

This should be replaced with actual authentication in production.

## Features in Detail

### QR Code Generation
Each pallet and package can generate a QR code containing:
- Type (pallet or package)
- ID
- Tracking/pallet number
- Additional metadata

QR codes can be printed as labels for physical items.

### Form Validation
All forms include client-side validation:
- Required fields marked with asterisk (*)
- Email format validation
- Number format validation
- Real-time feedback on errors

### Status Management
Both pallets and packages have status workflows:

**Pallet Status:**
- pendiente (pending)
- picking (in progress)
- completado (completed)
- enviado (sent)

**Package Status:**
- pendiente (pending)
- preparado (prepared)
- enviado (sent)
- entregado (delivered)

### Transporters Supported
- Seur
- Correos
- DHL
- UPS
- FedEx

## UI Components

### HomePage
- Statistics cards showing totals
- Large navigation cards for Palets and Paquetes
- Responsive grid layout

### PalletPicking
- Creation form in left sidebar
- List of recent pallets in main area
- QR code modal for label generation
- Status badges with color coding

### PackagePicking
- Creation form in left sidebar
- List of recent packages in main area
- Action buttons for: QR code, Mark as sent, Send notification
- Transporter icons for visual identification

## Styling

The application uses:
- Bootstrap 5 utility classes
- Custom CSS in `index.css`
- Bootstrap Icons for all icons
- Responsive design for mobile and desktop
- Custom hover effects and transitions
- Print-specific styles for QR code labels

## Error Handling

All API calls include:
- Try/catch blocks
- User-friendly error messages
- Toast-style alerts (auto-dismiss after 5 seconds)
- Loading states during async operations

## Browser Compatibility

The application is compatible with modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Future Enhancements

Potential improvements:
- User authentication system
- Advanced search and filtering
- Bulk operations
- Export to Excel/PDF
- Barcode scanner integration
- Real-time updates via WebSocket
- Mobile app version
- Advanced analytics dashboard

## Troubleshooting

### API Connection Issues
If you see "Error al cargar..." messages:
1. Verify the backend is running at `http://localhost:8001`
2. Check the browser console for CORS errors
3. Verify the API endpoints in `src/services/api.ts`

### Build Errors
If TypeScript compilation fails:
1. Run `npm install` to ensure all dependencies are installed
2. Check `tsconfig.json` for configuration issues
3. Verify all imports are correct

### Port Already in Use
If port 5006 is already in use:
1. Change the port in `vite.config.ts`
2. Update any hardcoded references to the port

## License

OSE Platform - Internal Use Only

## Contact

For support or questions, contact the OSE Platform team.
