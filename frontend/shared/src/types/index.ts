/**
 * OSE Platform - Shared TypeScript Types
 */

// ============================================================================
// API Response Types
// ============================================================================

export interface ApiResponse<T = any> {
  data?: T
  message?: string
  status: number
}

export interface ApiError {
  detail: string
  code?: string
  status_code: number
}

export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

// ============================================================================
// Authentication Types
// ============================================================================

export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
}

export type UserRole =
  | 'admin'
  | 'supervisor'
  | 'operator'
  | 'quality_inspector'
  | 'technician'
  | 'viewer'

// ============================================================================
// Device Types
// ============================================================================

export interface Device {
  id: string
  imei: string
  ccid?: string
  production_order?: string
  batch?: string
  production_line?: number
  status: DeviceStatus
  customer_id?: string
  warranty_start_date?: string
  warranty_end_date?: string
  created_at: string
  updated_at: string
}

export type DeviceStatus =
  | 'pending'
  | 'in_production'
  | 'quality_check'
  | 'approved'
  | 'rejected'
  | 'in_stock'
  | 'shipped'
  | 'installed'
  | 'active'
  | 'inactive'
  | 'rma'
  | 'retired'

// ============================================================================
// Production Order Types
// ============================================================================

export interface ProductionOrder {
  id: string
  order_number: string
  customer_id: string
  device_model: string
  quantity: number
  produced_count: number
  approved_count: number
  rejected_count: number
  status: ProductionOrderStatus
  start_date?: string
  end_date?: string
  created_at: string
  updated_at: string
}

export type ProductionOrderStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled'

// ============================================================================
// Service Ticket Types
// ============================================================================

export interface ServiceTicket {
  id: string
  ticket_number: string
  device_id: string
  customer_id: string
  title: string
  description: string
  status: TicketStatus
  priority: TicketPriority
  category: TicketCategory
  assigned_to?: string
  resolution?: string
  created_at: string
  updated_at: string
  closed_at?: string
}

export type TicketStatus = 'open' | 'in_progress' | 'waiting_customer' | 'resolved' | 'closed'

export type TicketPriority = 'low' | 'medium' | 'high' | 'critical'

export type TicketCategory =
  | 'hardware'
  | 'software'
  | 'connectivity'
  | 'warranty'
  | 'installation'
  | 'other'

// ============================================================================
// RMA Case Types
// ============================================================================

export interface RMACase {
  id: string
  rma_number: string
  device_id: string
  service_ticket_id?: string
  customer_id: string
  reason: string
  status: RMAStatus
  inspection_result?: InspectionResult
  resolution_type?: ResolutionType
  replacement_device_id?: string
  created_at: string
  updated_at: string
  closed_at?: string
}

export type RMAStatus =
  | 'pending'
  | 'received'
  | 'inspecting'
  | 'approved'
  | 'rejected'
  | 'replacing'
  | 'completed'

export type InspectionResult = 'passed' | 'failed' | 'partial'

export type ResolutionType = 'replacement' | 'repair' | 'refund' | 'reject'

// ============================================================================
// Customer Types
// ============================================================================

export interface Customer {
  id: string
  name: string
  email: string
  phone?: string
  company?: string
  address?: string
  city?: string
  country?: string
  is_distributor: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

// ============================================================================
// Employee Types
// ============================================================================

export interface Employee {
  id: string
  employee_number: string
  name: string
  email: string
  role: UserRole
  department?: string
  production_line?: number
  is_active: boolean
  hired_date?: string
  created_at: string
  updated_at: string
}

// ============================================================================
// Notification Types
// ============================================================================

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  duration?: number
  action?: {
    label: string
    callback: () => void
  }
}

// ============================================================================
// Table Types
// ============================================================================

export interface TableColumn {
  key: string
  label: string
  sortable?: boolean
  width?: string
  align?: 'left' | 'center' | 'right'
  formatter?: (value: any, row: any) => string
}

export interface TableOptions {
  page: number
  itemsPerPage: number
  sortBy?: string
  sortDesc?: boolean
  search?: string
}

// ============================================================================
// Form Types
// ============================================================================

export interface FormField {
  name: string
  label: string
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'date' | 'textarea' | 'checkbox'
  value?: any
  placeholder?: string
  required?: boolean
  disabled?: boolean
  options?: SelectOption[]
  rules?: ValidationRule[]
}

export interface SelectOption {
  label: string
  value: any
  disabled?: boolean
}

export type ValidationRule = (value: any) => boolean | string

// ============================================================================
// Chart Types
// ============================================================================

export interface ChartData {
  labels: string[]
  datasets: ChartDataset[]
}

export interface ChartDataset {
  label: string
  data: number[]
  backgroundColor?: string | string[]
  borderColor?: string | string[]
  borderWidth?: number
}

// ============================================================================
// Export all types
// ============================================================================

export type * from './index'
