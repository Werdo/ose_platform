# Quick Start Guide - OSE Picking Portal

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Backend API running on `http://localhost:8001`

## Installation & Setup

1. **Navigate to the project directory:**
```bash
cd C:\Users\pedro\claude-code-workspace\OSE-Platform\frontend-picking-portal
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start the development server:**
```bash
npm run dev
```

4. **Open your browser:**
Navigate to `http://localhost:5006`

## Quick Tour

### 1. Home Page (/)
- View real-time statistics
- Choose between Palets or Paquetes picking

### 2. Pallet Picking (/palets)
- Fill out the form on the left to create a new pallet
- Required fields: Pallet Number, Tipo de Contenido
- Click "Crear Palet" to submit
- View your pallet in the list on the right
- Click QR code icon to generate and print label

### 3. Package Picking (/paquetes)
- Fill out the form on the left to create a new package
- Required fields: Tracking Number, Transportista
- Click "Crear Paquete" to submit
- View your package in the list on the right
- Actions available:
  - QR code: Generate label
  - Check: Mark as sent
  - Envelope: Send notification email (requires customer email)

## Testing the Application

### Create a Test Pallet:
```
Pallet Number: PAL-TEST-001
Tipo de Contenido: Dispositivos electrónicos
Contenido IDs: DEV001, DEV002, DEV003
Pedido ID: ORD-2024-001
Peso (kg): 125.50
```

### Create a Test Package:
```
Tracking Number: SEUR123456789
Transportista: Seur
Order Code: ORD-2024-002
Cliente Email: test@ejemplo.com
Cliente Nombre: Juan Pérez
Dispositivos Info: 2x Laptops, 1x Monitor
Peso (kg): 5.50
```

## Common Operations

### Generate QR Code
1. Click the QR code icon next to any pallet/package
2. View the QR code in the modal
3. Click "Imprimir Etiqueta" to print

### Mark Package as Sent
1. Find the package in the list
2. Click the green check icon
3. Confirm the action
4. Package status will update to "enviado"

### Send Notification Email
1. Package must have a customer email
2. Click the envelope icon
3. Confirm the action
4. Email will be sent to the customer

## Troubleshooting

### "Error al cargar..."
- Ensure backend is running on port 8001
- Check browser console for errors
- Verify network connection

### Form Won't Submit
- Check all required fields are filled
- Verify email format is correct
- Check for error messages

### QR Code Not Generating
- Check browser console for errors
- Ensure qrcode library is installed
- Try refreshing the page

## Development Commands

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## API Endpoints Reference

All endpoints are prefixed with `http://localhost:8001/api/app6`

- `GET /stats` - Dashboard statistics
- `POST /palets` - Create pallet
- `GET /palets` - List pallets
- `POST /paquetes` - Create package
- `GET /paquetes` - List packages
- `POST /paquetes/{id}/marcar-enviado` - Mark sent
- `POST /paquetes/{id}/notificar` - Send notification

## Need Help?

- Check the main README.md for detailed documentation
- Review the browser console for error messages
- Verify backend API is running and accessible
- Check network tab in browser DevTools

## Next Steps

1. Customize the user authentication (replace `operario@ose.com`)
2. Add company logo and branding
3. Configure email templates for notifications
4. Set up production deployment
5. Configure barcode scanner integration

---

Happy picking!
