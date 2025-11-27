/**
 * OSE Platform - Series Notification Types
 * Types for device series notification to clients (IMEI/ICCID)
 */

// Device Serial Data
export interface DeviceSerial {
  imei: string
  iccid?: string
  package_no?: string
  device_id?: string
  exists?: boolean
  already_notified?: boolean
  error?: string
  // Campos adicionales para plantillas
  marca?: string
  operador?: string
  caja_master?: string
  pallet_id?: string
  order_number?: string
  nro_referencia?: string
}

// CSV Format Options
export type CSVFormat = 'separated' | 'unified' | 'detailed' | 'compact' | 'logistica-trazable' | 'imei-marca' | 'inspide' | 'clientes-genericos'

// Notification Request
export interface SeriesNotificationRequest {
  serials: DeviceSerial[]
  customer_id?: string
  customer_name?: string
  location: string
  csv_format: CSVFormat
  email_to: string
  email_cc?: string[]
  notes?: string
}

// Notification Response
export interface SeriesNotificationResponse {
  success: boolean
  notified_count: number
  csv_content: string
  csv_filename: string
  email_sent: boolean
  failed_serials: string[]
  errors?: string[]
}

// Notification History Item
export interface NotificationHistoryItem {
  id: string
  date: string
  customer_name: string
  customer_id: string
  device_count: number
  csv_format: CSVFormat
  email_to: string
  operator: string
  operator_email: string
  csv_filename: string
  notes?: string
  serials: DeviceSerial[]
  location: string
}

// Device from Backend
export interface Device {
  id: string
  imei: string
  iccid?: string
  serial_number?: string
  package_no?: string
  device_type?: string
  status: 'in_stock' | 'shipped' | 'delivered' | 'activated' | 'inactive'
  notified: boolean
  notification_date?: string
  customer_id?: string
  customer_name?: string
  current_location?: string
  created_at: string
  updated_at: string
}

// Customer
export interface Customer {
  id: string
  name: string
  email: string
  code?: string
  active: boolean
}

// Parse Result
export interface ParseResult {
  valid: DeviceSerial[]
  invalid: {
    input: string
    error: string
  }[]
}

// Validation Result
export interface ValidationResult {
  serial: DeviceSerial
  valid: boolean
  exists: boolean
  already_notified: boolean
  error?: string
}

// Bulk Validation Result
export interface BulkValidationResult {
  total: number
  valid: number
  invalid: number
  already_notified: number
  results: ValidationResult[]
}
