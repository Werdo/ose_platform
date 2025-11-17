# OSE Platform - Database Schema Reference

**Version:** 1.0
**Last Updated:** 2025-11-14
**Database:** MongoDB (via Beanie ODM)

---

## Table of Contents

1. [Overview](#overview)
2. [Collections](#collections)
   - [devices](#1-devices)
   - [customers](#2-customers)
   - [production_orders](#3-production_orders)
   - [movimientos](#4-movimientos)
   - [series_notifications](#5-series_notifications)
   - [packages](#6-packages)
   - [pallets](#7-pallets)
   - [employees](#8-employees)
3. [Relationships](#relationships)
4. [Example Documents](#example-documents)
5. [Common Query Patterns](#common-query-patterns)

---

## Overview

The OSE Platform uses MongoDB as its primary database with Beanie ODM (Object-Document Mapper) for Python. The system manages IoT/GPS device manufacturing, quality control, logistics, and customer notifications.

**Key Features:**
- Device lifecycle tracking (production to deployment)
- Customer and order management
- Logistics and movement tracking
- Employee authentication and permissions
- Series notifications for clients

---

## Collections

### 1. devices

**Purpose:** Core collection for managing IoT/GPS devices throughout their lifecycle from production to deployment.

**Collection Name:** `devices`

#### Fields

| Field Name | Data Type | Required | Indexed | Description | Example Value |
|------------|-----------|----------|---------|-------------|---------------|
| `_id` | ObjectId | Yes | Yes (auto) | MongoDB document ID | `507f1f77bcf86cd799439011` |
| `imei` | string | Yes | Yes | IMEI of the device (15 digits) | `123456789012345` |
| `ccid` | string | No | Yes | ICCID of the SIM card (19-22 digits) | `8934071000000000000` |
| `nro_orden` | string | No | Yes | Production order number | `ORD-2025-001` |
| `lote` | integer | No | No | Batch number within the order | `1` |
| `linea` | integer | No | No | Production line (1, 2, 3) | `1` |
| `puesto` | integer | No | No | Workstation number (1, 2) | `1` |
| `marca` | string | No | No | Device brand | `OversunTrack` |
| `nro_referencia` | string | No | No | Model reference number | `REF-2024-GPS-001` |
| `sku` | string | No | No | Product SKU | `SKU-GPS-100` |
| `estado` | enum | Yes | Yes | Device lifecycle state | `en_produccion` |
| `ubicacion_actual` | string | No | No | Current physical location | `Almacen A - Estante 3` |
| `package_no` | string | No | Yes | Package number (25 digits) | `PKG-2025-001-000000000001` |
| `codigo_innerbox` | string | No | No | Inner box/display box code | `IB-2025-001` |
| `codigo_unitario` | string | No | No | Individual device QR code | `UNIT-123456789012345` |
| `num_palet` | string | No | No | Pallet number | `PAL-2025-001` |
| `num_deposito` | string | No | No | Warehouse number | `DEP-001` |
| `cliente` | string | No | Yes | Customer ID (ObjectId as string) | `507f1f77bcf86cd799439012` |
| `cliente_codigo` | string | No | No | Customer code (denormalized) | `CUST-001` |
| `cliente_nombre` | string | No | No | Customer name (denormalized) | `Distribuidora Madrid SL` |
| `notificado` | boolean | Yes | Yes | If customer was notified (App 1) | `true` |
| `fecha_notificacion` | datetime | No | No | Date of customer notification | `2025-01-15T10:30:00Z` |
| `garantia` | object | No | No | Warranty information | See object structure below |
| `info_envio` | object | No | No | Shipping information | See object structure below |
| `valido` | boolean | Yes | No | If device passed all validations | `true` |
| `errores` | array | No | No | List of validation errors | `["IMEI duplicado"]` |
| `metadata` | object | No | No | Custom additional fields | `{"custom_field": "value"}` |
| `fecha_creacion` | datetime | Yes | Yes | Creation/registration date | `2025-01-15T08:00:00Z` |
| `fecha_actualizacion` | datetime | Yes | No | Last update date | `2025-01-15T10:30:00Z` |
| `creado_por` | string | No | No | Operator who created the record | `EMP-001` |
| `fecha_importacion` | datetime | No | No | Import date (if imported) | `2025-01-15T08:00:00Z` |

#### Estado (EstadoDispositivo) Enum Values
- `en_produccion` - In production
- `control_calidad` - Quality control
- `aprobado` - Approved
- `rechazado` - Rejected
- `empaquetado` - Packaged
- `enviado` - Shipped
- `activo` - Active (in service)
- `defectuoso` - Defective
- `rma` - RMA
- `reemplazado` - Replaced
- `retirado` - Retired

#### Garantia Object Structure
```json
{
  "fecha_inicio": "2025-01-15T00:00:00Z",
  "fecha_fin": "2026-01-15T00:00:00Z",
  "duracion_meses": 12,
  "tipo": "fabricante",
  "activa": true
}
```

#### Indexes
- Single: `imei`, `ccid`, `nro_orden`, `estado`, `cliente`, `package_no`, `notificado`, `fecha_creacion`
- Compound: `(imei, estado)`, `(nro_orden, lote)`, `(cliente, estado)`, `(notificado, cliente)`

---

### 2. customers

**Purpose:** Manages customer information including distributors, resellers, and end users.

**Collection Name:** `customers`

#### Fields

| Field Name | Data Type | Required | Indexed | Description | Example Value |
|------------|-----------|----------|---------|-------------|---------------|
| `_id` | ObjectId | Yes | Yes (auto) | MongoDB document ID | `507f1f77bcf86cd799439012` |
| `customer_code` | string | Yes | Yes | Unique customer code | `CUST-001` |
| `customer_type` | enum | Yes | No | Type of customer | `distributor` |
| `status` | enum | Yes | Yes | Customer status | `active` |
| `company_name` | string | No | No | Company name (for business customers) | `Distribuidora Madrid SL` |
| `first_name` | string | No | No | First name (for end users) | `Juan` |
| `last_name` | string | No | No | Last name (for end users) | `Pérez García` |
| `tax_id` | string | No | No | NIF/CIF/Tax ID | `B12345678` |
| `email` | EmailStr | Yes | Yes | Primary email | `contacto@distribuidora.com` |
| `phone` | string | No | No | Primary phone | `+34 912 345 678` |
| `mobile` | string | No | No | Mobile phone | `+34 600 123 456` |
| `website` | string | No | No | Website (for companies) | `https://distribuidora.com` |
| `address` | object | No | No | Customer address | See object structure below |
| `billing_address` | object | No | No | Billing address (if different) | See object structure below |
| `devices_count` | integer | Yes | No | Total devices owned | `150` |
| `active_devices_count` | integer | Yes | No | Active devices count | `145` |
| `tickets_count` | integer | Yes | No | Total tickets generated | `12` |
| `rma_count` | integer | Yes | No | Total RMAs generated | `3` |
| `discount_rate` | float | No | No | Discount percentage (0-100) | `15.5` |
| `payment_terms` | string | No | No | Payment terms | `30_days` |
| `credit_limit` | float | No | No | Credit limit | `50000.00` |
| `contacts` | array | No | No | Additional contacts | See array structure below |
| `notes` | string | No | No | Internal notes about customer | `Cliente VIP, prioridad alta` |
| `preferences` | object | No | No | Customer preferences | `{"notification_email": true}` |
| `tags` | array | No | No | Tags for classification | `["vip", "distributor", "spain"]` |
| `created_at` | datetime | Yes | Yes | Registration date | `2024-06-15T10:00:00Z` |
| `updated_at` | datetime | Yes | No | Last update | `2025-01-15T14:30:00Z` |
| `last_purchase_date` | datetime | No | No | Last purchase date | `2025-01-10T00:00:00Z` |
| `metadata` | object | No | No | Additional data | `{"crm_id": "CRM-12345"}` |

#### CustomerType Enum Values
- `end_user` - End user
- `distributor` - Distributor
- `reseller` - Reseller
- `enterprise` - Enterprise
- `government` - Government

#### CustomerStatus Enum Values
- `active` - Active
- `inactive` - Inactive
- `suspended` - Suspended
- `blacklisted` - Blacklisted

#### Address Object Structure
```json
{
  "street": "Calle Principal 123",
  "city": "Madrid",
  "state": "Madrid",
  "postal_code": "28001",
  "country": "España"
}
```

#### Contacts Array Structure
```json
[
  {
    "name": "Juan Pérez",
    "role": "Gerente Técnico",
    "email": "juan@empresa.com",
    "phone": "+34 600 123 456",
    "added_at": "2024-07-01T10:00:00Z"
  }
]
```

#### Indexes
- Single: `customer_code`, `email`, `status`, `customer_type`, `created_at`
- Compound: `(customer_type, status)`

---

### 3. production_orders

**Purpose:** Manages production orders for device manufacturing.

**Collection Name:** `production_orders`

#### Fields

| Field Name | Data Type | Required | Indexed | Description | Example Value |
|------------|-----------|----------|---------|-------------|---------------|
| `_id` | ObjectId | Yes | Yes (auto) | MongoDB document ID | `507f1f77bcf86cd799439013` |
| `order_number` | string | Yes | Yes | Unique production order number | `ORD-2025-001` |
| `reference_number` | string | No | No | Product reference number | `REF-2024-GPS-001` |
| `sku` | integer | No | No | Product SKU to manufacture | `100` |
| `product_name` | string | No | No | Product name | `GPS Tracker Pro` |
| `brand` | string | No | No | Product brand | `OversunTrack` |
| `quantity` | integer | Yes | No | Total quantity to produce | `1000` |
| `produced` | integer | Yes | No | Quantity produced | `850` |
| `approved` | integer | Yes | No | Quantity approved in QC | `820` |
| `rejected` | integer | Yes | No | Quantity rejected in QC | `30` |
| `status` | enum | Yes | Yes | Order status | `in_progress` |
| `production_line` | integer | No | Yes | Assigned production line (1-3) | `1` |
| `responsible` | string | No | No | Responsible employee ID | `EMP-001` |
| `created_at` | datetime | Yes | Yes | Order creation date | `2025-01-10T08:00:00Z` |
| `start_date` | datetime | No | No | Production start date | `2025-01-11T08:00:00Z` |
| `end_date` | datetime | No | No | Production end date | `2025-01-20T18:00:00Z` |
| `estimated_completion` | datetime | No | No | Estimated completion date | `2025-01-22T00:00:00Z` |
| `updated_at` | datetime | Yes | No | Last update | `2025-01-15T14:00:00Z` |
| `batches` | array | No | No | Production batches (coupons) | See array structure below |
| `total_batches` | integer | Yes | No | Total planned batches | `4` |
| `labels_required` | object | No | No | Required labels by type | See object structure below |
| `notes` | string | No | No | Additional notes | `Urgente, cliente VIP` |
| `priority` | string | No | No | Order priority | `high` |
| `metadata` | object | No | No | Custom additional fields | `{"customer_order": "CO-2025-045"}` |

#### ProductionOrderStatus Enum Values
- `pending` - Pending
- `in_progress` - In progress
- `paused` - Paused
- `on_hold` - On hold
- `packing` - Packing
- `completed` - Completed
- `cancelled` - Cancelled

#### Priority Values
- `low` - Low priority
- `normal` - Normal priority
- `high` - High priority
- `critical` - Critical priority

#### Batches Array Structure
```json
[
  {
    "batch_number": 1,
    "quantity": 250,
    "workstation": 1,
    "operator": "EMP001",
    "start_date": "2025-01-15T08:00:00Z",
    "end_date": "2025-01-15T12:00:00Z",
    "produced": 250,
    "status": "completed"
  }
]
```

#### Labels Required Object Structure
```json
{
  "label_24": 1000,
  "label_48": 500,
  "label_80": 1000,
  "label_96": 500
}
```

#### Indexes
- Single: `order_number`, `status`, `production_line`, `created_at`
- Compound: `(status, production_line)`, `(created_at DESC)`

---

### 4. movimientos

**Purpose:** Critical collection for logistics movement tracking (entries, exits, transfers).

**Collection Name:** `movimientos`

#### Fields

| Field Name | Data Type | Required | Indexed | Description | Example Value |
|------------|-----------|----------|---------|-------------|---------------|
| `_id` | ObjectId | Yes | Yes (auto) | MongoDB document ID | `507f1f77bcf86cd799439014` |
| `tipo` | enum | Yes | Yes | Type of movement | `salida` |
| `fecha` | datetime | Yes | Yes | Movement date | `2025-01-15T10:30:00Z` |
| `producto` | string | No | Yes | Device ID (ObjectId as string) | `507f1f77bcf86cd799439011` |
| `imei` | string | No | Yes | Device IMEI (denormalized) | `123456789012345` |
| `ccid` | string | No | No | Device ICCID (denormalized) | `8934071000000000000` |
| `cantidad` | integer | Yes | No | Quantity of units moved | `1` |
| `cliente` | string | No | Yes | Customer ID (ObjectId as string) | `507f1f77bcf86cd799439012` |
| `cliente_nombre` | string | No | No | Customer name (denormalized) | `Distribuidora Madrid SL` |
| `cliente_codigo` | string | No | No | Customer code (denormalized) | `CUST-001` |
| `deposito` | string | No | Yes | Origin warehouse/depot | `DEP-001` |
| `deposito_destino` | string | No | No | Destination warehouse (transfers) | `DEP-002` |
| `ubicacion_origen` | string | No | No | Origin physical location | `Almacen A - Estante 3` |
| `ubicacion_destino` | string | No | No | Destination physical location | `Almacen B - Estante 5` |
| `documento_referencia` | string | No | Yes | Reference document number | `ALB-2025-001` |
| `orden_produccion` | string | No | No | Related production order number | `ORD-2025-001` |
| `lote` | integer | No | No | Production batch | `1` |
| `usuario` | string | No | Yes | User who recorded the movement | `EMP-001` |
| `usuario_nombre` | string | No | No | User name (denormalized) | `Juan Operador` |
| `origen` | string | Yes | No | Movement origin | `manual` |
| `detalles` | string | No | No | Movement details or notes | `Envío urgente cliente VIP` |
| `metadata` | object | No | No | Custom additional data | `{"shipping_tracking": "TRK123"}` |
| `costo_unitario` | float | No | No | Unit cost of the movement | `45.50` |
| `costo_total` | float | No | No | Total cost of the movement | `45.50` |
| `moneda` | string | No | No | Currency | `EUR` |
| `created_at` | datetime | Yes | Yes | Record creation date | `2025-01-15T10:30:00Z` |
| `updated_at` | datetime | Yes | No | Last update | `2025-01-15T10:30:00Z` |

#### TipoMovimiento Enum Values
- `entrada` - Entry (receiving goods)
- `salida` - Exit (shipping to customer)
- `envio` - Shipment (alias for salida)
- `transferencia` - Transfer (between warehouses)
- `ajuste` - Adjustment (inventory adjustment)
- `devolucion` - Return (RMA/return)
- `produccion` - Production (output from production)
- `scrap` - Scrap (defect write-off)

#### Origen Values
- `manual` - Manual entry
- `app1` - From App 1
- `app2` - From App 2
- `import` - Imported
- `api` - API integration

#### Indexes
- Single: `tipo`, `fecha`, `producto`, `imei`, `cliente`, `deposito`, `usuario`, `documento_referencia`, `created_at`
- Compound: `(tipo, fecha DESC)`, `(producto, fecha DESC)`, `(cliente, fecha DESC)`, `(deposito, fecha DESC)`, `(usuario, fecha DESC)`

---

### 5. series_notifications

**Purpose:** Historical record of series notifications sent to customers (App 1).

**Collection Name:** `series_notifications`

#### Fields

| Field Name | Data Type | Required | Indexed | Description | Example Value |
|------------|-----------|----------|---------|-------------|---------------|
| `_id` | ObjectId | Yes | Yes (auto) | MongoDB document ID | `507f1f77bcf86cd799439015` |
| `fecha` | datetime | Yes | Yes | Notification date | `2025-01-15T11:00:00Z` |
| `customer_id` | string | No | Yes | Customer ID | `507f1f77bcf86cd799439012` |
| `customer_name` | string | No | No | Customer name | `Distribuidora Madrid SL` |
| `customer_code` | string | No | No | Customer code | `CUST-001` |
| `location` | string | Yes | Yes | Batch or delivery note number | `LOTE-2025-001` |
| `serials` | array | Yes | No | List of notified devices | See array structure below |
| `device_count` | integer | Yes | No | Number of notified devices | `25` |
| `notified_count` | integer | Yes | No | Devices marked as notified in DB | `25` |
| `failed_serials` | array | No | No | IMEIs that failed to notify | `["123456789012345"]` |
| `csv_format` | string | Yes | No | CSV format type | `separated` |
| `csv_filename` | string | Yes | No | Generated CSV filename | `series_LOTE-2025-001_20250115.csv` |
| `csv_content` | string | No | No | CSV content (optional, can be large) | `"IMEI,ICCID\n123..."` |
| `email_to` | string | Yes | Yes | Recipient email | `contacto@distribuidora.com` |
| `email_cc` | array | No | No | CC emails | `["backup@distribuidora.com"]` |
| `email_sent` | boolean | Yes | No | If email was sent successfully | `true` |
| `operator_id` | string | Yes | Yes | Operator who sent the notification | `EMP-001` |
| `operator_name` | string | Yes | No | Operator name | `Juan Operador` |
| `operator_email` | string | Yes | No | Operator email | `juan@ose.com` |
| `notes` | string | No | No | Additional notes | `Envío urgente` |
| `errors` | array | No | No | List of errors occurred | `["Email delivery delayed"]` |

#### CSV Format Values
- `separated` - Separated format
- `unified` - Unified format
- `detailed` - Detailed format
- `compact` - Compact format

#### Serials Array Structure
```json
[
  {
    "imei": "123456789012345",
    "ccid": "8934071000000000000",
    "device_id": "507f1f77bcf86cd799439011",
    "marca": "OversunTrack",
    "modelo": "GPS Tracker Pro"
  }
]
```

#### Indexes
- Single: `fecha`, `customer_id`, `location`, `email_to`, `operator_id`

---

### 6. packages

**Purpose:** Small package shipment management with tracking.

**Collection Name:** `packages`

#### Fields

| Field Name | Data Type | Required | Indexed | Description | Example Value |
|------------|-----------|----------|---------|-------------|---------------|
| `_id` | ObjectId | Yes | Yes (auto) | MongoDB document ID | `507f1f77bcf86cd799439016` |
| `tracking_number` | string | Yes | Yes | Carrier tracking number | `CX123456789ES` |
| `transportista` | string | Yes | Yes | Carrier name | `Seur` |
| `order_code` | string | Yes | Yes | Web order code | `PEDWEB-20251111-0021` |
| `order_ref` | ObjectId | No | No | Order ObjectId reference | `507f1f77bcf86cd799439020` |
| `cliente_id` | ObjectId | No | No | Customer reference | `507f1f77bcf86cd799439012` |
| `cliente_email` | EmailStr | Yes | Yes | Customer email for notification | `cliente@example.com` |
| `cliente_nombre` | string | No | No | Customer name | `Juan Pérez` |
| `cliente_telefono` | string | No | No | Customer phone | `+34 600 123 456` |
| `direccion_envio` | string | No | No | Full shipping address | `Calle Principal 123` |
| `ciudad` | string | No | No | City | `Madrid` |
| `codigo_postal` | string | No | No | Postal code | `28001` |
| `pais` | string | Yes | No | Country (ISO code) | `ES` |
| `dispositivos` | array | No | No | Device ObjectId references | `["507f1f77bcf86cd799439011"]` |
| `dispositivos_info` | array | No | No | Denormalized device info | See array structure below |
| `peso_kg` | float | No | No | Weight in kg | `0.5` |
| `dimensiones` | string | No | No | Dimensions | `30x20x10 cm` |
| `numero_bultos` | integer | Yes | No | Number of packages | `1` |
| `tipo` | string | Yes | No | Shipment type | `paqueteria` |
| `estado` | string | Yes | Yes | Package status | `enviado` |
| `fecha_envio` | datetime | No | No | Shipment date | `2025-01-15T10:00:00Z` |
| `fecha_entrega_estimada` | datetime | No | No | Estimated delivery date | `2025-01-17T00:00:00Z` |
| `fecha_entrega_real` | datetime | No | No | Actual delivery date | `2025-01-16T14:30:00Z` |
| `email_enviado` | boolean | Yes | No | If notification email was sent | `true` |
| `fecha_email` | datetime | No | No | Email sent date | `2025-01-15T10:05:00Z` |
| `enlace_seguimiento` | string | No | No | Carrier tracking URL | `https://tracking.seur.com/...` |
| `creado_por` | string | Yes | No | User who created the package | `operario@ose.com` |
| `fecha_creacion` | datetime | Yes | Yes | Creation date | `2025-01-15T09:00:00Z` |
| `fecha_modificacion` | datetime | No | No | Last modification date | `2025-01-15T10:00:00Z` |
| `notas` | string | No | No | Additional observations | `Entrega antes de las 18:00` |

#### Estado Values
- `preparado` - Prepared
- `enviado` - Sent
- `en_transito` - In transit
- `entregado` - Delivered
- `incidencia` - Incident

#### Dispositivos Info Array Structure
```json
[
  {
    "imei": "123456789012345",
    "modelo": "Tracker GPS",
    "descripcion": "Rastreador vehicular"
  }
]
```

#### Indexes
- Single: `tracking_number`, `order_code`, `transportista`, `estado`, `cliente_email`, `fecha_creacion`

---

### 7. pallets

**Purpose:** Pallet management for logistics picking.

**Collection Name:** `pallets`

#### Fields

| Field Name | Data Type | Required | Indexed | Description | Example Value |
|------------|-----------|----------|---------|-------------|---------------|
| `_id` | ObjectId | Yes | Yes (auto) | MongoDB document ID | `507f1f77bcf86cd799439017` |
| `pallet_number` | string | Yes | Yes | Unique pallet number | `PAL-2025-0001` |
| `qr_code` | string | Yes | Yes | Generated QR code for the pallet | `QR-PAL-2025-0001-ABC123` |
| `tipo_contenido` | string | Yes | No | Content type | `lote` |
| `contenido_ids` | array | No | No | IDs of batches, boxes or devices | `["LOTE-2024-1234"]` |
| `dispositivos` | array | No | No | Device ObjectId references | `["507f1f77bcf86cd799439011"]` |
| `pedido_id` | string | No | Yes | Associated order code | `PED-2025-0045` |
| `pedido_ref` | ObjectId | No | No | Order ObjectId reference | `507f1f77bcf86cd799439020` |
| `peso_kg` | float | No | No | Approximate weight in kg | `250.5` |
| `volumen_m3` | float | No | No | Approximate volume in m³ | `1.2` |
| `ubicacion` | string | No | No | Warehouse location | `Almacen A - Zona 2` |
| `creado_por` | string | Yes | No | User who created the pallet | `operario@ose.com` |
| `fecha_creacion` | datetime | Yes | Yes | Creation date | `2025-01-15T08:00:00Z` |
| `fecha_modificacion` | datetime | No | No | Last modification date | `2025-01-15T10:00:00Z` |
| `estado` | string | Yes | Yes | Pallet status | `preparado` |
| `notas` | string | No | No | Additional observations | `Frágil, manipular con cuidado` |

#### Tipo Contenido Values
- `lote` - Batch
- `caja` - Box
- `unidad` - Unit
- `sku` - SKU

#### Estado Values
- `preparado` - Prepared
- `en_transito` - In transit
- `entregado` - Delivered
- `cancelado` - Cancelled

#### Indexes
- Single: `pallet_number`, `qr_code`, `pedido_id`, `estado`, `fecha_creacion`

---

### 8. employees

**Purpose:** Employee management and authentication.

**Collection Name:** `employees`

#### Fields

| Field Name | Data Type | Required | Indexed | Description | Example Value |
|------------|-----------|----------|---------|-------------|---------------|
| `_id` | ObjectId | Yes | Yes (auto) | MongoDB document ID | `507f1f77bcf86cd799439018` |
| `employee_id` | string | Yes | Yes | Unique employee ID | `EMP-001` |
| `name` | string | Yes | No | Employee first name | `Juan` |
| `surname` | string | Yes | No | Employee surname | `García Martínez` |
| `email` | EmailStr | No | Yes | Employee email | `juan.garcia@ose.com` |
| `phone` | string | No | No | Contact phone | `+34 912 345 678` |
| `password_hash` | string | Yes | No | Bcrypt password hash | `$2b$12$KIXxRv...` |
| `role` | enum | Yes | Yes | Main employee role | `operator` |
| `status` | enum | Yes | Yes | Employee status | `active` |
| `permissions` | object | Yes | No | Granular permissions | See object structure below |
| `last_login` | datetime | No | No | Last login date | `2025-01-15T08:00:00Z` |
| `last_login_ip` | string | No | No | Last login IP | `192.168.1.100` |
| `failed_login_attempts` | integer | Yes | No | Failed login attempts counter | `0` |
| `locked_until` | datetime | No | No | Locked until (failed attempts) | `2025-01-15T08:30:00Z` |
| `refresh_token` | string | No | No | Current JWT refresh token | `eyJhbGc...` |
| `refresh_token_expires` | datetime | No | No | Refresh token expiration | `2025-01-22T08:00:00Z` |
| `created_at` | datetime | Yes | No | Creation date | `2024-06-01T10:00:00Z` |
| `updated_at` | datetime | Yes | No | Last update | `2025-01-15T08:00:00Z` |
| `created_by` | string | No | No | User who created this record | `ADMIN-001` |
| `notes` | string | No | No | Additional notes | `Empleado del mes enero` |

#### EmployeeRole Enum Values
- `operator` - Operator
- `supervisor` - Supervisor
- `quality_inspector` - Quality Inspector
- `technician` - Technician
- `manager` - Manager
- `admin` - Admin
- `super_admin` - Super Admin

#### EmployeeStatus Enum Values
- `active` - Active
- `inactive` - Inactive
- `suspended` - Suspended
- `on_leave` - On leave

#### Permissions Object Structure
```json
{
  "production_line1_station1": false,
  "production_line1_station2": false,
  "production_line2_station1": false,
  "production_line2_station2": false,
  "production_line3_station1": false,
  "production_line3_station2": false,
  "quality_control": false,
  "admin_access": false,
  "manage_users": false,
  "manage_settings": false,
  "view_reports": false,
  "manage_tickets": false,
  "manage_rma": false,
  "manage_customers": false,
  "manage_inventory": false
}
```

#### Indexes
- Single: `employee_id`, `email`, `role`, `status`
- Compound: `(employee_id, status)`

---

## Relationships

### Foreign Key Relationships

```
devices
  ├─ nro_orden → production_orders.order_number
  ├─ cliente → customers._id
  ├─ package_no → packages.tracking_number (loose)
  ├─ num_palet → pallets.pallet_number (loose)
  └─ creado_por → employees.employee_id

customers
  └─ (no foreign keys, referenced by other collections)

production_orders
  └─ responsible → employees.employee_id

movimientos
  ├─ producto → devices._id
  ├─ cliente → customers._id
  ├─ orden_produccion → production_orders.order_number
  └─ usuario → employees.employee_id

series_notifications
  ├─ customer_id → customers._id
  └─ operator_id → employees.employee_id

packages
  ├─ cliente_id → customers._id
  ├─ dispositivos[] → devices._id
  └─ creado_por → employees.email

pallets
  ├─ dispositivos[] → devices._id
  └─ creado_por → employees.email

employees
  └─ created_by → employees.employee_id
```

### Relationship Diagram

```
┌─────────────────┐
│   employees     │◄─────────┐
└────────┬────────┘          │
         │                   │
         │ responsible       │ creado_por
         │                   │
         ▼                   │
┌─────────────────────┐      │
│ production_orders   │      │
└──────────┬──────────┘      │
           │                 │
           │ nro_orden       │
           │                 │
           ▼                 │
    ┌──────────┐             │
    │ devices  │◄────────────┤
    └────┬─────┘             │
         │                   │
         │ producto          │
         │                   │
         ▼                   │
  ┌──────────────┐           │
  │ movimientos  │───────────┘
  └──────────────┘
         │
         │ cliente
         │
         ▼
  ┌──────────────┐
  │  customers   │◄──────────┐
  └──────────────┘           │
         ▲                   │
         │ customer_id       │
         │                   │
  ┌──────────────────┐       │
  │ series_notif...  │       │
  └──────────────────┘       │
                             │
  ┌──────────────────┐       │
  │    packages      │───────┤
  └──────────────────┘       │
                             │
  ┌──────────────────┐       │
  │     pallets      │───────┘
  └──────────────────┘
```

---

## Example Documents

### Device Example

```json
{
  "_id": "507f1f77bcf86cd799439011",
  "imei": "123456789012345",
  "ccid": "8934071000000000000",
  "nro_orden": "ORD-2025-001",
  "lote": 1,
  "linea": 1,
  "puesto": 1,
  "marca": "OversunTrack",
  "nro_referencia": "REF-2024-GPS-001",
  "sku": "SKU-GPS-100",
  "estado": "activo",
  "ubicacion_actual": "Cliente - Distribuidora Madrid",
  "package_no": "PKG-2025-001-000000000001",
  "cliente": "507f1f77bcf86cd799439012",
  "cliente_codigo": "CUST-001",
  "cliente_nombre": "Distribuidora Madrid SL",
  "notificado": true,
  "fecha_notificacion": "2025-01-15T10:30:00Z",
  "garantia": {
    "fecha_inicio": "2025-01-15T00:00:00Z",
    "fecha_fin": "2026-01-15T00:00:00Z",
    "duracion_meses": 12,
    "tipo": "fabricante",
    "activa": true
  },
  "valido": true,
  "errores": [],
  "metadata": {},
  "fecha_creacion": "2025-01-10T08:00:00Z",
  "fecha_actualizacion": "2025-01-15T10:30:00Z",
  "creado_por": "EMP-001"
}
```

### Customer Example

```json
{
  "_id": "507f1f77bcf86cd799439012",
  "customer_code": "CUST-001",
  "customer_type": "distributor",
  "status": "active",
  "company_name": "Distribuidora Madrid SL",
  "tax_id": "B12345678",
  "email": "contacto@distribuidora.com",
  "phone": "+34 912 345 678",
  "mobile": "+34 600 123 456",
  "website": "https://distribuidora.com",
  "address": {
    "street": "Calle Principal 123",
    "city": "Madrid",
    "state": "Madrid",
    "postal_code": "28001",
    "country": "España"
  },
  "devices_count": 150,
  "active_devices_count": 145,
  "tickets_count": 12,
  "rma_count": 3,
  "discount_rate": 15.5,
  "payment_terms": "30_days",
  "credit_limit": 50000.00,
  "contacts": [
    {
      "name": "Juan Pérez",
      "role": "Gerente Técnico",
      "email": "juan@distribuidora.com",
      "phone": "+34 600 123 456",
      "added_at": "2024-07-01T10:00:00Z"
    }
  ],
  "notes": "Cliente VIP, prioridad alta",
  "tags": ["vip", "distributor", "spain"],
  "created_at": "2024-06-15T10:00:00Z",
  "updated_at": "2025-01-15T14:30:00Z",
  "last_purchase_date": "2025-01-10T00:00:00Z"
}
```

### Production Order Example

```json
{
  "_id": "507f1f77bcf86cd799439013",
  "order_number": "ORD-2025-001",
  "reference_number": "REF-2024-GPS-001",
  "sku": 100,
  "product_name": "GPS Tracker Pro",
  "brand": "OversunTrack",
  "quantity": 1000,
  "produced": 850,
  "approved": 820,
  "rejected": 30,
  "status": "in_progress",
  "production_line": 1,
  "responsible": "EMP-001",
  "created_at": "2025-01-10T08:00:00Z",
  "start_date": "2025-01-11T08:00:00Z",
  "estimated_completion": "2025-01-22T00:00:00Z",
  "updated_at": "2025-01-15T14:00:00Z",
  "batches": [
    {
      "batch_number": 1,
      "quantity": 250,
      "workstation": 1,
      "operator": "EMP001",
      "start_date": "2025-01-11T08:00:00Z",
      "end_date": "2025-01-11T16:00:00Z",
      "produced": 250,
      "status": "completed"
    },
    {
      "batch_number": 2,
      "quantity": 250,
      "workstation": 2,
      "operator": "EMP002",
      "start_date": "2025-01-12T08:00:00Z",
      "end_date": null,
      "produced": 200,
      "status": "in_progress"
    }
  ],
  "total_batches": 4,
  "labels_required": {
    "label_24": 1000,
    "label_48": 500
  },
  "notes": "Urgente, cliente VIP",
  "priority": "high"
}
```

### Movimiento Example

```json
{
  "_id": "507f1f77bcf86cd799439014",
  "tipo": "salida",
  "fecha": "2025-01-15T10:30:00Z",
  "producto": "507f1f77bcf86cd799439011",
  "imei": "123456789012345",
  "ccid": "8934071000000000000",
  "cantidad": 1,
  "cliente": "507f1f77bcf86cd799439012",
  "cliente_nombre": "Distribuidora Madrid SL",
  "cliente_codigo": "CUST-001",
  "deposito": "DEP-001",
  "ubicacion_origen": "Almacen A - Estante 3",
  "documento_referencia": "ALB-2025-001",
  "orden_produccion": "ORD-2025-001",
  "lote": 1,
  "usuario": "EMP-001",
  "usuario_nombre": "Juan Operador",
  "origen": "manual",
  "detalles": "Envío urgente cliente VIP",
  "costo_unitario": 45.50,
  "costo_total": 45.50,
  "moneda": "EUR",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Series Notification Example

```json
{
  "_id": "507f1f77bcf86cd799439015",
  "fecha": "2025-01-15T11:00:00Z",
  "customer_id": "507f1f77bcf86cd799439012",
  "customer_name": "Distribuidora Madrid SL",
  "customer_code": "CUST-001",
  "location": "LOTE-2025-001",
  "serials": [
    {
      "imei": "123456789012345",
      "ccid": "8934071000000000000",
      "device_id": "507f1f77bcf86cd799439011",
      "marca": "OversunTrack",
      "modelo": "GPS Tracker Pro"
    }
  ],
  "device_count": 25,
  "notified_count": 25,
  "failed_serials": [],
  "csv_format": "separated",
  "csv_filename": "series_LOTE-2025-001_20250115.csv",
  "email_to": "contacto@distribuidora.com",
  "email_cc": ["backup@distribuidora.com"],
  "email_sent": true,
  "operator_id": "EMP-001",
  "operator_name": "Juan Operador",
  "operator_email": "juan@ose.com",
  "notes": "Envío urgente"
}
```

### Package Example

```json
{
  "_id": "507f1f77bcf86cd799439016",
  "tracking_number": "CX123456789ES",
  "transportista": "Seur",
  "order_code": "PEDWEB-20251111-0021",
  "cliente_email": "cliente@example.com",
  "cliente_nombre": "Juan Pérez",
  "cliente_telefono": "+34 600 123 456",
  "direccion_envio": "Calle Principal 123",
  "ciudad": "Madrid",
  "codigo_postal": "28001",
  "pais": "ES",
  "dispositivos_info": [
    {
      "imei": "123456789012345",
      "modelo": "Tracker GPS",
      "descripcion": "Rastreador vehicular"
    }
  ],
  "peso_kg": 0.5,
  "dimensiones": "30x20x10 cm",
  "numero_bultos": 1,
  "tipo": "paqueteria",
  "estado": "enviado",
  "fecha_envio": "2025-01-15T10:00:00Z",
  "fecha_entrega_estimada": "2025-01-17T00:00:00Z",
  "email_enviado": true,
  "fecha_email": "2025-01-15T10:05:00Z",
  "enlace_seguimiento": "https://tracking.seur.com/CX123456789ES",
  "creado_por": "operario@ose.com",
  "fecha_creacion": "2025-01-15T09:00:00Z"
}
```

### Pallet Example

```json
{
  "_id": "507f1f77bcf86cd799439017",
  "pallet_number": "PAL-2025-0001",
  "qr_code": "QR-PAL-2025-0001-ABC123",
  "tipo_contenido": "lote",
  "contenido_ids": ["LOTE-2024-1234", "LOTE-2024-1235"],
  "pedido_id": "PED-2025-0045",
  "peso_kg": 250.5,
  "volumen_m3": 1.2,
  "ubicacion": "Almacen A - Zona 2",
  "estado": "preparado",
  "creado_por": "operario@ose.com",
  "fecha_creacion": "2025-01-15T08:00:00Z",
  "notas": "Frágil, manipular con cuidado"
}
```

### Employee Example

```json
{
  "_id": "507f1f77bcf86cd799439018",
  "employee_id": "EMP-001",
  "name": "Juan",
  "surname": "García Martínez",
  "email": "juan.garcia@ose.com",
  "phone": "+34 912 345 678",
  "password_hash": "$2b$12$KIXxRvWnhyD7pXzEKC.K8uZ...",
  "role": "operator",
  "status": "active",
  "permissions": {
    "production_line1_station1": true,
    "production_line1_station2": true,
    "quality_control": false,
    "admin_access": false,
    "manage_users": false
  },
  "last_login": "2025-01-15T08:00:00Z",
  "last_login_ip": "192.168.1.100",
  "failed_login_attempts": 0,
  "locked_until": null,
  "created_at": "2024-06-01T10:00:00Z",
  "updated_at": "2025-01-15T08:00:00Z",
  "notes": "Empleado del mes enero"
}
```

---

## Common Query Patterns

### 1. Device Queries

#### Find device by IMEI
```python
device = await Device.find_one(Device.imei == "123456789012345")
```

#### Find all devices in a production order
```python
devices = await Device.find(Device.nro_orden == "ORD-2025-001").to_list()
```

#### Find devices by customer
```python
devices = await Device.find(
    Device.cliente == customer_id,
    Device.estado == "activo"
).to_list()
```

#### Find devices needing notification
```python
devices = await Device.find(
    Device.notificado == False,
    Device.estado == "empaquetado"
).to_list()
```

#### Count devices by status
```python
from beanie.operators import In

count = await Device.find(
    Device.estado.in_(["activo", "enviado"])
).count()
```

### 2. Customer Queries

#### Find active customers
```python
customers = await Customer.find(
    Customer.status == CustomerStatus.ACTIVE
).sort("-created_at").to_list()
```

#### Find customer by code
```python
customer = await Customer.find_one(
    Customer.customer_code == "CUST-001"
)
```

#### Find distributors
```python
distributors = await Customer.find(
    Customer.customer_type == CustomerType.DISTRIBUTOR,
    Customer.status == CustomerStatus.ACTIVE
).to_list()
```

### 3. Production Order Queries

#### Find active production orders
```python
orders = await ProductionOrder.find(
    ProductionOrder.status.in_([
        ProductionOrderStatus.IN_PROGRESS,
        ProductionOrderStatus.PENDING
    ])
).to_list()
```

#### Find orders by production line
```python
orders = await ProductionOrder.find(
    ProductionOrder.production_line == 1,
    ProductionOrder.status == ProductionOrderStatus.IN_PROGRESS
).to_list()
```

#### Get production statistics
```python
from datetime import datetime, timedelta

start = datetime.utcnow() - timedelta(days=30)
end = datetime.utcnow()

stats = await ProductionOrder.get_production_stats(start, end)
```

### 4. Movimiento (Movement) Queries

#### Find device movement history
```python
movements = await Movimiento.find(
    Movimiento.producto == device_id
).sort("-fecha").to_list()
```

#### Find movements by type and date range
```python
from datetime import datetime

movements = await Movimiento.find(
    Movimiento.tipo == TipoMovimiento.SALIDA,
    Movimiento.fecha >= start_date,
    Movimiento.fecha <= end_date
).sort("-fecha").to_list()
```

#### Find customer shipments
```python
shipments = await Movimiento.find(
    Movimiento.cliente == customer_id,
    Movimiento.tipo.in_([TipoMovimiento.SALIDA, TipoMovimiento.ENVIO])
).sort("-fecha").to_list()
```

#### Count movements by type
```python
counts = await Movimiento.count_by_type(start_date=start_date)
```

### 5. Series Notification Queries

#### Find notifications by customer
```python
notifications = await SeriesNotification.find(
    SeriesNotification.customer_id == customer_id
).sort("-fecha").to_list()
```

#### Find notifications by date range
```python
notifications = await SeriesNotification.find(
    SeriesNotification.fecha >= start_date,
    SeriesNotification.fecha <= end_date
).sort("-fecha").to_list()
```

#### Find failed email notifications
```python
failed = await SeriesNotification.find(
    SeriesNotification.email_sent == False
).to_list()
```

### 6. Package Queries

#### Find package by tracking number
```python
package = await Package.find_one(
    Package.tracking_number == "CX123456789ES"
)
```

#### Find packages by order code
```python
packages = await Package.find(
    Package.order_code == "PEDWEB-20251111-0021"
).to_list()
```

#### Find packages by status
```python
packages = await Package.find(
    Package.estado == "en_transito"
).sort("-fecha_creacion").to_list()
```

#### Find undelivered packages
```python
packages = await Package.find(
    Package.estado.in_(["preparado", "enviado", "en_transito"])
).to_list()
```

### 7. Employee Queries

#### Authenticate employee
```python
employee = await Employee.authenticate("EMP-001", "password123")
```

#### Find employee by ID
```python
employee = await Employee.find_one(
    Employee.employee_id == "EMP-001"
)
```

#### Find active employees
```python
employees = await Employee.find(
    Employee.status == EmployeeStatus.ACTIVE
).to_list()
```

#### Find employees by role
```python
operators = await Employee.find(
    Employee.role == EmployeeRole.OPERATOR,
    Employee.status == EmployeeStatus.ACTIVE
).to_list()
```

### 8. Complex Aggregation Queries

#### Device production dashboard (MongoDB aggregation)
```python
pipeline = [
    {
        "$match": {
            "nro_orden": "ORD-2025-001"
        }
    },
    {
        "$group": {
            "_id": "$estado",
            "count": {"$sum": 1}
        }
    }
]

results = await Device.aggregate(pipeline).to_list()
```

#### Customer device statistics
```python
pipeline = [
    {
        "$match": {
            "cliente": customer_id
        }
    },
    {
        "$group": {
            "_id": "$estado",
            "total": {"$sum": 1}
        }
    }
]

stats = await Device.aggregate(pipeline).to_list()
```

#### Monthly shipments report
```python
from datetime import datetime

pipeline = [
    {
        "$match": {
            "tipo": "salida",
            "fecha": {
                "$gte": datetime(2025, 1, 1),
                "$lt": datetime(2025, 2, 1)
            }
        }
    },
    {
        "$group": {
            "_id": {
                "$dateToString": {
                    "format": "%Y-%m-%d",
                    "date": "$fecha"
                }
            },
            "total_shipped": {"$sum": "$cantidad"}
        }
    },
    {
        "$sort": {"_id": 1}
    }
]

report = await Movimiento.aggregate(pipeline).to_list()
```

### 9. Useful Filters and Searches

#### Search devices with filters
```python
# Multiple filters
devices = await Device.find(
    Device.nro_orden == "ORD-2025-001",
    Device.estado == "aprobado",
    Device.notificado == False
).to_list()
```

#### Date range queries
```python
from datetime import datetime, timedelta

# Last 7 days
recent = await Device.find(
    Device.fecha_creacion >= datetime.utcnow() - timedelta(days=7)
).to_list()
```

#### Text search (requires text index)
```python
# Search in customer names
customers = await Customer.find(
    {"$text": {"$search": "Madrid"}}
).to_list()
```

#### Pagination
```python
page = 1
page_size = 50
skip = (page - 1) * page_size

devices = await Device.find().skip(skip).limit(page_size).to_list()
```

#### Count with filters
```python
total = await Device.find(
    Device.estado == "activo",
    Device.cliente != None
).count()
```

### 10. Update Operations

#### Update device status
```python
device = await Device.find_one(Device.imei == "123456789012345")
device.estado = EstadoDispositivo.ACTIVO
device.fecha_actualizacion = datetime.utcnow()
await device.save()
```

#### Bulk update
```python
await Device.find(
    Device.nro_orden == "ORD-2025-001",
    Device.lote == 1
).update({"$set": {"ubicacion_actual": "Almacen B"}})
```

#### Increment counters
```python
customer = await Customer.find_one(Customer.customer_code == "CUST-001")
await customer.increment_devices_count(quantity=25)
```

---

## Index Strategy

### Performance Recommendations

1. **Always index foreign keys** - All fields used for joins/lookups
2. **Index query filters** - Fields frequently used in `find()` queries
3. **Compound indexes** - For common multi-field queries
4. **Sort fields** - Fields used in `sort()` operations

### Current Index Coverage

All collections have appropriate indexes defined in their `Settings.indexes` configuration. The indexes are automatically created when the application starts.

### Monitoring Indexes

```python
# Check indexes on a collection
indexes = await Device.get_motor_collection().index_information()
print(indexes)
```

---

## Notes

1. **ObjectId References:** Foreign keys are stored as strings (ObjectId converted to string) for flexibility.
2. **Denormalization:** Some fields (like customer names, user names) are denormalized for faster queries.
3. **Timestamps:** All timestamps are stored in UTC using `datetime.utcnow()`.
4. **Soft Deletes:** The system does not implement soft deletes; use status fields instead.
5. **Validation:** Pydantic validators ensure data integrity at the application level.

---

**End of Database Schema Reference**
