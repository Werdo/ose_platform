/**
 * OSE Platform - TypeScript Type Definitions
 */

// User & Authentication Types
export interface User {
  employee_id: string
  name: string
  surname: string
  email: string
  role: EmployeeRole
  status: EmployeeStatus
  permissions: UserPermissions
  last_login?: string
  created_at?: string
  updated_at?: string
}

export type EmployeeRole = 'super_admin' | 'admin' | 'operator' | 'supervisor' | 'viewer'

export type EmployeeStatus = 'active' | 'inactive' | 'suspended'

export interface UserPermissions {
  [key: string]: boolean | undefined
  production_line1_station1?: boolean
  production_line1_station2?: boolean
  production_line2_station1?: boolean
  production_line2_station2?: boolean
  production_line3_station1?: boolean
  production_line3_station2?: boolean
  quality_control?: boolean
  admin_access?: boolean
  manage_users?: boolean
  manage_settings?: boolean
  view_reports?: boolean
  manage_tickets?: boolean
  manage_rma?: boolean
  manage_customers?: boolean
  manage_inventory?: boolean
}

export interface LoginCredentials {
  identifier: string // email or employee_id
  password: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user?: User
}

// API Response Types
export interface ApiResponse<T = any> {
  data?: T
  message?: string
  error?: string
  status: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

// Dashboard Types
export interface DashboardStats {
  total_users: number
  active_users: number
  total_products: number
  pending_orders: number
}

export interface ActivityItem {
  id: string
  type: 'login' | 'logout' | 'create' | 'update' | 'delete'
  user: string
  description: string
  timestamp: string
}

// Error Types
export interface ApiError {
  message: string
  detail?: string
  status: number
}

// Re-export invoice types
export * from './invoice'
